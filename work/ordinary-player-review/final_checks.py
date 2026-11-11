from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import defaultdict,Counter
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';F=ROOT/'game/data/final_design';checks=[]
def read(p):return json.loads(p.read_text())
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
for name in ['ordinary-player-review.html','character-script-final.html','full-game-design.html']:
 p=O/name;doc=Document();doc.feed(p.read_text());check(name+' uniqueIDs',len(doc.ids)==len(set(doc.ids)))
 for link in doc.links:
  u=urlsplit(link)
  if u.scheme:continue
  if u.path and not u.path.endswith('ordinary-player-final-checks.json'):check(name+' link '+link,(p.parent/unquote(u.path)).exists())
  elif u.fragment:check(name+' anchor '+u.fragment,u.fragment in doc.ids)
 if name.startswith('character'):
  check('Reader96scenes',doc.scenes==96);q=ROOT/'work/ordinary-player-review/reader-check.js';q.write_text('\n'.join(doc.scripts));subprocess.run(['node','--check',str(q)],check=True)
  check('Injuryandresponsibilityreaderpresent','确证共同责任' in p.read_text() and '暂时重伤：替换' in p.read_text())
m=read(F/'design_manifest.json');check('Currentmanifest0.16',m['version'].startswith('0.16'))
for key,path in m['domains'].items():check('Domain '+key,(F/path).exists())
x=read(O/'ordinary-player-inputs.json')
for path,digest in (x['design_sha256']|x['reference_sha256']).items():check('Input fingerprint '+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest)
r=read(O/'ordinary-player-after-routes.json')['rows'];check('15704independentexecutions',len(r)==15704)
check('Separatecoverageaxes',Counter(x['layer'] for x in r)=={'structural':4248,'rosters':11456})
groups=defaultdict(list)
for a in r:
 if a['layer']=='rosters':groups[(a['mission'],tuple(a['goals']),a['branch'],tuple(a['party']),a['level'])].append(a['success'])
check('1432trio-goalcontextsperlevel',len(groups)==2864)
check('Eachtriogoallevelhasanordinarysuccess',all(any(v) for v in groups.values()))
check('All36boardscovered',len({x['mission'] for x in r})==36)
for file,count in [('ordinary-player-after-campaigns.json',108),('ordinary-player-growth.json',30)]:
 d=read(O/file);check(file+' count',len(d['scenarios'])==count);check(file+' countedbattles',sum(len(r['battles']) for r in d['scenarios'])==d['actual_battles']);check(file+' everycampaignends',all(r['summary']['main_count']==24 for r in d['scenarios']));check(file+' nonnegativeobservedbudget',all(all(v>=0 for v in p['resources'].values()) for r in d['scenarios'] for p in r['pressure']))
current=read(O/'ordinary-player-after-campaigns.json')['scenarios'];check('Threeendings36each',Counter(r['summary']['world_ending'] for r in current)==dict(evacuation=36,distributed_rebuild=36,shared_control=36))
a=read(O/'ordinary-player-opportunities.json');check('384specialtycontexts768executions',len(a['rows'])==384 and a['trials']==768);check('Stalehintfailuregone',not any(r['states']['False']['success'] and not r['states']['True']['success'] for r in a['rows']))
t=read(O/'ordinary-player-checks.json');check('716rulespassed',t['passed']==716 and len(t['checks'])==716);check('2352dialoguestates',t['dialogue_combinations']==2352)
old=read(ROOT/'work/ordinary-player-review/runtime-before.json');new={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'game').rglob('*') if p.is_file() and (p.suffix in ['.gd','.tscn'] or p.name=='project.godot')};check('Formalruntimebyteidentical',old==new)
check('Mastercurrentsectionfirst',(O/'full-game-design.html').read_text().index('ORDINARY_START')<(O/'full-game-design.html').read_text().index('historical-015'))
result=dict(version='0.16',passed=len(checks),checks=checks,html_validation='Structural parsing, IDs, links and reader JavaScript syntax only. No visual or human UI validation claimed.',route_successes=sum(r['success'] for r in r),formal_runtime_changed=False)
(O/'ordinary-player-final-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('ARTIFACT CHECKS',len(checks))
