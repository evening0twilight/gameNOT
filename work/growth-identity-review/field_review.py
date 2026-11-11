from model import *
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
def one(args):
 mid,party=args;b=B[mid];goals=[x[0] for x in b['mandatory_groups']];out=[]
 for w in itertools.permutations(range(3),len(CONTRACT['services'][mid]['posts'])):
  for role,mode,skills in [('none','independent',False),('none','protected',True),('isolation','independent',True),('protect','protected',True)]:
   for ambition in [False,True]:
    for gear in [{},{'shield':next(i for i in range(3) if i not in w)}]+([{'insulation':w[0]}] if b['day']>7 else []):
     g=IdentityBattle(b,goals,party,{a:3 for a in party},role_policy=role,skills=skills,approach=mode,watchers=w,gear=gear,ambition=ambition,style='controls');r=g.run();r['role_policy']=role;out.append(r)
 good=[r for r in out if r['success'] and r['service_secured']]
 best=min(good or out,key=rank)
 return dict(mission=mid,party=party,trials=len(out),service=bool(good),best=result_view(best),log=best['log'])
if __name__=='__main__':
 cases=[]
 for mid in ['M05','M10','M21','S11']:
  b=B[mid];available=[a for a,c in CHARS.items() if c['join']==1 or c['join']<b['day'] or b['kind']=='side' and c['join']==b['day']]
  for party in itertools.combinations(available,3):cases.append((mid,list(party)))
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(one,cases,chunksize=3))
 (ROOT/'outputs/growth-identity-field.json').write_text(json.dumps(dict(rows=rows,trials=sum(r['trials'] for r in rows),scope='Current four optional field operations, every date-valid named trio. Controlled level3, standard/A, gear variants are owned-tool scenarios, not campaign free purchases.'),ensure_ascii=False,indent=2)+'\n');print('FIELD',len(rows),sum(r['trials'] for r in rows),sum(r['service'] for r in rows),flush=True)
