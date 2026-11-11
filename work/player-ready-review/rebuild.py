"""Rebuild current0.15 design and offline evidence. Never starts the formal game."""
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
for name in ['apply_design.py','extend_policy.py','jiang_balance.py','author_stories.py','sync.py','verify.py','matrix.py','baseline.py','focused.py','campaigns.py']:
 subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(HERE.parent/'final-design/build_report.py')],cwd=ROOT,check=True)
for name in ['build_report.py','final_checks.py']:subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
