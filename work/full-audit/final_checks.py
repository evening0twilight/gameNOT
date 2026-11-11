from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design';O=ROOT/'outputs';checks=[]
def read(n):return json.loads((D/n).read_text())
def check(n,v):assert v,n;checks.append(n)
for n in ['production_scope.json','player_choice_contract.json','growth_identity_contract.json','full_audit_contract.json','design_manifest.json']:
 check(n+' has current revision',read(n)['version'].startswith('0.14'))
scope=read('production_scope.json');abilities=read('abilities.json');gear=read('equipment.json')['items'];manifest=read('design_manifest.json')
check('Current active filters match16skills and7equipment',set(scope['abilities'])=={x['id'] for x in abilities if x.get('production_status')=='active'} and set(scope['equipment'])=={x['id'] for x in gear if x.get('production_status')=='active'} and len(scope['abilities'])==16 and len(scope['equipment'])==7)
for name in manifest['domains'].values():check('Domain source exists '+name,(D/name).exists())
c=read('combat.json');i=read('integration.json');check('Carrying exceptions have one current meaning',i['logical_audit_sections']['combat_resolution']['carrying_actions']==c['carrying_exception'])
check('Historical trust gate removed from current contradiction table',not any('双方60信任' in row[1] for row in i['resolved_contradictions']))
check('WorkshopII has a usable medical benefit',all(x in next(f['tier2'] for f in read('facilities.json') if f['id']=='workshop') for x in ['单品上限2→3','急救包每任务次数2→3','总容量仍3']))
check('Guide describes fixed specialties instead of deleted loadout choice','固定专长' in next(x['copy'] for x in read('player_experience_contract.json')['guides'] if x['id']=='G09'))
check('Narrative capacity explicitly distinguishes core and optional',all(x in read('stories.json')['scheduler']['capacity_notice'] for x in ['46','36','18','未读不扣好感']))
v=json.loads((O/'full-audit-checks.json').read_text());check('Current regression completed and all active actions covered',v['passed']>=195 and len(v['active_action_coverage'])==23)
m=json.loads((O/'full-audit-matrix.json').read_text());check('All1718named/baseline contexts succeeded',len(m['named'])==1432 and len(m['baseline'])==276 and all(x['success'] for x in m['named']+m['baseline']))
campaigns=json.loads((O/'full-audit-campaigns.json').read_text());check('Four full campaigns and132task transitions completed',len(campaigns['scenarios'])==4 and campaigns['actual_battles']==132 and all(x['summary']['main_count']==24 for x in campaigns['scenarios']))
check('Final failed campaign actually ends in evacuation',campaigns['scenarios'][-1]['summary']['world_ending']=='evacuation' and not campaigns['scenarios'][-1]['battles'][-1]['success'])
check('All reused subsystem scripts succeeded',all(x['exit_code']==0 for x in json.loads((O/'full-audit-subsystems.json').read_text())))
for name in ['full-audit-review.html','full-game-design.html']:
 text=(O/name).read_text();check(name+' current content',all(x in text for x in ['0.14','F10','工坊II','全量审查' if name=='full-audit-review.html' else '全域审查0.14（当前）']))
 for href in re.findall(r'href="([^"#]+)"',text):
  if href.startswith(('http:','https:','mailto:')):continue
  check(name+' relative link '+href,(O/href.split('#')[0]).exists())
inputs=json.loads((O/'full-audit-inputs.json').read_text());check('Report accompanies current normative data',all(hashlib.sha256((D/n).read_bytes()).hexdigest()==h for n,h in inputs['data_sha256'].items()))
before=json.loads((ROOT/'work/full-audit/runtime-before.json').read_text());after={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and (f.suffix in ['.gd','.tscn'] or f.name=='project.godot')};check('Production runtime untouched',before==after)
(O/'full-audit-final-checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks),ensure_ascii=False,indent=2)+'\n');print('FINAL ARTIFACT CHECKS',len(checks))
