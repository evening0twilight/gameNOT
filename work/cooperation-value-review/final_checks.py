from pathlib import Path
import json,hashlib,runpy
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*.json')}
before=hashes();runpy.run_path(str(ROOT/'work/cooperation-value-review/apply_design.py'));assert before==hashes()
checks=['current scope reapplication is idempotent']
class Doc(HTMLParser):
 def __init__(self,p):super().__init__();self.ids=[];self.links=[];self.feed(p.read_text())
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if t=='a' and 'href'in d:self.links.append(d['href'])
for name in ['cooperation-value-review.html','full-game-design.html']:
 p=O/name;d=Doc(p);assert len(d.ids)==len(set(d.ids));checks.append(name+'unique anchors')
 for h in d.links:
  u=urlsplit(h)
  if u.scheme:continue
  target=p.parent/unquote(u.path) if u.path else p;assert target.exists(),h;checks.append(name+':'+h)
  if u.fragment and target.suffix=='.html':assert unquote(u.fragment) in Doc(target).ids,h
runtime={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and (f.suffix in ['.gd','.tscn'] or f.name=='project.godot')}
assert runtime==json.loads((ROOT/'work/cooperation-value-review/runtime-before.json').read_text());checks.append('runtime unchanged')
master=(O/'full-game-design.html').read_text();assert '可实施设计 0.12' in master and '第5级将第一专长每任务次数从2提高到3' in master
checks.append('master publishes current growth and scope')
(O/'cooperation-artifact-checks.json').write_text(json.dumps(dict(version='0.12',passed=len(checks),checks=checks,runtime_unchanged=True,design_sha256=hashes()),ensure_ascii=False,indent=2)+'\n');print('ARTIFACT CHECKS',len(checks))
