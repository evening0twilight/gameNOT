"""Offline reference rules for0.11; not production game code."""
from pathlib import Path
from copy import deepcopy
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/approach-review'))
import encounter_choices as old
from encounter_choices import Party,Lab,distance,adjacent,inside
CONTRACT=json.loads((ROOT/'game/data/final_design/player_choice_contract.json').read_text())
HISTORICAL=json.loads((ROOT/'game/data/final_design/approach_review_contract.json').read_text())
SPEC={**HISTORICAL,'services':deepcopy(CONTRACT['services']),'mission_roles':CONTRACT['mission_roles']}
old.SPEC=SPEC
class ChoiceBattle(old.ChoiceBattle):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw)
  if self.spec:self.spec=deepcopy(self.spec)
  self.asset_spec=CONTRACT['asset_registry'].get(self.b['id']);self.field_effects=[];self.opened_exit=False
  self.current_helpers=set()
 def protocol_ready(self,key,a,b):
  return super().protocol_ready(key,a,b,require_training=key not in ['protected_work','mutual_cover'])
 def cover_watchers(self,a,b):
  assert self.protocol_ready('mutual_cover',a,b)
  x,y=self.h[a],self.h[b];token=(tuple(sorted([a,b])),'mutual_cover',self.rnd)
  assert a!=b and distance(x['p'],y['p'])<=2 and token not in self.protocol_used
  assert all(h['ap']>=1 and not h['down'] and not h['left'] and h['carry'] is None for h in [x,y])
  for h in [x,y]:
   h['shield']=max(2,h['shield']);self.spend(h,'mutual_cover',partner=b if h is x else a)
   if h['id'] in [w['actor'] for w in self.watches.values()]:self.steady[h['id']]=dict(guard=None,at=None,used=False)
  self.protocol_used.add(token);self.protection.pop((a,b,'mutual_cover'),None)
 def publish(self):
  super().publish();self.current_helpers=set()
 def spend(self,h,action,**kw):
  if action=='attack' and getattr(self,'spec',None) and self.b['id'] in CONTRACT['investments'] and kw.get('target')==self.spec['source_enemy'] and self.e[kw['target']]['hp']<=0:
   self.receipt('machine_destroyed',source=kw['target'],repair_supplies=2,repair_projects=1,support_last_day=CONTRACT['investments'][self.b['id']]['last_day'])
  Party.spend(self,h,action,**kw)
 def hit_hero(self,*a,**kw):
  previous=set(self.service_contributors);super().hit_hero(*a,**kw)
  self.current_helpers.update(self.service_contributors-previous);self.service_contributors=previous
 def restore_power(self,a,control):
  # Ordinary controls remain reversible even on maps whose extra task was removed.
  original=self.spec;enemy=next(e for e in self.e.values() if control in e.get('disable_requires',[]))
  self.spec=dict(source_enemy=enemy['id'],linked_controls=enemy['disable_requires'])
  try:return super().restore_power(a,control)
  finally:self.spec=original
 def policy(self):
  if self.spec and self.approach!='safe' and not self.service_done and not self.service_failed and any(not self.objects[k]['done'] for k in self.spec.get('prerequisites',[])):
   previous=self.style;self.style='rush'
   try:return Party.policy(self)
   finally:self.style=previous
  # Planner only: reserve a single-use mat for an actually wet operating point.
  # Manual use remains legal; changing stages never refills equipment charges.
  saved={h['id']:h['tools'][:] for h in self.h}
  for h in self.h:
   if 'insulation' not in h['tools']:continue
   exhausted=self.used.get((h['id'],'insulation'),0)>=1
   dry=False
   if self.spec and h['id'] in self.watchers:
    p=self.spec['posts'][list(self.watchers).index(h['id'])];dry=self.rows[p[1]][p[0]]!='~'
   if exhausted or dry:h['tools']=[x for x in h['tools'] if x!='insulation']
  try:return super().policy()
  finally:
   for h in self.h:h['tools']=saved[h['id']]
 def watch(self,a,post):
  assert self.spec and all(self.objects[k]['done'] for k in self.spec.get('prerequisites',[])), 'required physical repair/wiring not completed'
  return super().watch(a,post)
 def environment(self):
  # Shared combat/environment resolver, with four explicit task cadences below.
  Party.environment(self)
  if self.spec and not self.service_done and not self.service_failed:
   valid=self.power_live() and len(self.watches)==len(self.spec['posts'])
   for post,w in self.watches.items():
    h=self.h[w['actor']];valid=valid and not h['down'] and not h['left'] and h['p']==tuple(self.spec['posts'][post]) and not self.hit_during_watch.get(h['id'],False)
   for marker in self.steady.values():
    if marker['guard'] is not None:
     guard=self.h[marker['guard']]
     if guard['down'] or guard['left'] or guard['p']!=marker['at']:valid=False
   mode=self.spec['mode'];before=self.service_ticks
   if valid:self.service_ticks+=1
   elif mode=='consecutive':self.service_ticks=0;self.service_contributors.clear()
   self.service_history.append(dict(round=self.rnd,powered=self.power_live(),valid=bool(valid),ticks=self.service_ticks,mode=mode,operators=[self.party[w['actor']] for w in self.watches.values()]))
   if valid:
    self.service_contributors.update(self.party[w['actor']] for w in self.watches.values());self.service_contributors.update(self.current_helpers);self.receipt('service_tick',operators=[w['actor'] for w in self.watches.values()],ticks=self.service_ticks)
    if mode=='accumulate':
     changed=[]
     for x,y in self.spec['drain_stages'][before]:
      if self.rows[y][x]=='~':self.rows[y][x]='.';changed.append([x,y])
     self.field_effects.append(dict(kind='drained',round=self.rnd,cells=changed));self.receipt('drain_stage',cells=changed)
    if mode=='sequence' and self.service_ticks<len(self.spec['stages']):
     self.spec['posts']=deepcopy(self.spec['stages'][self.service_ticks]);self.objects['live_service']['p']=tuple(self.spec['posts'][0])
   if self.service_ticks>=self.spec['consecutive_rounds']:
    self.service_done=True;o=self.objects['live_service'];o['contributions']=[dict(actor=self.party.index(a),action='service_watch',round=self.rnd) for a in sorted(self.service_contributors)];self.complete(o);self.receipt('live_service_completed',source=self.spec['id'])
   elif self.rnd>=self.spec['deadline']:
    self.service_failed=True;self.objects['live_service']['lost']=True;self.receipt('live_service_window_closed',source=self.spec['id'])
  if self.spec and self.service_done and 'extra_exit' in self.spec and not self.opened_exit and all(self.objects[k]['done'] for k in self.spec['exit_requires']):
   p=tuple(self.spec['extra_exit']);assert self.passable(p)
   if p not in self.exits:self.exits.append(p)
   self.opened_exit=True;self.field_effects.append(dict(kind='exit_opened',round=self.rnd,cell=p));self.receipt('optional_exit_opened',cell=p)
 def run(self):
  r=super().run();r['field_effects']=deepcopy(self.field_effects);r['cooperation_actions']=sum(x['action'] in ['protected_service','protected_work','mutual_cover','relay_carry','coordinated_pull'] for x in self.log);r['advanced_actions']=sum(x['action'] in ['relay_carry','coordinated_pull'] for x in self.log)
  if self.asset_spec:r['machinery_intact']=self.e[self.asset_spec['source_enemy']]['hp']>0
  r['player_choice_version']='0.11';return r
