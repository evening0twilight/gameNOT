"""Readable0.8 supplement generated from executable design cases, not a UI prototype."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design';O=ROOT/'outputs'
C=json.loads((D/'player_experience_contract.json').read_text());R=json.loads((O/'player-experience-checks.json').read_text())
def e(s):return html.escape(str(s))
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def detail(title,d):return '<details><summary>'+e(title)+'</summary>'+''.join('<p><b>'+e(k)+'</b>：'+e(v)+'</p>' for k,v in d.items())+'</details>'
P=[]
def add(x):P.append(x)
add('<p class="eyebrow">夜潮事务所 · 设计补充0.8 · 2026-11-02</p><h1>玩家能理解，也能有自己的办法</h1><p class="lead">首次引导、人物吸引力，以及情境不同就有不同反应的关系设计。</p><div class="note">本轮直接补入15项首次机制引导、8人的视觉与性格方案、分层情绪评价和防刷取规则。沿用2D与既有36关，正式开发仍暂停。这里给出的是可实施规范与离线案例，不把它冒称已经做完界面、美术或真人游玩验证。</div>')
add('<nav><a href="#help">提示与自由解法</a><a href="#cast">人物第一眼</a><a href="#emotion">情绪怎么变</a><a href="#cases">A/B/C实际推演</a><a href="#loop">长线与反馈</a><a href="#checks">验证与边界</a></nav>')
add('<h2 id="help">提示教会判断，不替玩家指定唯一答案</h2><p>默认轻提示，每次一个短卡，按真正遇到的机制触发。M01分次介绍AP、威胁和救援，营地项目等到晚上再讲。所有提示可跳过、关闭、重看；关闭讲解仍显示目标、危险、费用与不可逆后果。</p>')
add(table(['帮助层','玩家能看到什么','怎样避免强制照做'],[
 ['常驻信息','必需目标、额外机会、AP、敌人预告、当前合作条件','只讲规则与后果，不给每个选择贴正确/错误标签'],
 ['第一次机制短卡','一句机制解释＋“例如可以这样做”','不锁其他合法按钮；用任务事实结束提示，不检查点击顺序'],
 ['主动展开办法','按当前配置列两到三类合法办法及其代价','未学专长、没带工具、未满足关系条件不能显示成可用解法'],
 ['再主动请求动作示例','一条基于当前局面的合法操作，标为“示例之一”','局面变动立即失效重算；未找到只说未找到，不宣判无解'],
 ['重复无效操作','同原因两次无效提交后，高亮“需要帮助？”','不按停留秒数催促，不强弹完整攻略；拒绝后同情境不再打扰']]))
add('<p>M01可用的文案是：“机器会攻击标出的区域。你可以避开、关停、推开或拆掉它；救援不要求清场。”旁边可展开具体办法，而不是让玩家必须先杀一台机器才能关掉教学。实际24组M01难度/环境/策略结果都能满足这种救援事实判定，包括先拆机器和直接处理主目标。</p>')
add(table(['首次位置','机制与触发','给玩家的原文','可走的不同办法','结束/跳过条件'],[[g['first'],g['trigger'],g['copy'],g['alternatives'],g['dismiss']] for g in C['guides']]))
add('<h3>允许逃课的明确边界</h3><p>'+e(C['tutorial_policy']['cheese'])+'</p><p>角色拒绝高级动作时，提示必须同时写出“拒绝的具体动作／原因／可接受保障／独立替代”，不能只给一个红色不可用按钮。保障者确实占位置、付AP，帮助示例不能把这些成本省略。</p><p>提示里的路径、AP、前置、风险查询与实际动作共用规则来源。必要信息用图形加文字，不只靠颜色；阅读暂停回合。教程状态随存档保留，不因重进游戏再次阻断操作。</p>')
add('<p>设计依据：<a href="https://gameaccessibilityguidelines.com/include-contextual-in-game-helpguidancetips/">Game Accessibility Guidelines的情境提示建议</a>强调在实际游玩中逐步解释机制，并允许重复练习。本项目的15个触发点和具体措辞是结合当前关卡制定的方案，不是该来源已验证的数值。</p>')
add('<h2 id="cast">第一眼的吸引力落实到八个具体人</h2><p>沿用2D表现，把你说的“建模”落实为外形与角色表现设计：高质量立绘、表情、姿态、服装轮廓和棋盘辨识度。并不因此改成3D。共同方向是有吸引力的成人群像、克制的半写实插画；年轻人的明快与中年人的成熟都可以成立。</p>')
add(table(['人物','第一眼的吸引方向','轮廓与配色','经历与日常细节'],[[a['name'],a['appeal'],a['visual'],a['story_detail']] for a in C['actors']]))
add('<p>每人先定同一套脸型、身材比例和装备逻辑，再做现场/日常两套服装与8种基础表情。不要把8种表情理解成8张无关新脸，也不把“漂亮”落实成所有人物同龄、同肤质、同一张脸。96px头像、灰度轮廓和并排站位必须仍能分清；战斗中的脸和日常立绘必须是同一个人。</p><p>首轮视觉决策用两种细化风格、相同人物与角度作对照；从中确定表现，再选择生成模型与必要的人工修正。当前尚未生成这些样图，因此没有“这个模型肯定足够好”或“美术已通过”的结论。</p>')
add('<h3>过去可以隐晦，作者不能也不知道真相</h3><p>作者底稿明确“发生过什么、谁选择了什么、谁知道哪些部分”；玩家则从物件、旧称呼、习惯和回避逐步理解，不必在角色卡上贴身份标签。出身艰难、被迫的处境与主动伤害别人要分开，外形好看也不替代责任。</p><p><b>江朔的新增背景底稿：</b>'+e(C['visual_policy']['implicit_example'])+'</p>')
add(table(['玩家接触的层次','可写的内容','实际作用'],[
 ['第一次见面','旧码头的人叫他一个已经不用的称呼，他停顿后把话题转回货物重量','提出疑问，但先让玩家认识他当前的专业能力'],
 ['日常相处','工钱簿划掉货主栏，却完整保留临工姓名；有人想替他扔掉，他拒绝','过去不是全靠苦情独白，物件同时解释他为何在意结算'],
 ['相关任务','他要求先说清货物性质，愿意自己承担多一趟，却不肯让不知情的临工上船','背景进入实际分工和边界，不只是收集一段秘密'],
 ['后续选择','可以公开欠款来源，也可以只交给可信核查者；不要求揭露一切才获得有价值结局','玩家了解事实后仍有隐私与信任选择']]))
add('<p>首次亮相的顺序是外形、说话方式、一次有用的行动；熟悉后出现日常反差，再进入旧事。没有把八个人全部改成“长得好看且悲惨”。好感也可以是欣赏、友谊、依恋或尊重，不预设每条关系都是恋爱。</p>')
add('<h2 id="emotion">同一事件，不同的人可以有不同反应</h2><p>原有旧怨G、活跃记忆R、信任和亲近保留。新补的是它们之前的事件评价，以及旁边的个人负荷和对外表达。不会把“天气×耗时×人数×好感”全部乘进同一个怨气数值。</p>')
add('<div class="flow">发生的事与实际责任 → 角色知道什么 → 如何评价<br>↘ 对具体人的记忆与信任　↘ 个人压力/自责负荷　↘ 当前场合如何表达<br>→ 明示后续合作条件、补救途径和人物反馈</div>')
add(table(['因素','具体生效方式','避免的误判'],[
 ['开始时间','影响明确轮班、出发约定或已发生的疲劳/危险成本时才计入','下午出发不比早上出发天然更惹人生气'],
 ['完成时间','与已接受的期限、剩余风险和实际代价比较；同次迟出发/迟归合并源事件','没承诺过快，就不凭空按超时违约扣信任'],
 ['天气','实际遭遇危险增加压力；隐瞒已知天气风险才对责任人建严重记忆','下雨不等于同伴犯错，未亲历也没得知的情况不影响内心'],
 ['人数与同伴','检查谁分担、谁决定、谁知情、谁见证；不是全队共享一条恩怨','三人遇到同一事故不把每个人的惩罚乘三'],
 ['想给C留下印象','根据B在意C的程度和B的性格，调整表达；真实成功合作可稍增加承认贡献的幅度','只带上C不发信用；当众不争执不等于心里原谅A'],
 ['性格与旧怨','决定先关注哪个问题、疑点有多刺眼、自责强度和表达；既有敏感度仍进入旧记忆曲线','没有因为B讨厌A就把证据改成A确实有责任'],
 ['结果与成本','成功、部分完成、失败；是否超出已同意的代价分别记录','任务成功仍可能违约；没有过错的失败也可保有互信']]))
add('<h3>各类增减走不同规则</h3>')
add(table(['事件类别','写入什么','基本量/上限'],[
 ['已证实违约、不公平、羞辱、隐瞒','有向记忆＋对应实际信任损失，再经过原来的旧怨/压力/重复刺激曲线','基础强度分别12/10/14/18；信任损失8/8/10/12；同源归并'],
 ['有证据的非承诺额外代价','按实际责任形成普通记忆','基础6，信任损失3；不能把正常风险当别人失信'],
 ['成功且真实自愿合作','可靠贡献增加信任，可缓和相关的普通记忆','每事件信用≤3、每方向每任务信用≤3；减怨每事件≤3、每任务≤6'],
 ['表面成功但确实违约','仍按违约处理，同一事件不再发可靠合作信用','不能让成功把已承诺撤离时间洗掉'],
 ['信息含糊、存在疑点','暂时解释/猜疑与对白，不确认为他人过错','每方向每任务≤4；不扣信任、不计入R、不触发拒绝；核实后同源转正式事件'],
 ['本人严格自责','新增个人自责负荷L，与对他人R分开','单事件≤6，单任务≤8；夜间−2，既有恢复项目再−4，真实支持每日最多再−2'],
 ['认责、补救、履约','继续绑定具体旧事，修复实际责任与合作边界','沿用0.6阶段规则，不用一次任务成功替代严重事件和历史修复']]))
add('<p><b>疑点如何落地：</b>B可以想“是不是A又漏了什么”，甚至因C在场更难堪；但界面会标成B尚未核实的看法。证据后来证明队长才是决定者，正式责任写向队长，关闭对A的猜测，不给玩家发一次“制造误会再澄清”的奖励。需要真实误归责事件的手写剧情仍使用原先的纠错规则；不会用随机性格骰子不停冤枉人。</p>')
add('<p><b>成功后的减怨不是宽恕按钮：</b>比如“上次你不肯一起搬重物”的普通不满，可以被这次实际分担缓和；旧事故、严重隐瞒和历史G不受这种泛化奖励影响。人物可以承认A这次做得好，同时仍未原谅过去。</p>')
add('<h3>自责会积累，也有恢复途径，但不是疾病升级条</h3><p>L到40/70分别进入担忧与过载表达，退出阈值为30/55。表现为反复复核、说“我是不是又漏了什么”、请求别人确认，或不再主动接新的额外承诺。不会随机取消基础行动、降低AP，或自动跳到某种临床诊断。已有承诺也不能被新增负荷规则暗中改判失败。</p><p>玩家可以安排已有恢复项目、落实轮班、允许他人承担工作，或在已知事实范围内澄清“这不是你能控制的”。支持不是让完美主义者听一句劝就永久痊愈；相同短谈不能反复刷数值，失败经历也不会一夜消失。若以后要写明确心理疾病的角色线，需要单独进行可信的剧情研究，不能由L满值自动生成。</p>')
add(table(['人物','不同性格的判断重点'],[[a['name'],a['appraisal']] for a in C['actors']]))
add('<h2 id="cases">你提出的A、B、C场景：已运行的对照</h2><p>A/B/C为测试代号，不新增角色，也不预设某对人物恋爱。各例B→A初始怨气40＝历史G30＋普通相关记忆10，信任50，自责负荷0。C在意程度设85；不同人格采用现有人物的设计参数作对照。数值是游戏基线，不是心理学测量。</p>')
labels={'public_restraint_private_concern':'当众克制，私下仍有具体不满','acknowledge_contribution':'承认对方这次贡献','shared_relief':'愿意分享这次合作的宽慰','state_specific_objection':'说明具体异议','tentative_question_not_accusation':'提出未核实的疑问','self_questioning_request_review':'先怀疑自己，请求复核','calm_firm_boundary':'冷静但明确拒绝越界'}
rows=[]
for x in R['examples']:
 d=x['result']['directions'].get('A');rows.append([x['name'],str(d['r_before'])+'→'+str(d['r_after']) if d else '不新增有向怨气',str(d['trust_before'])+'→'+str(d['trust_after']) if d else '不扣他人信任',x['result']['load_delta'],labels.get(d['expression'],d['expression']) if d else '说明客观处境，不指定替罪者'])
add(table(['情境','B→A怨气','信任','自责负荷新增','首要表达'],rows))
add('<p>同样有疑点的失败，较倾向外归因的配置留下1.89的暂时猜疑；严格自责配置为0.978，负荷却更高。两者仍能执行同样的基础行动。A有明确责任时，B的公开克制不打折正式记忆；这就是“内心、场合、事实”分开的作用。</p>')
add('<h3>接回真实关卡：M06的两条完整操作</h3><p>另重跑M06两种完整策略，并为对照明确设定一个玩家自愿接受的“第7轮末前返回”承诺；这不是把原关卡强制限时改成7轮。角色使用林岚、许舟、苏棠，责任来自队长的新决定，不能让执行搬运的队员背锅。</p>')
add(table(['实际操作优先级','完整撤离轮数','伤害','已保住目标','新评价结果'],[[x['style'],x['rounds'],x['damage'],','.join(x['secured']),'队长违约记忆；搬运者不凭空受责' if x['appraisal']['directions'].get('leader',{}).get('confirmed') else '无违约；放弃额外物件不构成失信'] for x in R['tactical_context_cases']]))
add('<p>这证明新评价入口可以接收实际战斗产生的完成时间、代价和贡献，不能把它扩大成全部36关都已跑完新社交层。两条轨迹和承诺前提都保留在本轮结果JSON中。</p>')
add('<h3>可以写出来的对白，而不是只改一根数值条</h3>')
add(table(['场合','对白示例','后续可观察的变化'],[
 ['共同完成，C在场','B：“刚才那一段，A处理得很稳。”稍后：“以前的事我还记着。但这次我看到了。”','承认具体贡献；相关普通不满缓和，旧事故仍保留'],
 ['A确实违约，C在场','B：“先把人送出去。答应的撤离时间，回去我们得说清楚。”','表达克制但违约入账；下一次相关合作会显示具体保障'],
 ['责任未明、较易怀疑同伴','B：“是不是又漏了那张检查单？……先把记录找出来。”','显示待核实解释，不能把这句台词当作A确实违规的证明'],
 ['责任未明、严格自责','B：“如果我再复核一遍，是不是就不会这样？你能和我一起看一次记录吗？”','负荷增加；允许共同复核与分担，而不是强迫玩家哄一个数值'],
 ['证据证明已尽力','B：“我知道那一段已经停电了。我只是还在想，有没有别的办法。”','可以仍然难过或自责，同时承认并不是A的责任']]))
add('<h2 id="loop">长期变化还要进入选择和后果</h2><p>单靠复杂情绪公式无法避免重复。因此用三类变化接到已设计的关卡：目标路线与保留成果；人员组合与真实分工；已知事实、旧怨和已接受义务。不会仅更换一句对白，就宣称是一条新玩法。</p>')
add(table(['关卡','不同经历来源','真实后果'],C['replay_structure']['examples']))
add('<p>八人有56条有向关系，也有56种三人无序组合。实现上不写56条复制的主线：重要历史关系用手写节点，普通任务用事实标签、观察者、关注对象和有限情绪片段组合；每个角色只选一个最相关的在意对象，不把整个队伍全排列后叠乘情绪。</p><p>战斗内仍每任务最多一个长冲突；其余反应简短呈现或汇总到结算日志。剧情不得反复挡住战术操作，旧场景冷却不等于条件清除。新评价在动作提交后处理；如果影响下一次合作，要在下一动作前显示，不能反悔已合法完成的动作。</p>')
add('<h3>结算卡必须解释到这个程度</h3><div class="note"><b>发生了什么：</b>档案带回，但超出了已经接受的撤离承诺。<br><b>B重视什么：</b>他仍在意过去被隐瞒的撤离风险；C在场让他选择先克制表达。<br><b>实际变化：</b>本次违约记忆已记录；不是因下雨扣分，也不是因A受伤扣分。<br><b>下一步：</b>可认领责任、重订带退出条件的安排并实际履行；当前仍可独立搬运与施工。</div>')
add('<p>默认给自然语言与方向变化，详情可看精确数值和事件来源。“可能的心理解释”标明是当事人推测；“确定的AP、时限、拒绝条件与代价”必须在做决定前可知。这使玩家能计划，同时不会把人物全部摊成一道乘法题。</p>')
add('<h2 id="checks">本轮验证与交付边界</h2>')
add(table(['执行内容','结果','不能替代什么'],[
 [str(R['passed_count'])+'项行为与契约检查','全部通过：在意者在场/缺席、成功仍违约、无过错失败、自责差异、核实纠错、去重、每日恢复等','真人是否理解台词、是否觉得人物公平'],
 ['1200个固定种子的组合情境','旧怨、信任、个人负荷、压力均有界；重复同源事件不重复结算','不是1200名玩家，也不是真实人格预测'],
 ['24组M01实际策略结果与教学结束条件','不同难度、天气与四种策略均可按救援事实结束提示','尚未运行真实教程界面，未测新手完成率'],
 ['八人视觉与背景规范','已给到具体轮廓、配色、服装、物件和首次亮相顺序','还没有画像样稿与视觉用户测试'],
 ['现有0.7战术与0.6关系规则','沿用；新评价入口明确去重与替代关系，基础战斗规则未改','未把全部36关重跑成0.8全部社交组合'],
 ['正式运行工程','文件哈希一致，未改脚本、场景或项目配置','并非已经开发完成这些功能']]))
add('<p>后续真人验收的问题现在就固定下来：不看攻略能否找到主目标与撤离；能否说出至少两类处理威胁的办法；关闭提示后能否重开帮助；能否区分“有怨但克制”与“已经和解”；能否从结算卡解释一次变化来源。验收时分别记录误解、误操作与自主解法，不能只看通关率，也不能把按提示点击当作理解。</p>')
add(detail('完整引导规则',C['tutorial_policy']));add(detail('完整情绪评价与结算规则',C['appraisal']))
add('<footer><a href="full-game-design.html">完整设计0.8</a> · <a href="tactical-playability-review.html">0.7逐关战术证据</a> · <a href="player-experience-checks.json">0.8逐项结果与对照输入</a> · <a href="../game/data/final_design/player_experience_contract.json">0.8完整规范数据</a></footer>')
style='''<style>*{box-sizing:border-box}body{margin:0;background:#edf3f1;color:#203e46;font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}main{max-width:1220px;background:white;margin:auto;padding:48px}h1{font-size:38px;line-height:1.35}h2{margin-top:52px;padding-top:18px;border-top:3px solid #087b72;font-size:25px}h3{margin-top:30px}.eyebrow{font-size:13px;color:#5e747a}.lead{font-size:19px}.note,.flow{background:#e8f4ef;padding:20px 24px;border-left:4px solid #087b72;margin:24px 0}.flow{text-align:center;border:1px solid #c2dbd3}a{color:#06796f}nav{display:flex;flex-wrap:wrap;gap:10px 24px;border-block:1px solid #d5e2de;padding:18px 0}table{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0}td,th{vertical-align:top;text-align:left;padding:12px;border-bottom:1px solid #d5e2de;min-width:90px}th{background:#edf4f1}.scroll{overflow:auto}details{border:1px solid #d5e2de;padding:16px;margin:16px 0}summary{font-weight:600;cursor:pointer}footer{margin-top:40px;font-size:14px}@media(max-width:760px){main{padding:23px}h1{font-size:28px}td,th{padding:9px}}@media print{main{padding:0}nav{display:none}}</style>'''
(O/'player-experience-design.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 引导、人物与情境关系设计0.8</title>'+style+'<main>'+'\n'.join(P)+'</main></html>')
fragment='<section id="player-experience"><h2>引导、人物与情境关系 · 0.8</h2><p>2026-11-02：新增15项首次机制引导、8份人物视觉与性格方案。提示可跳过并按目标事实完成，允许合法逃课；情绪分为实际责任、知情评价、有向关系、个人负荷与对外表达。在意者在场不抵消已证实违约，成功只缓和相关普通记忆，自责不等于临床诊断。</p><p>新事件入口调用原记忆曲线并按同源去重；不叠旧任务信用/压力奖励。新增规则已执行'+str(R['passed_count'])+'项检查和1200个组合样本；未声称完成真实教程、人物成品美术或全部36关新社交组合。</p><p><a href="player-experience-design.html">查看具体引导文案、八人外形设计、A/B/C数值与对白对照</a> · <a href="player-experience-checks.json">验证结果</a></p></section>'
(O/'player-experience-section.html').write_text(fragment)
for file,values in [('game/docs/development.json',dict(design_version='0.8-player-experience',latest_review='../../outputs/player-experience-design.html',project_stage='Design only. Contextual guidance, visual briefs and appraisal adapter reviewed; formal implementation remains paused.')),('game/data/product.json',dict(design_version='0.8-player-experience'))]:
 p=ROOT/file;d=json.loads(p.read_text());d.update(values);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'game/docs/logic-audit.json';d=json.loads(p.read_text());d.update(current_revision='0.8-player-experience',player_experience_contract='data/final_design/player_experience_contract.json',player_experience_scope=R['scope']);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Wrote0.8player-experience report and master section.')
