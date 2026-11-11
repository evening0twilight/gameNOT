"""Full earned-state campaigns with finite voluntary external recovery."""
from pathlib import Path
import json
from copy import deepcopy
from choices import CONTRACT,SPEC
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs'
p=ROOT/'work/approach-review/campaign.py'
source=p.read_text().split('scenarios=[]')[0].replace('from encounter_choices import ChoiceBattle,SPEC','from choices import ChoiceBattle,SPEC')
z={'__file__':str(p),'__name__':'choice_campaign_adapter'};exec(compile(source,str(p),'exec'),z)
OldLedger=z['Ledger'];RUN=z['ns'];USE_SUPPORT=False;REPAIR='none';ADVANCED_PLAN=False
run_source=z['source']
run_source=run_source.replace('  if g.projects<2:\n   trainees=', '  while g.projects<2:\n   trainees=')
run_source=run_source.replace("if trainees and g.resources['supplies']>=len(trainees):g.train(trainees)", "if trainees and g.resources['supplies']>=len(trainees):g.train(trainees)\n   else:break")
exec(compile(run_source,str(ROOT/'work/integrated-review/campaign.py'),'exec'),RUN)
wp=ROOT/'work/approach-review/protocol_witnesses.py';ws={'__file__':str(wp),'__name__':'earned_relay_policy'}
exec(compile(wp.read_text().split('out=[]')[0].replace('from encounter_choices import ChoiceBattle,distance,adjacent','from choices import ChoiceBattle,distance,adjacent'),str(wp),'exec'),ws)
class Ledger(OldLedger):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.support_uses={};self.support_ready={};self.assisted_days=set()
 def cooperation_allowed(self,actors,protocol,context=(),safeguards=()):
  if protocol not in CONTRACT['cooperation_training']['basic_actions']:return super().cooperation_allowed(actors,protocol,context,safeguards)
  if len(actors)!=2 or len(set(actors))!=2:return False
  data=json.loads((ROOT/'game/data/final_design/progression_relationship.json').read_text());tags=set(next(p['tags'] for p in data['protocols'] if p['id']==protocol));context=set(context);safeguards=set(safeguards);self.update_bands()
  for x,y in [actors,actors[::-1]]:
   rule=data['situational_cooperation'][x];relevant=max(self.bands[x+'>'+y],self.bands[x+'>leader'])>=2 and tags&set(rule['protocol_tags']) and ('any' in rule['when'] or context&set(rule['when']))
   if relevant and ((rule.get('required_any') and not safeguards&set(rule['required_any'])) or (rule.get('required_all') and not set(rule['required_all'])<=safeguards)):return False
  return True
 def train(self,actors,protocol=None):
  if protocol:assert protocol in CONTRACT['cooperation_training']['unlocks']
  super().train(actors,protocol)
  if len(actors)==2 and all(self.rel[x+'>'+y]['trust']>=60 for x,y in [actors,actors[::-1]]) and not all(tuple(sorted(actors))+(key,) in self.protocols for key in CONTRACT['cooperation_training']['unlocks']):
   for key in CONTRACT['cooperation_training']['unlocks']:self.protocols.add(tuple(sorted(actors))+(key,))
   self.receipt('coordination_bundle',actors=actors,learned=CONTRACT['cooperation_training']['unlocks'],paid_projects=1,paid_supplies=2)
 def repair_equipment(self,mid):
  assert mid in CONTRACT['investments'] and self.operational[mid]['primary_success']
  super().repair_equipment(mid);self.support_ready[mid]=self.day+1
 def available_support(self,mid):
  if mid not in CONTRACT['investments'] or mid not in self.operational:return 0
  s=CONTRACT['investments'][mid];o=self.operational[mid]
  return max(0,s['sessions']-self.support_uses.get(mid,0)) if o['primary_success'] and (o['intact'] or o['repaired']) and max(s['first_day'],self.support_ready.get(mid,s['first_day']))<=self.day<=s['last_day'] else 0
 def assisted_recovery(self,mid,actors):
  assert self.phase=='camp' and self.day not in self.assisted_days and self.available_support(mid)>0
  assert 1<=len(actors)<=2 and len(set(actors))==len(actors) and all(self.healthy(a) for a in actors)
  before={a:(self.crew[a]['fatigue'],self.crew[a]['stress']) for a in actors}
  for a in actors:
   self.crew[a]['fatigue']=max(0,self.crew[a]['fatigue']-(16 if self.fac['rest_area'] else 12));self.crew[a]['stress']=max(0,self.crew[a]['stress']-16)
  self.support_uses[mid]=self.support_uses.get(mid,0)+1;self.assisted_days.add(self.day)
  self.receipt('external_logistics',actors=actors,external_facility=mid,projects=0,fatigue_recovered=sum(before[a][0]-self.crew[a]['fatigue'] for a in actors),stress_recovered=sum(before[a][1]-self.crew[a]['stress'] for a in actors))
 def summary(self):
  r=super().summary();r['external_support']=dict(uses=self.support_uses,days=sorted(self.assisted_days),fatigue_recovered=sum(x.get('fatigue_recovered',0) for x in self.records if x.get('external_facility')),stress_recovered=sum(x.get('stress_recovered',0) for x in self.records if x.get('external_facility')))
  r['training_bundles']=sum(x['kind']=='coordination_bundle' for x in self.records);return r
old_record=z['record_operation']
def record_operation(g,battle,r):
 old_record(g,battle,r)
 if battle.spec:g.operational[battle.b['id']]['primary_success']=r['success']
 actions=[x for x in r['log'] if x['action'] in ['relay_carry','coordinated_pull']]
 if actions:g.receipt('advanced_actions_used',mission=battle.b['id'],actors=battle.party,levels=r['levels'],actions=actions,secured=r['secured'])
old_factory=z['factory']
def factory(board,goals,party,levels=None,**kw):
 selected=old_factory(board,goals,party,levels,**deepcopy(kw))
 if not ADVANCED_PLAN or board['id']!='M06' or party!=['lin','xu','su']:return selected
 g=z['ACTIVE'];pair=('lin','su','relay_carry')
 if pair not in g.protocols or not g.cooperation_allowed(['lin','su'],'relay_carry'):return selected
 candidate=ws['RelayWitness'].__new__(ws['RelayWitness']);candidate.use_protocol=True;candidate.handed=False
 options=deepcopy(kw);options.update(skills=False,style='rush',extra=['asset'])
 trust={(a,b):g.rel.get(a+'>'+b,{}).get('trust',0) for a in party for b in party if a!=b}
 z['ChoiceBattle'].__init__(candidate,board,goals,party,levels,trained=list(g.protocols),trust=trust,**options)
 result=candidate.run()
 if result['success'] and 'asset' in result['secured']:candidate.run=lambda:result;return candidate
 return selected
def training_and_repairs(g):
 if USE_SUPPORT:
  candidates=sorted([a for a in g.crew if g.healthy(a) and (g.crew[a]['fatigue']>=12 or g.crew[a]['stress']>=16)],key=lambda a:-(g.crew[a]['fatigue']+g.crew[a]['stress']))[:2]
  mid=next((m for m in CONTRACT['investments'] if g.available_support(m)),None)
  if mid and candidates:g.assisted_recovery(mid,candidates)
 if z['PROFILE']=='protected':
  if g.projects<2 and ('lin','su','relay_carry') not in g.protocols and all(g.healthy(a) and a not in g.used and g.crew[a]['fatigue']+8<=100 for a in ['lin','su']) and all(g.rel[p]['trust']>=60 for p in ['lin>su','su>lin']) and g.resources['supplies']>=2:g.train(['lin','su'],'relay_carry')
 if REPAIR!='none':
  for mid,inv in CONTRACT['investments'].items():
   o=g.operational.get(mid)
   if not o or not o['primary_success'] or o['intact'] or o['repaired']:continue
   remaining=max(0,inv['last_day']-g.day)
   ready=(remaining>=2 if REPAIR=='timely' else g.day>inv['last_day'])
   if ready and g.projects<2 and g.resources['supplies']>=2:g.repair_equipment(mid);break
RUN.update(Ledger=Ledger,Party=factory,rank=z['rank'],record_operation=record_operation,training_and_repairs=training_and_repairs)
scenarios=[]
for name,profile,support,repair,options in [
 ('普通轮换，不使用外部休整','safe',False,'none',{}),
 ('普通轮换，按需使用保全设施','safe',True,'none',{}),
 ('偏好阵容，一次搭档训练','protected',True,'timely',dict(fixed=True)),
 ('专业人员轮换，按需使用后勤','specialists',True,'timely',{}),
 ('固定阵容拆除，不维修','dismantle',True,'none',dict(fixed=True)),
 ('固定阵容拆除，及时维修并使用','dismantle',True,'timely',dict(fixed=True)),
 ('固定阵容拆除，过期后才公益修复','dismantle',True,'late',dict(fixed=True)),
 ('完整36关，按需合作和后勤','protected',True,'timely',dict(sides=True)),
 ('最高难度连续失误后继续','protected',True,'timely',dict(hard=True,disasters=(6,7,8,15))),
 ('真实养成后，在M06使用接力争取档案','protected',True,'timely',dict(fixed=True)),
 ('高出勤且偏好固定阵容，不维修','dismantle',True,'none',dict(fixed=True,sides=True)),
 ('高出勤且偏好固定阵容，及时维修','dismantle',True,'timely',dict(fixed=True,sides=True))]:
 z['PROFILE']=profile;USE_SUPPORT=support;REPAIR=repair;ADVANCED_PLAN=name.startswith('真实养成后')
 s=RUN['run'](name,**options);q=s['summary'];q['operational_summary']=dict(service_delivered=sum(x['service'] for x in s['operational'].values()),intact=sum(x['intact'] for x in s['operational'].values()),repaired=sum(x['repaired'] for x in s['operational'].values()),repair_projects=sum(x['kind']=='equipment_restored' for x in s['receipts']));scenarios.append(s)
 print(name,q['main_count'],q['side_count'],q['resources'],q['operational_summary'],q['external_support'],flush=True)
(O/'player-choice-campaign-results.json').write_text(json.dumps(dict(version='0.11',scenarios=scenarios,actual_battles=sum(len(s['battles']) for s in scenarios),scope='Twelve earned-state campaigns. Candidate tactical policies use hindsight; no claim of human preference or success probability. Includes deliberately late repair, ordinary-practice-to-M06-relay, and matched high-tempo fixed-preference comparisons.'),ensure_ascii=False,indent=2)+'\n')
