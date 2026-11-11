"""Named-party offline tactics. Canonical actions; bounded opportunistic planner.
Optional policy never means a skill is mandatory. Non-use is always a comparator.
"""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tactical-review'))
from actions import Lab,ABILITIES
from encounter import distance,adjacent,inside,Encounter
from copy import deepcopy
SITUATIONS=json.loads((Path(__file__).resolve().parents[2]/'game/data/final_design/progression_relationship.json').read_text())['situational_cooperation']

class Party(Lab):
 def __init__(self,board,goals,party,levels=None,skills=True,relations=None,agreements=False,**kw):
  levels=levels or {a:1 for a in party}
  super().__init__(board,goals,level=1,**kw);self.party=party;self.skills_enabled=skills;self.relations=relations or {};self.skill_failures=0;self.skill_actions=0;self.relation_refusals=0;self.allow_agreements=agreements
  for h,a in zip(self.h,party):
   lvl=levels[a];h.update(name=a,level=lvl,hp=10+int(lvl>=4)+int(lvl>=6),abilities=[f'{a}_1']+([f'{a}_3'] if lvl>=3 else []))
   if skills and a=='he' and lvl>=3:self.gear['he_3']=h['id']
 def usable(self,h,key):return self.skills_enabled and key in h['abilities'] and h['ap']>=ABILITIES[key]['ap'] and self.used.get((h['id'],key),0)<(ABILITIES[key]['charges_per_mission'] or 999)
 def spend(self,h,action,**kw):
  if action=='move' and h['carry'] is not None:kw['cargo']=h['carry']
  super().spend(h,action,**kw)
 def cooperation_blocked(self,a,b,tag):
  tags=set(ABILITIES[tag].get('tags',[]))
  for observer,target in [(a,b),(b,a)]:
   rule=SITUATIONS.get(observer,{})
   if tags&set(rule.get('protocol_tags',[])) and (self.relations.get((observer,target),False) or self.relations.get((observer,'leader'),False)):return True
  return False
 def cast(self,h,key,target=None,destination=None):
  if not self.usable(h,key):return False
  blocked=False
  if isinstance(target,int):blocked=self.cooperation_blocked(h['name'],self.h[target]['name'],key)
  if blocked and self.allow_agreements and key in ['su_3','xu_3','jiang_1']:
   self.agree(key,h['id'],target);blocked=False
  if blocked:self.relation_refusals+=1;self.receipt('cooperation_refused',actor=h['id'],target=target,skill=key,reason='需要本次动作的明确授权/接收者或人员物资优先约定')
  try:
   oid=h['carry'] if key=='jiang_1' else target if isinstance(target,str) and target in self.objects else None
   probe=deepcopy(self);probe.use(h['id'],key,target,destination,blocked=blocked)
   self.use(h['id'],key,target,destination,blocked=blocked)
   # Real specialty contributions must appear in the common outcome record.
   if oid and oid in self.objects and key in ['jiang_1','chen_3']:
    self.objects[oid]['contributions'].append(dict(actor=h['id'],action=key,round=self.rnd))
   self.skill_actions+=1;return True
  except AssertionError:self.skill_failures+=1;return False
 def execute_task(self,h,t):
  o=self.objects[t['target']]
  if self.skills_enabled and h['carry'] is None:
   if t['target'] in self.control_ids and distance(h['p'],o['p'])<=4 and len(t['route'])>1 and self.cast(h,'mo_1',o['id']):return True
   if t['action']=='stabilize' and o['kind']=='rescue':
    if distance(h['p'],o['p'])<=2 and self.cast(h,'lin_1',o['id']):return True
    path=t['route'];cost=sum(self.cost(p) for p in path[1:])
    if 0<cost<=2 and self.cast(h,'lin_3',o['id'],path[-1]):return True
   if len(t['route'])==1 and o['kind']=='work' and o['work']>o['progress']:
    # One-action cancellation is meaningful at the moment of threatened work.
    threat=next((x for x in self.e.values() if self.working(x) and h['p'] in x['intent']),None)
    if threat and h['ap']>=2:
     if self.cast(h,'chen_1',threat['id']) or self.cast(h,'ye_1',threat['id']):return True
   if len(t['route'])>1 and self.usable(h,'xu_1'):
    goal=t['route'][-1];oldcost=sum(self.cost(p) for p in t['route'][1:]);candidates=[]
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
     for n in [2,3]:
      p=(h['p'][0]+dx*n,h['p'][1]+dy*n)
      if not inside(p) or self.rows[p[1]][p[0]]!='.' or not self.passable(p) or self.occupied(p,h['id']):continue
      cells=[(h['p'][0]+dx*j,h['p'][1]+dy*j) for j in range(1,n)]
      if sum(self.rows[y][x] in '#X' for x,y in cells)!=1:continue
      tail=self.path(p,[goal],h)
      if tail:
       newcost=sum(self.cost(q) for q in tail[1:]);saving=oldcost-newcost
       if saving>3:candidates.append((newcost,p))
    if candidates and self.cast(h,'xu_1',destination=min(candidates)[1]):return True
  # Optional deliberate joint-work plan: walking the partner still spends real AP.
  if self.style=='joint' and self.gear.get('cooperation') and len(t['route'])==1 and o['kind']=='work' and o['work']-o['progress']>=3:
   pair=self.gear['cooperation_pair']
   if h['id'] in pair:
    other=next(a for a in self.h if a['id'] in pair and a['id']!=h['id'])
    if not other['down'] and not other['left'] and other['carry'] is None and other['ap']>=2 and distance(other['p'],h['p'])>1:
     route=self.path(other['p'],adjacent(h['p']),other)
     if route and sum(self.cost(p) for p in route[1:])<=self.budget(other):self.move(other,route)
  # Each character uses their own earned level, not a whole-team level shortcut.
  previous=self.level;self.level=h['level']
  try:return super().execute_task(h,t)
  finally:self.level=previous
 def policy(self):
  if self.skills_enabled:
   for h in self.h:
    if h['down'] or h['left'] or h['ap']<=0:continue
    if h['carry']:
     if self.usable(h,'jiang_1'):
      exits=lambda p:min(distance(p,x) for x in self.exits)
      receiver=next((a for a in self.alive() if a['id']!=h['id'] and a['carry'] is None and a['ap']==2 and distance(a['p'],h['p'])==1 and exits(a['p'])<exits(h['p'])),None)
      if receiver:self.cast(h,'jiang_1',receiver['id'])
     continue
    # Remote AP redistribution: another character already beside the switch.
    if self.usable(h,'mo_1') and self.style=='controls':
     control=next((o for o in self.objects.values() if o['id'] in self.control_ids and not o['done'] and self.working(self.e[o['disables']]) and distance(h['p'],o['p'])<=4 and distance(h['p'],o['p'])>1),None)
     if control:self.cast(h,'mo_1',control['id'])
    if self.usable(h,'su_1'):
     enemy=next((x for x in self.e.values() if self.working(x) and x['hp']==3 and any(a['id']!=h['id'] and a['ap']>=1 and distance(a['p'],x['p'])==1 for a in self.alive())),None)
     if enemy and self.style=='attack':self.cast(h,'su_1',enemy['id'])
    if self.usable(h,'su_3'):
     receiver=next((a for a in self.alive() if a['id']!=h['id'] and a['carry'] is not None and a['ap']>=1 and self.budget(a)<3 and distance(a['p'],h['p'])<=3),None)
     if receiver:self.cast(h,'su_3',receiver['id'])
    if self.usable(h,'he_1'):
     for enemy in self.e.values():
      threatened=[a for a in self.alive() if a['id']!=h['id'] and a['p'] in enemy['intent']]
      if not self.working(enemy) or enemy['type']!='sentinel' or not threatened:continue
      point=next((p for p in enemy['intent'] if distance(h['p'],p)==1 and self.passable(p) and not self.occupied(p) and distance(enemy['p'],p)<max(distance(enemy['p'],a['p']) for a in threatened)),None)
      if point and self.cast(h,'he_1',destination=point):break
  super().policy()
 def run(self):
  r=super().run();r.update(party=self.party,skills_enabled=self.skills_enabled,skill_actions=self.skill_actions,relation_refusals=self.relation_refusals,skill_action_types=sorted({x['action'] for x in self.log if x['action'] in ABILITIES}),levels={h['name']:h['level'] for h in self.h});return r
