"""Isolated mechanic experiments on the SAME encounter state.
Fixtures deliberately exercise edge cases; they are not complete mission witnesses.
"""
from encounter import Encounter, distance, adjacent, inside
from copy import deepcopy
import json
from pathlib import Path
D=Path(__file__).resolve().parents[2]/'game/data/final_design'
ABILITIES={a['id']:a for a in json.loads((D/'abilities.json').read_text())}
EQUIPMENT={a['id']:a for a in json.loads((D/'equipment.json').read_text())['items']}

class Lab(Encounter):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.rnd=1;self.anchors=set();self.barriers={};self.tagged={};self.control_until={};self.marks={};self.decoys={};self.protocol_used=set();self.protection={};self.prepared={};self.spent_supplies=0
  self.trust={(a,b):60 for a in range(3) for b in range(3) if a!=b};self.push_progress={}
  for h in self.h:h.update(ap=2,name='generic',level=6,abilities=[],tools=[],protocols=[],move_bonus=0)
 def prepare_safety(self,protector,a,b,key):
  h=self.h[protector];assert protector not in [a,b] and not h['down'] and not h['left'] and h['carry'] is None and h['ap']>=1 and self.rows[h['p'][1]][h['p'][0]]=='.' and distance(h['p'],self.h[a]['p'])==1
  self.protection[(a,b,key)]=(protector,self.rnd,h['p']);self.spend(h,'prepare_safety',protected=a)
 def agree(self,key,a,b):
  assert a!=b and all(not self.h[i]['left'] and not self.h[i]['down'] for i in [a,b])
  self.prepared[('agreement',key,a,b)]=True;self.receipt('explicit_agreement',actors=[a,b],scope=key)
 def basic_push(self,actor,target):
  h=self.h[actor];e=self.e[target];assert h['ap']>=1 and not h['down'] and h['carry'] is None and distance(h['p'],e['p'])==1 and e['hp']>0
  vector=(e['p'][0]-h['p'][0],e['p'][1]-h['p'][1]);old=self.push_progress.get(target);n=old[2]+1 if old and old[:2]==(self.rnd,vector) else 1
  self.push_progress[target]=(self.rnd,vector,n);self.spend(h,'push',target=target)
  if e['type'] in ['hauler','sentinel'] and n<2:return
  self.push_progress.pop(target);p=(e['p'][0]+vector[0],e['p'][1]+vector[1])
  if self.passable(p) and not self.occupied(p):e['p']=p;e['intent']=[(v[0]+vector[0],v[1]+vector[1]) for v in e['intent'] if inside((v[0]+vector[0],v[1]+vector[1]))]
  else:e['hp']-=1
 def emergency_retreat(self):
  for h in self.h:
   if h['left']:continue
   h['injured']=h['down'] or h['p'] not in self.exits;h['permanent']=h['down'] and self.difficulty=='hard';h['left']=True
  self.ended=True;self.receipt('emergency_retreat',actor_states=[dict(actor=h['id'],injured=h.get('injured',False),permanent=h.get('permanent',False)) for h in self.h])
 def use(self,actor,key,target=None,destination=None,blocked=False):
  before=deepcopy(self.__dict__)
  try:return self._use(actor,key,target,destination,blocked)
  except Exception:self.__dict__=before;raise
 def _use(self,actor,key,target,destination,blocked):
  h=self.h[actor];assert not h['down'] and not h['left']
  spec=ABILITIES.get(key) or EQUIPMENT.get(key);assert spec
  skill=key in ABILITIES;ap=spec.get('ap',spec.get('action_ap',0));limit=spec.get('charges_per_mission',spec.get('uses_per_mission'))
  assert h['ap']>=ap
  if skill:assert spec['actor']==h['name'] and key in h['abilities'] and h['level']>=spec['level'] and len(h['abilities'])<=2
  else:assert key in h['tools'] or spec['slot']=='consumable'
  if h['carry'] is not None:assert key in ['jiang_1','jiang_3','xu_1','stretcher','he_3']
  if limit:assert self.used.get((actor,key),0)<limit
  if key in ['he_3','stretcher']:self.gear[key]=actor;return
  hero=self.h[target] if isinstance(target,int) else None
  obj=self.objects.get(target) if isinstance(target,str) else None
  enemy=self.e.get(target) if isinstance(target,str) else None
  first=(self.h[target[0]] if isinstance(target[0],int) else self.objects[target[0]]) if isinstance(target,list) and target else None
  p=tuple(destination) if destination is not None else hero['p'] if hero else obj['p'] if obj else enemy['p'] if enemy else first['p'] if first else None
  assert p is not None and distance(h['p'],p)<=spec['range']
  if spec.get('tags'):assert not blocked,'Known situational refusal applies to tagged specialties too'
  if key in ['lin_1','lin_3','lin_5']:
   targets=[self.objects[x] for x in target] if isinstance(target,list) else [obj]
   if key=='lin_3':
    route=self.path(h['p'],[p],h);assert route and sum(self.cost(v) for v in route[1:])<=2;h['p']=p
   assert 1<=len(targets)<= (2 if key=='lin_5' else 1) and len({o['id'] for o in targets})==len(targets)
   for o in targets:assert o and o['kind']=='rescue' and not o['stable'] and not o['lost'] and self.ready(o) and distance(h['p'],o['p'])<=(2 if key=='lin_1' else 1)
   for o in targets:o['stable']=True;o['contributions'].append(dict(actor=actor,action=key,round=self.rnd))
  elif key=='xu_1':
   assert p[0]==h['p'][0] or p[1]==h['p'][1]
   dx=0 if p[0]==h['p'][0] else 1 if p[0]>h['p'][0] else -1;dy=0 if p[1]==h['p'][1] else 1 if p[1]>h['p'][1] else -1
   cells=[(h['p'][0]+dx*n,h['p'][1]+dy*n) for n in range(1,distance(h['p'],p)+1)]
   assert self.rows[p[1]][p[0]]=='.' and self.passable(p) and not self.occupied(p,actor) and sum(self.rows[y][x] in '#X' for x,y in cells)<=1
   assert h['carry'] is None or any(distance(h['p'],a)<=1 for a in self.anchors)
   h['p']=p
  elif key=='xu_3':
   # Target position is used for cast range; explicit destination is a one-cell pull.
   assert hero and distance(h['p'],hero['p'])<=2 and distance(hero['p'],p)==1 and distance(h['p'],p)<distance(h['p'],hero['p']) and self.rows[p[1]][p[0]]=='.' and self.passable(p) and not self.occupied(p)
   assert not hero['down'] and not hero['left'] and self.used.get(('pull',target,self.rnd),0)==0
   hero['p']=p;self.used[('pull',target,self.rnd)]=1
  elif key in ['xu_5','winch']:
   assert self.passable(p) and self.rows[p[1]][p[0]]=='.';self.anchors.add(p)
  elif key=='su_1':assert enemy and self.working(enemy) and target not in self.marks;self.marks[target]=self.rnd
  elif key=='su_3':assert hero and not hero['down'] and not hero['left'];hero['move_bonus']=max(1,hero['move_bonus'])
  elif key=='su_5':assert p==tuple(self.b['backup_exit']) and self.rows[p[1]][p[0]]=='.' and self.passable(p);self.exits.append(p)
  elif key in ['chen_1','ye_1']:
   assert enemy and self.working(enemy) and self.rnd>=self.control_until.get(target,0)
   enemy['skip']=self.rnd;self.control_until[target]=self.rnd+2
  elif key=='chen_3':assert obj and not obj['lost'] and not self.used.get(('reinforce',target));obj['shield']+=3;self.used[('reinforce',target)]=1
  elif key in ['chen_5','ye_5','crowbar','cutter','battery','scanner']:
   assert obj and obj['kind']=='work' and not obj['lost'] and not obj['done'] and self.ready(obj)
   tags=set(obj.get('interaction_tags',[]))
   if key=='chen_5':assert obj['work']<=2 and 'engineering' in tags and all(self.objects[x]['done'] for x in obj['prerequisites']) and obj.get('power_off',False)
   if key=='ye_5':assert tags&{'light_obstacle','heavy_obstacle'}
   if key=='crowbar':assert 'light_obstacle' in tags
   if key=='cutter':assert 'heavy_obstacle' in tags
   if key=='battery':assert 'power_socket' in tags
   if key=='scanner':assert obj['id'] in self.control_ids
   obj['progress']=min(obj['work'],obj['progress']+(1 if key=='scanner' else 2))
   if obj['progress']==obj['work']:self.complete(obj)
  elif key in ['ye_3','insulation']:
   cells=[p]
   if key=='ye_3':
    assert p[0]==h['p'][0] or p[1]==h['p'][1]
    dx=0 if p[0]==h['p'][0] else 1 if p[0]>h['p'][0] else -1;dy=0 if p[1]==h['p'][1] else 1 if p[1]>h['p'][1] else -1
    cells=[(h['p'][0]+dx*n,h['p'][1]+dy*n) for n in [1,2]]
   assert all(inside(v) and self.rows[v[1]][v[0]] not in '#X' for v in cells);self.insulated.update(cells)
  elif key in ['he_1','shield']:
   assert self.passable(p) and not self.occupied(p);self.barriers[p]=dict(owner=actor,hp=3 if key=='he_1' else 4,expires=self.rnd+1 if key=='he_1' else 999)
  elif key=='he_5':
   assert isinstance(target,list) and len(set(target))==len(target)<=2
   for i in target:assert i!=actor and distance(h['p'],self.h[i]['p'])<=2 and not self.h[i]['down']
   for i in target:self.h[i]['shield']=max(2,self.h[i]['shield'])
  elif key=='mo_1':
   assert obj and target in self.control_ids and self.ready(obj) and not obj['done'] and not obj['lost'];obj['progress']+=1
   obj['contributions'].append(dict(actor=actor,action=key,round=self.rnd))
   if obj['progress']>=obj['work']:self.complete(obj)
  elif key in ['mo_3','beacon']:
   assert self.passable(p) and self.rows[p[1]][p[0]]=='.' and not self.occupied(p)
   if key=='mo_3':assert enemy and enemy['type']=='scout'
   self.decoys[target or 'nearest_scout']=dict(p=p,from_round=self.rnd+1,uses=1 if key=='mo_3' else 2)
  elif key=='mo_5':
   assert enemy and enemy['type']=='relay';wave=next((x for x in self.pending if x['source']==target),None);assert wave;self.pending.remove(wave)
  elif key=='jiang_1':
   assert hero and h['carry'] is not None and hero['carry'] is None and not hero['down'] and not hero['left']
   oid=h['carry'];hero['carry']=oid;h['carry']=None;self.objects[oid]['carrier']=target
  elif key=='jiang_3':
   assert hero and hero['carry'] is None and not hero['down'] and self.used.get('med_dose',0)<self.gear.get('med_dose',0)
   # Concrete remote medicine case. Other consumables use their own target rules.
   assert hero['hp']<10;hero['hp']=min(10,hero['hp']+3);self.used['med_dose']=self.used.get('med_dose',0)+1;self.spent_supplies+=1
  elif key=='jiang_5':assert self.rows[p[1]][p[0]]==':';self.rows[p[1]][p[0]]='.'
  elif key=='medkit':
   assert hero and not hero['down'] and hero['hp']<10 and self.used.get('med_dose',0)<self.gear.get('med_dose',0)
   hero['hp']=min(10,hero['hp']+3);self.used['med_dose']=self.used.get('med_dose',0)+1;self.spent_supplies+=1
  elif key=='foam':assert p==tuple(self.b['environment']['water_addition']['source']['cell']);self.foam_until=self.rnd+2
  elif key=='extinguisher':
   area={p,*adjacent(p)};assert area&self.fire or any(e['type']=='welder' and e['p'] in area for e in self.e.values());self.fire-=area;self.prepared['fire_suppression']=area;self.prepared['welder_debuff_round']=self.rnd;self.prepared['welder_debuff_area']=area
  else:raise AssertionError(key)
  if not skill and spec['slot']=='consumable':assert self.used.get(('stock',key),0)<self.gear.get(key+'_stock',0);self.used[('stock',key)]=self.used.get(('stock',key),0)+1;self.spent_supplies+=spec['consumable_supply_cost']
  h['ap']-=ap;self.ap_used+=ap;self.used[(actor,key)]=self.used.get((actor,key),0)+1;self.receipt(key,actor=actor,target=target,destination=destination,ap_left=h['ap'])
 def protocol(self,key,a,b,target=None,blocked=False,safeguard=False):
  before=deepcopy(self.__dict__)
  try:
   x,y=self.h[a],self.h[b];assert a!=b and all(h['ap']>=1 and not h['down'] and not h['left'] for h in [x,y]);assert key in x['protocols'] and key in y['protocols'];assert self.trust[(a,b)]>=60 and self.trust[(b,a)]>=60
   marker=self.protection.get((a,b,key));physical=False
   if marker:
    protector,rnd,p=marker;helper=self.h[protector];physical=rnd==self.rnd and helper['p']==p and not helper['down'] and not helper['left'] and distance(helper['p'],x['p'])==1
   permitted=physical if key in ['protected_work','mutual_cover'] else self.prepared.get(('agreement',key,a,b),False)
   assert not blocked or permitted,'A caller-provided safeguard boolean is not a physical/consented safeguard'
   assert (tuple(sorted([a,b])),key,self.rnd) not in self.protocol_used
   if key=='relay_carry':
    assert distance(x['p'],y['p'])==1 and x['carry'] is not None and y['carry'] is None
    oid=x['carry'];x['carry']=None;y['carry']=oid;self.objects[oid]['carrier']=b
    route=self.path(y['p'],self.exits,y,True)
    if route:
     used=0;end=0
     for i,p in enumerate(route[1:],1):
      used+=self.cost(p)
      if used>3:break
      if not self.occupied(p,b):end=i
     y['p']=route[end]
   else:
    assert x['carry'] is None and y['carry'] is None
    if key=='protected_work':
     o=self.objects[target];assert distance(x['p'],y['p'])==1 and distance(x['p'],o['p'])<=1 and self.ready(o) and o['kind']=='work' and not o['lost'] and not o['done'];o['progress']=min(o['work'],o['progress']+3);x['shield']=max(2,x['shield'])
     if o['progress']==o['work']:self.complete(o)
    elif key=='mutual_cover':assert distance(x['p'],y['p'])<=2;x['shield']=max(2,x['shield']);y['shield']=max(2,y['shield'])
    elif key=='coordinated_pull':
     e=self.e[target];assert e['type'] in ['hauler','sentinel'] and distance(x['p'],e['p'])==distance(y['p'],e['p'])==1
     p=next((p for p in adjacent(e['p']) if self.passable(p) and not self.occupied(p)),None);assert p
     dx,dy=p[0]-e['p'][0],p[1]-e['p'][1];e['p']=p;e['intent']=[(v[0]+dx,v[1]+dy) for v in e['intent'] if inside((v[0]+dx,v[1]+dy))]
    else:raise AssertionError(key)
   for h in [x,y]:h['ap']-=1;self.ap_used+=1
   self.protocol_used.add((tuple(sorted([a,b])),key,self.rnd));self.protection.pop((a,b,key),None);self.receipt(key,actors=[a,b],target=target)
  except Exception:self.__dict__=before;raise
