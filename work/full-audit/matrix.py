"""Replay prior named-party witnesses and all goal/difficulty/weather baselines."""
from pathlib import Path
import sys,json,itertools,multiprocessing
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
from model import *
OLD=json.loads((ROOT/'outputs/growth-identity-matrix.json').read_text())
def named(row):
 old=row['states']['L3_specialists'];p=old['plan'];b=IdentityRoutes(B[row['mission']],row['goals'],row['party'],{a:3 for a in row['party']},skills=True,allocation=p['allocation'],priority=p['priority'],style=p['style'],role_policy=p['role'],extra=extras(B[row['mission']],row['goals']));r=b.run()
 return dict(mission=row['mission'],goals=row['goals'],party=row['party'],success=r['success'],rounds=r['rounds'],damage=r['damage'],prior_rounds=old['rounds'],prior_damage=old['damage'])
def baseline(arg):
 mid,goals,difficulty,variant=arg;b=B[mid];p=['lin','xu','su'];results=[]
 for style in ['rush','controls']:
  g=IdentityBattle(b,goals,p,{a:1 for a in p},skills=False,difficulty=difficulty,variant=variant,style=style);results.append(g.run())
 r=min(results,key=rank);return {k:r[k] for k in ['mission','goals','difficulty','variant','success','rounds','damage','downed']}
if __name__=='__main__':
 args=[(b['id'],goals,d,v) for b in B.values() for groups in b.get('route_groups',{'default':b['mandatory_groups']}).values() for goals in itertools.product(*groups) for d,v in itertools.product(['relaxed','standard','hard'],['A','B'])]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  rows=[]
  for i,r in enumerate(pool.map(named,OLD['rows'],chunksize=8),1):
   rows.append(r)
   if i%250==0:print('named',i,flush=True)
  basic=list(pool.map(baseline,args,chunksize=4))
 out=dict(version='0.14',named=rows,baseline=basic,trial_count=len(rows)+len(basic)*2,scope='Replays1432previous legal named-party witnesses at controlledL3, then552baseline routes across276goal/difficulty/weather contexts. No exhaustive action search and no human usability claim.')
 (ROOT/'outputs/full-audit-matrix.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print('MATRIX',len(rows),sum(r['success'] for r in rows),len(basic),sum(r['success'] for r in basic),flush=True)
