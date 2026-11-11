"""Build the existing final project; exporting does not assert Windows acceptance."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import struct
import tempfile
import sys
from bootstrap import LOCK, ROOT, templates_dir
from check import run

subprocess.run([sys.executable, str(ROOT / 'tools/check.py'), '--engine'], cwd=ROOT, check=True)
for name in ['windows_debug_x86_64.exe', 'windows_release_x86_64.exe']:
    if not (templates_dir() / name).is_file():
        raise SystemExit('Missing locked Windows templates: python3 tools/bootstrap.py templates')
engine = os.environ.get('GODOT', str(ROOT / LOCK['godot']['local_macos_binary']))
out = ROOT / 'build/windows-p4-tuning'
out.mkdir(parents=True, exist_ok=True)
run([engine, '--headless', '--path', 'game', '--export-release', 'Windows Desktop', str(out / 'night-tide.exe')])
for name in ['night-tide.exe', 'night-tide.pck']:
    if not (out / name).is_file():
        raise SystemExit(f'Missing output: {name}')
# Verify the target architecture without claiming to execute Windows code on macOS.
with (out / 'night-tide.exe').open('rb') as executable:
    if executable.read(2) != b'MZ':
        raise SystemExit('Export is not a Windows executable')
    executable.seek(0x3C)
    pe_offset = struct.unpack('<I', executable.read(4))[0]
    executable.seek(pe_offset)
    if executable.read(4) != b'PE\0\0' or struct.unpack('<H', executable.read(2))[0] != 0x8664:
        raise SystemExit('Export is not a Windows x86_64 PE executable')
# Boot only the exported pack in an empty project path: no source-tree fallback.
with tempfile.TemporaryDirectory(prefix='night-tide-pack-') as empty_project:
    run([engine, '--headless', '--path', empty_project, '--main-pack',
         str(out / 'night-tide.pck'), '--quit-after', '3'], 'PROJECT_BOOT_OK:')
receipt = {'pe_architecture': 'x86_64', 'exported_pack_host_smoke': True, 'design': '0.18-predevelopment', 'engine': LOCK['godot']['version_output'], 'windows_runtime_tested': False,
           'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           'working_tree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True)),
           'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.suffix in ['.exe', '.pck']}}
(out / 'build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(f'WINDOWS_EXPORT_OK: {out}; native Windows tests remain required')
