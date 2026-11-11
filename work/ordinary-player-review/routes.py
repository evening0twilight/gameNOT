from policies import *
import multiprocessing,collections
from concurrent.futures import ProcessPoolExecutor

def cases():
 for board in B.values():
  unlocked=[a for a,c in CHARS.items() if c['join']<board['day'] or c['join']==1 or board['kind']=='side' and c['join']<=board['day']]
  # Full structural branches x extra sets x policy x difficulty/weather on starterparty.
  for branch,goals in goal_variants(board):
   for extra in extra_sets(board,goals,branch):
    for behavior,difficulty,variant in itertools.product(PROFILES,['relaxed','standard','hard'],['A','B']):
     for service in ([False,True] if board['id'] in CONTRACT['services'] else [False]):
      yield dict(layer='structural',mission=board['id'],branch=branch,goals=goals,extra=extra,behavior=behavior,difficulty=difficulty,variant=variant,party=['lin','xu','su'],level=3,service=service)
  # Every date-legal trio on every required-goal branch, fixed ordinary choices;
  # separate axis rather than pretend we enumerated their giant Cartesian product.
  for party in itertools.combinations(unlocked,3):
   for branch,goals in goal_variants(board):
    for behavior,level in itertools.product(['main_only','cautious','favorite','mixed'],[3,5]):
     yield dict(layer='rosters',mission=board['id'],branch=branch,goals=goals,extra=(),behavior=behavior,difficulty='standard',variant='A',party=list(party),level=level,service=False)

def one(x):
 g=battle(B[x['mission']],x['goals'],x['party'],{a:x['level'] for a in x['party']},x['behavior'],x['extra'],service=x['service'],difficulty=x['difficulty'],variant=x['variant']);r=g.run()
 return x|{k:r[k] for k in ['success','secured','lost','downed','damage','rounds','ap','healthy_extracted','service_secured']}
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='ordinary-player-after-routes.json');args=ap.parse_args();inputs=list(cases());print('CASES',len(inputs),collections.Counter(x['layer'] for x in inputs),flush=True)
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  rows=[]
  for i,r in enumerate(pool.map(one,inputs,chunksize=16),1):
   rows.append(r)
   if i%2000==0:print('routes',i,flush=True)
 (ROOT/'outputs'/args.output).write_text(json.dumps(dict(version='0.16-audit',rows=rows,scope='All108authored required-goal/optional-intention combinations across6ordinarypolicies,3difficulties,2weatherstates,plusservicechoice; everydatelegaltrio on46goalbranches with4policies separately. Not every action sequence or all-axis Cartesian product. No after-result selection.'),ensure_ascii=False,indent=2)+'\n');print('DONE',len(rows),sum(r['success'] for r in rows),flush=True)
