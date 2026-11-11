from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';F=ROOT/'game/data/final_design';checks=[]
def check(n,b):assert b,n;checks.append(n)
class Document(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.scenes=0;self.scripts=[];self.in_script=False
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag=='a' and d.get('href'):self.links.append(d['href'])
  if tag=='details' and d.get('class')=='scene':self.scenes+=1
  if tag=='script':self.in_script=True
 def handle_endtag(self,t):
  if t=='script':self.in_script=False
 def handle_data(self,d):
  if self.in_script:self.scripts.append(d)
for name in ['player-ready-review.html','character-script-final.html']:
 p=O/name;doc=Document();doc.feed(p.read_text());check(name+' uniqueIDs',len(doc.ids)==len(set(doc.ids)))
 for link in doc.links:
  u=urlsplit(link)
  if u.scheme:continue
  if u.path:check(name+' link '+link,(p.parent/unquote(u.path)).exists())
  elif u.fragment:check(name+' anchor '+u.fragment,u.fragment in doc.ids)
 if name.startswith('character'):
  check('Reader has96actualscene sections',doc.scenes==96)
  q=ROOT/'work/player-ready-review/reader-check.js';q.write_text('\n'.join(doc.scripts));subprocess.run(['node','--check',str(q)],check=True)
manifest=json.loads((F/'design_manifest.json').read_text());check('Manifest current0.15',manifest['version'].startswith('0.15'))
for key,path in manifest['domains'].items():check('Domain exists '+key,(F/path).exists())
x=json.loads((O/'player-ready-inputs.json').read_text())
for path,digest in (x['design_sha256']|x['reference_sha256']).items():check('Evidence fingerprint '+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest)
for name in ['matrix','baseline','focused','campaigns','checks']:
 d=json.loads((O/f'player-ready-{name}.json').read_text());check(name+' current result version',d['version']=='0.15')
c=json.loads((O/'player-ready-campaigns.json').read_text());check('8earnedcampaigns252battles',len(c['scenarios'])==8 and c['actual_battles']==252)
check('Everyrealcampaignreaches24main',all(r['summary']['main_count']==24 for r in c['scenarios']))
check('Noactualcampaignnegativebudget',all(all(v>=0 for v in r['summary']['resources'].values()) for r in c['scenarios']))
for file in ['game/data/characters.json','game/data/final_design/abilities.json']:
 d=json.loads((ROOT/file).read_text());check(file+' readableJSON',bool(d))
old=json.loads((ROOT/'work/player-ready-review/runtime-before.json').read_text());new={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'game').rglob('*') if p.is_file() and (p.suffix in ['.gd','.tscn'] or p.name=='project.godot')};check('Formalruntimebyteidentical',old==new)
result=dict(version='0.15',passed=len(checks),checks=checks,html_validation='Structural parsing, IDs, links and reader JavaScript syntax only. Browser file preview blocked by URL security policy; no visual/UI validation claimed.')
(O/'player-ready-final-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('ARTIFACT CHECKS',len(checks))
