"""Compare complete outcomes, not only action-count savings."""
from pathlib import Path
import json,itertools,sys
from choices import ChoiceBattle,SPEC
from encounter_choices import extras
from social import Social,CHARS,INITIAL
from guidance import Guidance
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';B=json.loads((ROOT/'game/data/final_design/boards.json').read_text())['boards']
T={(r['observer'],r['target']):r['trust'] for r in INITIAL}
def trained_for(party):return [tuple(sorted([a,b]))+(k,) for a,b in itertools.combinations(party,2) if min(T.get((a,b),0),T.get((b,a),0))>=60 for k in ['relay_carry','coordinated_pull']]
def compact(r):return {k:v for k,v in r.items() if k not in ['log','used','service_ticks']}
def basic_rank(r):return (not r['success'],r['downed'],r['rounds'],r['damage'],r['ap'])
def service_rank(r):return (not r['success'],not r['service_secured'],not r['machinery_intact'],-len(r['secured']),r['downed'],r['damage'],r['rounds'],r['ap'])
def signature(r):return (r['success'],r['service_secured'],r['machinery_intact'],tuple(sorted(r['secured'])),r['downed'])
cases=[];maps=[];witnesses=[];failures=[];attempts=0;support_comparisons=[]
for b in B:
 available=[a for a,c in CHARS.items() if c['join']==1 or c['join']<b['day'] or b['kind']=='side' and c['join']==b['day']]
 levels={a:max(1,1+(b['day']-1)//6) for a in available};start=len(cases)
 for route,groups in b.get('route_groups',{'default':b['mandatory_groups']}).items():
  for goals in itertools.product(*groups):
   for trio in itertools.combinations(available,3):
    party=list(trio);social=Social();relations=social.restrictions(party,b['day']);trained=trained_for(party)
    base=[];amb=[];live=[]
    for skills,style in itertools.product([False,True],['rush','controls']):
     for ambitious,where in [(False,base),(True,amb)]:
      battle=ChoiceBattle(b,goals,party,levels,skills=skills,style=style,ambition=ambitious,relations=relations);r=battle.run();where.append((battle,r));attempts+=1
    baseline=min(base,key=lambda x:basic_rank(x[1]));ambitious=min(amb,key=lambda x:(not x[1]['success'],-len(x[1]['secured']),x[1]['downed'],x[1]['damage'],x[1]['rounds'],x[1]['ap']))
    if b['id'] in SPEC['services']:
     n=len(SPEC['services'][b['id']]['posts'])
     for watchers in itertools.permutations(range(3),n):
      for ambition in [False,True]:
       same=[]
       configurations=[('independent',False,{}),('independent',True,{}),('protected',True,{}),('dismantle',False,{})]
       if b['day']>4:configurations.append(('independent',False,{'shield':next(i for i in range(3) if i not in watchers)}))
       if b['day']>7:configurations.append(('independent',False,{'insulation':watchers[0]}))
       for mode,skills,gear in configurations:
        battle=ChoiceBattle(b,goals,party,levels,skills=skills,approach=mode,watchers=watchers,trained=trained,trust=T,relations=relations,gear=gear,style='controls',ambition=ambition);r=battle.run();attempts+=1;live.append((battle,r));same.append(r)
       independent,skilled,protected=same[:3]
       if protected['success'] and protected['service_secured'] and not skilled['service_secured']:
        support_comparisons.append(dict(mission=b['id'],party=party,watchers=watchers,trained=trained,ambition=ambition,independent=compact(skilled),protected=compact(protected)))
    chosen=min(live,key=lambda x:service_rank(x[1])) if live else baseline
    battle,r=chosen;social.settle(battle,r,party,b['day']);guide=Guidance();guide.scene(battle.b,r['log'])
    distinct=len({signature(x[1]) for x in base+amb+live})
    row=dict(mission=b['id'],route=route,party=party,baseline=compact(baseline[1]),ambition=compact(ambitious[1]),service=compact(r) if live else None,qualitative_outcomes=distinct,trained_assumption=trained,live_options=[compact(x[1]) for x in live])
    cases.append(row)
    if not baseline[1]['success']:failures.append(dict(mission=b['id'],party=party,kind='no baseline found',trials=[compact(x[1]) for x in base]))
    if live and len([w for w in witnesses if w['mission']==b['id']])<4:
     candidates=[baseline,chosen]+[x for x in live if x[1]['success'] and x[1]['service_secured'] and not x[1]['machinery_intact']][:1]
     for g,z in candidates:
      witnesses.append(dict(**compact(z),route=route,log=z['log'],service_ticks=z['service_ticks']))
    elif not live and len([w for w in witnesses if w['mission']==b['id']])<1:
     witnesses.append(dict(**compact(ambitious[1]),route=route,log=ambitious[1]['log']))
 rs=cases[start:];maps.append(dict(mission=b['id'],title=b['title'],cases=len(rs),baseline_solved=sum(x['baseline']['success'] for x in rs),service_solved=sum(x['service'] is not None and x['service']['success'] and x['service']['service_secured'] for x in rs),intact_service=sum(x['service'] is not None and x['service']['success'] and x['service']['service_secured'] and x['service']['machinery_intact'] for x in rs),different_outcomes=sum(x['qualitative_outcomes']>1 for x in rs),role=SPEC['mission_roles'][b['id']]))
 print(maps[-1],flush=True)
out=dict(version='0.11-player-choice-review',scope='Every chronologically available named trio and46main-goal selections; fixed chapter levels,standard/A,canonical spawn slots. Extra objectives both independently and alongside4revised field operations. Training is controlled and only assigned to initially trust-eligible pairs; paid equipment comparators are explicitly supplied, not earned campaign inventory. Not exhaustive search or human play.',attempts=attempts,configurations=len(cases),maps=maps,cases=cases,witnesses=witnesses,unfound=failures,support_comparisons=support_comparisons)
(O/'player-choice-matrix-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Player-choice matrix',len(cases),'configurations',attempts,'attempts','baseline failures',len(failures),'cooperation outcome counterfactuals',len(support_comparisons))
