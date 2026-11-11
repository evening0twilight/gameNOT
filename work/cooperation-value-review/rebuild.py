"""Called after a fresh0.11 rebuild by the full design pipeline.
Separate interpreters keep historical and current model imports from leaking.
"""
from pathlib import Path
import subprocess,sys,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
assert json.loads((ROOT/'game/data/final_design/player_choice_contract.json').read_text())['version'].startswith('0.11'),'Run work/final-design/rebuild.py to reconstruct the prior baseline first.'
for name in ['matrix.py','focused.py','challenge.py','audit_campaigns.py','apply_design.py','current_matrix.py','current_campaign.py','verify.py','build_report.py']:
 subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(HERE.parent/'final-design/build_report.py')],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(HERE/'final_checks.py')],cwd=ROOT,check=True)
