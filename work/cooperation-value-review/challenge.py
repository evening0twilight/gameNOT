"""Challenge remaining sampled cooperative frontier with denser ordinary routes.
Focus cases are selected by observed gaps, not by a desired positive result.
"""
from routes import *
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
D=json.loads((ROOT/'outputs/cooperation-value-matrix.json').read_text())
def one(row):
 board=B[row['mission']];party=row['party'];levels={a:max(1,1+(board['day']-1)//6) for a in party};runs=[]
 gears=[{}]+([{'stretcher':i} for i in range(3)] if board['day']>16 else [])
 for plan in configurations(board,row['goals'],True):
  for skills,gear in itertools.product([False,True],gears):
   g,r=execute(board,row['goals'],party,levels,plan,skills=skills,gear=gear,trained=[]);runs.append(r)
 no_tool=[r for r in runs if 'stretcher' not in r['gear']]  # He's earned passive is not a purchased tool
 best=min(runs,key=rank);best_free=min(no_tool,key=rank)
 return dict(mission=board['id'],party=party,trials=len(runs),previous_frontier=len(row['frontier']),matched_or_better_without_purchase=sum(any(dominates(o,r,True) for o in no_tool) for r in row['frontier']),matched_or_better_owned_stretcher=sum(any(dominates(o,r,True) for o in runs) for r in row['frontier']),ordinary_best=compact(best),ordinary_free=compact(best_free),log=best_free['log'])
if __name__=='__main__':
 targets=[r for r in D['rows'] if r['frontier']];rows=[]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  for i,r in enumerate(pool.map(one,targets,chunksize=2),1):
   rows.append(r)
   if i%10==0:print(i,len(targets),flush=True)
 out=dict(scope='Denser all-owner ordinary assignments on the71observed frontier cases; no tools and already-owned stretcher separately. Tool acquisition cost remains24credits+2parts and available afterM16; no free-income assumption.',trials=sum(r['trials'] for r in rows),rows=rows)
 (ROOT/'outputs/cooperation-frontier-challenge.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('DONE',out['trials'],[(k,sum(r[k] for r in rows)) for k in ['previous_frontier','matched_or_better_without_purchase','matched_or_better_owned_stretcher']],flush=True)
