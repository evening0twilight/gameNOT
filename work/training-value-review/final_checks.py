from pathlib import Path
import json,hashlib,collections
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';F=ROOT/'game/data/final_design';checks=[]
def read(p):return json.loads(p.read_text())
def check(n,b):assert b,n;checks.append(n)
class Doc(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if 'id' in d:self.ids.append(d['id'])
  if t=='a' and d.get('href'):self.links.append(d['href'])
for name in ['training-value-review.html','full-game-design.html']:
 p=O/name;d=Doc();d.feed(p.read_text());check(name+' IDs unique',len(d.ids)==len(set(d.ids)))
 for link in d.links:
  u=urlsplit(link)
  if u.scheme:continue
  if u.path and not u.path.endswith('training-final-checks.json'):check(name+' file '+link,(p.parent/unquote(u.path)).exists())
  elif u.fragment:check(name+' anchor '+u.fragment,u.fragment in d.ids)
for name,count in [('training-campaigns',576),('training-specialty',64),('training-mentorship',24),('training-general-campaigns',108),('training-planned',96)]:
 d=read(O/(name+'.json'));check(name+' scenariocount',len(d['scenarios'])==count);check(name+' actualbattlecount',d['actual_battles']==sum(len(r['battles']) for r in d['scenarios']));check(name+' all36boardscovered',len({b['mission'] for r in d['scenarios'] for b in r['battles']})==36)
 check(name+' allreach24main',all(r['summary']['main_count']==24 for r in d['scenarios']));check(name+' nonnegativeobservedresources',all(all(v>=0 for v in p['resources'].values()) for r in d['scenarios'] for p in r['pressure']))
d=read(O/'training-campaigns.json');groups=collections.defaultdict(dict)
for r in d['scenarios']:
 s=r['spec'];k=tuple(s[x] for x in ['training_actor','formation','exposure','difficulty','variant']);groups[k][s['training_rule']]=r
 check('Exposureflag '+s['name'],s['sides']==('all' if s['exposure']=='all' else False))
check('192matchedcomparisoncontexts',len(groups)==192 and all(set(g)=={'none','legacy','current'} for g in groups.values()))
for k,g in groups.items():
 specs=[{x:v for x,v in r['spec'].items() if x not in ['name','training_rule','training']} for r in g.values()];check('Sameinputsacrosspaidchoice '+str(k),all(x==specs[0] for x in specs))
 for mode,r in g.items():
  if mode=='current':
   for a,n in r['summary']['xp'].items():
    paid=sum(x.get('gains',{}).get(a,0) for x in r['receipts'] if x['kind']=='training_gain');check('CurrentpaidXPbounded '+r['spec']['name']+'/'+a,paid<=48)
old={r['spec']['name']:r for r in read(O/'ordinary-player-after-campaigns.json')['scenarios']};new=read(O/'training-general-campaigns.json')['scenarios'];untouched=[r for r in new if r['spec']['behavior'] in ['main_only','dismantler']]
check('36untrainedcampaignsunchanged',len(untouched)==36 and all(r['battles']==old[r['spec']['name']]['battles'] and r['summary']['resources']==old[r['spec']['name']]['summary']['resources'] and r['summary']['levels']==old[r['spec']['name']]['summary']['levels'] for r in untouched))
proof=read(O/'training-inputs.json')
for path,digest in proof['sha256'].items():check('Input '+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest)
old=read(ROOT/'work/training-value-review/runtime-before.json');new={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'game').rglob('*') if p.is_file() and (p.suffix in ['.gd','.tscn'] or p.name=='project.godot')};check('Formalruntimeunchanged',old==new)
m=read(F/'design_manifest.json');check('Currentmanifest0.17',m['version'].startswith('0.17'))
for k,p in m['domains'].items():check('Manifest '+k,(F/p).exists())
check('1174rulespassed',read(O/'training-checks.json')['passed']==1174)
result=dict(version='0.17',passed=len(checks),checks=checks,formal_runtime_changed=False,validation='HTML structure/links, data coverage, paired inputs, fingerprints and unchanged runtime. No browser preview or human UX test.')
(O/'training-final-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('ARTIFACT CHECKS',len(checks))
