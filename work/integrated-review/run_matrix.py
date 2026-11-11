"""Every available named trio on36maps/46goal selections. Offline standard/A.
Chapter levels isolate composition; only campaign runs claim earned XP/fatigue.
"""
from pathlib import Path
import itertools,json,sys
from collections import Counter
from party import Party
from social import Social,CHARS
from guidance import Guidance
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';B=json.loads((ROOT/'game/data/final_design/boards.json').read_text())['boards']
def rank(r):return (not r['success'],r['downed'],r['rounds'],r['damage'],r['ap'])
def short(r):return {k:v for k,v in r.items() if k not in ['log','used']}
rows=[];examples=[];map_rows=[];attempts=0;skill_uses=Counter();logs=[]
for b in B:
 available=[a for a,c in CHARS.items() if c['join']==1 or c['join']<b['day'] or (b['kind']=='side' and c['join']==b['day'])]
 levels={a:max(1,1+(b['day']-1)//6,1+((CHARS[a]['join']-1)//6 if CHARS[a]['join']>1 else 0)) for a in available}
 start=len(rows)
 for route,groups in b.get('route_groups',{'default':b['mandatory_groups']}).items():
  for goals in itertools.product(*groups):
   for trio in itertools.combinations(available,3):
    trials=[];baselines=[]
    for enabled,style in itertools.product([False,True],['rush','controls']):
     battle=Party(b,goals,list(trio),levels,skills=enabled,style=style);r=battle.run();attempts+=1;trials.append((battle,r))
     if not enabled:baselines.append(r)
     skill_uses.update(r['skill_action_types'])
    battle,best=min(trials,key=lambda x:rank(x[1]));base=min(baselines,key=rank)
    social=Social();reaction=social.settle(battle,best,list(trio),b['day']);guide=Guidance();guide.scene(b,best['log'],restricted=any(social.restrictions(list(trio),b['day']).values()))
    row=dict(route=route,**short(best),baseline=short(base),benefit=(best['rounds'],best['damage'],best['ap'])!=(base['rounds'],base['damage'],base['ap']),help_cards=len([x for x in guide.log if x['kind']=='nonmodal_card']),relationship_changes=[dict(observer=a,target=t,gain=v['actual_trust_gain']) for a,s in social.people.items() for receipt in s.receipts for t,v in receipt['directions'].items() if v['actual_trust_gain']])
    rows.append(row)
    if row['benefit'] and len([e for e in examples if e['mission']==b['id']])<2:
     examples.append(dict(mission=b['id'],party=trio,route=route,baseline=short(base),selected=short(best),log=best['log']))
    if not best['success']:logs.append(dict(mission=b['id'],party=trio,goals=goals,trials=[short(x[1]) for x in trials]))
 rs=rows[start:];map_rows.append(dict(mission=b['id'],title=b['title'],day=b['day'],available=available,configurations=len(rs),solved=sum(x['success'] for x in rs),benefit_cases=sum(x['benefit'] for x in rs),metric_signatures=len({(x['rounds'],x['ap'],x['damage'],tuple(x['goals'])) for x in rs}),skill_actions=sum(x['skill_actions'] for x in rs),max_cards=max([x['help_cards'] for x in rs] or [0])))
 print(b['id'],'named configurations',len(rs),'solved',map_rows[-1]['solved'],'skill benefits',map_rows[-1]['benefit_cases'],flush=True)
out={'version':'0.9-integrated-review','scope':'36maps/46goal selections, every chronologically available named trio at fixed chapter comparison levels; standard difficulty,Aweather,canonical slot order,two deterministic policies,with/without opportunistically selected skills. Not all6slot permutations/all24skill loadouts or novice play. New social settlement and guidance scheduler receive each retained full trace.','attempts':attempts,'named_configurations':len(rows),'maps':map_rows,'cases':rows,'examples':examples,'unfound':logs,'skill_uses':dict(skill_uses),'all_solved':all(r['success'] for r in rows)}
(O/'integrated-party-matrix.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['attempts','named_configurations','all_solved','skill_uses']},ensure_ascii=False))
