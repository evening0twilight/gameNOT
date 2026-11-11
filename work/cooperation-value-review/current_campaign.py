"""Four complete campaigns under current reduced production scope."""
from current_rules import *
import importlib.util
_spec=importlib.util.spec_from_file_location('value_campaign_adapter',ROOT/'work/cooperation-value-review/campaign.py')
c=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=c;_spec.loader.exec_module(c)
import inspect
c.Routes=CurrentRoutes;c.HeavyRoutes=CurrentHeavy;c.Z['ChoiceBattle']=CurrentBattle
class CurrentNoAdvancedHeavy(CurrentHeavy):
 def protocol_ready(self,key,a,b):
  return False if key in ['relay_carry','coordinated_pull'] else super().protocol_ready(key,a,b)
c.NoAdvancedHeavy=CurrentNoAdvancedHeavy
src=inspect.getsource(c.factory)
old=next(l for l in src.splitlines() if l.strip().startswith('pairs='))
src=src.replace(old,' pairs=list(itertools.combinations(range(3),2))').replace("MODE=='cultivate'",'True')
exec(compile(src,'current_campaign_factory','exec'),c.__dict__)
c.RUN.update(Party=c.factory)
def one(args):
 name,profile,opts=args
 c.MODE='ordinary';c.CACHE.clear();c.Z['PROFILE']=profile;c.ns['REPAIR']='none';c.ns['ADVANCED_PLAN']=False
 s=c.RUN['run'](name,**opts);assert not s['summary']['trained_protocols'];return s
if __name__=='__main__':
 from concurrent.futures import ProcessPoolExecutor
 import multiprocessing
 rows=[]
 cases=[('固定偏好与完整支线','protected',dict(fixed=True,sides=True)),('普通轮换与完整支线','safe',dict(sides=True)),('最高难度完整支线','protected',dict(hard=True,sides=True)),('最高难度连续失误','protected',dict(hard=True,disasters=(6,7,8,15)))]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  for s in pool.map(one,cases):
   rows.append(s);q=s['summary'];print(q['name'],q['main_count'],q['side_count'],q['resources'],flush=True)
 (ROOT/'outputs/cooperation-current-campaign.json').write_text(json.dumps(dict(version='0.12-current',scope='Four current-scope earned campaigns; retained ordinary choices compete with free situational cooperation. Character progression, dates, inventory and concrete relationship restrictions remain real. Hindsight policy search is not player observation.',scenarios=rows,actual_battles=sum(len(s['battles']) for s in rows)),ensure_ascii=False,indent=2)+'\n')
