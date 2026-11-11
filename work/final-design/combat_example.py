"""Executable M02 reference encounter: real AP, collision, scout intent, work and evacuation.
Only this encounter's action subset is implemented; not a general combat engine.
"""
from pathlib import Path
import json,heapq,copy
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
B=next(b for b in json.loads((D/'boards.json').read_text())['boards'] if b['id']=='M02')
def play(style):
 heroes={k:dict(p=tuple(p),hp=10,ap=0,left=False,first_work=True) for k,p in zip(['A','B','C'],B['spawns'])}
 enemy=dict(p=tuple(B['enemies'][0]['cell']),hp=3,disabled=False);progress={'cut':0,'power':0,'stop':0};log=[];supply=0
 cells={'cut':(2,2),'power':(6,2),'stop':(6,3)};rows=[list(x) for x in B['rows']]
 def path(start,goals):
  q=[(0,start)];best={start:0};prev={};goals=set(goals)
  while q:
   cost,p=heapq.heappop(q)
   if cost!=best[p]:continue
   if p in goals:
    out=[p]
    while out[-1]!=start:out.append(prev[out[-1]])
    return out[::-1]
   x,y=p
   for v in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    a,b=v
    if not(0<=a<8 and 0<=b<8) or rows[b][a] in '#X' or (v==enemy['p'] and enemy['hp']>0):continue
    n=cost+(2 if rows[b][a] in '~:' else 1)
    if n<best.get(v,999):best[v]=n;prev[v]=p;heapq.heappush(q,(n,v))
  return None
 def distance(a,b):return abs(a[0]-b[0])+abs(a[1]-b[1])
 for rnd in range(1,B['round_limit']+1):
  for h in heroes.values():h['ap']=0 if h['left'] or h['hp']<=0 else 2
  # Deterministic axis: greater absolute offset; horizontal on tie.
  alive=[(distance(enemy['p'],h['p']),k,h) for k,h in heroes.items() if not h['left'] and h['hp']>0]
  intent=[]
  if alive and not enemy['disabled']:
   _,_,target=min(alive,key=lambda x:x[:2]);dx=target['p'][0]-enemy['p'][0];dy=target['p'][1]-enemy['p'][1]
   step=((1 if dx>=0 else -1),0) if abs(dx)>=abs(dy) else (0,(1 if dy>=0 else -1))
   for n in range(1,4):
    p=(enemy['p'][0]+n*step[0],enemy['p'][1]+n*step[1])
    if not(0<=p[0]<8 and 0<=p[1]<8) or rows[p[1]][p[0]] in '#X':break
    intent.append(p)
  log.append(dict(round=rnd,event='intent',enemy_at=enemy['p'],cells=intent))
  for k in ['B','C','A']:
   h=heroes[k]
   while h['ap']>0:
    target={'B':'cut','C':'stop','A':'power'}[k]
    all_done=progress['cut']==2 and progress['power']==2
    if all_done:
     if list(h['p']) in B['exits']:
      h['ap']-=1;h['left']=True;log.append(dict(round=rnd,actor=k,action='leave_site',ap_left=h['ap']));break
     goals=[tuple(p) for p in B['exits']]
    elif progress[target]>=2:
     # Do not crowd another actor's goal; conserve AP until goal completes.
     break
    else:
     x,y=cells[target];goals=[(x,y),(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
     if distance(h['p'],cells[target])<=1:
      if target=='power' and progress['cut']<2:break
      add=1;action='interact'
      if style=='level2' and h['first_work']:add=2;h['first_work']=False
      if style=='battery' and target=='power':add=2;action='battery';supply+=2
      progress[target]=min(2,progress[target]+add);h['ap']-=1
      if progress['stop']==2:enemy['disabled']=True
      log.append(dict(round=rnd,actor=k,action=action,target=target,work=progress[target],ap_left=h['ap']));continue
    others={o['p'] for oid,o in heroes.items() if oid!=k and not o['left']}
    goals=[p for p in goals if p not in others and 0<=p[0]<8 and 0<=p[1]<8 and rows[p[1]][p[0]] not in '#X']
    route=path(h['p'],goals);assert route,(style,k,target)
    used=0;end=0
    for i,p in enumerate(route[1:],1):
     c=2 if rows[p[1]][p[0]] in '~:' else 1
     if used+c>3:break
     used+=c
     if p not in others:end=i
    if not end:break
    h['p']=route[end];h['ap']-=1;log.append(dict(round=rnd,actor=k,action='move',path=route[:end+1],ap_left=h['ap']))
  if not enemy['disabled']:
   for p in intent:
    hit=next((k for k,h in heroes.items() if not h['left'] and h['p']==p),None)
    if hit:
     heroes[hit]['hp']-=2;log.append(dict(round=rnd,event='scout_hit',target=hit,damage=2));break
    enemy['p']=p
  if rnd==5:
   for x,y in B['environment']['water_addition']['cells']:rows[y][x]='~'
  log.append(dict(round=rnd,event='end_round',hp={k:h['hp'] for k,h in heroes.items()},work=copy.deepcopy(progress)))
  if all(h['left'] for h in heroes.values()):break
 assert progress['cut']==2 and progress['power']==2 and all(h['left'] for h in heroes.values()),(style,progress,heroes)
 assert all(h['hp']>0 for h in heroes.values())
 return dict(style=style,rounds=rnd,ap_used=sum('action' in x for x in log),supplies_used=supply,hp={k:h['hp'] for k,h in heroes.items()},log=log)
R=[play(s) for s in ['baseline','level2','battery']]
checks=[('three cases extracted without incapacitation',all(min(r['hp'].values())>0 for r in R)),('battery paid exactly2 supplies',R[2]['supplies_used']==2),('baseline costs no supplies',R[0]['supplies_used']==0),('growth and equipment reduce AP independently',R[1]['ap_used']<R[0]['ap_used'] and R[2]['ap_used']<R[0]['ap_used'])]
assert all(v for _,v in checks)
# Compare genuinely equivalent two-actor work positions, not vague multiplicative damage buffs.
cooperation={'scenario':'two adjacent actors both adjacent to a three-work console, one imminent machine hit for2','basic':{'total_ap':3,'work':3,'damage_to_worker':2},'protected_work':{'total_ap':2,'work':3,'damage_to_worker':0,'requires':'mutual trust>=60, trained/equipped protocol, relevant safety condition satisfied'},'low_trust':{'same_basic_work_legal':True,'advanced_protocol_legal':False},'limits':'shield blocks one machine hit only; electricity bypasses it; this is an algebraic action comparison, not an extra simulated map.'}
out=dict(cases=R,checks=[n for n,v in checks],cooperation=cooperation,scope='Executed subset: M02 terrain, 3 heroes, AP movement, occupied endpoints, scout locked intent/damage, work prerequisites, stop control, mission goals, water addition and evacuation. No general proof for other 35 maps, all enemy types or every skill.')
(ROOT/'outputs/combat-design-example.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k!='log'} for x in R],ensure_ascii=False))
