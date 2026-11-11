"""Rebuild the current design review from the existing canonical36-map design."""
from pathlib import Path
import runpy,sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
for name in ['apply_design.py','run_matrix.py','campaign.py','witnesses.py','assess.py','verify.py','build_report.py']:
 runpy.run_path(str(HERE/name),run_name='__main__')
runpy.run_path(str(HERE.parent/'final-design/build_report.py'),run_name='__main__')
runpy.run_path(str(HERE/'final_checks.py'),run_name='__main__')
