"""Rebuild0.14 design artifacts and reference checks, never the production game."""
from pathlib import Path
import subprocess,sys,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
assert json.loads((ROOT/'game/data/final_design/production_scope.json').read_text())['version'].startswith(('0.13','0.14'))
for name in ['reproduce_before.py','apply_design.py','verify.py','matrix.py','campaigns.py','subsystems.py','build_report.py']:
 subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(HERE.parent/'final-design/build_report.py')],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(HERE/'final_checks.py')],cwd=ROOT,check=True)
