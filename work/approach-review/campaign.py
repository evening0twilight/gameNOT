"""Earned-party campaign: operational choices and optional repairs share real budgets."""
from pathlib import Path
from copy import deepcopy
import json,sys,itertools
from encounter_choices import ChoiceBattle,SPEC
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs'
base=ROOT/'work/integrated-review/campaign.py'
# Reuse the existing ledger adapter and complete day/story schedule, not a new game.
source=base.read_text().split('scenarios=[')[0]
source=source.replace("guide.scene(b,r['log']", "guide.scene(battle.b,r['log']")
source=source.replace(' g.settle(packet)',' g.settle(packet)\n record_operation(g,battle,r)')
source=source.replace(' return dict(mission=mid,party=cast,',' return dict(operational=operation(battle),mission=mid,party=cast,')
source=source.replace('  party=g.choose_party(fixed=fixed);','  prepare_day(g)\n  party=g.choose_party(fixed=fixed);')
source=source.replace('  # Reward projects are paid','  training_and_repairs(g)\n  # Reward projects are paid')
source=source.replace(' return dict(summary=summary,battles=battles,',' return dict(operational=g.operational,summary=summary,battles=battles,')
ns={'__file__':str(base),'__name__':'approach_campaign_adapter'}
exec(compile(source,str(base),'exec'),ns)
BaseLedger=ns['Ledger'];PROFILE='safe';DO_REPAIR=False;ACTIVE=None;SKIP_TRAIN=False
class Ledger(BaseLedger):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.operational={};global ACTIVE;ACTIVE=self
 def choose_party(self,fixed=False,side=False):
  if PROFILE!='specialists':return super().choose_party(fixed,side)
  ids=[a for a in self.crew if self.eligible(a)];ids.sort(key=lambda a:(a not in ['chen','ye','he'],self.crew[a]['fatigue'],list(self.crew).index(a)));return ids[:3]
 def repair_equipment(self,mid):
  assert self.phase=='camp' and mid in self.operational and not self.operational[mid]['intact'] and not self.operational[mid]['repaired']
  assert self.projects<2 and self.resources['supplies']>=2
  self.claim_project([]);self.spend(supplies=2);self.operational[mid]['repaired']=True;self.receipt('equipment_restored',mission=mid,scope='physical_equipment_only',supplies=2,projects=1)
 def summary(self):
  result=super().summary()
  result['operational_epilogues']={mid:dict(service='delivered_in_window' if x['service'] else 'missed_window',equipment='preserved' if x['intact'] else 'restored_later' if x['repaired'] else 'not_restored',label=SPEC['services'][mid]['label']) for mid,x in self.operational.items()}
  return result
def operation(battle):
 return dict(service=battle.service_done,intact=battle.e[battle.spec['source_enemy']]['hp']>0,source=battle.spec['id'],repaired=False,service_ticks=deepcopy(battle.service_history)) if battle.spec else None
def record_operation(g,battle,r):
 if not battle.spec:return
 assert battle.b['id'] not in g.operational
 g.operational[battle.b['id']]=operation(battle);g.receipt('operational_outcome',mission=battle.b['id'],service=battle.service_done,intact=g.operational[battle.b['id']]['intact'])
def prepare_day(g):
 if PROFILE=='protected' and g.day>4 and 'shield' not in g.tools and g.resources['credits']>=30 and g.resources['parts']>=3:g.buy_tool('shield')
 if PROFILE in ['protected','specialists'] and g.day>7 and 'insulation' not in g.tools and g.resources['credits']>=30 and g.resources['parts']>=2:g.buy_tool('insulation')
def training_and_repairs(g):
 if PROFILE=='protected' and not SKIP_TRAIN:
  for key in ['protected_work','mutual_cover']:
   if g.projects>=2:break
   if ('lin','su',key) not in g.protocols and all(g.healthy(a) and a not in g.used and g.crew[a]['fatigue']+8<=100 for a in ['lin','su']) and all(g.rel[p]['trust']>=60 for p in ['lin>su','su>lin']) and g.resources['supplies']>=2:g.train(['lin','su'],key)
 if DO_REPAIR:
  for mid,x in g.operational.items():
   if not x['intact'] and not x['repaired'] and g.projects<2 and g.resources['supplies']>=2:g.repair_equipment(mid);break
def factory(board,goals,party,levels=None,**kw):
 g=ACTIVE;options=[];trained=[p for p in g.protocols if set(p[:2])<=set(party)];trust={(a,b):g.rel.get(a+'>'+b,{}).get('trust',0) for a in party for b in party if a!=b}
 spec=SPEC['services'].get(board['id']);modes=['safe'] if PROFILE=='safe' or not spec else ['protected','independent'] if PROFILE=='protected' else ['independent'] if PROFILE=='specialists' else ['dismantle']
 for mode in modes:
  watchers=itertools.permutations(range(3),len(spec['posts'])) if spec and mode!='safe' else [()]
  for watcher in watchers:
   options_kw=deepcopy(kw)
   if PROFILE=='dismantle':options_kw['skills']=False
   gear=options_kw.setdefault('gear',{})
   if mode!='safe' and 'insulation' in g.tools:gear['insulation']=watcher[0]
   if mode!='safe' and 'shield' in g.tools:gear['shield']=next(i for i in range(3) if i not in watcher)
   battle=ChoiceBattle(board,goals,party,levels,approach=mode,watchers=watcher,trained=trained,trust=trust,**options_kw);r=battle.run();options.append((battle,r))
 # Default objective is still primary completion. Optional ambition never forces a loss.
 if spec and PROFILE!='safe':
  battle=ChoiceBattle(board,goals,party,levels,approach='safe',trained=trained,trust=trust,**deepcopy(kw));r=battle.run();options.append((battle,r))
 chosen,r=min(options,key=lambda z:rank(z[1]))
 chosen.run=lambda:r  # Already executed once. Return the immutable chosen receipt below.
 return chosen
def rank(r):
 return (not r['success'],not r.get('service_secured',False),not r.get('machinery_intact',True) if PROFILE!='dismantle' else False,r['downed'],r['damage'],r['rounds'],r['ap'])
ns.update(Ledger=Ledger,Party=factory,record_operation=record_operation,operation=operation,prepare_day=prepare_day,training_and_repairs=training_and_repairs,rank=rank)
scenarios=[]
for name,profile,repair,options in [
 ('基础通关，不接现场值守','safe',False,{}),
 ('固定偏好，支付训练争取在线服务','protected',False,dict(fixed=True)),
 ('工程电力与防护人员轮换','specialists',False,{}),
 ('拆除威胁，营地优先维修','dismantle',True,{}),
 ('同样拆除，保留物资与项目','dismantle',False,{}),
 ('轮换并做全部可出勤支线','protected',True,dict(sides=True)),
 ('最高难度连续失误后仍继续','protected',True,dict(hard=True,disasters=(6,7,8,15)))]:
 PROFILE=profile;DO_REPAIR=repair
 s=ns['run'](name,**options);q=s['summary'];q['operational_summary']=dict(service_delivered=sum(x['service'] for x in s['operational'].values()),intact=sum(x['intact'] for x in s['operational'].values()),repaired=sum(x['repaired'] for x in s['operational'].values()),unrepaired=sum(not x['intact'] and not x['repaired'] for x in s['operational'].values()),repair_projects=sum(r['kind']=='equipment_restored' for r in s['receipts']))
 scenarios.append(s);print(name,q['main_count'],q['side_count'],q['resources'],q['operational_summary'],flush=True)
out=dict(version='0.10-approach-review',scope='Actual earned levels,trust,paid training and purchased tools. Seven complete campaigns; best candidate policies use hindsight, not player success estimates. Optional equipment repairs share the real two-project camp budget; no service is retroactively restored.',scenarios=scenarios,actual_battles=sum(len(s['battles']) for s in scenarios))
(O/'approach-campaign-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
