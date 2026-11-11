"""Prespecified player intent: use specialty for own profession, no outcome ranking."""
from policies import *
class SpecialtyRules:
 def policy(self):
  # Protect the next visible wet segment while advancing; only when an active
  # electrical source exists. Costs and geometry remain canonical.
  if any(e['type']=='skimmer' and self.working(e) for e in self.e.values()):
   for h in self.alive():
    if h['name']!='ye' or h['carry'] or not self.usable(h,'ye_3'):continue
    targets=[self.task_action(h,k) for k in sorted(self.wanted) if k in self.objects and not self.objects[k]['lost'] and not self.objects[k]['secured']]
    targets=[t for t in targets if t and len(t.get('route',[]))>1]
    if targets:
     t=min(targets,key=lambda t:t['steps']);p=t['route'][1]
     if self.rows[p[1]][p[0]]=='~' and p not in self.insulated:self.cast(h,'ye_3',destination=p)
  return super().policy()
class SpecialtyBattle(SpecialtyRules,OrdinaryBattle):pass
class SpecialtyField(SpecialtyRules,OrdinaryField):pass
def specialty_battle(board,goals,party,levels,behavior,extra=(),service=False,focus=None,**kw):
 style='controls' if focus in ['chen','mo'] else 'rush';role='rope' if focus=='xu' else 'protect'
 kw.update(style=style,skills=True,extra=list(extra),behavior=behavior,role_policy=role)
 if service and board['id'] in CONTRACT['services']:
  g=SpecialtyField(board,goals,party,levels,approach='independent',watchers=tuple(range(len(CONTRACT['services'][board['id']]['posts']))),**kw)
 else:
  alloc={}
  if focus in party and focus in ['lin','xu','he','jiang']:
   target=next((o['id'] for o in board['objectives'] if o['id'] in list(goals)+list(extra) and o['kind'] in ['rescue','cargo']),None)
   if target:alloc[target]=party.index(focus)
  g=SpecialtyBattle(board,goals,party,levels,allocation=alloc,priority='cargo',**kw)
 return g
