"""Rebuild only current0.17 evidence. Historical screening data are frozen."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
for file,args in [(H/'apply_design.py',[]),(H/'verify.py',[]),(H/'study.py',[]),(H/'specialty_study.py',[]),(H/'mentor_study.py',[]),(H/'planned_study.py',[]),(R/'work/ordinary-player-review/campaigns.py',['--output','training-general-campaigns.json']),(H/'sync.py',[]),(H/'build_report.py',[]),(H/'final_checks.py',[])]:
 print('RUN',file.name,flush=True);subprocess.run([sys.executable,str(file),*args],check=True)
