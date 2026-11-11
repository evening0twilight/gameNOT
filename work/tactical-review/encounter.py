"""Offline design rehearsal: deterministic discrete combat, NOT production game code.
Commands produce inspectable action receipts. The policy is heuristic, not a proof
of optimality; a failed search must never be called an impossible level.
"""
from copy import deepcopy
from collections import deque
import heapq, math

def distance(a,b):return abs(a[0]-b[0])+abs(a[1]-b[1])
def adjacent(p):return [(p[0]+dx,p[1]+dy) for dx,dy in [(0,-1),(-1,0),(1,0),(0,1)]]
def inside(p):return 0<=p[0]<8 and 0<=p[1]<8
HP={'scout':3,'welder':5,'hauler':8,'relay':4,'skimmer':4,'sentinel':10}

class Encounter:
 def __init__(self,board,goals,difficulty='standard',variant='A',style='controls',gear=None,level=1,extra=(),delay=0):
  self.b=deepcopy(board);self.rows=[list(r) for r in board['rows']];self.goals=set(goals);self.required=set(goals);self.extra=set(extra);self.wanted=set(goals)|set(extra);self.style=style;self.difficulty=difficulty;self.variant=variant;self.rnd=0;self.limit=board.get('hard_round_limit',board['round_limit']-1) if difficulty=='hard' else board['round_limit']+{'standard':0,'relaxed':3}[difficulty];self.log=[];self.damage_taken=0;self.ap_used=0;self.delay=delay
  self.h=[dict(id=i,p=tuple(p),hp=10+int(level>=4)+int(level>=6),ap=0,carry=None,left=False,down=False,deadline=None,stabilized=False,first_work=True,first_move=True,shield=0) for i,p in enumerate(board['spawns'])]
  self.objects={o['id']:dict(deepcopy(o),p=tuple(o['cell']),progress=0,done=False,secured=False,lost=False,stable=o.get('initial_stable',True),carrier=None,started=None,ticks=0,index=0,shield=0,completed_round=None,contributions=[]) for o in board['objectives']+board['controls']}
  self.control_ids={o['id'] for o in board['controls']};self.e={x['id']:dict(deepcopy(x),p=tuple(x['cell']),hp=HP[x['type']],disabled=False,intent=[],step=(0,1),rail_index=0,rail_direction=1,skip=0) for x in board['enemies']}
  self.gear=gear or {};self.level=level;self.used={};self.exits=list(map(tuple,board['exits']));self.pending=[];self.spawned=0;self.fire=set();self.insulated=set();self.foam_until=0;self.water_done=False;self.ended=False;self.round_damage=[];self.assignments={};self.branch=None
  if self.gear.get('incoming_failure'):self.rows[5][1]=':'
  self.water_round=board['environment']['water_addition']['round'] if variant=='A' else board['variant']['B']['water_round']
  self.fire_round=board['environment']['fire_pulse']['round'] if variant=='A' else board['variant']['B']['fire_round']
  if board['id']=='M24':
   active=self.wanted|{'archive'}
   self.objects={k:o for k,o in self.objects.items() if k in self.control_ids or k in active}
  def expand(k):
   for dep in self.objects[k]['prerequisites']:
    if dep not in self.wanted:self.wanted.add(dep);expand(dep)
  for k in list(self.wanted):expand(k)
  for enemy in self.e.values():
   if enemy['rail']:
    rail=list(map(tuple,enemy['rail']));enemy['rail_index']=rail.index(enemy['p']) if enemy['p'] in rail else 0
 def receipt(self,action,**kw):self.log.append(dict(round=self.rnd,action=action,**kw))
 def alive(self):return [h for h in self.h if not h['left'] and not h['down']]
 def machine_at(self,p):return next((e for e in self.e.values() if e['p']==p and e['hp']>0),None)
 def passable(self,p):return inside(p) and self.rows[p[1]][p[0]] not in '#X' and not self.machine_at(p)
 def occupied(self,p,except_id=None):return any(h['p']==p and not h['left'] and not h['down'] and h['id']!=except_id for h in self.h)
 def cost(self,p):return 2 if self.rows[p[1]][p[0]] in '~:' else 1
 def ready(self,o):return all(self.objects[d]['done'] for d in o['prerequisites'])
 def working(self,e):return e['hp']>0 and not e['disabled'] and e['skip']!=self.rnd
 def water_component(self,start):
  if self.rows[start[1]][start[0]]!='~':return set()
  seen={start};q=[start]
  for p in q:
   for v in adjacent(p):
    if inside(v) and v not in seen and self.rows[v[1]][v[0]]=='~':seen.add(v);q.append(v)
  return seen
 def publish(self):
  if hasattr(self,'barriers'):
   self.barriers={p:b for p,b in self.barriers.items() if b['expires']>self.rnd}
  if hasattr(self,'marks'):self.marks={k:day for k,day in self.marks.items() if day>=self.rnd}
  for e in list(self.e.values()):
   e['intent']=[]
   if not self.working(e):continue
   heroes=self.alive()
   if heroes:
    target=min(heroes,key=lambda h:(distance(e['p'],h['p']),h['id']))['p'];dx=target[0]-e['p'][0];dy=target[1]-e['p'][1]
    direction=((1 if dx>=0 else -1),0) if abs(dx)>=abs(dy) else (0,1 if dy>=0 else -1)
   else:direction=(0,1)
   if e['type']=='scout' and hasattr(self,'decoys'):
    decoy=self.decoys.get(e['id']) or self.decoys.get('nearest_scout')
    if decoy and self.rnd>=decoy['from_round'] and decoy['uses']>0:
     dx,dy=decoy['p'][0]-e['p'][0],decoy['p'][1]-e['p'][1];direction=((1 if dx>=0 else -1),0) if abs(dx)>=abs(dy) else (0,1 if dy>=0 else -1);decoy['uses']-=1
   t=e['type']
   if t not in ['welder','sentinel'] or self.rnd%2:e['step']=direction
   dx,dy=e['step'];x,y=e['p']
   if t=='scout' or (t=='sentinel' and not self.rnd%2):
    for n in range(1,4):
     p=(x+dx*n,y+dy*n)
     if not inside(p) or self.rows[p[1]][p[0]] in '#X':break
     e['intent'].append(p)
   elif t=='welder' and not self.rnd%2:e['intent']=[p for p in [(x+dx,y+dy),(x+dx-dy,y+dy+dx),(x+dx+dy,y+dy-dx)] if inside(p) and self.rows[p[1]][p[0]] not in '#X']
   elif t=='skimmer':
    if self.rnd%2:
     choices=[p for p in [e['p']]+adjacent(e['p']) if inside(p) and self.rows[p[1]][p[0]]=='~' and not self.occupied(p) and (p==e['p'] or not self.machine_at(p))]
     e['move_to']=min(choices,key=lambda p:(min([distance(p,h['p']) for h in heroes] or [0]),p[1],p[0])) if choices else e['p']
    else:e['intent']=sorted(self.water_component(e['p']))
   elif t=='hauler':
    rail=list(map(tuple,e['rail'] or []));idx=e['rail_index'];direction=e['rail_direction']
    if not(0<=idx+direction<len(rail)):direction*=-1
    e['rail_direction']=direction;e['rail_targets']=[]
    for _ in range(2):
     idx+=direction
     if not 0<=idx<len(rail):break
     e['rail_targets'].append(idx);e['intent'].append(rail[idx])
   elif t=='relay' and self.rnd in [3,6] and self.spawned+len(self.pending)<self.b['reinforcement']['cap']:
    cells=list(map(tuple,self.b['reinforcement']['cells']));cell=next((p for p in cells if not self.occupied(p) and not self.machine_at(p)),None)
    if cell:self.pending.append(dict(source=e['id'],p=cell,due=self.rnd+1,delayed=False));self.receipt('spawn_warning',source=e['id'],cell=cell,due=self.rnd+1)
  self.receipt('intents',enemies=[dict(id=e['id'],type=e['type'],at=e['p'],cells=e['intent']) for e in self.e.values() if self.working(e)])
 def risk(self,p):
  return sum((3 if e['type']=='sentinel' else 2) for e in self.e.values() if self.working(e) and p in e['intent'])+(1 if p in self.fire else 0)
 def path(self,start,goals,hero,carry=False):
  goals={tuple(p) for p in goals if self.passable(tuple(p)) and not self.occupied(tuple(p),hero['id']) and tuple(p) not in getattr(self,'barriers',{})}
  if not goals:return None
  q=[(0,0,start)];best={start:(0,0)};prev={}
  while q:
   score,cost,p=heapq.heappop(q)
   if (score,cost)!=best[p]:continue
   if p in goals:
    route=[p]
    while route[-1]!=start:route.append(prev[route[-1]])
    return route[::-1]
   for v in adjacent(p):
    if not self.passable(v):continue
    nc=cost+self.cost(v);ns=score+self.cost(v)+(.2 if self.style=='rush' else .7)*self.risk(v)
    if (ns,nc)<best.get(v,(1e9,1e9)):best[v]=(ns,nc);prev[v]=p;heapq.heappush(q,(ns,nc,v))
  return None
 def budget(self,h):
  if h['carry'] is not None:return min(3,(3 if self.gear.get('stretcher')==h['id'] or self.gear.get('he_3')==h['id'] else 2)+h.get('move_bonus',0))
  return min(4,3+max(h.get('move_bonus',0),int(self.level>=2 and h['first_move'] and self.gear.get('growth_move',False))))
 def move(self,h,route):
  spent=0;end=0
  for n,p in enumerate(route[1:],1):
   if spent+self.cost(p)>self.budget(h):break
   spent+=self.cost(p)
   if not self.occupied(p,h['id']) and p not in getattr(self,'barriers',{}):end=n
  if not end:return False
  h['p']=route[end];h['first_move']=False;h['move_bonus']=0;self.spend(h,'move',path=route[:end+1]);return True
 def spend(self,h,action,**kw):
  assert h['ap']>=1 and not h['down'] and not h['left'];h['ap']-=1;self.ap_used+=1;self.receipt(action,actor=h['id'],at=h['p'],ap_left=h['ap'],**kw)
 def complete(self,o):
  assert not o['lost'],'A lost object cannot become secured again'
  o['done']=o['secured']=True;o['completed_round']=self.rnd
  if o.get('hero_id') is not None:self.h[o['hero_id']]['left']=True;self.h[o['hero_id']]['rescued']=True
  for e in self.e.values():
   if e['disable_requires'] and all(self.objects[d]['done'] for d in e['disable_requires']):e['disabled']=True
  self.receipt('completed',target=o['id'])
 def hit_hero(self,h,damage,source,electric=False):
  if h['left'] or h['down']:return
  if electric and h['p'] in self.insulated:return
  if not electric and h['shield']:damage=max(0,damage-h['shield']);h['shield']=0
  damage=max(1,damage-1) if self.difficulty=='relaxed' and damage>0 and source!='fire' else damage
  h['hp']-=damage;self.damage_taken+=damage;self.receipt('damage',actor=h['id'],source=source,damage=damage,hp=h['hp'])
  if h['hp']<=0:
   h['down']=True;h['ap']=0;h['deadline']=self.rnd+2
   if h['carry'] is not None:
    o=self.objects[h['carry']];o['carrier']=None;o['p']=h['p'];h['carry']=None
   self.receipt('downed',actor=h['id'],rescue_deadline=h['deadline'])
   key='downed_'+str(h['id']);self.objects[key]=dict(id=key,kind='hero_rescue',p=h['p'],cell=list(h['p']),work=0,hp=1,prerequisites=[],progress=0,done=False,secured=False,lost=False,stable=False,carrier=None,started=None,ticks=0,index=0,shield=0,completed_round=None,contributions=[],hero_id=h['id'])
 def hit_objects(self,p,damage,source):
  for o in self.objects.values():
   if o['kind']=='hero_rescue' or o['p']!=p or o['lost'] or o['carrier'] is not None or (o['done'] and not o.get('sustain_until_exit')) or not self.ready(o):continue
   absorb=min(o['shield'],damage);o['shield']-=absorb;o['hp']-=damage-absorb
   if o['hp']<=0:o['lost']=True;o['secured']=False;self.receipt('object_lost',target=o['id'],source=source)
 def environment(self):
  electric=set()
  for e in sorted(list(self.e.values()),key=lambda x:x['id']):
   if not self.working(e):continue
   typ=e['type']
   if typ=='scout':
    for p in e['intent']:
     other=self.machine_at(p)
     if other and other['id']!=e['id']:break
     h=next((h for h in self.alive() if h['p']==p),None)
     if h:self.hit_hero(h,2,e['id']);break
     e['p']=p;self.hit_objects(p,2,e['id'])
   elif typ=='hauler':
    for idx,p in zip(e.get('rail_targets',[]),e['intent']):
     if self.machine_at(p):break
     h=next((h for h in self.alive() if h['p']==p),None)
     if h:
      step=(p[0]-e['p'][0],p[1]-e['p'][1]);dest=(p[0]+step[0],p[1]+step[1]);self.hit_hero(h,2,e['id'])
      if self.passable(dest) and not self.occupied(dest):h['p']=dest
      else:self.hit_hero(h,1,'blocked_push');break
     e['p']=p;e['rail_index']=idx;self.hit_objects(p,2,e['id'])
   elif typ=='skimmer' and self.rnd%2:
    p=e.get('move_to',e['p'])
    if not self.occupied(p) and (p==e['p'] or not self.machine_at(p)):e['p']=p
   elif typ=='skimmer' and not self.rnd%2:electric|=self.water_component(e['p'])
   elif typ in ['welder','sentinel']:
    cells=self.water_component(e['p']) if typ=='skimmer' and not self.rnd%2 else e['intent']
    for p in cells:
     barrier=getattr(self,'barriers',{}).get(p)
     if barrier:
      self.receipt('barrier_intercept',owner=barrier.get('owner'),source=e['id'],protected_actors=[h['id'] for h in self.alive() if typ=='sentinel' and h['p'] in list(cells)[list(cells).index(p)+1:]])
      barrier['hp']-=3 if typ=='sentinel' else 2
      if barrier['hp']<=0:del self.barriers[p]
      if typ=='sentinel':break
      continue
     for h in self.alive():
      if h['p']==p:self.hit_hero(h,3 if typ=='sentinel' else 2-int(getattr(self,'prepared',{}).get('welder_debuff_round')==self.rnd and p in self.prepared.get('welder_debuff_area',set())),e['id'])
     self.hit_objects(p,3 if typ=='sentinel' else 2,e['id'])
  if not self.water_done and self.rnd>=self.water_round and self.rnd>self.foam_until:
   for x,y in self.b['environment']['water_addition']['cells']:
    if self.rows[y][x] not in '#X':self.rows[y][x]='~'
   self.water_done=True;self.receipt('water_added',cells=self.b['environment']['water_addition']['cells'])
  if self.rnd==self.fire_round:self.fire=set(map(tuple,self.b['environment']['fire_pulse']['cells']))-getattr(self,'prepared',{}).pop('fire_suppression',set())
  if self.rnd>=self.fire_round+3:self.fire.clear()
  for p in self.fire|electric:
   amount=max(1 if p in self.fire else 0,2 if p in electric else 0)
   for h in self.alive():
    if h['p']==p:
     damage=1 if p in self.insulated and p in self.fire else 0 if p in self.insulated else amount
     if damage:self.hit_hero(h,damage,'fire' if p not in electric else 'live_water',p in electric and p not in self.insulated)
   self.hit_objects(p,amount,'water/fire')
  for o in self.objects.values():
   if o['lost'] or o['done'] or not self.ready(o):continue
   if o['kind']=='rescue' and not o['stable']:
    timer=o.get('stabilize_deadline',{'mode':'none'})
    due=timer.get('round',999) if timer['mode']=='fixed_round' else max([self.objects[x]['completed_round'] or 0 for x in o['prerequisites']]+[999 if timer['mode']=='none' else 0])+2
    if self.rnd>=due:o['lost']=True;self.receipt('object_lost',target=o['id'],source='stabilization_deadline')
   if o['kind']=='channel' and o['started'] is not None:
    o['ticks']+=1
    if o['ticks']>=o['hold_rounds']:self.complete(o)
   if o['kind']=='convoy' and o['started'] is not None:
    waypoints=list(map(tuple,o['waypoints']));n=o['index']+1
    if n<len(waypoints) and not self.occupied(waypoints[n]) and not self.machine_at(waypoints[n]):o['index']=n;o['p']=waypoints[n];self.receipt('convoy_step',target=o['id'],at=o['p'])
    if o['index']==len(waypoints)-1:self.complete(o)
   if o.get('opportunity_deadline') and self.rnd>=o['opportunity_deadline'] and not o['secured']:
    o['lost']=True
    if o['carrier'] is not None:self.h[o['carrier']]['carry']=None;o['carrier']=None
    self.receipt('object_lost',target=o['id'],source='announced_opportunity_deadline')
  for h in self.h:
   if h['down'] and not h['left'] and self.rnd>=h['deadline']:
    h['left']=True;h['permanent']=self.difficulty=='hard';o=self.objects['downed_'+str(h['id'])];o['lost']=True
    if o['carrier'] is not None:self.h[o['carrier']]['carry']=None;o['carrier']=None
    self.receipt('secondary_retrieval',actor=h['id'],permanent=self.difficulty=='hard')
  for spawn in self.pending[:]:
   if self.rnd<spawn['due']:continue
   if spawn['source']!='cutter' and (self.e[spawn['source']]['hp']<=0 or self.e[spawn['source']]['disabled']):self.pending.remove(spawn);continue
   if self.occupied(spawn['p']) or self.machine_at(spawn['p']):
    if not spawn['delayed']:spawn['due']+=1;spawn['delayed']=True
    else:self.pending.remove(spawn)
   else:
    self.spawned+=1;eid='reinforcement_'+str(self.spawned);self.e[eid]=dict(id=eid,type='scout',p=spawn['p'],hp=3,disabled=False,disable_requires=[],skip=0,intent=[],step=(0,1),rail=None);self.pending.remove(spawn);self.receipt('spawn',enemy=eid,at=spawn['p'])
  self.receipt('round_end',hp=[h['hp'] for h in self.h],positions=[h['p'] for h in self.h],secured=[k for k,o in self.objects.items() if o['secured']])
 def all_secured(self):return all(self.objects[k]['secured'] for k in self.required)
 def task_action(self,h,k):
  o=self.objects[k]
  if o['lost'] or o['done'] or not self.ready(o) or o['carrier'] is not None:return None
  if h['carry'] is not None:return None
  if o['kind'] in ['channel','convoy'] and o['started'] is not None:return None
  if k in self.control_ids and self.gear.get('scanner')==h['id'] and not self.used.get('scanner') and distance(h['p'],o['p'])<=4:return dict(target=k,route=[h['p']],steps=0,action='scanner',work=max(1,o['work']-o['progress']))
  goals=[o['p']]+adjacent(o['p']);route=self.path(h['p'],goals,h)
  if not route:return None
  cost=sum(self.cost(p) for p in route[1:]);steps=math.ceil(cost/self.budget(h))
  action='interact'
  if o['kind'] in ['rescue','hero_rescue'] and not o['stable']:action='stabilize'
  elif o['kind'] in ['rescue','cargo','hero_rescue']:action='pickup'
  return dict(target=k,route=route,steps=steps,action=action,work=max(1,o['work']-o['progress']))
 def execute_task(self,h,t):
  o=self.objects[t['target']]
  if len(t['route'])>1:return self.move(h,t['route'])
  action=t['action']
  if action=='stabilize':
   o['stable']=True
   if o.get('hero_id') is not None:
    casualty=self.h[o['hero_id']]
    if not casualty['stabilized']:casualty['deadline']+=1;casualty['stabilized']=True
  elif action=='pickup':h['carry']=o['id'];o['carrier']=h['id']
  else:
   increment=1
   if action=='scanner':self.used['scanner']=1
   tags=o.get('interaction_tags',[])
   partner=next((p for p in self.alive() if p['id']!=h['id'] and p['ap']>=1 and p['carry'] is None and distance(h['p'],p['p'])==1 and tuple(sorted([h['id'],p['id']]))==tuple(self.gear.get('cooperation_pair',[0,1])) and not self.used.get(('coop',tuple(sorted([h['id'],p['id']])),self.rnd))),None)
   if self.gear.get('cooperation') and not self.gear.get('refusal') and partner and o['kind']=='work' and o['work']-o['progress']>=3:
    o['progress']=min(o['work'],o['progress']+3);h['shield']=max(h['shield'],2);self.spend(partner,'protected_work_assist',target=o['id']);self.used[('coop',tuple(sorted([h['id'],partner['id']])),self.rnd)]=1;self.spend(h,'protected_work',target=o['id'])
    o['contributions']+=[dict(actor=x,action='protected_work',round=self.rnd) for x in [h['id'],partner['id']]]
    if o['progress']==o['work']:self.complete(o)
    return True
   tool=next((name for name,tag in [('crowbar','light_obstacle'),('cutter','heavy_obstacle'),('battery','power_socket')] if self.gear.get(name)==h['id'] and tag in tags and (name=='crowbar' or self.used.get(name,0)<(2 if name=='cutter' else 1))),None)
   if tool:increment=2;action=tool;self.used[tool]=self.used.get(tool,0)+1
   elif action=='interact' and self.level>=2 and h['first_work'] and not self.gear.get('growth_move'):increment=2;h['first_work']=False
   if o['id'] in self.control_ids and hasattr(self,'tagged') and self.tagged.get(o['disables']):increment+=self.tagged.pop(o['disables'])
   if o['kind']=='work':
    o['progress']=min(o['work'],o['progress']+increment)
    if o['progress']==o['work']:self.complete(o)
   else:o['started']=self.rnd
   if tool=='cutter' and self.spawned+len(self.pending)<self.b['reinforcement']['cap']:
    cells=sorted(map(tuple,self.b['reinforcement']['cells']),key=lambda p:(distance(p,o['p']),p))
    cell=next((p for p in cells if not self.occupied(p) and not self.machine_at(p)),None)
    if cell:self.pending.append(dict(source='cutter',p=cell,due=self.rnd+1,delayed=False));self.receipt('spawn_warning',source='cutter',cell=cell,due=self.rnd+1)
  o['contributions'].append(dict(actor=h['id'],action=action,round=self.rnd));self.spend(h,action,target=o['id']);return True
 def policy(self):
  # Iterate actors' next legal actions, preserving an assignment until its task phase ends.
  for _ in range(9):
   did=False
   for h in self.h:
    if h['ap']<=0 or h['left'] or h['down']:continue
    if self.rnd<=self.delay:continue
    if h['carry'] is not None:
     if h['p'] in self.exits:
      o=self.objects[h['carry']];o['carrier']=None;self.complete(o);h['carry']=None
      unclaimed=any(not self.objects[k]['secured'] and not self.objects[k]['lost'] and self.objects[k]['carrier'] is None for k in self.wanted)
      if not unclaimed:self.spend(h,'leave_site',delivered=o['id']);h['left']=True
      else:self.spend(h,'extract',target=o['id'])
      did=True;continue
     route=self.path(h['p'],self.exits,h,True)
     if route and self.move(h,route):did=True
     continue
    emergency={k for k,o in self.objects.items() if o['kind']=='hero_rescue' and not o['secured'] and not o['lost']}
    remaining=[k for k in self.wanted|emergency if not self.objects[k]['secured'] and not self.objects[k]['lost']]
    if not remaining:
     if h['p'] in self.exits:h['left']=True;self.spend_leaving(h);did=True;continue
     route=self.path(h['p'],self.exits,h)
     if route and self.move(h,route):did=True
     continue
    tasks=[]
    ids=set(remaining)
    if self.style=='controls':ids|={k for k in self.control_ids if not self.objects[k]['done'] and self.e[self.objects[k]['disables']]['hp']>0}
    for k in sorted(ids):
     t=self.task_action(h,k)
     if not t:continue
     o=self.objects[k];penalty=0
     if o['kind']=='hero_rescue':penalty=-12
     elif t['action']=='stabilize':penalty=-8
     elif k in self.control_ids:penalty=-2
     elif o['kind']=='channel' or o['kind']=='convoy':penalty=-2
     elif k in self.extra:penalty=-5 if self.style=='optional_first' else 2
     assigned=next((other for other,target in self.assignments.items() if target==k and other!=h['id'] and self.h[other]['ap']>0),None)
     if assigned is not None:penalty+=4
     if self.assignments.get(h['id'])==k:penalty-=.7
     tasks.append((t['steps']+t['work']*.25+penalty,k,t))
    # Adjacent attack, or approach dangerous machinery under dismantle policy.
    if self.style=='attack':
     for e in self.e.values():
      if not self.working(e):continue
      route=self.path(h['p'],adjacent(e['p']),h)
      if route:
       steps=math.ceil(sum(self.cost(p) for p in route[1:])/3)
       tasks.append((steps+math.ceil(e['hp']/2)*.25-1.8,e['id'],dict(action='attack',target=e['id'],route=route)))
    if tasks:
     _,k,t=min(tasks,key=lambda x:(x[0],x[1]));self.assignments[h['id']]=k
     if t['action']=='attack':
      if len(t['route'])>1:did=self.move(h,t['route']) or did
      else:
       bonus=int(hasattr(self,'marks') and k in self.marks)
       if bonus:self.marks.pop(k)
       self.e[k]['hp']-=2+bonus;self.spend(h,'attack',target=k,damage=2+bonus);did=True
     else:did=self.execute_task(h,t) or did
    else:
     # While timers/other carriers finish, leave convoy routes and imminent attacks.
     blocked={tuple(p) for o in self.objects.values() if o['kind']=='convoy' and not o['done'] for p in o['waypoints']}
     carriers=[other for other in self.alive() if other['carry'] is not None and other['id']!=h['id']]
     if h['p'] in blocked or self.risk(h['p']) or any(distance(h['p'],other['p'])<=2 for other in carriers):
      choices=[p for y in range(8) for x in range(8) if self.passable(p:=(x,y)) and p not in blocked and not self.risk(p) and not self.occupied(p,h['id']) and all(distance(p,other['p'])>=3 for other in carriers)]
      route=self.path(h['p'],choices,h)
      if route and self.move(h,route):did=True
   if not did:break
 def spend_leaving(self,h):
  h['left']=False;self.spend(h,'leave_site');h['left']=True
 def run(self):
  for rnd in range(1,self.limit+1):
   self.rnd=rnd
   for h in self.h:h['ap']=2 if not h['down'] and not h['left'] else 0;h['shield']=0
   self.publish();self.policy()
   if all(h['left'] for h in self.h):break
   self.environment()
   if not self.alive():break
  return dict(mission=self.b['id'],goals=sorted(self.goals),extra=sorted(self.extra),difficulty=self.difficulty,variant=self.variant,style=self.style,gear=self.gear,level=self.level,rounds=self.rnd,limit=self.limit,ap=self.ap_used,damage=self.damage_taken,healthy_extracted=sum(h['left'] and not h['down'] for h in self.h),downed=sum(h['down'] for h in self.h),success=self.all_secured() and all(h['left'] and not h['down'] for h in self.h),secured=[k for k,o in self.objects.items() if o['secured'] and k not in self.control_ids],lost=[k for k,o in self.objects.items() if o['lost']],controls=sum(self.objects[k]['done'] for k in self.control_ids),spawned=self.spawned,used=self.used,log=self.log)
