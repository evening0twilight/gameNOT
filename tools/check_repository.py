"""Cheap repository checks before restoring evidence or starting Godot."""
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'game'

def main():
    files = {}
    failures = []
    for directory, dirs, names in os.walk(GAME):
        if '.git' in dirs or '.git' in names:
            failures.append(f'Nested Git metadata: {directory}')
        dirs[:] = [d for d in dirs if d not in {'.git', '.godot', '__pycache__'}]
        for name in names:
            path = Path(directory) / name
            relative = path.relative_to(GAME).as_posix()
            key = relative.casefold()
            if key in files:
                failures.append(f'Case-insensitive collision: {relative} / {files[key]}')
            files[key] = relative
    for relative in files.values():
        path = GAME / relative
        if path.suffix not in {'.gd', '.tscn', '.tres'}:
            continue
        for resource in re.findall(r'res://([^"\s]+)', path.read_text(encoding='utf-8')):
            # Literal resource references only; dynamic paths need runtime coverage.
            if '%' in resource:
                continue
            if resource.casefold() not in files:
                failures.append(f'Missing literal resource in {relative}: {resource}')
            elif files[resource.casefold()] != resource:
                failures.append(f'Resource case mismatch in {relative}: {resource}')
    project = (GAME / 'project.godot').read_text(encoding='utf-8')
    if 'renderer/rendering_method="gl_compatibility"' not in project:
        failures.append('Renderer differs from the approved Compatibility decision')
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'REPOSITORY_OK: {len(files)} files; nesting, case, literal resources, renderer')

if __name__ == '__main__':
    main()
