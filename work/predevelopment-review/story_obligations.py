"""Current offline obligation evaluator, without rewriting historical evidence."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'work/final-design/verify_contracts.py').read_text().split('\ncases={')[0]
exec(compile(source,str(ROOT/'work/final-design/verify_contracts.py'),'exec'))
historical_verified=verified
def verified(actor,records,created=10,day=23):
 if actor!='he':return historical_verified(actor,records,created,day)
 r=[x for x in records if x['seq']>created]
 for mission in [x for x in r if x['kind']=='mission_settled']:
  if 'he' not in mission.get('actors',[]) or not mission.get('all_extracted'):continue
  same=[x for x in r if x.get('mission')==mission['mission']]
  work=any(x['kind']=='objective_completed' and set(x.get('contributors',[])) & (ACTORS-{'he'}) for x in same)
  protection=any(x['kind']=='protect_or_rescue' and x.get('actor')=='he' for x in same)
  if work and protection:return True
 return False
