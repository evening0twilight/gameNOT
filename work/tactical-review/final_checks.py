"""Final design artifact consistency, idempotence, and no-runtime-change checks."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import json,hashlib,runpy,contextlib,io
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design';O=ROOT/'outputs'
checks=[]
def check(n,v):assert v,n;checks.append(n)
def hashes(base):return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.glob('*.json')}
before=hashes(D)
with contextlib.redirect_stdout(io.StringIO()):runpy.run_path(str(ROOT/'work/tactical-review/apply_design.py'))
check('reapplying0.7does not accumulate or change definitions',before==hashes(D))
before=hashes(D)
with contextlib.redirect_stdout(io.StringIO()):runpy.run_path(str(ROOT/'work/integrated-review/apply_design.py'))
check('reapplying0.9does not accumulate or change definitions',before==hashes(D))
before=hashes(D)
with contextlib.redirect_stdout(io.StringIO()):runpy.run_path(str(ROOT/'work/approach-review/apply_design.py'))
check('reapplying0.10does not accumulate or change definitions',before==hashes(D))
runtime={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and f.suffix in ['.gd','.tscn','.godot'] and '.godot' not in f.parts}
check('no production script scene or project setting modified',runtime==json.loads((ROOT/'work/tactical-review/runtime-before.json').read_text()))
class Links(HTMLParser):
 def __init__(self,text):super().__init__();self.ids=[];self.links=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and 'href' in a:self.links.append(a['href'])
for name in ['tactical-playability-review.html','full-game-design.html','systematic-logic-audit.html','integrated-design-review.html','approach-design-review.html']:
 p=O/name;doc=Links(p.read_text());check(name+' unique anchors',len(doc.ids)==len(set(doc.ids)))
 for href in doc.links:
  url=urlsplit(href)
  if url.scheme:continue
  target=p.parent/unquote(url.path) if url.path else p
  check(name+' local link '+href,target.exists())
  if url.fragment and target.suffix=='.html':check(name+' anchor '+href,unquote(url.fragment) in Links(target.read_text()).ids)
combat=json.loads((D/'combat.json').read_text());integ=json.loads((D/'integration.json').read_text())
check('no repeated movement policy',integ['stacking_rules'].count('空手基础3')==1)
check('hard limits have single authored source',combat['difficulty']['hard'].get('deadline_source')=='board.hard_round_limit' and 'deadline_bonus' not in combat['difficulty']['hard'])
check('carrying geometry acknowledges explicit exceptions','xu_5' in combat['geometry']['movement'])
matrix=json.loads((O/'tactical-matrix-results.json').read_text())
check('hard baseline witnesses retain stated2roundmargin',all(c['limit']-c['rounds']>=2 for c in matrix['cases'] if c['difficulty']=='hard'))
check('all four strategy attempts retained including failures',len(matrix['strategy_runs'])==1104 and len(matrix['failed_policy_attempts'])==2)
out={'version':'0.10-approach-review','result':'PASS','passed_count':len(checks),'checks':checks,'design_sha256':hashes(D),'runtime_unchanged':True,'formal_development':'paused_by_user','scope':'artifact and design consistency; no human playtest claim'}
(O/'tactical-final-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Final0.10artifact checks:',len(checks),'passed; runtime unchanged.')
