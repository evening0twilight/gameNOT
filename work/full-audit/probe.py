from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'work/growth-identity-review'))
from relationships import *
def fixture(actor='xu',level=5,gear=None):
 b=deepcopy(B['M01']);b.update(rows=['........']*8,spawns=[[2,4],[3,4],[1,4]],enemies=[],controls=[],objectives=[dict(id='r1',kind='rescue',cell=[2,3],work=0,hp=4,prerequisites=[],initial_stable=True,stabilize_deadline={'mode':'none'})])
 p=[actor]+[a for a in ['lin','xu','su'] if a!=actor][:2]
 g=IdentityBattle(b,['r1'],p,{a:level for a in p},gear=gear or {});g.rnd=1;return g
out=[]
g=fixture(gear={'winch':0});g.h[0]['tools'].append('winch');g.use(0,'winch',destination=(2,3));out.append(dict(id='winch_deleted',observed=list(g.anchors),expected=[[2,3]],bug=not g.anchors))
g=fixture('lin',6,{'medkit':0,'med_dose':2});g.h[0]['tools'].append('medkit');g.h[1]['hp']=10
try:g.use(0,'medkit',1);worked=True
except AssertionError:worked=False
out.append(dict(id='cannot_heal_above10',hp=g.h[1]['hp'],maxHP=12,bug=not worked))
g=fixture('jiang',6,{'med_dose':2});g.h[1].update(hp=7,left=True)
try:g.use(0,'jiang_3',1);worked=True
except AssertionError:worked=False
out.append(dict(id='heals_departed_actor',bug=worked))
(R/'outputs/full-audit-before.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
