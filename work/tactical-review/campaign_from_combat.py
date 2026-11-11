"""Feed ACTUAL rehearsal outcomes/contributions into the existing campaign ledger.
This is still offline design analysis, not a game controller.
"""
from pathlib import Path
from copy import deepcopy
import json,runpy,contextlib,io,itertools
from encounter import Encounter
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs'
with contextlib.redirect_stdout(io.StringIO()):ns=runpy.run_path(str(ROOT/'work/campaign-review/ledger_review.py'))
Ledger=ns['Ledger'];B=ns['BOARDS'];calendar={x['day']:x['scenes'] for x in ns['CAL']}
def run(hard=False):
 g=Ledger('实际战斗结果驱动的'+('最高难度' if hard else '标准')+'轮换整局',hard=hard);battles=[];skipped=[]
 for day in range(1,25):
  b=B[f'M{day:02}'];party=g.choose_party();assert len(party)==3
  support=next((a for a in g.crew if a not in party and g.eligible(a,8) and (a!='su' or 'su' not in g.plans)),None)
  if day==24:g.route='shared_control' if 'shared_control' in g.available_routes() else 'distributed_rebuild'
  goals=[group[0] for group in (b['route_groups'][g.route] if day==24 else b['mandatory_groups'])]
  trials=[]
  for style in ['controls','rush','attack']:
   battle=Encounter(b,goals,difficulty='hard' if hard else 'standard',style=style);r=battle.run();trials.append((battle,r))
  battle,r=min(trials,key=lambda x:(not x[1]['success'],x[1]['downed'],x[1]['rounds'],x[1]['damage'],x[1]['ap']))
  assert r['success']
  # Floor comparison: actual actors may have higher HP/passives; this conservative
  # route voluntarily uses only10HP and universal actions, no invented skill access.
  g.deploy(b['id'],party,support)
  completed=[k for k,o in battle.objects.items() if o['done'] and k not in battle.control_ids]
  secured=[k for k in r['secured'] if k in completed]
  contributions={}
  for k in completed:
   actual=[]
   for action in battle.objects[k]['contributions']:
    name=party[action['actor']]
    if name not in actual:actual.append(name)
   if actual:contributions[k]=actual
  packet=dict(mission=b['id'],completed=completed,secured=secured,contributions=contributions,injured=[],withdrawn=[],consumed={},protection=[],all_extracted=True,xu_standing_on_exit='xu' in party,kept_deadline=r['rounds']<=battle.limit-2,branch=g.route if day==24 else 'repair' if day==17 else None)
  g.settle(packet);battles.append(dict(day=day,party=party,rounds=r['rounds'],limit=r['limit'],ap=r['ap'],damage=r['damage'],style=r['style'],completed=completed,actual_contributors=contributions,xp_after={a:g.crew[a]['xp'] for a in party}))
  if day==24:break
  g.begin_camp();g.confirm_audits()
  for node in calendar[day]:
   try:g.scene(node)
   except AssertionError:skipped.append(dict(day=day,node=node,reason='current state/project/proof constraints; not silently granted'))
  urgent=[a for a in g.crew if g.healthy(a) and a not in g.used and g.crew[a]['fatigue']>=60]
  if urgent and g.projects<2:g.recover(urgent[:2])
  if day in [20,22,23] and g.projects<2:
   missing=next((e for e in ['E_ORDER','E_MAINTENANCE','E_WARNING'] if e not in g.evidence),None)
   if missing:g.review([missing]);g.confirm_audits()
  if g.projects<2:
   trainees=sorted([a for a in g.crew if g.healthy(a) and a not in g.used and g.crew[a]['fatigue']+8<=100],key=lambda a:g.crew[a]['xp'])[:2]
   if trainees and g.resources['supplies']>=len(trainees):g.train(trainees)
  g.confirm_audits();g.night()
 summary=g.summary();assert summary['main_count']==24 and g.phase=='ending' and all(v>=0 for v in g.resources.values())
 return dict(summary=summary,battles=battles,skipped_nodes=skipped,receipts=g.records)
results=[run(),run(True)]
out={'scope':'24 actual simulated battles feed one ledger per scenario. Party availability, fatigue, XP, supplied support work, projects, narrative proof and ending evaluated together. Tactical solution is selected from3 heuristic policies, not a simulated novice; no auto-granted personal reconciliation.','scenarios':results,'checks':['48 simulated main battles actually completed','combat contributions mapped to actual assigned characters','camp costs/fatigue use the same ledger','personal story proof not synthesized from victory','final route eligibility checked from actual world/evidence','no runtime development performed']}
(O/'campaign-from-tactical-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([dict(name=x['summary']['name'],ending=x['summary']['world_ending'],resources=x['summary']['resources'],verified_contracts=x['summary']['verified_contracts'],levels=x['summary']['levels']) for x in results],ensure_ascii=False,indent=2))
