from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
s=(ROOT/'work/full-audit/verify.py').read_text().split("(ROOT/'outputs/full-audit-checks.json').write_text")[0]
s=s.replace('96 unique registered nodes, not96 finished scripts','96 registered narrative nodes')
exec(compile(s,str(ROOT/'work/full-audit/verify.py'),'exec'))
F=ROOT/'game/data/final_design';EC=json.loads((ROOT/'game/data/campaign_economy_contract.json').read_text())
# Actual extra mode cap survives rounds, reloading, invalid actions, and still leaves movement mode.
g=fixture('su');g.use(0,'su_3',1);g.rnd+=1;g.h[0]['ap']=2;g.h[1]['ap']=2
check('balance','Second AP transfer rejected across rounds without spending',rejects(g,lambda:g.use(0,'su_3',2)))
saved=roundtrip(g);check('balance','Per-mission transfer cap persists',rejects(saved,lambda:saved.use(0,'su_3',2)))
g.use(0,'su_3',2,destination='movement');check('balance','Second total coordination use remains movement option',g.h[2]['move_bonus']==1 and g.used[(0,'su_3')]==2)
g=fixture('chen',3);g.objects['task']['p']=(4,4);g.use(0,'chen_3','task');check('balance','Chen protects device from2cells',g.objects['task']['shield']==3)
g=fixture('mo',5);g.objects['task']['p']=(7,4);g.control_ids.add('task');g.objects['task']['disables']='unit';g.use(0,'mo_1','task');check('balance','Mo works known control from5cells for2work',g.objects['task']['progress']==2)
g=fixture('mo',5);g.objects['task']['p']=(7,4);check('balance','Longer range never opens normal objective remotely',rejects(g,lambda:g.use(0,'mo_1','task')))
# Per-role controlled mechanics with real AP and state; not claims about player preference.
g=fixture('lin',5);g.objects['r1']['p']=(5,4);g.use(0,'lin_1','r1');check('role','Lin stabilization at3cells before pickup',g.objects['r1']['stable'] and g.h[0]['ap']==1)
g=fixture('xu',5);g.h[1]['p']=(3,5);g.rows[4][3]='X';g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True);g.use(0,'xu_1',destination=(4,4));check('role','Xu carries acrossoneblockedcell without common anchor',g.h[0]['p']==(4,4) and g.h[0]['carry']=='r1' and not g.anchors)
g=fixture('ye',3);g.h[0]['p']=(2,3);g.use(0,'ye_1','unit');check('role','Ye separates danger from retained machine state',g.e['unit']['output_isolated'] and not g.e['unit']['disabled'] and g.e['unit']['hp']==3 and g.h[0]['ap']==0)
g=fixture('he',3);g.h[0]['carry']='r1';check('role','He carries3 without buying/using support slot',g.budget(g.h[0])==3 and 'stretcher' not in g.gear)
g=fixture('jiang',5);g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True);g.h[1]['p']=(4,4);g.use(0,'jiang_1',1);check('role','Jiang transfersover2drycells preserving receiverAP',g.h[1]['carry']=='r1' and g.h[1]['ap']==2 and g.h[0]['ap']==1)
g=fixture('jiang',3,{'med_dose':1});g.h[0]['carry']='r1';g.h[1]['hp']=6;g.use(0,'jiang_3',1);check('role','Jiang can heal whilecarrying, payingactualmedicine',g.h[0]['carry']=='r1' and g.h[1]['hp']==9 and g.used['med_dose']==1)
for level,reach in [(1,1),(3,2),(5,3)]:
 g=fixture('jiang',level);g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True);g.h[1]['p']=(2+reach,4);g.use(0,'jiang_1',1);check('balance',f'JiangL{level}range{reach} legal',g.h[1]['carry']=='r1')
for obstacle in ['water','ally']:
 g=fixture('jiang',5);g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True);g.h[1]['p']=(5,4)
 if obstacle=='water':g.rows[4][3]='X'
 else:g.h[2]['p']=(3,4)
 check('balance','Jiang extendedhandoff rejects '+obstacle,rejects(g,lambda:g.use(0,'jiang_1',1)))
check('tradeoff','S02 medicalcache exceedscashconversion whilebookfund remainsflexible',next(r['reward']['supplies'] for r in EC['objective_rewards'] if r['mission']=='S02' and r['objective']=='med')*EC['supply_buy_cost']>next(r['reward']['credits'] for r in EC['objective_rewards'] if r['mission']=='S02' and r['objective']=='books'))
# Explicit objective payments: only secured, only once, real phase transitions.
def transaction(mid,secured=True):
 g=RelationshipLedger('objective reward',external_social=True);b=B[mid];g.day=b['day'];g.phase='briefing' if b['kind']=='main' else 'after_main'
 party=['lin','xu','su'];g.deploy(mid,party);return g
for reward in EC['objective_rewards']:
 mid,oid=reward['mission'],reward['objective'];objs={o['id']:o for o in B[mid]['objectives']};check('economy',mid+'.'+oid+' reward references actual objective',oid in objs)
 done=set()
 def add(k):
  for d in objs[k]['prerequisites']:add(d)
  done.add(k)
 add(oid)
 packet=dict(mission=mid,completed=sorted(done),secured=sorted(done),contributions={},injured=[],withdrawn=[],consumed={},branch=None)
 for secured in [True,False]:
  g=transaction(mid);p=deepcopy(packet)
  if not secured:p['secured']=[]
  g.settle(p);paid=[r for r in g.records if r['kind']=='objective_reward' and r['mission']==mid and r['object']==oid]
  check('economy',mid+'.'+oid+(' secured paysonce' if secured else ' completedbutlost givesnothing'),len(paid)==int(secured) and (not paid or paid[0]['reward']==reward['reward']))
  check('economy',mid+'.'+oid+' no second settlement '+str(secured),rejects(g,lambda:g.settle(p)))
# Zero-money no-success campaign: explicitly supplied results, not synthetic combat proof.
g=RelationshipLedger('empty allfailed',hard=True,empty=True,external_social=True)
for day in range(1,25):
 g.day=day
 for actor in g.crew:
  if g.crew[actor]['joined']:g.crew[actor]['withdrawn']=True
 if day==24:g.route='evacuation'
 g.deploy(f'M{day:02}',[]);g.settle(dict(mission=f'M{day:02}',completed=[],secured=[],contributions={},injured=[],withdrawn=[],consumed={},branch='evacuation' if day==24 else 'repair' if day==17 else None))
 check('fallback',f'D{day} zeroavailableheroes still legal withnonnegative budget',all(v>=0 for v in g.resources.values()) and g.rows[-1]['reserves']==3)
 if day<24:g.begin_camp();g.night()
check('fallback','24failed duties still reach evacuation;6credit floor notremoved',g.summary()['world_ending']=='evacuation' and g.resources['credits']==144)
maximum={k:EC['start'][k]+24*EC['main_rewards']['success'][k]+12*EC['side_rewards']['success'][k]+sum(r['reward'].get(k,0) for r in EC['objective_rewards']) for k in ['credits','parts']}
check('tradeoff','Evenallcashcaches cannotbuyallfacilitiesplusalltools',maximum['credits']==416 and maximum['credits']<380+98)
check('tradeoff','47parts maximumforcesfacilityselection evenwithouttoolpurchases',maximum['parts']==47 and maximum['parts']<48)
# A real camp tradeoff rather than an abstract positive balance.
g=RelationshipLedger('budget choice',external_social=True);g.day=12;g.phase='camp';g.resources=dict(credits=35,supplies=2,parts=4);g.settled={f'M{i:02}' for i in range(1,13)};before=deepcopy(g)
g.upgrade('communications');check('tradeoff','Buy35credit facility excludes20credit winch now',rejects(g,lambda:g.buy_tool('winch')) and g.fac['communications']==1)
before.buy_tool('winch');check('tradeoff','Buy20credit winch excludes35credit facility now',rejects(before,lambda:before.upgrade('communications')) and 'winch' in before.tools)
# Narrative completeness / truthful branch ownership.
st=json.loads((F/'stories.json').read_text());script=json.loads((F/'character_scripts.json').read_text());all_ids=[]
for source,target in [('personal_nodes','personal'),('relationship_nodes','relationships'),('community_nodes','community'),('recovery_nodes','life'),('chapter_nodes','chapter')]:
 lookup={x['id']:x for x in script[target]};check('scripts',source+' exact authored ID coverage',set(lookup)=={x['id'] for x in st[source]})
 for n in st[source]:
  x=lookup[n['id']];all_ids.append(n['id']);assert n['dialogue_ref'].endswith('#'+n['id'])
  if 'choices' in n:check('scripts',n['id']+' every choice has written response',set(x['choices'])=={c['id'] for c in n['choices']} and all(all(isinstance(t,str) and t.strip() for t in lines) for lines in x['choices'].values()))
  if target=='personal':check('scripts',n['id']+' absent/unmet/laterbreach/unread text exists',all(x[k] for k in ['withdrawn','unmet','later_breach','unread','injured']))
  if target=='chapter':check('scripts',n['id']+' only secured facts count',x['condition']['state']=='secured')
check('scripts','96 full nodes with distinct IDs',len(all_ids)==len(set(all_ids))==96)
check('scripts','M17 active isolation has its own successful story branch',bool(next(n for n in script['chapter'] if n['id']=='K12')['isolate_text']))
check('scripts','No obsolete learning-cooperation promise inR06',all('学习' not in c['label'] and '再学' not in c['label'] for c in next(n for n in st['relationship_nodes'] if n['id']=='R06')['choices']))
if not __import__('os').environ.get('NIGHT_TIDE_CURRENT_RULE_CHECK'):
 oldhash=json.loads((ROOT/'work/player-ready-review/runtime-before.json').read_text());newhash={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and (f.suffix in ['.gd','.tscn'] or f.name=='project.godot')};check('scope','0.15 production runtime remains byte-identical',oldhash==newhash)
(ROOT/'outputs/player-ready-checks.json').write_text(json.dumps(dict(version='0.15',passed=len(checks),checks=checks,scope='Prior195crosssystem checks rerun plus new balance,transaction,script and fallback checks. Controlled fixtures are not human usability tests.'),ensure_ascii=False,indent=2)+'\n');print('PASSED',len(checks),flush=True)
