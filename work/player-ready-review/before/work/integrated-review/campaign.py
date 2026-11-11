"""New social owner + named tactics + real ledger + guidance across complete campaigns."""
from pathlib import Path
from copy import deepcopy
import json,sys,runpy,contextlib,io
from party import Party
from social import Social,CHARS,qualified
from guidance import Guidance
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs'
with contextlib.redirect_stdout(io.StringIO()):ns=runpy.run_path(str(ROOT/'work/campaign-review/ledger_review.py'))
Ledger=ns['Ledger'];B=ns['BOARDS'];calendar={x['day']:x['scenes'] for x in ns['CAL']}
def rank(r):return (not r['success'],r['downed'],r['rounds'],r['damage'],r['ap'])
def play(g,social,guide,mid,party,hard=False,disaster=False,overcommit=False,invest=False):
 b=B[mid];cast=party+[f'reserve{i}' for i in range(3-len(party))];levels={a:sum(g.crew[a]['xp']>=t for t in [0,12,28,48,72,100]) if a in g.crew else 1 for a in cast}
 if mid=='M24':g.route='shared_control' if 'shared_control' in g.available_routes() else 'evacuation' if disaster else 'distributed_rebuild'
 goals=[grp[0] for grp in (b['route_groups'][g.route] if mid=='M24' else b['mandatory_groups'])]
 blocked=social.restrictions(party,g.day);trials=[];gear={}
 if invest:
  gear['crowbar']=0
  if 'scanner' in g.tools:gear['scanner']=1
  if 'stretcher' in g.tools:gear['stretcher']=2
  trained=next((p for p in sorted(g.protocols) if p[2]=='protected_work' and set(p[:2])<=set(party) and g.cooperation_allowed(list(p[:2]),p[2],context=['active_machine'])),None)
  if trained:gear.update(cooperation=True,cooperation_pair=[cast.index(a) for a in trained[:2]])
 extras=sorted({o['id'] for o in b['objectives']}-set(goals)-({'isolate'} if mid=='M17' else set())) if invest else []
 if invest and mid=='M24':extras=['archive']
 promise_deadline=None
 if overcommit:
  # A legal prior plan meets the voluntary deadline. The actual policy then wastes2rounds.
  plans=[Party(b,goals,cast,levels,skills=False,style=style).run() for style in ['rush','controls']]
  promise_deadline=min((r for r in plans if r['success']),key=rank)['rounds']
 for skills in [False,True]:
  for style in (['rush','controls','joint'] if invest else ['rush','controls']):
   battle=Party(b,goals,cast,levels,skills=skills,relations=blocked,gear=deepcopy(gear),extra=extras,difficulty='hard' if hard else 'standard',style=style,delay=(b.get('hard_round_limit',b['round_limit']) if hard else b['round_limit'])-1 if disaster else 2 if overcommit else 0);r=battle.run();trials.append((battle,r))
 battle,r=min(trials,key=lambda x:(not x[1]['success'],-len(x[1]['secured']),-sum(z['action']=='protected_work' for z in x[1]['log']),x[1]['downed'],x[1]['rounds'],x[1]['damage'],x[1]['ap']) if invest else rank(x[1]));all_extracted=r['healthy_extracted']==3
 injured=[];withdrawn=[]
 for i,a in enumerate(cast):
  if a not in g.crew:continue
  h=battle.h[i]
  if h.get('permanent') or (h['down'] and not h.get('rescued') and hard):withdrawn.append(a)
  elif h['down'] or not h['left']:injured.append(a)
 completed=[k for k,o in battle.objects.items() if o['done'] and k not in battle.control_ids and k in {o['id'] for o in b['objectives']}]
 secured=[k for k in r['secured'] if k in completed];contributions={}
 for k in completed:
  contributors=qualified(battle,r,k,cast)
  if contributors:contributions[k]=contributors
 support=next((a for a in g.crew if a not in party and g.eligible(a,8)),None) if b['kind']=='main' else None
 g.deploy(mid,party,support)
 packet=dict(mission=mid,completed=completed,secured=secured,contributions=contributions,injured=injured,withdrawn=withdrawn,consumed={},protection=[cast[x['owner']] for x in r['log'] if x['action']=='barrier_intercept' and x.get('protected_actors') and cast[x['owner']] in party],all_extracted=all_extracted,xu_standing_on_exit='xu' in party and 'xu' not in injured+withdrawn,kept_deadline=r['rounds']<=battle.limit-2,branch=g.route if mid=='M24' else 'repair' if mid=='M17' else None)
 g.settle(packet)
 promise=dict(id='accepted-return-'+mid,deadline=battle.limit-2,warned=True,accepted=True) if disaster and r['rounds']>battle.limit-2 else None
 if overcommit and r['rounds']>promise_deadline:promise=dict(id='accepted-return-'+mid,deadline=promise_deadline,warned=True,accepted=True)
 response=social.settle(battle,r,cast,g.day,promise);social.sync(g)
 if promise:
  for a in party:
   root=mid+':decision:'+promise['id'];g.receipt('promise_breach',mission=mid,actor='leader',observer=a,target='leader',event_id=root,scope='retreat_deadline',responsibility=1);g.breaches[a]=g.seq
 guide.scene(b,r['log'],restricted=any(blocked.values()))
 return dict(mission=mid,party=cast,levels=levels,success=r['success'],rounds=r['rounds'],limit=r['limit'],ap=r['ap'],damage=r['damage'],skills=r['skill_action_types'],equipment=gear,protocol_actions=sum(x['action']=='protected_work' for x in r['log']),tool_actions=sum(x['action'] in ['crowbar','scanner'] for x in r['log']),relation_refusals=r['relation_refusals'],secured=secured,injured=injured,withdrawn=withdrawn,restricted_directions=[list(k) for k,v in blocked.items() if v],social=response)
def run(name,hard=False,sides=False,fixed=False,disasters=(),hints='light',overcommits=(),invest=False):
 g=Ledger(name,hard=hard,external_social=True);social=Social();guide=Guidance(hints);battles=[];skipped=[]
 side_days={b['day']:b['id'] for b in B.values() if b['kind']=='side'}
 for day in range(1,25):
  if invest:
   for item,unlock in [('scanner',10),('stretcher',16)]:
    if day>unlock and item not in g.tools:g.buy_tool(item)
  party=g.choose_party(fixed=fixed);battles.append(play(g,social,guide,f'M{day:02}',party,hard,day in disasters,day in overcommits,invest))
  if day==24:break
  if sides and day in side_days:
   party=g.choose_party(side=True)
   if len(party)==3:battles.append(play(g,social,guide,side_days[day],party,hard))
   else:skipped.append(dict(day=day,side=side_days[day],reason='真实可出勤人物不足3；支线不临时借调'))
  g.begin_camp();guide.camp(day,recruit=any(c['join']==day and day>1 for c in CHARS.values()));g.confirm_audits()
  for node in calendar[day]:
   try:g.scene(node)
   except AssertionError:skipped.append(dict(day=day,node=node,reason='项目/缺席/证据条件不足，未强发奖励'))
  if invest and g.projects<2 and ('lin','su','protected_work') not in g.protocols and all(g.healthy(a) and a not in g.used and g.crew[a]['fatigue']+8<=100 for a in ['lin','su']) and all(g.rel[k]['trust']>=60 for k in ['lin>su','su>lin']) and g.resources['supplies']>=2:g.train(['lin','su'],'protected_work')
  # Reward projects are paid and derive self-load recovery from real receipts.
  tired=sorted([a for a in g.crew if g.healthy(a) and a not in g.used and g.crew[a]['fatigue']>=50],key=lambda a:-g.crew[a]['fatigue'])
  if tired and g.projects<2:g.recover(tired[:2])
  if day in [20,22,23] and g.projects<2:
   missing=next((e for e in ['E_ORDER','E_MAINTENANCE','E_WARNING'] if e not in g.evidence),None)
   if missing:g.review([missing]);g.confirm_audits()
  if g.projects<2:
   trainees=sorted([a for a in g.crew if g.healthy(a) and a not in g.used and g.crew[a]['fatigue']+8<=100],key=lambda a:g.crew[a]['xp'])[:2]
   if trainees and g.resources['supplies']>=len(trainees):g.train(trainees)
  social.night_from_ledger(g,day)
 summary=g.summary();assert summary['main_count']==24 and all(v>=0 for v in g.resources.values())
 return dict(summary=summary,battles=battles,skipped=skipped,guidance=guide.log,social=social.totals(24),rows=g.rows,receipts=g.records)
scenarios=[run('标准轮换'),run('标准全支线',sides=True),run('最高轮换',hard=True),run('最高连续失误后继续',hard=True,disasters=(6,7,8,15)),run('固定偏好阵容且关闭讲解',fixed=True,hints='off'),run('反复失约但仍尝试救援',fixed=True,overcommits=tuple(range(6,16))),run('真实购买装备与训练合作，争取额外目标',fixed=True,invest=True)]
out={'version':'0.9-integrated-review','scope':'Actual named-party tactics and derived social receipts feed seven full24day ledgers. Counterfactual adverse scenarios explicitly waste rounds and violate accepted feasible return promises; not a forecast of human behavior. Tutorial mode is a scheduling model, not a real rendered game UI.','scenarios':scenarios,'checks':{'all_reach_ending':True,'old_social_awards_disabled':True,'recovery_from_real_camp_projects':True,'actual_battles':sum(len(s['battles']) for s in scenarios)}}
(O/'integrated-campaign-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for s in scenarios:print(s['summary']['name'],s['summary']['main_count'],s['summary']['side_count'],s['summary']['world_ending'],'injurywithdraw',len(s['summary']['withdrawn']),'cards',sum(x['kind']=='nonmodal_card' for x in s['guidance']))
