"""Offline route-policy search. No production game implementation.

Task priorities are search parameters, never character stat changes. All movement,
AP, deadlines and outcomes use the existing referee. Search is bounded, not optimal.
"""
from pathlib import Path
from copy import deepcopy
import sys,json,itertools
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/player-choice-review'))
from choices import ChoiceBattle,distance,adjacent,CONTRACT
from encounter_choices import extras
from social import CHARS,INITIAL,Social
B={b['id']:b for b in json.loads((ROOT/'game/data/final_design/boards.json').read_text())['boards']}
T={(r['observer'],r['target']):r['trust'] for r in INITIAL}

class Routes(ChoiceBattle):
 def __init__(self,*a,allocation=None,priority='balanced',exchange='none',pair=(0,2),**kw):
  self.allocation=allocation or {};self.priority=priority;self.exchange=exchange;self.pair=pair;self.transferred=set()
  super().__init__(*a,**kw)
 def task_action(self,h,k):
  t=super().task_action(h,k)
  if not t:return t
  # Bias the inherited planner, without changing the physical route/action.
  if k in self.allocation:
   owner=self.allocation[k];other=self.h[owner]
   if not other['down'] and not other['left']:
    t['steps']+=-9 if owner==h['id'] else 9
  o=self.objects[k]
  if self.priority=='deadline' and o.get('opportunity_deadline'):
   t['steps']-=12
  elif self.priority=='cargo' and o['kind'] in ['rescue','cargo']:t['steps']-=3
  return t
 def transfer(self,h):
  if self.exchange=='none' or h['carry'] is None:return False
  oid=h['carry']
  if (oid,self.rnd) in self.transferred:return False
  for y in self.alive():
   if y is h or y['carry'] or distance(h['p'],y['p'])!=1 or y['ap']<1:continue
   if self.exchange=='advanced' and {h['id'],y['id']}!=set(self.pair):continue
   # Receiver must be no farther from evacuation; no gratuitous passing loops.
   exit_d=lambda x:min(distance(x['p'],p) for p in self.exits)
   if exit_d(y)>exit_d(h) or (h['ap']>y['ap'] and self.exchange!='advanced'):continue
   route=self.path(y['p'],self.exits,y,True)
   if not route:continue
   if self.exchange=='advanced':
    if h['ap']<1 or not self.protocol_ready('relay_carry',h['id'],y['id']):continue
    cost=0;path=[route[0]]
    for p in route[1:]:
     if cost+self.cost(p)>3:break
     cost+=self.cost(p);path.append(p)
    while len(path)>1 and self.occupied(path[-1],y['id']):path.pop()
    if len(path)<2:continue
    self.relay_path(h['id'],y['id'],path)
   else:
    # Ordinary drop is free, receiving costs 1 AP; walking is separate.
    self.transferred.add((oid,self.rnd))
    h['carry']=None;y['carry']=oid;self.objects[oid]['carrier']=y['id'];self.objects[oid]['p']=h['p']
    self.receipt('drop',actor=h['id'],target=oid,at=h['p']);self.spend(y,'pickup',target=oid)
    if y['ap'] and len(route)>1:self.move(y,route)
   self.transferred.add((oid,self.rnd));return True
  return False
 def move(self,h,route):
  if h['carry'] and self.transfer(h):return True
  return super().move(h,route)

class HeavyRoutes(Routes):
 """A deliberate cut/move/relocate plan, usable on any heavy-machine map.
 A costly plan can lose to shutdown or simply routing around the machine.
 """
 def __init__(self,*a,heavy_mode='pull',**kw):
  super().__init__(*a,**kw);self.heavy_mode=heavy_mode;self.heavy_done=False
  self.heavy_target=next((e['id'] for e in self.e.values() if e['type'] in ['hauler','sentinel']),None)
 def policy(self):
  if self.heavy_done or not self.heavy_target:return super().policy()
  e=self.e[self.heavy_target];x,y=[self.h[i] for i in self.pair]
  if any(h['left'] or h['down'] or h['carry'] for h in [x,y]) or e['hp']<=0:
   self.heavy_done=True;return super().policy()
  cut=next((k for k in e['disable_requires'] if not self.objects[k]['done']),None)
  if cut:
   for _ in range(2):
    if y['ap']<1:break
    t=super().task_action(y,cut)
    if t:self.execute_task(y,t)
  else:
   cells=[p for p in adjacent(e['p']) if self.passable(p) and (not self.occupied(p) or p in [x['p'],y['p']])]
   targets=[p for p in cells if not self.occupied(p) and p not in list(map(tuple,e.get('rail') or []))]
   if self.heavy_mode=='push':
    targets=[p for p in targets if (2*e['p'][0]-p[0],2*e['p'][1]-p[1]) in cells]
   if not targets:self.heavy_done=True
   else:
    dest=targets[0]
    if self.heavy_mode=='pull':
     positions=[p for p in cells if p!=dest]
     if len(positions)<2:self.heavy_done=True
     else:
      positions=sorted(positions,key=lambda p:(distance(x['p'],p),p))[:2]
      for h,p in zip([x,y],positions):
       for _ in range(2):
        if h['ap']<1 or h['p']==p or not self.move_to(h,[p]):break
      if all(h['p']==p for h,p in zip([x,y],positions)) and min(x['ap'],y['ap'])>=1 and self.protocol_ready('coordinated_pull',x['id'],y['id']):
       self.precise_pull(x['id'],y['id'],e['id'],dest);self.heavy_done=True
    else:
     p=(2*e['p'][0]-dest[0],2*e['p'][1]-dest[1])
     if x['p']!=p and x['ap']:self.move_to(x,[p])
     if x['p']==p and x['ap']>=2:
      self.basic_push(x['id'],e['id']);self.basic_push(x['id'],e['id']);self.heavy_done=True
  if self.heavy_done:return super().policy()
  saved={h['id']:h['ap'] for h in [x,y]}
  for h in [x,y]:h['ap']=0
  super().policy()
  for i,ap in saved.items():self.h[i]['ap']=ap

def configurations(board,goals,dense=False):
 ids=sorted(extras(board,goals)|set(goals))
 # Enumerate all 3^n owner assignments on small maps in the focused search.
 if dense and len(ids)<=5:
  owners=itertools.product(range(3),repeat=len(ids))
 else:
  owners=[tuple(p[i%3] for i in range(len(ids))) for p in itertools.permutations(range(3))]
 plans=[({},'balanced','rush'),({},'balanced','controls'),({},'deadline','optional_first'),({},'balanced','attack')]
 for owner in owners:
  allocation=dict(zip(ids,owner))
  plans.append((allocation,'balanced','rush'))
  if dense:plans.append((allocation,'deadline','controls'))
 return plans

def compact(r):
 return {k:v for k,v in r.items() if k not in ['used','log','service_ticks']}

def dominates(a,b,costs=False):
 # No scalar "fun" score. Keep different outcomes and injury/speed tradeoffs.
 if not a['success'] or not set(a['secured'])>=set(b['secured']):return False
 keys=['downed','damage','rounds','ap']
 if any(a[k]>b[k] for k in keys):return False
 if not a.get('machinery_intact',True) and b.get('machinery_intact',True):return False
 return any(a[k]<b[k] for k in keys) or set(a['secured'])>set(b['secured']) or costs

def rank(r):return (not r['success'],-len(r['secured']),r['downed'],r['damage'],r['rounds'],r['ap'])

def execute(board,goals,party,levels,plan,skills=True,exchange='none',pair=(0,2),gear=None,trust=None,trained=None,relations=None,difficulty='standard',variant='A',heavy=None):
 allocation,priority,style=plan
 trust=trust if trust is not None else T
 trained=trained if trained is not None else [tuple(sorted([party[pair[0]],party[pair[1]]]))+(k,) for k in ['relay_carry','coordinated_pull']]
 cls=HeavyRoutes if heavy else Routes
 g=cls(board,goals,list(party),levels,skills=skills,style=style,extra=extras(board,goals),allocation=allocation,priority=priority,exchange=exchange,pair=pair,trained=trained,trust=trust,relations=relations,gear=deepcopy(gear or {}),difficulty=difficulty,variant=variant,**({'heavy_mode':heavy} if heavy else {}))
 r=g.run();r['plan']=dict(allocation=allocation,priority=priority,style=style,exchange=exchange,pair=pair)
 return g,r

if __name__=='__main__':
 party=['lin','xu','su'];board=B['M06'];goals=['r1','r2'];levels={a:2 for a in party};runs=[]
 for plan in configurations(board,goals,True):
  for skills in [False,True]:
   for exchange in ['none','ordinary','advanced']:
    g,r=execute(board,goals,party,levels,plan,skills,exchange);runs.append(r)
 for mode in ['none','ordinary','advanced']:
  rr=sorted([r for r in runs if r['plan']['exchange']==mode],key=rank)
  print(mode,len(rr),[(r['rounds'],r['damage'],r['ap'],r['secured'],r['plan'],r['skill_action_types']) for r in rr[:2]],flush=True)
 (ROOT/'outputs/cooperation-route-pilot.json').write_text(json.dumps([compact(r)|{'log':r['log']} for r in sorted(runs,key=rank)[:12]],ensure_ascii=False,indent=2))
