from relationships import *
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
RUN=c.RUN;CACHE={};CFG={}
class Ledger(RelationshipLedger):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.identity_pacts=CFG.get('pacts',False);self.identity_training=CFG.get('training','none');self.identity_dock=CFG.get('dock',False)
 def choose_party(self,fixed=False,side=False):
  if side or CFG.get('formation')!='flex':return super().choose_party(fixed,side)
  desired=['chen','ye','lin'] if self.day<14 else ['chen','mo','su'] if self.day<18 else ['su','jiang','he'] if self.day<20 else ['su','he','ye']
  available=[a for a in self.crew if self.eligible(a)]
  return sorted(available,key=lambda a:(a not in desired,desired.index(a) if a in desired else 99,self.crew[a]['fatigue']))[:3]

def factory(board,goals,party,levels=None,**kw):
 g=c.Z['ACTIVE'];board=deepcopy(board);kw['medical_capacity']=g.medical_pack_limit()
 if board['kind']=='main' and g.identity_dock:
  plans=g.dispatch_options([a for a in party if not a.startswith('reserve')])
  if plans and CFG.get('dock_days','late')!='none' and (not isinstance(CFG.get('dock_days'),list) or g.day in CFG['dock_days']):
   g.select_dispatch([a for a in party if not a.startswith('reserve')],plans[0]);board['exits']=[board['backup_exit']]
 key=(board['id'],tuple(goals),tuple(party),tuple(sorted(levels.items())),str(kw.get('gear')),str(kw.get('relations')),kw.get('difficulty'),kw.get('delay'),str(board['exits']),g.medical_pack_limit())
 if key in CACHE:return CACHE[key]
 results=[]
 for plan in configurations(board,goals):
  allocation,priority,style=plan
  # Include ordinary no-skill plans even at high character levels.
  for skills in [False,True]:
   opts=deepcopy(kw);opts.update(style=style,skills=skills,extra=extras(board,goals))
   b=IdentityRoutes(board,goals,party,levels,allocation=allocation,priority=priority,**opts);r=b.run();results.append((b,r))
 for role in ['isolation','protect']:
  for style in ['rush','controls']:
   opts=deepcopy(kw);opts.update(style=style,skills=True,extra=extras(board,goals))
   b=IdentityRoutes(board,goals,party,levels,role_policy=role,**opts);r=b.run();results.append((b,r))
 # Keep the four existing optional field operations in the same full battle.
 if board['id'] in CONTRACT['services']:
  n=len(CONTRACT['services'][board['id']]['posts'])
  for w in itertools.permutations(range(3),n):
   for role,mode in [('none','independent'),('isolation','independent'),('protect','protected')]:
    opts=deepcopy(kw);opts.update(style='controls',skills=True,extra=extras(board,goals))
    b=IdentityBattle(board,goals,party,levels,role_policy=role,approach=mode,watchers=w,**opts);r=b.run();results.append((b,r))
 b,r=min(results,key=lambda x:rank(x[1]));b.run=lambda:r;CACHE[key]=b;return b

def prepare_day(g):pass
def training(g):
 if g.identity_training=='none':return
 # Mentoring is chosen for an approaching learner unlock, rather than farming XP.
 if g.identity_training in ['mentor','selective'] and g.projects<2 and g.resources['supplies']>=2:
  candidates=g.mentor_candidates()
  if g.identity_training=='selective':
   nextday=g.day+1
   desired=['chen','ye','lin'] if nextday<14 else ['chen','mo','su'] if nextday<18 else ['su','jiang','he'] if nextday<20 else ['su','he','ye']
   candidates=[x for x in candidates if x[1] in desired and any(g.crew[x[1]]['xp']+3<t<=g.crew[x[1]]['xp']+x[2] for t in [12,28,72])]
  candidates.sort(key=lambda x:(not any(g.crew[x[1]]['xp']<t<=g.crew[x[1]]['xp']+x[2] for t in [12,28,72]),g.crew[x[1]]['xp']))
  if candidates:g.mentor(*candidates[0][:2])
 if g.projects>=2:return
 actors=[a for a in g.crew if g.healthy(a) and a not in g.used and g.crew[a]['fatigue']+8<=100 and g.crew[a]['xp']<100]
 if g.identity_training in ['targeted','mentor','selective']:
  actors=[a for a in actors if any(g.crew[a]['xp']<t<=g.crew[a]['xp']+3 for t in [12,28,72])]
 actors.sort(key=lambda a:g.crew[a]['xp'])
 actors=actors[:min(2,g.resources['supplies'])]
 if actors:g.train(actors)

# Reuse the actual day/story/social schedule but remove automatic filler training.
source=c.ns['run_source']
start=source.index('  while g.projects<2:\n   trainees=')
end=source.index('  social.night_from_ledger',start)
source=source[:start]+source[end:]
source=source.replace("if mid=='M24':g.route='shared_control' if 'shared_control' in g.available_routes() else 'evacuation' if disaster else 'distributed_rebuild'", "if mid=='M24':g.route=CFG.get('ending','shared_control') if CFG.get('ending','shared_control') in g.available_routes() else 'distributed_rebuild'")
exec(compile(source,str(ROOT/'work/integrated-review/campaign.py'),'exec'),RUN)
RUN.update(Ledger=Ledger,Party=factory,rank=rank,record_operation=c.ns['record_operation'],training_and_repairs=training,prepare_day=prepare_day,operation=c.Z['operation'],CFG=CFG)

def one(args):
 name,cfg,options=args;CFG.clear();CFG.update(cfg);CACHE.clear();RUN['CFG']=CFG
 r=RUN['run'](name,**options);return r
if __name__=='__main__':
 cases=[
 ('固定队伍：不额外训练',dict(training='none',formation='fixed'),dict(fixed=True,sides=True)),
 ('固定队伍：临界点训练',dict(training='targeted',formation='fixed'),dict(fixed=True,sides=True)),
 ('换阵容：不额外训练',dict(training='none',formation='flex'),dict(sides=True)),
 ('换阵容：临界点训练',dict(training='targeted',formation='flex'),dict(sides=True)),
 ('换阵容：关系带教',dict(training='mentor',formation='flex',pacts=True),dict(sides=True)),
 ('同样关系与带教：改派接应',dict(training='mentor',formation='flex',pacts=True,dock=True),dict(sides=True)),
 ('共同重建路线',dict(training='targeted',formation='flex',pacts=True,ending='distributed_rebuild'),dict(sides=True)),
 ('最高难度失误后撤离',dict(training='mentor',formation='flex',pacts=True,dock=True,ending='evacuation'),dict(hard=True,disasters=(6,7,8,15)))
 ]
 rows=[]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  for s in pool.map(one,cases):
   rows.append(s);q=s['summary'];print(q['name'],q['main_count'],q['side_count'],q['positive_relationships'],q['resources'],flush=True)
 (ROOT/'outputs/growth-identity-campaigns.json').write_text(json.dumps(dict(version='0.13',scope='Eight real earned-state campaigns using one day/story/social ledger. Same route search across arms; no free level/trust/items. Preselected strategies, not optimal policies or human preference.',scenarios=rows,actual_battles=sum(len(s['battles']) for s in rows)),ensure_ascii=False,indent=2)+'\n')
