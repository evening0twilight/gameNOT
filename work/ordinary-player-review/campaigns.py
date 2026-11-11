from policies import *
from relationships import RelationshipLedger,c
from social import Social,qualified
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
EC=json.loads((ROOT/'game/data/campaign_economy_contract.json').read_text());ST=json.loads((ROOT/'game/data/final_design/stories.json').read_text());CAL={x['day']:x['scenes'] for x in json.loads((ROOT/'outputs/final-design-validation.json').read_text())['story_calendar']};EQ={x['id']:x for x in json.loads((ROOT/'game/data/final_design/equipment.json').read_text())['items']}

def party_for(g,cfg,side=False):
 eligible=[a for a in g.crew if g.eligible(a)]
 favorites=cfg.get('favorites',['lin','xu','su'])
 if cfg['formation']=='rotate':eligible.sort(key=lambda a:(g.crew[a]['fatigue'],list(g.crew).index(a)))
 else:eligible.sort(key=lambda a:(a not in favorites,favorites.index(a) if a in favorites else 99,g.crew[a]['fatigue']))
 return eligible[:3]
def run(spec):
 cfg=PROFILES[spec['behavior']]|spec;g=RelationshipLedger(spec['name'],hard=cfg['difficulty']=='hard',external_social=True);g.identity_pacts=True;social=Social();battles=[];skipped=[];pressure=[];pending_sides={}
 side_days={b['day']:b['id'] for b in B.values() if b['kind']=='side'}
 def execute(mid):
  board=deepcopy(B[mid]);party=party_for(g,cfg,board['kind']=='side')
  if board['kind']=='side' and len(party)<3:skipped.append(dict(day=g.day,reason='side_deferred_no_three',mission=mid));return False
  cast=party+[f'reserve{i}' for i in range(3-len(party))]
  if mid=='M24':
   g.route=cfg['ending'] if cfg['ending'] in g.available_routes() else 'evacuation';branch=g.route
   goals=[grp[cfg.get('choice_index',0)%len(grp)] for grp in board['route_groups'][g.route]]
  else:
   goals=[grp[cfg.get('choice_index',0)%len(grp)] for grp in board['mandatory_groups']];branch=('isolate' if 'isolate' in goals else 'repair') if mid=='M17' else None
  extras=list(extra_sets(board,goals,branch))[-1];extras=[] if cfg['optional']=='none' else list(extras[:1]) if cfg['optional']=='one' else list(extras)
  # No hindsight retry, no changing purchased resources after seeing combat.
  pack={};desired=cfg.get('pack',1)
  if desired:
   need=max(0,desired-g.inventory['med_dose'])
   if need and g.resources['supplies']<need:
    n=min(need-g.resources['supplies'],g.resources['credits']//4)
    if n:g.buy_supplies(n)
   n=min(need,g.resources['supplies'])
   if n:g.craft('med_dose',n)
   n=min(desired,g.inventory['med_dose'],g.medical_pack_limit())
   if n:pack={'med_dose':n}
  gear={'medkit':0,'crowbar':0,'med_dose':pack.get('med_dose',0)}
  if 'scanner' in g.tools:gear['scanner']=1
  if 'stretcher' in g.tools:gear['stretcher']=2
  support=next((a for a in g.crew if a not in party and g.eligible(a,8)),None) if cfg['support'] and board['kind']=='main' else None
  levels={a:sum(g.crew[a]['xp']>=t for t in [0,12,28,48,72,100]) if a in g.crew else 1 for a in cast};blocked=social.restrictions(party,g.day)
  g.deploy(mid,party,support,pack)
  instance=battle(board,goals,cast,levels,cfg['behavior'],extras,service=cfg.get('service',False),difficulty=cfg['difficulty'],variant=cfg['variant'],gear=gear,relations=blocked,medical_capacity=g.medical_pack_limit(),delay=1 if g.day in cfg.get('delays',[]) else 0)
  if cfg.get('disable_favorite_skills'):
   for h in instance.h:
    if h['name']==cfg['favorites'][0]:h['abilities']=[];instance.gear.pop('he_3',None) if h['name']=='he' else None
  r=instance.run();injured=[];withdrawn=[]
  for h,a in zip(instance.h,cast):
   if a not in party:continue
   if h.get('permanent') or (h['down'] and not h.get('rescued') and g.hard):withdrawn.append(a)
   elif h['down'] or not h['left']:injured.append(a)
  ids={o['id'] for o in board['objectives']};done=[k for k,o in instance.objects.items() if k in ids and o['done']];secured=[k for k in r['secured'] if k in done]
  contributions={k:qualified(instance,r,k,cast) for k in done};contributions={k:[a for a in v if a in party] for k,v in contributions.items() if v}
  consumed={'med_dose':instance.used.get('med_dose',0)} if instance.used.get('med_dose',0) else {}
  packet=dict(mission=mid,completed=done,secured=secured,contributions=contributions,injured=injured,withdrawn=withdrawn,consumed=consumed,protection=list({cast[x['owner']] for x in r['log'] if x['action']=='barrier_intercept' and x.get('protected_actors') and cast[x['owner']] in party}),all_extracted=r['healthy_extracted']==3,xu_standing_on_exit='xu' in party and 'xu' not in injured+withdrawn,kept_deadline=False,branch=branch)
  g.settle(packet);c.ns['record_operation'](g,instance,r);social.settle(instance,r,cast,g.day,None);social.sync(g)
  row={k:r[k] for k in ['mission','success','rounds','damage','ap','secured','lost','downed','skill_action_types','service_secured']};row.update(party=cast,levels=levels,injured=injured,withdrawn=withdrawn,consumed=consumed,packed=pack,branch=branch,goals=goals,extra=extras);battles.append(row);return True
 for day in range(1,25):
  if cfg.get('shop') and day in [4,5,8,11,17]:
   wanted={4:'winch',5:'shield',8:'insulation',11:'scanner',17:'stretcher'}[day];e=EQ[wanted]
   if wanted not in g.tools and g.resources['credits']>=e['price_credits'] and g.resources['parts']>=e['price_parts']:g.buy_tool(wanted)
   else:skipped.append(dict(day=day,reason='cannot_afford_tool',item=wanted))
  execute(f'M{day:02}')
  if day==24:break
  if cfg['sides'] and day in side_days and (cfg['sides']=='all' or day%4==0):pending_sides[side_days[day]]=min(23,day+1)
  for sid,deadline in list(pending_sides.items()):
   if day>deadline:skipped.append(dict(day=day,reason='side_window_expired',mission=sid));del pending_sides[sid];continue
   if execute(sid):del pending_sides[sid];break
   if day==deadline:skipped.append(dict(day=day,reason='side_window_expired',mission=sid));del pending_sides[sid]
  g.begin_camp();g.confirm_audits()
  if cfg.get('facility') and g.projects<2:
   f='workshop' if cfg['facility']=='workshop' else 'infirmary';tier=g.fac[f]
   if tier<2:
    credit,parts=[(35,4),(60,8)][tier]
    if g.resources['credits']>=credit and g.resources['parts']>=parts:g.upgrade(f)
  # Existing actual scenes; error recorded, no fake branches or resource debt.
  for nid in CAL[day]:
   try:g.scene(nid)
   except AssertionError:skipped.append(dict(day=day,reason='scene_unavailable',node=nid))
  hurt=[a for a in g.crew if g.crew[a]['joined'] and not g.crew[a]['withdrawn'] and g.crew[a]['ready']>day+1 and a not in g.used]
  if cfg.get('treat',True) and hurt and g.projects<2:
   cost=2*min(len(hurt),2)-int(g.fac['infirmary']>=1 and g.treated==0)
   if g.resources['supplies']<cost:
    n=min(cost-g.resources['supplies'],g.resources['credits']//4)
    if n:g.buy_supplies(n)
   if g.resources['supplies']>=cost:g.treat(hurt[:2])
   else:skipped.append(dict(day=day,reason='treatment_unaffordable',actors=hurt))
  # Training habit is an explicit human-behavior stress case, never product default.
  if g.projects<2 and cfg['training']!='none':
   people=[a for a in g.crew if g.healthy(a) and a not in g.used and g.training_available(a)]
   if cfg.get('training_actor'):people=[a for a in people if a==cfg['training_actor']]
   if cfg['training']=='targeted':people=[a for a in people if any(g.crew[a]['xp']<t<=g.crew[a]['xp']+12 for t in [12,28,72])]
   if cfg['training']=='favorite':people=[a for a in people if a in cfg.get('favorites',['lin','xu','su'])];people.sort(key=lambda a:cfg.get('favorites',['lin','xu','su']).index(a))
   people=people[:2]
   if people and len(people)>g.resources['supplies']:
    if cfg['training']=='habit' and g.resources['credits']>=4*(len(people)-g.resources['supplies']):g.buy_supplies(len(people)-g.resources['supplies'])
    else:skipped.append(dict(day=day,reason='training_unaffordable',actors=people));people=people[:g.resources['supplies']]
   if people:g.train(people)
  tired=[a for a in g.crew if g.healthy(a) and a not in g.used and g.crew[a]['fatigue']>=50]
  if tired and g.projects<2:g.recover(tired[:2])
  if day in [20,22,23] and g.projects<2:
   missing=next((e for e in ['E_ORDER','E_WARNING','E_MAINTENANCE'] if e not in g.evidence),None)
   if missing:g.review([missing]);g.confirm_audits()
  pressure.append(dict(day=day,resources=deepcopy(g.resources),projects=g.projects,healthy=sum(g.healthy(a) for a in g.crew),max_fatigue=max(x['fatigue'] for x in g.crew.values())))
  if cfg.get('publish_plan') and 'mo' in g.plans and g.projects<2 and g.healthy('mo') and 'mo' not in g.used and g.evidence:
   evidence=next((e for e in sorted(g.evidence) if not any(r['kind']=='public_record_release' and r.get('evidence_id')==e for r in g.records)),None)
   if evidence:g.release_redacted(evidence)
  social.night_from_ledger(g,day)
 return dict(spec=spec,summary=g.summary(),battles=battles,pressure=pressure,skipped=skipped,receipts=g.records,rows=g.rows)

def specs():
 for i,(behavior,diff,variant,ending) in enumerate(itertools.product(PROFILES,['relaxed','standard','hard'],['A','B'],['evacuation','distributed_rebuild','shared_control'])):
  yield dict(name=f'{behavior}/{diff}/{variant}/{ending}',behavior=behavior,difficulty=diff,variant=variant,ending=ending,choice_index=i%2,sides=False if behavior=='main_only' else 'some' if behavior in ['cautious','favorite'] else 'all',shop=behavior in ['collector','mixed'],facility='workshop' if behavior=='collector' else None,pack=2 if behavior in ['collector','mixed'] else 1,delays=[6,12,18] if behavior=='mixed' else [],favorites=['jiang','he','mo'] if behavior=='favorite' else ['lin','xu','su'],service=behavior=='cautious')
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='ordinary-player-after-campaigns.json');ap.add_argument('--smoke',action='store_true');args=ap.parse_args();cases=list(specs());cases=cases[::18] if args.smoke else cases
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  rows=[]
  for i,r in enumerate(pool.map(run,cases),1):
   rows.append(r)
   if i%12==0 or args.smoke:print(i,r['summary']['name'],r['summary']['resources'],sum(b['success'] for b in r['battles']),flush=True)
 (ROOT/'outputs'/args.output).write_text(json.dumps(dict(version=json.loads((ROOT/'game/data/final_design/design_manifest.json').read_text())['version'],scenarios=rows,actual_battles=sum(len(r['battles']) for r in rows),scope='Single committed local-information policy per mission; no result ranking/retry. Behavioral stress cases, not sampled human success probabilities.'),ensure_ascii=False,indent=2)+'\n');print('CAMPAIGNS',len(rows),flush=True)
