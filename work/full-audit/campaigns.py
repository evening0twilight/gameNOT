from pathlib import Path
import sys,json,multiprocessing
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
from campaign_review import *
if __name__=='__main__':
 cases=[('0.14固定队伍全36关',dict(training='targeted',formation='fixed'),dict(fixed=True,sides=True)),('0.14轮换与选择性培养全36关',dict(training='selective',formation='flex',pacts=True,dock=True,dock_days=[22]),dict(sides=True)),('0.14最高难度全36关',dict(training='targeted',formation='flex',pacts=True),dict(hard=True,sides=True)),('0.14最高难度含终战在内五次失误',dict(training='selective',formation='flex',pacts=True,ending='shared_control'),dict(hard=True,disasters=(6,7,8,15,24)))]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  rows=[]
  for r in pool.map(one,cases):
   rows.append(r);print(r['summary']['name'],r['summary']['world_ending'],r['summary']['resources'],r['summary']['withdrawn'],flush=True)
 (ROOT/'outputs/full-audit-campaigns.json').write_text(json.dumps(dict(version='0.14',scenarios=rows,actual_battles=sum(len(r['battles']) for r in rows),scope='Four actual earned-state campaigns; two standard and one hard full36mission paths plus hard setbacks including final mission. Medical third-dose value is separately exercised in controlled transaction/action tests, not smuggled into these campaigns for free.'),ensure_ascii=False,indent=2)+'\n')
