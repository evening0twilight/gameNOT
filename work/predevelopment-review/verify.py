"""Design admission checks; explicitly not a Godot or human acceptance test."""
from pathlib import Path
import json,hashlib,runpy,sys,subprocess,os,collections
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
R=Path(__file__).resolve().parents[2];W=Path(__file__).parent;F=R/'game/data/final_design';O=R/'outputs'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(group,name,condition):
 assert condition,(group,name)
 checks.append(dict(group=group,name=name))
base=read(F/'release_baseline.json');ds=base['domains'];manifest=read(F/'design_manifest.json')
ck('authority','exact baseline version',base['version']==manifest['version']=='0.18-predevelopment')
for key,ref in manifest['domains'].items():ck('authority',key+' pointer',ref=='release_baseline.json#/domains/'+key and key in ds)
for path,key in manifest['generated_views'].items():ck('authority','identical generated view '+path,read(R/path)==ds[key])
ck('authority','runtime not authorized',base['stage']=='design_only' and not base['formal_development_authorized'])
for key,v in ds.items():
 if isinstance(v,dict) and 'version' in v:ck('authority',key+' current version',v['version']==base['version'])
ck('scope','all active abilities only',len(ds['abilities'])==16 and {x['id'] for x in ds['abilities']}==set(ds['scope']['abilities']))
ck('scope','all active equipment only',len(ds['equipment']['items'])==7 and {x['id'] for x in ds['equipment']['items']}==set(ds['scope']['equipment']))
ck('scope','legacy equipment projection',read(R/'game/data/equipment.json')==ds['equipment']['items'])
ck('scope','legacy enemy projection',read(R/'game/data/enemies.json')==ds['enemies'])
ck('scope','four services two investments',set(ds['field_operations']['services'])=={'M05','M10','M21','S11'} and set(ds['field_operations']['investments'])=={'M05','M10'})
rules=read(R/'game/data/rules.json');ck('scope','no learned cooperation flags',rules['progression']['generic_cooperation_trust_min'] is None and not rules['progression']['advanced_protocol_requires_mutual_trust'])
ck('scope','current root rules projection',rules==ds['compatibility_rules'])
ck('economy','product economy identical',ds['product']['start_resources']==ds['economy']['start'] and ds['product']['reward_design']==ds['economy']['main_rewards'])
ck('economy','current initial resources',ds['economy']['start']==dict(credits=30,supplies=6,parts=2))
boards={b['id']:b for b in ds['boards']['boards']};actors={a['id']:a for a in ds['characters']}
ck('content','36 boards,24 main,12 side',len(boards)==36 and sum(b['kind']=='main' for b in boards.values())==24)
for mid,b in boards.items():
 ck('content',mid+'8x8',len(b['rows'])==8 and all(len(r)==8 for r in b['rows']))
 objects={x['id']:x for x in b['objectives']+b['controls']}
 ck('content',mid+' unique objects',len(objects)==len(b['objectives'])+len(b['controls']))
 ck('content',mid+' correct reward owner','objective_rewards' in b['optional_reward_rule'] and '额外+1' not in b['optional_reward_rule'])
 ck('content',mid+' no retired foam logic','foam_rule' not in b['environment']['water_addition'])
 for oid,obj in objects.items():
  ck('content',mid+'/'+oid+' prerequisite IDs',all(k in objects for k in obj['prerequisites']))
  visited=set()
  def dfs(k,stack):
   assert k not in stack,(mid,k,'cycle')
   if k in visited:return
   for parent in objects[k]['prerequisites']:dfs(parent,stack|{k})
   visited.add(k)
  dfs(oid,set())
  ck('content',mid+'/'+oid+' no dependency cycle',True)
 for groups in [b['mandatory_groups'],*b.get('route_groups',{}).values()]:
  ck('content',mid+' valid nonempty goal groups',bool(groups) and all(g and all(k in objects for k in g) for g in groups))
 ck('content',mid+' authored role',mid in ds['field_operations']['mission_roles'])
rewards=ds['economy']['objective_rewards'];tokens=[]
for reward in rewards:
 key=(reward['mission'],reward['objective']);tokens.append(key)
 ck('economy','real reward '+str(key),key[1] in {x['id'] for x in boards[key[0]]['objectives']} and reward['condition']=='secured')
ck('economy','22unique object reward sources',len(tokens)==len(set(tokens))==22)
ck('economy','M02 recovery parts',next(x['reward'] for x in rewards if x['mission']=='M02')=={'parts':2})
for source,target in [('personal_nodes','personal'),('relationship_nodes','relationships'),('community_nodes','community'),('recovery_nodes','life'),('chapter_nodes','chapter')]:
 ck('narrative',source+' exact script IDs',{n['id'] for n in ds['stories'][source]}=={n['id'] for n in ds['scripts'][target]})
ck('narrative','96 full nodes',sum(len(ds['scripts'][k]) for k in ['personal','relationships','community','life','chapter'])==96)
ck('narrative','46 night slots and36 main relationship/personal nodes',23*ds['stories']['scheduler']['camp_short_scenes']==46 and len(ds['stories']['personal_nodes'])+len(ds['stories']['relationship_nodes'])==36)
ck('narrative','orthogonal epilogue',all('overrides_integrated' not in x for x in ds['stories']['ending_resolution']['priority']) and len(ds['scripts']['ending_priority'])==4)
# Abstract day/phase graph, not tactical solvability. Actual low-resource ledger
# and mission simulations are covered by the separately rerun rule/campaign suites.
flow=ds['player_flow']; edges=collections.defaultdict(set);start=(1,'briefing');seen={start};queue=[start]
while queue:
 day,state=queue.pop(0)
 for edge in flow['transitions']:
  if edge['from']!=state:continue
  cond=edge['on']
  if 'less_than_24' in cond and day==24:continue
  if 'equals_24' in cond and day!=24:continue
  nd=day+1 if state=='night' else day; nxt=(nd,edge['to'])
  if state=='ending':continue
  assert nd<=24
  edges[(day,state)].add(nxt)
  if nxt not in seen:seen.add(nxt);queue.append(nxt)
good={(24,'ending')}
while True:
 more={s for s,ns in edges.items() if ns&good}-good
 if not more:break
 good|=more
ck('flow','all campaign phase nodes can reach ending',seen<=good)
ck('flow','no day24 camp or side stage',not any(d==24 and s in ['camp','night','side_offer','side_mission','side_settlement'] for d,s in seen))
for day in range(1,24):ck('flow','D'+str(day)+' skip-side legal', (day,'camp') in edges[(day,'side_offer')])
ck('flow','newgame and load error return paths',any(x['from']=='new_game' and x['to']=='title' for x in flow['transitions']) and any(x['from']=='load_error' and x['to']=='title' for x in flow['transitions']))
ck('flow','critical snapshots listed',any('training_completed' in s for s in ds['persistence_inventory']['snapshot']['campaign']) and any('AP转交已用' in s for s in ds['persistence_inventory']['snapshot']['battle']))
ck('acceptance','design and future acceptance separate',len(ds['acceptance']['criteria'])==18 and sum(x['status']=='pending' for x in ds['acceptance']['criteria'])==12)
ck('scope','16 screens unique',len(ds['release_scope']['screens'])==len({x[0] for x in ds['release_scope']['screens']})==16)
ck('scope','12 location kits',len({b['location'] for b in boards.values()})==12)
gates={x['id'] for x in ds['acceptance']['criteria']}
for requirement in ds['requirements']:ck('acceptance',requirement['id']+' mapped to actual gate',bool(requirement['acceptance_ids']) and set(requirement['acceptance_ids'])<=gates)
# Reuse the current regression's fixtures and add tests for the newly fixed
# per-actor L2 switch; this executes actions, not a mirror of a prose formula.
ns=runpy.run_path(str(W/'regression.py'));fixture=ns['fixture'];CHARS=ns['CHARS']
for actor in CHARS:
 for level in [1,2,3,5,6]:
  for choice in ['work','move']:
   g=fixture(actor,level);h=g.h[0];other=g.h[1];h['l2_choice']=choice;other['l2_choice']='work' if choice=='move' else 'move'
   want=4 if level>=6 or level>=2 and choice=='move' else 3
   ck('l2',actor+str(level)+choice+' personal move',g.budget(h)==want)
   ck('l2',actor+str(level)+choice+' other independent',g.budget(other)==(4 if level>=6 or level>=2 and other['l2_choice']=='move' else 3))
   before=dict(g.gear);g.execute_task(h,dict(target='task',route=[h['p']],steps=0,action='interact',work=4))
   ck('l2',actor+str(level)+choice+' actual work',g.objects['task']['progress']==(2 if level>=6 or level>=2 and choice=='work' else 1))
   ck('l2',actor+str(level)+choice+' no global leakage',g.gear==before)
   g.h[0]['ap']=2;g.execute_task(h,dict(target='task',route=[h['p']],steps=0,action='interact',work=4))
   ck('l2',actor+str(level)+choice+' firstwork not repeated',g.objects['task']['progress']==(3 if level>=6 or level>=2 and choice=='work' else 2))
from appraisal import FAMILIES
for key,(s,t,c,severe) in FAMILIES.items():ck('emotion',key+' exact current family',ds['experience']['appraisal']['numeric_families'][key]==dict(severity=s,trust_loss=t,category=c,severe=severe))
ob=runpy.run_path(str(W/'story_obligations.py'))['verified']
he=[dict(seq=11,kind='mission_settled',mission='M17',actors=['he','su'],all_extracted=True),dict(seq=12,kind='objective_completed',mission='M17',contributors=['he','su'],primary_contributor='he'),dict(seq=13,kind='protect_or_rescue',mission='M17',actor='he')]
ck('narrative','He can assist without forfeiting delegated work',ob('he',he))
for case in ['primary_only','no_other','no_protection','wrong_mission','not_extracted']:
 rows=json.loads(json.dumps(he))
 if case=='primary_only':rows[1].pop('contributors');rows[1]['primary_contributor']='su'
 if case=='no_other':rows[1]['contributors']=['he']
 if case=='no_protection':rows.pop()
 if case=='wrong_mission':rows[2]['mission']='M18'
 if case=='not_extracted':rows[0]['all_extracted']=False
 ck('narrative','He false proof rejected '+case,not ob('he',rows))
probe="""import sys,json
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path.cwd()/'work/integrated-review'))
from social import qualified
o=dict(contributions=[],completed_round=2,kind='cargo',cell=[0,0])
b=SimpleNamespace(objects={'photo':o},exits=[(4,0)])
r={'log':[dict(action='move',actor=0,cargo='photo',round=1,path=[(0,0),(1,0),(2,0)],at=(2,0)),dict(action='move',actor=1,cargo='photo',round=2,path=[(2,0),(3,0),(4,0)],at=(4,0))]}
print(json.dumps(qualified(b,r,'photo',['jiang','ye','lin'])))
"""
seed_results=[]
old_seed_results=[]
for seed in ['0','1','2','27','99']:
 out=subprocess.check_output([sys.executable,'-c',probe],cwd=R,env={**os.environ,'PYTHONHASHSEED':seed},text=True).strip();seed_results.append(json.loads(out))
 ck('determinism','qualified across hash seed '+seed,json.loads(out)==['jiang','ye'])
 oldprobe=probe.replace('from social import qualified',"from social import CHARS\ns=Path('work/predevelopment-review/before/work/integrated-review/social.py').read_text()\nexec(s[s.index('def qualified('):s.index('\\nclass Social:')])")
 old_seed_results.append(json.loads(subprocess.check_output([sys.executable,'-c',oldprobe],cwd=R,env={**os.environ,'PYTHONHASHSEED':seed},text=True).strip()))
ck('determinism','historical unordered path reproducibly differs across seeds',len({tuple(x) for x in old_seed_results})>1)
old=read(O/'training-general-campaigns.json')['scenarios'];new=read(O/'predevelopment-campaigns.json')['scenarios'];lookup={r['spec']['name']:r for r in old};receipt_diffs=[]
ck('campaigns','108 fresh campaigns',len(new)==108)
ck('campaigns','3420 actual battles',sum(len(r['battles']) for r in new)==3420)
ck('campaigns','36 maps covered',{b['mission'] for r in new for b in r['battles']}==set(boards))
for r in new:
 name=r['spec']['name'];prev=lookup[name]
 ck('campaigns',name+' all24main',r['summary']['main_count']==24)
 ck('campaigns',name+' battle results unchanged',r['battles']==prev['battles'])
 ck('campaigns',name+' final state unchanged',r['summary']==prev['summary'])
 ck('campaigns',name+' intermediate pressure unchanged',r['pressure']==prev['pressure'])
 if r['receipts']!=prev['receipts']:
  ck('campaigns',name+' same receipt count',len(r['receipts'])==len(prev['receipts']))
  for a,b in zip(prev['receipts'],r['receipts']):
   if a==b:continue
   permitted={'contributors','primary_contributor'}
   ck('determinism',name+' only contribution ordering differs',{k:v for k,v in a.items() if k not in permitted}=={k:v for k,v in b.items() if k not in permitted} and set(a.get('contributors',[]))==set(b.get('contributors',[])))
   receipt_diffs.append(dict(campaign=name,old=a,new=b))
runtime={str(p.relative_to(R)):sha(p) for p in (R/'game').rglob('*') if p.is_file() and (p.suffix in ['.gd','.tscn'] or p.name=='project.godot')}
ck('boundary','all formal runtime files unchanged',runtime==read(W/'runtime-before.json'))
ck('boundary','no unresolved product decision',ds['decisions']['user_decisions_required_now']==[])
class Doc(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if 'id' in d:self.ids.append(d['id'])
  if t=='a' and d.get('href'):self.links.append(d['href'])
html_checked=[]
for name in ['full-game-design.html','predevelopment-review.html','character-script-final.html']:
 p=O/name
 if not p.exists() or '0.18' not in p.read_text()[:2000]:continue
 doc=Doc();doc.feed(p.read_text());ck('artifact',name+' unique anchors',len(doc.ids)==len(set(doc.ids)))
 for href in doc.links:
  u=urlsplit(href)
  if u.scheme:continue
  if u.path:
   target=p.parent/unquote(u.path)
   if target.name=='predevelopment-checks.json' and not target.exists():continue
   ck('artifact',name+' '+href,target.exists())
  elif u.fragment:ck('artifact',name+' #'+u.fragment,u.fragment in doc.ids)
 html_checked.append(name)
fingerprints={str(p.relative_to(R)):sha(p) for p in [F/'release_baseline.json',F/'design_manifest.json',*[R/p for p in manifest['generated_views']],R/'work/cooperation-value-review/current_rules.py',R/'work/growth-identity-review/relationships.py',R/'work/integrated-review/social.py',W/'story_obligations.py',R/'work/campaign-review/ledger_review.py',R/'work/ordinary-player-review/campaigns.py',W/'regression.py',W/'verify.py']}
result=dict(version=base['version'],date='2026-11-04',design_checks=len(checks),rule_regression=read(O/'predevelopment-rule-checks.json')['passed'],campaigns=108,actual_battles=3420,phase_graph_nodes=len(seen),checks=checks,contribution_receipt_corrections=receipt_diffs,hash_seed_results=seed_results,historical_hash_seed_results=old_seed_results,html_structure_checked=html_checked,runtime_unchanged=True,known_design_blockers=[],development_readiness='GO_FOR_SAME_FINAL_PROJECT_WHEN_USER_AUTHORIZES',formal_development_started=False,release_readiness='NOT_VERIFIED',limitations=ds['acceptance']['coverage_limits'],sha256=fingerprints)
write(O/'predevelopment-checks.json',result)
print('DESIGN CHECKS',len(checks),'RULES',result['rule_regression'],'CAMPAIGNS',108,'BATTLES',3420,'RECEIPT CORRECTIONS',len(receipt_diffs))
