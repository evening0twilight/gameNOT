"""0.14 cross-system design correction; does not modify the product runtime."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
def read(n):return json.loads((D/n).read_text())
def write(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
c=read('combat.json');c['version']='0.14-full-audit'
carry='许舟抛索：未满5级携带伤员时须邻接实际部署的winch锚点；5级个人携带例外不要求锚点，亦不生成给别人用的免费锚点。其他AP、次数、单格障碍与干地空落点规则不变。江朔交接/实际药剂补给保留原携带例外。'
c['carrying_exception']=carry;c['geometry']['movement']='四方向加权移动，可经过站立友军但不能停在友军格；不能穿过未毁机器、墙或深水。抛索例外统一读取carrying_exception。'
c['resolution_amendments']['tools']='永久装备任务前分配，任务内不交接刷新次数；部署锚点持续本任务，个人抛索不回收锚点。携带例外只读carrying_exception。屏障不能通过免费拾放回满HP。'
for a in c['actions']:
 if a['id']=='pickup':a['effect']=a['effect'].split(' 明确例外')[0]+' 明确例外统一读取carrying_exception，不另保留旧版锚点限制。'
c['medical_rules']='医疗恢复最多3HP，以上限10+L4加1+L6加1截断；离场或失能者不可治疗，本关不能复活。急救包禁止携带时操作；江朔可携带操作但接收者须空手。必须消耗实际打包药剂和1AP。基础急救包2次，工坊II出勤快照为3次；江朔技能次数不变。'
c['command_transaction']='合法性与执行使用同一规则。检查角色、目标、已获专长、当前AP/次数、实际关系条件、持物和场景状态；拒绝后包括锚点、次数、药剂、AP、贡献记录在内全部不变。'
c['save_and_undo']='稳定玩家阶段、营地允许手动保存；自动保存出发前、轮初和终结结算前。0.14存档清单见full_audit_contract.json。读档不能重置次数/冷却或重复结算；旧规则存档先迁移校验，失败保留原文件并说明不兼容。当前尚无正式游戏存档实现。'
write('combat.json',c)
f=read('facilities.json')
for x in f:
 if x['id']=='workshop':x['tier2']='医疗分装：药剂单品上限2→3，队伍总容量仍3；急救包每任务次数2→3。药剂仍每份1物资、治疗仍1AP；不增江朔专长次数，不免费生成药剂。'
write('facilities.json',f)
e=read('equipment.json');e['inventory']='永久工具全队每种最多一件，三人各tool/support一槽；任务内不交接刷新次数。当前唯一耗材为医疗药剂，队伍总容量3、单品默认2，工坊II后单品3；未用药剂撤退后回仓，已用不返。永久工具不因角色离队丢失。'
e['craft']='仅制作医疗药剂，每份1物资。打包不再次付费，使用扣任务内库存，未用回仓。工坊II是增加可用药剂与急救包次数，不再是无效的总容量3→4。'
for x in e['items']:
 if x['id']=='medkit':x['effect']='1AP使用实际打包药剂，为站立且未离场队友恢复最多3HP，截断到该角色当前等级HP上限；基础2次，工坊II出勤快照3次。不复活、不空耗药剂、不在携带时操作。'
write('equipment.json',e)
g=read('growth_identity_contract.json');g['version']='0.14-full-audit'
g['positive_relationships']['renegotiation']='营地关系页提供重新协商：占1短谈，同一人物对每日最多改一次，双方已加入且未永久离队。重复选择当前约定不收费、不刷新；只改变未来共同安排，不清事件记忆、不返还成本、不重置每章带教次数。第24日不再补谈。'
g['positive_relationships']['dispatch_draft']='出发前可免费取消改派并返回普通出口；改变阵容后重新检查，失效草案自动撤销并显示免费出口，确认新出发预览后才提交。选择草案不扣物资/经验，不占后勤班次；只有实际deploy付费，出发后不再改派。'
g['positive_relationships']['history_scope']='两次不同任务中双方各有真实目标贡献。排除涉及这两人的已记录违约；不把无关第三人的违约归到他们头上。缺少归责元数据的旧记录不自动判定为无关。与正向信任奖励要求同一目标的规则分开：资格不直接发信任。'
write('growth_identity_contract.json',g)
p=read('production_scope.json');p['version']='0.14-full-audit';p['growth']['L1']='获得第一专长；次数以abilities条目为准，叶禾分路隔离1次，其余按各自定义。';p['audit_ref']='full_audit_contract.json';write('production_scope.json',p)
p=read('player_choice_contract.json');p['version']='0.14-full-audit';write('player_choice_contract.json',p)
i=read('integration.json');i['authority']='当前设计0.14：design_manifest.json列出有效规则及其领域；历史审查报告只证明当时覆盖，不覆盖本次修订。运行工程尚未实现完整规则。';i['full_audit_authority']='full_audit_contract.json'
for row in i.get('resolved_contradictions',[]):
 if '60信任' in row[1]:row[1]='基础贡献与真实合作均可形成凭据；四项协作无统一信任门槛，按具体关系与安全条件检查。'
if 'logical_audit_sections' in i:
 i['logical_audit_sections']['combat_resolution']['carrying_actions']=carry
 i['logical_audit_sections']['combat_resolution']['tools']=c['resolution_amendments']['tools']
write('integration.json',i)
w=read('whole_campaign_contract.json');w['version']='0.14-full-audit';w['one_state']['positive_plans']='关系节点选择、当日重新协商记录、每学员每章带教使用集合、出发前接应安排与后勤扣费回执、药剂容量出勤快照'
for row in w['decisions']:
 if row[0]=='玩家临时换队怎么办':row[1]='出发前按实际三人重新检查。四项协作无需学习标记，缺少搭档或保障时不可用，基础动作仍可用。'
write('whole_campaign_contract.json',w)
contract=dict(version='0.14-full-audit',formal_development=False,
 authority='领域规则见design_manifest.json；标记retired的技能和装备只保留历史，不能当作当前内容覆盖数。',
 snapshot=dict(campaign=['日期与阶段','当前与已结算任务ID','选定世界路线和目标','资源/库存/打包/消耗','成员加入/重伤/离队/经验/倾向/疲劳','项目和短谈占用','地区与永久上限','人物承诺及创建/履约/违约凭据','合作约定与重新协商日','带教学员-章节集合','接应选择及后勤成本'],
 battle=['规则版本与数据指纹','地图/环境变体','轮次与锁定预告','AP/HP/携带者/失能期限','技能与工具次数','已部署锚点/屏障/绝缘','危险输出隔离及原供电状态','AP转交同轮接收标记','目标进度/失去/送达/贡献','已排队增援','当前出口和现场服务进度','实际关系限制与本次明确同意','药剂容量出勤快照'],
 social=['有向旧怨与信任','每条事实及首次知情时间','活跃/归档记忆幅度与修复阶段','关系阶段及冲突冷却','每任务正负变化额度','个人压力/自责负荷','待核实误会及已处理证据','已处理事件ID','教程首次触发/关闭/排队状态']),
 persistence='情绪与事件以Social状态为权威，营地账本保存对应投影；加载先恢复阶段与记忆，再同步投影，不重复发奖励。保存规范与离线JSON往返检查不是正式存档实现。预览不可写状态；读档校验版本及指纹，不能兼容时保留旧档。结算以任务ID去重，写入失败整体回滚。UI提示和当前选择不重新发奖励。',
 usability=dict(cannot_act='显示具体原因及可选普通行动；无AP可结束回合；无可行救援可确认撤退，禁止没有退出路径的窗口。',
 medication='同时显示药剂库存、打包量、工具次数和角色最大HP；满血/离场/失能者不成为可点击治疗目标。',
 workshop='购买前明确多带一份药剂且急救包多用一次；无药剂时提示当前不会产生治疗次数收益，不把库存凭空补满。',
 relationship='共同约定、实际合作资格、当前暂停原因分开显示；不把好友的第三方纠纷当作本人的过错。重新协商不等于原谅。',
 failure='最后撤出者、目标即将过期、最高难度永久医疗离队均显示具体对象；保留原有失败继续到结局政策。'),
 release_design_gaps=['8个人物的最终立绘/棋子及风格一致性尚未验收','96节点是状态与内容设计，完整对白、演出与文字质量尚未全部完成','等级和装备的真实选择率/时间价值未经过真人测试','键鼠操作、文字缩放、信息密度和新手理解仍只有设计要求','正式存档/迁移、预览执行一致性、运行性能与兼容尚未实现验收'],
 verification_boundary='本次全量指逐域审查并覆盖全部关卡与分支数据；不等于穷举所有行动序列、证明不存在最佳阵容或证明玩家喜欢。旧结果注明旧版本，新规则另作回归。')
write('full_audit_contract.json',contract)
manifest=dict(version='0.14-full-audit',stage='design_only',domains={'battle':'combat.json','active_scope':'production_scope.json','growth_and_positive_plans':'growth_identity_contract.json','emotion':'progression_relationship.json','inventory':'equipment.json','facilities':'facilities.json','boards':'boards.json','stories':'stories.json','campaign':'whole_campaign_contract.json','integration':'integration.json','guidance':'player_experience_contract.json','audit_and_persistence':'full_audit_contract.json'},precedence='当前领域文件优先；历史补丁只在当前领域明确引用的部分有效。retired条目和历史报告不重新激活能力。')
write('design_manifest.json',manifest)
# Remove active copies of superseded rules and clarify finite narrative capacity.
a=read('abilities.json')
for x in a:
 if x['id']=='su_3':x['level5_effect']=x['level5_effect'].replace('当前AP不超过3','接收前AP最多2、接收后最多3')
write('abilities.json',a)
g=read('growth_identity_contract.json');g['level5']['su_3']=next(x['level5_effect'] for x in a if x['id']=='su_3');write('growth_identity_contract.json',g)
e=read('equipment.json')
for x in e['items']:
 if x['id']=='insulation':x['valid_target_tags']=['ground_not_wall_or_deep_water'];x['effect']='1AP铺一格绝缘持续本任务，可提前铺在干地、碎石或浅水；不能在墙/深水铺。只免电伤，不改变占位、通行或火伤。'
write('equipment.json',e)
p=read('progression_relationship.json');p['version']='0.14-full-audit';p['protocol_training']='四项协作无需学习且无统一60信任门槛，仍检查具体风险与关系保障。普通训练按training_rule；共同带教按growth_identity_contract，不额外发好感。';write('progression_relationship.json',p)
sysc=read('system_audit_contract.json')
if 'combat_resolution' in sysc.get('sections',{}):
 sysc['sections']['combat_resolution']['carrying_actions']=carry;sysc['sections']['combat_resolution']['tools']=c['resolution_amendments']['tools']
sysc['current_authority']='0.14 design_manifest.json；本文件保留被当前领域引用的情绪等规则，不能用历史战斗说明覆盖combat.json。';write('system_audit_contract.json',sysc)
st=read('stories.json');st['scheduler']['capacity_notice']='23个营地夜晚最多46段短谈；24个人节点+12关系节点合计36段可排入。18生活短谈、认责及重新协商共享剩余窗口，不承诺同周目全部发生；未读不扣好感、不锁主线或全部人物结局，不设必须看完54段的本周目要求。日志保留已读全文，未发生节点只留标题/状态/可见摘要，不伪造已经共同经历。第23晚只作一次未处理事项提醒。';write('stories.json',st)
ux=read('player_experience_contract.json')
for x in ux['guides']:
 if x['id']=='G04':x['copy']='今晚有2个重点安排和2次交谈；同一人最多参加一个重点项目。故事涉及实际安排时会同时占项目，确认前显示。'
 if x['id']=='G07':x['trigger']='首次准备受限的情境协作'
 if x['id']=='G09':x.update(first='首次查看新人物专长或3/5级升级',trigger='首次查看新专长或用途强化',copy='1/3级获得两项固定专长，5级强化其中一项；营地可切换的是2级倾向。',options='看本次解锁的用途与适用场景，再决定是否出勤',dismiss='关闭角色页',alternatives='不强制试用；普通办法仍可推进')
 if x['id']=='G10':x['options']='比较情境协作与普通交互的完整成本'
ux['current_context_help']={'medical':'显示当前人物HP上限、已打包药剂和剩余急救包次数；不能治疗时说明满血、失能、离场或缺药。','pact':'显示已选约定、两次真实合作资格、当前暂停原因以及重新协商入口；不显示独立合作经验条。','dispatch':'选择前并列普通/改派出口与费用；出发前可免费取消，换队失效后重新确认，未出发不扣钱。','capacity':'普通短谈、实际项目、生活择看分别显示占用；不靠未读红点强迫玩家补齐全部54段。'}
write('player_experience_contract.json',ux)
for n in ['development.json','logic-audit.json']:
 path=ROOT/'game/docs'/n;d=json.loads(path.read_text());d.update(design_version='0.14-full-audit',latest_review='../../outputs/full-audit-review.html');d['authored_this_revision']=['全域规则与覆盖审查','装备、医疗、工坊投资修正','关系归责与重新协商','存档状态清单和拒绝操作原子性'];path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Applied0.14 design contracts')
