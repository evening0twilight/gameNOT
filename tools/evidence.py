"""Restore or verify byte-identical archived evidence; never overwrite differing files."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def restore():
    manifest = json.loads((ROOT / 'archives/evidence/manifest.json').read_text())
    for entry in manifest['files']:
        target = ROOT / entry['path']
        if target.exists():
            if digest(target.read_bytes()) != entry['sha256']:
                raise SystemExit(f'Changed evidence; refusing overwrite: {target}')
            continue
        packed = (ROOT / entry['archive']).read_bytes()
        if digest(packed) != entry['archive_sha256']:
            raise SystemExit(f'Corrupt archive: {entry["archive"]}')
        raw = gzip.decompress(packed)
        if digest(raw) != entry['sha256'] or len(raw) != entry['bytes']:
            raise SystemExit(f'Corrupt evidence: {target}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    print(f'EVIDENCE_OK: {len(manifest["files"])} files')

def prune():
    """Validate every archive and original before deleting redundant originals."""
    manifest = json.loads((ROOT / 'archives/evidence/manifest.json').read_text())
    candidates = []
    for entry in manifest['files']:
        packed = (ROOT / entry['archive']).read_bytes()
        if digest(packed) != entry['archive_sha256']:
            raise SystemExit(f'Corrupt archive: {entry["archive"]}')
        raw = gzip.decompress(packed)
        if digest(raw) != entry['sha256'] or len(raw) != entry['bytes']:
            raise SystemExit(f'Corrupt evidence: {entry["path"]}')
        target = ROOT / entry['path']
        if target.exists():
            if digest(target.read_bytes()) != entry['sha256']:
                raise SystemExit(f'Changed evidence; refusing deletion: {target}')
            candidates.append((target, len(raw)))
    for target, _ in candidates:
        target.unlink()
    print(f'PRUNED: {len(candidates)} originals, {sum(size for _, size in candidates)} bytes; archives retained')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prune', action='store_true', help='Remove only verified redundant originals')
    args = parser.parse_args()
    prune() if args.prune else restore()
