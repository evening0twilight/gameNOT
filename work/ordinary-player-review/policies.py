"""Single committed, local-information policies. Never rank completed trial outcomes."""
from pathlib import Path
import sys,json,itertools
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
from model import *
PROFILES={
 'main_only':dict(style='rush',optional='none',mistake='none',formation='fixed',training='none',support=False),
 'cautious':dict(style='controls',optional='one',mistake='detour',formation='rotate',training='targeted',support=True),
 'collector':dict(style='optional_first',optional='all',mistake='hesitate',formation='fixed',training='habit',support=True),
 'favorite':dict(style='rush',optional='one',mistake='late',formation='favorite',training='favorite',support=False),
 'dismantler':dict(style='attack',optional='all',mistake='none',formation='rotate',training='none',support=True),
 'mixed':dict(style='rush',optional='one',mistake='hesitate',formation='rotate',training='targeted',support=True),
}
class OrdinaryRules:
 def __init__(self,*a,behavior='main_only',medicine=True,**kw):
  self.behavior=behavior;self.medicine=medicine;self.mistake_tokens=set();super().__init__(*a,**kw)
 def policy(self):
  cfg=PROFILES[self.behavior]
  if self.medicine and self.used.get('med_dose',0)<self.gear.get('med_dose',0):
   for h in list(self.alive()):
    if h['ap']<1:continue
    targets=sorted([y for y in self.alive() if distance(h['p'],y['p'])<=1 and y['hp']<=7],key=lambda y:y['hp'])
    for y in targets:
     key='jiang_3' if h['name']=='jiang' and h['level']>=3 and h['carry'] else 'medkit'
     try:self.use(h['id'],key,y['id']);break
     except AssertionError:pass
  if cfg['mistake']=='detour' and self.rnd==1 and 'detour' not in self.mistake_tokens:
   self.mistake_tokens.add('detour');h=self.h[0]
   places=[p for p in adjacent(h['p']) if self.passable(p) and not self.occupied(p) and self.cost(p)<=self.budget(h)]
   if places and h['ap']:
    target=next(iter(sorted(self.goals)));goal=self.objects[target]['p'];p=max(places,key=lambda p:distance(p,goal));self.move(h,[h['p'],p])
  if cfg['mistake']=='hesitate' and self.rnd in [2,4] and self.rnd not in self.mistake_tokens:
   self.mistake_tokens.add(self.rnd);h=self.h[self.rnd%3]
   if not h['down'] and not h['left'] and h['ap']:self.spend(h,'hesitate',reason='重新查看任务/错误操作后浪费本次行动，受控行为假设')
  if cfg['mistake']=='late':
   for h in self.alive():
    token=('late_exit',h['id'])
    if token in self.mistake_tokens or h['p'] not in self.exits:continue
    if not all(o['secured'] or o['lost'] or k==h['carry'] for k,o in self.objects.items() if k in self.wanted):continue
    self.mistake_tokens.add(token)
    while h['ap']:self.spend(h,'hesitate_exit',reason='已到撤离点但多等一轮')
  return super().policy()
class OrdinaryBattle(OrdinaryRules,IdentityRoutes):pass
class OrdinaryField(OrdinaryRules,IdentityBattle):pass

def goal_variants(board):
 for branch,groups in board.get('route_groups',{'default':board['mandatory_groups']}).items():
  for goals in itertools.product(*groups):
   branch=('isolate' if 'isolate' in goals else 'repair') if board['id']=='M17' else branch
   yield branch,tuple(goals)
def extra_sets(board,goals,branch):
 ids={o['id'] for o in board['objectives']};objects={o['id']:o for o in board['objectives']};required=set(goals)
 def deps(k):
  for p in objects[k]['prerequisites']:
   if p not in required:required.add(p);deps(p)
 for k in goals:deps(k)
 if board['id']=='M17':ids-=({'repair1','repair2'} if branch=='isolate' else {'isolate'})
 if board['id']=='M24':ids=set(goals)|{'archive'}
 optional=sorted(ids-required)
 for n in range(len(optional)+1):
  for subset in itertools.combinations(optional,n):yield tuple(subset)
def battle(board,goals,party,levels,behavior,extra=(),service=False,**kw):
 cfg=PROFILES[behavior];kw.update(style=cfg['style'],skills=True,extra=list(extra),behavior=behavior,role_policy='protect' if behavior=='cautious' else 'rope' if behavior=='favorite' else 'none')
 if service and board['id'] in CONTRACT['services']:
  n=len(CONTRACT['services'][board['id']]['posts']);return OrdinaryField(board,goals,party,levels,approach='independent',watchers=tuple(range(n)),**kw)
 return OrdinaryBattle(board,goals,party,levels,**kw)
