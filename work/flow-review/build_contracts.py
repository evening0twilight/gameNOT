raise SystemExit("Archived v0.3 flow authoring: current source is work/final-design/rebuild.py; do not overwrite v0.4.")
"""Design authoring and paper-trace model. It does not simulate tactical combat."""
from pathlib import Path
import json
from copy import deepcopy

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'game/data'
def read(n):return json.loads((DATA/n).read_text())
def write(n,x): (DATA/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

policy={
 'version':'0.3', 'confirmed_by_user':'2026-10-31',
 'campaign':'Continue to a complete ending after mistakes; lose resources, opportunities and favourable outcomes.',
 'ordinary_and_standard_loss':'Recoverable serious injury; no involuntary permanent loss during the campaign.',
 'highest_difficulty_loss':'Permanent medical withdrawal may follow failure to retrieve an incapacitated hero before the visibly announced deadline; disclose at difficulty selection and before the specific irreversible action.',
 'loss_is_not_random_death':True,
 'provenance':{'user_confirmed':['failure_continues_with_losses','recoverable_injury_below_highest_difficulty','highest_difficulty_may_allow_permanent_departure_with_disclosure','basic_action_control_retained'], 'designer_operational_choices':['medical_withdrawal_after_announced_rescue_deadline','manual_saves_on_all_difficulties','no_random_death_roll']},
 'conflict_agency':'Characters may refuse a specific cooperation or request safeguards. All legal basic actions remain player-controlled.',
 'save_policy':'Manual saves and stage backups remain available at every difficulty; highest difficulty does not imply ironman.'}
write('confirmed_experience_policy.json',policy)

economy={
 'version':'0.3','status':'design_contract_not_tactical_balance_proof',
 'basic_living':'Community services cover basic food, accommodation and routine first aid. There is no per-roster-size daily resource tax.',
 'start':{'credits':60,'supplies':8,'parts':2},
 'main_rewards':{'success':{'credits':24,'supplies':2,'parts':2},'partial':{'credits':14,'supplies':1,'parts':1},'failed':{'credits':6,'supplies':0,'parts':0}},
 'side_rewards':{'success':{'credits':16,'supplies':1,'parts':1},'partial':{'credits':8,'supplies':0,'parts':0},'failed':{'credits':0,'supplies':0,'parts':0}},
 'main_base_allowance':6,'allowance_reason':'One municipal deployment-and-handover allowance per scheduled main duty, included in the totals above; not a second reward.',
 'supply_buy_cost':4,'supplies_resale':False,'parts_resale':False,
 'shared_equipment':'Permanent tools do not consume charges for their baseline action. Consumables and expedited treatment spend supplies. No core objective requires a purchased item.',
 'fallback':'With no resources, free basic actions, ordinary recovery and eligible community responders still permit the next main duty. Extra training, consumables and upgrades may be unavailable.',
 'responders':{'max':3,'eligible':'Only fill vacancies when fewer than 3 present main characters can legally deploy.','upfront_cost':0,'reward_reduction_each':4,'main_reward_floor':6,'hero_xp':False,'personal_arcs':False,'skills':'Universal basic actions; no personal specialties or advanced relationship protocols.','persistent_identity':'Mission-scoped IDs; never substitute for a missing named role in character story.'},
 'camp':{'projects_per_evening':2,'one_project_per_participant':True,'default':'Unassigned heroes take basic sleep; heroes who did no day work also receive day-rest recovery.','treatment':{'max_patients':2,'supplies_each':2},'training':{'max_participants':2,'supplies_each':1,'xp_each':3,'fatigue_each':8},'recovery':{'max_participants':2,'extra_fatigue_reduction_each':12,'cost':0},'conversation':{'max_participants':3,'generic_item_gifting_clears_grievances':False},'record_review':{'cost':0,'uses_project':True,'requires_specific_hero':False},'facility':{'max_per_evening':1,'uses_project':True}},
 'fatigue':{'main_cost':18,'side_cost':18,'support_cost':8,'sleep_reduction':12,'idle_day_reduction':16,'warning_at':60,'deployment_rule':'Current fatigue + known mission fatigue cost must be <=100. Reserve cost before confirmation; do not clamp away excess cost.','same_day_redeployment':'Permitted only if healthy and the second deployment also meets the projected-cost test.'},
 'injury':{'ordinary_ready_day':'injury_day + 2; no resource cost','treated_ready_day':'injury_day + 1, after the first overnight; 2 supplies per patient','highest_withdrawal':'If the hero is still incapacitated and not extracted when the displayed rescue deadline expires or the player confirms abandonment, transfer to long-term hospital care and remove from this campaign roster. No random roll.','shared_gear':'Recovered through the following settlement inventory transfer; no main-story key item is personally owned.','fallback_epilogue':'Long-term recovery / changed occupation, reflecting the facts recorded before withdrawal.'},
 'support':{'max_workers':1,'supply_gain':1,'xp':2,'stage':'Primary-duty phase only. A worker cannot also take the main duty. Taking a later side duty is legal, but forfeits idle-day rest.'},
 'growth':{'main_xp':{'success':5,'partial':3,'failed':1},'side_xp':{'success':3,'partial':1,'failed':0},'power_budget':'Levels mainly unlock choices and modifiers; total extra base HP over the campaign <=2, base attack is not multiplied by level.','new_recruit':'Receives the chapter XP floor, cannot join a mission already settled, may join the subsequent optional duty if healthy.'}}
write('campaign_economy_contract.json',economy)

districts=['dock','medical','workshops','overpass','floodgates','old_town']
# Mission definitions now follow narrative causality, not a repeating list of task verbs.
rows=[
 ('M01','最后一班渡轮','dock','将两名受困居民送到撤离格','取回渡轮线路图','码头路线得以登记；错过者由后续市级撤离接管','M02'),
 ('M02','诊所的备用电','medical','关闭错误供电回路并恢复诊所供电','保存备用电池','诊所是否保留稳定电源影响后续医疗现场','M03'),
 ('M03','被锁住的仓库','workshops','开启仓库并转出一箱救援物资','回收破拆工具部件','公共工具登记完成，失败仍能用初始基础工具','M04'),
 ('M04','高架桥下','overpass','保护维修人员完成两处桥面加固并撤出','保持临时护栏完整','陈砚按社区派驻安排在结算后加入，并非任务救出的唯一人质','M05'),
 ('M05','旧泵房来电','floodgates','关闭失控装置并启动应急排水','保留泵站控制模块','决定下一次涨潮时的额外可用道路','M06'),
 ('M06','第一次涨潮','old_town','在涨潮期限前完成居民接力撤离','带走一件社区公共资产','首章结算已救出的居民，不追溯抹去成功','M07'),
 ('M07','工具箱的名字','workshops','解除工厂作业区危险并接出维修人员','带回旧维修编号','叶禾通过轮调加入；旧案线索不自动等于她原谅陈砚','M08'),
 ('M08','断开的补给线','workshops','打通两处运输阻碍并让补给车到达出口','保留一条备用运输线','工坊地区的恢复状态形成后续作业优势','M09'),
 ('M09','屋顶上的病房','medical','稳定并转移两名伤员','保存便携医疗设备','未达成的额外目标影响当地恢复叙述，不取消基础医疗','M10'),
 ('M10','撤离预案','overpass','测试并保留一条可用的双向撤离通道','标记第二处集合点','贺鸣按事先协调于任务后加入；意见与指令分开记录','M11'),
 ('M11','需要签字的门','workshops','安全解除工业门锁与相连设备','保存维护记录 E_MAINTENANCE','核对设备事故，不用一份文件免除所有人责任','M12'),
 ('M12','闸下的记录','floodgates','让取证设备完成两轮备份并撤离','保存封闸指令 E_ORDER','封闸历史进入可核查阶段；失败可在后续公共副本处补查','M13'),
 ('M13','会说谎的日志','old_town','隔离故障节点并让日志终端安全下线','保存报警覆盖记录 E_WARNING','莫遥完成派驻交接，关键资料不绑定她必须在队','M14'),
 ('M14','冷库里的电池','medical','转移冷库药品或恢复其冷藏电源，至少完成一项','兼顾两项','明确告诉玩家无法全拿时的取舍，不把两种合理方案都写成错','M15'),
 ('M15','三条同时响起的电话','old_town','在地图内优先处理至少一个求援点并安全离开','完成第二个目标','未签承诺的第三处求援不自动让全队怨恨队长','M16'),
 ('M16','没有空位的船','dock','清出运输通道并组织居民上船','保留社区生活物资','江朔按合作约定加入，轮换能力增加但基本食宿成本不增加','M17'),
 ('M17','修复或拆除','floodgates','完成泵站修复或断开危险供电，任选一条合法路线','取得维护记录副本 E_MAINTENANCE','方案改变地方设施状态，均能继续主线','M18'),
 ('M18','广播塔的盲区','old_town','解除中继干扰并发出撤离通告','保存广播备份','第四章前显示各地区的实际状况与可改进项','M19'),
 ('M19','警戒水位','medical','转移高风险病房并保住临时集合点','减少设备损耗','进入最后一轮风暴准备；这里不是“只剩一夜”后又过六天','M20'),
 ('M20','两座避难所','old_town','完成至少一处避难所防护与转运安排','兼顾第二处','集中资源或分散布局都有清楚收益，另开放公共记录核查','M21'),
 ('M21','旧路与新桥','overpass','打通最后阶段的撤离路线','补取封闸指令副本 E_ORDER','若旧路失败仍有最终撤离模板，失去的是效率与额外收益','M22'),
 ('M22','最后一份记录','workshops','保护记录终端并完成交接','补取报警记录副本 E_WARNING','最终路线条件进入明示阶段，仍允许一次公共核查','M23'),
 ('M23','撤离顺序','dock','安排居民与关键物资的最后登船顺序','保留更多重建物资','最后一次支线与营地整备，提示明天进入终局','M24'),
 ('M24','天亮以前','floodgates','执行已选的共同控制、分区隔离或总撤离方案','尽量保住已争取的地区成果','任务结算立即组装结局；失利也有完整的撤离收束',None)]
infrastructure_missions={'M02','M04','M05','M08','M10','M16','M17','M18','M20','M21','M23'}
evidence={'E_ORDER':{'direct':['M12','M21'],'review_days':[20,22,23]},'E_WARNING':{'direct':['M13','M22'],'review_days':[20,22,23]},'E_MAINTENANCE':{'direct':['M11','M17'],'review_days':[20,22,23]}}
contracts=[]
for mid,title,district,goal,bonus,consequence,nxt in rows:
 contracts.append({'id':mid,'title':title,'day':int(mid[1:]),'district':district,'primary':goal,'optional':bonus,'carry_forward':consequence,'next':nxt,
  'outcome_rule':'success when all explicitly required milestones are completed; partial when at least one required milestone is completed; otherwise failed. Withdrawal uses the achieved milestones rather than paying a second reward.',
  'infrastructure_delta':{'success':1,'partial':0,'failed':-1} if mid in infrastructure_missions else {'success':0,'partial':0,'failed':0},
  'failure_next_mission_complication_cap':1,'requires_named_hero':False,
  'failed_transition':'The next site remains available, with the recorded local consequence. No success prerequisite.',
  'basic_action_contract':'Core objective or an orderly retreat must be expressible with universal actions. Concrete board layouts still require tactical verification.'})
world={'version':'0.3','district_initial':{d:1 for d in districts},'district_bounds':[0,3],
 'missions':contracts,'evidence':evidence,'record_review':'One evening project verifies one named record after its source incident. No supplies, no named hero, no duplicated record counts. Maximum two projects per evening including all other projects.',
 'evidence_timing_contract':'Cross-district public copies become accessible after communications recover on day 20. Late verification can restore route eligibility but cannot undo expired promises, settled personal choices or past rescue losses. Early field evidence enables earlier informed interventions; each associated authored scene must implement that timing difference.',
 'endings':{'shared_control':'final selected route=shared_control, mission M24 success, infrastructure sum>=10, >=2 distinct verified evidence IDs','distributed_rebuild':'final selected route=distributed_rebuild and M24 success; evidence not required','evacuation':'selected evacuation, or the final selected objective fails/partially succeeds. World coda uses preserved district and rescue records.'},
 'ending_priority':['resolve actual final mission outcome','select one world ending','resolve each hero: withdrawn before personal arc before relationship coda','append district and relationship codas'],
 'no_named_hero_requirement':True,'no_automatic_forgiveness_from_evidence':True,'no_post_final_activity':True}
write('campaign_world_contract.json',world)

coordination={'version':'0.3','stages':['briefing','main_assignment','main_action','main_settlement','side_offer_or_skip','side_action_if_accepted','side_settlement','camp_two_projects','night_recovery','next_briefing'],
 'final_day_override':'After M24 settlement go directly to ending. Day 23 is the last normal camp.',
 'assignment_receipt':'One actor can hold one assignment in a given phase. A main-duty hero may take the later side duty if the known fatigue and health constraints still pass; no duplicate idle-day recovery.',
 'side_windows':'Offers last through the next duty day, capped at day 23. At most one side duty per day. A resolved or expired offer cannot be replayed.',
 'reward_receipt':'Key by mission ID and result transaction ID; rewards, recruits, district effects, XP and memories commit together once.',
 'relationship_receipt':'Key by event ID, observer, target and opportunity; common mission participation is not proof of cooperation.',
 'conflict_queue':{'priority':['immediate safety relevance','explicit promise expiry','severity band','earliest triggering command index','stable relationship ID'],'interruptions_per_squad_per_mission':1,
  'persistent_constraints':'All declared cooperation conditions are visible in action previews. The scene cap does not silently remove another pair’s restrictions.',
  'after_cap':'Further consequences appear in the result preview and log, and any extended conversation moves to camp. Basic actions remain available. No additional forced action or secret sabotage.',
  'pending_event':'At camp recalculate relevance. Resolve by chosen remedy, schedule a concrete next opportunity, or explicitly choose professional distance. Never automatically forgive it because the queue was full.'},
 'safety_of_commit':'Preview predicted relationship restrictions before spending AP/resources on the triggering choice. Already committed actions are not retroactively changed.',
 'strongest_team_tradeoff':'A fixed squad can remain useful, but sustained deployment requires recovery projects that compete with equipment, training, investigation and relationship work. Rotation preserves camp projects but spreads mission XP. No intention to force every character to equal win rate.'}
write('campaign_coordination_contract.json',coordination)

# Keep the existing full-product tables in sync with the adopted flow decisions.
p=read('product.json');p['design_version']='0.3-flow-contracts';p['start_resources']=economy['start'];p['daily_upkeep']='0：基本食宿由社区保障；物资用于战术、加速治疗与训练。';p['reward_design']=economy['main_rewards'];p['death_policy']='从容与标准：可恢复重伤；严峻：明示救援期限内未救出的失能队员可能永久医疗离队，不是随机死亡。';write('product.json',p)
r=read('rules.json');r['recovery'].update(main_fatigue=economy['fatigue']['main_cost'],side_fatigue=18,fatigue_warning=60,fatigue_deploy_limit=None,projected_fatigue_limit=100,dedicated_rest_extra_fatigue_reduction=12,idle_day_fatigue_reduction=16)
r['recovery']['permanent_withdrawal_difficulty']='hard';r['recovery']['automatic_permanent_loss_on_conflict']=False;r['recovery']['serious_injury_treated_days']=1
r['progression']['main_xp_each_deployed']=economy['growth']['main_xp'];r['progression']['side_xp_each_deployed']=economy['growth']['side_xp']
r['relationship']['conflict_control']='basic actions stay controlled by player; only specific cooperation restrictions';write('rules.json',r)
registry=read('mission_registry.json')
for m in registry:
 if m['kind']=='main':
  c=next(c for c in contracts if c['id']==m['id']);m.update(title=c['title'],objective=c['primary'],optional_objective=c['optional'],status='flow_contract_defined_board_not_authored',contract_ref='campaign_world_contract.json#'+m['id'])
 else:m['offer_expires_day']=min(23,m['day']+1)
write('mission_registry.json',registry)

class PaperCampaign:
 """Outcome-fed design model: it does NOT infer combat victories or player fun."""
 def __init__(self,resources=None):
  self.resources=deepcopy(resources or economy['start']);self.world=deepcopy(world['district_initial']);self.evidence=set();self.resolved=set();self.rows=[];self.absent=set();self.projects={};self.final_route=None
 def resolve(self,mid,outcome='success',reserve_count=0,record=None):
  if mid in self.resolved:raise ValueError('duplicate settlement')
  c=next(x for x in contracts if x['id']==mid)
  assert len(self.resolved)+1==c['day']
  if mid=='M24' and self.final_route is None:raise ValueError('final route must be confirmed before mission')
  reward=deepcopy(economy['main_rewards'][outcome]);reward['credits']=max(6,reward['credits']-4*reserve_count)
  before=deepcopy(self.resources)
  for k,v in reward.items():self.resources[k]+=v
  self.world[c['district']]=max(0,min(3,self.world[c['district']]+c['infrastructure_delta'][outcome]))
  if record:
   assert mid in evidence[record]['direct'];self.evidence.add(record)
  self.resolved.add(mid)
  row={'day':c['day'],'mission':mid,'outcome':outcome,'before':before,'reward':reward,'after':deepcopy(self.resources),'infrastructure':sum(self.world.values()),'evidence':sorted(self.evidence),'reserves':reserve_count}
  self.rows.append(row)
  return row
 def spend(self,cost):
  if any(v<0 for v in cost.values()):raise ValueError('negative cost')
  if not all(self.resources[k]>=v for k,v in cost.items()):return False
  for k,v in cost.items():self.resources[k]-=v
  return True
 def review(self,record,day):
  if day != len(self.resolved) or day>=24 or day not in evidence[record]['review_days']:raise ValueError('review unavailable')
  if record in self.evidence:return False
  if self.projects.get(day,0)>=2:raise ValueError('camp project budget exhausted')
  self.evidence.add(record)
  self.projects[day]=self.projects.get(day,0)+1
  self.rows[-1].setdefault('camp_reviews',[]).append(record)
  self.rows[-1]['after_camp_evidence']=sorted(self.evidence)
  return True
 def available_routes(self):
  return ['evacuation','distributed_rebuild']+(['shared_control'] if sum(self.world.values())>=10 and len(self.evidence)>=2 else [])
 def choose_final(self,route):
  if len(self.resolved)!=23 or route not in self.available_routes():raise ValueError('invalid final choice')
  self.final_route=route
 def ending(self):
  if len(self.resolved)!=24:raise ValueError('premature ending')
  return self.final_route if self.rows[-1]['outcome']=='success' else 'evacuation'

checks=[]
def check(label,x):
 if not x:raise AssertionError(label)
 checks.append(label)

traces={}
normal=PaperCampaign()
for c in contracts:
 if c['id']=='M24':normal.choose_final('shared_control')
 record=next((k for k,v in evidence.items() if c['id']==v['direct'][0]),None)
 normal.resolve(c['id'],'success',record=record)
check('normal full trace reaches shared control',normal.ending()=='shared_control');traces['normal']=normal.rows
disaster=PaperCampaign({'credits':0,'supplies':0,'parts':0})
disaster_withdrawn=set()
all_characters=read('characters.json')
for c in contracts:
 if c['id']=='M24':disaster.choose_final('evacuation')
 available=[x['id'] for x in all_characters if (x['join']<c['day'] or x['join']==1) and x['id'] not in disaster_withdrawn]
 deployed=available[:3]
 row=disaster.resolve(c['id'],'failed',reserve_count=3-len(deployed))
 # Extreme hard-mode trace: every deployed named hero misses an explicitly
 # announced retrieval deadline. This is supplied input, not a combat prediction.
 disaster_withdrawn.update(deployed)
 row['named_team']=deployed;row['withdrawn_after_mission']=sorted(disaster_withdrawn)
check('all-failure abstract trace settles 24 duties without resource debt',len(disaster.resolved)==24 and all(v>=0 for v in disaster.resources.values()))
check('all-failure trace has a complete alternative ending',disaster.ending()=='evacuation');traces['all_failed']=disaster.rows
isolation=PaperCampaign()
for c in contracts:
 if c['id']=='M24':
  check('missing-evidence route is disabled before committing final mission','shared_control' not in isolation.available_routes())
  isolation.choose_final('distributed_rebuild')
 isolation.resolve(c['id'],'success')
check('isolation route does not require evidence or named hero',isolation.ending()=='distributed_rebuild')
traces['isolation_no_evidence']=isolation.rows
reviewed=PaperCampaign()
for c in contracts:
 if c['id']=='M24':reviewed.choose_final('shared_control')
 reviewed.resolve(c['id'],'success')
 if c['day']==20:reviewed.review('E_ORDER',20)
 if c['day']==22:reviewed.review('E_WARNING',22)
 if c['day']==23:
  check('duplicate evidence does not consume another project or grant credit',reviewed.review('E_ORDER',23) is False and len(reviewed.evidence)==2)
check('missing direct evidence can be recovered before the ending',reviewed.ending()=='shared_control')
traces['public_evidence_recovery']=reviewed.rows
try:reviewed.review('E_MAINTENANCE',23);late=False
except ValueError:late=True
check('no retroactive evidence lookup after the final mission',late)
recovery=PaperCampaign({'credits':0,'supplies':0,'parts':0})
recovery.resolve('M01','failed',reserve_count=0)
recovery.rows[-1]['injury']={'lin':{'injury_day':1,'ordinary_ready_day':3}}
check('free ordinary recovery is not gated by buying treatment',not recovery.spend({'supplies':2}) and recovery.resources['supplies']==0)
recovery.resolve('M02','failed',reserve_count=1)
recovery.rows[-1]['named_team']=['xu','su']
recovery.rows[-1]['injury']={'xu':{'injury_day':2,'ordinary_ready_day':4}}
check('two failed duties still leave valid resource state',recovery.resources=={'credits':12,'supplies':0,'parts':0})
check('optional expedited treatment can be bought after two allowances',recovery.spend({'credits':8}))
recovery.resources['supplies']+=2;check('treatment cost has explicit payment',recovery.spend({'supplies':2}))
recovery.rows[-1]['camp_treatment']={'actor':'xu','treated_ready_day':3,'cost_credits_to_buy_two_supplies':8,'remaining_resources':deepcopy(recovery.resources)}
check('two failures can return the original team on day three',1+2==3 and 2+1==3 and recovery.resources=={'credits':4,'supplies':0,'parts':0})
traces['two_failures_zero_stock']=recovery.rows
before=deepcopy(normal.resources)
try:normal.resolve('M24','success');duplicate=False
except ValueError:duplicate=True
check('duplicate mission reward rejected',duplicate and normal.resources==before)
check('new crew cannot create a food-tax penalty',p['daily_upkeep'].startswith('0'))
check('projected fatigue test rejects cap-and-reset exploit',not (88+economy['fatigue']['main_cost']<=100))
check('a fresh main-duty actor can take a side duty',economy['fatigue']['main_cost']+economy['fatigue']['side_cost']<=100)
check('late exhausted actor cannot double-deploy',70+economy['fatigue']['main_cost']<=100 and not (70+economy['fatigue']['main_cost']+economy['fatigue']['side_cost']<=100))
check('there are no side duties after final settlement',all(m['day']<24 and m.get('offer_expires_day',23)<24 for m in registry if m['kind']=='side'))
check('all evidence has multiple direct sources and explicit public review windows',all(len(v['direct'])>=2 and v['review_days'] for v in evidence.values()))
check('each main milestone has an explicit no-named-hero fallback contract',all(not c['requires_named_hero'] for c in contracts))
check('normal and hard differ in loss policy, not basic action control',policy['loss_is_not_random_death'] and r['recovery']['automatic_permanent_loss_on_conflict'] is False)

def loss_state(difficulty,retrieved,deadline_expired,abandoned=False):
 if retrieved:return 'recoverable_injury'
 if not deadline_expired and not abandoned:return 'incapacitated'
 return 'permanent_medical_withdrawal' if difficulty=='hard' else 'recoverable_injury'
check('ordinary and standard never impose permanent loss on a missed rescue',all(loss_state(d,False,True)=='recoverable_injury' for d in ['relaxed','standard']))
check('hard-mode timely retrieval still saves the developed character',loss_state('hard',True,False)=='recoverable_injury')
check('hard-mode loss needs a missed deadline or confirmed abandonment',loss_state('hard',False,False)=='incapacitated' and loss_state('hard',False,True)=='permanent_medical_withdrawal' and loss_state('hard',False,False,True)=='permanent_medical_withdrawal')
conflicts=[{'id':'lin>xu','safety':1,'expiry':0,'band':3,'command':5,'constraint':'independent_protection'},
           {'id':'su>xu','safety':1,'expiry':0,'band':3,'command':4,'constraint':'confirm_before_joint_relay'}]
queue=sorted(conflicts,key=lambda x:(-x['safety'],-x['expiry'],-x['band'],x['command'],x['id']))
assert len({actor for item in conflicts for actor in item['id'].split('>')}) <= 3
scene=queue[:1];deferred=queue[1:];constraints={x['constraint'] for x in queue}
check('two conflicts select one deterministic scene without dropping restrictions',scene[0]['id']=='su>xu' and len(deferred)==1 and len(constraints)==2)
check('constraint categories do not override universal movement or first aid',constraints.isdisjoint({'move','stabilize','basic_attack','extract'}))

# Actual fatigue/XP/project opportunity-cost comparison, not combat-win simulation.
characters=read('characters.json')
def roster_trace(style):
 states={c['id']:{'fatigue':0,'xp':0} for c in characters};rows=[];recovery_projects=0;training_projects=0;reserves=0;resources=deepcopy(economy['start'])
 main_cost=economy['fatigue']['main_cost']
 for day in range(1,25):
  active=[c['id'] for c in characters if c['join']<day or c['join']==1]
  for c in characters:
   if c['join']==day-1 and c['join']!=1:states[c['id']]['xp']=r['progression']['chapter_recruit_xp_floor'][(c['join']-1)//6]
  available=[x for x in active if states[x]['fatigue']+main_cost<=100]
  if style=='fixed':available.sort(key=lambda x:(x not in ['lin','xu','su'],['lin','xu','su'].index(x) if x in ['lin','xu','su'] else states[x]['fatigue']))
  else:available.sort(key=lambda x:(states[x]['fatigue'],states[x]['xp'],x))
  deployed=available[:3];borrowed=3-len(deployed);reserves+=borrowed
  for k,v in economy['main_rewards']['success'].items():resources[k]+=max(6,v-4*borrowed) if k=='credits' else v
  for x in deployed:states[x]['fatigue']+=main_cost;states[x]['xp']+=5
  projects=0;project_actors=set()
  if style=='fixed' and day<24:
   need=[x for x in deployed if states[x]['fatigue']-12>64]
   for start in range(0,len(need),2):
    if projects==2:break
    group=need[start:start+2]
    for x in group:states[x]['fatigue']=max(0,states[x]['fatigue']-12);project_actors.add(x)
    projects+=1;recovery_projects+=1
  if day<24:
   tomorrow=[c['id'] for c in characters if c['join']<=day]
   def next_fatigue(x):return max(0,states[x]['fatigue']-12-(16 if x not in deployed else 0))
   while projects<2 and sum(next_fatigue(x)+main_cost<=100 for x in tomorrow)<3:
    candidates=[x for x in active if x not in project_actors and next_fatigue(x)+main_cost>100 and max(0,next_fatigue(x)-12)+main_cost<=100]
    if not candidates:break
    group=sorted(candidates,key=next_fatigue)[:2]
    for x in group:states[x]['fatigue']=max(0,states[x]['fatigue']-12);project_actors.add(x)
    projects+=1;recovery_projects+=1
   remaining=[x for x in active if x not in project_actors and states[x]['fatigue']+8<=100]
   remaining.sort(key=lambda x:(states[x]['xp'],x))
   while projects<2 and remaining:
    group=[]
    for x in list(remaining):
     trial=deepcopy(states);trial[x]['fatigue']+=8
     for already in group:trial[already]['fatigue']+=8
     tomorrow=[c['id'] for c in characters if c['join']<=day]
     ready=sum(max(0,trial[y]['fatigue']-12-(16 if y not in deployed else 0))+main_cost<=100 for y in tomorrow)
     if ready>=3:group.append(x)
     if len(group)==2:break
    if not group:break
    missing=max(0,len(group)-resources['supplies'])
    if resources['credits']<missing*4:break
    resources['credits']-=missing*4;resources['supplies']+=missing
    resources['supplies']-=len(group)
    for x in group:states[x]['fatigue']+=8;states[x]['xp']+=3;remaining.remove(x);project_actors.add(x)
    projects+=1;training_projects+=1
  if day<24:
   for x in active:states[x]['fatigue']=max(0,states[x]['fatigue']-12-(16 if x not in deployed else 0))
  rows.append({'day':day,'team':deployed,'reserves':borrowed,'evening_projects':projects,'state':deepcopy(states),'resources':deepcopy(resources)})
 return {'style':style,'recover_projects':recovery_projects,'training_projects':training_projects,'borrowed_slots':reserves,'final':states,'resources':resources,'days':rows,
         'assumptions':'Both scripts preserve at least three projected eligible actors before spending on training. All main outcomes are supplied as success; no side missions, injuries or relationship interference. Training and purchases are paid from the same reward rules. These are illustrative policies, not optimal strategies or player-win simulations.'}
comparison=[roster_trace(x) for x in ['fixed','rotation']]
check('roster scheduling never double-books more than three main heroes',all(len(t['team'])<=3 and len(t['team'])==len(set(t['team'])) for s in comparison for t in s['days']))
check('camp schedule stays within two projects',all(t['evening_projects']<=2 for s in comparison for t in s['days']))
check('fatigue comparison stays in valid range',all(0<=v['fatigue']<=100 for s in comparison for t in s['days'] for v in t['state'].values()))
check('training and purchase costs stay within earned resources',all(v>=0 for s in comparison for t in s['days'] for v in t['resources'].values()))
result={'version':'0.3','date':'2026-10-31','passed':len(checks),'checks':checks,'traces':traces,'roster_comparison':comparison,
 'limits':['Mission outcomes are supplied, not inferred from playable boards.','No claim about player enjoyment, actual playtime or strategic win rates.','All-failure trace verifies accounting and ending rules, not the physical feasibility of unbuilt maps.','Conditional narrative text and full character arcs are not authored by this script.']}
(ROOT/'outputs/flow-review-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'normal_end':normal.ending(),'disaster_end':disaster.ending(),'roster':[{k:v for k,v in x.items() if k not in ['days','final']} for x in comparison]},ensure_ascii=False,indent=2))
