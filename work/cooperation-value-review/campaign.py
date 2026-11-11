"""Matched full campaigns: best sampled ordinary routes versus earned cooperation.
No one is granted trust, levels, equipment or a learned pair bundle for free.
"""
from routes import *
import contextlib,io
p=ROOT/'work/player-choice-review/campaign.py'
ns={'__file__':str(p),'__name__':'value_campaign_adapter'}
exec(compile(p.read_text().split('\nscenarios=[]')[0],str(p),'exec'),ns)
RUN=ns['RUN'];Z=ns['z'];Ledger=ns['Ledger'];MODE='ordinary';CACHE={};SELECTED=[]
class NoAdvancedHeavy(HeavyRoutes):
 def protocol_ready(self,key,a,b):
  return False if key in ['relay_carry','coordinated_pull'] else super().protocol_ready(key,a,b)

def factory(board,goals,party,levels=None,**kw):
 g=Z['ACTIVE'];levels=levels or {a:1 for a in party}
 key=(board['id'],tuple(goals),tuple(party),tuple(sorted(levels.items())),str(kw),str(sorted(g.protocols)),str(g.rel),MODE)
 if key in CACHE:return CACHE[key]
 # Preserve the old ordinary/field-operation candidate too: richer search must
 # never throw out a known ordinary solution just to make cooperation look good.
 old=ns['old_factory'](board,goals,party,levels,**deepcopy(kw));rs=[(old,old.run())]
 trust={(a,b):g.rel.get(a+'>'+b,{}).get('trust',0) for a in party for b in party if a!=b}
 pairs=[pair for pair in itertools.combinations(range(3),2) if tuple(sorted([party[i] for i in pair]))+('relay_carry',) in g.protocols and min(trust[(party[pair[0]],party[pair[1]])],trust[(party[pair[1]],party[pair[0]])])>=60]
 for plan in configurations(board,goals):
  for exchange,pair in [('none',(0,2)),('ordinary',(0,2))]+([('advanced',p) for p in pairs] if MODE=='cultivate' else []):
   allocation,priority,style=plan;opts=deepcopy(kw);opts.update(style=style,extra=extras(board,goals))
   b=Routes(board,goals,party,levels,allocation=allocation,priority=priority,exchange=exchange,pair=pair,trained=list(g.protocols),trust=trust,**opts);r=b.run();rs.append((b,r))
 if any(e['type'] in ['hauler','sentinel'] for e in board['enemies']):
  # Preparing a pull can incidentally find a better shutdown route without ever
  # pulling. Give these legal ordinary movements to BOTH arms, including all pairs.
  for pair in itertools.combinations(range(3),2):
   for cls,heavy_mode in [(NoAdvancedHeavy,'pull'),(HeavyRoutes,'push')]:
    opts=deepcopy(kw);opts.update(extra=extras(board,goals))
    b=cls(board,goals,party,levels,pair=pair,heavy_mode=heavy_mode,trained=[],trust=trust,**opts);r=b.run();rs.append((b,r))
 if MODE=='cultivate' and any(e['type'] in ['hauler','sentinel'] for e in board['enemies']):
  for pair in pairs:
   opts=deepcopy(kw);opts.update(extra=extras(board,goals))
   b=HeavyRoutes(board,goals,party,levels,pair=pair,trained=list(g.protocols),trust=trust,**opts);r=b.run();rs.append((b,r))
 b,r=min(rs,key=lambda z:rank(z[1]));b.run=lambda:r;CACHE[key]=b
 return b

def train(g):
 # Both arms get the same existing finite assistance policy.
 support=ns['USE_SUPPORT'];ns['USE_SUPPORT']=True
 prev=Z['PROFILE'];Z['PROFILE']='safe';ns['training_and_repairs'](g);Z['PROFILE']=prev;ns['USE_SUPPORT']=support
 if MODE=='ordinary':return
 # Spend on a real eligible pair likely to deploy; don't counterfeit trust gains.
 available=[a for a in g.crew if g.healthy(a) and a not in g.used and g.crew[a]['fatigue']+8<=100]
 pair=next((list(p) for p in itertools.combinations(available,2) if all(g.rel[a+'>'+b]['trust']>=60 for a,b in [p,p[::-1]]) and tuple(sorted(p))+('relay_carry',) not in g.protocols),None)
 if pair and g.projects<2 and g.resources['supplies']>=2:g.train(pair,'relay_carry')

RUN.update(Party=factory,training_and_repairs=train)

if __name__=='__main__':
 out=[]
 for profile,options in [('fixed',dict(fixed=True,sides=True)),('rotate',dict(sides=True)),('hard',dict(hard=True,sides=True)),('setbacks',dict(hard=True,disasters=(6,7,8,15)))]:
  for mode in ['ordinary','cultivate']:
   MODE=mode;CACHE.clear();Z['PROFILE']='safe';ns['REPAIR']='none';ns['ADVANCED_PLAN']=False
   s=RUN['run'](profile+'_'+mode,**options);out.append(s)
   q=s['summary'];print(q['name'],q['main_count'],q['side_count'],sum(q['xp'].values()),q['resources'],q['training_bundles'],sum(r['kind']=='advanced_actions_used' for r in s['receipts']),flush=True)
 (ROOT/'outputs/cooperation-value-campaign.json').write_text(json.dumps(dict(version='0.12-audit',scope='Eight matched earned-state campaigns; same target preferences and route candidate menu, optional dedicated training takes real slots. Hindsight best-candidate selection is a model, not human behavior.',scenarios=out,actual_battles=sum(len(s['battles']) for s in out)),ensure_ascii=False,indent=2)+'\n')
