"""Reference content/logic audit. Route schedules exclude combat/occupancy and are not win-rate claims."""
from pathlib import Path
import json,heapq,itertools,math
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design';OUT=ROOT/'outputs'
def read(n):return json.loads((D/n).read_text())
B=read('boards.json')['boards'];C=read('combat.json');S=read('stories.json');P=read('progression_relationship.json');A=read('abilities.json');E=read('equipment.json')['items'];N=read('enemies.json')
checks=[]
def check(name,ok):
 if not ok:raise AssertionError(name)
 checks.append(name)
check('36 distinct encounters',len(B)==len({b['id'] for b in B})==36)
check('24 named specialties with legal actor/level pairs',len(A)==24 and len({(a['actor'],a['level']) for a in A})==24 and all(a['level'] in [1,3,5] for a in A))
check('12 equipment definitions and 4 protocols',len(E)==12 and len(P['protocols'])==4)
check('6 enemy archetypes and 8 facility tiers',len(N)==6 and len(read('facilities.json'))*2==8)
check('96 uniquely identified story nodes',sum(len(S[k]) for k in ['personal_nodes','relationship_nodes','community_nodes','recovery_nodes','chapter_nodes'])==len({n['id'] for k in ['personal_nodes','relationship_nodes','community_nodes','recovery_nodes','chapter_nodes'] for n in S[k]})==96)
boardmap={b['id']:b for b in B}
def dist(b,start,targets,blocked=(),carry=False):
 rows=b['rows'];cost={'.':1,'~':2,':':2};start=tuple(start);targets=set(map(tuple,targets));blocked=set(map(tuple,blocked))
 # Stress both declared variants and incoming failure terrain at once, conservatively.
 wet=set(map(tuple,b['environment']['water_addition']['cells']));rubble=(1,5)
 q=[(0,start)];best={start:0};prev={}
 while q:
  d,p=heapq.heappop(q)
  if best[p]!=d:continue
  if p in targets:
   path=[p]
   while path[-1]!=start:path.append(prev[path[-1]])
   path.reverse();budget=2 if carry else 3;ap=0;remaining=0
   for x,y in path[1:]:
    k=max(cost[rows[y][x]],2 if (x,y) in wet or (x,y)==rubble else 1)
    if remaining<k:ap+=1;remaining=budget
    remaining-=k
   return {'cost':d,'ap':ap,'path':[list(v) for v in path],'end':list(p)}
  x,y=p
  for v in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   a,z=v
   if not (0<=a<8 and 0<=z<8) or rows[z][a] not in cost or v in blocked:continue
   nd=d+max(cost[rows[z][a]],2 if v in wet or v==rubble else 1)
   if nd<best.get(v,10000):best[v]=nd;prev[v]=p;heapq.heappush(q,(nd,v))
 return None

def adj(cell):
 x,y=cell;return [[x,y],[x-1,y],[x+1,y],[x,y-1],[x,y+1]]

def schedule(b,targets):
 # Recursively include actual objective dependencies; all machine controls included.
 objects={o['id']:o for o in b['objectives']+b['controls']}
 needed=set(targets)|{o['id'] for o in b['controls']}
 def add(i):
  for p in objects[i]['prerequisites']:
   if p not in needed:needed.add(p);add(p)
 for i in list(needed):add(i)
 states=[{'p':p[:],'t':0} for p in b['spawns']];done={};log=[]
 blocked=[e['cell'] for e in b['enemies']]
 while needed:
  candidates=[]
  for oid in sorted(needed):
   o=objects[oid]
   if not all(x in done for x in o['prerequisites']):continue
   for index,s in enumerate(states):
    route=dist(b,s['p'],adj(o['cell']),blocked)
    if not route:continue
    ap=route['ap'];extra=[];end=route['end']
    if o['kind'] in ['rescue','cargo']:
     ap+=(1 if o['kind']=='rescue' else 0)+1
     back=dist(b,end,b['exits'],blocked,carry=True)
     if not back:continue
     ap+=back['ap']+1;end=back['end'];extra=back['path']
    else:ap+=o['work']
    start=max(s['t'],max([done[x] for x in o['prerequisites']]+[0]));finish=start+ap
    if o['kind']=='rescue' and o['stabilize_deadline']['mode']!='none':
     stabilize_round=math.ceil((start+route['ap']+1)/2)
     deadline=o['stabilize_deadline']['round'] if o['stabilize_deadline']['mode']=='fixed_round' else math.ceil(max(done[x] for x in o['prerequisites'])/2)+2
     if stabilize_round>deadline:continue
    if o['kind']=='channel':finish=2*(math.ceil(finish/2)+o['hold_rounds'])
    if o['kind']=='convoy':finish=2*(math.ceil(finish/2)+len(o['waypoints'])-1)
    candidates.append((finish,0 if oid in {x['id'] for x in b['controls']} else 1,oid,index,start,ap,route,end,extra))
  if not candidates:raise AssertionError(f'Unreachable or dependency cycle {b["id"]}: {needed}')
  finish,_,oid,index,start,ap,route,end,extra=min(candidates,key=lambda x:x[:4]);states[index]={'p':end,'t':finish};done[oid]=finish;needed.remove(oid)
  log.append(dict(task=oid,actor=index,start_ap_tick=start,finish_ap_tick=finish,ap_used=ap,path=route['path'],carry_return=extra))
 # Everyone walks out; no teleport completion.
 for i,s in enumerate(states):
  route=dist(b,s['p'],b['exits'],blocked);assert route
  s['t']+=route['ap']+1
  log.append(dict(task='leave_site',actor=i,finish_ap_tick=s['t'],ap_used=route['ap']+1,path=route['path']))
 return dict(rounds=math.ceil(max(s['t'] for s in states)/2),sum_ap=sum(x['ap_used'] for x in log),steps=log)

reports=[]
for b in B:
 ids={o['id'] for o in b['objectives']+b['controls']};enemies={e['id'] for e in b['enemies']}
 check(b['id']+' geometry/objects valid',len(b['rows'])==8 and all(len(r)==8 for r in b['rows']) and all(b['rows'][o['cell'][1]][o['cell'][0]] not in '#X' for o in b['objectives']+b['controls']+b['enemies']))
 check(b['id']+' prerequisite references valid',all(set(o['prerequisites'])<=ids for o in b['objectives']+b['controls']))
 check(b['id']+' all machines have finite universal shutdowns',all(set(e['disable_requires'])<=ids for e in b['enemies']))
 for o in b['objectives']+b['controls']:
  check(b['id']+'/'+o['id']+' reachable by baseline actor',dist(b,b['spawns'][0],adj(o['cell']),[e['cell'] for e in b['enemies']]) is not None)
 for e in b['enemies']:
  if e['rail']:check(b['id']+' rail traversable',all(b['rows'][y][x] not in '#X' for x,y in e['rail']))
 cases=b.get('route_groups',{'default':b['mandatory_groups']})
 for route,groups in cases.items():
  check(b['id']+'/'+route+' objective groups valid',all(set(g)<=ids and g for g in groups))
  for selection in itertools.product(*groups):
   plan=schedule(b,selection);reports.append(dict(mission=b['id'],route=route,selection=selection,hard_deadline=b.get('hard_round_limit',b['round_limit']-1),standard_deadline=b['round_limit'],**plan))
   check(b['id']+'/'+route+'/'+','.join(selection)+' conservative logistics below standard deadline',plan['rounds']<=b['round_limit'])
 # Optional raw IDs or compound named selectors.
 for bonus in b['optional']:
  if bonus not in ['both','any_two','all_three']:check(b['id']+' optional '+bonus+' references exist',set(bonus.split('+'))<=ids)
 if b['evidence_receipt']:check(b['id']+' evidence producers exist',set(b['evidence_receipt']['requires'])<=ids)

# State table path enumeration: absent, unfinished, all legal final choices.
paths=[]
for actor,p in S['profiles'].items():
 nodes=[n for n in S['personal_nodes'] if n['actor']==actor]
 check(actor+' scenes all available before final',all(1<=n['earliest_day']<=23 for n in nodes))
 check(actor+' non-paying plan available',any(c['credits']==0 for c in nodes[1]['choices']))
 for first in nodes[0]['choices']:
  for plan in nodes[1]['choices']:
   for verified in [False,True]:
    if verified and not plan['creates_contract']:continue
    choices=[c['id'] for c in nodes[2]['choices'] if not c['requires'] or verified]
    check(actor+' no false reconciliation',('integrated' in choices)==verified)
    for final in choices:
     for absent in [False,True]:paths.append(dict(actor=actor,first=first['id'],plan=plan['id'],verified=verified,requested_ending=final,absent=absent,actual='medical_withdrawal' if absent else final))
 check(actor+' absent final always medical withdrawal',all(p['actual']=='medical_withdrawal' for p in paths if p['actor']==actor and p['absent']))
# Greedy earliest-window schedule includes all personal nodes and pair scenes, not mandatory leisure completion.
pending={n['id']:n for n in S['personal_nodes']+S['relationship_nodes']};resolved=set();calendar=[]
for day in range(1,24):
 slots=[];projects=0
 for slot in range(2):
  ready=[n for n in pending.values() if n['earliest_day']<=day and all(x in resolved for x in n.get('requires_resolved',[])) and projects+n.get('project_cost',0)<=2]
  if not ready:break
  n=min(ready,key=lambda n:(0 if n['id'].startswith('P_') else 1,n['earliest_day'],n['id']));slots.append(n['id']);projects+=n.get('project_cost',0);resolved.add(n['id']);del pending[n['id']]
 calendar.append(dict(day=day,scenes=slots,projects=projects))
check('all 24 personal and 12 pair nodes have schedule slots',not pending)
check('story decisions leave camp capacity',sum(x['projects'] for x in calendar)==8 and all(x['projects']<=2 for x in calendar))
# These are logical eligibility paths, not evidence that all conditional proofs can be earned together.
check('protocols spend positive AP and no AP generation',all('各1AP' in x['cost'] for x in P['protocols']))
check('base action control is independent of trust',all(x['id'] in [a['id'] for a in C['actions']] for x in [{'id':'move'},{'id':'stabilize'},{'id':'attack'},{'id':'extract'}]))
report=dict(version='0.4',passed_count=len(checks),checks=checks,board_routes=reports,story_paths=paths,story_calendar=calendar,
 limitations=['Path schedules include equipment-free movement, work, pickup, carry, delivery, evacuation, prerequisites, channel/convoy waits and every enemy shutdown control.','They DO NOT execute enemy attacks, moving unit collisions, ability use, dynamic damage or gameplay decisions. Slack is a logistics sanity check, not a combat win proof.','Story enumeration verifies resolution/absence/eligibility and reading slots; it does not claim all characters can simultaneously earn every proof in one run.'])
(OUT/'final-design-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'route_cases':len(reports),'max_rounds':max(x['rounds'] for x in reports),'story_paths':len(paths),'last_scene_day':max(x['day'] for x in calendar if x['scenes'])},ensure_ascii=False))
