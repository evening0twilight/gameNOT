from pathlib import Path
import sys,json,itertools,multiprocessing
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
from model import *
OLD=json.loads((ROOT/'outputs/growth-identity-matrix.json').read_text())
def one(row):
 board=B[row['mission']];party=row['party'];goals=row['goals'];plans=[]
 for state in ['L3_basic','L3_specialists','L5_specialists']:
  p=row['states'][state]['plan'];x=(p['allocation'],p['priority'],p['style'],p['role'])
  if x not in plans:plans.append(x)
 allocation,priority,style,_=plans[0];plans.append((allocation,priority,style,'rope'))
 out=dict(mission=row['mission'],goals=goals,party=party,states={});count=0
 for level in [3,5]:
  candidates=[]
  # Identical candidate menu at each level; always retain no-specialty route.
  for allocation,priority,style,role in plans:
   for skills in [False,True]:
    g=IdentityRoutes(board,goals,party,{a:level for a in party},skills=skills,allocation=allocation,priority=priority,style=style,role_policy=role,extra=extras(board,goals));r=g.run();candidates.append(r);count+=1
  r=min(candidates,key=rank);out['states'][str(level)]=result_view(r)
 out['trials']=count;return out
if __name__=='__main__':
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  rows=[]
  for i,r in enumerate(pool.map(one,OLD['rows'],chunksize=8),1):
   rows.append(r)
   if i%250==0:print('compared',i,flush=True)
 out=dict(version='0.15',rows=rows,trials=sum(x['trials'] for x in rows),scope='1432 date-legal trio/goal contexts, controlled L3/L5, same candidate plans at each level including basic routes. Finite replay search, not exhaustive or player study.')
 (ROOT/'outputs/player-ready-matrix.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('DONE',len(rows),out['trials'],flush=True)
