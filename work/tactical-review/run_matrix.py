"""Reproducible whole-map strategy witnesses, comparisons, and honest failure logs."""
from pathlib import Path
from copy import deepcopy
import json,itertools,hashlib
from encounter import Encounter
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design';O=ROOT/'outputs'
B=json.loads((D/'boards.json').read_text())['boards'];OLD=json.loads((ROOT/'work/tactical-review/boards-before.json').read_text())['boards'];STYLES=['controls','rush','attack','optional_first'];checks=[];witnesses=[];cases=[];all_runs=[]
def check(name,ok):assert ok,name;checks.append(name)
def short(r):return {k:v for k,v in r.items() if k not in ['log','used']}
def rank(r):return (not r['success'],r['downed'],r['rounds'],r['damage'],r['ap'])
def extras(b,goals):
 out={o['id'] for o in b['objectives']}-set(goals)
 if b['id']=='M17':out-=({'isolate'} if 'repair2' in goals else {'repair1','repair2'})
 if b['id']=='M24':out={'archive'}
 return out
def source_cases(boards):
 for b in boards:
  for route,groups in b.get('route_groups',{'default':b['mandatory_groups']}).items():
   for goals in itertools.product(*groups):yield b,route,goals

# Save pre-amendment comparisons with the SAME corrected simulator, not preliminary output.
before=[]
for b,route,goals in source_cases(OLD):
 for style in STYLES:
  r=Encounter(b,goals,style=style,extra=extras(b,goals)).run();before.append(dict(route=route,**short(r)))
(O/'tactical-before-comparison.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')

for b,route,goals in source_cases(B):
 for difficulty,variant in itertools.product(['relaxed','standard','hard'],['A','B']):
  trials=[]
  for style in STYLES:
   r=Encounter(b,goals,difficulty,variant,style).run();trials.append(r);all_runs.append(dict(route=route,**short(r)))
  best=min(trials,key=rank);case=dict(route=route,**short(best),successful_strategies=[r['style'] for r in trials if r['success']])
  cases.append(case)
  if best['success']:witnesses.append({**best,'route':route,'used':{str(k):v for k,v in best['used'].items()}})
  print(b['id'],route,','.join(goals),difficulty,variant,'OK' if best['success'] else 'NO WITNESS',best['rounds'],best['damage'],flush=True)
check('all36boards and46goal combinations represented',len({r['mission'] for r in cases})==36 and len(cases)==46*6)
check('all276difficulty/environment/goal cases have full extracted basic-action witness',all(r['success'] for r in cases))

# Optional ambition and different priorities; no promise that every aspiration fits one run.
optional=[];gear=[];delay=[]
eq={e['id']:e for e in json.loads((D/'equipment.json').read_text())['items']}
for b,route,goals in source_cases(B):
 extra=extras(b,goals)
 for style in STYLES:
  r=Encounter(b,goals,style=style,extra=extra).run();optional.append(dict(route=route,all_requested_secured=extra<=set(r['secured']),**short(r)))
 # Deliberately waste an entire opening round; retreat remains legal even if a goal expires.
 rs=[Encounter(b,goals,style=s,delay=1).run() for s in STYLES]
 delay.append(dict(route=route,**short(min(rs,key=rank))))
 # Slot assignment is part of the choice: test each carrier, not a magically shared tool.
 candidates=['cooperation','refusal','growth','growth_move','incoming_failure']
 for item in ['crowbar','battery','cutter','stretcher','scanner']:
  if b['day']>eq[item]['unlocked_after_main']:candidates.append(item)
 for item in candidates:
  for actor in (list(itertools.combinations(range(3),2)) if item in ['cooperation','refusal'] else range(3) if item in ['crowbar','battery','cutter','stretcher','scanner'] else [None]):
   load={'cooperation':True,'cooperation_pair':list(actor),'refusal':item=='refusal'} if item in ['cooperation','refusal'] else {item:actor} if actor is not None else {'cooperation':True,'refusal':True} if item=='refusal' else {item:True}
   level=2 if item in ['growth','growth_move'] else 1
   # Same policy and same extra ambitions, so resource/action differences stay inspectable.
   for style in ['controls','rush']:
    r=Encounter(b,goals,style=style,gear=load,level=level,extra=extra).run();gear.append(dict(item=item,holder=actor,route=route,controlled_level_case=item in ['growth','growth_move'],controlled_learned_pair_case=item in ['cooperation','refusal'],**short(r)))
check('high resentment/refused protocol still has a baseline full-map strategy',all(any(g['success'] for g in gear if g['mission']==b['id'] and g['goals']==sorted(goals) and g['route']==route and g['item']=='refusal') for b,route,goals in source_cases(B)))
# Cross product: growth x real equipment x cooperation boundary x difficulty.
factorial=[]
for b,route,goals in source_cases(B):
 item='scanner' if b['day']>10 else 'crowbar'
 for level,equipped,refused,difficulty in itertools.product([1,2],[False,True],[False,True],['standard','hard']):
  load={'cooperation':True,'cooperation_pair':[0,2],'refusal':refused}
  if equipped:load[item]=0
  trials=[Encounter(b,goals,difficulty=difficulty,style=style,gear=load,level=level).run() for style in ['controls','rush']]
  best=min(trials,key=rank);factorial.append(dict(route=route,equipped=equipped,refused=refused,**short(best)))
check('all736crossed growth/equipment/relationship/difficulty cases have a retained basic solution',all(x['success'] for x in factorial))
# Every ordinary party shares the witnessed universal actions; no need to fake56 distinct simulations.
check('baseline witnesses consume no specialty/equipment/protocol action',all(all(x['action'] not in ['battery','cutter','crowbar','protected_work'] for x in r['log']) for r in witnesses))
check('basic witnesses retrieve all3 standing actors without downing',all(r['healthy_extracted']==3 and r['downed']==0 for r in witnesses))
check('no witness awards a lost target as secured',all(not(set(r['lost'])&set(r['secured'])) for r in witnesses))
check('no equipment comparison exceeds finite reinforcement cap',all(r['spawned']<=2 for r in gear))

# Explicitly report bounded search failures, rather than silently dropping them.
failures=[r for r in all_runs if not r['success']]
opportunity=[r for r in optional if r['mission'] in ['M06','M12','M18','S07']]
changes=[]
for mid in ['M06','M12','M18','S07']:
 old=[r for r in before if r['mission']==mid];new=[r for r in opportunity if r['mission']==mid]
 changes.append(dict(mission=mid,before=old,after=new))
unchanged=json.loads((ROOT/'work/tactical-review/runtime-before.json').read_text())
now={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and f.suffix in ['.gd','.tscn','.godot'] and '.godot' not in f.parts}
check('production runtime remains byte-identical',unchanged==now)
out={'version':'0.7-tactical-review','passed_count':len(checks),'checks':checks,'scope':'Whole-map deterministic simulation of universal actions, six enemy types, occupied endpoints, HP, object damage, stabilization and optional deadlines, water/fire, finite waves, work/channel/convoy and extraction. Four fixed heuristic policies are not exhaustive search or human play. Specialty effects are covered separately by controlled fixtures; not every specialty is used by this automatic policy.','cases':cases,'strategy_runs':all_runs,'attempt_count':len(all_runs),'failed_policy_attempts':failures,'optional_runs':optional,'gear_runs':gear,'one_round_delay':delay,'factorial_cases':factorial,'amendment_comparisons':changes,'counts':{'map_goal_cases':46,'difficulty_variant_cases':len(cases),'policy_attempts':len(all_runs),'optional_attempts':len(optional),'equipment_growth_relationship_attempts':len(gear),'one_round_delay_attempts':len(delay)*4,'full_basic_witnesses':len(witnesses),'factorial_configurations':len(factorial),'factorial_policy_attempts':len(factorial)*2},'limitations':['A found legal trace establishes an available solution for that configuration, not that novices will discover it.','A failed heuristic does not prove a level impossible.','Controlled level2 comparisons isolate growth; they are not a claim that every early mission can field three level2 actors.','All24specialties are not exhaustively composed across all56named trios and every equipment slot.','No player enjoyment, UI discoverability, final duration, market or production implementation claim.']}
(O/'tactical-matrix-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(O/'tactical-full-witnesses.json').write_text(json.dumps(witnesses,ensure_ascii=False)+'\n')
print(json.dumps({'checks':len(checks),'counts':out['counts'],'failed_policy_attempts':len(failures),'one_round_delay_solved':sum(x['success'] for x in delay)},ensure_ascii=False,indent=2))
