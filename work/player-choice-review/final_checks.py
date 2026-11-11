from pathlib import Path
import runpy,json,hashlib
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design';O=ROOT/'outputs'
def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*.json')}
before=hashes();runpy.run_path(str(ROOT/'work/player-choice-review/apply_design.py'));assert before==hashes(),'0.11 reapplication changed authored state'
class Doc(HTMLParser):
 def __init__(self,p):super().__init__();self.ids=[];self.links=[];self.feed(p.read_text())
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if t=='a' and 'href'in a:self.links.append(a['href'])
n=1
for name in ['player-choice-review.html','full-game-design.html']:
 p=O/name;d=Doc(p);assert len(d.ids)==len(set(d.ids));n+=1
 for h in d.links:
  u=urlsplit(h)
  if u.scheme:continue
  target=p.parent/unquote(u.path) if u.path else p;assert target.exists(),h;n+=1
  if u.fragment and target.suffix=='.html':assert unquote(u.fragment) in Doc(target).ids,h;n+=1
runtime={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and f.suffix in ['.gd','.tscn','.godot'] and '.godot' not in f.parts}
assert runtime==json.loads((ROOT/'work/tactical-review/runtime-before.json').read_text());n+=1
(O/'player-choice-final-checks.json').write_text(json.dumps(dict(version='0.11',passed_count=n,result='PASS',runtime_unchanged=True,design_sha256=hashes()),ensure_ascii=False,indent=2)+'\n');print('0.11 artifact checks:',n)
