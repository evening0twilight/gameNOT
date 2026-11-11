from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'work/ordinary-player-review/verify.py').read_text().split("(ROOT/'outputs/ordinary-player-checks.json').write_text")[0]
exec(compile(source,str(ROOT/'work/ordinary-player-review/verify.py'),'exec'))
base_count=len(checks)
# Natural XP, entry XP, thresholds and ordinary fatigue rules are unchanged.
old=json.loads((ROOT/'work/training-value-review/before/game/data/rules.json').read_text());new=json.loads((ROOT/'game/data/rules.json').read_text())
for key in ['levels','level_xp','xp_thresholds','main_xp_each_deployed','side_xp_each_deployed','support_xp','chapter_recruit_xp_floor']:
 if key in old['progression']:check('natural',key+' unchanged',new['progression'][key]==old['progression'][key])
check('natural','Allnontrainingprogressionfieldsunchanged',{k:v for k,v in new['progression'].items() if not k.startswith('training_')}=={k:v for k,v in old['progression'].items() if not k.startswith('training_')})
check('natural','Naturalrestunchanged',old['recovery']==new['recovery'])
def fresh(day=1):
 g=RelationshipLedger('training boundary',external_social=True);g.day=day;g.phase='camp';g.resources.update(supplies=20);return g
for who in CHARS:
 for day in range(CHARS[who]['join'],24):
  g=fresh(day);g.crew[who].update(joined=True,withdrawn=False,ready=1,xp=0,fatigue=0)
  slots=(day-1)//6-(CHARS[who]['join']-1)//6+1
  check('stages',who+' D'+str(day)+' recruitedstagesonly',g.training_slots(who)==slots)
  g.train([who]);check('stages',who+' D'+str(day)+' exactpaymentgain',g.resources['supplies']==19 and g.projects==1 and g.crew[who]['xp']==12 and g.crew[who]['fatigue']==6 and g.training_slots(who)==slots-1)
  check('stages',who+' D'+str(day)+' norepeatedsameevening',rejects(g,lambda:g.train([who])))
g=fresh(13);g.train(['lin']);g.day=14;g.projects=0;g.used.clear();g.train(['lin']);check('stages','Unusedearliercoursescarryacrosschapters',g.training_completed['lin']==2 and g.training_slots('lin')==1)
saved=roundtrip(g);check('stages','Savepreservescompletedstages',saved.training_completed==g.training_completed and saved.training_slots('lin')==1)
g=fresh(6);g.train(['lin']);g.day=7;g.projects=0;g.used.clear();check('stages','Newchapterunlocksoneadditionalstage',g.training_slots('lin')==1)
g=fresh(1);g.train(['lin']);g.day=2;g.used.clear();g.projects=0;check('stages','NoXPfarmwithinusedchapter',rejects(g,lambda:g.train(['lin'])))
for state in ['resources','project','injured','withdrawn','unjoined','maxxp','day24','notcamp','fatigue']:
 g=fresh()
 if state=='resources':g.resources['supplies']=0
 if state=='project':g.projects=2
 if state=='injured':g.crew['lin']['ready']=3
 if state=='withdrawn':g.crew['lin']['withdrawn']=True
 if state=='unjoined':g.crew['lin']['joined']=False
 if state=='maxxp':g.crew['lin']['xp']=100
 if state=='day24':g.day=24
 if state=='notcamp':g.phase='briefing'
 if state=='fatigue':g.crew['lin']['fatigue']=95
 check('atomic','Rejectedtraining '+state,rejects(g,lambda:g.train(['lin'])))
g=fresh();g.crew['lin']['xp']=97;g.train(['lin']);check('cap','Nearcapgains3not12',g.crew['lin']['xp']==100 and next(r for r in g.records if r['kind']=='training_gain')['gains']['lin']==3)
g=fresh();g.train(['lin','su']);check('cost','Twoparticipantsoneprojecttwosupplies',g.projects==1 and g.resources['supplies']==18 and g.training_completed==dict(lin=1,su=1))
g=fresh();check('atomic','Duplicatedparticipantrejected',rejects(g,lambda:g.train(['lin','lin'])))
# Training is not rest: same XP unlock can make the planned next duty unavailable.
g=fresh();g.crew['lin'].update(xp=66,fatigue=90);rest=deepcopy(g);g.train(['lin']);rest.recover(['lin']);train_next=g.crew['lin']['fatigue']-12;rest_next=rest.crew['lin']['fatigue']-12
check('fatigue','TrainingcanunlockL5yetblocknextduty',g.crew['lin']['xp']==78 and train_next+18>100 and rest_next+18<=100)
check('fatigue','Foregonerestmeans18fatiguedifference',train_next-rest_next==18)
# Carrying old courses does not create extra mentorships by changing partners.
g,pair=ledger();m,l=pair;g.crew[m]['xp']=60;before=deepcopy(g.rel);g.mentor(m,l)
check('mentor','24XPrealcostandsharedlearnerstage',g.crew[l]['xp']==44 and g.crew[m]['xp']==60 and g.resources['supplies']==18 and g.training_completed[l]==1 and g.crew[l]['fatigue']==6 and g.crew[m]['fatigue']==6 and g.rel==before)
g.day+=1;g.used.clear();g.projects=0;check('mentor','Existingchapterteachingcapretained',not any(x[1]==l for x in g.mentor_candidates()))
g,pair=ledger();m,l=pair;g.crew[m]['xp']=33;g.mentor(m,l);check('mentor','Cannotovertakementor',g.crew[l]['xp']==33)
g,pair=ledger();m,l=pair;g.crew[m]['xp']=32;check('mentor','Noexpensiveofferwhenordinary12isequal',not any(x[1]==l for x in g.mentor_candidates()))
g,pair=ledger();m,l=pair;g.crew[m]['xp']=80;g.training_completed[l]=g.training_slots(l);check('mentor','Cannotbypassspentstageswithdifferenttrainingmode',not any(x[1]==l for x in g.mentor_candidates()))
g=fresh();before=(deepcopy(g.rel),deepcopy(g.plans),deepcopy(g.evidence));g.train(['lin']);check('facts','Trainingdoesnotfabricatefieldexperience',(g.rel,g.plans,g.evidence)==before and not any(r['kind'] in ['objective_completed','casualty_saved','public_record_release'] for r in g.records))
# Constructor inputs must not leak trained passives into the comparison.
from policies import battle
gear={'crowbar':0,'medkit':0,'med_dose':1};party=['he','lin','xu'];a=battle(B['M12'],['backup','drive'],party,dict(he=3,lin=3,xu=3),'cautious',gear=gear);b=battle(B['M12'],['backup','drive'],party,dict(he=2,lin=3,xu=3),'cautious',gear=gear)
check('comparison','Battledoesnotmutateinputequipment','he_3' not in gear)
check('comparison','UntrainedHehasnotrainedpassive',a.gear.get('he_3')==0 and 'he_3' not in b.gear)
# Pure paid solo growth cannot replace the expedition progression entirely.
for who in CHARS:
 g=fresh(23);g.crew[who].update(joined=True,xp=[0,12,28,48][(CHARS[who]['join']-1)//6]);max_paid=g.training_slots(who)*12
 check('growth',who+' solotrainingalonebelowL5',g.crew[who]['xp']+max_paid<72)
(ROOT/'outputs/training-checks.json').write_text(json.dumps(dict(version='0.17',passed=len(checks),inherited=base_count,checks=checks),ensure_ascii=False,indent=2)+'\n');print('CHECKS',len(checks),'inherited',base_count)
