from policies import *
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
class VisibleIsolation(OrdinaryField):
 def policy(self):
  if self.spec and not self.service_done and not self.service_failed and self.rnd<=self.spec['deadline']:
   source=self.e[self.spec['source_enemy']]
   for h in self.alive():
    if h['name']!='ye' or not self.usable(h,'ye_1') or not self.working(source):continue
    if distance(h['p'],source['p'])<= (2 if h['level']>=5 else 1) and self.cast(h,'ye_1',source['id']):continue
    if h['ap']:self.move_to(h,adjacent(source['p']))
  return super().policy()
def one(spec):
 mid,party,level,difficulty,variant=spec;b=B[mid];goals=[g[0] for g in b['mandatory_groups']];rows={}
 for guided in [False,True]:
  cls=VisibleIsolation if guided else OrdinaryField;g=cls(b,goals,party,{a:level for a in party},behavior='cautious',style='controls',skills=True,extra=[],approach='independent',watchers=tuple(range(len(CONTRACT['services'][mid]['posts']))),difficulty=difficulty,variant=variant);r=g.run();rows[str(guided)]={k:r[k] for k in ['success','rounds','damage','ap','service_secured','downed','secured','skill_action_types']}
 return dict(mission=mid,party=party,level=level,difficulty=difficulty,variant=variant,states=rows)
if __name__=='__main__':
 cases=[]
 for mid in ['M10','M21','S11']:
  b=B[mid];unlocked=[a for a,c in CHARS.items() if c['join']<b['day'] or c['join']==1]
  for pair in itertools.combinations([a for a in unlocked if a!='ye'],2):
   for level,diff,variant in itertools.product([3,5],['standard','hard'],['A','B']):cases.append((mid,list(pair)+['ye'],level,diff,variant))
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(one,cases,chunksize=8))
 (ROOT/'outputs/ordinary-player-opportunities.json').write_text(json.dumps(dict(version='0.16',rows=rows,trials=len(rows)*2,scope='Fixed visible service-source isolation policy versus ordinary service policy; no best-result selection. ControlledL3/L5, not earned-state campaigns. Shows whether an understandable specialty plan helps, including cases where it hurts.'),ensure_ascii=False,indent=2)+'\n');print('OPPORTUNITIES',len(rows),len(rows)*2,flush=True)
