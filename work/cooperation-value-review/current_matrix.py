from current_rules import *
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
OLD=json.loads((ROOT/'outputs/cooperation-value-matrix.json').read_text())
def one(row):
 board=B[row['mission']];party=row['party'];levels={a:max(1,1+(board['day']-1)//6) for a in party};p=row['ordinary_best']['plan'];out=[]
 configs=[(p,row['ordinary_best']['skills_enabled'],'none')]+[(dict(allocation={},priority='balanced',style=s),False,'none') for s in ['rush','controls']]
 for plan,skills,exchange in configs:
  b=CurrentRoutes(board,row['goals'],party,levels,skills=skills,style=plan['style'],allocation=plan['allocation'],priority=plan['priority'],exchange=exchange,extra=extras(board,row['goals']),trained=[]);out.append(b.run())
 for pair in itertools.combinations(range(3),2):
  b=CurrentRoutes(board,row['goals'],party,levels,skills=True,style=p['style'],allocation=p['allocation'],priority=p['priority'],exchange='advanced',pair=pair,extra=extras(board,row['goals']),trained=[]);out.append(b.run())
 best=min(out,key=rank)
 return dict(mission=row['mission'],goals=row['goals'],party=party,success=best['success'],secured=best['secured'],rounds=best['rounds'],damage=best['damage'],trials=len(out),cooperation_used=best['advanced_actions'])
if __name__=='__main__':
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(one,OLD['rows'],chunksize=8))
 baseline=[]
 for b in B.values():
  for route,groups in b.get('route_groups',{'default':b['mandatory_groups']}).items():
   for goals in itertools.product(*groups):
    for difficulty,variant in itertools.product(['relaxed','standard','hard'],['A','B']):
     p=['lin','xu','su'];rr=[CurrentBattle(b,goals,p,{a:1 for a in p},skills=False,trained=[],difficulty=difficulty,variant=variant,style=s).run() for s in ['rush','controls']]
     r=min(rr,key=rank);baseline.append({k:r[k] for k in ['mission','goals','difficulty','variant','success','rounds']})
 out=dict(version='0.12-current',scope='Current reduced scope,1432named configurations with6sampled policies each; independent276goal/difficulty/weather baseline contexts with2policies. No paid cooperation prerequisites. Not exhaustive.',rows=rows,baseline=baseline,trials=sum(r['trials'] for r in rows)+2*len(baseline))
 assert all(r['success'] for r in rows+baseline)
 (ROOT/'outputs/cooperation-current-matrix.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('CURRENT MATRIX',len(rows),len(baseline),out['trials'],flush=True)
