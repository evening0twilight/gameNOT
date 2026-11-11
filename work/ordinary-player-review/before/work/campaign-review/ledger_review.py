"""One-ledger design review. Mission results are supplied scenarios, NOT simulated combat.
No Godot runtime, UI or shipping implementation is created here.
"""
from pathlib import Path
from copy import deepcopy
import json,itertools,math,runpy,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'system-audit'))
from reference import Direction, value as memory_value, fund, total as memory_total, band_after, contract_deadline, contract_status, relationship_overlays
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data';F=D/'final_design';OUT=ROOT/'outputs'
def read(p):return json.loads(p.read_text())
BOARDS={b['id']:b for b in read(F/'boards.json')['boards']};CHARS={c['id']:c for c in read(D/'characters.json')};EC=read(D/'campaign_economy_contract.json');WORLD={m['id']:m for m in read(D/'campaign_world_contract.json')['missions']};EQ={e['id']:e for e in read(F/'equipment.json')['items']};ST=read(F/'stories.json');NODES={n['id']:n for n in ST['personal_nodes']};CAL=read(OUT/'final-design-validation.json')['story_calendar'];PROOFS=runpy.run_path(str(ROOT/'work/final-design/verify_contracts.py'));verified=PROOFS['verified'];ending=PROOFS['ending']

def objective_bonuses(board,secured):
 secured=set(secured);object_ids={o['id'] for o in board['objectives']};out=[]
 for tag in board['optional']:
  if tag=='any_two':ok=len(object_ids&secured)>=2
  elif tag=='all_three':ok=len(object_ids&secured)>=3
  elif tag=='both':ok=object_ids<=secured
  else:ok=set(tag.split('+'))<=secured
  if ok:out.append(tag)
 return out

def atomic(fn):
 def guarded(self,*args,**kwargs):
  before=deepcopy(self.__dict__)
  try:return fn(self,*args,**kwargs)
  except Exception:self.__dict__=before;raise
 return guarded

class Ledger:
 def __init__(self,name,hard=False,empty=False,external_social=False):
  self.external_social=external_social
  self.name=name;self.hard=hard;self.day=1;self.phase='briefing';self.resources=deepcopy(EC['start']) if not empty else dict(credits=0,supplies=0,parts=0)
  self.crew={a:dict(joined=c['join']==1,withdrawn=False,ready=1,fatigue=0,stress=10,xp=0,worked=False) for a,c in CHARS.items()}
  self.rel={r['id']:dict(grudge=r['grudge'],trust=r['trust'],closeness=r['closeness'],categories=r['grudge_categories'],memories=[]) for r in read(D/'initial_relationships.json')}
  self.inventory={'med_dose':0,'battery':0};self.tools={'crowbar','medkit'};self.fac={k:0 for k in ['infirmary','workshop','rest_area','communications']};self.discounts=set();self.treated=0
  self.projects=0;self.scenes=0;self.used=set();self.settled=set();self.rows=[];self.records=[];self.seq=0;self.plans={};self.read_nodes=set();self.finals={};self.evidence=set();self.evidence_seq={};self.district={k:1 for k in read(D/'rules.json')['endings']['district_ids']};self.caps={k:3 for k in self.district};self.route=None;self.active=None;self.total_reserves=0;self.total_consumed={};self.breaches={};self.repaired={};self.verified_at={};self.protocols=set();self.bands={k:0 for k in self.rel}
 def receipt(self,kind,**kw):
  self.seq+=1;r=dict(seq=self.seq,kind=kind,day=self.day,**kw);self.records.append(r);return r
 def healthy(self,a):
  c=self.crew[a];return c['joined'] and not c['withdrawn'] and c['ready']<=self.day
 def eligible(self,a,cost=18):return self.healthy(a) and self.crew[a]['fatigue']+cost<=100
 def choose_party(self,fixed=False,side=False):
  ids=[a for a in self.crew if self.eligible(a)]
  ids.sort(key=lambda a:((0 if fixed and a in ['lin','xu','su'] else 1),self.crew[a]['fatigue'],list(self.crew).index(a)))
  return ids[:3]
 def spend(self,**cost):
  assert all(v>=0 and self.resources[k]>=v for k,v in cost.items()),('insufficient resources',cost,self.resources)
  for k,v in cost.items():self.resources[k]-=v
 @atomic
 def buy_supplies(self,n):
  assert self.phase in ['briefing','after_main','camp'] and type(n) is int and n>0;self.spend(credits=4*n);self.resources['supplies']+=n;self.receipt('purchase',item='supplies',quantity=n)
 @atomic
 def craft(self,item,n):
  assert self.phase in ['briefing','after_main','camp'] and type(n) is int and n>0
  recipes={e['id']:(e['consumable_supply_cost'],e['unlocked_after_main']) for e in EQ.values() if e['slot']=='consumable'}|{'med_dose':(1,0)}
  assert item in recipes
  cost,unlock=recipes[item];assert unlock==0 or f'M{unlock:02}' in self.settled
  self.spend(supplies=n*cost);self.inventory[item]=self.inventory.get(item,0)+n;self.receipt('craft',item=item,quantity=n)
 @atomic
 def buy_tool(self,item):
  assert self.phase in ['briefing','after_main','camp'];e=EQ[item];assert e['slot'] in ['tool','support'] and item not in self.tools and (e['unlocked_after_main']==0 or f'M{e["unlocked_after_main"]:02}' in self.settled)
  token=f'M{self.day:02}';discount=int(self.fac['workshop']>=1 and token in self.settled and token not in self.discounts and e['price_parts']>0)
  self.spend(credits=e['price_credits'],parts=e['price_parts']-discount);self.tools.add(item)
  if discount:self.discounts.add(token)
  self.receipt('tool_purchase',item=item,discount_parts=discount)
 @atomic
 def deploy(self,mid,party,support=None,pack=None):
  b=BOARDS[mid];kind=b['kind'];assert mid not in self.settled and len(party)==len(set(party)) and len(party)<=3
  if kind=='main':assert self.phase=='briefing' and mid==f'M{self.day:02}'
  else:assert self.phase=='after_main' and b['day']<=self.day<=min(23,b['day']+1) and len(party)==3
  assert all(self.eligible(a) for a in party)
  reserves=3-len(party)
  if reserves:assert kind=='main' and len([a for a in self.crew if self.eligible(a)])==len(party)
  assert support is None or (kind=='main' and support not in party and self.eligible(support,8))
  if mid=='M24':assert self.route in self.available_routes()
  pack=pack or {};assert sum(pack.values())<=(3 if hasattr(self,'medical_pack_limit') else 3+int(self.fac['workshop']>=2)) and all(type(n) is int and 0<n<=(self.medical_pack_limit() if i=='med_dose' and hasattr(self,'medical_pack_limit') else 2) and i in self.inventory and self.inventory[i]>=n for i,n in pack.items())
  for i,n in pack.items():self.inventory[i]-=n
  for a in party:self.crew[a]['fatigue']+=18;self.crew[a]['worked']=True
  if support:self.crew[support]['fatigue']+=8;self.crew[support]['worked']=True
  self.update_bands();self.active=dict(mid=mid,party=party[:],support=support,packed=pack.copy(),reserves=reserves);self.phase='mission';self.total_reserves+=reserves
  self.receipt('assignment',mission=mid,mission_kind=kind,actors=party,support=support,reserves=reserves)
 def current_r(self,pair):
  r=self.rel[pair];return memory_total(r['grudge'],r['memories'],self.day)
 def update_bands(self):
  for key in self.rel:self.bands[key]=band_after(self.bands[key],self.current_r(key),self.crew[key.split('>')[0]]['stress'])
 @atomic
 def breach(self,observer,target,category='promise',severity=12,responsibility=1,event_id='',event_kind='promise_breach',promise_id=None,warned=False,known=True):
  assert self.phase=='mission' and observer in self.active['party'] and target in self.active['party']+['leader'] and target!=observer
  key=observer+'>'+target;r=self.rel[key];assert event_id and 0<responsibility<=1
  if event_id in r.get('facts',{}):return
  assigned=sum(x.get('responsibility',0) for x in self.records if x['kind']=='promise_breach' and x.get('event_id')==event_id and x.get('observer')==observer);assert assigned+responsibility<=1+1e-8
  definitions={e['id']:e for e in read(F/'progression_relationship.json')['memory_events']};assert event_kind in definitions
  definition=definitions[event_kind]
  state=Direction(grudge=r['grudge'],trust=r['trust'],memories=r['memories'],facts=r.get('facts',{}),grudge_categories=tuple(r['categories']))
  if not state.add(event_id,self.day,severity=definition['severity'] if event_kind!='promise_breach' else severity,loss=definition['trust_loss'],category=category,severe=event_kind in ['risk_concealment','persistent_breach'],share=responsibility,sensitivity=CHARS[observer]['sensitivity'].get(category,1),stress=self.crew[observer]['stress'],known=known,promise=promise_id,warned=warned):return
  r['trust']=state.trust;r['memories']=state.memories;r['facts']=state.facts;self.update_bands()
  self.receipt('promise_breach',mission=self.active['mid'],actor=target,observer=observer,target=target,id=event_id,event_id=event_id,scope='retreat_deadline',responsibility=responsibility,strength=round(state.memories[-1]['strength'],2));self.breaches[target]=self.seq;self.breaches[observer]=self.seq
 @atomic
 def settle(self,packet):
  assert self.phase=='mission' and self.active and packet['mission']==self.active['mid'];a=self.active;b=BOARDS[a['mid']];objs={o['id']:o for o in b['objectives']};done=set(packet['completed']);secured=set(packet['secured']);assert secured<=done<=set(objs)
  assert packet.get('branch') in ([None,'repair','isolate'] if b['id']=='M17' else [self.route] if b['id']=='M24' else [None])
  if b['id']=='M24':assert done<=set().union(*map(set,b['route_groups'][self.route]),{'archive'})
  selected_groups=b.get('route_groups',{}).get(self.route,b['mandatory_groups']) if b['id']=='M24' else ([['isolate']] if packet.get('branch')=='isolate' and b['id']=='M17' else b['mandatory_groups'])
  for oid in done:assert set(objs[oid]['prerequisites'])<=done
  if b['id']=='M17':
   assert not {'repair2','isolate'}<=done
   assert 'isolate' not in done or packet.get('branch')=='isolate'
   assert packet.get('branch')!='isolate' or 'repair2' not in done
  relevant={x for g in selected_groups for x in g}
  # Ancestor milestones count toward partial completion; optional records never do.
  queue=list(relevant)
  while queue:
   for dep in objs[queue.pop()]['prerequisites']:
    if dep not in relevant:relevant.add(dep);queue.append(dep)
  result='success' if all(set(g)&secured for g in selected_groups) else 'partial' if done&relevant else 'failed'
  consumed=packet.get('consumed',{})
  assert all(type(n) is int and 0<n<=a['packed'].get(i,0) for i,n in consumed.items())
  for i,n in a['packed'].items():self.inventory[i]=self.inventory.get(i,0)+n-consumed.get(i,0);self.total_consumed[i]=self.total_consumed.get(i,0)+consumed.get(i,0)
  injury=packet.get('injured',[]);withdraw=packet.get('withdrawn',[]);assert len(injury)==len(set(injury)) and len(withdraw)==len(set(withdraw));assert set(injury+withdraw)<=set(a['party']) and not set(injury)&set(withdraw) and (not withdraw or self.hard)
  rewards=deepcopy(EC['main_rewards' if b['kind']=='main' else 'side_rewards'][result]);rewards['credits']=max(6,rewards['credits']-4*a['reserves']) if b['kind']=='main' else rewards['credits']
  bonus_ids=objective_bonuses(b,secured)
  if 'objective_rewards' in EC:
   for bonus in EC['objective_rewards']:
    if bonus['mission']==b['id'] and bonus['objective'] in secured:
     for k,v in bonus['reward'].items():rewards[k]+=v
     self.receipt('objective_reward',mission=b['id'],object=bonus['objective'],reward=deepcopy(bonus['reward']))
  elif b['id']=='S05' and result=='success':rewards['supplies']+=2
  elif bonus_ids:rewards['parts' if b['id']=='M03' else 'supplies']+=1
  for k,v in rewards.items():self.resources[k]+=v
  contributions=packet.get('contributions',{});pair_awards=set()
  for oid,actors in contributions.items():
   assert oid in done and set(actors)<=set(a['party']) and len(actors)==len(set(actors))
   o=objs[oid];assert len(actors)<=max(1,o['work']) if o['kind']=='work' else len(actors)<=3
   self.receipt('objective_completed',mission=b['id'],mission_kind=b['kind'],object=oid,type=o['kind'],tags=o.get('interaction_tags',[]),contributors=actors,primary_contributor=actors[0] if actors else None)
   if o['kind']=='rescue' and oid in secured:self.receipt('casualty_saved',mission=b['id'],mission_kind=b['kind'],object=oid,contributors=actors)
   for x,y in itertools.permutations(actors,2):pair_awards.add(x+'>'+y)
  if not self.external_social:
   for key in pair_awards:self.rel[key]['trust']=min(100,self.rel[key]['trust']+4)
  for who in a['party']:
   self.crew[who]['xp']+=EC['growth']['main_xp' if b['kind']=='main' else 'side_xp'][result]
   if who in injury:self.crew[who]['ready']=self.day+2
   if who in withdraw:self.crew[who]['withdrawn']=True
   if not self.external_social:
    gain=min(12,(8 if who in injury+withdraw else 0)+4*len(set(injury+withdraw)-{who})+(4 if result!='success' else 0));self.crew[who]['stress']=max(0,min(100,self.crew[who]['stress']+gain-(4 if result=='success' else 0)))
  if b['kind']=='main':
   w=WORLD[b['id']];delta=w['infrastructure_delta'][result];district=w['district']
   if b['id']=='M17' and packet.get('branch')=='isolate' and 'isolate' in secured:self.caps[district]=2;delta=0
   self.district[district]=max(0,min(self.caps[district],self.district[district]+delta))
   if a['support']:
    self.resources['supplies']+=1;self.crew[a['support']]['xp']+=2;self.receipt('support_work',mission=b['id'],actor=a['support'])
   for who,c in CHARS.items():
    if c['join']==self.day and c['join']>1:self.crew[who]['joined']=True;self.crew[who]['xp']=max(self.crew[who]['xp'],[0,12,28,48][(self.day-1)//6]);self.receipt('recruit',actor=who)
  ev=b['evidence_receipt']
  if ev and set(ev['requires'])<=secured:self.add_evidence(ev['id'],b['id'])
  self.receipt('mission_settled',mission=b['id'],mission_kind=b['kind'],actors=a['party'],all_extracted=packet.get('all_extracted') is True,xu_standing_on_exit=packet.get('xu_standing_on_exit') is True,result=result)
  if 'xu' in a['party'] and 'xu' in self.plans:self.receipt('retreat_promise',mission=b['id'],kept=packet.get('kept_deadline') is True)
  # A supplied report must explicitly claim observed protection; being present is insufficient.
  for who in packet.get('protection',[]):assert who in a['party'];self.receipt('protect_or_rescue',mission=b['id'],actor=who)
  self.settled.add(b['id']);self.rows.append(dict(day=self.day,mission=b['id'],party=a['party'],reserves=a['reserves'],support=a['support'],outcome=result,branch=packet.get('branch'),completed=sorted(done),secured=sorted(secured),injured=injury,withdrawn=withdraw,resources_after_mission=deepcopy(self.resources),evidence=sorted(self.evidence),district_sum=sum(self.district.values())))
  self.confirm_audits();self.update_bands()
  self.phase='ending' if b['id']=='M24' else 'after_main' if b['kind']=='main' else 'camp';self.active=None
 def add_evidence(self,eid,source):
  if eid not in self.evidence:self.evidence.add(eid);self.evidence_seq[eid]=self.receipt('evidence_verified',id=eid,source=source)['seq']
 @atomic
 def begin_camp(self):assert self.phase in ['after_main','camp'] and self.day<24;self.phase='camp'
 def claim_project(self,participants):
  assert self.phase=='camp' and self.projects<2 and not self.used&set(participants) and len(participants)==len(set(participants))
  assert all(self.crew[a]['joined'] and not self.crew[a]['withdrawn'] for a in participants)
  self.projects+=1;self.used.update(participants)
 def cooperation_allowed(self,actors,protocol,context=(),safeguards=()):
  """Evaluate relationship conditions only; runtime also checks learning, loadout, AP and geometry."""
  if len(actors)!=2 or len(set(actors))!=2:return False
  data=read(F/'progression_relationship.json');definitions={x['id']:x for x in data['protocols']}
  if protocol not in definitions:return False
  tags=set(definitions[protocol]['tags']);context=set(context);safeguards=set(safeguards)
  for x,y in itertools.permutations(actors,2):
   if self.rel[x+'>'+y]['trust']<60:return False
   rule=data['situational_cooperation'][x]
   self.update_bands()
   relevant=max(self.bands[x+'>'+y],self.bands[x+'>leader'])>=2 and tags&set(rule['protocol_tags']) and ('any' in rule['when'] or context&set(rule['when']))
   if relevant:
    if rule.get('required_any') and not safeguards&set(rule['required_any']):return False
    if rule.get('required_all') and not set(rule['required_all'])<=safeguards:return False
  return True
 @atomic
 def train(self,actors,protocol=None):
  assert 1<=len(actors)<=2 and all(self.healthy(a) and self.crew[a]['fatigue']+8<=100 for a in actors)
  if protocol:assert protocol in {p['id'] for p in read(F/'progression_relationship.json')['protocols']} and len(actors)==2 and all(self.rel[x+'>'+y]['trust']>=60 for x,y in itertools.permutations(actors,2)) and tuple(sorted(actors))+(protocol,) not in self.protocols
  self.claim_project(actors);self.spend(supplies=len(actors))
  for a in actors:self.crew[a]['xp']+=3;self.crew[a]['fatigue']+=8
  if protocol:self.protocols.add(tuple(sorted(actors))+ (protocol,))
  self.receipt('training',actors=actors,protocol=protocol)
 @atomic
 def recover(self,actors):
  assert 1<=len(actors)<= (3 if self.fac['rest_area']>=2 else 2);self.claim_project(actors)
  for a in actors:self.crew[a]['fatigue']=max(0,self.crew[a]['fatigue']-(16 if self.fac['rest_area'] else 12));self.crew[a]['stress']=max(0,self.crew[a]['stress']-16)
  self.receipt('recovery',actors=actors)
 @atomic
 def treat(self,actors):
  assert 1<=len(actors)<= (3 if self.fac['infirmary']>=2 else 2) and all(self.crew[a]['ready']>self.day+1 for a in actors);self.claim_project(actors)
  cost=2*len(actors)-int(self.fac['infirmary']>=1 and self.treated==0);self.spend(supplies=cost)
  for a in actors:self.crew[a]['ready']=self.day+1
  self.treated+=len(actors);self.receipt('treatment',actors=actors,cost=cost)
 @atomic
 def upgrade(self,facility):
  assert self.fac[facility]<2 and not any(r['kind']=='facility' and r['day']==self.day for r in self.records);self.claim_project([]);cost=[(35,4),(60,8)][self.fac[facility]];self.spend(credits=cost[0],parts=cost[1]);self.fac[facility]+=1;self.receipt('facility',facility=facility,tier=self.fac[facility])
 @atomic
 def review(self,evidence):
  assert self.day in ([18,20,22,23] if self.fac['communications'] else [20,22,23]) and 1<=len(evidence)<= (2 if self.fac['communications']>=2 and self.day in [20,22,23] else 1) and len(evidence)==len(set(evidence)) and not set(evidence)&self.evidence
  self.claim_project([])
  for e in evidence:assert e in ['E_ORDER','E_WARNING','E_MAINTENANCE'];self.add_evidence(e,'public_review')
 @atomic
 def scene(self,nid,choice_id=None):
  assert self.phase=='camp' and self.scenes<2 and nid not in self.read_nodes
  if nid.startswith('R'):
   n=next(n for n in ST['relationship_nodes'] if n['id']==nid);assert n['earliest_day']<=self.day;self.scenes+=1;self.read_nodes.add(nid);self.receipt('absent_pair_coda' if any(self.crew[a]['withdrawn'] for a in n.get('participants',n.get('actors',[]))) else 'short_scene',node=nid);return
  n=NODES[nid];a=n['actor'];assert n['earliest_day']<=self.day and all(x in self.read_nodes for x in n['requires_resolved']);self.scenes+=1;self.read_nodes.add(nid)
  if self.crew[a]['withdrawn']:self.finals[a]='medical_withdrawal';self.receipt('absent_coda',actor=a,node=nid);return
  if n['stage']==2:
   self.claim_project([a]);choice=next((c for c in n['choices'] if c['id']==choice_id),None) if choice_id else n['choices'][0] if self.resources['credits']>=n['choices'][0]['credits'] else n['choices'][1];assert choice is not None;self.spend(credits=choice['credits']);start=self.receipt('story_choice',actor=a,node=nid,choice=choice['id'])['seq']
   if choice['creates_contract']:
    assert contract_deadline(a,self.day)
    self.plans[a]=start
    if a=='chen':self.receipt('payment',purpose='chen_compensation',amount=8);self.receipt('known_information',actor='ye',fact='chen_signed_responsibility')
    if a=='jiang':self.receipt('payment',purpose='jiang_wages',amount=6)
    if a=='mo':self.receipt('public_record_release',privacy='redacted')
  elif n['stage']==3:
   proof=a in self.plans and verified(a,self.records,self.plans[a],self.day);choice=choice_id or ('integrated' if proof else 'professional');assert choice in {c['id'] for c in n['choices']} and (choice!='integrated' or proof);self.finals[a]=choice;self.receipt('ending_preference',actor=a,choice=choice)
  else:self.receipt('story_choice',actor=a,node=nid,choice=n['choices'][0]['id'])
 def confirm_audits(self):
  if 'ye' in self.plans and 'E_MAINTENANCE' in self.evidence and not any(r['kind']=='known_information' and r.get('fact')=='maintenance_audit' for r in self.records):self.receipt('known_information',actor='ye',fact='maintenance_audit')
  for actor,created in self.plans.items():
   if actor not in self.verified_at and verified(actor,self.records,created,self.day):self.verified_at[actor]=self.seq
 def character_ending(self,actor):
  c=self.crew[actor];choice=self.finals.get(actor,'unresolved');present=not c['withdrawn']
  currently_valid=actor in self.plans and verified(actor,self.records,self.plans[actor],self.day)
  fulfilled=actor in self.verified_at or currently_valid
  events=[dict(kind='breach',id=r['event_id'],observer=r['observer'],target=r['actor']) for r in self.records if r['kind']=='promise_breach']
  overlays=relationship_overlays(events,actor)
  return dict(presence='in_crew' if present else 'medical_withdrawal',requested_personal_choice=choice,ongoing_obligation='breached' if actor in ['mo','jiang'] and fulfilled and not currently_valid else 'no_recorded_breach',contract=contract_status(actor in self.plans,fulfilled,not present),career='long_term_recovery' if not present else 'postwar_change' if choice=='new_life' else 'continue_work',relationship_overlay='unrepaired_breach' if overlays or self.breaches.get(actor,0)>self.repaired.get(actor,0) else 'no_new_unresolved_breach',relationship_directions=[r['observer']+'>'+r['target'] for r in overlays])
 @atomic
 def night(self):
  assert self.phase=='camp' and self.day<24
  for a,c in self.crew.items():
   if c['joined'] and not c['withdrawn']:c['fatigue']=max(0,c['fatigue']-12-(0 if c['worked'] else 16));c['stress']=max(0,c['stress']-8)
  self.rows[-1]['night']=dict(projects=self.projects,scenes=self.scenes,resources=deepcopy(self.resources),fatigue={a:c['fatigue'] for a,c in self.crew.items() if c['joined'] and not c['withdrawn']},xp={a:c['xp'] for a,c in self.crew.items() if c['joined']},available_next=[a for a,c in self.crew.items() if c['joined'] and not c['withdrawn'] and c['ready']<=self.day+1 and c['fatigue']+18<=100],lin_xu=dict(trust=self.rel['lin>xu']['trust'],resentment=round(self.current_r('lin>xu'),2)))
  self.day+=1;self.update_bands();self.projects=0;self.scenes=0;self.treated=0;self.used.clear();self.phase='briefing'
  for c in self.crew.values():c['worked']=False
 def available_routes(self):return ['distributed_rebuild','evacuation']+(['shared_control'] if sum(self.district.values())>=10 and len(self.evidence)>=2 else [])
 def summary(self):
  assert self.phase=='ending';last=self.rows[-1];world=self.route if last['outcome']=='success' else 'evacuation'
  return dict(name=self.name,world_ending=world,selected_route=self.route,main_count=sum(x.startswith('M') for x in self.settled),side_count=sum(x.startswith('S') for x in self.settled),resources=self.resources,crafted_inventory=self.inventory,consumed=self.total_consumed,tools=sorted(self.tools),facilities=self.fac,borrowed_slots=self.total_reserves,withdrawn=[a for a,c in self.crew.items() if c['withdrawn']],levels={a:sum(c['xp']>=t for t in [0,12,28,48,72,100]) for a,c in self.crew.items() if c['joined']},xp={a:c['xp'] for a,c in self.crew.items() if c['joined']},story_projects=len(self.plans),read_scenes=len(self.read_nodes),verified_contracts=[a for a,t in self.plans.items() if verified(a,self.records,t,self.day)],character_endings={a:self.character_ending(a) for a,c in self.crew.items() if c['joined']},trained_protocols=[list(p) for p in sorted(self.protocols)],relationship_sample={k:dict(trust=self.rel[k]['trust'],resentment=round(self.current_r(k),2)) for k in ['lin>xu','lin>su','ye>chen']})

# Predetermined tactical outcomes: no automatic victory, path feasibility or enemy simulation implied.
def packet(mid,party,kind='success',branch=None,injured=(),withdrawn=(),consumed=None,evidence=True):
 b=BOARDS[mid];objs={o['id']:o for o in b['objectives']};groups=b['mandatory_groups'];goals=[g[0] for g in groups]
 if mid=='M17' and branch=='isolate':goals=['isolate']
 if mid=='M24':goals={'shared_control':['bus','auth'],'distributed_rebuild':['west','east'],'evacuation':['r1','r2']}[branch]
 done=set()
 def complete(i):
  for x in objs[i]['prerequisites']:complete(x)
  done.add(i)
 if kind=='success':
  for g in goals:complete(g)
  if evidence and b['evidence_receipt']:
   for i in b['evidence_receipt']['requires']:complete(i)
 elif kind=='partial':
  if len(goals)>1:complete(goals[0])
  elif objs[goals[0]]['prerequisites']:complete(objs[goals[0]]['prerequisites'][0])
 contributions={}
 for i in sorted(done):
  o=objs[i];primary='chen' if 'chen' in party and o['kind']=='work' else party[0] if party else None
  if primary:
   count=2 if o['kind']=='rescue' or (o['kind']=='work' and o['work']>=2) else 1
   contributions[i]=([primary]+[a for a in party if a!=primary])[:count]
 return dict(all_extracted=not withdrawn,xu_standing_on_exit='xu' in party and 'xu' not in list(injured)+list(withdrawn),mission=mid,completed=sorted(done),secured=sorted(done),contributions=contributions,injured=list(injured),withdrawn=list(withdrawn),consumed=consumed or {},branch=branch,protection=['he'] if 'he' in party and kind=='success' else [],kept_deadline=kind!='failed')

def run(name,fixed=False,hard=False,disaster=False,medical_uses=0):
 g=Ledger(name,hard=hard,empty=disaster);calendar={x['day']:x['scenes'] for x in CAL};sides={2:'S01',6:'S03',10:'S05',14:'S07',18:'S09',22:'S11'}
 for day in range(1,25):
  mid=f'M{day:02}';party=g.choose_party(fixed)
  if day==24:g.route='shared_control' if not disaster and 'shared_control' in g.available_routes() else 'evacuation'
  support=next((a for a in g.crew if a not in party and g.eligible(a,8)),None)
  pack={}
  if not disaster and medical_uses:
   if g.resources['supplies']<medical_uses:g.buy_supplies(medical_uses-g.resources['supplies'])
   g.craft('med_dose',medical_uses);pack['med_dose']=medical_uses
  if not disaster and day==2:
   if g.resources['supplies']<2:g.buy_supplies(2-g.resources['supplies'])
   g.craft('battery',1);pack['battery']=1
  if not disaster and day==12 and not medical_uses:g.craft('med_dose',1);pack={'med_dose':1}
  g.deploy(mid,party,support,pack)
  if day==6 and not disaster and 'lin' in party and 'xu' in party:g.breach('lin','xu',responsibility=.5,event_id='M06_extra_trip');g.breach('lin','leader',responsibility=.5,event_id='M06_extra_trip')
  result='failed' if disaster else 'partial' if day in [6,9,18] else 'failed' if day==12 else 'success'
  hurt=[party[0]] if not disaster and day in [4,9] and party else []
  p=packet(mid,party,result,'isolate' if mid=='M17' and fixed else g.route if mid=='M24' else None,hurt,party if disaster else (),({**({'battery':1} if day==2 and pack else {}),**({'med_dose':medical_uses} if medical_uses else {})}),evidence=not fixed)
  g.settle(p)
  if day==24:break
  if not disaster:
   tool={3:'winch',7:'insulation',10:'scanner',13:'cutter',16:'stretcher'}.get(day)
   if tool:
    try:g.buy_tool(tool)
    except AssertionError:pass
   if day in sides:
    sideparty=g.choose_party(fixed,side=True)
    if len(sideparty)==3:g.deploy(sides[day],sideparty);g.settle(packet(sides[day],sideparty,'success',evidence=False))
  g.begin_camp();g.confirm_audits()
  for nid in calendar[day]:
   try:g.scene(nid)
   except AssertionError:pass
  # Actors assigned to substantive story work cannot also train or rest tonight.
  urgent=[a for a,c in g.crew.items() if c['joined'] and not c['withdrawn'] and a not in g.used and c['fatigue']>=60]
  if urgent and g.projects<2:g.recover(sorted(urgent,key=lambda a:-g.crew[a]['fatigue'])[:2])
  if not disaster and day in [5,8,14,19] and g.projects<2:
   try:g.upgrade({5:'workshop',8:'rest_area',14:'communications',19:'communications'}[day])
   except AssertionError:pass
  if not disaster and day in [18,20,22,23] and g.projects<2:
   missing=[e for e in ['E_MAINTENANCE','E_ORDER','E_WARNING'] if e not in g.evidence]
   if missing:
    try:g.review(missing[:2 if g.fac['communications']>=2 else 1]);g.confirm_audits()
    except AssertionError:pass
  if not disaster and g.projects<2:
   available=[a for a in g.crew if g.healthy(a) and a not in g.used and g.crew[a]['fatigue']+8<=82]
   available.sort(key=lambda a:g.crew[a]['xp'])
   if len(available)>=2:
    trainees=available[:2]
    if day==1:trainees=['lin','su']
    try:
     if g.resources['supplies']<2:g.buy_supplies(2-g.resources['supplies'])
     g.train(trainees,'relay_carry' if day==1 else None)
    except AssertionError:pass
  g.confirm_audits();g.night()
 return g

G=[run('偏好固定队伍',fixed=True),run('轮换与建设'),run('最高难度极端连续失败',hard=True,disaster=True)]
SENS=[run('固定队伍：每主任务使用2份医疗耗材',fixed=True,medical_uses=2),run('轮换：每主任务使用2份医疗耗材',medical_uses=2)]
checks=[]
def check(n,ok):
 assert ok,n;checks.append(n)
for g in G+SENS:
 s=g.summary();check(g.name+' reaches 24-duty ending',s['main_count']==24);check(g.name+' no negative resources',all(v>=0 for v in g.resources.values()));check(g.name+' no actor fatigue exceeds100',all(0<=c['fatigue']<=100 for c in g.crew.values()));check(g.name+' no double-settled missions',len(g.rows)==len(g.settled));check(g.name+' all camp budgets within2',all(x.get('night',{}).get('projects',0)<=2 and x.get('night',{}).get('scenes',0)<=2 for x in g.rows));check(g.name+' all pair trust withinbounds',all(0<=r['trust']<=100 for r in g.rel.values()))
check('highest loss path removes all8 named heroes but still ends',len(G[2].summary()['withdrawn'])==8 and G[2].summary()['world_ending']=='evacuation')
check('unspent packed medical dose returns as medicine, not duplicated raw supplies',all(g.inventory['med_dose']==1 and g.total_consumed['med_dose']==0 for g in G[:2]))
check('consumed battery removed exactly once',all(g.inventory['battery']==0 and g.total_consumed['battery']==1 for g in G[:2]))
# Error-path snapshots: rejected operations leave the SAME ledger, not just resource balance.
def rejected_unchanged(g,fn,label):
 before=deepcopy(g.__dict__)
 try:fn();rejected=False
 except AssertionError:rejected=True
 check(label,rejected and g.__dict__==before)
g=Ledger('fault checks');rejected_unchanged(g,lambda:g.deploy('M01',['lin','lin','su']),'duplicate actor rejected without any mutation');g.deploy('M01',['lin','xu','su']);p=packet('M01',['lin','xu','su']);rejected_unchanged(g,lambda:g.settle({**p,'consumed':{'battery':1}}),'unpacked consumption rejected atomically');g.settle(p);rejected_unchanged(g,lambda:g.settle(p),'second settlement cannot issue duplicate XP or rewards');g.begin_camp();g.train(['lin','su']);rejected_unchanged(g,lambda:g.recover(['lin']),'same actor cannot train and recover in same evening');rejected_unchanged(g,lambda:g.train(['xu'],'relay_carry'),'one actor cannot train a pair protocol')
h=Ledger('injury timing');h.day=2;h.settled.add('M01');h.deploy('M02',['lin','xu','su']);h.settle(packet('M02',['lin','xu','su'],injured=['lin']));check('injury rejection test uses an actually open side mission',BOARDS['S01']['day']<=h.day<=BOARDS['S01']['day']+1 and h.phase=='after_main');rejected_unchanged(h,lambda:h.deploy('S01',['lin','xu','su']),'injury cannot be bypassed by entering side deployment');h.begin_camp();h.treat(['lin']);check('expedited treatment does not enable same-day side duty',not h.healthy('lin') and h.crew['lin']['ready']==3);h.night();check('treated actor ready next morning',h.healthy('lin'))
# Collateral loss must alter the same result used by payment and facilities.
k=Ledger('secured result');k.day=2;k.phase='briefing';k.deploy('M02',['lin','xu','su']);p=packet('M02',['lin','xu','su']);p['secured']=['cut'];k.settle(p);check('destroyed power fixture gives partial reward and no facility gain',k.rows[-1]['outcome']=='partial' and k.resources['credits']==74 and k.district[WORLD['M02']['district']]==1)
rel=Ledger('specific cooperation');rel.phase='camp';rel.rel['lin>xu']['trust']=65;rel.rel['xu>lin']['trust']=65;rel.rel['lin>xu']['grudge']=70
rel.train(['lin','xu'],'protected_work');check('safe training does not promise unsafe field cooperation',tuple(sorted(['lin','xu']))+('protected_work',) in rel.protocols and not rel.cooperation_allowed(['lin','xu'],'protected_work',context=['fall']))
check('verified protection restores the specific field cooperation',rel.cooperation_allowed(['lin','xu'],'protected_work',context=['fall'],safeguards=['independent_anchor']))
check('unrelated ground work does not trigger a fall-related refusal',rel.cooperation_allowed(['lin','xu'],'protected_work',context=['electrical']))
rejected_unchanged(rel,lambda:rel.train(['lin','xu'],'protected_work'),'already learned protocol cannot be purchased again as a new unlock')
check('unrelated cooperation is not blanket-disabled by resentment',rel.cooperation_allowed(['lin','xu'],'relay_carry'))
check('basic deployment remains controlled despite relational conflict',rel.eligible('lin') and rel.eligible('xu'))
ep=Ledger('epilogue separation');ep.finals['lin']='new_life';ep.breaches['lin']=20
check('later conflict does not erase chosen postwar career',ep.character_ending('lin')['career']=='postwar_change' and ep.character_ending('lin')['relationship_overlay']=='unrepaired_breach')
ep.crew['lin']['withdrawn']=True
check('permanent medical withdrawal still overrides present-tense career scene',ep.character_ending('lin')['career']=='long_term_recovery')
out={'version':'0.6-system-audit','scope':'Unified design ledger driven by explicitly supplied tactical outcomes/contributions. Not a tactical simulator, gameplay demo or production controller.','checks':checks,'passed_count':len(checks),'scenarios':[dict(summary=g.summary(),daily_trace=g.rows,receipts=g.records) for g in G],'consumption_sensitivity':[dict(summary=g.summary(),assumption='每个主任务给定两次合法医疗使用记录；是成本敏感性情境，不是预测玩家每关必需治疗两次。') for g in SENS],'limitations':['Scenario policies are illustrative, not optimal strategies.','Narrative stages may choose professional outcomes when their proof was not earned by that reading time; this is intentional, not an automatic happy-ending simulator.','Temporary memory aging and trust contributions are evaluated, but all old-grudge repair branches and every tactical cooperation restriction are not exhaustively exercised.','Input mission contributions are stipulated, not proof that the full combat board can produce them.']}
(OUT/'whole-campaign-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'scenarios':[{'name':g.name,'ending':g.summary()['world_ending'],'main':g.summary()['main_count'],'side':g.summary()['side_count'],'resources':g.resources,'withdrawn':len(g.summary()['withdrawn'])} for g in G+SENS]},ensure_ascii=False,indent=2))
