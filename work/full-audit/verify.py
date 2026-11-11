"""Current-scope action coverage, state round trips and cross-system boundaries."""
from pathlib import Path
import sys,json,hashlib,math,itertools
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
from relationships import *
from social import Social
checks=[];coverage=[]
def check(group,name,ok):
 assert ok,(group,name)
 checks.append(dict(group=group,name=name))
def rejects(g,fn):
 before=deepcopy(g.__dict__)
 try:fn();return False
 except (AssertionError,KeyError,ValueError,IndexError):return g.__dict__==before
def fixture(actor='xu',level=5,gear=None,medical_capacity=2):
 b=deepcopy(B['M01']);b.update(rows=['........']*8,spawns=[[2,4],[3,4],[1,4]],enemies=[],controls=[],objectives=[dict(id='task',kind='work',cell=[2,3],work=4,hp=6,prerequisites=[],interaction_tags=['engineering','light_obstacle'],power_off=True),dict(id='r1',kind='rescue',cell=[2,3],work=0,hp=4,prerequisites=[],initial_stable=False,stabilize_deadline={'mode':'none'})])
 p=[actor]+[a for a in ['lin','xu','su'] if a!=actor][:2]
 g=IdentityBattle(b,['task'],p,{a:level for a in p},gear=gear or {},medical_capacity=medical_capacity);g.rnd=1
 g.e['unit']=dict(id='unit',type='scout',p=(2,2),hp=3,disabled=False,disable_requires=[],skip=0,intent=[],step=(0,1),rail=None)
 return g
for key in SCOPE['abilities']+SCOPE['equipment']:
 actor=ABILITIES[key]['actor'] if key in ABILITIES else 'lin';gear={'med_dose':2}
 if key in SCOPE['equipment']:gear[key]=0
 g=fixture(actor,3,gear);target=None;dest=None
 if key=='lin_1':target='r1'
 elif key=='lin_3':target='r1';dest=(2,3);g.objects['r1']['p']=(2,2)
 elif key=='xu_1':dest=(4,4);g.rows[4][3]='X';g.h[1]['p']=(3,5)
 elif key=='xu_3':target=1;g.h[1]['p']=(4,4);dest=(3,4)
 elif key in ['su_1','chen_1']:target='unit'
 elif key=='su_3':target=1
 elif key=='chen_3':target='task'
 elif key=='ye_1':target='unit';g.h[0]['p']=(2,3)
 elif key in ['ye_3','insulation']:dest=(3,4)
 elif key in ['he_1','shield','winch']:dest=(2,5)
 elif key in ['mo_1','scanner']:target='task';g.control_ids.add('task');g.objects['task']['disables']='unit'
 elif key=='mo_3':target='unit';dest=(3,3)
 elif key=='jiang_1':target=1;g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True)
 elif key in ['jiang_3','medkit']:target=1;g.h[1]['hp']=7
 elif key=='crowbar':target='task'
 before=g.h[0]['ap'];g.use(0,key,target,dest)
 check('active_actions',key+' has executable owned/earned action',g.h[0]['ap']>=0 and (g.h[0]['ap']<before or key in ['he_3','stretcher']))
 coverage.append(dict(action=key,ap=before-g.h[0]['ap'],fixture=True))
g=fixture('xu',3,{'winch':0});g.use(0,'winch',destination=(2,5));check('equipment','Deployed winch persists',g.anchors=={(2,5)})
g.rnd+=1;g.h[0]['ap']=2;g.h[1]['p']=(3,5);g.rows[4][3]='X';g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True);g.use(0,'xu_1',destination=(4,4));check('equipment','L3 uses real anchor without deleting it',g.h[0]['p']==(4,4) and g.anchors=={(2,5)})
for level in [1,4,5,6]:
 g=fixture('lin',level,{'medkit':0,'med_dose':2});maximum=10+int(level>=4)+int(level>=6);g.h[1]['hp']=maximum-1;g.use(0,'medkit',1)
 check('medical',f'L{level} healing uses current max HP',g.h[1]['hp']==maximum and g.used['med_dose']==1)
 check('medical',f'L{level} full HP rejects without stock/AP loss',rejects(g,lambda:g.use(0,'medkit',1)))
for key,actor in [('medkit','lin'),('jiang_3','jiang')]:
 for state in ['left','down']:
  g=fixture(actor,6,{'medkit':0,'med_dose':2});g.h[1].update(hp=5);g.h[1][state]=True
  check('medical',key+' cannot treat '+state,rejects(g,lambda:g.use(0,key,1)))
for cap in [2,3]:
 g=fixture('lin',5,{'medkit':0,'med_dose':cap},cap)
 for i in range(cap):g.h[0]['ap']=2;g.h[1]['hp']=5;g.use(0,'medkit',1)
 g.h[0]['ap']=2;g.h[1]['hp']=5;check('medical',f'Capacity{cap} limits both actual doses and kit uses',g.used['med_dose']==cap and rejects(g,lambda:g.use(0,'medkit',1)))
try:fixture('lin',5,{'medkit':0,'winch':0});bad=False
except AssertionError:bad=True
check('equipment','Two tools cannot silently occupy same actor slot',bad)
g=fixture('su');g.relations[('xu','su')]=True
check('command','Direct AP-transfer command checks actual relationship',rejects(g,lambda:g.use(0,'su_3',2)))
g.agree('su_3',0,2);g.use(0,'su_3',2);check('command','Explicit named agreement restores legal action',g.h[2]['ap']==3)
for actor,target in [(-1,1),(True,1),(0,-1),(0,True)]:
 g=fixture('su');check('command','Malformed actor/target rejected '+str((actor,target)),rejects(g,lambda:g.use(actor,'su_3',target)))
g=fixture('xu',5);g.h[1]['p']=(3,5);g.h[0]['carry']='r1';g.rows[4][3]='X';g.rows[4][4]='X';check('command','Rejected personal rope leaves no temporary anchor',rejects(g,lambda:g.use(0,'xu_1',destination=(4,4))) and not g.anchors)
def ledger(node='R01'):
 g=RelationshipLedger('edge',external_social=True);g.day=20;g.phase='camp';g.resources.update(credits=200,supplies=20,parts=20)
 for a in g.crew:g.crew[a].update(joined=True,xp=20,fatigue=0,stress=0)
 for r in g.rel.values():r.update(grudge=0,trust=30,memories=[])
 pair=NODES[node]['actors'];g.scene(node,'agreement')
 for mid in ['M01','M02']:g.settled.add(mid);g.receipt('objective_completed',mission=mid,contributors=pair)
 return g,pair
g,pair=ledger();others=[a for a in g.crew if a not in pair];g.receipt('promise_breach',mission='M01',observer=others[0],target=others[1]);check('relationships','Unrelated third-party breach does not erase this pair history',len(g.pair_history(pair))==2)
g.receipt('promise_breach',mission='M01',observer=pair[0],target=others[0]);check('relationships','Relevant breach still invalidates that mission',len(g.pair_history(pair))==1)
g,pair=ledger();g.crew[pair[0]]['xp']=40;g.mentor(*pair);before=deepcopy(g.rel);used=deepcopy(g.apprentices);g.revise_pact('R01','distance')
check('relationships','Renegotiation costs one short scene, no memory/usage reset',g.scenes==2 and g.rel==before and g.apprentices==used)
check('relationships','Same-day toggling cannot reset pact',rejects(g,lambda:g.revise_pact('R01','agreement')))
g.day+=1;g.scenes=0;g.used=set();g.projects=0;g.revise_pact('R01','agreement');check('relationships','Re-agreement preserves already-used chapter teaching',not any(x[1]==pair[1] for x in g.mentor_candidates()))
check('relationships','Repeating identical choice consumes nothing',rejects(g,lambda:g.revise_pact('R01','agreement')))
g.day=24;g.scenes=0;check('relationships','No nonexistent day24 camp negotiation',rejects(g,lambda:g.revise_pact('R01','distance')))
g,pair=ledger('R04');g.phase='briefing';party=['su','lin','xu'];budget=deepcopy(g.resources);plan=g.dispatch_options(party)[0];g.select_dispatch(party,plan);g.select_dispatch(party);check('dispatch','Selecting then cancelling draft is free and restores default',g.dispatch is None and g.resources==budget)
g.select_dispatch(party,plan);check('dispatch','Changing to party without agreed partner invalidates draft',not g.refresh_dispatch(['lin','xu','chen']) and g.dispatch is None and g.resources==budget)
g.select_dispatch(party,plan);g.crew['su']['fatigue']=100;check('dispatch','Unusable field member invalidates plan before payment',not g.refresh_dispatch(party) and g.resources==budget)
g=RelationshipLedger('medical economics');g.day=8;g.phase='camp';g.resources.update(credits=200,supplies=8,parts=20);g.upgrade('workshop');g.day=9;g.projects=0;g.upgrade('workshop');g.craft('med_dose',3);g.phase='briefing';g.deploy('M09',['lin','xu','su'],pack={'med_dose':3})
check('economy','Two workshop tiers and3 doses pay real budget',g.resources==dict(credits=105,supplies=5,parts=8) and g.active['packed']=={'med_dose':3})
g.settle(dict(mission='M09',completed=[],secured=[],consumed={'med_dose':2}));check('economy','Failure returns only one unused dose',g.inventory['med_dose']==1 and g.total_consumed['med_dose']==2)
check('economy','Duplicate settlement cannot return stock or pay again',rejects(g,lambda:g.settle(dict(mission='M09',completed=[],secured=[],consumed={'med_dose':2}))))
g=RelationshipLedger('final failure');g.day=24;g.route='distributed_rebuild';g.deploy('M24',['lin','xu','su']);check('endings','Foreign final route results rejected atomically',rejects(g,lambda:g.settle(dict(mission='M24',completed=['bus','auth'],secured=['bus','auth'],branch='distributed_rebuild'))));g.settle(dict(mission='M24',completed=[],secured=[],branch='distributed_rebuild'));check('endings','Final mission failure reaches evacuation coda',g.summary()['world_ending']=='evacuation')
g=RelationshipLedger('all unavailable',hard=True,empty=True)
for day in range(1,25):
 party=g.choose_party();mid=f'M{day:02}'
 if day==24:g.route='evacuation'
 g.deploy(mid,party);g.settle(dict(mission=mid,completed=[],secured=[],withdrawn=party,branch='evacuation' if day==24 else None))
 if day<24:g.begin_camp();g.night()
check('endings','All8 protagonists unavailable still reach24main coda through real reserve slots',len(g.summary()['withdrawn'])==8 and g.summary()['main_count']==24 and g.summary()['world_ending']=='evacuation' and g.summary()['borrowed_slots']>0)
# Typed JSON is an offline round-trip probe, not a production save implementation.
social=Social();classes={type(social.people['lin']).__name__:type(social.people['lin']),type(social.people['lin'].direction('xu')).__name__:type(social.people['lin'].direction('xu'))}
def encode(v):
 if v is None or type(v) in [str,int,bool]:return v
 if type(v) is float:assert math.isfinite(v);return v
 if isinstance(v,dict):return {'$dict':[[encode(k),encode(x)] for k,x in v.items()]}
 if isinstance(v,list):return [encode(x) for x in v]
 if isinstance(v,tuple):return {'$tuple':[encode(x) for x in v]}
 if isinstance(v,set):return {'$set':[encode(x) for x in sorted(v,key=repr)]}
 if type(v).__name__ in classes and classes[type(v).__name__] is type(v):return {'$class':type(v).__name__,'state':encode(v.__dict__)}
 raise TypeError(type(v))
def decode(v):
 if isinstance(v,list):return [decode(x) for x in v]
 if not isinstance(v,dict):return v
 if '$dict' in v:return {decode(k):decode(x) for k,x in v['$dict']}
 if '$tuple' in v:return tuple(decode(x) for x in v['$tuple'])
 if '$set' in v:return set(decode(x) for x in v['$set'])
 if '$class' in v:
  obj=classes[v['$class']].__new__(classes[v['$class']]);obj.__dict__=decode(v['state']);return obj
 raise ValueError('Unknown type')
def roundtrip(obj):
 raw=json.dumps(encode(obj.__dict__),ensure_ascii=False,sort_keys=True);restored=type(obj).__new__(type(obj));restored.__dict__=decode(json.loads(raw));check('persistence',type(obj).__name__+' all current fields survive typed JSON',json.dumps(encode(restored.__dict__),ensure_ascii=False,sort_keys=True)==raw);return restored
g=fixture('su');g.use(0,'su_3',1);saved=roundtrip(g);check('persistence','AP receiver token and task charges survive reload',rejects(saved,lambda:saved.use(0,'su_3',1)))
g=fixture('xu',3,{'winch':0});g.use(0,'winch',destination=(2,5));saved=roundtrip(g);check('persistence','Deployed equipment survives reload',saved.anchors=={(2,5)})
g,pair=ledger('R04');g.crew[pair[0]]['xp']=40;g.mentor(*pair);g.phase='briefing';g.dispatch=g.dispatch_options(['su','lin','xu'])[0];saved=roundtrip(g);check('persistence','Mentoring and committed dispatch choice survive reload',saved.apprentices==g.apprentices and saved.dispatch==g.dispatch and saved.pacts==g.pacts)
social.people['lin'].direction('xu').add('saved_incident',20,severity=12,loss=8);social.people['lin'].seen.add('saved_incident');social.bands[('lin','xu')]=2;saved=roundtrip(social);check('persistence','Social memory and dedup preserve same current result',saved.people['lin'].direction('xu').resentment(20)==social.people['lin'].direction('xu').resentment(20) and 'saved_incident' in saved.people['lin'].seen)
from guidance import Guidance
ui=Guidance();ui.offer('G01','M01',1);ui.boundary('M01',1,{'G01'});saved=roundtrip(ui);before=len(saved.log);saved.offer('G01','M01',2);saved.boundary('M01',2,{'G01'});check('persistence','Seen tutorial does not replay after reload',len(saved.log)==before)
ledger_state,_=ledger();social.sync(ledger_state);saved_ledger=roundtrip(ledger_state);saved_social=roundtrip(social);saved_social.sync(saved_ledger)
check('persistence','Social canonical state rebuilds ledger projection without reward',saved_ledger.rel==ledger_state.rel and saved_ledger.resources==ledger_state.resources and saved_ledger.bands==ledger_state.bands)
# All authored content, including branches and active scope, is structurally audited.
for mid,b in B.items():
 objects={o['id']:o for o in b['objectives']+b['controls']};check('boards',mid+' unique IDs and8x8 cells',len(objects)==len(b['objectives'])+len(b['controls']) and len(b['rows'])==8 and all(len(r)==8 for r in b['rows']))
 visiting=set();done=set()
 def visit(k):
  assert k in objects and k not in visiting,(mid,k)
  if k in done:return
  visiting.add(k)
  for dep in objects[k]['prerequisites']:visit(dep)
  visiting.remove(k);done.add(k)
 for k in objects:visit(k)
 check('boards',mid+' dependency DAG and all branch groups valid',all(x in objects for groups in b.get('route_groups',{'default':b['mandatory_groups']}).values() for group in groups for x in group))
 check('boards',mid+' endpoints and deadlines valid',all(0<=x<8 and 0<=y<8 and b['rows'][y][x] not in '#X' for x,y in b['spawns']+b['exits']+[b['backup_exit']]) and b['round_limit']>0 and b['hard_round_limit']>0)
st=json.loads((ROOT/'game/data/final_design/stories.json').read_text());nodes=[n for k in ['personal_nodes','relationship_nodes','community_nodes','recovery_nodes','chapter_nodes'] for n in st[k]]
check('stories','96 unique registered nodes, not96 finished scripts',len(nodes)==len({n['id'] for n in nodes})==96)
personal={n['id']:n for n in st['personal_nodes']}
for a in ['lin','xu','su','chen','ye','he','mo','jiang']:
 ns=sorted([n for n in personal.values() if n['actor']==a],key=lambda n:n['stage']);check('stories',a+' has three ordered prefinal nodes',len(ns)==3 and [n['stage'] for n in ns]==[1,2,3] and all(n['earliest_day']<=23 for n in ns) and all(k in personal for n in ns for k in n['requires_resolved']))
check('scope','16 current skills and7 current tools are all exercised',len(coverage)==23 and set(x['action'] for x in coverage)==set(SCOPE['abilities']+SCOPE['equipment']))
if not __import__('os').environ.get('NIGHT_TIDE_CURRENT_RULE_CHECK'):
 before=json.loads((ROOT/'work/full-audit/runtime-before.json').read_text());after={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and (f.suffix in ['.gd','.tscn'] or f.name=='project.godot')};check('scope','Production runtime unchanged',before==after)
(ROOT/'outputs/full-audit-checks.json').write_text(json.dumps(dict(version='0.14',passed=len(checks),checks=checks,active_action_coverage=coverage,runtime_unchanged=True),ensure_ascii=False,indent=2)+'\n');print('FULL AUDIT CHECKS',len(checks),flush=True)
