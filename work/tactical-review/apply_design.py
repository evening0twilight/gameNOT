"""0.7 tactical design amendments; no production engine edits."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
def read(n):return json.loads((D/n).read_text())
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
b=read('boards.json');b['version']='0.7-tactical-review'
hard_limits={'M01':9,'M02':8,'M03':9,'M04':9,'M05':7,'M06':9,'M07':10,'M08':12,'M09':10,'M10':7,'M11':7,'M12':9,'M13':7,'M14':7,'M15':9,'M16':10,'M17':8,'M18':9,'M19':8,'M20':7,'M21':6,'M22':8,'M23':10,'M24':9,'S01':6,'S02':8,'S03':9,'S04':7,'S05':10,'S06':9,'S07':7,'S08':8,'S09':6,'S10':6,'S11':6,'S12':7}
timers={('M06','asset'):(6,'远端财物由第6轮末最后一班货运接驳接收；超时失去本次带回机会'),('M12','e'):(3,'第3轮末原始签名页所在终端断电；提前完成复制才保留原件证据，后期公共副本仍存在'),('M18','backup'):(3,'第3轮末临时备份缓冲被轮换覆盖，提前拷贝可保留地方记录'),('S07','copy'):(5,'第5轮末副本接驳关闭；需先完成送达，主线资格不受影响')}
for board in b['boards']:
 mid=board['id'];board['hard_round_limit']=hard_limits[mid]
 if mid in ['M12','M22']:
  next(e for e in board['enemies'] if e['type']=='sentinel')['cell']=[3,0]
 if mid=='M22':
  rows=[list(row) for row in board['rows']];rows[1][3]='.';board['rows']=[''.join(row) for row in rows]
 if mid=='M19':next(e for e in board['enemies'] if e['type']=='welder')['cell']=[6,1]
 for o in board['objectives']:
  if (mid,o['id']) in [('M17','repair2'),('M21','route')]:o['work']=4
  if (mid,o['id']) in timers:
   o['opportunity_deadline'],o['opportunity_reason']=timers[(mid,o['id'])];o['deadline_rule']='从简报和第1轮即明示。玩家在该轮仍可操作，轮末未secured则lost；已完成复制/交付永久保留。携带但未交付不算完成，不可事后补领奖。该计时不随接近触发，不因难度临时隐改。'
  tags=set(o['interaction_tags'])
  # Evidence and conversations cannot qualify as electrical construction.
  if o['kind']=='work' and o['id'] not in ['e','map','serial','meeting','log','ledger','backup','marker','privacy','archive','photo','chart']:
   tags.add('engineering')
  else:tags.discard('engineering')
  o['interaction_tags']=sorted(tags)
 board['tactical_review']='0.7逐动作推演：目标达成、全员撤离、敌人预告/伤害、火水、增援和占位；详细覆盖范围见outputs/tactical-playability-review.html。'
save('boards.json',b)
a=read('abilities.json')
amend={
 'xu_1':'自身沿直线跨过最多1格X/墙到空的干地；通常不携带伤员；唯一携带例外为从已部署xu_5锚点邻接位置出发。不穿过连续两障碍，落点须可见；仍支付原AP和次数。',
 'xu_5':'邻格设置锚点持续本任务；在锚点邻接位置出发的许舟可用抛索携带稳定伤员，仍付抛索AP与次数。只明确豁免该次携带禁用；其他队员使用已部署绞盘通行，不能凭空获得许舟技能。',
 'jiang_1':'自己携带时可用：向相邻空手、自愿且站立队友交接，自己1AP、接收者0AP；不直接记获救。受handoff相关关系条件约束，不能绕过已知拒绝。',
 'jiang_3':'1AP使用已打包的一份耗材；可从自己或相邻自愿队友位置为施放原点，仍检查原耗材范围、合法目标和数量。医疗药剂实例不要求额外医疗包本体；不生成库存、不免去关系条件。',
 'chen_5':'对明确断电、engineering标签、原需最多2工量的设备完成剩余工作，1AP一次；不能作用于资料、交谈、取证、备份计时或搬运。',
 'su_1':'1AP标记4格内一台机器到下轮开始，下一次基础攻击+1伤害后消费；价值是分担前排AP和远程配合，不宣称总伤害优于两次基础攻击。'}
for x in a:
 if x['id'] in amend:x['effect']=amend[x['id']]
save('abilities.json',a)
eq=read('equipment.json')
for item in eq['items']:
 if item['id']=='scanner':item.update(display_name='远程停机探针',action_ap=1,range=4,uses_per_mission=1,valid_target_tags=['machine_shutdown'],effect='1AP对4格内一处已知停机开关提供1工量，每任务一次；不加速主目标、证据或计时步骤，不叠加L2施工。基础交互仍可完成同样工量；价值是省去走近并分担前排AP。')
save('equipment.json',eq)
for board in b['boards']:board['variant']['selection']='天气安排在免费简报中公开；A/B为场景变体，不再作为付费扫描功能或已验证的重玩卖点。'
save('boards.json',b)
p=read('progression_relationship.json');p['version']='0.7-tactical-review'
for x in p['protocols']:
 if x['id']=='protected_work':x['effect']='双方各1AP提供3工量，执行者获一次机器伤害-2至下轮开始；每人物对每轮一次，不叠加L2施工，不跳前置或专门步骤。';x['baseline']='三次普通交互；未消费L2施工时可用两次普通交互达成3工量，但没有附加护盾。'
p['specialty_relationship_scope']='关系条件同样检查xu_3/su_3的partner_motion和jiang_1的handoff；其他基础行动不受此扩展。没有因为技能按钮换名而默许相同合作。'
save('progression_relationship.json',p)
c=read('combat.json');c['version']='0.7-tactical-review'
c['difficulty']['hard']['deadline_source']='board.hard_round_limit';c['difficulty']['hard'].pop('deadline_bonus',None);c['difficulty_constraints']='放松为标准限时+3且敌伤-1（最低1）；标准保持原限时；最高使用每关明确hard_round_limit，不再统一减1。敌人HP、人格与记忆不变。最高每种主目标与A/B环境均须有基础行动无重伤解法，时间余量仍不等于新手必能发现。';c['movement_stack']='空手基础3、临时+1最多4；搬运基础2，担架/安全搬运/单次协调取最有利办法但最终最多3；接力附带移动固定3，不再叠加。'
c['carrying_exception']='携带时仍可用jiang_1交接、jiang_3实际耗材补给，以及在已部署xu_5锚点邻接出发的xu_1；各自AP、范围、次数、合法落点和相关关系条件全部保留。其余主动专长不开放。'
for x in c['actions']:
 if x['id']=='pickup':x['effect']=x['effect'].split(' 明确例外见carrying_exception')[0]+' 明确例外见carrying_exception：江朔交接/补给与锚点保护的许舟抛索，不得被通用禁用再次覆盖。'
c['geometry']['shutdown_occupancy']='停机机器仍占格，不能把断电当作瞬移清空通路；拆毁后不阻塞。玩家在窄路需花正常移动让出停靠格，搬运者不能在队友脚下结束移动。'
c['geometry']['movement']='Weighted orthogonal movement; may pass through standing allies but not finish on one; no pass through intact enemies, walls or deep water. Carrying rope travel requires the explicit deployed winch or xu_5 plus xu_1 exception, with normal costs and legal endpoints.'
c['turn_order'][4]='apply environmental damage once per actor: electricity and fire take the larger applicable value; insulation removes electricity only'
c['environment_damage_order']='放电水域与火合并为本轮环境危害，同格取较大值；绝缘消去电伤后仍保留火伤。普通机器攻击按各自来源结算；屏障截射线，不挡电火。'
c['optional_deadlines']='带opportunity_deadline的额外目标：该轮玩家阶段有效，轮末未完成则机会失去；与普通伤员稳定期限独立，两者都展示。已lost不能在随后交付恢复为secured。'
save('combat.json',c)
contract={'version':'0.7-tactical-review','formal_development':'paused_by_user','decisions':[
 ['通用携带限制误伤人物核心技能','显式列出江朔交接/补给、锚点许舟抛索三种例外，各自仍付真实代价'],
 ['只检查协议导致个人技能绕过关系边界','给所有合作标签的技能检查同一有向关系与保障条件'],
 ['保护作业在成长后经常无收益','改为2总AP/3工量/一次保护；不叠L2；M17重建与M21重障碍工量4，给合作和工具真实用途'],
 ['大量额外目标可无脑顺带完成','仅4个额外目标增加从简报就可见的机会期限；主线基础期限保留；比较先救人/先取物的真实行动后果'],
 ['远端机器与核心目标互动少','M12/M22守闸机移至(3,0)，M22(3,1)改为通道以免射线被原墙挡住，M19焊接机移至(6,1)，让预告覆盖操作区域；保持基础停机与绕行'],
 ['停机后是否还能穿过机器没有统一','停机仍占格，拆毁才清格；推进搬运前可以主动让路，绝不免费穿越站立队友落脚'],
 ['工程技能可把取证当施工','明确engineering标签；陈砚重设不能生成证据或跳过备份计时'],
 ['扫描仪收费切换A/B却未在基础推演中产生收益','天气简报免费；原scanner槽改为1AP/4格/一次的远程停机探针，真实提供1工量'],
 ['最高难度只减一轮几乎没有选择压力','最高改用逐关明示限时，依据基础行动推演保留至少两轮参考余量；不暗改命中、人格或伤害'],
 ['任务评价忽视居民损失','成功达成最低目标不等于完美救援；结算逐项呈现未救者，M15三选一不播放全楼获救台词']
 ],'scope':'所有36地图的46种目标组合、六敌种动态行动、三难度两环境与不同策略；专长/全装备/协议另有40个受控动作实验。没有声称穷尽全部战斗状态或完成真人测试。','player_points':['救援与停机的先后','可选机会与主目标时间分配','装备缩短路程/工量但占槽或消耗','个人技能把AP交给不同位置的人','关系条件约束具体合作且有独立替代','失败保留已完成事实','人物养成不充当主线钥匙','不同地区/证据形成结局差异']}
save('tactical_review_contract.json',contract)
i=read('integration.json');i['version']='0.7-tactical-review';i['tactical_authority']='tactical_review_contract.json';i['authority']='当前设计0.7：本目录基础定义→system_audit_contract.json的0.6系统规则→tactical_review_contract.json明确修订；正式运行工程未实现这些数据。';i['stacking_rules']=i['stacking_rules'].split('移动预算：')[0]+c['movement_stack']+' 控制同机器后下一轮不能再次控制，永久停机不受临时控制间隔限制。';i['story_verifiers']['chen']['all'][1]['requires_tag']='engineering';save('integration.json',i)
stories=read('stories.json')
for node in stories['personal_nodes']:
 if node['id']=='P_chen_2':
  for choice in node['choices']:
   if choice['creates_contract']:choice['latest_creation_day']=20
stories['audit_rules']['latest_plan']='苏棠最迟D21；陈砚最迟D20（M22只有记录类work，M23没有工程施工）；林岚/许舟/贺鸣D22；叶禾/莫遥/江朔D23。晚读保留专业选择。';save('stories.json',stories)
# Keep the previously normative section from contradicting the new explicit exceptions.
sysc=read('system_audit_contract.json');sysc['superseded_by']='tactical_review_contract.json for the explicitly listed amendments';sysc['sections']['combat_resolution']['carrying_actions']=sysc['sections']['combat_resolution']['carrying_actions'].split(' '+c['carrying_exception'])[0]+' '+c['carrying_exception'];sysc['sections']['story_and_ending']['latest_plan']=stories['audit_rules']['latest_plan'];sysc['sections']['combat_resolution']['tools']=sysc['sections']['combat_resolution']['tools'].replace('不能把人物个人绳索技能也当同例外','许舟xu_5实际锚点与xu_1组合是另一明确例外，其他绳索动作不自动获得豁免');save('system_audit_contract.json',sysc)
print('Applied 0.7 tactical design amendments.')
i=read('integration.json');i['logical_audit_sections']=sysc['sections']
i['stacking_rules']='每次动作只算一次工量/目标完成。L2施工只作用于通用interact，不叠加工具或协议工量。'+c['movement_stack']+' 控制同机器后下一轮不能再次控制，永久停机不受临时控制间隔限制。'
for row in i['resolved_contradictions']:
 if row[0]=='隐藏危险与完整预告':row[1]='天气简报和开战后的危险预告免费公开；原扫描仪改为远程停机探针，付费收益为合法的远程1工量。'
save('integration.json',i)
