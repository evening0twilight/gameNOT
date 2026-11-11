from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'work/ordinary-player-review'))
from policies import *
from relationships import RelationshipLedger as OriginalLedger,c,atomic_identity
from training_rules import StudyLedger
RelationshipLedger=StudyLedger
from social import Social,qualified
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
EC=json.loads((ROOT/'game/data/campaign_economy_contract.json').read_text());ST=json.loads((ROOT/'game/data/final_design/stories.json').read_text());CAL={x['day']:x['scenes'] for x in json.loads((ROOT/'outputs/final-design-validation.json').read_text())['story_calendar']};EQ={x['id']:x for x in json.loads((ROOT/'game/data/final_design/equipment.json').read_text())['items']}

def party_for(g,cfg,side=False):
 eligible=[a for a in g.crew if g.eligible(a)]
 favorites=cfg.get('favorites',['lin','xu','su'])
 if cfg['formation']=='reserve' and g.day<cfg['activation_day']:
  eligible.sort(key=lambda a:(a==cfg['training_actor'],g.crew[a]['fatigue'],list(g.crew).index(a)))
 elif cfg['formation']=='rotate':eligible.sort(key=lambda a:(g.crew[a]['fatigue'],list(g.crew).index(a)))
 else:eligible.sort(key=lambda a:(a not in favorites,favorites.index(a) if a in favorites else 99,g.crew[a]['fatigue']))
 return eligible[:3]
def run(spec):
 cfg=PROFILES[spec['behavior']]|spec;g=RelationshipLedger(spec['name'],hard=cfg['difficulty']=='hard',external_social=True);g.training_rule=cfg.get('training_rule','none');g.identity_pacts=True;social=Social();battles=[];skipped=[];pressure=[];pending_sides={}
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
  paid_xp={a:sum(r.get('gains',{}).get(a,0) for r in g.records if r['kind']=='training_gain') for a in cast}
  levels={a:sum(g.crew[a]['xp']>=t for t in [0,12,28,48,72,100]) if a in g.crew else 1 for a in cast};blocked=social.restrictions(party,g.day)
  xp_at_entry={a:g.crew[a]['xp'] for a in party};g.deploy(mid,party,support,pack)
  play=battle
  if cfg.get('specialty_intent'):
   from specialty import specialty_battle
   from functools import partial
   play=partial(specialty_battle,focus=cfg['training_actor'])
  instance=play(board,goals,cast,levels,cfg['behavior'],extras,service=cfg.get('service',False),difficulty=cfg['difficulty'],variant=cfg['variant'],gear=gear,relations=blocked,medical_capacity=g.medical_pack_limit(),delay=1 if g.day in cfg.get('delays',[]) else 0)
  if cfg.get('disable_favorite_skills'):
   for h in instance.h:
    if h['name']==cfg['favorites'][0]:h['abilities']=[];instance.gear.pop('he_3',None) if h['name']=='he' else None
  r=instance.run();injured=[];withdrawn=[]
  counterfactual=None
  if cfg.get('training_rule')=='current':
   natural_levels={a:sum(max(0,g.crew[a]['xp']-paid_xp[a])>=t for t in [0,12,28,48,72,100]) if a in g.crew else 1 for a in cast}
   if natural_levels!=levels:
    alt=play(board,goals,cast,natural_levels,cfg['behavior'],extras,service=cfg.get('service',False),difficulty=cfg['difficulty'],variant=cfg['variant'],gear=gear,relations=blocked,medical_capacity=g.medical_pack_limit(),delay=1 if g.day in cfg.get('delays',[]) else 0);q=alt.run();counterfactual=dict(levels=natural_levels,**{k:q[k] for k in ['success','rounds','damage','ap','secured','downed','skill_action_types','service_secured']})

  for h,a in zip(instance.h,cast):
   if a not in party:continue
   if h.get('permanent') or (h['down'] and not h.get('rescued') and g.hard):withdrawn.append(a)
   elif h['down'] or not h['left']:injured.append(a)
  ids={o['id'] for o in board['objectives']};done=[k for k,o in instance.objects.items() if k in ids and o['done']];secured=[k for k in r['secured'] if k in done]
  contributions={k:qualified(instance,r,k,cast) for k in done};contributions={k:[a for a in v if a in party] for k,v in contributions.items() if v}
  consumed={'med_dose':instance.used.get('med_dose',0)} if instance.used.get('med_dose',0) else {}
  packet=dict(mission=mid,completed=done,secured=secured,contributions=contributions,injured=injured,withdrawn=withdrawn,consumed=consumed,protection=list({cast[x['owner']] for x in r['log'] if x['action']=='barrier_intercept' and x.get('protected_actors') and cast[x['owner']] in party}),all_extracted=r['healthy_extracted']==3,xu_standing_on_exit='xu' in party and 'xu' not in injured+withdrawn,kept_deadline=False,branch=branch)
  g.settle(packet);c.ns['record_operation'](g,instance,r);social.settle(instance,r,cast,g.day,None);social.sync(g)
  row={k:r[k] for k in ['mission','success','rounds','damage','ap','secured','lost','downed','skill_action_types','service_secured']};row.update(without_paid_growth=counterfactual,xp_at_entry=xp_at_entry,party=cast,levels=levels,injured=injured,withdrawn=withdrawn,consumed=consumed,packed=pack,branch=branch,goals=goals,extra=extras);battles.append(row);return True
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
  if g.projects<2 and cfg['training']!='none' and g.day>=cfg.get('training_after',1):
   people=[a for a in g.crew if g.healthy(a) and a not in g.used and g.training_available(a)]
   if cfg.get('training_actor'):people=[a for a in people if a==cfg['training_actor']]
   if cfg['training']=='targeted':people=[a for a in people if any(g.crew[a]['xp']<t<=g.crew[a]['xp']+3 for t in [12,28,72])]
   if cfg['training']=='favorite':people=[a for a in people if a in cfg.get('favorites',['lin','xu','su'])];people.sort(key=lambda a:cfg.get('favorites',['lin','xu','su']).index(a))
   if cfg.get('training_decision')=='next_duty':
    reasonable=[]
    for a in people:
     xp=g.crew[a]['xp'];crosses=any(xp<t<=xp+min(12,100-xp) for t in [12,28,48,72,100])
     if not crosses:continue
     future=deepcopy(g);future.day+=1;future.phase='briefing'
     for actor,person in future.crew.items():
      if person['joined'] and not person['withdrawn']:person['fatigue']=max(0,person['fatigue']+(6 if actor==a else 0)-12-(0 if person['worked'] else 16))
     if a in party_for(future,cfg):reasonable.append(a)
    people=reasonable
   people=people[:2]
   if people and len(people)>g.resources['supplies']:
    if cfg['training']=='habit' and g.resources['credits']>=4*(len(people)-g.resources['supplies']):g.buy_supplies(len(people)-g.resources['supplies'])
    else:skipped.append(dict(day=day,reason='training_unaffordable',actors=people));people=people[:g.resources['supplies']]
   if people and cfg.get('prefer_mentor'):
    options=[x for x in g.mentor_candidates() if x[1] in people]
    if options and g.resources['supplies']>=2:
     teacher,learner,amount=max(options,key=lambda x:(x[2],g.crew[x[0]]['xp']));g.mentor(teacher,learner);people.remove(learner)
   if people and g.projects<2:g.train(people)
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
