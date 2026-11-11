"""Focused reference-rule assertions and evidence checks. No product runtime execution."""
from relationships import *
import hashlib
checks=[]
def check(n,v):
 assert v,n
 checks.append(n)
def rejects(fn):
 try:fn();return False
 except AssertionError:return True
def fixture(actor,level=5):
 b=deepcopy(B['M01']);b.update(rows=['........']*8,spawns=[[2,4],[3,4],[1,4]],exits=[[0,4]],enemies=[],controls=[],objectives=[dict(id='task',kind='work',cell=[2,3],work=4,hp=6,prerequisites=[],interaction_tags=['engineering'],power_off=True),dict(id='r1',kind='rescue',cell=[2,3],work=0,hp=4,prerequisites=[],initial_stable=False,stabilize_deadline={'mode':'none'})])
 p=[actor]+[a for a in ['lin','xu','su'] if a!=actor][:2]
 g=IdentityBattle(b,['task'],p,{a:level for a in p},skills=True);g.rnd=1
 g.e['unit']=dict(id='unit',type='scout',p=(2,2),hp=3,disabled=False,disable_requires=[],skip=0,intent=[],step=(0,1),rail=None)
 return g

g=fixture('su');before=sum(h['ap'] for h in g.h);g.use(0,'su_3',1)
check('AP transfer conserves team total and receiver can reach3',sum(h['ap'] for h in g.h)==before and g.h[1]['ap']==3 and g.h[0]['ap']==1)
check('Same recipient cannot receive again this round',rejects(lambda:g.use(0,'su_3',1)))
check('Cannot give AP to self',rejects(lambda:g.use(0,'su_3',0)))
g=fixture('su');g.h[1]['down']=True;check('Cannot reactivate downed teammate',rejects(lambda:g.use(0,'su_3',1)))
g=fixture('su');g.h[0]['carry']='r1';check('Carrier cannot operate command',rejects(lambda:g.use(0,'su_3',1)))
g=fixture('su');g.use(0,'su_3',1,destination='movement');check('L5 retains old movement alternative',g.h[1]['move_bonus']==1 and g.h[1]['ap']==2)
g.rnd+=1;g.h[0]['ap']=2;g.use(0,'su_3',1);g.h[0]['ap']=2
check('Modes share two-use limit',rejects(lambda:g.use(0,'su_3',2)))
g=fixture('lin');g.objects['r1']['p']=(2,1);g.use(0,'lin_1','r1');check('L5 medical stabilization works at3 cells',g.objects['r1']['stable'] and g.h[0]['ap']==1)
g=fixture('lin',3);g.objects['r1']['p']=(2,1);check('L3 does not silently acquire L5 range',rejects(lambda:g.use(0,'lin_1','r1')))
g=fixture('xu');g.h[1]['p']=(3,5);g.rows[4][3]='X';g.h[0]['carry']='r1';g.objects['r1']['carrier']=0;g.use(0,'xu_1',destination=(4,4))
check('L5 rope transports one casualty without leaving free anchors',g.h[0]['p']==(4,4) and g.h[0]['carry']=='r1' and not g.anchors)
g=fixture('xu',3);g.h[1]['p']=(3,5);g.rows[4][3]='X';g.h[0]['carry']='r1';check('L3 carrying still requires real equipment anchor',rejects(lambda:g.use(0,'xu_1',destination=(4,4))))
g=fixture('chen');g.use(0,'chen_3','task');check('L5 shield is6 and not unlimited stacking',g.objects['task']['shield']==6 and rejects(lambda:g.use(0,'chen_3','task')))
g=fixture('he');g.use(0,'he_1',destination=(2,5));check('L5 screen persists but still has3HP',g.barriers[(2,5)]['expires']==999 and g.barriers[(2,5)]['hp']==3)
g=fixture('ye');g.use(0,'ye_3',destination=(2,3));check('L5 insulation covers3 cells',g.insulated=={(2,3),(2,2),(2,1)})
g=fixture('ye');g.rows[2][2]='#';check('Insulation cannot extend through intermediate wall',rejects(lambda:g.use(0,'ye_3',destination=(2,3))) and not g.insulated)
g=fixture('mo');g.control_ids.add('task');g.objects['task'].update(work=3,disables='unit');g.use(0,'mo_1','task');check('L5 remote work gives exactly2 and respects incomplete goal',g.objects['task']['progress']==2 and not g.objects['task']['done'])
g=fixture('mo');check('Remote specialization cannot replace main task or evidence',rejects(lambda:g.use(0,'mo_1','task')))
g=fixture('jiang');g.h[1]['p']=(4,4);g.h[0]['carry']='r1';g.objects['r1']['carrier']=0;g.use(0,'jiang_1',1)
check('Two-cell handoff changes carrier without auto extraction',g.h[0]['carry'] is None and g.h[1]['carry']=='r1' and not g.objects['r1']['secured'] and g.h[1]['ap']==2)
g=fixture('jiang');g.h[1]['p']=(4,4);g.h[0]['carry']='r1';g.rows[4][3]='#';check('Two-cell handoff cannot cross wall',rejects(lambda:g.use(0,'jiang_1',1)))
g=fixture('ye');g.h[0]['p']=(2,3);g.pending=[dict(source='unit')];g.fire={(4,4)};g.use(0,'ye_1','unit')
check('Isolation stops danger without destroying machine or erasing existing effects',not g.working(g.e['unit']) and g.e['unit']['hp']==3 and not g.e['unit']['disabled'] and g.pending==[dict(source='unit')] and g.fire=={(4,4)} and g.h[0]['ap']==0)
g.h[0]['ap']=2;check('Isolation cannot be repeated',rejects(lambda:g.use(0,'ye_1','unit')))
# Constructed ledger fixtures test rules; full earned-state campaigns checked below.
def ledger(node='R01'):
 g=RelationshipLedger('fixture',external_social=True);g.day=20;g.phase='camp';g.resources['supplies']=20
 for a in g.crew:g.crew[a].update(joined=True,xp=20,fatigue=0,stress=0)
 for r in g.rel.values():r.update(grudge=0,trust=30,memories=[])
 pair=NODES[node]['actors'];g.scene(node,'agreement')
 for mid in ['M01','M02']:
  g.settled.add(mid);g.receipt('objective_completed',mission=mid,contributors=pair)
 return g,pair

g,pair=ledger();m,l=pair;g.crew[m]['xp']=40;before=deepcopy(g.rel);g.mentor(m,l)
check('Mentorship has real project, supply and fatigue costs',g.projects==1 and g.resources['supplies']==18 and all(g.crew[a]['fatigue']==8 for a in pair))
check('Mentor gains no XP and no relationship farming reward',g.crew[m]['xp']==40 and g.crew[l]['xp']==26 and g.rel==before)
g.day+=1;g.projects=0;g.used=set();check('Chapter learner cap survives another evening',not any(x[1]==l for x in g.mentor_candidates()))
g,pair=ledger();m,l=pair;g.crew[m]['xp']=99;g.crew[l]['xp']=95;g.mentor(m,l);check('Learner never overtakes teacher',g.crew[l]['xp']==99)
g,pair=ledger();m,l=pair;g.crew[m]['xp']=120;g.crew[l]['xp']=98;check('Near-cap learner gets ordinary training instead',not any(x[1]==l for x in g.mentor_candidates()));g.train([l]);check('Paid XP stops at100',g.crew[l]['xp']==100)
g.day+=1;g.projects=0;g.used=set();check('No payment for fully trained learner',rejects(lambda:g.train([l])))
g,pair=ledger();g.records=[r for r in g.records if r.get('mission')!='M02'];check('One real mission is insufficient',not g.pact_for(pair))
g,pair=ledger();g.receipt('promise_breach',mission='M01');check('Manufactured betrayal does not count as cooperation history',not g.pact_for(pair))
g,pair=ledger();g.pacts['R01']='distance';check('Professional distance disables pact without forcing basic restriction',not g.pact_for(pair) and g.eligible(pair[0]))
g,pair=ledger('R04');g.phase='briefing';party=['su','lin','xu'];plans=g.dispatch_options(party);check('Earned pair can split field and existing support seat',bool(plans));g.dispatch=plans[0];support=g.dispatch['support'];xp=g.crew[support]['xp'];g.deploy('M20',party)
check('Dispatch consumes2 once and ordinary support8fatigue',g.resources['supplies']==18 and g.crew[support]['fatigue']==8)
g.settle(dict(mission='M20',completed=[],secured=[],all_extracted=True));check('Dispatch forgoes normal supply but retains support2XP even after failure',g.resources['supplies']==18 and g.crew[support]['xp']==xp+2 and g.dispatch is None)
before=deepcopy(g.__dict__);check('Settled mission cannot pay or reward twice',rejects(lambda:g.settle(dict(mission='M20',completed=[],secured=[]))) and g.__dict__==before)
g,pair=ledger('R04');g.phase='briefing';g.resources['supplies']=1;check('Low budget offers free default rather than unpaid dispatch',not g.dispatch_options(['su','lin','xu']))
g,pair=ledger('R04');g.phase='after_main';check('Side mission cannot consume main dispatch',not g.dispatch_options(['su','lin','xu']))
g,pair=ledger('R04');g.phase='briefing';g.dispatch=g.dispatch_options(['su','lin','xu'])[0];before=deepcopy(g.__dict__);check('Invalid deployment rolls back new dispatch payment too',rejects(lambda:g.deploy('M19',['su','lin','xu'])) and g.__dict__==before)
g,pair=ledger('R04');g.phase='briefing';g.crew['jiang']['withdrawn']=True;check('Absent support cannot be assigned',not g.dispatch_options(['su','lin','xu']))
g=IdentityBattle(B['M06'],['r1','r2'],['lin','xu','su'],{a:3 for a in ['lin','xu','su']},trust={(a,b):0 for a in ['lin','xu','su'] for b in ['lin','xu','su'] if a!=b})
check('Basic cooperation remains possible without affection gate',g.protocol_ready('relay_carry',0,2));g.relations[('su','lin')]=True;check('Concrete conflict still requires real agreement',not g.protocol_ready('relay_carry',0,2));g.agree('relay_carry',0,2);check('Specific agreement restores only named action',g.protocol_ready('relay_carry',0,2))
m=json.loads((ROOT/'outputs/growth-identity-matrix.json').read_text());check('1432 date-valid contexts keep ordinary primary solutions',len(m['rows'])==1432 and all(x['states']['L1_basic']['success'] for x in m['rows']));check('All36 missions are covered',len(m['maps'])==36)
f=json.loads((ROOT/'outputs/growth-identity-field.json').read_text());check('All126 date-valid field trios have sampled service solution',len(f['rows'])==126 and all(r['service'] and r['best']['success'] for r in f['rows']))
p=json.loads((ROOT/'outputs/growth-identity-ports.json').read_text());check('Both physical exit geometries retain92 goal solutions',len(p['rows'])==92 and all(x['success'] for x in p['rows']))
cs=json.loads((ROOT/'outputs/growth-identity-campaigns.json').read_text())
for s in cs['scenarios']:
 q=s['summary'];check(q['name']+' completes24main with nonnegative resources',q['main_count']==24 and all(v>=0 for v in q['resources'].values()))
 check(q['name']+' has no retired equipment or pair-learning currency',not set(q['tools'])&set(SCOPE['retired_equipment']) and not q['trained_protocols'])
check('Three chosen ending routes survive integrated runs',{'shared_control','distributed_rebuild','evacuation'}<={s['summary']['world_ending'] for s in cs['scenarios']})
check('Highest difficulty failures really caused permanent withdrawal',bool(cs['scenarios'][-1]['summary']['withdrawn']))
check('Normal campaigns have no permanent losses',all(not s['summary']['withdrawn'] for s in cs['scenarios'][:-1]))
before=json.loads((ROOT/'work/growth-identity-review/runtime-before.json').read_text());after={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and (f.suffix in ['.gd','.tscn'] or f.name=='project.godot')};check('Production runtime is byte-identical',before==after)
(ROOT/'outputs/growth-identity-checks.json').write_text(json.dumps(dict(version='0.13',passed=len(checks),checks=checks,runtime_unchanged=True,fixture_warning='Hand-built edge states establish rule legality, not earned progression or fun.'),ensure_ascii=False,indent=2)+'\n');print('PASSED',len(checks))
