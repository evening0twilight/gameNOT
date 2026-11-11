"""Finite positive relationship payoffs in the real campaign ledger.
No relationship points are awarded for clicking an agreement, teaching or docking.
"""
from model import *
import importlib.util
_s=importlib.util.spec_from_file_location('identity_campaign_base',ROOT/'work/cooperation-value-review/current_campaign.py')
base=importlib.util.module_from_spec(_s);sys.modules[_s.name]=base;_s.loader.exec_module(base)
c=base.c;BaseLedger=c.Ledger
NODES={n['id']:n for n in json.loads((ROOT/'game/data/final_design/stories.json').read_text())['relationship_nodes']}
def atomic_identity(fn):
 def call(self,*args,**kw):
  before=deepcopy(self.__dict__)
  try:return fn(self,*args,**kw)
  except Exception:self.__dict__=before;raise
 return call
class RelationshipLedger(BaseLedger):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.pacts={};self.apprentices=set();self.dispatch=None;self.identity_training='none';self.identity_pacts=False;self.identity_dock=False;self.pact_revision_days={};self.training_completed={}
 @atomic_identity
 def scene(self,nid,choice_id=None):
  if not nid.startswith('R'):return super().scene(nid,choice_id)
  node=NODES[nid];choice=choice_id or ('agreement' if self.identity_pacts else 'distance')
  assert choice in ['agreement','distance']
  super().scene(nid,choice)
  if all(self.crew[a]['joined'] and not self.crew[a]['withdrawn'] for a in node['actors']):
   self.pacts[nid]=choice;self.receipt('relationship_choice',node=nid,actors=node['actors'],choice=choice)
 @atomic_identity
 def craft(self,item,n):
  assert item=='med_dose','retired consumable'
  return super().craft(item,n)
 @atomic_identity
 def buy_tool(self,item):
  assert next(e for e in json.loads((ROOT/'game/data/final_design/equipment.json').read_text())['items'] if e['id']==item).get('production_status','active')=='active','retired tool'
  return super().buy_tool(item)
 def medical_pack_limit(self):return 3 if self.fac['workshop']>=2 else 2
 @atomic_identity
 def revise_pact(self,nid,choice):
  assert self.phase=='camp' and self.day<=23 and self.scenes<2 and nid in self.pacts
  assert choice in ['agreement','distance'] and choice!=self.pacts[nid] and self.pact_revision_days.get(nid)!=self.day
  assert all(self.crew[a]['joined'] and not self.crew[a]['withdrawn'] for a in NODES[nid]['actors'])
  self.scenes+=1;self.pacts[nid]=choice;self.pact_revision_days[nid]=self.day
  self.receipt('relationship_choice_revised',node=nid,actors=NODES[nid]['actors'],choice=choice)
 def pair_history(self,pair):
  good=[]
  for mid in self.settled:
   contributors=set(a for r in self.records if r['kind']=='objective_completed' and r['mission']==mid for a in r['contributors'])
   breached=any(r['kind']=='promise_breach' and r['mission']==mid and (not any(k in r for k in ['actor','target','observer']) or set(pair)&{r.get('actor'),r.get('target'),r.get('observer')}) for r in self.records)
   if set(pair)<=contributors and not breached:good.append(mid)
  return sorted(good)
 def pact_for(self,pair,dispatch=False):
  for nid,choice in self.pacts.items():
   if choice!='agreement' or set(NODES[nid]['actors'])!=set(pair) or dispatch and nid not in ['R04','R10']:continue
   if len(self.pair_history(pair))<2:continue
   # Actual unresolved conditional-cooperation band remains relevant. No new
   # arbitrary affection threshold, and agreement never clears old memories.
   self.update_bands()
   if any(self.bands[a+'>'+b]>=2 for a,b in [pair,pair[::-1]]):continue
   if not all(self.healthy(a) for a in pair):continue
   return nid
  return None
 def training_slots(self,a):
  # Chapters unlock curriculum stages. Unused stages persist; pre-join stages
  # are represented by the recruit's existing XP and cannot be purchased again.
  if a not in self.crew:return 0
  unlocked=max(0,(min(self.day,23)-1)//6-(CHARS[a]['join']-1)//6+1)
  return max(0,unlocked-self.training_completed.get(a,0))
 def training_available(self,a):
  return self.phase=='camp' and 1<=self.day<=23 and self.healthy(a) and a not in self.used and self.crew[a]['xp']<100 and self.crew[a]['fatigue']+6<=100 and self.training_slots(a)>0
 def mentor_candidates(self):
  out=[];chapter=(self.day-1)//6
  for mentor,learner in itertools.permutations(self.crew,2):
   if not self.training_available(learner) or not self.healthy(mentor) or mentor in self.used or self.crew[mentor]['fatigue']+6>100:continue
   amount=min(24,self.crew[mentor]['xp']-self.crew[learner]['xp'],100-self.crew[learner]['xp'])
   if amount<=min(12,100-self.crew[learner]['xp']) or (learner,chapter) in self.apprentices or not self.pact_for([mentor,learner]):continue
   out.append((mentor,learner,amount))
  return out
 @atomic_identity
 def mentor(self,mentor,learner):
  options=self.mentor_candidates();assert (mentor,learner) in [(m,l) for m,l,v in options]
  amount=next(v for m,l,v in options if (m,l)==(mentor,learner));assert self.projects<2 and self.resources['supplies']>=2
  self.claim_project([mentor,learner]);self.spend(supplies=2)
  for a in [mentor,learner]:self.crew[a]['fatigue']+=6
  self.crew[learner]['xp']+=amount;self.apprentices.add((learner,(self.day-1)//6));self.training_completed[learner]=self.training_completed.get(learner,0)+1
  self.receipt('mentorship',mentor=mentor,learner=learner,xp=amount,projects=1,supplies=2,fatigue_each=6,stage_used=self.training_completed[learner],history=self.pair_history([mentor,learner]))
  self.receipt('training_gain',actors=[learner],gains={learner:amount},source='mentorship')
 @atomic_identity
 def train(self,actors,protocol=None):
  assert protocol is None and 1<=len(actors)<=2 and all(self.training_available(a) for a in actors)
  self.claim_project(actors);self.spend(supplies=len(actors));gains={}
  for a in actors:
   gains[a]=min(12,100-self.crew[a]['xp']);self.crew[a]['xp']+=gains[a];self.crew[a]['fatigue']+=6;self.training_completed[a]=self.training_completed.get(a,0)+1
  self.receipt('training',actors=actors,protocol=None,rule='stage12_carry',xp=gains,fatigue=6,supplies=len(actors),projects=1,stages={a:self.training_completed[a] for a in actors})
  self.receipt('training_gain',actors=actors,gains=gains,source='solo')
 def dispatch_options(self,party):
  out=[]
  if self.phase!='briefing' or self.resources['supplies']<2:return out
  for field in party:
   if field not in self.crew or not self.eligible(field):continue
   for support in self.crew:
    if support in party or not self.eligible(support,8):continue
    node=self.pact_for([field,support],dispatch=True)
    if node:out.append(dict(node=node,field=field,support=support,mission=f'M{self.day:02}'))
  return out
 @atomic_identity
 def select_dispatch(self,party,plan=None):
  assert self.phase=='briefing'
  assert plan is None or plan in self.dispatch_options(party)
  self.dispatch=deepcopy(plan)
 def refresh_dispatch(self,party):
  assert self.phase=='briefing'
  if self.dispatch is not None and self.dispatch not in self.dispatch_options(party):self.dispatch=None;return False
  return True
 @atomic_identity
 def deploy(self,mid,party,support=None,pack=None):
  assert set(pack or {})<={'med_dose'},'retired packed consumable'
  chosen=self.dispatch
  if chosen:
   assert chosen in self.dispatch_options(party) and mid==chosen['mission']
   support=chosen['support'];self.spend(supplies=2)
  super().deploy(mid,party,support,pack)
  if chosen:self.receipt('dispatch_plan',**chosen,supplies=2,exit=[7,7],replaces_default_exit=True)
 @atomic_identity
 def settle(self,packet):
  chosen=deepcopy(self.dispatch);super().settle(packet)
  if chosen:
   # Existing support still earns its2XP and8fatigue, but boat handling replaces
   # the usual +1supply logistics output. Do not charge or remove it twice.
   self.resources['supplies']-=1;self.rows[-1]['resources_after_mission']=deepcopy(self.resources)
   self.receipt('dispatch_logistics_foregone',mission=packet['mission'],supplies=1)
   self.dispatch=None
 def summary(self):
  r=super().summary();r['positive_relationships']=dict(choices=self.pacts,mentoring=sum(x['kind']=='mentorship' for x in self.records),dispatches=sum(x['kind']=='dispatch_plan' for x in self.records));return r
