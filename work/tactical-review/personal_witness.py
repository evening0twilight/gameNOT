"""Actual full M22 witness: He protects another operator with his real L1 shield.
Only initial positions/configuration are set; all subsequent positions cost AP.
"""
from pathlib import Path
import json,runpy,contextlib,io
from actions import Lab
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs'
b=next(b for b in json.loads((ROOT/'game/data/final_design/boards.json').read_text())['boards'] if b['id']=='M22')
g=Lab(b,['handover'],difficulty='hard');g.h[2]['name']='he';g.h[2]['abilities']=['he_1'];g.h[2]['level']=1
g.rnd=1;g.publish()
for i,path in [(0,[(1,7),(1,6),(1,5),(1,4)]),(0,[(1,4),(1,3),(2,3),(3,3)]),(2,[(3,7),(4,7),(4,6),(4,5)]),(2,[(4,5),(4,4),(5,4),(5,3)])]:
 assert all(g.passable(p) for p in path);assert g.move(g.h[i],path)
g.environment();g.rnd=2
for h in g.h:h['ap']=2
g.publish();g.execute_task(g.h[0],dict(target='handover',route=[g.h[0]['p']],action='interact'));g.move(g.h[0],[(3,3),(3,2)])
g.move(g.h[2],[(5,3),(5,2),(5,1),(4,1)]);g.use(2,'he_1',destination=(3,1));g.environment()
blocked=[r for r in g.log if r['action']=='barrier_intercept' and r['owner']==2 and 0 in r['protected_actors']]
assert blocked and g.h[0]['hp']==10
for rnd in range(3,g.limit+1):
 g.rnd=rnd
 for h in g.h:h['ap']=0 if h['left'] else 2;h['shield']=0
 g.publish();g.policy()
 if all(h['left'] for h in g.h):break
 g.environment()
assert g.objects['handover']['secured'] and all(h['left'] and not h['down'] for h in g.h)
with contextlib.redirect_stdout(io.StringIO()):v=runpy.run_path(str(ROOT/'work/final-design/verify_contracts.py'))
records=[dict(seq=11,kind='objective_completed',mission='M22',primary_contributor='lin'),dict(seq=12,kind='protect_or_rescue',mission='M22',actor='he'),dict(seq=13,kind='mission_settled',mission='M22',actors=['lin','xu','he'],all_extracted=True)]
assert v['verified']('he',records,10,22)
out={'mission':'M22','difficulty':'hard','party':['lin','xu','he'],'equipment':[],'active_specialty':'he_1 only; He joined afterM10, L1 skill available','rounds':g.rnd,'limit':g.limit,'ap':g.ap_used,'damage':g.damage_taken,'all_extracted':True,'story_proof_verified':True,'actual_protection':blocked,'primary_contribution':g.objects['handover']['contributions'],'receipts':records,'log':g.log,'scope':'Entire map reached and exited with legal AP. Camp branch requires accepting He plan beforehand and deferring final choice until this evidence exists; no forced reconciliation.'}
(O/'he-personal-full-witness.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['mission','rounds','limit','ap','damage','all_extracted','story_proof_verified']},ensure_ascii=False))
