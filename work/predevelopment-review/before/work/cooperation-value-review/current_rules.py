"""0.12 OFFLINE reference adapter; the Godot product remains untouched."""
from routes import *
import encounter_choices as historical
from actions import ABILITIES
SCOPE=json.loads((ROOT/'game/data/final_design/production_scope.json').read_text())
class ScopeRules:
 def __init__(self,*a,**kw):
  assert not set(kw.get('gear',{}))&set(SCOPE['retired_equipment'])
  super().__init__(*a,**kw)
 def budget(self,h):
  if h['carry'] is not None:
   return min(3,(3 if self.gear.get('stretcher')==h['id'] or self.gear.get('he_3')==h['id'] else 2)+h.get('move_bonus',0))
  earned=h['level']>=6 or h['level']>=2 and self.gear.get('growth_move',False)
  return min(4,3+max(h.get('move_bonus',0),int(earned and h['first_move'])))
 def execute_task(self,h,t):
  # AtL6 the second passive is earned too, rather than silently retaining the
  # whole-party level1 movement placeholder from the historical referee.
  old=self.gear.get('growth_move');present='growth_move' in self.gear
  if h['level']>=6:self.gear['growth_move']=False
  try:return super().execute_task(h,t)
  finally:
   if present:self.gear['growth_move']=old
   else:self.gear.pop('growth_move',None)
 def protocol_ready(self,key,a,b):
  return historical.ChoiceBattle.protocol_ready(self,key,a,b,require_training=False)
 def usable(self,h,key):
  if key not in SCOPE['abilities']:return False
  spec=ABILITIES[key];limit=spec['charges_per_mission']
  if limit and spec['level']==1 and h['level']>=5:limit+=1
  return self.skills_enabled and key in h['abilities'] and h['ap']>=spec['ap'] and self.used.get((h['id'],key),0)<(limit or 999)
 def use(self,actor,key,*a,**kw):
  assert key in SCOPE['abilities'] or key in SCOPE['equipment'],'Retired effect is not a current command'
  spec=ABILITIES.get(key);before=spec['charges_per_mission'] if spec else None
  if spec and before and spec['level']==1 and self.h[actor]['level']>=5:spec['charges_per_mission']=before+1
  try:return super().use(actor,key,*a,**kw)
  finally:
   if spec:spec['charges_per_mission']=before
class CurrentRoutes(ScopeRules,Routes):pass
class CurrentHeavy(ScopeRules,HeavyRoutes):pass
class CurrentBattle(ScopeRules,ChoiceBattle):pass
