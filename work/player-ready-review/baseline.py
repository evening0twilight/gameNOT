from pathlib import Path
import sys,json,itertools,multiprocessing
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
from model import *
def one(arg):
 mid,goals,difficulty,variant=arg;results=[]
 for style in ['rush','controls']:
  g=IdentityBattle(B[mid],goals,['lin','xu','su'],{a:1 for a in ['lin','xu','su']},skills=False,difficulty=difficulty,variant=variant,style=style);results.append(g.run())
 r=min(results,key=rank);return {k:r[k] for k in ['mission','goals','difficulty','variant','success','rounds','damage','downed']}
if __name__=='__main__':
 args=[(b['id'],goals,d,v) for b in B.values() for groups in b.get('route_groups',{'default':b['mandatory_groups']}).values() for goals in itertools.product(*groups) for d,v in itertools.product(['relaxed','standard','hard'],['A','B'])]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(one,args,chunksize=4))
 (ROOT/'outputs/player-ready-baseline.json').write_text(json.dumps(dict(version='0.15',rows=rows,trials=len(rows)*2),ensure_ascii=False,indent=2)+'\n');print('BASELINE',len(rows),sum(x['success'] for x in rows))
