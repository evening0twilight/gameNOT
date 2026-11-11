"""Rule, geometry, learning and economic boundary checks for0.11."""
from pathlib import Path
from copy import deepcopy
import json,itertools,hashlib
from choices import ChoiceBattle,CONTRACT,SPEC,HISTORICAL,Party
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design';B={b['id']:b for b in json.loads((D/'boards.json').read_text())['boards']};P=['lin','xu','su'];checks=[]
def check(n,v):assert v,n;checks.append(n)
def rejects(fn):
 try:fn();return False
 except (AssertionError,StopIteration):return True
def fixture(mid):
 g=ChoiceBattle(B[mid],[x[0] for x in B[mid]['mandatory_groups']],P,{a:3 for a in P},approach='independent');g.rnd=1;g.publish()
 for e in g.e.values():e['skip']=99;e['intent']=[]
 for k in g.spec.get('prerequisites',[]):g.objects[k]['done']=True
 return g
def pay(g,post=0,a=0):
 g.h[a].update(p=tuple(g.spec['posts'][post]),ap=2);g.watch(a,post)
def next_round(g):
 g.rnd+=1;g.publish()
 for e in g.e.values():e['skip']=99;e['intent']=[]
check('four operations replace twelve, eight retired',len(SPEC['services'])==4 and len(CONTRACT['removed_services'])==8)
check('four cadence types, only one continuous dual hold',len({s['mode'] for s in SPEC['services'].values()})==4 and sum(s['mode']=='consecutive' for s in SPEC['services'].values())==1)
g=fixture('M10');g.trust[(0,2)]=20;g.trained.clear();check('basic cover does not require buying training or trust60',g.protocol_ready('mutual_cover',0,2))
check('advanced handoff still requires real learning and trust',not g.protocol_ready('relay_carry',0,2))
g=fixture('M21');g.relations[('lin','leader')]=True;check('free cover still respects concrete fall-safety restriction',not g.protocol_ready('protected_work',0,2))
g.h[0]['p']=(4,2);g.h[2]['p']=(4,3);g.h[1]['p']=(3,2);g.prepare_safety(1,0,2,'protected_work');check('actual third-person safeguard restores basic cooperation',g.protocol_ready('protected_work',0,2))
g=fixture('M21');g.relations[('lin','leader')]=True;g.h[2]['p']=(4,2);g.h[0]['p']=(4,4);g.h[1]['p']=(3,2);g.prepare_safety(1,2,0,'mutual_cover');check('protecting partner does not falsely satisfy Lin own safety condition',not g.protocol_ready('mutual_cover',2,0))
g=ChoiceBattle(B['M10'],['test1','test2'],['reserve0','lin','su']);check('community reserve can perform basic cover, not advanced skills',g.protocol_ready('mutual_cover',0,1) and not g.protocol_ready('relay_carry',0,1))
for mid in CONTRACT['removed_services']:
 g=ChoiceBattle(B[mid],[x[0] for x in B[mid]['mandatory_groups']],P,approach='protected')
 check(mid+' no retired objective or service-control warning','live_service' not in g.objects and not any(c.get('service_linked') for c in B[mid]['controls']))
g=fixture('M05');g.objects['pump']['done']=False;check('unrepaired pump cannot drain water',rejects(lambda:pay(g)))
g=fixture('M05');pay(g);g.environment();check('first drainage stage changes actual shallow cells',g.service_ticks==1 and g.rows[3][6]=='.' and not g.service_done)
next_round(g);g.environment();check('interrupted drainage retains completed stage',g.service_ticks==1)
next_round(g);pay(g);g.environment();check('resumed drainage completes without erasing earlier work',g.service_done and g.rows[4][6]=='.')
g=fixture('M10');pay(g,0,0);g.environment();check('one operator cannot complete two-terminal confirmation',not g.service_done)
next_round(g);pay(g,0,0);pay(g,1,2);g.environment();check('one synchronous round completes M10',g.service_done and not g.opened_exit)
for k in ['test1','test2']:g.objects[k]['done']=True
next_round(g);g.environment();check('new exit requires both existing tests as well as confirmation',g.opened_exit and (6,1) in g.exits)
g=fixture('M21');pay(g,0,0);pay(g,1,2);g.environment();check('first bridge round is not enough',g.service_ticks==1 and not g.service_done)
next_round(g);g.environment();check('interrupted continuous escort resets progress',g.service_ticks==0)
g=fixture('S11');pay(g);g.environment();check('clinic shifts real operating position after first stage',g.service_ticks==1 and g.spec['posts']==[[6,3]] and not g.service_done)
next_round(g);g.environment();check('clinic movement gap does not erase first connection',g.service_ticks==1)
next_round(g);pay(g);g.environment();check('clinic second position completes handover',g.service_done)
g=fixture('S11');g.h[0].update(p=(6,2),ap=2);g.h[0]['tools']=['insulation'];g.gear['insulation']=0;g.policy();g.environment()
check('planner does not spend wet-ground mat on dry first stage',g.used.get((0,'insulation'),0)==0)
g=fixture('M05');g.current_helpers.add('su');g.environment();check('failed accumulated stage cannot award stale helper credit',not g.service_contributors)
g=fixture('M21');g.service_done=True;g.objects['live_service'].update(done=True,secured=True);g.objects['route']['done']=True;g.environment()
for k in g.spec['linked_controls']:g.objects[k]['done']=True
g.environment();check('later shutdown does not erase bridge passage already earned',g.service_done and g.opened_exit)
g=fixture('M05');g.rnd=g.spec['deadline'];g.environment();g.rnd+=1;g.h[0].update(p=tuple(g.spec['posts'][0]),ap=2);check('late operation cannot recreate past window',rejects(lambda:g.watch(0,0)))
# A geometrical use for coordinated pull, with exactly the same ordinary physics.
g=ChoiceBattle(B['M08'],['block1','block2','truck'],P,{a:2 for a in P},trained=[('lin','su',k) for k in CONTRACT['cooperation_training']['unlocks']]);g.rnd=4;g.publish();e=g.e[HISTORICAL['services']['M08']['source_enemy']];e['p']=(7,5);g.h[0].update(p=(7,6),ap=2);g.h[2].update(p=(7,4),ap=2)
check('westward basic push would require an out-of-map standing cell',not g.passable((8,5)))
g.precise_pull(0,2,e['id'],(6,5));check('two legal side positions can pull the machine off rail intact',e['p']==(6,5) and e['off_rail'] and e['hp']>0)
g.rnd+=1;g.publish();g.environment();check('off-rail movement still cannot teleport',e['p']==(6,5))
# Import only ledger definitions, not another complete campaign run.
p=ROOT/'work/player-choice-review/campaign.py';ns={'__file__':str(p),'__name__':'economic_fixtures'};exec(compile(p.read_text().split('\nscenarios=[]')[0],str(p),'exec'),ns);Ledger=ns['Ledger']
def economy(day=5,intact=False):
 g=Ledger('isolated economic fixture',external_social=True);g.day=day;g.phase='camp';g.operational['M05']=dict(service=False,intact=intact,repaired=False,primary_success=True,service_ticks=[])
 for a in P:g.crew[a].update(fatigue=36,stress=20)
 return g
g=economy();before=deepcopy(g.resources);g.repair_equipment('M05');check('repair pays one real project and two supplies',g.projects==1 and before['supplies']-g.resources['supplies']==2)
check('repair cannot be repeated for new visits',rejects(lambda:g.repair_equipment('M05')))
check('no same-evening payoff after repair',g.available_support('M05')==0)
g.day=6;g.used=set();g.projects=2;trust=deepcopy(g.rel);g.assisted_recovery('M05',['lin','su']);check('volunteer logistics uses neither character assignment nor third camp project',g.projects==2 and not g.used and g.crew['lin']['fatigue']==24)
check('external care neither creates trust nor deletes resentment',g.rel==trust)
check('same evening cannot double spend support',rejects(lambda:g.assisted_recovery('M05',['xu'])))
check('volunteer logistics does not permit a third regular project',rejects(lambda:g.train(['lin'])))
g.projects=0;prior=g.crew['lin']['xp'];g.train(['lin']);check('assisted character can still use a legal training project',g.crew['lin']['xp']==prior+3 and g.projects==1)
g.day=7;g.projects=0;g.used=set();g.assisted_recovery('M05',['lin','su']);g.day=8;g.used=set();check('two visits are finite',g.available_support('M05')==0)
g=economy(intact=True);g.day=6;check('preservation has exactly the same two visits without repair cost',g.available_support('M05')==2 and g.projects==0)
check('intact equipment cannot be demolished through the repair menu',rejects(lambda:g.repair_equipment('M05')))
g=economy(day=8);g.repair_equipment('M05');g.day=9;check('late but timely repair has only one remaining usable evening',g.available_support('M05')==2 and CONTRACT['investments']['M05']['last_day']==g.day)
g.day=10;check('unused visits expire at original calendar end',g.available_support('M05')==0)
g=economy(day=10);g.repair_equipment('M05');g.day=11;check('post-expiry philanthropy cannot renew campaign assistance',g.available_support('M05')==0)
g=economy(intact=True);g.day=6;g.crew['lin']['ready']=8;check('external recovery is not treatment for severe injury',rejects(lambda:g.assisted_recovery('M05',['lin'])))
g=economy(intact=True);g.day=6
for a in ['lin','su']:g.crew[a].update(fatigue=0,stress=0)
g.assisted_recovery('M05',['lin','su']);check('rested characters do not generate imaginary recovery value',g.records[-1]['fatigue_recovered']==0 and g.records[-1]['stress_recovered']==0)
g=economy(intact=True);g.day=6;g.crew['lin']['fatigue']=98;check('high-fatigue return can genuinely prevent training',rejects(lambda:g.train(['lin'])))
g.assisted_recovery('M05',['lin']);g.train(['lin']);check('finite volunteer support can make that training legal',g.crew['lin']['fatigue']==94 and g.projects==1)
g=economy();xp={a:g.crew[a]['xp'] for a in ['lin','su']};sup=g.resources['supplies'];g.train(['lin','su']);check('ordinary pair training learns two advanced actions without extra cost',len(g.protocols)==2 and g.projects==1 and sup-g.resources['supplies']==2 and all(g.crew[a]['xp']==xp[a]+3 for a in xp))
check('second protocol cannot be repurchased for duplicate XP',rejects(lambda:g.train(['lin','su'],'coordinated_pull')))
g.rel['lin>su']['trust']=59;check('learning bundle does not bypass later trust restrictions',not g.cooperation_allowed(['lin','su'],'relay_carry'))
check('camp preflight agrees that basic cover has no trust60 gate',g.cooperation_allowed(['lin','su'],'mutual_cover'))
# Full36-map baseline replay across three difficulties and two weather variants.
baseline=[]
for b in B.values():
 for route,groups in b.get('route_groups',{'default':b['mandatory_groups']}).items():
  for goals in itertools.product(*groups):
   for difficulty,variant in itertools.product(['relaxed','standard','hard'],['A','B']):
    results=[ChoiceBattle(b,goals,P,{a:1 for a in P},skills=False,approach='safe',difficulty=difficulty,variant=variant,style=style).run() for style in ['rush','controls']]
    best=min(results,key=lambda r:(not r['success'],r['downed'],r['damage'],r['rounds']));baseline.append({k:best[k] for k in ['mission','goals','difficulty','variant','success','rounds','damage']})
check('276 baseline goal/difficulty/weather contexts retain a solution',len(baseline)==276 and all(r['success'] for r in baseline))
M=json.loads((O/'player-choice-matrix-results.json').read_text());check('all1432 named baseline configurations remain solvable in sampled policies',M['configurations']==1432 and not M['unfound'])
C=json.loads((O/'player-choice-campaign-results.json').read_text())
check('twelve campaigns include learned cooperation and high-tempo comparisons',len(C['scenarios'])==12)
earned=next(s for s in C['scenarios'] if s['summary']['name'].startswith('真实养成后'));advanced=[r for r in earned['receipts'] if r['kind']=='advanced_actions_used' and r['mission']=='M06']
check('actual earlier training feeds an archive-preserving M06 relay',bool(advanced) and 'asset' in advanced[0]['secured'] and any(r['kind']=='coordination_bundle' and set(r['actors'])=={'lin','su'} and r['day']<6 for r in earned['receipts']) and any(a['action']=='relay_carry' for a in advanced[0]['actions']))
for s in C['scenarios']:
 q=s['summary'];name=q['name'];check(name+' reaches ending with nonnegative resources',q['main_count']==24 and min(q['resources'].values())>=0)
 check(name+' regular camp projects stay capped',all(r.get('night',{}).get('projects',0)<=2 for r in s['rows']))
 assistance=[r for r in s['receipts'] if r.get('external_facility')]
 check(name+' finite dated assistance only',len({r['day'] for r in assistance})==len(assistance) and all(CONTRACT['investments'][r['external_facility']]['first_day']<=r['day']<=CONTRACT['investments'][r['external_facility']]['last_day'] for r in assistance) and all(sum(r['external_facility']==mid for r in assistance)<=2 for mid in CONTRACT['investments']))
 check(name+' only the two authored facilities can charge repair',all(r['mission'] in CONTRACT['investments'] and r['supplies']==2 and r['projects']==1 for r in s['receipts'] if r['kind']=='equipment_restored'))
 check(name+' acquired advanced-action bundles match real training receipts',all(any(t['kind']=='training' and t['actors']==r['actors'] and t['day']==r['day'] for t in s['receipts']) for r in s['receipts'] if r['kind']=='coordination_bundle'))
W={r['witness_name']:r for r in json.loads((O/'player-choice-witnesses.json').read_text())}
check('relay still retains an additional archive in full-map comparison',W['relay']['success'] and W['ordinary_handoff']['success'] and 'asset' in W['relay']['secured'] and 'asset' not in W['ordinary_handoff']['secured'])
check('pull full map survives retirement of artificial holding task',W['pull_without_added_wait']['success'] and 'live_service' not in W['pull_without_added_wait']['secured'] and W['pull_without_added_wait']['machinery_intact'])
check('M22 ordinary full objective route is retained',W['M22_ordinary_no_added_wait']['success'] and {'e','privacy','handover'}<=set(W['M22_ordinary_no_added_wait']['secured']))
from guidance import Guidance
for r in W.values():
 g=Guidance();g.scene(B[r['mission']],r['log']);check(r['witness_name']+' hint budget remains one',sum(x['kind']=='nonmodal_card' for x in g.log)<=1)
runtime={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and f.suffix in ['.gd','.tscn','.godot'] and '.godot' not in f.parts}
check('production runtime unchanged',runtime==json.loads((ROOT/'work/tactical-review/runtime-before.json').read_text()))
(O/'player-choice-checks.json').write_text(json.dumps(dict(version='0.11',passed_count=len(checks),checks=checks,baseline_contexts=baseline,runtime_unchanged=True,scope='Boundary fixtures and full reference replays. No human fun, readability or preference claim.'),ensure_ascii=False,indent=2)+'\n');print('0.11 player-choice checks:',len(checks))
