"""Cross-system receipts, branching verification and explicit conflict resolutions."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data';OUT=D/'final_design'
def save(n,x): (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
checks={
'lin':{'after':'P_lin_2.rotation','all':[{'receipt':'casualty_saved','mission_kind':'main','distinct_contributing_actors_min':2,'at_least_one_actor_not':'lin'}]},
'xu':{'after':'P_xu_2.bounded','all':[{'receipt':'mission_settled','actors_include':['xu'],'xu_standing_on_exit':True},{'receipt':'retreat_promise','deadline_default':'round_limit-2','kept':True}]},
'su':{'after':'P_su_2.rota','window_next_main_count':2,'all':[{'receipt':'assignments','no_support_actor':'su','for_all_in_window':True},{'receipt':'support_work','actor_not':'su','at_least':1}]},
'chen':{'after':'P_chen_2.fund','all':[{'receipt':'payment','purpose':'chen_compensation','credits':8},{'receipt':'objective_completed','kind':'work','contributor':'chen','mission_kind':'main'},{'receipt':'known_information','actor':'ye','fact':'chen_signed_responsibility'}]},
'ye':{'after':'P_ye_2.audit','all':[{'receipt':'evidence_verified','id':'E_MAINTENANCE'},{'receipt':'known_information','actor':'ye','fact':'maintenance_audit'}]},
'he':{'after':'P_he_2.delegate','all':[{'receipt':'mission_settled','actors_include':['he'],'hero_all_extracted':True},{'receipt':'objective_completed','primary_contributor_not':'he'},{'receipt':'protect_or_rescue','actor':'he'}]},
'mo':{'after':'P_mo_2.redact','any':[{'receipt':'public_record_release','privacy':'redacted'},{'receipt':'objective_completed','mission':'M22','objective':'privacy'}],'invalidate_if':{'receipt':'public_record_release','privacy':'unredacted'}},
'jiang':{'after':'P_jiang_2.settle','not_before_day':23,'all':[{'receipt':'payment','purpose':'jiang_wages','credits':6}],'invalidate_if':{'receipt':'promise_breach','scope':'jiang_personnel_priority'}}}
save('integration.json',{
 'version':'0.4',
 'authority':'本目录是0.4内容与系统规范。外层旧JSON保留基础工程兼容，不应把旧的概述覆盖这里的具体关卡。冲突时以本目录及同步补丁为准。设计参数是可实施基线，不宣称最终数值无需实玩调整。',
 'receipt_schema':{'id':'campaign_id/mission_id/command_index/event_type/object_id','fields':['source_state_revision','campaign_day','round','actor_ids','observer_ids','object_id','previous_state','next_state','resource_delta','promise_id','information_scope'],'transaction':'先验证合法性、AP、库存、目标状态、前置与角色条件，再一次提交所有状态与事件；任何失败不扣AP、不留半条记忆。任务结算按mission_id幂等，包含角色加入、XP、地区、证据与奖励。'},
 'pipeline':['preflight_validity','preview exact cost, threat, relation attribution, irreversible loss','player confirm only when material risk changes','commit action state and receipt atomically','apply immediate known negative memories and re-evaluate future cooperation conditions','end-round enemy/environment/objective deadlines','settlement grants XP, proof of contributions and world facts once','camp decisions can create contracts; only future real receipts fulfill them','final route eligibility before M24; final objective results select world coda; character outcomes resolve separately'],
 'story_verifiers':checks,
 'receipt_time_rule':'默认验证凭据必须发生在承诺后。例外仅为ye已存在的维护证据与已知信息；她的核查项目本身提供新确认。mo可在既有privacy完成后承诺保持脱敏，但仍需本次选择产生公开回执。不能从三天前的无关好事补发新承诺信用。',
 'history_repair_routes':[
 {'pair':'lin>xu','stage1':'双方同意核对历史，xu确认执行过提前封闸，lin取得已知事实回执','stage2':'xu的bounded承诺被后续实际撤离验证','stage3':'此后另一个主任务双方共同完成救援且无同承诺违约','reductions':[6,12,12]},
 {'pair':'xu>lin','stage1':'lin同意把已证实责任和未知部分分开公开','stage2':'下一次公开回访未把未证实意图归为故意伤害','stage3':'后续双方共同完成基础目标','reductions':[6,12,12]},
 {'pair':'ye>chen','stage1':'完整验收附页和陈砚责任声明已知','stage2':'陈砚实际补偿付款且后续工作已兑现','stage3':'之后双方参与安全断电后的共同目标，叶禾明确选择接受专业合作','reductions':[6,12,12]},
 {'pair':'chen>ye','stage1':'双方按核实事实交谈且没有公开羞辱','stage2':'以后一个共同目标完成','stage3':'另一个共同目标完成','reductions':[6,12,12]},
 {'pair':'su>xu','stage1':'许舟确认额外承诺曾由苏棠收尾','stage2':'新的任务按时撤离，不再追加未经同意的接应','stage3':'另一主任务各自承诺均兑现','reductions':[6,12,12]},
 {'pair':'xu>he','stage1':'贺鸣公开事先授权范围','stage2':'he.delegate得到实证','stage3':'之后二人共同完成另一个目标','reductions':[6,12,12]},
 {'pair':'he>xu','stage1':'许舟确认停止条件','stage2':'xu.bounded得到实证','stage3':'之后二人共同守约','reductions':[6,12,12]},
 {'pair':'mo>chen','stage1':'陈砚说明签字与条件均存在','stage2':'陈砚补偿得到实证','stage3':'另一任务一起按事实做交接','reductions':[6,12,12]},
 {'pair':'chen>mo','stage1':'莫遥按来源标注日志','stage2':'公开记录已核实且脱敏','stage3':'后续共同目标交接仍无隐瞒','reductions':[6,12,12]}],
 'repair_limits':'历史修复依次解锁，按pair/stage去重，不同阶段要求不同的实际任务回执；减到0为止。无需全部修完才能通关。道歉修新记忆与历史修复分开，不对同一旧事故重复建记忆。',
 'late_breach_resolution':'个人线第三段较早选择integrated后，若又发生相关的未修复违约，最终改写为professional_ruptured_after_progress，明确曾有进展但后来受损；不得仍播放已经建立信任的结语。只有新的实际补救/守约凭据时间晚于违约才恢复，不能重放旧回执。职业选择仍尊重本人，附加关系事实。',
 'verifier_scope':'he的保护、队友贡献与安全撤离必须来自同一任务；xu的守约与撤离必须同任务；lin的两位贡献者必须是同一伤员的不同真实操作者。重复ID不算第二个人。',
 'missing_actor':'主线关卡和世界证据不引用角色必须在场。人物永久离队把pending执行合同转interrupted_by_injury，不判恶意背约；已付专项不退但社区仍落实，尾声说明谁接手。对方来信只包含其已知事实，不能凭空增加知情。',
 'bad_outcome_chain':'本关失败的世界成果真实保留；给下一主任务最多一个碎石格的现场不利，不叠加攻击、物价和伤势倍率。人物自己的伤势与丢失机会仍存在，保底只保证继续，不恢复成果。',
 'M17_override':'repair成功：泵区+1，上限3；isolate成功：泵区本次不加分且本局上限降为2，当前值超2截为2；两方案互斥。部分/失败按旧表0/-1；旧表笼统成功+1对此关不再适用。最终shared_control按实际各区之和判定。',
 'M24_override':'先选route，再使用boards.M24.route_groups；只激活该路线必需对象，其他路线对象不出现，archive保留。目标没完成则撤离尾声；选择evacuation且失败不是伪造全员成功撤离，按实际saved/lost名单写代价。',
 'environment_stacking':'第一次失败修饰只改变一格代价，不关闭通路；遇到设备水火与角色能力，先改变地形/电源，再按剩余预告结算。同格水火环境伤害取最大，护盾不能挡电。',
 'stacking_rules':'每次动作只算一次工量/目标完成。L2施工只作用于通用interact，不叠加工具的2工量。移动预算：基础3、搬运2、担架/安全搬运取3；各种临时移动加成只取最大+1，最高4。AP永不超过回合开始的2，不用击杀返AP。控制同机器后下一轮不能再次控制，永久停机不受临时控制冷却限制。',
 'injury_activity':'重伤者不能出勤、后勤或训练；可接受治疗、恢复和营地交谈。每晚一人至多一个付费/重点项目；免费短谈不占此项，但剧情最多两段。普通模式人物选择换职业只在终战后执行。',
 'difficulty_rescue':'最高难度的永久离队只来自明确救援失败/放弃失能者；关系冲突与人物职业选择绝不另加战役中强制离队。降难度只在营地生效，不追回已结算损失。',
 'responder_scope':'社区临时支援只保证主任务补齐3人；可选支线需3名合格主角，否则明确不可派遣并可跳过。因医疗缺席不能执行的约定记为interrupted而非恶意背约，地方机会仍会失去。',
 'disclosure_followup':'选择暂时私下保存资料后，可在后续该角色个人节点的附加选项申请定向分享；当事人明确同意才生成consent与known_information记录，不重发节点奖励。无同意不能由队长直接公开私人资料来刷修复。',
 'postgame':'结局后回到主菜单，可查看本周目日志与分支摘要；另开存档重玩，可选择已通关的A/B环境和不同投资，不保留等级压低难度。无无限刷资源模式，首次剧情完整收束。',
 'resolved_contradictions':[
 ['隐藏危险与完整预告','扫描仪改为出发前选择环境变体；开战后危险对所有玩家公开。'],
 ['三套养成只加伤害','等级解锁办法，装备改变路线/工量，关系改变协作方式；基本攻击不随等级倍增。'],
 ['为看故事挤掉全部恢复','短谈每晚两段免费；只有实质决定占项目；8条个人线的关键项目合计8个。'],
 ['人物收束全挤在最后三天','调整第三段开放日并排出36段个人/重点关系的可用日历；不保证所有额外生活短谈一周目读完。'],
 ['设备不开就无法救人、救不到人就缺技能','各关都有通用交互与停机开关；角色加入按主任务结算，不以成功为条件。'],
 ['低信任无法合作就永远不涨信任','基础贡献也能产生守约凭据；只有高级协议需要双方60信任。'],
 ['互相搬运刷信用和AP','同目标贡献去重；信任在任务结算发；所有协议支付双方AP，放下不触发奖励。'],
 ['M17修复和隔离收益完全相同','隔离更近工量更少，但失去排水恢复并降低地区上限；修复保留完整设施潜力。'],
 ['缺席人物仍在过场说话','明确临时伤势、永久医疗离队、战役后换职业三种状态；现场、来信、尾声分别处理。'],
 ['证据原件与后期公共副本等价','早得事实可提前履约；晚核查仅补路线资格，不撤销已经违约或错过的人物选择。'],
 ['工厂北侧资料被墙与两台机器封死','增加一个实际可走的侧门，路径检查覆盖所有任务对象，未用“默认有路”替代。']
 ]})
print('Authored cross-system receipts, eight proof verifiers, nine directed history-repair routes and resolved contradictions.')
