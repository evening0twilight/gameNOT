from routes import *
from concurrent.futures import ProcessPoolExecutor
import multiprocessing,time
OUT=ROOT/'outputs/cooperation-value-matrix.json'
def one(case):
 mid,route,goals,party=case;board=B[mid];levels={a:max(1,1+(board['day']-1)//6) for a in party};plans=configurations(board,goals)
 ordinary=[];advanced=[];n=0
 for plan in plans:
  for skills,exchange in [(False,'none'),(True,'none'),(True,'ordinary')]:
   g,r=execute(board,goals,party,levels,plan,skills,exchange,trained=[]);ordinary.append(r);n+=1
 # Deliberate ordinary heavy push is a comparator, not a compulsory task.
 heavy=any(e['type'] in ['hauler','sentinel'] for e in board['enemies'])
 if heavy:
  for pair in itertools.combinations(range(3),2):
   g,r=execute(board,goals,party,levels,plans[0],pair=pair,heavy='push',trained=[]);ordinary.append(r);n+=1
 for pair in itertools.combinations(range(3),2):
  a,b=[party[i] for i in pair];eligible=min(T.get((a,b),0),T.get((b,a),0))>=60
  # Optimistic controlled trust is an upper-bound opportunity test, NOT earned.
  trust=dict(T);trust[(a,b)]=trust[(b,a)]=60
  for plan in plans:
   g,r=execute(board,goals,party,levels,plan,exchange='advanced',pair=pair,trust=trust)
   r['initially_eligible_pair']=eligible;advanced.append(r);n+=1
  if heavy:
   g,r=execute(board,goals,party,levels,plans[0],pair=pair,trust=trust,heavy='pull')
   r['initially_eligible_pair']=eligible;advanced.append(r);n+=1
 base=min(ordinary,key=rank);used=[r for r in advanced if r['advanced_actions'] and r['success']]
 frontier=[r for r in used if not any(dominates(o,r) for o in ordinary)]
 new=[r for r in used if not any(dominates(o,r,True) for o in ordinary)]
 # A strictly larger rescue/evidence set with no worse casualties is separate
 # from one-AP speed differences; this is still only the bounded search frontier.
 unique=[r for r in used if not any(o['success'] and set(o['secured'])>=set(r['secured']) and o['downed']<=r['downed'] for o in ordinary)]
 return dict(mission=mid,route=route,goals=goals,party=party,trials=n,ordinary_best=compact(base),advanced_used=len(used),non_dominated_owned=len(frontier),non_dominated_new=len(new),qualitative=len(unique),natural_frontier=sum(r['initially_eligible_pair'] for r in frontier),best_cooperation=compact(min(used,key=rank)) if used else None,frontier=[compact(r) for r in sorted(frontier,key=rank)[:3]],witness=base['log'] if mid in ['M06','M08'] else None)

if __name__=='__main__':
 cases=[]
 for b in B.values():
  available=[a for a,c in CHARS.items() if c['join']==1 or c['join']<b['day'] or b['kind']=='side' and c['join']==b['day']]
  for route,groups in b.get('route_groups',{'default':b['mandatory_groups']}).items():
   for goals in itertools.product(*groups):
    for party in itertools.combinations(available,3):cases.append((b['id'],route,list(goals),list(party)))
 rows=[];start=time.time()
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  for i,r in enumerate(pool.map(one,cases,chunksize=5),1):
   rows.append(r)
   if i%80==0:print(i,len(cases),round(time.time()-start),flush=True)
 maps=[]
 for mid in B:
  rr=[r for r in rows if r['mission']==mid]
  maps.append(dict(mission=mid,cases=len(rr),ordinary_success=sum(r['ordinary_best']['success'] for r in rr),used_cases=sum(r['advanced_used']>0 for r in rr),frontier_cases=sum(r['non_dominated_owned']>0 for r in rr),new_frontier_cases=sum(r['non_dominated_new']>0 for r in rr),qualitative_cases=sum(r['qualitative']>0 for r in rr)))
 result=dict(version='0.12-audit',cases=len(rows),trials=sum(r['trials'] for r in rows),scope='All chronologically available named trios and46goal variants, fixed spawn order, chapter levels, standard/A. Ordinary assignment/priority/skills/handoff and deliberate push versus identical assignment menu plus trained relay/targeted pull. Cooperative pairs get optimistic mutual60 to isolate capability; trust cultivation and safety are NOT earned here. No tools, no global-optimality or human-fun claim.',maps=maps,rows=rows)
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('DONE',result['cases'],result['trials'],maps,flush=True)
