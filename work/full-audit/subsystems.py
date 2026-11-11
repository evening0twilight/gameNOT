"""Re-execute unchanged emotion, appraisal/guidance and story-proof tests."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/full-audit';out=[]
for name in ['system-audit/verify.py','player-experience/verify.py','final-design/verify_contracts.py']:
 with (W/(name.replace('/','-')+'.log')).open('w') as log:r=subprocess.run([sys.executable,str(ROOT/'work'/name)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 out.append(dict(script=name,exit_code=r.returncode));print(name,r.returncode,flush=True)
(ROOT/'outputs/full-audit-subsystems.json').write_text(json.dumps(out,indent=2)+'\n')
