from pathlib import Path
p=Path(__file__).resolve().parents[2]/'work/growth-identity-review/model.py';s=p.read_text()
needle=' def execute_task(self,h,t):\n'
addition=""" def cast(self,h,key,target=None,destination=None):
  # Automated policy chooses the remaining legal mode explicitly. Direct UI/use
  # commands never silently change an AP request into a movement request.
  if key=='su_3' and h['level']>=5 and self.used.get(('ap_transfer_mission',h['id'])) and destination is None:destination='movement'
  return super().cast(h,key,target,destination)
 def execute_task(self,h,t):
  if h['carry'] is None and t['target'] in self.control_ids and distance(h['p'],self.objects[t['target']]['p'])<=5 and len(t['route'])>1 and self.cast(h,'mo_1',t['target']):return True
"""
if 'Automated policy chooses' not in s:s=s.replace(needle,addition)
needle=' def move(self,h,route):\n'
addition=""" def move(self,h,route):
  if self.role_policy=='rope' and h['name']=='xu' and h['level']>=5 and h['carry'] and self.usable(h,'xu_1'):
   original=sum(self.cost(p) for p in route[1:]);candidates=[]
   for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
    for length in [2,3]:
     p=(h['p'][0]+dx*length,h['p'][1]+dy*length)
     if not (0<=p[0]<8 and 0<=p[1]<8) or self.rows[p[1]][p[0]]!='.' or not self.passable(p) or self.occupied(p,h['id']):continue
     path=self.path(p,[route[-1]],h,carry=True)
     if path and sum(self.cost(v) for v in path[1:])+self.budget(h)<original:candidates.append((sum(self.cost(v) for v in path[1:]),p))
   for _,p in sorted(candidates):
    if self.cast(h,'xu_1',destination=p):return True
"""
if 'original=sum(self.cost' not in s:s=s.replace(needle,addition)
p.write_text(s)
p=Path(__file__).with_name('matrix.py');s=p.read_text();s=s if "plans.append((allocation,priority,style,'rope'))" in s else s.replace("out=dict(mission=row['mission']", "allocation,priority,style,_=plans[0];plans.append((allocation,priority,style,'rope'))\n out=dict(mission=row['mission']");p.write_text(s)
