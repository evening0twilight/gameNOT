"""Adversarial checks for the operational-choice rules, plus full-map counterexamples."""
from pathlib import Path
from copy import deepcopy
import json,itertools,hashlib
from encounter_choices import ChoiceBattle,SPEC,distance,adjacent
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';B={b['id']:b for b in json.loads((ROOT/'game/data/final_design/boards.json').read_text())['boards']};checks=[]
P=['lin','xu','su'];trained=[('lin','su',k) for k in ['protected_work','mutual_cover','relay_carry','coordinated_pull']]
def check(name,value):assert value,name;checks.append(name)
def rejects(fn):
 try:fn();return False
 except AssertionError:return True
for mid,spec in SPEC['services'].items():
 board=B[mid];source=next(e for e in board['enemies'] if e['id']==spec['source_enemy'])
 check(mid+' identifies recoverable asset before its destruction',source.get('recoverable_asset') and bool(source.get('asset_disclosure')))
 check(mid+' discloses the service affected by linked shutdown',all(c.get('service_linked')==spec['id'] and c.get('service_shutdown_effect')==spec['reason'] and '暂停现场服务' in c['label'] for c in board['controls'] if c['id'] in spec['linked_controls']))
def fixture(mid='M22'):
 g=ChoiceBattle(B[mid],[x[0] for x in B[mid]['mandatory_groups']],P,{a:3 for a in P},approach='protected',trained=trained,watchers=[0] if len(SPEC['services'][mid]['posts'])==1 else [0,2]);g.rnd=2;g.publish()
 for h in g.h:h['ap']=2
 return g
# Fixtures isolate exact edge cases; their positions are not full-map witnesses.
g=fixture();post=tuple(g.spec['posts'][0]);g.h[0]['p']=post;g.h[2]['p']=(post[0]+1,post[1]);g.guarded_watch(0,2,0)
check('paid guarded watch consumes one AP from each participant',g.h[0]['ap']==g.h[2]['ap']==1)
g.hit_hero(g.h[0],3,g.spec['source_enemy']);check('guarded watch tolerates one nonfatal machine interruption',not g.hit_during_watch.get(0) and g.h[0]['hp']==9)
g.hit_hero(g.h[0],3,g.spec['source_enemy']);check('same guard cannot absorb a second machine interruption',g.hit_during_watch.get(0))
g=fixture();g.h[0]['p']=post;g.h[2]['p']=(post[0]+1,post[1]);g.guarded_watch(0,2,0);g.hit_hero(g.h[0],2,'live_water',True)
check('guarding does not grant electricity immunity',g.hit_during_watch.get(0) and g.h[0]['hp']==8)
g=fixture();g.h[0]['p']=post;g.h[2]['p']=(post[0]+1,post[1]);g.h[0]['hp']=1;g.guarded_watch(0,2,0);g.hit_hero(g.h[0],3,g.spec['source_enemy'])
check('downed operator cannot be kept on duty by a guard',g.h[0]['down'] and g.hit_during_watch.get(0))
g=fixture();g.h[0]['p']=post;g.h[2]['p']=(post[0]+1,post[1]);g.guarded_watch(0,2,0);g.h[2]['p']=(7,7);g.hit_hero(g.h[0],3,g.spec['source_enemy'])
check('walking away invalidates the live safeguard',g.hit_during_watch.get(0))
g=fixture('M10');g.h[0]['p']=tuple(g.spec['posts'][0]);g.watch(0,0);g.h[0]['p']=tuple(g.spec['posts'][1]);check('one operator cannot count as two simultaneous posts',rejects(lambda:g.watch(0,1)))
g=fixture();g.h[0]['p']=post;g.h[0]['carry']='e';check('carrying an object prevents precision watch',rejects(lambda:g.watch(0,0)))
g.h[0]['carry']=None;g.watch(0,0);check('same post cannot be paid twice for extra progress',rejects(lambda:g.watch(0,0)))
g=fixture();g.h[0]['p']=post;g.h[2]['p']=(post[0]+1,post[1]);g.trust[(0,2)]=59;check('unearned trust does not unlock cooperation',rejects(lambda:g.guarded_watch(0,2,0)))
g.trust[(0,2)]=60;g.trained.clear();check('unpaid training cannot be substituted by high trust',rejects(lambda:g.guarded_watch(0,2,0)))
g=fixture();g.h[0]['p']=post;g.h[2]['p']=(post[0]+1,post[1]);g.relations[('lin','leader')]=True
check('unrelated historical resentment does not block terminal work',g.protocol_ready('protected_work',0,2))
g=fixture('M21');post=tuple(g.spec['posts'][0]);g.h[0]['p']=post;g.h[2]['p']=(post[0]+1,post[1]);g.relations[('lin','leader')]=True
check('relevant relationship restriction applies to service cooperation',not g.protocol_ready('protected_work',0,2))
g.h[1]['p']=(post[0]-1,post[1]);g.prepare_safety(1,0,2,'protected_work');check('real third-person safety action satisfies the same restriction',g.protocol_ready('protected_work',0,2) and g.h[1]['ap']==1)

electrical=ChoiceBattle(B['M17'],['repair2'],['chen','ye','he'],{a:3 for a in ['chen','ye','he']},approach='protected',trained=[('chen','ye','protected_work')],relations={('chen','leader'):True,('ye','leader'):True})
electrical.rnd=2;electrical.h[0]['p']=(6,3);electrical.h[1]['p']=(6,2);electrical.h[2]['p']=(5,3)
electrical.prepare_safety(2,0,1,'protected_work')
check('third-person protection cannot substitute for electrical safeguards',not electrical.protocol_ready('protected_work',0,1))
electrical.insulated.update([(6,3),(6,2)])
check('Chen still requires real reinforcement in addition to insulation',not electrical.protocol_ready('protected_work',0,1))
assert electrical.cast(electrical.h[0],'chen_3','live_service')
check('actual reinforcement and insulation satisfy Chen and Ye together',electrical.protocol_ready('protected_work',0,1))

# Power restoration spends real AP and changes only the affected warnings.
g=fixture('M13');controls=g.spec['linked_controls']
for key in controls:g.objects[key].update(done=True,secured=True,progress=g.objects[key]['work'])
source=g.e[g.spec['source_enemy']];source['disabled']=True;g.h[0]['p']=g.objects[controls[0]]['p'];other=next(e for e in g.e.values() if e['id']!=source['id']);before=deepcopy(other);pending=deepcopy(g.pending)
check('full linked shutdown switches off the service',not g.power_live())
g.restore_power(0,controls[0]);check('ordinary restoration restores bus with a real AP cost',g.power_live() and g.h[0]['ap']==1)
check('restoration does not reroll unrelated warnings or spawn twice',g.e[other['id']]==before and g.pending==pending)
check('restoring an already live control cannot be spammed',rejects(lambda:g.restore_power(0,controls[0])))

# Two complete direct counterfactuals on exactly the same starting party and plan.
counter=[]
for mid,watchers in [('M22',[0]),('M21',[0,2]),('M10',[2,0])]:
 b=B[mid];goals=[x[0] for x in b['mandatory_groups']]
 for mode in ['independent','protected']:
  battle=ChoiceBattle(b,goals,P,{a:3 for a in P},skills=True,approach=mode,trained=trained,watchers=watchers,style='controls');r=battle.run();counter.append(dict(mission=mid,mode=mode,**{k:v for k,v in r.items() if k not in ['mission','used']}))
check('M22 cooperation changes the delivered service, not merely AP',counter[0]['success'] and counter[1]['success'] and not counter[0]['service_secured'] and counter[1]['service_secured'] and counter[1]['machinery_intact'])

post=tuple(SPEC['services']['M22']['posts'][0])
# Service completion remains a fact even when power is later deliberately cut.
g=fixture();g.service_done=True;g.objects['live_service'].update(done=True,secured=True)
for k in g.spec['linked_controls']:g.objects[k]['done']=True
g.environment();check('later power isolation cannot erase completed service',g.service_done and g.objects['live_service']['secured'])
g=fixture();g.rnd=g.spec['deadline'];g.environment();g.rnd+=1;g.h[0]['p']=post;g.h[0]['ap']=2
check('missed service window cannot be revived by late watching',g.service_failed and rejects(lambda:g.watch(0,0)))
g=fixture();g.service_ticks=1;g.service_contributors={'su'};g.environment();check('interrupted sequence discards stale contribution credit',g.service_ticks==0 and not g.service_contributors)

# New tactical interfaces preserve their stated geometry and limited budget.
g=fixture('M08');e=g.e[g.spec['source_enemy']];e['p']=(7,2);g.h[0]['p']=(6,2);g.h[2]['p']=(7,1)
g.precise_pull(0,2,e['id'],(7,3));check('coordinated pull follows the chosen legal direction',e['p']==(7,3) and e['rail_index']==1)
g=fixture('M08');e=g.e[g.spec['source_enemy']];e['p']=(7,2);g.h[0]['p']=(7,1);g.h[2]['p']=(7,3);g.precise_pull(0,2,e['id'],(6,2));g.rnd+=1;g.publish();g.environment()
check('off-rail machine does not teleport back next round',e['p']==(6,2) and e['off_rail'] and not g.working(e))
g=fixture('M08');e=g.e[g.spec['source_enemy']];g.h[0]['p']=(7,1);g.h[2]['p']=(7,3);check('pull cannot enter an occupied target cell',rejects(lambda:g.precise_pull(0,2,e['id'],(7,3))))
g=fixture('M22');g.h[0].update(p=(1,6),carry='e');g.h[2]['p']=(2,6);g.objects['e']['carrier']=0
g.relay_path(0,2,[(2,6),(3,6),(4,6)]);check('relay can move to a chosen on-site staging point',g.h[2]['p']==(4,6) and g.h[2]['carry']=='e' and g.h[0]['carry'] is None and (4,6) not in g.exits)
check('relay pays both actors instead of minting actions',g.h[0]['ap']==g.h[2]['ap']==1)
g=fixture('M22');g.h[0].update(p=(1,6),carry='e');g.h[2]['p']=(2,6);snapshot=[(h['p'],h['ap'],h['carry']) for h in g.h]
check('invalid relay path fails before moving or charging anyone',rejects(lambda:g.relay_path(0,2,[(2,6),(6,6)])) and snapshot==[(h['p'],h['ap'],h['carry']) for h in g.h])

stress=[]
for mid,spec in SPEC['services'].items():
 b=B[mid];goals=[x[0] for x in b['mandatory_groups']];watchers=[0] if len(spec['posts'])==1 else [0,2]
 for difficulty,variant in itertools.product(['relaxed','standard','hard'],['A','B']):
  trials=[]
  for mode in ['safe','independent','protected','dismantle']:
   battle=ChoiceBattle(b,goals,P,{a:3 for a in P},skills=True,approach=mode,trained=trained,watchers=watchers,difficulty=difficulty,variant=variant,style='controls');r=battle.run();trials.append({k:v for k,v in r.items() if k not in ['log','used','service_ticks']})
  stress.append(dict(mission=mid,difficulty=difficulty,variant=variant,trials=trials))
check('all72 service-map difficulty/weather contexts retain a base solution',all(any(t['success'] for t in x['trials'] if t['approach']=='safe') for x in stress))
check('no recorded HP/AP or watch rate exceeds the rules',all(t['ap']>=0 and (not t['service_secured'] or t['rounds']>=2) for x in stress for t in x['trials']))
C=json.loads((O/'approach-campaign-results.json').read_text())
for scenario in C['scenarios']:
 s=scenario['summary'];check(s['name']+' finishes24main without negative resources',s['main_count']==24 and all(v>=0 for v in s['resources'].values()))
 repairs=[r for r in scenario['receipts'] if r['kind']=='equipment_restored'];check(s['name']+' repairs unique and paid',len({r['mission'] for r in repairs})==len(repairs) and all(r['supplies']==2 and r['projects']==1 for r in repairs))
 check(s['name']+' preserves two-project cap',all(x.get('night',{}).get('projects',0)<=2 for x in scenario['rows']))
for s in C['scenarios']:
 check(s['summary']['name']+' ending preserves separate service and equipment facts',all(s['summary']['operational_epilogues'][mid]['service']==('delivered_in_window' if x['service'] else 'missed_window') and s['summary']['operational_epilogues'][mid]['equipment']==('preserved' if x['intact'] else 'restored_later' if x['repaired'] else 'not_restored') for mid,x in s['operational'].items()))
 for mid,x in s['operational'].items():
  if x['service']:
   history=x['service_ticks'];check(s['summary']['name']+mid+' has consecutive observed service ticks',any(a['valid'] and b['valid'] and a['round']+1==b['round'] for a,b in zip(history,history[1:])))
W=json.loads((O/'approach-protocol-witnesses.json').read_text());w={r['witness_name']:r for r in W}
check('complete relay path preserves archive beyond primary rescue',w['relay']['success'] and 'asset' in w['relay']['secured'] and w['ordinary_handoff']['success'] and 'asset' not in w['ordinary_handoff']['secured'])
check('relay outcome is not disguised as a faster clear',w['relay']['rounds']>w['ordinary_handoff']['rounds'])
check('complete pull plan preserves bus service and equipment',w['pull']['success'] and w['pull']['service_secured'] and w['pull']['machinery_intact'])
check('full pull actually walks pushes pulls and restores power',all(any(r['action']==a for r in w['pull']['log']) for a in ['move','push','coordinated_pull','restore_power','service_watch']))
check('ordinary parallel allocation remains a full M22 alternative',w['ordinary_parallel_M22']['success'] and w['ordinary_parallel_M22']['service_secured'] and w['ordinary_parallel_M22']['machinery_intact'] and {'e','privacy','handover','live_service'}<=set(w['ordinary_parallel_M22']['secured']) and w['ordinary_parallel_M22']['skill_actions']==0 and w['ordinary_parallel_M22']['protocol_effects']==0 and not w['ordinary_parallel_M22']['gear'])
from guidance import Guidance
for r in W:
 guide=Guidance();board=deepcopy(B[r['mission']]);guide.scene(board,r['log'])
 check('new protocol trace obeys tutorial budget '+r['witness_name'],sum(x['kind']=='nonmodal_card' for x in guide.log)<=1)
runtime={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and f.suffix in ['.gd','.tscn','.godot'] and '.godot' not in f.parts}
check('formal runtime remains unchanged',runtime==json.loads((ROOT/'work/tactical-review/runtime-before.json').read_text()))
out=dict(version='0.10-approach-review',passed_count=len(checks),checks=checks,counterfactuals=counter,difficulty_weather_contexts=stress,runtime_unchanged=True,scope='Targeted adversarial fixtures and complete tactical/campaign reference traces,not human fun/UI verification.')
(O/'approach-review-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('0.10 checks passed:',len(checks))
