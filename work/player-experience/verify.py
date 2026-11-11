"""Behavioral scenarios for0.8, not a claim of novice usability or human psychology."""
from pathlib import Path
from copy import deepcopy
import sys,json,random,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from appraisal import Session,PROFILES,Direction,value,evaluate,tutorial_gate,usable_hints
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';checks=[];examples=[]
def check(n,v):assert v,n;checks.append(n)
def event(**kw):
 e=dict(id='case',mission='M17',day=8,kind='cooperation',outcome='success',known_by=['B','A','C'],witnesses=['B','A','C'],contributors=['B','A'],responsibility={},evidence='verified',voluntary_contribution=True,relevant_category='fairness',extra_cost=0,self_control=.75)
 e.update(kw);return e
def subject(profile='xu',severe=False):
 s=Session('B',PROFILES[profile]);d=Direction(grudge=30,trust=50)
 d.memories=[dict(id='old',day=8,category='fairness',strength=10,raw_strength=10,severe=severe,stage=0,active=True)]
 s.directions['A']=d;return s
for name,e,profile in [
 ('成功，C不在场',event(witnesses=['B','A']),'xu'),
 ('成功，C在场且B在意其评价',event(),'xu'),
 ('成功，但明确违约仍成立',event(kind='breach',responsibility={'A':1},explicit_violation=True),'xu'),
 ('失败，A有明确责任，C在场',event(kind='cost_overrun',outcome='failed',responsibility={'A':1},extra_cost=2),'xu'),
 ('失败，只有疑点，B倾向外归因',event(kind='cost_overrun',outcome='failed',evidence='ambiguous',suspect='A',visible_cue=True,extra_cost=2),'ye'),
 ('同样失败，B更严格自责',event(kind='cost_overrun',outcome='failed',evidence='ambiguous',suspect='A',visible_cue=True,extra_cost=2),'lin'),
 ('坏天气下未完成，没有个人过错',event(kind='cost_overrun',outcome='failed',contributors=[],weather_hazard_experienced=True),'lin')]:
 s=subject(profile);r=s.apply(e,{'C':85});examples.append(dict(name=name,profile=profile,input=e,result=r))
check('reliable success can reduce relevant ordinary irritation',examples[0]['result']['directions']['A']['r_after']<40)
check('audience may add bounded credit with real joint contribution',examples[1]['result']['directions']['A']['trust_after']>examples[0]['result']['directions']['A']['trust_after'])
check('successful breach remains resentment and loses trust',examples[2]['result']['directions']['A']['r_after']>40 and examples[2]['result']['directions']['A']['trust_after']<50)
check('restraint is not forgiveness',examples[3]['result']['directions']['A']['expression']=='public_restraint_private_concern' and examples[3]['result']['directions']['A']['r_after']>40)
check('ambiguous blame does not fabricate guilt',examples[4]['result']['directions']['A']['r_after']==40 and examples[4]['result']['directions']['A']['trust_after']==50)
check('strict self appraisal has higher load for same observed setback',examples[5]['result']['load_delta']>examples[4]['result']['load_delta'])
check('strict self appraisal changes first expressed concern',examples[5]['result']['directions']['A']['expression']=='self_questioning_request_review' and examples[4]['result']['directions']['A']['expression']=='tentative_question_not_accusation')
check('weather with no responsible actor produces no directed blame',not examples[6]['result']['directions'] and examples[6]['result']['stress_delta']>0)
s=subject();r=s.apply(event(contributors=['B']),{'C':100});check('merely bringing likedC produces no relationship credit',not r['directions'] or all(x['actual_trust_gain']==0 for x in r['directions'].values()))
s=subject(severe=True);r=s.apply(event(),{'C':100});check('success cannot erase severe old memory or G',r['directions']['A']['r_after']==40 and s.direction('A').grudge==30)
s=subject();s.direction('A').memories[0]['category']='humiliation';r=s.apply(event(),{'C':100});check('irrelevant good task cannot erase humiliation',r['directions']['A']['r_after']==40)
s=subject();r=s.apply(event(),{'C':85});state=deepcopy(s.__dict__);r2=s.apply(event(),{'C':85});check('repeated root receipt makes no second change',r2.get('duplicate') and s.__dict__==state)
r2=s.apply(event(mission='M18'),{'C':85});check('same root cannot bypass dedup by changing mission',r2.get('duplicate') and s.__dict__==state)
for n in range(10):s.apply(event(id=f'help{n}'),{'C':100})
check('positive credit mission cap is3 per direction',s.direction('A').trust==53)
check('ordinary relief mission cap6 and never returns archive',s.relief_budget[('M17','A')]<=6 and s.direction('A').resentment(8)>=34)
for confirmed in ['breach','unfairness','humiliation','concealment','cost_overrun']:
 a=subject();b=subject();ev=event(kind=confirmed,outcome='failed',responsibility={'A':1})
 a.apply(ev,{'C':0});b.apply(ev,{'C':100})
 check(confirmed+' audience does not discount verified wrongdoing',a.direction('A').resentment(8)==b.direction('A').resentment(8) and a.direction('A').trust==b.direction('A').trust)
for k in ['start','finish']:
 a=subject();b=subject();e1=event(start=1,finish=8);e2=event(start=4,finish=10)
 a.apply(e1);b.apply(e2);check(k+' irrelevant time does not automatically add resentment',a.direction('A').resentment(8)==b.direction('A').resentment(8) and a.stress==b.stress)
a=subject();a.apply(event(start=4,finish=10,start_relevant=True,agreed_start=3,time_relevant=True,agreed_finish=9,kind='breach',responsibility={'A':1},explicit_violation=True));check('late start and finish same breach is one memory',len(a.direction('A').memories)==2)
a=subject();b=subject();a.apply(event(),{'C':85});b.apply(event(witnesses=['A','B','C','D','E'],known_by=['A','B','C','D','E']),{'C':85,'D':85,'E':85})
check('more people cannot multiply social credit or emotion',a.direction('A').resentment(8)==b.direction('A').resentment(8) and a.direction('A').trust==b.direction('A').trust)
a=subject();b=subject();a.apply(event(witnesses=['A','B']),{'C':100});b.apply(event(witnesses=['A','B','C'],known_by=['A','B']),{'C':100})
check('audience lacking information does not count as informed witness',a.direction('A').trust==b.direction('A').trust)
s=subject();s.apply(event(known_by=['A','C'],kind='breach',responsibility={'A':1}),{'C':100});check('unlearned event has no internal or relational penalty',s.direction('A').resentment(8)==40 and s.stress==10 and s.self_load==0)
check('unknown event does not consume later learning token','case' not in s.seen)
s.apply(event(day=9,occurred_day=8,kind='breach',responsibility={'A':1}),{'C':100});check('later learning keeps occurrence separate from memory date',s.direction('A').facts['case']['occurred']==8 and s.direction('A').facts['case']['learned']==9)
s=subject();s.apply(event(outcome='failed',kind='cost_overrun',evidence='ambiguous',visible_cue=True,suspect='A'),{'C':85});load=s.self_load;stress=s.stress
check('pending explanation retained with explicit uncertainty',len(s.pending)==1)
proof=event(day=9,outcome='failed',kind='cost_overrun',responsibility={'A':1})
check('late evidence confirms original event once',s.confirm(proof) and not s.confirm(proof) and 'case' in s.direction('A').facts and not s.pending)
check('late confirmation does not double charge selfload and stress',s.self_load==load and s.stress==stress)
s=subject();s.apply(event(outcome='failed',kind='cost_overrun',evidence='ambiguous',visible_cue=True,suspect='A'));s.confirm(event(day=9,kind='cost_overrun',responsibility={'leader':1}))
check('correction assigns actual leader and not suspected coworker','case' not in s.direction('A').facts and 'case' in s.direction('leader').facts)
s=subject();s.apply(event(outcome='failed',kind='cost_overrun',evidence='ambiguous',visible_cue=True,suspect='A'));t=s.direction('A').trust;s.confirm(event(day=9,kind='cost_overrun',responsibility={}))
check('proven no blame closes suspicion without reward',not s.pending and s.direction('A').trust==t)
s=subject('lin')
for n in range(8):s.apply(event(id=f'bad{n}',outcome='failed',kind='cost_overrun',extra_cost=3,self_control=1,contributors=[]))
check('all directions share single personal load and stress caps',s.self_load<=8 and s.stress<=22)
s.self_load=75;s.update_band();check('self burden can request support without basic action loss',s.self_band==2 and all(not r['basic_actions_changed'] for r in s.receipts))
s.night(8,recovery_project=True,meaningful_support=True);check('existing recovery and support reduce load by8',s.self_load==67)
v=s.self_load;s.night(8,True,True);check('same night cannot farm recovery',s.self_load==v)
for day in range(9,16):s.night(day,True,True)
check('self burden has reachable exit and is not a diagnostic label',s.self_load<30 and s.self_band==0)
s=subject();before=deepcopy(s.__dict__)
try:s.apply(event(kind='breach',responsibility={'A':.8,'leader':.8}))
except AssertionError:pass
check('invalid responsibility transaction rolls back all state',s.__dict__==before)

# Property sampling combines traits, evidence, audience, weather and event families.
rng=random.Random(20261102)
for n in range(1200):
 p=rng.choice(list(PROFILES));s=subject(p);ev=event(id=f'r{n}',kind=rng.choice(list(['cooperation','breach','unfairness','concealment','cost_overrun'])),outcome=rng.choice(['success','partial','failed']),evidence=rng.choice(['verified','ambiguous']),extra_cost=rng.randrange(4),self_control=rng.random(),weather_hazard_experienced=bool(n%2),responsibility={'A':.5,'leader':.5},suspect='A',visible_cue=True)
 s.apply(ev,{'C':rng.randrange(101)});snap=deepcopy(s.__dict__);s.apply(ev,{'C':99})
 assert snap==s.__dict__ and 0<=s.self_load<=8 and 0<=s.stress<=22
 assert all(0<=d.resentment(8)<=100 and 0<=d.trust<=100 for d in s.directions.values())
check('1200fixedseed contexts preserve bounded causal state',True)

matrix=json.loads((O/'tactical-matrix-results.json').read_text());m01=[x for x in matrix['strategy_runs'] if x['mission']=='M01']
for r in m01:
 check('M01tutorial accepts '+r['difficulty']+r['variant']+r['style'],all(tutorial_gate(r['secured'],goal,r['style']) for goal in r['goals']))
check('skipping help does not require solving an invented exercise',tutorial_gate([], 'r1','anything',True))
check('unsecured cargo cannot satisfy rescue tutorial',not tutorial_gate([], 'r1','pickup'))
check('hints filter unavailable or stale actions',usable_hints([dict(id='lockedskill',legal=False,state_version=1),dict(id='oldtarget',legal=True,state_version=0),dict(id='walk',legal=True,state_version=1)],1)==[dict(id='walk',legal=True,state_version=1)])
contract=json.loads((ROOT/'game/data/final_design/player_experience_contract.json').read_text())
check('all8cast have individual visual and appraisal briefs',len(contract['actors'])==8 and len({x['id'] for x in contract['actors']})==8)
check('guide entries have alternatives and dismissal',len(contract['guides'])==15 and all(g['alternatives'] and g['dismiss'] for g in contract['guides']))
# Attach the new appraisal to two real whole-map results, with an explicitly
# stipulated voluntary return promise. This does not replace the map deadline.
sys.path.insert(0,str(ROOT/'work/tactical-review'))
from encounter import Encounter
board=next(b for b in json.loads((ROOT/'game/data/final_design/boards.json').read_text())['boards'] if b['id']=='M06')
context_cases=[]
for style in ['attack','optional_first']:
 battle=Encounter(board,['r1','r2'],style=style,extra={'asset'});result=battle.run();assert result['success']
 cast=['lin','xu','su'];contributions=set()
 for oid in result['secured']:
  if oid in battle.objects:
   contributions.update(cast[c['actor']] for c in battle.objects[oid]['contributions'])
 late=result['rounds']>7
 ev=event(id='M06-voluntary-return',mission='M06',day=6,kind='breach' if late else 'cooperation',outcome='success',known_by=cast+['leader'],witnesses=cast,contributors=sorted(contributions),responsibility={'leader':1} if late else {},explicit_violation=late,time_relevant=True,finish=result['rounds'],agreed_finish=7,promise='voluntary-return-by7',warned=True,deliberate=late,extra_cost=min(3,result['damage']//2))
 observer=Session('lin');outcome=observer.apply(ev,{'su':85})
 context_cases.append(dict(style=style,rounds=result['rounds'],damage=result['damage'],secured=result['secured'],promise='第7轮末前返回：为对照明确设定的自愿承诺，不是原关卡的强制限时',appraisal=outcome,log=result['log']))
check('M06actual alternatives preserve different optional outcomes','asset' not in context_cases[0]['secured'] and 'asset' in context_cases[1]['secured'])
check('actual risky decision attributes breach to commander not carrier',context_cases[1]['appraisal']['directions']['leader']['confirmed'] and not context_cases[1]['appraisal']['directions'].get('xu',{}).get('confirmed',False))
check('actual safe alternative does not invent broken promise',all(not v['confirmed'] for v in context_cases[0]['appraisal']['directions'].values()))
runtime={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and f.suffix in ['.gd','.tscn','.godot'] and '.godot' not in f.parts}
check('runtime remains untouched',runtime==json.loads((ROOT/'work/tactical-review/runtime-before.json').read_text()))
out={'version':'0.8-player-experience','passed_count':len(checks),'checks':checks,'property_sample_count':1200,'m01_strategy_configurations':len(m01),'examples':examples,'tactical_context_cases':context_cases,'scope':'Offline evaluation adapter and guide-contract checks. M01 acceptance uses existing actual tactical results; twoM06full-map runs feed appraisal under an explicitly stipulated voluntary promise. Does not test a real tutorial interface, generated artwork, clinical psychology, all36maps with new appraisal or human enjoyment.','runtime_unchanged':True}
(O/'player-experience-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Experience checks:',len(checks),'passed;1200context samples;24M01strategy configurations.')
