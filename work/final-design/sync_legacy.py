"""Keep the existing final-product project aligned without claiming new runtime implementation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data';F=D/'final_design'
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
B={b['id']:b for b in read(F/'boards.json')['boards']}
p=read(D/'product.json');p['design_version']='0.4-implementable-content-baseline';p['design_authority']='data/final_design/';p['implementation_status']='完整内容与系统设计基线已编写；Godot仍为基础工程，尚非可玩完整战役';save(D/'product.json',p)
missions=read(D/'mission_registry.json')
for m in missions:
 b=B[m['id']];m['status']='coordinate_board_and_objective_contract_authored_runtime_pending';m['board_ref']='final_design/boards.json#'+m['id'];m['objective']=' / '.join(o['label'] for o in b['objectives'] if o['id'] in {i for g in b['mandatory_groups'] for i in g});m['optional_objective']='、'.join(b['optional']) or '无';m['baseline_fallback']='已定义通用停机开关、目标坐标与基础搬运/互动路径；具体见board_ref'
save(D/'mission_registry.json',missions)
r=read(D/'rules.json');r['status']='0.4 design baseline; parameters require runtime playtesting';r['authoritative_combat']='final_design/combat.json';r['authoritative_progression']='final_design/progression_relationship.json';r['authoritative_facilities']='final_design/facilities.json';r['tactical']['action_ap']['leave_site']=1;r['tactical']['action_ap']['emergency_retreat']=0;save(D/'rules.json',r)
equip=read(D/'equipment.json');new={e['id']:e for e in read(F/'equipment.json')['items']}
for e in equip:
 e['effect']=new[e['id']]['effect'];e['slot']=new[e['id']]['slot'];e.pop('weight',None);e['status']='complete_design_definition_runtime_pending';e['definition_ref']='final_design/equipment.json#'+e['id']
save(D/'equipment.json',equip)
enemies=read(D/'enemies.json');new={e['id']:e for e in read(F/'enemies.json')}
for e in enemies:e['hp']=new[e['id']]['hp'];e['intent']=new[e['id']]['rule'];e['status']='complete_design_definition_runtime_pending';e['definition_ref']='final_design/enemies.json#'+e['id']
save(D/'enemies.json',enemies)
world=read(D/'campaign_world_contract.json');world['version']='0.4';world['authoritative_objectives']='final_design/boards.json';world['mission_specific_override']={'M17':read(F/'integration.json')['M17_override'],'M24':read(F/'integration.json')['M24_override']};world['record_review_facility_override']='通信台一级新增第18日窗口，二级每项目可核查2份；否则20/22/23日每项目1份。';save(D/'campaign_world_contract.json',world)
economy=read(D/'campaign_economy_contract.json');economy['version']='0.4';economy['camp']['free_short_scenes']=2;economy['camp']['conversation']['uses_project']='Only substantive personal plan/repair work; short story reading uses free two-scene window.';economy['facility_effects_ref']='final_design/facilities.json';economy['equipment_costs_ref']='final_design/equipment.json';save(D/'campaign_economy_contract.json',economy)
state=read(ROOT/'game/docs/development.json');state['design_version']='0.4';state['logical_closure_status']='SPECIFIED_WITH_COORDINATE_CONTENT_AND_REFERENCE_CHECKS; NOT_FULL_RUNTIME_OR_PLAYER_VALIDATION';state['authored_this_revision']=['36 coordinate boards and 46 mandatory goal combinations','24 personal branching nodes and 72 supporting narrative nodes','24 specialties, 12 equipment definitions, 4 cooperation protocols, 8 facility tiers','Concrete receipt semantics, 8 story obligation verifiers and 9 directed historical repair routes','One executable M02 reference combat subset, independent from the Godot runtime'];state['design_authority']='data/final_design/';state['not_implemented']=['Playable Godot campaign/tactical controllers and all rule adapters for v0.4','Godot event receipt issuance, previews, UI, animations and content presentation','Full runtime combat traversal across 36 boards and all ability combinations','Final prose polish, scene art, audio and accessibility implementation','Save migrations and Windows real-device verification'];state['design_verification']={'content_checks':'../../outputs/final-design-validation.json','combat_example':'../../outputs/combat-design-example.json','story_checks':'../../outputs/story-contract-checks.json'};save(ROOT/'game/docs/development.json',state)
audit=read(ROOT/'game/docs/logic-audit.json');audit['current_revision']='0.4';audit['current_design_authority']='data/final_design/';audit['overall_status']='COORDINATE_BOARDS_AND_BRANCH_RULES_AUTHORED; REFERENCE_CHECKS_PASS; FULL_RUNTIME_AND_PLAYER_VALIDATION_PENDING';audit['revision_resolutions']=read(F/'integration.json')['resolved_contradictions'];audit['prior_findings_note']='Earlier finding records describe the historical v0.2/v0.3 audit; current content status is specified in final_design and revision_resolutions.';save(ROOT/'game/docs/logic-audit.json',audit)
print('Synchronized primary project data and honest implementation status to v0.4.')
