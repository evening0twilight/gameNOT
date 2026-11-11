from pathlib import Path
import sys,json,multiprocessing
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
import campaign_review as old
from campaign_review import *
EC=json.loads((ROOT/'game/data/campaign_economy_contract.json').read_text());FACS={x['id']:x for x in json.loads((ROOT/'game/data/final_design/facilities.json').read_text())}
# Acquired gear is passed into actual battles; each choice respects slots.
def factory(board,goals,party,levels=None,**kw):
 g=c.Z['ACTIVE'];gear=deepcopy(kw.get('gear',{}))
 if CFG.get('investment')=='tools':
  gear['crowbar']=0
  if 'scanner' in g.tools:gear['scanner']=1
  if 'stretcher' in g.tools:gear['stretcher']=2
 kw['gear']=gear;return old.factory(board,goals,party,levels,**kw)
def prepare(g):
 if CFG.get('investment')!='tools':return
 for item in ['scanner','stretcher']:
  e=EQUIPMENT[item]
  if item not in g.tools and g.day>e['unlocked_after_main'] and g.resources['credits']>=e['price_credits']+14 and g.resources['parts']>=e['price_parts']:g.buy_tool(item)
def camp(g):
 kind=CFG.get('investment')
 if kind in ['medical','facilities'] and g.projects<2:
  queue=['infirmary','infirmary','workshop','workshop'] if kind=='medical' else ['rest_area','communications','communications','workshop','workshop','infirmary','infirmary','rest_area']
  # Buy only when it remains possible to pay both authored financial commitments.
  for f in queue:
   if g.fac[f]>=queue.count(f):continue
   cost=FACS[f]['costs'][g.fac[f]]
   if g.resources['credits']>=cost[0]+14 and g.resources['parts']>=cost[1]:g.upgrade(f)
   break
 old.training(g)
RUN.update(Party=factory,prepare_day=prepare,training_and_repairs=camp)
def runone(args):return old.one(args)
if __name__=='__main__':
 cases=[
 ('固定队伍全36关/临界训练',dict(training='targeted',formation='fixed'),dict(fixed=True,sides=True)),
 ('轮换全36关/选择性培养与M22接应',dict(training='selective',formation='flex',pacts=True,dock=True,dock_days=[22]),dict(sides=True)),
 ('轮换仅24主线/不额外购工具',dict(training='targeted',formation='flex'),dict()),
 ('轮换仅24主线/购买工具',dict(training='targeted',formation='flex',investment='tools'),dict()),
 ('全36关/设施优先',dict(training='targeted',formation='flex',investment='facilities'),dict(sides=True)),
 ('全36关/医疗设施优先',dict(training='targeted',formation='flex',investment='medical'),dict(sides=True)),
 ('最高难度全36关',dict(training='targeted',formation='flex',pacts=True),dict(hard=True,sides=True)),
 ('最高难度五次失误含终战',dict(training='selective',formation='flex',pacts=True),dict(hard=True,disasters=(6,7,8,15,24)))]
 with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('fork')) as pool:
  rows=[]
  for r in pool.map(runone,cases):
   rows.append(r);q=r['summary'];print(q['name'],q['resources'],q['facilities'],q['world_ending'],flush=True)
 (ROOT/'outputs/player-ready-campaigns.json').write_text(json.dumps(dict(version='0.15',scenarios=rows,actual_battles=sum(len(r['battles']) for r in rows),scope='Eight actual earned-state campaigns, with optional purchase policies and all real costs. Medical investment buys capacity only; dose use sensitivity is separately tested, not falsely claimed here.'),ensure_ascii=False,indent=2)+'\n')
