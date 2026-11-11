"""Reproduce the current offline review. Preserves frozen before evidence; no Godot edits."""
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
for name,args in [('apply_design.py',[]),('refine_growth.py',[]),('close_edges.py',[]),('sync.py',[]),('verify.py',[]),('routes.py',['--output','ordinary-player-after-routes.json']),('campaigns.py',['--output','ordinary-player-after-campaigns.json']),('growth.py',[]),('opportunities.py',[]),('build_report.py',[]),('final_checks.py',[])]:
 print('RUN',name,flush=True);subprocess.run([sys.executable,str(HERE/name),*args],check=True)
