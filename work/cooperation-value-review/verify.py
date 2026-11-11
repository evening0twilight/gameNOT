from current_rules import *
import hashlib,runpy
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
def rejects(f):
 try:f();return False
 except AssertionError:return True
check('16 active specialties and7 equipment types',len(SCOPE['abilities'])==16 and len(SCOPE['equipment'])==7)
check('No paid pair-learning branch or universal trust gate',not SCOPE['cooperation']['training_tree'] and not SCOPE['cooperation']['learned_pair_flags'] and not SCOPE['cooperation']['blanket_trust_threshold'])
P=['lin','xu','su'];L={a:5 for a in P}
g=CurrentBattle(B['M06'],['r1','r2'],P,L,trained=[],trust={(a,b):0 for a in P for b in P if a!=b})
check('Untrained low-trust pair may perform contextually legal relay',g.protocol_ready('relay_carry',0,2))
g.relations[('su','lin')]=True
check('Concrete handoff dispute still requires receiver agreement',not g.protocol_ready('relay_carry',0,2))
g.agree('relay_carry',0,2)
check('Named action agreement restores this cooperation only',g.protocol_ready('relay_carry',0,2) and not g.prepared.get(('agreement','coordinated_pull',0,2)))
g=CurrentBattle(B['M10'],['test1','test2'],P,L,relations={('lin','su'):True},trained=[])
check('Removing training does not erase physical fall safeguards',not g.protocol_ready('protected_work',0,2))
for level in [4,5,6]:
 g=CurrentBattle(B['M06'],['r1','r2'],P,{a:level for a in P});h=g.h[2];target=next(iter(g.e));h['p']=(6,2)
 for i in range(2):h['ap']=2;g.marks.clear();g.use(2,'su_1',target)
 h['ap']=2;g.marks.clear()
 if level==4:check('L4 retains two first-specialty uses',rejects(lambda:g.use(2,'su_1',target)))
 else:
  g.use(2,'su_1',target);check('L'+str(level)+'third use is legal and paid',g.used[(2,'su_1')]==3 and h['ap']==1)
  h['ap']=2;g.marks.clear();check('L'+str(level)+'fourth use still rejected',rejects(lambda:g.use(2,'su_1',target)))
check('Temporary reference limit does not mutate ability definition',ABILITIES['su_1']['charges_per_mission']==2)
g=CurrentBattle(B['M06'],['r1','r2'],P,{a:6 for a in P})
check('L6 second passive uses individual level for first free movement',g.budget(g.h[0])==4)
g.h[0]['first_move']=False
check('L6 movement passive is not infinite',g.budget(g.h[0])==3)
g.h[0]['first_move']=True;g.h[0]['carry']='r1'
check('First free movement bonus does not increase carrying budget',g.budget(g.h[0])==2)
g=CurrentBattle(B['M06'],['r1','r2'],P,L)
for key in SCOPE['retired_equipment']+SCOPE['retired_abilities']:
 check('Retired command rejected: '+key,rejects(lambda:g.use(0,key)))
check('Cannot pack retired equipment',rejects(lambda:CurrentBattle(B['M06'],['r1','r2'],P,L,gear={'foam':0})))
# Same four field-operation rules, using only current equipment/abilities.
field=[]
for mid in ['M05','M10','M21','S11']:
 board=B[mid];goals=[x[0] for x in board['mandatory_groups']];spec=CONTRACT['services'][mid]
 for watchers in itertools.permutations(range(3),len(spec['posts'])):
  for mode,skills,ambition in itertools.product(['independent','protected','dismantle'],[False,True],[False,True]):
   for gear in [{},{'shield':next(i for i in range(3) if i not in watchers)}]+([{'insulation':watchers[0]}] if board['day']>7 else []):
    b=CurrentBattle(board,goals,P,L,approach=mode,watchers=watchers,trained=[],skills=skills,ambition=ambition,gear=gear,style='controls');r=b.run();field.append(compact(r))
 check(mid+'retains a sampled optional field solution',any(r['mission']==mid and r['success'] and r['service_secured'] for r in field))
out=json.loads((ROOT/'outputs/cooperation-current-matrix.json').read_text())
check('Current1432named configurations retain a primary solution',len(out['rows'])==1432 and all(r['success'] for r in out['rows']))
check('Current276difficulty/weather contexts retain a primary solution',len(out['baseline'])==276 and all(r['success'] for r in out['baseline']))
campaigns=json.loads((ROOT/'outputs/cooperation-current-campaign.json').read_text())
for s in campaigns['scenarios']:
 q=s['summary'];check(q['name']+' reaches24main missions',q['main_count']==24)
 check(q['name']+' has no learned protocol flags',not q['trained_protocols'])
 check(q['name']+' never purchases excluded equipment',not set(q['tools'])&set(SCOPE['retired_equipment']))
 check(q['name']+' nonnegative budget',all(v>=0 for v in q['resources'].values()))
 check(q['name']+' has no cooperation training reward',not any(r['kind']=='coordination_bundle' for r in s['receipts']))
# Ordinary route refutes the old M06 archive claim across all four early trios.
f=json.loads((ROOT/'outputs/cooperation-focused-ordinary.json').read_text())
check('Four early trios retrieve M06all goals with ordinary6round zero-damage routes',all(r['success'] and r['rounds']==6 and r['damage']==0 and {'r1','r2','asset'}<=set(r['secured']) for r in f if r['mission']=='M06') and sum(r['mission']=='M06' for r in f)==4)
a=json.loads((ROOT/'outputs/cooperation-value-campaign.json').read_text());control=json.loads((ROOT/'outputs/cooperation-equal-training-controls.json').read_text())
for s in a['scenarios']:
 if not s['summary']['name'].endswith('_cultivate'):continue
 name=s['summary']['name'].removesuffix('_cultivate');c=next(x for x in control['scenarios'] if x['summary']['name']==name+'_trained_no_actions')
 keys=['resources','xp','world_ending','character_endings','withdrawn','main_count','side_count']
 check(name+'same-training control isolates cooperation',all(s['summary'][k]==c['summary'][k] for k in keys))
before=json.loads((ROOT/'work/cooperation-value-review/runtime-before.json').read_text());after={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and (f.suffix in ['.gd','.tscn'] or f.name=='project.godot')}
check('Formal runtime is byte-identical',before==after)
result=dict(version='0.12',passed=len(checks),checks=checks,field_trials=len(field),field_results=field,runtime_unchanged=True)
(ROOT/'outputs/cooperation-current-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('CURRENT CHECKS',len(checks),'field trials',len(field))
