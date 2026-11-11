"""Adversarial design probes, information scheduling and counterfactual rewards."""
from pathlib import Path
from copy import deepcopy
from dataclasses import asdict
import sys,json,runpy,contextlib,io,hashlib
from social import Social,qualified,close_inquiry,Session,Direction
from guidance import Guidance
from party import Party
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design';checks=[];examples=[]
def check(n,v):assert v,n;checks.append(n)
def rejected(fn):
 try:fn();return False
 except (AssertionError,KeyError):return True
def state(x):
 if isinstance(x,dict):return {k:state(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return tuple(state(v) for v in x)
 if hasattr(x,'__dict__'):return state(x.__dict__)
 return x
def compact(s,day=8):return dict(trust=s.trust,resentment=s.resentment(day),facts=len(s.facts))
B={b['id']:b for b in json.loads((D/'boards.json').read_text())['boards']}
g=Party(B['M01'],['r1','r2'],['lin','xu','su'],skills=False,style='controls');r=g.run();social=Social();social.settle(g,r,g.party,1);before=deepcopy(social.__dict__)
check('same mission cannot mint a second relationship settlement',social.settle(g,{**r,'external_event_id':'different-label'},g.party,1).get('duplicate') and state(before)==state(social.__dict__))
for oid in ['r1','r2']:
 duplicate=deepcopy(g)
 duplicate.objects[oid]['contributions']*=20
 check('duplicated action receipts do not multiply contributors '+oid,qualified(duplicate,r,oid,g.party)==qualified(g,r,oid,g.party))
 bad=deepcopy(g);bad.objects[oid]['secured']=False;bad.objects[oid]['lost']=True;s=Social();start=deepcopy(s.__dict__)
 check('unsecured or lost goal cannot claim completion '+oid,rejected(lambda:s.settle(bad,r,bad.party,1)) and state(s.__dict__)==state(start))
fake=deepcopy(g);oid='r1';fake.objects[oid]['contributions']=[dict(actor=0,action='stabilize',round=1),dict(actor=1,action='pickup',round=2),dict(actor=2,action='pickup',round=2),dict(actor=2,action='chen_3',round=20)]
fr={**r,'log':[]};check('touch transfer and post-completion buff are not useful transport',qualified(fake,fr,oid,fake.party)==['lin'])
# Taking a crate out and back cannot give each carrier fresh progress credit.
origin=tuple(fake.objects[oid]['cell']);near=(origin[0],origin[1]+1);far=(origin[0]+1,origin[1]+1)
fr['log']=[dict(action='move',actor=1,cargo=oid,at=far,path=[origin,near,far]),dict(action='move',actor=2,cargo=oid,at=origin,path=[far,near,origin])]
check('out and back transport earns no new cooperation credit','su' not in qualified(fake,fr,oid,fake.party))

detour={**r,'log':[dict(action='move',actor=1,cargo=oid,at=far,path=[origin,near,far])]}
check('useful non-straight transport path can earn actual contribution','xu' in qualified(fake,detour,oid,fake.party))
causal=Social();causal.settle(g,r,g.party,1,dict(id='harm-and-return',deadline=0,warned=True,accepted=True,caused_object='r1'))
check('same-source caused loss does not issue new cooperation credit',not any(claim[1]=='r1' for claim in causal.claims))

# Registered ambiguous event: proving it false earns zero positive credit.
s=Session('lin');ev=dict(id='M08:decision:test',mission='M08',day=8,kind='cost_overrun',outcome='failed',known_by=['lin','xu','su'],witnesses=['lin','xu','su'],contributors=[],responsibility={},evidence='ambiguous',suspect='xu',visible_cue=True,extra_cost=1,self_control=.5)
proof={**ev,'evidence':'verified','responsibility':{}}
registry={ev['id']:{'source':'authored decision'}};start=s.direction('xu').trust
close_inquiry(s,ev,proof,registry);load=s.self_load
for _ in range(12):close_inquiry(s,ev,proof,registry)
check('manufacture and clear a suspicion yields zero trust',s.direction('xu').trust==start and s.direction('xu').resentment(8)==0 and s.self_load==load)
check('unregistered invented misunderstanding rejected',rejected(lambda:close_inquiry(s,{**ev,'id':'fake'}, {**proof,'id':'fake'},registry)))
# Real harm then repair is compared with the SAME subsequent legitimate cooperation.
clean=Direction(trust=50);harm=Direction(trust=50)
harm.add('harm',8,severity=12,loss=8);harm.acknowledge('harm');harm.repair('harm','real-work','harm')
for d in [clean,harm]:d.trust=min(100,d.trust+3)
check('harm then valid repair cannot beat equally cooperative clean path',harm.trust<=clean.trust and harm.resentment(8)>=clean.resentment(8))
examples.append(dict(case='同样后续合作：无害／制造伤害后有效补救',clean=compact(clean),harm_then_repair=compact(harm)))
before=deepcopy(harm.__dict__);check('repeating same repair token has no additional reward',not harm.repair('harm','real-work','harm') and harm.__dict__==before)
check('different incident proof cannot repair this incident',not harm.repair('harm','other-work','other-incident'))
harm.revoke('harm');check('proven false attribution refunds actual loss without profit',harm.trust==clean.trust)
before=harm.trust;harm.revoke('harm');check('repeated correction cannot refund twice',harm.trust==before)

# Wrong evidence was allowed to partially edit directions in0.8; chronology is now
# checked at the canonical boundary before submitting a correction.
g2=Party(B['M02'],[v[0] for v in B['M02']['mandatory_groups']],['lin','xu','su'],skills=False,style='controls');r2=g2.run();before=state(social)
check('canonical battle timeline cannot move backwards',rejected(lambda:social.settle(g2,r2,g2.party,0)) and state(social)==before)

# The old ledger path would award4, then the new owner up to3. Explicitly verify off.
with contextlib.redirect_stdout(io.StringIO()):ns=runpy.run_path(str(ROOT/'work/campaign-review/ledger_review.py'))
Ledger=ns['Ledger'];packet=ns['packet']
for mid,yes,no in [('M15',['north','east'],['north']),('S02',['med','books'],['med']),('S04',['seed','rack'],['seed']),('S08',['luggage','tools'],['tools'])]:
 check('aggregate optional reward checks actual objects '+mid,bool(ns['objective_bonuses'](B[mid],yes)) and not ns['objective_bonuses'](B[mid],no))

old=Ledger('historical0.7');new=Ledger('0.9',external_social=True)
for x in [old,new]:x.deploy('M01',['lin','xu','su']);x.settle(packet('M01',['lin','xu','su']))
check('single owner disables legacy trust and pressure awards',old.rel['lin>xu']['trust']==38 and new.rel['lin>xu']['trust']==34 and new.crew['lin']['stress']==10)
examples.append(dict(case='旧结算与新入口叠加风险',initial=34,legacy_after=old.rel['lin>xu']['trust'],new_ledger_before_owner=new.rel['lin>xu']['trust']))

# No arbitrary free project can be supplied to social recovery.
new.begin_camp();social2=Social();social2.people['lin'].self_load=20;social2.sync(new);new.recover(['lin']);projects=new.projects;social2.night_from_ledger(new,1)
check('real recovery consumes project and changes self load once',projects==1 and social2.people['lin'].self_load==14 and new.day==2)
snapshot=deepcopy(social2.__dict__);check('same night cannot be replayed for free recovery',rejected(lambda:social2.night_from_ledger(new,1)) and state(social2.__dict__)==state(snapshot))

# Compact JSON typed serialization test of review states, not production save format.
def pack(x):
 if isinstance(x,Social):return {'@social':pack(x.__dict__)}
 if isinstance(x,Session):return {'@session':pack(x.__dict__)}
 if isinstance(x,Direction):return {'@direction':pack(x.__dict__)}
 if isinstance(x,Guidance):return {'@guidance':pack(x.__dict__)}
 if isinstance(x,dict):return {'@dict':[[pack(k),pack(v)] for k,v in x.items()]}
 if isinstance(x,set):return {'@set':[pack(v) for v in sorted(x,key=str)]}
 if isinstance(x,tuple):return {'@tuple':[pack(v) for v in x]}
 if isinstance(x,list):return [pack(v) for v in x]
 return x
def unpack(x):
 if isinstance(x,list):return [unpack(v) for v in x]
 if not isinstance(x,dict):return x
 if '@dict' in x:return {unpack(k):unpack(v) for k,v in x['@dict']}
 if '@set' in x:return set(unpack(v) for v in x['@set'])
 if '@tuple' in x:return tuple(unpack(v) for v in x['@tuple'])
 for key,cls in [('@social',Social),('@session',Session),('@direction',Direction),('@guidance',Guidance)]:
  if key in x:o=cls.__new__(cls);o.__dict__=unpack(x[key]);return o
 raise AssertionError('unknown save value')
restored=unpack(json.loads(json.dumps(pack(social),ensure_ascii=False)))
check('social JSON roundtrip retains receipts and dedup',restored.totals(1)==social.totals(1) and restored.settle(g,r,g.party,1).get('duplicate'))

# Every old actual map trace in every difficulty/weather goes through new guidance.
W=json.loads((O/'tactical-full-witnesses.json').read_text());modes=[]
for mode in ['light','off','detailed']:
 for w in W:
  guide=Guidance(mode);guide.scene(B[w['mission']],w['log']);cards=[x for x in guide.log if x['kind']=='nonmodal_card'];cap=3 if w['mission']=='M01' else 1
  assert len(cards)<=cap and (mode!='off' or not cards) and len({(x['mission'],x['round']) for x in cards})==len(cards) and all(not x['steals_focus'] and not x['auto_action'] for x in cards)
  modes.append(dict(mission=w['mission'],difficulty=w['difficulty'],variant=w['variant'],mode=mode,cards=len(cards),confirmations=sum(x['kind']=='decision_confirmation' for x in guide.log)))
check('828actual map traces keep bounded nonmodal guidance',len(modes)==828)
guide=Guidance();guide.offer('old','M12',1);guide.boundary('M12',2,set());check('stale target help is discarded',not guide.log and not guide.pending)
guide=Guidance('off');guide.offer('loss','M24',1,essential=True,decision='withdraw');guide.offer('loss','M24',1,essential=True,decision='withdraw')
check('turning off instruction retains one irreversible confirmation',len(guide.log)==1)
saved=unpack(json.loads(json.dumps(pack(guide))));saved.offer('loss','M24',1,essential=True,decision='withdraw');check('reload does not repeat same decision confirmation',len(saved.log)==1)

changed=Guidance('off');changed.offer('loss','M24',1,essential=True,decision='withdraw',decision_state='A-safe');changed.offer('loss','M24',2,essential=True,decision='withdraw',decision_state='A-wounded')
check('changed irreversible consequences require a fresh confirmation',len(changed.log)==2)
quiet=Guidance();quiet.scene(B['M01'],r['log'],restricted=True)
check('unrelated resentment cannot insert a cooperation lecture',not any(x['key']=='G07' for x in quiet.log))
for mid in ['M06','M12','M18','S07']:
 gd=Guidance();gd.scene(B[mid],[dict(round=1,action='intents')]);card=next(x for x in gd.log if x['key']=='G08')
 check('optional hint reads its own authored deadline '+mid,all('第'+str(o['opportunity_deadline'])+'轮' in card['copy'] for o in B[mid]['objectives'] if o.get('opportunity_deadline')))

# Relationship boundaries alter actual skill availability and permit explicit agreements.
relcases=[]
for mid in ['M16','M19','M23']:
 b=B[mid];goals=[v[0] for v in b['mandatory_groups']]
 for agree in [False,True]:
  battle=Party(b,goals,['lin','xu','su'],{a:3 for a in ['lin','xu','su']},skills=True,relations={('xu','leader'):True},agreements=agree,style='controls');x=battle.run();relcases.append(dict(mission=mid,agreements=agree,success=x['success'],rounds=x['rounds'],ap=x['ap'],refusals=x['relation_refusals'],skill_actions=x['skill_action_types'],log=x['log']))
check('high resentment retains full basic solution in tested complete maps',all(x['success'] for x in relcases))
check('explicit agreement changes an actual cooperation refusal',any(x['refusals']>0 for x in relcases if not x['agreements']) and all(x['refusals']==0 for x in relcases if x['agreements']))
runtime={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and f.suffix in ['.gd','.tscn','.godot'] and '.godot' not in f.parts}
check('no formal runtime changed',runtime==json.loads((ROOT/'work/tactical-review/runtime-before.json').read_text()))
out={'version':'0.9-integrated-review','passed_count':len(checks),'checks':checks,'examples':examples,'guidance_cases':modes,'relation_full_maps':relcases,'scope':'Adversarial offline receipt and scheduling cases; typed JSON review-state roundtrip is not production save implementation. Failed heuristic policies are not human failures.','runtime_unchanged':True}
(O/'integrated-review-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Integrated adversarial checks:',len(checks),'passed; guidance traces828.')
