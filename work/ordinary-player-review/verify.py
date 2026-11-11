from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'work/player-ready-review/verify.py').read_text().split("(ROOT/'outputs/player-ready-checks.json').write_text")[0]
exec(compile(source,str(ROOT/'work/player-ready-review/verify.py'),'exec'))
import sys;sys.path.insert(0,str(ROOT/'work/ordinary-player-review'))
from narrative import render,SCENES
from social import qualified
# All real personal branch choices go through the ledger, not only supplied proof packets.
st=json.loads((ROOT/'game/data/final_design/stories.json').read_text())
for n in st['personal_nodes']:
 if n['stage']>2:continue
 for choice in n['choices']:
  g=RelationshipLedger('all actual storychoices',external_social=True);g.day=max(n['earliest_day'],18);g.phase='camp';g.resources.update(credits=100,supplies=20)
  for actor in g.crew:g.crew[actor].update(joined=True,withdrawn=False)
  g.read_nodes.update(n['requires_resolved']);g.scene(n['id'],choice['id']);r=next(r for r in g.records if r['kind']=='story_choice')
  check('narrative',n['id']+'/'+choice['id']+' actualchoicepersisted',r['choice']==choice['id'])
  if choice.get('credits'):
   check('narrative',n['id']+' exactpayment',g.resources['credits']==100-choice['credits'])
  if n['id']=='P_mo_2':check('narrative','Mo '+choice['id']+' doesnotinstantlypublish',not any(r['kind']=='public_record_release' for r in g.records))
g=RelationshipLedger('real Mo publication',external_social=True);g.day=18;g.phase='camp';g.crew['mo']['joined']=True;g.read_nodes.add('P_mo_1');g.scene('P_mo_2','redact');g.evidence.add('E_WARNING')
check('narrative','Mo cannotdoa secondpersonalproject the sameevening',rejects(g,lambda:g.release_redacted('E_WARNING')))
g.day=19;g.projects=0;g.used.clear();g.release_redacted('E_WARNING')
check('narrative','Actual publication consumes oneproject and verifiesplan',g.projects==1 and 'mo' in g.used and c.Ledger.scene is not None and any(r['kind']=='public_record_release' for r in g.records))
g.confirm_audits();check('narrative','ActualpublicationfulfillsMoobligation','mo' in g.verified_at)
check('narrative','Duplicatepublicationdoesnotfarm receipts',rejects(g,lambda:g.release_redacted('E_WARNING')))
g.day=20;g.projects=0;g.used.clear();check('narrative','No publicationof unknown evidence',rejects(g,lambda:g.release_redacted('NOT_KNOWN')))
# Final choices traverse the actual ledger with explicitly supplied evidence fixtures.
# These are branch/transaction tests, not claims of earned campaign proof.
proof_examples=json.loads((ROOT/'outputs/story-contract-checks.json').read_text())['valid_examples']
# Migrate the supplied He fixture to the current explicit-contribution schema.
# A display-only primary_contributor label no longer authenticates delegation.
for row in proof_examples['he']:
 if row['kind']=='objective_completed':row['contributors']=['su']
for n in st['personal_nodes']:
 if n['stage']!=3:continue
 for choice,hasproof,presence in itertools.product(n['choices'],[False,True],['healthy','injured','withdrawn']):
  a=n['actor'];g=RelationshipLedger('finalchoice fixture',external_social=True);g.day=23;g.phase='camp';g.crew[a].update(joined=True,withdrawn=presence=='withdrawn',ready=25 if presence=='injured' else 1);g.read_nodes.update(n['requires_resolved']);g.plans[a]=10;g.records=deepcopy(proof_examples[a]) if hasproof else [];g.seq=30
  label=n['id']+'/'+choice['id']+'/'+str(hasproof)+'/'+presence
  if choice['id']=='integrated' and not hasproof and presence!='withdrawn':check('ending',label+' rejectsunsupportedwarmending',rejects(g,lambda:g.scene(n['id'],choice['id'])))
  else:
   g.scene(n['id'],choice['id']);check('ending',label+' respectschoiceorpresence',g.finals[a]==('medical_withdrawal' if presence=='withdrawn' else choice['id']))
# Enumerate semantic lines across every authored choice and responsibility/presence state.
rendered=0
for nid,n in SCENES.items():
 a=n['actor']
 events=[None,dict(known_by=[a],observer=a,target='leader',responsibility={'leader':1},evidence='verified'),dict(known_by=[a],observer='leader',target=a,responsibility={a:1},evidence='verified'),dict(known_by=[a],observer=a,target='leader',responsibility={a:.4,'leader':.6},evidence='verified'),dict(known_by=[a],observer=a,target='leader',responsibility={},evidence='unknown'),dict(known_by=[],observer=a,target='leader',responsibility={'leader':1},evidence='verified'),dict(known_by=[a],observer='unrelated_A',target='unrelated_B',responsibility={'unrelated_B':1},evidence='verified')]
 for choice,presence,proof,event in itertools.product(n['choices'],['healthy','injured','withdrawn'],[False,True],events):
  out=render(nid,choice,presence,proof,event);rendered+=1
  if presence=='withdrawn':assert out['kind']=='letter' and not out['choice_applied'] and out['overlay'] is None
  elif choice=='integrated' and not proof:assert out['kind']=='unmet' and not out['choice_applied']
  else:
   assert out['choice_applied']
   if presence=='injured':assert out['lines'][0]==n['injured_opening'][0] and '本次只记录' in ''.join(out['lines'])
   if event is events[1]:assert out['overlay']=='other'
   if event is events[2]:assert out['overlay']=='self'
   if event is events[3]:assert out['overlay']=='shared'
   if event is events[4]:assert out['overlay']=='unknown'
   if event is events[5] or event is events[6]:assert out['overlay'] is None
 check('narrative',nid+' allpresence/proof/knowledge/responsibility combinations',True)
# Failure is visible and escapable, not a successful objective fabricated afterward.
g=fixture('lin',3);g.objects['r1']['prerequisites']=['task'];g.objects['task'].update(lost=True,done=False);g.propagate_unavailable()
check('dependency','Lostunfinishedparent makesdependentunavailable',g.objects['r1']['lost'] and g.objects['r1']['dependency_blocked'])
count=len(g.log);g.propagate_unavailable();check('dependency','No repeated notification for sameblockedchain',len(g.log)==count)
g=fixture('lin',3);g.objects['r1']['prerequisites']=['task'];g.objects['task'].update(lost=True,done=True);g.propagate_unavailable();check('dependency','Completedmilestoneisnotretroactivelyerased',not g.objects['r1']['lost'])
from policies import battle
p=['he','ye','chen'];g=battle(B['M12'],['backup','drive'],p,{'he':2,'ye':3,'chen':3},'mixed',['e'],gear={'medkit':0,'crowbar':0,'scanner':1,'med_dose':2},difficulty='standard',variant='A',delay=1);r=g.run()
check('dependency','ExactM12failedroute canretreatbeforelimitwithoutfakevictory',not r['success'] and r['healthy_extracted']==3 and r['rounds']<15 and 'drive' not in r['secured'])
# Transport attribution counts geometric progress, not presses of handoff button.
g=fixture('xu',5);g.h[1]['p']=(3,5);g.rows[4][3]='X';g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True,cell=[2,4]);g.use(0,'xu_1',destination=(4,4));actors=qualified(g,{'log':g.log},'r1',g.party)
check('contribution','Carriedrope supplies realtransportcredit','xu' in actors)
g.h[0]['ap']=2;g.use(0,'xu_1',destination=(2,4));actors=qualified(g,{'log':g.log},'r1',g.party);check('contribution','Outandbackrope cannotfarmtransportcredit','xu' not in actors)
g=fixture('jiang',3);g.h[1]['p']=(4,4);g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True,cell=[2,4]);g.use(0,'jiang_1',1);check('contribution','Extendedhandoffprogresscreditedtoactualmover','jiang' in qualified(g,{'log':g.log},'r1',g.party))
# Actual-paid refunds and the deployment boundary, including discounted parts.
for discount in [False,True]:
 g=RelationshipLedger('unusedbuy',external_social=True);g.day=4;g.phase='after_main';g.settled={f'M{i:02}' for i in range(1,5)};g.fac['workshop']=int(discount);start=deepcopy(g.resources);g.buy_tool('winch');g.undo_tool_purchase('winch')
 check('economy','Unusedpurchase refundexactpaid '+str(discount),g.resources==start and 'winch' not in g.tools and not g.discounts)
 check('economy','No repeatrefund '+str(discount),rejects(g,lambda:g.undo_tool_purchase('winch')))
 g.buy_tool('winch');g.phase='briefing';g.day=5;g.deploy('M05',['lin','xu','su']);check('economy','Departureclosesrefundwindow '+str(discount),rejects(g,lambda:g.undo_tool_purchase('winch')))
g=RelationshipLedger('initialtool');check('economy','Startertoolcannotgeneratecash',rejects(g,lambda:g.undo_tool_purchase('medkit')))
# NewL5effects have observable tactical consequences, not only prose.
def shield_pair(hp_override=None):
 g=fixture('he',5);g.h[0]['p']=(1,5);g.h[1]['p']=(2,6);g.h[2]['p']=(6,6);g.e['unit'].update(type='sentinel',p=(2,4),intent=[(2,5),(2,6)],disable_requires=[]);g.water_round=999;g.fire_round=999
 g.use(0,'he_1',destination=(2,5))
 if hp_override:g.barriers[(2,5)]['hp']=hp_override
 for rnd in [2,4]:g.rnd=rnd;g.environment()
 return g
old_shield=shield_pair(3);new_shield=shield_pair()
check('growth','L5He5HPshield absorbssecondknown3damagebeam',old_shield.h[1]['hp']==8 and new_shield.h[1]['hp']==11)
g=fixture('ye',5);g.h[0]['p']=(2,4);g.h[1]['p']=(4,4);g.h[2]['p']=(1,4);g.use(0,'ye_1','unit');check('growth','L5Yeisolatesstraight2awaywithoutsteppingintoedge',g.e['unit']['output_isolated'] and g.h[0]['ap']==0 and g.h[0]['p']==(2,4))
for obstacle in ['wall','ally']:
 g=fixture('ye',5)
 if obstacle=='wall':g.rows[3][2]='#'
 else:g.h[1]['p']=(2,3)
 check('growth','Extendedisolationcannotreachthrough '+obstacle,rejects(g,lambda:g.use(0,'ye_1','unit')))
g=fixture('ye',3);check('growth','L3Yestillneedsadjacency',rejects(g,lambda:g.use(0,'ye_1','unit')))
# Removed items cannot re-enter through commands; rejected mutations are atomic.
g=RelationshipLedger('retired inventory');g.day=20;g.phase='briefing';g.settled={f'M{i:02}' for i in range(1,20)};g.resources.update(credits=999,parts=99,supplies=99)
check('economy','Retiredcuttercannotbepurchased',rejects(g,lambda:g.buy_tool('cutter')))
check('economy','Retiredbatterycannotbecrafted',rejects(g,lambda:g.craft('battery',1)))
g.inventory['battery']=1
check('economy','Legacybatterycannotbepacked',rejects(g,lambda:g.deploy('M20',['lin','xu','su'],pack={'battery':1})))
# A specialty example ceases to move a hero once its own purpose has ended.
from opportunities import VisibleIsolation,OrdinaryField
for state in ['complete','failed','expired']:
 args=(B['M10'],['test1','test2'],['lin','su','ye'],{'lin':5,'su':5,'ye':5})
 a=VisibleIsolation(*args,behavior='cautious',style='controls',skills=True,extra=[],approach='independent',watchers=(0,1),difficulty='standard',variant='A')
 if state=='complete':a.service_done=True
 if state=='failed':a.service_failed=True
 if state=='expired':a.rnd=a.spec['deadline']+1
 b=deepcopy(a);a.publish();b.publish();a.policy();OrdinaryField.policy(b)
 check('guidance','ExpiredisolationexampledoesnotconsumeextraAP '+state,a.log==b.log and a.h==b.h)
(ROOT/'outputs/ordinary-player-checks.json').write_text(json.dumps(dict(version='0.16',passed=len(checks),checks=checks,dialogue_combinations=rendered,m12_fixed=dict(rounds=r['rounds'],healthy_extracted=r['healthy_extracted'],success=r['success']),scope='Previous482checks rerun plus actualchoice,publication,dependency,attribution,refundchecks and deterministicdialogue rendering. Not formal UI or human test.'),ensure_ascii=False,indent=2)+'\n');print('CHECKS',len(checks),'DIALOGUE',rendered,'M12',r['rounds'],r['healthy_extracted'])
