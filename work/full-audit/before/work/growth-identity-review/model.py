"""0.13 offline design referee and policy experiments, NOT production code."""
from pathlib import Path
import sys,json,itertools,math
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/cooperation-value-review'))
from current_rules import *

class IdentityRules:
 def __init__(self,*a,role_policy='none',**kw):
  self.role_policy=role_policy;super().__init__(*a,**kw)
 def working(self,e):return not e.get('output_isolated',False) and super().working(e)
 def usable(self,h,key):
  if key=='ye_1':return self.skills_enabled and key in h['abilities'] and h['ap']>=2 and self.used.get((h['id'],key),0)<1
  if key not in ABILITIES:return False
  spec=ABILITIES[key]
  return self.skills_enabled and key in h['abilities'] and h['ap']>=spec['ap'] and self.used.get((h['id'],key),0)<(spec['charges_per_mission'] or 999)
 def use(self,actor,key,target=None,destination=None,blocked=False):
  h=self.h[actor]
  if key in ABILITIES:assert self.usable(h,key) and not h['down'] and not h['left']
  if h['level']>=5 and key=='su_3' and destination!='movement':
   y=self.h[target];assert not blocked and h['carry'] is None and target!=actor and not y['down'] and not y['left'] and distance(h['p'],y['p'])<=3 and y['ap']<=2
   token=('coordinated_ap',target,self.rnd);assert not self.used.get(token)
   self.spend(h,key,target=target,effect='transfer_one_ap');y['ap']+=1;self.used[(actor,key)]=self.used.get((actor,key),0)+1;self.used[token]=1;return
  if h['level']>=5 and key=='lin_1':
   o=self.objects[target];assert not blocked and h['carry'] is None and o['kind']=='rescue' and not o['stable'] and not o['lost'] and self.ready(o) and distance(h['p'],o['p'])<=3
   o['stable']=True;o['contributions'].append(dict(actor=actor,action=key,round=self.rnd));self.spend(h,key,target=target);self.used[(actor,key)]=self.used.get((actor,key),0)+1;return
  if key=='su_3' and destination=='movement':destination=None
  if key!='ye_1':
   anchor=h['level']>=5 and key=='xu_1' and h['carry'] is not None
   old_anchors=set(self.anchors)
   if anchor:self.anchors.add(h['p'])
   old_range=ABILITIES[key]['range'] if key in ABILITIES else None
   if h['level']>=5 and key=='jiang_1':
    y=self.h[target];d=distance(h['p'],y['p'])
    assert d<=2
    if d==2:
     assert h['p'][0]==y['p'][0] or h['p'][1]==y['p'][1]
     mid=((h['p'][0]+y['p'][0])//2,(h['p'][1]+y['p'][1])//2)
     assert self.passable(mid) and self.rows[mid[1]][mid[0]]=='.' and not self.occupied(mid)
    ABILITIES[key]['range']=2
   try:result=super().use(actor,key,target,destination,blocked=blocked)
   finally:
    self.anchors=old_anchors
    if old_range is not None:ABILITIES[key]['range']=old_range
   if h['level']>=5:
    if key=='mo_1':
     o=self.objects[target]
     if not o['done']:
      o['progress']=min(o['work'],o['progress']+1)
      if o['progress']==o['work']:self.complete(o)
    elif key=='chen_3':self.objects[target]['shield']+=3
    elif key=='he_1':self.barriers[tuple(destination)]['expires']=999
    elif key=='ye_3':
     p=tuple(destination);dx=0 if p[0]==h['p'][0] else 1 if p[0]>h['p'][0] else -1;dy=0 if p[1]==h['p'][1] else 1 if p[1]>h['p'][1] else -1
     q=(h['p'][0]+3*dx,h['p'][1]+3*dy)
     path=[(h['p'][0]+i*dx,h['p'][1]+i*dy) for i in [1,2,3]]
     if all(0<=v[0]<8 and 0<=v[1]<8 and self.rows[v[1]][v[0]] not in '#X' for v in path):self.insulated.add(q)
   return result
  h=self.h[actor];e=self.e.get(target)
  assert self.usable(h,key) and not h['down'] and not h['left'] and h['carry'] is None
  assert e and e['hp']>0 and not e.get('output_isolated') and distance(h['p'],e['p'])==1
  e['output_isolated']=True;h['ap']-=2;self.ap_used+=2;self.used[(actor,key)]=self.used.get((actor,key),0)+1
  self.receipt(key,actor=actor,target=target,ap_left=h['ap'],effect='isolate_danger_keep_supply')
 def execute_task(self,h,t):
  if h['level']>=5 and t['action']=='stabilize' and distance(h['p'],self.objects[t['target']]['p'])<=3 and self.cast(h,'lin_1',t['target']):return True
  return super().execute_task(h,t)
 def move(self,h,route):
  if self.skills_enabled and h['level']>=5 and h['carry'] and h['name']=='jiang' and (h['carry'],self.rnd) not in self.transferred:
   oid=h['carry'];d=lambda x:min(distance(x['p'],e) for e in self.exits)
   for y in self.alive():
    if y is not h and y['carry'] is None and y['ap']>=1 and distance(h['p'],y['p'])==2 and d(y)<d(h) and self.cast(h,'jiang_1',y['id']):
     self.transferred.add((oid,self.rnd));return True
  return super().move(h,route)
 def policy(self):
  reserved={}
  if self.skills_enabled:
   for h in self.alive():
    if h['name']!='su' or h['level']<5 or not self.usable(h,'su_3') or h['carry']:continue
    for y in self.alive():
     if y is h or distance(h['p'],y['p'])>3 or y['ap']>2 or self.used.get(('coordinated_ap',y['id'],self.rnd)):continue
     onsite=any(not o['done'] and not o['lost'] and self.ready(o) and distance(y['p'],o['p'])<=1 for o in self.objects.values() if o['id'] in self.wanted)
     if (y['carry'] or onsite) and self.cast(h,'su_3',y['id']):break
  if self.skills_enabled and self.role_policy!='none':
   for h in self.alive():
    if h['ap']<1 or h['carry']:continue
    if h['name']=='ye' and self.role_policy=='isolation' and self.used.get((h['id'],'ye_1'),0)<1:
     targets=[e for e in self.e.values() if self.working(e)]
     target=min(targets,key=lambda e:distance(h['p'],e['p'])) if targets else None
     if target:
      if distance(h['p'],target['p'])==1 and h['ap']>=2:self.cast(h,'ye_1',target['id'])
      elif h['ap']>=1:
       self.move_to(h,adjacent(target['p']))
       # Deliberately wait to spend2AP next round; waiting itself gives no benefit.
       reserved[h['id']]=h['ap'];h['ap']=0
    if h['name']=='chen' and self.role_policy=='protect':
     o=next((o for o in self.objects.values() if o['id'] not in self.control_ids and not o['done'] and not o['lost'] and self.risk(o['p']) and distance(h['p'],o['p'])<=1 and not self.used.get(('reinforce',o['id']))),None)
     if o:self.cast(h,'chen_3',o['id'])
    if h['name']=='xu' and self.role_policy=='protect':
     for friend in self.alive():
      if friend is h or not self.risk(friend['p']) or distance(h['p'],friend['p'])>2:continue
      places=[p for p in adjacent(friend['p']) if self.passable(p) and self.rows[p[1]][p[0]]=='.' and not self.occupied(p) and not self.risk(p) and distance(h['p'],p)<distance(h['p'],friend['p'])]
      if places and self.cast(h,'xu_3',friend['id'],places[0]):break
    if h['name']=='mo' and self.role_policy=='protect':
     enemy=next((e for e in self.e.values() if e['type']=='scout' and self.working(e) and not self.decoys.get(e['id'])),None)
     if enemy:
      places=[p for p in adjacent(enemy['p']) if distance(h['p'],p)<=3 and self.passable(p) and self.rows[p[1]][p[0]]=='.' and not self.occupied(p) and not any(o['p']==p and not o['done'] for o in self.objects.values())]
      if places:self.cast(h,'mo_3',enemy['id'],places[0])
  super().policy()
  for i,ap in reserved.items():self.h[i]['ap']=ap
class IdentityRoutes(IdentityRules,CurrentRoutes):pass
class IdentityBattle(IdentityRules,CurrentBattle):pass

def play(board,goals,party,level,plan,skills=True,role='none',dock=False):
 board=deepcopy(board)
 if dock:board['exits']=[board['backup_exit']]
 allocation,priority,style=plan
 g=IdentityRoutes(board,goals,list(party),{a:level for a in party},skills=skills,style=style,allocation=allocation,priority=priority,extra=extras(board,goals),trained=[],role_policy=role)
 r=g.run();r['plan']=dict(allocation=allocation,priority=priority,style=style,role=role,dock=dock);return g,r

def result_view(r):
 z=compact(r);z['mechanisms']={}
 for x in r['log']:
  if x['action'] in ['move','interact','pickup','stabilize','attack','extract','leave_site','intents']:continue
  if x['action'] in ABILITIES or x['action'] in ['relay_carry','coordinated_pull']:
   z['mechanisms'][x['action']]=z['mechanisms'].get(x['action'],0)+1
 return z
