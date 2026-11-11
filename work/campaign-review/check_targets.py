from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
B=json.loads((D/'boards.json').read_text())['boards'];E=json.loads((D/'equipment.json').read_text())['items'];checks=[];examples=[]
def check(n,v):assert v,n;checks.append(n)
for b in B:
 s=b['environment']['water_addition']['source'];x,y=s['cell'];check(b['id']+' leak is an explicit accessible overlay',0<=x<8 and 0<=y<8 and b['rows'][y][x] not in '#X')
 check(b['id']+' ignition only targets traversable cells',all(b['rows'][y][x] not in '#X' for x,y in b['environment']['fire_pulse']['cells']))
for e in E:
 candidates=[]
 for b in B:
  if b['day']<e['unlocked_after_main'] or (b['kind']=='main' and b['day']==e['unlocked_after_main']):continue
  matches=[]
  for o in b['objectives']:
   if set(e['valid_target_tags'])&set(o['interaction_tags']):matches.append(o['id'])
  if e['id']=='foam' and b['environment']['water_addition']['source']['targetable']:matches.append(b['id']+'_leak')
  if e['id']=='extinguisher' and (b['environment']['fire_pulse']['cells'] or any(x['type']=='welder' for x in b['enemies'])):matches.append('announced_fire_or_welder')
  if e['id']=='insulation' and any('~' in row for row in b['rows']):matches.append('existing_shallow_water')
  if e['id']=='winch' and any('X' in row for row in b['rows']):matches.append('single_gap_anchor_geometry')
  if e['id']=='medkit' and b['enemies']:matches.append('standing_hero_after_damage; conditional_not_initial_state')
  if e['id']=='shield':matches.append('empty_walkable_tile')
  if e['id']=='scanner' and b['controls']:matches.extend(o['id'] for o in b['controls'])
  if e['id']=='beacon' and any(x['type'] in ['scout','relay'] for x in b['enemies']):matches.append('dry_tile_for_next_scout_intent')
  if e['id']=='stretcher' and any(o['kind']=='rescue' for o in b['objectives']):matches.append('actor_carrying_stabilized_casualty')
  if matches:candidates.append({'mission':b['id'],'targets':matches})
 check(e['id']+' has a defined use after its actual unlock',bool(candidates));examples.append({'item':e['id'],'unlocked_after_main':e['unlocked_after_main'],'example':candidates[0],'matching_encounters':len(candidates)})
(ROOT/'outputs/equipment-target-review.json').write_text(json.dumps({'passed_count':len(checks),'checks':checks,'examples':examples,'scope':'Static target existence and unlock timing. Does not prove utility, optimal cost or live tactical reachability for every item.'},ensure_ascii=False,indent=2)+'\n')
print('Equipment target and unlock checks:',len(checks))
