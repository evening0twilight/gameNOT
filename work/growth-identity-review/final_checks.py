from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design';checks=[]
def check(n,v):assert v,n;checks.append(n)
for f in ['production_scope.json','player_choice_contract.json','growth_identity_contract.json']:
 check(f+' current version',json.loads((D/f).read_text())['version'].startswith('0.13'))
A=json.loads((D/'abilities.json').read_text());S=json.loads((D/'production_scope.json').read_text())
check('16 active specialties, eight upgrades, seven equipment',len(S['abilities'])==16 and sum('level5_effect' in a for a in A)==8 and len(S['equipment'])==7)
check('Ye dangerous output specification and action cost align',next(a for a in A if a['id']=='ye_1')['ap']==2)
for name in ['growth-identity-review.html','full-game-design.html']:
 s=(O/name).read_text();check(name+' has current form and content',all(t in s for t in ['0.13','俯视2D','带教','AP转交','S11']))
 for href in re.findall(r'href="([^"#]+)"',s):
  if href.startswith(('http:','https:','mailto:')):continue
  check(name+' link '+href,(O/href.split('#')[0]).exists())
check('Master currently filters retired active skills', '第1/3级获得两项固定专长，第5级强化其中一项' in (O/'full-game-design.html').read_text())
sel=json.loads((O/'growth-identity-selective-campaigns.json').read_text())['scenarios']
for s in sel:
 q=s['summary'];check(q['name']+' all36 objectives and no permanent losses',len(s['battles'])==36 and all(b['success'] for b in s['battles']) and not q['withdrawn']);check(q['name']+' only one deliberately selected mentorship',q['positive_relationships']['mentoring']==1)
a,b=sel;check('Selective docking costs3 net and improves sampled mission one round',a['summary']['resources']['supplies']-b['summary']['resources']['supplies']==3 and sum(x['rounds'] for x in a['battles'])-sum(x['rounds'] for x in b['battles'])==1)
before=json.loads((ROOT/'work/growth-identity-review/runtime-before.json').read_text());after={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and (f.suffix in ['.gd','.tscn'] or f.name=='project.godot')};check('Formal runtime unchanged',before==after)
(O/'growth-identity-final-checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks),ensure_ascii=False,indent=2)+'\n');print('FINAL CHECKS',len(checks))
