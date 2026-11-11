"""Canonical battle receipts -> one social owner. Offline review only."""
from pathlib import Path
from copy import deepcopy
import sys,json,itertools,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'player-experience'))
from appraisal import Session,Direction
from reference import band_after
ROOT=Path(__file__).resolve().parents[2]
INITIAL=json.loads((ROOT/'game/data/initial_relationships.json').read_text());CHARS={x['id']:x for x in json.loads((ROOT/'game/data/characters.json').read_text())}
def qualified(battle,result,oid,party):
 """Credit actual useful work, not merely touching/passing an already safe object."""
 o=battle.objects[oid];allowed={'service_watch','interact','protected_work','lin_1','lin_3','lin_5','stabilize','crowbar','cutter','battery','ye_5','chen_5'}
 actors=[]
 for c in o['contributions']:
  if c['action'] in allowed and c['round']<= (o['completed_round'] or 999):
   a=party[c['actor']]
   if a not in actors:actors.append(a)
 if o['kind'] in ['rescue','cargo']:
  # Credit the surviving actual transport path, including sensible detours.
  # Erasing loops prevents out-and-back handoffs from manufacturing contribution.
  walk=[tuple(o['cell'])];owners=[]
  for x in result['log']:
   if x['action'] in ['move','transport_path'] and x.get('cargo')==oid and x.get('round',0)<=(o['completed_round'] or 999):
    for p in x.get('path',[x['at']]):
     p=tuple(p)
     if p==walk[-1]:continue
     if p in walk:
      i=walk.index(p);walk=walk[:i+1];owners=owners[:i]
     else:walk.append(p);owners.append(party[x['actor']])
  minimum=min(2,len(owners));progress={a:owners.count(a) for a in set(owners)}
  for a,amount in progress.items():
   if amount>=max(1,minimum) and a not in actors:actors.append(a)
  if minimum==0 and tuple(o['cell']) in battle.exits:
   delivery=next((x for x in result['log'] if (x['action']=='extract' and x.get('target')==oid) or (x['action']=='leave_site' and x.get('delivered')==oid)),None)
   if delivery and party[delivery['actor']] not in actors:actors.append(party[delivery['actor']])
 return [a for a in actors if a in CHARS]

class Social:
 def __init__(self):
  self.people={a:Session(a) for a in CHARS};self.settled=set();self.claims=set();self.history=[];self.source_registry={};self.last_day=0;self.bands={}
  for x in INITIAL:
   self.people[x['observer']].directions[x['target']]=Direction(grudge=x['grudge'],trust=x['trust'],grudge_categories=tuple(x['grudge_categories']))
  self.closeness={(x['observer'],x['target']):x['closeness'] for x in INITIAL}
 def sync(self,ledger):
  for a,s in self.people.items():
   ledger.crew[a]['stress']=s.stress
   for b,d in s.directions.items():
    key=a+'>'+b
    if key in ledger.rel:ledger.rel[key].update(grudge=d.grudge,trust=d.trust,memories=d.memories,facts=d.facts)
  ledger.update_bands()
 def restrictions(self,party,day):
  blocked={}
  for a in party:
   for b in party+['leader']:
    if a==b:continue
    d=self.people[a].direction(b);key=(a,b);self.bands[key]=band_after(self.bands.get(key,0),d.resentment(day),self.people[a].stress)
    blocked[key]=self.bands[key]>=2
  return blocked
 def settle(self,battle,result,party,day,breach=None):
  before=deepcopy(self.__dict__)
  try:return self._settle(battle,result,party,day,breach)
  except Exception:self.__dict__=before;raise
 def _settle(self,battle,result,party,day,breach):
  mid=battle.b['id']
  if mid in self.settled:return {'duplicate':True}
  assert day>=self.last_day and len(party)==3 and len(set(party))==3
  self.last_day=day
  assert all(a in CHARS or a.startswith('reserve') for a in party)
  joined=[a for a in party if a in self.people];known=joined+['leader'];rows=[]
  # Per-object roots are authored mission/object ids, never action ids or text strings.
  # Only completion of real authored objectives yields relationship credit.
  for oid in sorted(result['secured']):
   if oid in battle.control_ids or oid not in {o['id'] for o in battle.b['objectives']}:continue
   o=battle.objects[oid];assert o['secured'] and not o['lost']
   actors=qualified(battle,result,oid,party)
   if len(actors)<2:continue
   root=mid+':outcome:'+oid
   self.source_registry[root]=dict(mission=mid,object=oid,contributors=actors)
   # Deliberately breaching a commitment is not repaired by labeling the same act help.
   caused=breach is not None and breach.get('caused_object')==oid
   if caused:continue
   for a in actors:
    key=(mid,oid,a)
    if key in self.claims:continue
    self.claims.add(key)
    ev=dict(id=root,mission=mid,day=day,kind='cooperation',outcome='success',known_by=known,witnesses=joined,contributors=actors,responsibility={},evidence='verified',voluntary_contribution=True,relevant_category='fairness',extra_cost=0,self_control=0)
    rows.append(self.people[a].apply(ev,{b:self.closeness.get((a,b),0) for b in joined}))
  # One mission stress outcome, NOT repeated once for every object or pair.
  for a in joined:
   i=party.index(a);damage=sum(x.get('damage',0) for x in result['log'] if x['action']=='damage' and x.get('actor')==i)
   env=any(x['action']=='damage' and x.get('actor')==i and x.get('source') in ['fire','live_water'] for x in result['log'])
   ev=dict(id=mid+':personal-outcome',mission=mid,day=day,kind='cost_overrun',outcome='success' if result['success'] else 'partial' if result['secured'] else 'failed',known_by=known,witnesses=joined,contributors=[],responsibility={},evidence='verified',voluntary_contribution=False,extra_cost=min(3,damage/2),self_control=.5,weather_hazard_experienced=env)
   if breach:ev.update(time_relevant=True,finish=result['rounds'],agreed_finish=breach['deadline'])
   rows.append(self.people[a].apply(ev,{b:self.closeness.get((a,b),0) for b in joined}))
  if breach:
   assert breach['deadline']<result['rounds'] and breach['warned'] and breach['accepted']
   root=mid+':decision:'+breach['id'];self.source_registry[root]=dict(mission=mid,decision=breach['id'],known_by=known)
   for a in joined:
    ev=dict(id=root,mission=mid,day=day,kind='breach',outcome='success' if result['success'] else 'failed',known_by=known,witnesses=joined,contributors=[],responsibility={'leader':1},evidence='verified',voluntary_contribution=False,extra_cost=0,self_control=0,explicit_violation=True,promise=breach['id'],warned=True,deliberate=True,time_relevant=True,finish=result['rounds'],agreed_finish=breach['deadline'])
    ev['personal_effects_accounted']=True
    row=self.people[a].apply(ev,{b:self.closeness.get((a,b),0) for b in joined});rows.append(row)
  self.settled.add(mid);record=dict(mission=mid,day=day,party=party,rows=rows,breach=breach)
  self.history.append(record);return record
 def night_from_ledger(self,ledger,day):
  assert ledger.day==day and ledger.phase=='camp'
  recovered={a for r in ledger.records if r['day']==day and r['kind']=='recovery' for a in r['actors']}
  for a,s in self.people.items():
   if not ledger.crew[a]['joined'] or ledger.crew[a]['withdrawn']:continue
   # Pull real camp stress changes once, then both ledgers advance the same night.
   s.stress=ledger.crew[a]['stress'];s.night(day,recovery_project=a in recovered,meaningful_support=False)
  ledger.night();self.sync(ledger)
 def totals(self,day):
  return {a:dict(stress=round(s.stress,3),self_load=round(s.self_load,3),band=s.self_band,trust={b:round(d.trust,3) for b,d in s.directions.items()},resentment={b:round(d.resentment(day),3) for b,d in s.directions.items()}) for a,s in self.people.items()}

def close_inquiry(session,event,proof,registry):
 """Only registered causes can be investigated. Negative knowledge isn't a currency."""
 root=event['id'];assert root in registry and proof['id']==root and proof['evidence']=='verified'
 before=deepcopy(session.__dict__)
 try:
  session.apply(event);session.confirm(proof)
 except Exception:session.__dict__=before;raise
 return session.__dict__!=before
