"""Current design checks only. Does not launch or change the production game."""
from pathlib import Path
import subprocess,sys,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
version=json.loads((ROOT/'game/data/final_design/production_scope.json').read_text())['version']
assert version.startswith(('0.12','0.13')),'Rebuild the baseline via work/final-design/rebuild.py first.'
for name in ['apply_design.py','matrix.py','campaign_review.py','selective_campaigns.py','field_review.py','ports.py','verify.py','build_report.py']:
 subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(HERE.parent/'final-design/build_report.py')],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(HERE/'final_checks.py')],cwd=ROOT,check=True)
