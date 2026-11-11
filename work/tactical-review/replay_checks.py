"""Replay recorded witnesses without calling the strategy policy.
Checks action legality, cost and resulting combat state, including occupied landings.
"""
from pathlib import Path
import json
from encounter import Encounter,distance
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs'
B={b['id']:b for b in json.loads((ROOT/'game/data/final_design/boards.json').read_text())['boards']}
W=json.loads((O/'tactical-full-witnesses.json').read_text());count=0;commands=0;enemy_steps=0
for w in W:
 g=Encounter(B[w['mission']],w['goals'],w['difficulty'],w['variant'],w['style'])
 for rnd in range(1,w['rounds']+1):
  g.rnd=rnd
  for h in g.h:h['ap']=2 if not h['left'] and not h['down'] else 0;h['shield']=0
  g.publish()
  for a in [x for x in w['log'] if x['round']==rnd and x['action'] in ['move','interact','stabilize','pickup','extract','leave_site','attack']]:
   h=g.h[a['actor']];action=a['action'];assert h['ap']>=1 and not h['down'] and not h['left']
   if action=='move':
    path=list(map(tuple,a['path']));assert path[0]==h['p'] and len(path)>1
    assert all(distance(x,y)==1 and g.passable(y) for x,y in zip(path,path[1:]));assert sum(g.cost(p) for p in path[1:])<=g.budget(h);assert not g.occupied(path[-1],h['id'])
    assert g.move(h,path) and h['p']==path[-1]
   elif action in ['interact','stabilize','pickup']:
    o=g.objects[a['target']];assert distance(h['p'],o['p'])<=1 and not o['lost'] and not o['done'] and g.ready(o) and o['carrier'] is None
    if action=='stabilize':assert not o['stable']
    if action=='pickup':assert o['stable'] and h['carry'] is None
    assert g.execute_task(h,dict(target=a['target'],route=[h['p']],action=action))
   elif action=='attack':
    e=g.e[a['target']];assert h['carry'] is None and distance(h['p'],e['p'])==1 and e['hp']>0;e['hp']-=2;g.spend(h,'attack',target=e['id'])
   elif action=='extract':
    assert h['p'] in g.exits and h['carry']==a['target'];o=g.objects[h['carry']];o['carrier']=None;g.complete(o);h['carry']=None;g.spend(h,'extract',target=o['id'])
   else:
    assert h['p'] in g.exits
    if a.get('delivered'):
     assert h['carry']==a['delivered'];o=g.objects[h['carry']];o['carrier']=None;g.complete(o);h['carry']=None
    assert h['carry'] is None;g.spend_leaving(h)
   assert h['ap']==a['ap_left'] and h['p']==tuple(a['at']),(w['mission'],a)
   commands+=1
  if not all(h['left'] for h in g.h):g.environment();enemy_steps+=1
 assert g.all_secured() and all(h['left'] and not h['down'] for h in g.h),w['mission']
 assert g.ap_used==w['ap'] and g.damage_taken==w['damage']
 assert sorted(k for k,o in g.objects.items() if o['secured'] and k not in g.control_ids)==sorted(w['secured'])
 count+=1
assert count==276
out={'witnesses_replayed':count,'player_commands_checked':commands,'enemy_environment_steps_replayed':enemy_steps,'strategy_policy_called':False,'result':'PASS','boundary':'Independent command legality/replay, same authored rule model; not independent human play or production implementation.'}
(O/'tactical-replay-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
