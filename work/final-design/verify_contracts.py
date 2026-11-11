"""Executable verification for story obligations; only authenticated game receipts may enter it."""
from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[2]
ACTORS={'lin','xu','su','chen','ye','he','mo','jiang'}
def verified(actor,records,created=10,day=23):
 r=[x for x in records if x['seq']>created]
 def rows(kind):return [x for x in r if x['kind']==kind]
 if actor=='lin':return any(x.get('mission_kind')=='main' and len(set(x.get('contributors',[])))>=2 and set(x['contributors'])-{'lin'} for x in rows('casualty_saved'))
 if actor=='xu':
  return any('xu' in m.get('actors',[]) and m.get('xu_standing_on_exit') and any(p.get('mission')==m['mission'] and p.get('kept') for p in rows('retreat_promise')) for m in rows('mission_settled'))
 if actor=='su':
  duties=sorted([x for x in rows('assignment') if x.get('mission_kind')=='main'],key=lambda x:(x['day'],x['seq']))[:2]
  return len(duties)==2 and len({x['mission'] for x in duties})==2 and all(x.get('support')!='su' for x in duties) and any(x.get('support') in ACTORS-{'su'} and any(w.get('mission')==x['mission'] and w.get('actor')==x['support'] for w in rows('support_work')) for x in duties)
 if actor=='chen':return any(x.get('purpose')=='chen_compensation' and x.get('amount')==8 for x in rows('payment')) and any(x.get('mission_kind')=='main' and x.get('type')=='work' and 'engineering' in x.get('tags',[]) and 'chen' in x.get('contributors',[]) for x in rows('objective_completed')) and any(x.get('actor')=='ye' and x.get('fact')=='chen_signed_responsibility' for x in rows('known_information'))
 if actor=='ye':return any(x['kind']=='evidence_verified' and x.get('id')=='E_MAINTENANCE' for x in records) and any(x.get('actor')=='ye' and x.get('fact')=='maintenance_audit' for x in rows('known_information'))
 if actor=='he':return any('he' in m.get('actors',[]) and m.get('all_extracted') and any(x.get('mission')==m['mission'] and x.get('primary_contributor') in ACTORS-{'he'} for x in rows('objective_completed')) and any(x.get('mission')==m['mission'] and x.get('actor')=='he' for x in rows('protect_or_rescue')) for m in rows('mission_settled'))
 if actor=='mo':return not any(x.get('privacy')=='unredacted' for x in rows('public_record_release')) and (any(x.get('privacy')=='redacted' for x in rows('public_record_release')) or any(x.get('mission')=='M22' and x.get('object')=='privacy' for x in rows('objective_completed')))
 if actor=='jiang':return day>=23 and any(x.get('purpose')=='jiang_wages' and x.get('amount')==6 for x in rows('payment')) and not any(x.get('scope')=='jiang_personnel_priority' for x in rows('promise_breach'))
 raise ValueError(actor)
def ending(choice,absent=False,verified_at=0,breach_at=0,repaired_at=0):
 if absent:return 'medical_withdrawal'
 if choice=='integrated' and breach_at>max(verified_at,repaired_at):return 'professional_ruptured_after_progress'
 return choice or 'professional_unresolved'
def R(kind,seq=11,**kw):return dict(kind=kind,seq=seq,**kw)
cases={
'lin':[R('casualty_saved',mission='M09',mission_kind='main',contributors=['lin','su'])],
'xu':[R('mission_settled',mission='M11',actors=['xu'],xu_standing_on_exit=True),R('retreat_promise',seq=12,mission='M11',kept=True)],
'su':[R('assignment',mission='M12',mission_kind='main',day=12,support='chen'),R('assignment',seq=12,mission='M13',mission_kind='main',day=13,support=None),R('support_work',seq=13,mission='M12',actor='chen')],
'chen':[R('payment',purpose='chen_compensation',amount=8),R('objective_completed',seq=12,mission_kind='main',type='work',tags=['engineering'],contributors=['chen']),R('known_information',seq=13,actor='ye',fact='chen_signed_responsibility')],
'ye':[R('evidence_verified',seq=4,id='E_MAINTENANCE'),R('known_information',actor='ye',fact='maintenance_audit')],
'he':[R('mission_settled',mission='M17',actors=['he','su'],all_extracted=True),R('objective_completed',seq=12,mission='M17',primary_contributor='su'),R('protect_or_rescue',seq=13,mission='M17',actor='he')],
'mo':[R('public_record_release',privacy='redacted')],
'jiang':[R('payment',purpose='jiang_wages',amount=6)]}
checks=[]
def check(name,ok):
 assert ok,name;checks.append(name)
for a,receipts in cases.items():
 check(a+' actual evidence completes obligation',bool(verified(a,receipts)))
 check(a+' empty evidence cannot complete obligation',not verified(a,[]))
 for i in range(len(receipts)):
  check(a+f' missing required receipt {i} rejects completion',not verified(a,receipts[:i]+receipts[i+1:]))
 if a!='ye':
  old=copy.deepcopy(receipts)
  for x in old:x['seq']=1
  check(a+' unrelated pre-promise deeds cannot backfill obligation',not verified(a,old))
wrong=copy.deepcopy(cases['xu']);wrong[1]['mission']='M99';check('xu promise and retreat must be same mission',not verified('xu',wrong))
wrong=copy.deepcopy(cases['he']);wrong[2]['mission']='M99';check('he cooperation cannot combine unrelated missions',not verified('he',wrong))
wrong=copy.deepcopy(cases['lin']);wrong[0]['contributors']=['lin','lin'];check('duplicate contributor is not two people',not verified('lin',wrong))
check('mo later unredacted release invalidates promise',not verified('mo',cases['mo']+[R('public_record_release',seq=20,privacy='unredacted')]))
check('jiang waits until explicit final audit day',not verified('jiang',cases['jiang'],day=22))
check('jiang cannot substitute another payment purpose',not verified('jiang',[R('payment',purpose='chen_compensation',amount=6)]))
check('later betrayal changes an earlier warm ending',ending('integrated',verified_at=15,breach_at=20)=='professional_ruptured_after_progress')
check('later actual restitution can restore the ending',ending('integrated',verified_at=15,breach_at=20,repaired_at=22)=='integrated')
check('withdrawal always overrides restored relationship',ending('integrated',absent=True,verified_at=15,breach_at=20,repaired_at=22)=='medical_withdrawal')
check('professional choice respected even if proof obtained',ending('professional',verified_at=22)=='professional')
report={'checks':checks,'passed_count':len(checks),'valid_examples':cases,'boundary':'Receipt authenticity, actor authority and atomic issue are runtime requirements; this reference evaluates supplied receipts, not an implemented event bus.'}
(ROOT/'outputs/story-contract-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Story obligation and ending checks:',len(checks))
