from pathlib import Path
import json,collections
R=Path(__file__).resolve().parents[2];O=R/'outputs'
d=json.loads((O/'training-campaigns.json').read_text());rows=d['scenarios']
def key(r):return tuple(r['spec'][k] for k in ['training_actor','formation','exposure','difficulty','variant'])
def met(r):return dict(wins=sum(b['success'] for b in r['battles']),rounds=sum(b['rounds'] for b in r['battles']),damage=sum(b['damage'] for b in r['battles']),ap=sum(b['ap'] for b in r['battles']),missions=len(r['battles']))
groups=collections.defaultdict(dict)
for r in rows:groups[key(r)][r['spec']['training_rule']]=r
print('ACTUAL',d['actual_battles'],'groups',len(groups))
for mode in ['legacy','current']:
 print(mode,{k:collections.Counter('better' if (met(g[mode])[k]>met(g['none'])[k] if k=='wins' else met(g[mode])[k]<met(g['none'])[k]) else 'same' if met(g[mode])[k]==met(g['none'])[k] else 'worse' for g in groups.values()) for k in ['wins','damage','rounds']})
 print('TRAIN',sum(sum(x['kind']=='training' for x in g[mode]['receipts']) for g in groups.values()))
for who in ['lin','xu','su','chen','ye','he','mo','jiang']:
 cases=[g for k,g in groups.items() if k[0]==who];cf=[(r,b,b['without_paid_growth']) for g in cases for r in [g['current']] for b in r['battles'] if b.get('without_paid_growth')]
 print('ROLE',who,'cf',len(cf),'wins+',sum(b['success'] and not q['success'] for r,b,q in cf),'wins-',sum(q['success'] and not b['success'] for r,b,q in cf),'damage+',sum(b['damage']<q['damage'] for r,b,q in cf),'services+',sum(b['service_secured'] and not q['service_secured'] for r,b,q in cf),'newskills',sum(bool(set(b['skill_action_types'])-set(q['skill_action_types'])) for r,b,q in cf))
 print('examples',[(r['spec']['name'],b['mission'],b['levels'][who],q['levels'][who],b['success'],q['success'],b['damage'],q['damage'],b['rounds'],q['rounds'],b['skill_action_types'],q['skill_action_types']) for r,b,q in cf if b['success'] and not q['success'] or b['damage']<q['damage']][:3])
m=json.loads((O/'training-mentorship.json').read_text())['scenarios']
for r in m:
 z=[x for x in r['receipts'] if x['kind']=='mentorship']
 if z:print('MENTOR',r['spec']['name'],z)
