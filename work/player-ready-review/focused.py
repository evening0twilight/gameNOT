from pathlib import Path
import sys,json,itertools,multiprocessing
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
from model import *
def one(arg):
 mid,party=arg;b=B[mid];goals=[g[0] for g in (b['route_groups']['evacuation'] if mid=='M24' else b['mandatory_groups'])];states={};trials=0
 for enabled in [False,True]:
  results=[]
  for allocation,priority,style in configurations(b,goals,dense=True):
   for exchange in ['none','ordinary']:
    g=IdentityRoutes(b,goals,party,{a:3 for a in party},skills=True,allocation=allocation,priority=priority,style=style,exchange=exchange,extra=extras(b,goals))
    if not enabled:g.h[party.index('jiang')]['abilities']=[]
    r=g.run();results.append(r);trials+=1
  states[str(enabled)]=result_view(min(results,key=rank))
 return dict(mission=mid,party=party,states=states,trials=trials)
if __name__=='__main__':
 args=[(m,p) for m in ['M16','M19','M23','M24'] for p in [['lin','he','jiang'],['xu','su','jiang'],['chen','mo','jiang']]]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(one,args))
 (ROOT/'outputs/player-ready-focused.json').write_text(json.dumps(dict(version='0.15',rows=rows,trials=sum(r['trials'] for r in rows),scope='Focused all task allocations<=5 objectives, with ordinary handoff retained; only Jiang specialties ablated at equalL3. Conditional opportunity evidence, not world-wide hero ranking.'),ensure_ascii=False,indent=2)+'\n');print('FOCUSED',len(rows),sum(rank(x['states']['True'])<rank(x['states']['False']) for x in rows),sum(r['trials'] for r in rows))
