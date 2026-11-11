"""Structural integrity checks; these do not certify narrative quality or balance."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
def read(name): return json.loads((ROOT/'data'/name).read_text())
chars=read('characters.json'); rel=read('initial_relationships.json'); missions=read('mission_registry.json')
checks=[]
def check(name,condition):
    if not condition: raise AssertionError(name)
    checks.append(name)
ids={c['id'] for c in chars}
check('eight unique character IDs',len(ids)==len(chars)==8)
check('all 56 crew directions and eight leader directions exist', {(r['observer'],r['target']) for r in rel} == {(a,b) for a in ids for b in ids|{'leader'} if a!=b})
check('relationship IDs are unique',len({r['id'] for r in rel})==64)
check('initial stats stay in range',all(0<=r[k]<=100 for r in rel for k in ('grudge','trust','closeness')))
check('old grievances include reason and matching categories',all(r['history'] and r['grudge_categories'] for r in rel if r['grudge']))
check('personal arcs and distinct endings planned for everyone',all(len(c['arc'])==3 and len(c['endings'])==3 for c in chars))
check('three initial crew and five later recruits',sum(c['join']==1 for c in chars)==3 and sum(c['join']>1 for c in chars)==5)
byid={m['id']:m for m in missions}
check('24 main and 12 side outlines',len(byid)==36 and sum(m['kind']=='main' for m in missions)==24)
check('all mission dependencies exist',all(p in byid for m in missions for p in m['prerequisite_resolved']))
done=set()
while True:
    ready={m['id'] for m in missions if all(p in done for p in m['prerequisite_resolved'])}
    if ready<=done: break
    done|=ready
check('dependency graph acyclic and all mission outlines reachable',done==set(byid))
check('main progression depends on resolution, not winning',all(m['failure_continues'] for m in missions if m['kind']=='main'))
check('every mission has explicit baseline fallback',all(m['baseline_fallback'] for m in missions))
check('all later characters have a matching recruit beat',all(c['id'] in byid[f'M{c["join"]:02}']['recruits'] for c in chars if c['join']>1))
check('side missions do not unlock required recruits',all(not m['recruits'] for m in missions if m['kind']=='side'))
req=read('requirements.json')
check('requirements have acceptance conditions and honest status',len({r['id'] for r in req})==len(req)==36 and all(r['acceptance'] and r['status']=='specified_not_implemented' for r in req))
check('six enemies and twelve equipment archetypes',len(read('enemies.json'))==6 and len(read('equipment.json'))==12)
rules=read('rules.json'); flow=read('campaign_flow.json'); event=read('event_contract_example.json')
thresholds=rules['progression']['cumulative_xp_thresholds']
check('level thresholds are strictly increasing and cover all levels',len(thresholds)==rules['progression']['max_level'] and all(a<b for a,b in zip(thresholds,thresholds[1:])))
edges=flow['transitions']; nodes={e['from'] for e in edges}|{e['to'] for e in edges}
reachable={flow['start']}
while True:
    more={e['to'] for e in edges if e['from'] in reachable}
    if more<=reachable:break
    reachable|=more
check('all campaign phases and ending reachable in declared graph',reachable==nodes and flow['terminal'] in reachable)
to_end={flow['terminal']}
while True:
    more={e['from'] for e in edges if e['to'] in to_end}
    if more<=to_end:break
    to_end|=more
check('all declared phases have a path to ending',to_end==nodes)
check('main and side failure states have settlement transitions',all(any(e['from']==p and 'failure' in e['on'] for e in edges) for p in ('main_mission','side_mission')))
check('example event roles exist and responsibility is normalized',set(event['required_roles'])<=ids and all(sum(c.get('responsibility',{}).values())<=1 for c in event['choices']))
check('ending fallback exists and has no evidence lock',rules['endings']['fallback'] in rules['endings']['world_routes'] and flow['required_recovery_paths']['failed_final_objective']=='evacuation_ending')
check('all side offers precede the final main mission',all(m['day']<flow['max_main_days'] for m in missions if m['kind']=='side'))
check('final result settles directly into ending',any(e['from']=='main_settlement' and e['to']=='ending' and e['on']=='commit_unique_main_result_when_current_day_equals_24' for e in edges))
check('post-main side phase excludes final day',all('less_than_24' in e['on'] for e in edges if e['from']=='main_settlement' and e['to']=='side_offer'))
check('trust can be earned without already unlocking advanced cooperation',rules['relationship']['trust_reward_requires_advanced_protocol'] is False and any('universal basic actions' in c for c in rules['relationship']['trust_reward_conditions']))
report={'passed_count':len(checks),'checks':checks,'limitations':'Reference and reachability checks only; mission layouts, full scripts, final numbers and playtime are not implemented or certified.'}
(ROOT/'docs'/'design-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
