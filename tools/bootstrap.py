"""Fetch checksum-locked official tools. No pip dependencies or silent upgrades."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())

def templates_dir():
    if sys.platform == 'darwin':
        base = Path.home() / 'Library/Application Support'
    elif sys.platform == 'win32':
        base = Path(os.environ['APPDATA'])
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))
    return base / 'Godot/export_templates' / LOCK['godot']['templates_version']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', choices=['linux', 'windows', 'templates'])
    target = parser.parse_args().target
    spec = LOCK['downloads'][target]
    cache = ROOT / 'work/toolchain/downloads'
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / spec['url'].split('/')[-1]
    if not archive.exists():
        partial = archive.with_suffix('.partial')
        for url in [spec['url']] + ([spec['mirror']] if 'mirror' in spec else []):
            result = subprocess.run(['curl', '--fail', '--location', '--continue-at', '-', '--retry', '2', '--max-time', '600', url, '-o', str(partial)])
            if result.returncode == 0:
                break
        else:
            raise SystemExit('Official download unavailable; retry later. No unverified fallback installed.')
        partial.replace(archive)
    with archive.open('rb') as stream:
        actual_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual_hash != spec['sha256']:
        raise SystemExit(f'Checksum mismatch; remove and fetch again: {archive}')
    dest = templates_dir() if target == 'templates' else ROOT / 'work/toolchain' / target
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        names = ['templates/windows_debug_x86_64.exe', 'templates/windows_release_x86_64.exe', 'templates/version.txt'] if target == 'templates' else z.namelist()
        for name in names:
            leaf = Path(name).name
            if not leaf or name.endswith('/'):
                continue
            (dest / leaf).write_bytes(z.read(name))
            if target == 'linux':
                (dest / leaf).chmod(0o755)
    print(f'INSTALLED {target}: {dest}')

if __name__ == '__main__':
    main()
