from routes import *
import importlib.util
_spec=importlib.util.spec_from_file_location('value_campaign_adapter',ROOT/'work/cooperation-value-review/campaign.py')
c=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=c;_spec.loader.exec_module(c)
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
def one(arg):
 name,mode,opts=arg;c.MODE=mode;c.CACHE.clear();c.Z['PROFILE']='safe';c.ns['REPAIR']='none';c.ns['ADVANCED_PLAN']=False
 return c.RUN['run'](name+'_'+mode,**opts)
if __name__=='__main__':
 cases=[(name,mode,opts) for name,opts in [('fixed',dict(fixed=True,sides=True)),('rotate',dict(sides=True)),('hard',dict(hard=True,sides=True)),('setbacks',dict(hard=True,disasters=(6,7,8,15)))] for mode in ['ordinary','cultivate','trained_no_actions']]
 rows=[]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  for s in pool.map(one,cases):
   rows.append(s);q=s['summary'];print(q['name'],sum(q['xp'].values()),q['resources'],sum(r['kind']=='advanced_actions_used' for r in s['receipts']),flush=True)
 for name,subset in [('cooperation-value-campaign.json',[r for r in rows if not r['summary']['name'].endswith('trained_no_actions')]),('cooperation-equal-training-controls.json',[r for r in rows if r['summary']['name'].endswith('trained_no_actions')])]:
  (ROOT/'outputs'/name).write_text(json.dumps(dict(version='0.12-audit',scope='Matched real24dayledgers. All arms include the same ordinary assignment, handoff, shutdown and heavy-setup movements; cultivated arm adds only actually earned cooperation. Same-training disabled-command control isolates growth effects. Hindsight candidate selection, not human play.',scenarios=subset,actual_battles=sum(len(s['battles']) for s in subset)),ensure_ascii=False,indent=2)+'\n')
