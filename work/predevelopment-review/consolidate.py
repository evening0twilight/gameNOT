"""Freeze a single design baseline; no Godot runtime files are written."""
from pathlib import Path
from copy import deepcopy
import json, hashlib, shutil
R=Path(__file__).resolve().parents[2]; W=Path(__file__).parent; D=R/'game/data'; F=D/'final_design'
V='0.18-predevelopment'; DATE='2026-11-04'
def read(p): return json.loads(p.read_text())
def write(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def runtime():return {str(p.relative_to(R)):digest(p) for p in (R/'game').rglob('*') if p.is_file() and (p.suffix in ['.gd','.tscn'] or p.name=='project.godot')}
if not (W/'before').exists():
 shutil.copytree(D,W/'before/game/data')
 for rel in ['game/README.txt','game/docs/development.json','outputs/full-game-design.html','work/cooperation-value-review/current_rules.py','work/player-choice-review/choices.py','work/growth-identity-review/relationships.py']:
  p=W/'before'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/rel,p)
 write(W/'runtime-before.json',runtime())
B=W/'before/game/data'
def orig(n):return read(B/(n+'.json'))
def final(n):return orig('final_design/'+n)
domains={}; views={}
def add(key,path,value):
 if isinstance(value,dict):
  value=deepcopy(value)
  for k in ['version','design_version']:
   if k in value:value[k]=V
  if 'date' in value:value['date']=DATE
 domains[key]=value;views[str((D/path).relative_to(R))]=key
def normalize(x):
 if isinstance(x,dict):return {k:normalize(v) for k,v in x.items()}
 if isinstance(x,list):return [normalize(v) for v in x]
 if isinstance(x,str):
  for a,b in [('最多+4信任','最多+3信任'),('上限+4信任','上限+3信任'),('单任务最多+4','单任务最多+3'),('正向信任每任务每方向上限4','正向信任每任务每方向上限3')]:x=x.replace(a,b)
 return x
scope=final('production_scope'); scope['validation_limits']=[
 '离线规则检查不等于Godot界面、存档、目标设备或真人体验验收。',
 '有限配置覆盖不是全部行动序列穷举；可作为开工基线，不能证明所有阵容等强。']
add('scope','final_design/production_scope.json',scope)
economy=orig('campaign_economy_contract');add('economy','campaign_economy_contract.json',economy)
product=orig('product');product.update(start_resources=economy['start'],reward_design=economy['main_rewards'],design_authority='final_design/design_manifest.json',implementation_status='设计基线已收敛；本轮未进入正式开发。')
product['scope']['equipment_archetypes']=7
product['scope']['target_first_play_hours']=[12,16]
product['scope']['target_is_measured']=False
product['scope']['duration_policy']='12–16小时仅内容节奏目标，不能作为已达时长或拖长关卡依据；真人记录主线/支线/阅读时间后再定商业承诺。'
product.pop('price_proposal',None);product['commercial_scope']='单机买断方向；售价、渠道、商店与发行决策另开讨论，本基线不创建充值货币或付费抽卡。'
add('product','product.json',product)
add('confirmed_policy','confirmed_experience_policy.json',orig('confirmed_experience_policy'))
add('characters','characters.json',orig('characters'));add('initial_relationships','initial_relationships.json',orig('initial_relationships'))
add('abilities','final_design/abilities.json',[a for a in final('abilities') if a['id'] in scope['abilities']])
add('enemies','final_design/enemies.json',final('enemies'))
equipment=final('equipment');equipment['items']=[x for x in equipment['items'] if x['id'] in scope['equipment']]
for e in equipment['items']:
 if e['id']=='shield':e['effect']='1AP放置4HP屏障，持续本任务，友军可穿过但不可落脚。每任务部署一次；本作不提供拾回/再部署操作，任务结算后工具自动归还，不能中途刷新HP。'
equipment['consumables']=[dict(id='med_dose',name='医疗药剂',recipe_supplies=1,base_pack_limit=2,workshop_II_pack_limit=3,team_pack_limit=3,slot='shared_inventory',use='由急救包/江朔实际补给消耗，未用归仓；不是可免费购买的永久工具。')]
add('equipment','final_design/equipment.json',equipment)
add('facilities','final_design/facilities.json',final('facilities'))
combat=final('combat');combat.pop('system_audit_ref',None)
combat['objective_machine']['outcome']='所有必需组各有一个secured目标才成功；否则已有必需原子里程碑则部分，其余失败。可选成果不抬高失败等级。lost后不能新完成或送达；先completed后lost的持续保全对象保留历史里程碑但不算secured。目标完成不自动终止玩家行动，时限继续运行。'
combat['resolution_amendments']['carrying_actions']=combat['carrying_exception']
combat['save_and_undo_ref']='player_flow.json#persistence'
combat['result_dimensions']={
 'mission_outcome':'由目标组计算success/partial/failed，决定报酬、XP和地区结果。',
 'crew_outcome':'分别记录站立撤出、带回重伤、未救回重伤/最高难度医疗离队；不偷改目标完成事实。',
 'personal_experience':'个人压力可以因有人受伤上升；用于个人评价的partial不得替代mission_outcome。',
 'promise_outcome':'逐条承诺核验；营救成功仍可能背约，任务失败仍可能守约。',
 'narrative':'先报目标事实，再报人员代价和具体承诺。示例：居民已救出，但陈砚重伤；不得改写为居民救援失败。'}
add('combat','final_design/combat.json',combat)
prog=normalize(final('progression_relationship'))
prog['levels']['respec']='每名角色单独记录L2倾向work/move，首次默认work并提示可免费更换。任务出发前（晨间、主线结算后支线准备、营地）均可切换；部署快照后锁定，不刷新当场次数。L6同时具有两项。'
families={'promise_breach':(12,8,False),'risk_concealment':(18,12,True),'unfair_assignment':(10,8,False),'public_blame':(14,10,False),'cost_overrun':(6,3,False)}
for e in prog['memory_events']:
 if e['id'] in families:e.update(zip(['severity','trust_loss','severe'],families[e['id']]))
prog['stress']={'range':[0,100],'initial':10,'negative_gain_cap_per_mission':12,'meaningful_rescue_relief_cap':4,'night':-8,'dedicated_rest_extra':-16,'appraisal_source':'player_experience_contract.json#appraisal','effect':'只由情境评价入口累计，不叠旧own_downing/witness_downing奖励。压力不减少AP、不产生随机拒绝。'}
prog['conflict_state']['hysteresis']='Q=min(100,R+0.25*max(压力−40,0))；按Q进入45/65/80，按Q严格小于35/50/60退出；R<25直接平静。保存已有阶段，不能只从当前阈值重算。'
edge=final('relationship_edge_cases')
prog['attribution_detail']=edge['attribution'];prog['recovery_detail']=edge['recovery'];prog.pop('relationship_edge_cases_ref',None)
prog['curve_formula']='raw=min(40,severity×share×clamp(sensitivity,.8,1.3)×(1+.7×(relevant_G/100)^2)×(1+.8×(R/100)^2)×(1+.25×stress/100)×(1+min(.4,.1×recent_same_category_count)))；近期为当日及前两日，旧怨仅相关类别放大；先算幅度再分配记忆预算。'
add('progression_relationship','final_design/progression_relationship.json',prog)
for key,name in [('growth','growth_identity_contract'),('training','training_value_contract')]:add(key,'final_design/'+name+'.json',final(name))
experience=final('player_experience_contract')
for k in ['integrated_revision','approach_revision','sources']:experience.pop(k,None)
experience['authority']='当前评价、性格和视觉规则；数值存储与修复在progression_relationship域。'
experience['appraisal']['single_owner']='评价入口是唯一正负关系结算者；禁止旧账本再发共同贡献或压力。夜间恢复只结算一次。'
experience['appraisal']['provisional']=experience['appraisal']['provisional'].replace('旧误归责纠正仍按0.6revoke执行','错误归责按原事件实际损失纠正，不发额外奖励')
experience['appraisal']['numeric_families']={k:dict(severity=a,trust_loss=b,category=c,severe=d) for k,a,b,c,d in [('breach',12,8,'promise',False),('unfairness',10,8,'fairness',False),('humiliation',14,10,'humiliation',False),('concealment',18,12,'promise',True),('cost_overrun',6,3,'fairness',False)]}
for g in experience['guides']:
 if g['id']=='G05':g.update(copy='先断路再恢复供电；可分工人工施工，或在有对应轻障碍时使用撬棍。现场备用组件只能带回，不能当作可消耗电池。',alternatives='单人分步施工／多人分工／先处理已知危险再施工')
 if g['id']=='G09':g['copy']='1/3级获得两项固定专长，5级强化其中一项；每名角色的2级倾向可在任务出发前免费切换。'
add('experience','final_design/player_experience_contract.json',experience)
fields=final('player_choice_contract')
old=final('approach_review_contract')
fields['asset_registry']={mid:{'source_enemy':x['source_enemy'],'meaning':'仅记录原设施是否保全，不是额外值守任务或自动奖励。'} for mid,x in old['services'].items()}
fields['authority_note']='当前仅services四项现场操作、investments两项营地修复。asset_registry十二处设施仅是事实归属，不能重新生成旧版十二项服务。'
add('field_operations','final_design/player_choice_contract.json',fields)
for key,path in [('world','campaign_world_contract'),('coordination','campaign_coordination_contract')]:add(key,path+'.json',orig(path))
whole=normalize(final('whole_campaign_contract'));whole.pop('system_audit_authority',None)
whole['one_state']['positive_plans']+='；training_completed按角色累计已用阶段、每学员每章带教使用记录均持久化，不随重谈清空。'
whole['scope_of_review']='完整状态契约；离线证据范围见当前验收清单，不视为正式程序已实现。'
add('campaign','final_design/whole_campaign_contract.json',whole)
integ=normalize(final('integration'))
logical=integ.pop('logical_audit_sections')
for k in ['resolved_contradictions','system_audit_authority','tactical_authority']:integ.pop(k,None)
integ['authority']='只整合当前域：目标事实→唯一结算→人物核验→正交结局。历史审查文档不覆盖本版。'
integ['attribution_detail']=logical['attribution']
integ['postgame']='结局后可只读查看当前周目日志；新开存档重玩，无跨周目等级/资源。首次开局固定A环境以保持教学可复现，首次通关后可在新存档选择A或B；章节支线/人际选择仍由玩家决定。'
add('integration','final_design/integration.json',integ)
stories=final('stories');stories['ending_resolution']['priority']=['presence:在队或医疗离队','career:已选择的职业方向','personal_plan:曾履约/仍待完成/医疗中断','relationship_overlays:仅覆盖各具体未修复方向的关系台词']
add('stories','final_design/stories.json',stories)
scripts=final('character_scripts');scripts['ending_priority']=stories['ending_resolution']['priority'];scripts['status']='96个完整中文场景已著写；分支条件和在场变体有离线检查，最终文字审读、演出和真人感受尚待验收。'
add('scripts','final_design/character_scripts.json',scripts)
boards=final('boards')
for b in boards['boards']:
 b['optional_reward_rule']='仅按campaign_economy_contract.objective_rewards的具体任务/对象ID发一次奖励；未列入的可选对象只记事实，没有通用额外物资奖励。'
 b['environment']['water_addition'].pop('foam_rule',None)
 b['environment']['fire_pulse']['rule']=b['environment']['fire_pulse']['rule'].replace('灭火立即清除并抑制下一次点火。','')
 b.pop('tactical_review',None)
 if b['id']=='M01':b['decision']='可分头稳定搬运，或先集中停机再救援；本教学关没有另设接触触发的失血倒计时，仍受整关时限与实际伤害约束。'
 if b['id']=='M02':
  b['decision']='先断开错误回路再用通用交互恢复电源；可单人施工或三人分工，先停机也可。备用组件仅是可选带回目标，不提供现场电池快捷操作。'
  b['consequence']='成功改变医疗区成果；带回spare奖励2零件，仅一次，详见经济表。'
  next(x for x in b['objectives'] if x['id']=='spare')['label']='带回备用电源组件'
 if b['id']=='S11':b['decision']='先完成人工供电，再选择是否投入连续现场操作；可先处理机器危险或用绝缘保护，放弃额外成果也可撤离。没有消耗电池捷径。'
add('boards','final_design/boards.json',boards)
ready=final('player_ready_contract');ready['controls']['end_turn']=ready['controls']['end_turn'].replace('仍可放下、撤离','仍可0AP放下或确认紧急撤退；正常出口离场仍需1AP')
add('player_readiness','final_design/player_ready_contract.json',ready)
audit=final('full_audit_contract')
audit['snapshot']['campaign']+=['每角色training_completed和L2倾向','难度变更历史/当前部署难度快照','支线接受/过期状态、手动存档槽与内容版本']
audit['snapshot']['battle']+=['苏棠每任务AP转交已用标记','全部角色L2首次施工/移动已用标记','不可逆提交边界与整组撤销快照']
audit['release_design_gaps']=['最终角色/场景/界面/声音资产尚未制作验收','96场景正文已著写，文学审读与运行时事实一致性待验收','真实玩家选择、理解、疲劳感和时长尚未测量','正式完整战役、保存恢复、性能与Windows实机兼容尚未实现验收']
add('persistence_inventory','final_design/full_audit_contract.json',audit)
# Keep source consumers working, but these files are generated views of one bundle.
for path,key in views.items():write(R/path,domains[key])
rules=orig('rules');rules.update(status='Generated compatibility projection of release_baseline.json; not an independent rule source.',design_version=V)
rules['tactical']['board_max']=[8,8]
rules['progression'].update(specialty_unlock_levels=[1,3],generic_cooperation_trust_min=None,equipped_cooperation_protocols_per_actor=0,advanced_protocol_requires_mutual_trust=False,level5_is_upgrade=True)
rules['relationship'].update(meaningful_cooperation_trust_gain=2,trust_reward_cap_per_pair_per_mission=3)
rules['relationship']['trust_reward_conditions']=['Both voluntarily contribute to the same successfully secured factual objective','Unique mission/root decision/direction; no same-incident violation','Base 2, at most 1 additional salient witness credit; directional mission cap 3']
rules['endings']['hero_epilogue_priority']=['presence','career','personal_plan','directional_relationship_overlays']
write(D/'rules.json',rules)
write(D/'equipment.json',equipment['items']);write(D/'enemies.json',domains['enemies'])
write(W/'compatibility-rules.json',rules)
write(F/'release_baseline.json',dict(version=V,date=DATE,stage='design_only',formal_development_authorized=False,domains=domains))
write(W/'views.json',views)
shutil.copy2(W/'before/outputs/full-game-design.html',R/'outputs/full-game-design-v017.html')
print('Consolidated',len(domains),'domains; runtime unchanged:',runtime()==read(W/'runtime-before.json'))
