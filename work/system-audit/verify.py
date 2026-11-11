"""Cross-system design regressions, counterexamples and invariant checks.
Supplied mission outcomes do NOT establish tactical feasibility or player fun.
"""
from pathlib import Path
from copy import deepcopy
import json, runpy, random, hashlib, contextlib, io, sys
ROOT=Path(__file__).resolve().parents[2]; O=ROOT/'outputs'; D=ROOT/'game/data/final_design'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from reference import *
with contextlib.redirect_stdout(io.StringIO()):
    ns=runpy.run_path(str(ROOT/'work/campaign-review/ledger_review.py'))
Ledger=ns['Ledger']; packet=ns['packet']; boards=ns['BOARDS']
verified=ns['verified']; R=ns['PROOFS']['R']; valid=ns['PROOFS']['cases']
checks=[]; examples=[]
def check(group,name,ok,detail=None):
    assert ok,(group,name,detail)
    checks.append(dict(group=group,name=name,detail=detail))
def rejected(g,fn,name):
    before=deepcopy(g.__dict__)
    try:fn();caught=False
    except (AssertionError,KeyError,ValueError):caught=True
    check('transaction',name,caught and before==g.__dict__)

# Reproduce the hidden overflow problem before exercising the funded solution.
old_before=min(100,42+40+40+40)
old_after=min(100,42+40+40+40*.45)
check('memory','old capped total hides a genuine repair',old_before==old_after==100)
r=Direction(42,100)
for i in range(3):r.add('severe'+str(i),1,severity=40,loss=10,severe=True)
before=r.resentment(1); r.acknowledge('severe2');r.repair('severe2','repair2','severe2'); after=r.resentment(1)
check('memory','repair at100 visibly reduces actual total',before==100 and after<100)
check('memory','sum of displayed active sources equals actual number',abs(after-(r.grudge+sum(value(m,1) for m in r.memories)))<1e-8)
examples.append(dict(id='saturation',old_before=old_before,old_after=old_after,new_before=before,new_after=round(after,4),new_active=[round(value(m,1),4) for m in r.memories]))
check('memory','duplicate restitution cannot mint trust',not r.repair('severe2','another','severe2'))
check('memory','unrelated repair evidence rejected',not r.repair('severe0','proof','unrelated'))
before_trust=r.trust;before_r=r.resentment(1)
check('memory','duplicate incident adds neither memory nor loss',not r.add('severe2',1,severity=40,severe=True) and r.trust==before_trust and r.resentment(1)==before_r)
t=Direction();t.add('s',1,severity=40,severe=True,stress=0);eight=t.resentment(9)
check('memory','severe8day decay uses blended floor not max-floor',abs(eight-27)<1e-8,{'correct':eight,'old_ledger':max(20,14)})
t.acknowledge('s');t.repair('s','fix','s')
check('memory','restitution clears serious residual floor',abs(t.resentment(9)-9)<1e-8)
r=Direction(42,100)
for i in range(4):r.add('ordinary'+str(i),1,severity=12)
check('memory','ordinary live slots never exceed3',sum(m.get('active',True) for m in r.memories)<=3)
active=next(m['id'] for m in r.memories if m.get('active',True));before=r.resentment(1);r.acknowledge(active);r.repair(active,'o_fix',active)
check('memory','archived ordinary event does not refill after repair',r.resentment(1)<before and sum(m.get('active',True) for m in r.memories)<=3)
r=Direction(42,100);trace=[]
for day in range(1,4):
    r.add(f'e{day}',day,promise=f'p{day}',sensitivity=1.25,warned=True)
    trace.append(round(r.resentment(day),4))
check('memory','third distinct warned breach escalates once',len(r.memories)==3 and r.memories[-1]['severe'] and trace[-1]>=80)
examples.append(dict(id='repeated_breach',resentment=trace,trust=r.trust))
r=Direction(0,100)
for day in [1,2,4]:r.add('d'+str(day),day,promise='p'+str(day),warned=True)
check('memory','D-3 is outside the three-day escalation window',not r.memories[-1]['severe'])
r=Direction()
for i in range(3):r.add('old'+str(i),10,occurrence_day=i+1,promise='p'+str(i),warned=True)
check('memory','late discovery does not invent contemporaneous warning/escalation',not any(m['severe'] for m in r.memories))
r=Direction();r.add('unknown',1,known=False)
check('attribution','unknown responsibility does not deduct directed trust',not r.memories and r.trust==50)
check('attribution','forced operator receives no blame',attribution(True)=={'leader':1})
check('attribution','informed volunteer splits responsibility with approving leader',attribution(True,informed_voluntary_proposer='xu')=={'leader':.5,'xu':.5})
effects=[dict(observer='lin',target='leader',root_decision='M06_extra',severity=12,loss=8,severe=False,consequence=k) for k in ['injury','missed_exit','delayed_treatment']]
merged=coalesce_effects(effects)
check('attribution','one decision with three consequences is one memory',len(merged)==1 and merged[0]['severity']==12 and merged[0]['loss']==8)
effects.append(dict(observer='lin',target='leader',root_decision='M06_later_lie',severity=16,loss=10,severe=True))
check('attribution','new intentional concealment remains a separate choice',len(coalesce_effects(effects))==2)
effects.append(dict(observer='su',target='leader',root_decision='M06_extra',severity=12,loss=8,severe=False))
check('attribution','different witnesses retain their own directed memories',len(coalesce_effects(effects))==3)
r=Direction();r.add('same',1)
r.revise_consequence('same',1,16,10,True)
check('attribution','known severe consequence amends one event and deducts only trust delta',len(r.memories)==1 and r.trust==40)
before=deepcopy(r)
r.revise_consequence('same',1,16,10,True)
check('attribution','replaying same consequence does not amplify memory',abs(r.resentment(1)-before.resentment(1))<1e-8 and r.trust==before.trust)
r.acknowledge('same');r.repair('same','corrective','same');r.revoke('same')
check('attribution','false blame refunds actual net loss without double restitution',r.trust==50 and r.resentment(1)==0 and not r.revoke('same'))
r=Direction(42);r.add('new',1,severity=12,category='fairness',stress=0)
check('attribution','unrelated history does not use promise-specific sensitivity multiplier',abs(r.memories[0]['raw_strength']-12*(1+.8*.42**2))<1e-8)
g=Ledger('shared incident');g.deploy('M01',['lin','xu','su'])
g.breach('lin','leader',responsibility=.5,event_id='one');g.breach('lin','xu',responsibility=.5,event_id='one')
check('attribution','one source permits distinct accountable directions',len(g.rel['lin>leader']['memories'])==1 and len(g.rel['lin>xu']['memories'])==1)
before=deepcopy(g.__dict__);g.breach('lin','xu',responsibility=.5,event_id='one')
check('attribution','duplicate directed event is a true no-op',before==g.__dict__)
rejected(g,lambda:g.breach('lin','su',responsibility=.5,event_id='one'),'third attribution cannot exceed total responsibility1')

stage=0;stages=[]
for q in [84,64,59,50,49]:stage=band_after(stage,q,0);stages.append(stage)
check('conflict','hysteresis retains refusal until below50',[3,3,2,2,1]==stages,stages)
check('conflict','very low resentment cannot be forced into conflict by general stress',band_after(3,24,100)==0)
cs=ConflictScenes();pair=['lin','xu']
check('conflict','first relevant warned rupture gets one long scene',cs.trigger(pair,6,'M06',3,True,True,True))
check('conflict','reversing direction does not bypass pair cooldown',not cs.trigger(pair[::-1],6,'S03',3,True,True,True))
check('conflict','next day remains on cooldown',not cs.trigger(pair,7,'M07',3,True,True,True))
check('conflict','expiry alone cannot surprise player with a scene',not cs.trigger(pair,8,'M08',3,True,True,False))
check('conflict','new warned request on D+2 may trigger',cs.trigger(pair,8,'M08',3,True,True,True))
check('conflict','another pair cannot cause second long scene in same mission',not cs.trigger(['ye','chen'],8,'M08',3,True,True,True))
g=Ledger('leader conditions');g.rel['lin>xu']['trust']=70;g.rel['xu>lin']['trust']=70;g.rel['lin>leader']['grudge']=70
check('conflict','anger at commander constrains dangerous order without blaming partner',not g.cooperation_allowed(['lin','xu'],'protected_work',['fall']) and g.rel['lin>xu']['grudge']==42)
check('conflict','real protection restores that action during cooldown too',g.cooperation_allowed(['lin','xu'],'protected_work',['fall'],['third_person_protection']))
g.rel['lin>leader']['grudge']=55
check('conflict','ledger retains conditional band at55',not g.cooperation_allowed(['lin','xu'],'protected_work',['fall']))
g.rel['lin>leader']['grudge']=49
check('conflict','ledger exits conditional band below50',g.cooperation_allowed(['lin','xu'],'protected_work',['fall']))
check('conflict','high resentment leaves legal basic deployment available',all(g.eligible(a) for a in ['lin','xu','su']))

check('combat','hard downed but retrieved is injury, not permanent loss',retrieval(True,True,'hard',False)=='injury')
check('combat','hard standing emergency evac never permanent loss',retrieval(False,False,'hard',True)=='injury')
check('combat','hard abandoned downed actor withdraws',retrieval(True,False,'hard',True)=='medical_withdrawal')
check('combat','standard abandoned downed actor is recoverable',retrieval(True,False,'standard',True)=='injury')
check('combat','delivery precedes same-round rescue expiry',resolve_due_round(6,True,True) is None)
check('combat','stabilization extends once, not a new full timer',resolve_due_round(6,True,False)==7)

g=Ledger('resources')
for item,n in [('invented',1),('foam',1),('battery',1),('med_dose',.5),('med_dose',True)]:
    rejected(g,lambda i=item,n=n:g.craft(i,n),'illegal recipe/unlock/quantity '+str((item,n)))
g.day=2;g.settled.add('M01')
rejected(g,lambda:g.buy_tool('battery'),'zero-price consumable cannot be bought as permanent tool')
g.craft('battery',1);before=g.resources['supplies'];g.deploy('M02',['lin','xu','su'],pack={'battery':1})
rejected(g,lambda:g.settle({**packet('M02',['lin','xu','su']),'consumed':{'battery':.5}}),'fractional inventory settlement atomically rejected')
g.settle(packet('M02',['lin','xu','su'],consumed={'battery':1}))
check('economy','crafted/packed/consumed conservation with real ledger',g.inventory['battery']==0 and g.resources['supplies']==before+2)
g.begin_camp();g.rel['lin>su']['trust']=70;g.rel['su>lin']['trust']=70
rejected(g,lambda:g.train(['lin','su'],'invented_protocol'),'unknown training protocol cannot consume a project or mint unlock')
h=Ledger('public review');h.phase='camp';h.day=18;h.fac['communications']=2
rejected(h,lambda:h.review(['E_ORDER','E_WARNING']),'tier2 does not silently extend two-record power to D18')
h.day=20
rejected(h,lambda:h.review(['E_ORDER','E_ORDER']),'duplicate evidence cannot masquerade as two distinct records')
h.review(['E_ORDER','E_WARNING'])
check('economy','tier2 legitimate two-record project costs one slot',len(h.evidence)==2 and h.projects==1)

bad=deepcopy(valid['su']);bad[1]['mission_kind']='side';bad[1]['mission']='S07'
check('story','side duty cannot satisfy Su two-main-duty plan',not verified('su',bad))
check('story','assigned but never performed support cannot satisfy Su plan',not verified('su',[x for x in valid['su'] if x['kind']!='support_work']))
check('story','actual two-main schedule remains accepted',bool(verified('su',valid['su'])))
g=Ledger('missing deadline');g.plans['xu']=0;g.deploy('M01',['lin','xu','su']);p=packet('M01',['lin','xu','su']);del p['kept_deadline'];g.settle(p)
check('story','missing Xu promise record defaults to unproven',not verified('xu',g.records,0,g.day))
g=Ledger('retrieved injured teammate');g.day=17;g.crew['he']['joined']=True;g.plans['he']=0;g.deploy('M17',['lin','he','su']);p=packet('M17',['lin','he','su'],injured=['lin']);g.settle(p)
check('story','injured teammate brought back counts as all retrieved',any(r['kind']=='mission_settled' and r['all_extracted'] for r in g.records))
check('story','He proof remains valid with safely retrieved injury',bool(verified('he',g.records,0,g.day)))
check('story','D22 Su two-future-main promise refused',not contract_deadline('su',22))
check('story','D21 Su plan still has two main windows',contract_deadline('su',21))
check('story','D22 Chen plan refused because M23 lacks work',not contract_deadline('chen',22) and all(o['kind']!='work' for o in boards['M23']['objectives']))
check('story','D20 Chen plan has actual M21 engineering targets',contract_deadline('chen',20) and any('engineering' in o['interaction_tags'] for o in boards['M21']['objectives']))
check('story','D22 Lin plan has actual M23 casualty targets',contract_deadline('lin',22) and any(o['kind']=='rescue' for o in boards['M23']['objectives']))
g=Ledger('too late plan');g.day=22;g.phase='camp';g.read_nodes.add('P_su_1')
rejected(g,lambda:g.scene('P_su_2'),'late impossible plan does not charge scenes, projects or payment')
g.scene('P_su_2','specialist')
check('story','late reader still has complete professional choice',g.projects==1 and 'P_su_2' in g.read_nodes and 'su' not in g.plans)
g=Ledger('explicit career');g.day=18;g.phase='camp';g.read_nodes.update(['P_su_1','P_su_2']);g.scene('P_su_3','new_life')
check('story','player can explicitly choose career change without fabricated proof',g.character_ending('su')['career']=='postwar_change' and g.character_ending('su')['contract']=='not_promised')
g=Ledger('missing partner');g.day=6;g.phase='camp';g.crew['xu']['withdrawn']=True;g.scene('R01')
check('story','absent partner creates correspondence coda, not live pair scene',g.records[-1]['kind']=='absent_pair_coda')
check('ending','completed plan survives later medical withdrawal',contract_status(True,True,True)=='fulfilled')
check('ending','uncompleted plan is interrupted, not maliciously broken',contract_status(True,False,True)=='interrupted_by_injury')
g=Ledger('fulfilled before loss');g.plans['lin']=5;g.verified_at['lin']=20;g.crew['lin']['withdrawn']=True;g.finals['lin']='new_life'
check('ending','actual ledger preserves fulfilled history plus hospital presence',g.character_ending('lin')['contract']=='fulfilled' and g.character_ending('lin')['presence']=='medical_withdrawal')
g=Ledger('later privacy breach');g.crew['mo']['joined']=True;g.plans['mo']=0;g.receipt('public_record_release',privacy='redacted');g.confirm_audits();g.receipt('public_record_release',privacy='unredacted')
check('ending','past achievement and later ongoing-duty breach coexist',g.character_ending('mo')['contract']=='fulfilled' and g.character_ending('mo')['ongoing_obligation']=='breached')
events=[dict(kind='breach',id='a',observer='lin',target='leader'),dict(kind='breach',id='b',observer='lin',target='xu'),dict(kind='repair',repairs='b',observer='lin',target='xu')]
check('ending','repairing one directed incident leaves another unresolved',[x['id'] for x in relationship_overlays(events,'lin')]==['a'])
check('ending','unrelated character does not inherit rupture',not relationship_overlays(events,'chen'))
g=Ledger('M17 cap');g.day=17;g.district[ns['WORLD']['M17']['district']]=3;g.deploy('M17',['lin','xu','su']);g.settle(packet('M17',['lin','xu','su'],branch='isolate'))
check('world','M17 isolation clips current district as well as future cap',g.district[ns['WORLD']['M17']['district']]==2 and g.caps[ns['WORLD']['M17']['district']]==2)
h=Ledger('wrong M17 branch');h.day=17;h.deploy('M17',['lin','xu','su']);p=packet('M17',['lin','xu','su'],branch='isolate');p['branch']=None
rejected(h,lambda:h.settle(p),'isolation action cannot be settled under unspecified repair branch')
g=Ledger('route facts');g.day=24;g.route='shared_control';g.evidence={'E_ORDER','E_MAINTENANCE'}
rejected(g,lambda:g.deploy('M24',['lin','xu','su']),'two records cannot bypass infrastructure threshold')
g.route='evacuation';g.deploy('M24',['lin','xu','su']);p=packet('M24',['lin','xu','su'],'success','shared_control')
rejected(g,lambda:g.settle(p),'wrong-route objects cannot pay chosen-route victory')
g.settle(packet('M24',['lin','xu','su'],'partial','evacuation'))
check('world','failed final plan keeps only actual saved object',g.summary()['world_ending']=='evacuation' and g.rows[-1]['secured']==['r1'])
rejected(g,lambda:g.begin_camp(),'M24 cannot open a nonexistent final camp')

# Independent metamorphic checks, not hundreds of duplicate named examples.
rng=random.Random(61031);state_steps=0;max_drift=0
for trial in range(160):
    r=Direction(rng.choice([0,12,42,85,100]),100);day=1
    for step in range(50):
        old=r.resentment(day);choice=rng.randrange(5)
        if choice in [0,1]:
            r.add(f'{trial}_{step}',day,severity=rng.choice([8,12,16,18,40]),severe=choice==1,category=rng.choice(['promise','fairness','humiliation']),share=rng.choice([.5,1]))
            assert r.resentment(day)+1e-7>=old
        elif choice==2:
            day+=rng.randint(1,3);assert r.resentment(day)<=old+1e-7
        elif choice==3 and r.memories:
            m=rng.choice(r.memories);r.acknowledge(m['id']);r.repair(m['id'],f'fix_{step}',m['id']);assert r.resentment(day)<=old+1e-7
        elif choice==4:
            r.history(r.history_stage+1,f'h_{step}');assert r.resentment(day)<=old+1e-7
        current=r.resentment(day);assert -1e-8<=current<=100+1e-8 and 0<=r.trust<=100
        assert all(sum(m.get('active',True) and not m['severe'] and m['category']==c for m in r.memories)<=3 for c in ['promise','fairness','humiliation'])
        for c in ['promise','fairness','humiliation']:assert sum(value(m,day) for m in r.memories if not m['severe'] and m['category']==c)<=24+1e-7
        prior=deepcopy(r.memories);fund(r.grudge,r.memories,day);max_drift=max(max_drift,abs(r.resentment(day)-current));assert max_drift<1e-7
        state_steps+=1
check('properties','8000 seeded relationship transitions preserve caps and monotonic repair/decay',state_steps==8000,{'transitions':state_steps,'max_reallocation_drift':max_drift})
band_cases=0
for initial in range(4):
    for resentment in range(101):
        last=0
        for stress in range(101):
            new=band_after(initial,resentment,stress);assert 0<=new<=3 and new>=last;last=new;band_cases+=1
check('properties','40804 band states respect bounds and increasing stress monotonicity',band_cases==40804,{'states':band_cases})
for b in boards.values():
    ids={o['id'] for o in b['objectives']+b['controls']}
    for enemy in b['enemies']:assert enemy['disable_requires'] and set(enemy['disable_requires'])<=ids
check('content','all36maps retain authored baseline shutdown references',len(boards)==36)
s=json.loads((D/'stories.json').read_text())
check('content','M24 narrative delivered as epilogue, not camp',all(n.get('delivery')=='ending_archive_no_camp_no_extra_rewards' for n in s['community_nodes']+s['chapter_nodes'] if n['source']=='M24'))
baseline=json.loads((ROOT/'work/system-audit/runtime-before.json').read_text())
now={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and f.suffix in ['.gd','.tscn','.godot'] and '.godot' not in f.parts}
check('scope','all runtime scripts/scenes/project files unchanged',baseline==now,{'files':len(now)})
out={'version':'0.6-system-audit','date':'2026-11-01','passed_count':len(checks),'checks':checks,'examples':examples,'property_cases':{'relationship_transitions':state_steps,'band_states':band_cases},'existing_suites':{'content':json.loads((O/'final-design-validation.json').read_text())['passed_count'],'story':json.loads((O/'story-contract-checks.json').read_text())['passed_count'],'ledger':json.loads((O/'whole-campaign-review.json').read_text())['passed_count'],'equipment':json.loads((O/'equipment-target-review.json').read_text())['passed_count']},'boundaries':['Design reference calculations and supplied mission results; no complete tactical campaign simulation.','Narrative clauses such as attribution correction and carrier expiry are specified; not every clause has an executable gameplay model.','Rule correctness is distinct from fun, market demand, measured duration, balance and runtime implementation.']}
(O/'system-audit-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'properties':out['property_cases'],'examples':examples,'runtime_unchanged':True},ensure_ascii=False,indent=2))
