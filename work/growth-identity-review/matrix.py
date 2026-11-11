from model import *
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
OLD=json.loads((ROOT/'outputs/cooperation-value-matrix.json').read_text())
def one(row):
 b=B[row['mission']];party=row['party'];goals=row['goals'];plans=configurations(b,goals)
 out={};trials=0
 for name,lvl,skills in [('L1_basic',1,False),('L3_basic',3,False),('L3_specialists',3,True),('L5_specialists',5,True)]:
  rs=[]
  for plan in plans:
   _,r=play(b,goals,party,lvl,plan,skills);rs.append(r);trials+=1
  if skills:
   for role in ['isolation','protect']:
    for plan in plans[:4]:
     _,r=play(b,goals,party,lvl,plan,skills,role);rs.append(r);trials+=1
  out[name]=result_view(min(rs,key=rank))
 # A clear qualitative gain is more rescued/evidence results, not just different text.
 lower=out['L3_basic'];upper=out['L3_specialists']
 return dict(mission=b['id'],goals=goals,party=party,trials=trials,states=out,
  specialty_gain=upper['success'] and (set(upper['secured'])>set(lower['secured']) or upper['damage']<lower['damage'] or upper['rounds']<lower['rounds']),
  extra_outcomes=upper['success'] and set(upper['secured'])>set(lower['secured']),
  growth_gain=rank(out['L5_specialists'])<rank(out['L3_specialists']))
if __name__=='__main__':
 rows=[]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  for i,r in enumerate(pool.map(one,OLD['rows'],chunksize=6),1):
   rows.append(r)
   if i%150==0:print(i,len(OLD['rows']),flush=True)
 maps=[]
 for mid in B:
  rr=[r for r in rows if r['mission']==mid]
  maps.append(dict(mission=mid,cases=len(rr),baseline=sum(r['states']['L1_basic']['success'] for r in rr),specialty_gain=sum(r['specialty_gain'] for r in rr),extra_outcomes=sum(r['extra_outcomes'] for r in rr),L5_gain=sum(r['growth_gain'] for r in rr)))
 (ROOT/'outputs/growth-identity-matrix.json').write_text(json.dumps(dict(version='0.13',scope='1432chronologically available named trios/goal selections, fixed spawns, standard/A. Levels1/3/5 are controlled capability comparisons, not magically earned campaign states. Same ordinary assignment menu; specialists additionally try relevant proactive policies. No equipment or relationship dock. Bounded routes, not human preference.',trials=sum(r['trials'] for r in rows),maps=maps,rows=rows),ensure_ascii=False,indent=2)+'\n');print('DONE',sum(r['trials'] for r in rows),flush=True)
