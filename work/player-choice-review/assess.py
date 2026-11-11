"""Bounded domination checks, without inventing satisfaction scores."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs'
M=json.loads((O/'player-choice-matrix-results.json').read_text());EQ={x['id']:x for x in json.loads((ROOT/'game/data/final_design/equipment.json').read_text())['items']}
def equipment(r):return [EQ[k] for k in r['gear'] if k in EQ and EQ[k]['slot'] in ['tool','support']]
def costs(r,purchase):
 return [r['downed'],r['damage'],r['rounds'],r['ap']]+([int(r.get('advanced_actions',0)>0),sum(e['price_credits'] for e in equipment(r)),sum(e['price_parts'] for e in equipment(r))] if purchase else [])
def dominates(a,b,purchase):
 if not a['success'] or not set(a['secured'])>=set(b['secured']) or a['machinery_intact']<b['machinery_intact'] or a['service_secured']<b['service_secured']:return False
 ca,cb=costs(a,purchase),costs(b,purchase)
 return all(x<=y for x,y in zip(ca,cb)) and (any(x<y for x,y in zip(ca,cb)) or set(a['secured'])>set(b['secured']) or a['machinery_intact']>b['machinery_intact'] or a['service_secured']>b['service_secured'])
rows=[];examples=[]
for mid in ['M05','M10','M21','S11']:
 cases=[x for x in M['cases'] if x['mission']==mid];row=dict(mission=mid,cases=len(cases),cooperation_attempts=0,dominated_if_owned=0,dominated_if_new_purchase=0,cases_with_non_dominated_cooperation=0)
 for c in cases:
  options=c['live_options'];coops=[r for r in options if r['success'] and r.get('cooperation_actions',0)>0];ordinary=[r for r in options if not r.get('cooperation_actions',0)]
  survivors=0
  for r in coops:
   owned=next((a for a in ordinary if dominates(a,r,False)),None);purchase=next((a for a in ordinary if dominates(a,r,True)),None)
   row['cooperation_attempts']+=1;row['dominated_if_owned']+=owned is not None;row['dominated_if_new_purchase']+=purchase is not None;survivors+=owned is None
   if len([e for e in examples if e['mission']==mid])<2 and owned:examples.append(dict(mission=mid,party=c['party'],cooperation=r,ordinary=owned))
  row['cases_with_non_dominated_cooperation']+=survivors>0
 rows.append(row)
out=dict(scope='Compare sampled successful full-map plans, all task schedules and tool alternatives available in each named configuration. Non-dominated is not proof of global optimality or fun. Costs are separate dimensions; no fabricated preference weights.',rows=rows,ordinary_dominance_examples=examples,baseline_configurations=M['configurations'],baseline_unfound=len(M['unfound']))
(O/'player-choice-dominance.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(rows)
