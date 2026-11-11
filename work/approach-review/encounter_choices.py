"""Operational-choice extension of the existing offline tactical referee."""
from pathlib import Path
from copy import deepcopy
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/integrated-review'))
from party import Party,Lab,distance,adjacent,inside,SITUATIONS
SPEC=json.loads((ROOT/'game/data/final_design/approach_review_contract.json').read_text())
PROTO={p['id']:p for p in json.loads((ROOT/'game/data/final_design/progression_relationship.json').read_text())['protocols']}

def extras(board,goals):
 out={o['id'] for o in board['objectives']}-set(goals)
 if board['id']=='M17':out-=({'isolate'} if 'repair2' in goals else {'repair1','repair2'})
 if board['id']=='M24':out={'archive'}
 return out

class ChoiceBattle(Party):
 def __init__(self,*args,approach='safe',watchers=None,trained=(),trust=None,ambition=False,**kw):
  super().__init__(*args,**kw);self.approach=approach;self.spec=SPEC['services'].get(self.b['id']);self.watchers=watchers or tuple(range(len(self.spec['posts']))) if self.spec else ()
  for h in self.h:h['tools']=[k for k,v in self.gear.items() if type(v) is int and v==h['id'] and k in ['insulation','shield','winch']]
  self.watches={};self.steady={};self.service_done=False;self.service_failed=False;self.service_ticks=0;self.service_contributors=set();self.service_history=[];self.hit_during_watch={};self.freed_for_primary=False
  self.trained=set(tuple(x) for x in trained);self.explicit_trust=trust or {(a,b):60 for a in self.party for b in self.party if a!=b}
  for h in self.h:h['protocols']=[k for k in PROTO if any(h['name'] in p[:2] and p[2]==k for p in self.trained)]
  for a in self.h:
   for b in self.h:
    if a['id']!=b['id']:self.trust[(a['id'],b['id'])]=self.explicit_trust.get((a['name'],b['name']),0)
  if ambition:
   extra=extras(self.b,self.goals);self.extra|=extra;self.wanted|=extra
  if self.spec:
   self.b['service_spec']={**self.spec,'source_hp':self.e[self.spec['source_enemy']]['hp']}
   # Same canonical authored id in every plan; its completion is an optional fact.
   o=dict(id='live_service',label=self.spec['label'],kind='watch',cell=self.spec['posts'][0],p=tuple(self.spec['posts'][0]),work=0,hp=999,prerequisites=[],progress=0,done=False,secured=False,lost=False,stable=True,carrier=None,started=None,ticks=0,index=0,shield=0,completed_round=None,contributions=[])
   self.objects['live_service']=o;self.b['objectives'].append(deepcopy(o))
   if approach!='safe':self.extra.add('live_service');self.wanted.add('live_service')
 def spend(self,h,action,**kw):
  if action=='attack' and getattr(self,'spec',None) and kw.get('target')==self.spec['source_enemy'] and self.e[kw['target']]['hp']<=0:
   self.receipt('machine_destroyed',source=kw['target'],repair_supplies=2,repair_projects=1)
  super().spend(h,action,**kw)
 def power_live(self):return self.spec is not None and not all(self.objects[k]['done'] for k in self.spec['linked_controls'])
 def publish(self):
  super().publish();self.watches={};self.steady={};self.hit_during_watch={}
 def task_action(self,h,k):
  if k=='live_service':return None
  return super().task_action(h,k)
 def hit_objects(self,p,damage,source):
  # Stations are existing infrastructure, not an extra indestructible enemy shield.
  super().hit_objects(p,damage,source)
 def watch(self,a,post):
  h=self.h[a];assert self.spec and 0<=post<len(self.spec['posts']) and self.rnd<=self.spec['deadline'] and not self.service_done and not self.service_failed
  assert h['p']==tuple(self.spec['posts'][post]) and h['carry'] is None and not h['down'] and not h['left'] and h['ap']>=1
  assert post not in self.watches and a not in [x['actor'] for x in self.watches.values()]
  self.watches[post]=dict(actor=a,start_hp=h['hp'],at=h['p']);self.spend(h,'service_watch',post=post)
 def protocol_ready(self,key,a,b,require_training=True):
  x,y=self.h[a],self.h[b];token=tuple(sorted([x['name'],y['name']]))+(key,)
  if require_training and (token not in self.trained or min(self.trust.get((a,b),0),self.trust.get((b,a),0))<60):return False
  tags=set(PROTO[key]['tags'])
  marker=self.protection.get((a,b,key));physical=False
  if marker:
   helper,rnd,at=marker;h=self.h[helper];physical=rnd==self.rnd and not h['down'] and not h['left'] and h['p']==at
  consent=self.prepared.get(('agreement',key,a,b),False)
  context=set()
  if self.spec and self.e[self.spec['source_enemy']]['type']=='skimmer':context.add('electrical')
  if self.b['id'] in ['M10','M21','S04']:context.add('fall')
  for observer,target in [(x['name'],y['name']),(y['name'],x['name'])]:
   rule=SITUATIONS.get(observer,dict(protocol_tags=[],when=[]))
   relevant=tags&set(rule['protocol_tags']) and ('any' in rule['when'] or context&set(rule['when']))
   restricted=self.relations.get((observer,target),False) or self.relations.get((observer,'leader'),False)
   if not relevant or not restricted:continue
   actor=x if observer==x['name'] else y
   if observer=='lin':permitted=(physical and distance(self.h[marker[0]]['p'],actor['p'])==1) or any(distance(actor['p'],p)<=1 for p in self.anchors)
   elif observer=='chen':permitted=not self.power_live() or all(h['p'] in self.insulated for h in [x,y]) and self.objects.get('live_service',{}).get('shield',0)>=3
   elif observer=='ye':permitted=not self.power_live() or all(h['p'] in self.insulated for h in [x,y])
   elif observer=='he':permitted=bool(self.exits) and self.limit>0 and bool(self.path(actor['p'],self.exits,actor))
   else:permitted=consent
   if not permitted:return False
  return True
 def guarded_watch(self,a,b,post):
  assert self.protocol_ready('protected_work',a,b)
  x,y=self.h[a],self.h[b];assert a!=b and distance(x['p'],y['p'])==1 and y['carry'] is None and not y['down'] and not y['left'] and y['ap']>=1
  assert (tuple(sorted([a,b])),'protected_work',self.rnd) not in self.protocol_used
  self.watch(a,post);self.spend(y,'protected_service',operator=a,post=post);x['shield']=max(x['shield'],2)
  self.steady[a]=dict(guard=b,at=y['p'],used=False);self.protocol_used.add((tuple(sorted([a,b])),'protected_work',self.rnd))
 def cover_watchers(self,a,b):
  assert self.protocol_ready('mutual_cover',a,b)
  Lab.protocol(self,'mutual_cover',a,b)
  for i in [a,b]:
   if i in [w['actor'] for w in self.watches.values()]:self.steady[i]=dict(guard=None,at=None,used=False)
 def hit_hero(self,h,damage,source,electric=False):
  before=h['hp'];was_watched=h['id'] in [w['actor'] for w in self.watches.values()]
  super().hit_hero(h,damage,source,electric)
  if was_watched and h['hp']<before:
   marker=self.steady.get(h['id']);guard=self.h[marker['guard']] if marker and marker['guard'] is not None else None
   valid=marker and not marker['used'] and not h['down'] and source in self.e and not electric and (guard is None or not guard['down'] and not guard['left'] and guard['p']==marker['at'] and distance(guard['p'],h['p'])==1)
   if valid:
    marker['used']=True;self.receipt('service_guard_absorbs_interruption',actor=h['id'],guard=marker['guard'],source=source)
    if guard:self.service_contributors.add(guard['name'])
   else:self.hit_during_watch[h['id']]=True
  elif was_watched and source in self.e and self.steady.get(h['id'],{}).get('guard') is not None:
   self.service_contributors.add(self.h[self.steady[h['id']]['guard']]['name'])
 def restore_power(self,a,control):
  h=self.h[a];assert self.spec and control in self.spec['linked_controls'] and self.objects[control]['done'] and distance(h['p'],self.objects[control]['p'])<=1 and h['carry'] is None
  self.spend(h,'restore_power',target=control)
  o=self.objects[control];o.update(done=False,secured=False,progress=0,completed_round=None)
  enemy=self.e[self.spec['source_enemy']];enemy['disabled']=False
  # Recompute warnings, without resetting this round's paid watches or protections.
  old=deepcopy(self.e);pending=deepcopy(self.pending);logs=len(self.log);Party.publish(self)
  for key,value in old.items():
   if key!=enemy['id']:self.e[key]=value
  self.pending=pending;self.log=self.log[:logs];self.receipt('power_restored_warning',source=enemy['id'],cells=self.e[enemy['id']]['intent'])
 def precise_pull(self,a,b,enemy_id,destination):
  assert self.protocol_ready('coordinated_pull',a,b)
  x,y=self.h[a],self.h[b];e=self.e[enemy_id];p=tuple(destination)
  assert e['type'] in ['hauler','sentinel'] and e['hp']>0 and all(not h['down'] and not h['left'] and h['carry'] is None and h['ap']>=1 and distance(h['p'],e['p'])==1 for h in [x,y])
  assert distance(e['p'],p)==1 and self.passable(p) and not self.occupied(p)
  token=(tuple(sorted([a,b])),'coordinated_pull',self.rnd);assert token not in self.protocol_used
  old=e['p'];delta=(p[0]-old[0],p[1]-old[1]);e['p']=p;e['intent']=[(q[0]+delta[0],q[1]+delta[1]) for q in e['intent'] if inside((q[0]+delta[0],q[1]+delta[1]))]
  # Off-rail haul machines stop their drive until moved back to a valid rail cell;
  # they do not teleport back on the next tick. Motor intact, bus remains powered.
  if e.get('rail'):
   rail=list(map(tuple,e['rail']));e['off_rail']=p not in rail
   if not e['off_rail']:e['rail_index']=rail.index(p)
  for h in [x,y]:self.spend(h,'coordinated_pull',target=enemy_id,destination=p)
  self.protocol_used.add(token)
 def basic_push(self,actor,target):
  super().basic_push(actor,target);e=self.e[target]
  if e.get('rail'):
   rail=list(map(tuple,e['rail']));e['off_rail']=e['p'] not in rail
   if not e['off_rail']:e['rail_index']=rail.index(e['p'])
 def working(self,e):return not e.get('off_rail',False) and super().working(e)
 def relay_path(self,a,b,path):
  assert self.protocol_ready('relay_carry',a,b)
  x,y=self.h[a],self.h[b];path=list(map(tuple,path));assert a!=b and distance(x['p'],y['p'])==1 and x['carry'] is not None and y['carry'] is None
  assert all(not h['down'] and not h['left'] and h['ap']>=1 for h in [x,y]) and path and path[0]==y['p']
  assert sum(self.cost(p) for p in path[1:])<=3 and all(distance(p,q)==1 and self.passable(q) and q not in self.barriers for p,q in zip(path,path[1:])) and not self.occupied(path[-1],b)
  token=(tuple(sorted([a,b])),'relay_carry',self.rnd);assert token not in self.protocol_used
  oid=x['carry'];x['carry']=None;y['carry']=oid;self.objects[oid]['carrier']=b;y['p']=path[-1]
  for h in [x,y]:self.spend(h,'relay_carry',target=oid,path=path if h is y else None)
  self.receipt('transport_path',actor=b,cargo=oid,path=path,at=y['p']);self.protocol_used.add(token)
 def move_to(self,h,targets):
  route=self.path(h['p'],targets,h)
  return bool(route and len(route)>1 and self.move(h,route))
 def support_service(self,operators):
  # Actual current warning and geography determine support, not the character name alone.
  source=self.e[self.spec['source_enemy']]
  for h in self.alive():
   if h['id'] in operators or h['ap']<=0 or h['carry'] is not None:continue
   if 'shield' in h['tools'] and self.used.get((h['id'],'shield'),0)==0:
    for e in self.e.values():
     protected=[self.h[i] for i in operators if self.h[i]['p'] in e['intent']]
     if e['type']!='sentinel' or not self.working(e) or not protected:continue
     cells=[p for p in e['intent'] if self.passable(p) and not self.occupied(p) and distance(e['p'],p)<max(distance(e['p'],w['p']) for w in protected)]
     for p in cells:
      if distance(h['p'],p)>1 and h['ap']>=2:
       route=self.path(h['p'],adjacent(p),h)
       if route and sum(self.cost(z) for z in route[1:])<=self.budget(h):self.move(h,route)
      if distance(h['p'],p)<=1 and h['ap']>=1:self.use(h['id'],'shield',destination=p);break
     if self.used.get((h['id'],'shield'),0):break
   if self.approach=='dismantle' and source['hp']>0:
    for _ in range(2):
     if h['ap']<=0 or source['hp']<=0:break
     if distance(h['p'],source['p'])==1:source['hp']-=2;self.spend(h,'attack',target=source['id'],damage=2)
     elif not self.move_to(h,adjacent(source['p'])):break
   elif self.skills_enabled and any(self.risk(self.h[i]['p']) for i in operators):
    if self.cast(h,'chen_1',source['id']) or self.cast(h,'ye_1',source['id']):continue
    if h['ap']>=2 and any(self.usable(h,key) for key in ['chen_1','ye_1']):
     spots=[(x,y) for y in range(8) for x in range(8) if self.passable((x,y)) and not self.occupied((x,y),h['id']) and distance((x,y),source['p'])<=3]
     path=self.path(h['p'],spots,h)
     if path and sum(self.cost(p) for p in path[1:])<=self.budget(h):
      self.move(h,path)
      if self.cast(h,'chen_1',source['id']) or self.cast(h,'ye_1',source['id']):continue
    if self.usable(h,'ye_3'):
     post=next((self.h[i]['p'] for i in operators if self.rows[self.h[i]['p'][1]][self.h[i]['p'][0]]=='~' and self.h[i]['p'] not in self.insulated),None)
     if post and self.cast(h,'ye_3',destination=post):continue
    # A real shield only works if it lies on a ray ahead of the operator.
    for e in self.e.values():
     if not self.working(e) or e['type']!='sentinel':continue
     protected=[self.h[i] for i in operators if self.h[i]['p'] in e['intent']]
     positions=[p for p in e['intent'] if protected and distance(h['p'],p)==1 and self.passable(p) and not self.occupied(p) and distance(e['p'],p)<max(distance(e['p'],x['p']) for x in protected)]
     if positions and self.cast(h,'he_1',destination=positions[0]):break
 def policy(self):
  if self.rnd<=self.delay:return
  active=self.spec and self.approach!='safe' and not self.service_done and not self.service_failed
  if not active:return super().policy()
  if any(self.h[a]['down'] or (self.h[a]['hp']<=3 and not self.service_done) for a in self.watchers):
   self.service_failed=True;self.objects['live_service']['lost']=True;self.receipt('abandon_optional_service',reason='撤回低生命值值守者，保留主目标');return super().policy()
  reserved=set();operators=[]
  for post,a in enumerate(self.watchers):
   h=self.h[a]
   if h['down'] or h['left'] or h['carry'] is not None:continue
   target=tuple(self.spec['posts'][post])
   for _ in range(2):
    if h['ap']<=0:break
    if h['p']!=target:
     if not self.move_to(h,[target]):break
    else:break
   if h['p']==target and h['ap']>=1:
    if 'insulation' in h['tools'] and target not in self.insulated and h['ap']>=2:
     self.use(a,'insulation',destination=target)
    guarded=False
    if self.approach=='protected' and len(self.spec['posts'])==1:
     for guard in self.alive():
      if guard['id']==a or guard['carry'] is not None or guard['ap']<1 or not self.protocol_ready('protected_work',a,guard['id']):continue
      if distance(guard['p'],h['p'])>1 and guard['ap']>=2:self.move_to(guard,adjacent(h['p']))
      if distance(guard['p'],h['p'])==1 and guard['ap']>=1:self.guarded_watch(a,guard['id'],post);reserved.add(guard['id']);guarded=True;break
    if not guarded:self.watch(a,post)
    reserved.add(a);operators.append(a)
  if self.approach=='protected' and len(operators)==2:
   a,b=operators
   if self.protocol_ready('mutual_cover',a,b) and min(self.h[a]['ap'],self.h[b]['ap'])>=1 and distance(self.h[a]['p'],self.h[b]['p'])<=2:self.cover_watchers(a,b)
  self.support_service(operators)
  # Preserve the declared watch, rather than the generic policy walking it away.
  ap={i:self.h[i]['ap'] for i in reserved}
  for i in reserved:self.h[i]['ap']=0
  oldstyle=self.style;self.style='rush'
  super().policy();self.style=oldstyle
  for i,v in ap.items():self.h[i]['ap']=v
 def environment(self):
  super().environment()
  if not self.spec or self.service_done or self.service_failed:return
  valid=self.power_live() and len(self.watches)==len(self.spec['posts'])
  for post,w in self.watches.items():
   h=self.h[w['actor']];valid=valid and not h['down'] and not h['left'] and h['p']==tuple(self.spec['posts'][post]) and not self.hit_during_watch.get(h['id'],False)
  for a,marker in self.steady.items():
   if marker['guard'] is not None:
    guard=self.h[marker['guard']]
    if guard['down'] or guard['left'] or guard['p']!=marker['at']:valid=False
  self.service_ticks=self.service_ticks+1 if valid else 0
  if not valid:self.service_contributors.clear()
  self.service_history.append(dict(round=self.rnd,powered=self.power_live(),valid=bool(valid),ticks=self.service_ticks,operators=[self.party[w['actor']] for w in self.watches.values()]))
  if valid:
   self.service_contributors.update(self.party[w['actor']] for w in self.watches.values())
   self.receipt('service_tick',operators=[w['actor'] for w in self.watches.values()],ticks=self.service_ticks)
  if self.service_ticks>=self.spec['consecutive_rounds']:
   self.service_done=True;o=self.objects['live_service'];o['contributions']=[dict(actor=self.party.index(a),action='service_watch',round=self.rnd) for a in sorted(self.service_contributors)];self.complete(o);self.receipt('live_service_completed',source=self.spec['id'])
  elif self.rnd>=self.spec['deadline']:
   self.service_failed=True;self.objects['live_service']['lost']=True;self.receipt('live_service_window_closed',source=self.spec['id'])
 def run(self):
  r=super().run();r.update(approach=self.approach,service_secured=self.service_done,service_ticks=self.service_history,machinery_intact=self.e[self.spec['source_enemy']]['hp']>0 if self.spec else True,watchers=self.watchers,trained=[list(t) for t in sorted(self.trained)],protocol_effects=sum(x['action']=='service_guard_absorbs_interruption' for x in self.log))
  return r
