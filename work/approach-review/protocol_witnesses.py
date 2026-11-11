"""Full-board, paid-action demonstrations for chosen-direction pull and relay."""
from pathlib import Path
import json
from encounter_choices import ChoiceBattle,distance,adjacent
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';B={b['id']:b for b in json.loads((ROOT/'game/data/final_design/boards.json').read_text())['boards']};P=['lin','xu','su']
def ordinary_third(g):
 ap={i:g.h[i]['ap'] for i in [0,2]}
 for i in ap:g.h[i]['ap']=0
 style=g.style;g.style='rush';wanted=g.wanted.copy();g.wanted.discard('asset')
 super(type(g),g).policy()
 g.wanted=wanted;g.style=style
 for i,v in ap.items():g.h[i]['ap']=v
class RelayWitness(ChoiceBattle):
 def __init__(self,use_protocol=True):
  self.use_protocol=use_protocol
  super().__init__(B['M06'],['r1','r2'],P,{a:2 for a in P},skills=False,style='rush',extra=['asset'],trained=[('lin','su','relay_carry')]);self.handed=False
 def policy(self):
  if self.handed:return super().policy()
  giver,receiver=self.h[0],self.h[2]
  for _ in range(2):
   if giver['ap']<=0:break
   if giver['carry']=='asset':
    if distance(giver['p'],receiver['p'])>1:self.move_to(giver,adjacent(receiver['p']))
    break
   task=self.task_action(giver,'asset')
   if task:self.execute_task(giver,task)
  for _ in range(2):
   if receiver['ap']<=0:break
   patient=self.objects['r2']
   if not patient['stable']:
    task=self.task_action(receiver,'r2')
    if task:self.execute_task(receiver,task)
   elif receiver['p']!=(6,2):
    if not self.move_to(receiver,[(6,2)]):break
   else:break
  if giver['carry']=='asset' and receiver['carry'] is None and min(giver['ap'],receiver['ap'])>=1 and distance(giver['p'],receiver['p'])==1:
   route=self.path(receiver['p'],self.exits,receiver,True);cost=0;path=[route[0]]
   for p in route[1:]:
    if cost+self.cost(p)>3:break
    cost+=self.cost(p);path.append(p)
   while len(path)>1 and self.occupied(path[-1],2):path.pop()
   if self.use_protocol:self.relay_path(0,2,path)
   else:
    giver['carry']=None;self.objects['asset']['p']=giver['p'];self.objects['asset']['carrier']=2;receiver['carry']='asset';self.receipt('drop',actor=0,target='asset',at=giver['p']);self.spend(receiver,'pickup',target='asset')
    if receiver['ap']>=1:self.move(receiver,route)
   self.handed=True
  if not self.handed:ordinary_third(self)
  else:super().policy()
class PullWitness(ChoiceBattle):
 def __init__(self):
  super().__init__(B['M08'],['block1','block2','truck'],P,{a:2 for a in P},skills=False,approach='independent',watchers=[0,2],trained=[('lin','su','coordinated_pull')],style='rush');self.phase='cut';self.positions=None
 def policy(self):
  if self.phase=='done':return super().policy()
  e=self.e[self.spec['source_enemy']];control=self.spec['linked_controls'][0]
  if self.phase=='cut':
   h=self.h[2]
   for _ in range(2):
    if h['ap']<=0:break
    t=self.task_action(h,control)
    if t:self.execute_task(h,t)
   # Other participant makes legal early progress toward the opposite rail side.
   h=self.h[0]
   for _ in range(2):
    if h['ap']<=0 or not self.move_to(h,[(7,6)]):break
   if self.objects[control]['done']:self.phase='position'
  if self.phase=='position':
   # Never choose the intended destination as a participant position.
   dests=[p for p in adjacent(e['p']) if self.passable(p) and not self.occupied(p) and p not in list(map(tuple,e['rail']))]
   if not dests:
    # Narrow rail: first push it along the rail to a wider section using basic actions.
    h=self.h[2];above=(e['p'][0],e['p'][1]-1);below=(e['p'][0],e['p'][1]+1)
    if self.passable(above) and self.passable(below) and not self.occupied(below):
     if h['p']!=above and h['ap']>=1:self.move_to(h,[above])
     if h['p']==above and h['ap']>=2:self.basic_push(2,e['id']);self.basic_push(2,e['id'])
    ordinary_third(self);return
   if dests:
    dest=dests[0];positions=[p for p in adjacent(e['p']) if p!=dest and self.passable(p)]
    if len(positions)>=2:
     # Opposite vertical sides are feasible next to the eastern boundary.
     positions.sort(key=lambda p:(p[0]!=e['p'][0],-p[1]))
     for a,p in zip([0,2],positions[:2]):
      for _ in range(2):
       if self.h[a]['ap']<=0 or self.h[a]['p']==p or not self.move_to(self.h[a],[p]):break
     if all(self.h[a]['p']==p for a,p in zip([0,2],positions[:2])) and min(self.h[0]['ap'],self.h[2]['ap'])>=1:
      self.precise_pull(0,2,e['id'],dest)
      if e.get('off_rail'):self.phase='restore'
  if self.phase=='restore':
   for _ in range(2):
    h=self.h[0]
    if h['ap']<=0 or h['p']==(5,3) or not self.move_to(h,[(5,3)]):break
   h=self.h[2]
   for _ in range(2):
    if h['ap']<=0:break
    if distance(h['p'],self.objects[control]['p'])<=1:self.restore_power(2,control);self.phase='done';break
    if not self.move_to(h,[self.objects[control]['p']]+adjacent(self.objects[control]['p'])):break
  if self.phase!='done':ordinary_third(self)
  else:super().policy()
out=[]
for name,g in [('relay',RelayWitness()),('ordinary_handoff',RelayWitness(False)),('pull',PullWitness())]:
 r=g.run();r.pop('used',None);r['training_assumption']='Lin/Su initially satisfy mutual trust60; one prior paid training project and2supplies stipulated. All board travel and actions are executed, no position fixtures.';out.append(r)
 r['witness_name']=name
 print(name,r['success'],r['rounds'],r['secured'],r['service_secured'],r['machinery_intact'],[x for x in r['log'] if x['action'] in ['relay_carry','coordinated_pull','restore_power']],flush=True)
g=ChoiceBattle(B['M22'],['handover'],['lin','xu','su'],{a:3 for a in ['lin','xu','su']},skills=False,approach='independent',watchers=[1],ambition=True,style='controls')
r=g.run();r.pop('used',None);r.update(witness_name='ordinary_parallel_M22',training_assumption='No protocol training, skills or purchased tools used; level3 controlled context, same starting party as the M22 cooperation comparison. Different task allocation, not the same-plan counterfactual.')
assert r['success'] and r['service_secured'] and r['machinery_intact'] and {'e','privacy','handover','live_service'}<=set(r['secured'])
out.append(r);print('ordinary_parallel_M22',r['rounds'],r['ap'],r['damage'],r['secured'],flush=True)
(O/'approach-protocol-witnesses.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
