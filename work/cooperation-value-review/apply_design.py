"""Apply the reduced final-product design scope; never edits runtime files."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
def read(n):return json.loads((D/n).read_text())
def write(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
active_tools=['crowbar','medkit','winch','shield','insulation','scanner','stretcher']
abilities=read('abilities.json')
for a in abilities:a['production_status']='active' if a['level'] in [1,3] else 'retired_0.12'
write('abilities.json',abilities)
equipment=read('equipment.json')
for e in equipment['items']:e['production_status']='active' if e['id'] in active_tools else 'retired_0.12'
equipment['craft']='0.12仅保留医疗药剂的库存打包，仍受队伍3份、单品2份上限；永久工具按原价格和解锁日期购买。取消泡沫、电池、信标、切割器、灭火器的购买/制作入口。原定义保留仅作历史记录，不能带入任务。'
write('equipment.json',equipment)
scope=dict(version='0.12-cooperation-value',date='2026-11-02',stage='design_only',
 decision='取消独立高级合作养成分支；四项协作改为情境行动，不将其当作培养回报。人物培养集中在两项专业能力、已有被动和人物关系履约。',
 abilities=[a['id'] for a in abilities if a['production_status']=='active'],equipment=active_tools,
 retired_abilities=[a['id'] for a in abilities if a['production_status']!='active'],retired_equipment=[e['id'] for e in equipment['items'] if e['production_status']!='active'],
 cooperation=dict(training_tree=False,learned_pair_flags=False,blanket_trust_threshold=False,actions=['protected_work','mutual_cover','relay_carry','coordinated_pull'],rules='沿用现有AP、距离、次数、真实路径与具体情境保障。移除每人物对学习标记和60信任总门槛。发生过具体冲突仍需要相应承诺、接收者安排或物理保障；基础动作不受剥夺。',ui='协作放入目标的情境行动菜单；隐藏无关操作，合法性预览解释当前需要的搭档/位置/保障。不新增合作经验条、解锁页或熟练度货币。'),
 growth=dict(L1='第一专长，每任务基础2次',L2='现有施工/移动被动二选一',L3='第二专长，固定保留两项，不另做三选二配装',L4='原有HP+1',L5='第一专长每任务次数2→3；仅改上限，不刷新当前任务次数',L6='原有HP+1并取得另一L2被动'),
 scope_caps=dict(board='固定8×8二维棋盘；36关数据化目标/布置，四种额外现场操作',crew='8人、3人出勤；每人最多2项专长',enemies='保留6种已有确定性预告模式，不新增Boss规则树',presentation='2D立绘/头像＋棋盘标记、少量通用移动和命中特效；不采用骨骼战斗动画或3D角色模型',platform='先完成单机桌面版本；一个规则结算器供预览、执行、存档和事件账本共用',not_in_scope=['实时战斗/物理连锁','联网/服务器/实时AI角色','程序生成地图','随机词条装备/武器技能树','额外第三专长分支','独立高级合作养成树','新天气伤害类型','即时动态全语音演出']),
 validation_limits=['离线规则通过不等于Godot界面、动画、存档恢复和目标设备通过','36关具名配置不是所有输入序列、全部专长装备组合的穷举','所有既有0.11报告属于旧方案证据；0.12必须使用新的复核记录'],
 engineering_contract=dict(command=['actor/partner/target/path','preflight eligibility and exact effects','single commit with stable receipt IDs'],preview='同一纯状态转换产生预览与提交结果，显示AP、落点、实际伤害、目标期限和明确关系条件；避免另一份UI规则。',save='只在稳定玩家阶段和营地落盘；保存预告、目标ID、库存、已用次数和事件去重ID；动作中途不写半个状态。',content='地图仅组合已验证目标和机器模板；新脚本机制必须替换现有机制而不是自动叠加。',acceptance=['同命令在相同状态产生相同预览和实际结果','存档恢复后下轮预告/目标期限/道具用量一致','移除人物或协作后仍有基础救援和继续结局路线','一次任务事实只结算一次关系、资源和剧情贡献','实机文字可读、输入反馈与新手理解由真人验证']),
 capacity_judgment='收敛后的二维确定性方案有可实施路径；现有仓库尚无可玩完整战役，不能据离线推演保证两人交付质量或报出可靠工期。开发能力的主要风险是集成和内容验收，并非单个算法。')
write('production_scope.json',scope)
p=read('progression_relationship.json');p['levels']['L5']=scope['growth']['L5'];p['levels']['L3']=scope['growth']['L3'];p['levels']['respec']='营地免费切换L2选择。每人固定两项专长；不重置HP、次数、关系或任务状态；任务内锁定。'
p['protocol_training']='0.12取消独立高级合作培养：四项协作均为无需学习的情境行动，无统一60信任门槛，仍按具体风险与关系检查保障。普通训练沿用每人1物资、+3经验、+8疲劳和1项目；不额外学协议或产生好感。'
p['production_scope_ref']='production_scope.json';write('progression_relationship.json',p)
c=read('player_choice_contract.json');c['version']='0.12-cooperation-value';c['cooperation_training']=dict(cost='无独立合作训练；普通人物训练成本不变',trust=None,unlocks=[],basic_actions=scope['cooperation']['actions'],xp='普通训练每人3经验，不发协作解锁奖励',rule=p['protocol_training']);c['production_scope_ref']='production_scope.json';write('player_choice_contract.json',c)
combat=read('combat.json');combat['production_scope_ref']='production_scope.json';combat['target_tags']='0.12轻障碍可用撬棍；远程停机探针仅用于已标记控制器。重障碍和供电工量均保留普通交互；退出本版本的切割器、电池等不能再购买或使用。绝缘、屏障、锚点与担架按保留规则工作。无泡沫延迟涨水、诱导信标和灭火工具。'
combat['safeguard_producers']['independent_anchor']='本任务实际部署的winch锚点及保护范围；xu_5已退出本版本，未部署库存不算保障。'
combat['carrying_exception']='携带时仍可用jiang_1交接、jiang_3实际耗材补给，以及在已部署winch锚点邻接出发的xu_1；各自AP、范围、次数、落点和关系条件保留。其余主动专长不开放。'
combat['geometry']['movement']=combat['geometry']['movement'].replace('winch or xu_5','winch')
write('combat.json',combat)
for name in ['development.json','logic-audit.json']:
 f=ROOT/'game/docs'/name
 if not f.exists():continue
 data=json.loads(f.read_text());data['design_version']='0.12-cooperation-value';data['latest_review']='../../outputs/cooperation-value-review.html'
 if name=='development.json':
  data['project_stage']='Design only. Advanced-cooperation investment challenged with stronger ordinary routes; production scope reduced. No runtime development.'
  data['current_production_scope']='data/final_design/production_scope.json'
  data['authored_this_revision']=['36 mission definitions retained; stronger ordinary-route and earned-cost comparisons','16 active specialties,7 active equipment types,4 situational cooperation actions; no separate pair-learning branch','L5 improves first-specialty charges rather than introducing8additional active effects']
 f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Applied0.12 design scope:16specialties,7tools,no independent cooperation progression; runtime untouched.')
