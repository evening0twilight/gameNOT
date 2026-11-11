"""Integrated design audit. Evidence and limits stay beside each conclusion."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
def read(p):return json.loads(p.read_text())
M=read(O/'integrated-party-matrix.json');C=read(O/'integrated-campaign-results.json');V=read(O/'integrated-review-checks.json');K=read(D/'integrated_review_contract.json');B={b['id']:b for b in read(D/'boards.json')['boards']};names={c['id']:c['name'] for c in read(ROOT/'game/data/characters.json')}
def esc(x):return html.escape(str(x))
def tab(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def para(s):return '<p>'+s+'</p>'
P=[]
def add(s):P.append(s)
benefits=sum(m['benefit_cases'] for m in M['maps']);changed=sum(m['benefit_cases']>0 for m in M['maps'])
add('<p class="kicker">夜潮事务所 · 设计复审0.9 · 2026-11-02 · 仅离线设计推演</p><h1>把人物、战斗与整局放在一起检验</h1>')
add('<p class="lead">已修正奖励重复、任务评价重复、搬运刷信用、固定错误提示、名义专长缺乏收益及额外目标结算等问题。基础解法、条件合作与失败后继续能在本次推演中连起来；“玩家一定觉得好玩”和“每关换人都明显不同”仍没有证据支持。</p>')
add('<div class="note"><b>当前判断：</b>保留“三人战术救援＋有事实依据的群像关系”方向。优先靠任务中的分工与代价产生人物经历；不再增加情绪维度、随机误会或新货币。规则闭环有所加强，但本轮不是最终体验验收，也不启动正式开发。</div>')
add('<nav>'+''.join('<a href="#'+k+'">'+v+'</a>' for k,v in [('evidence','证据范围'),('fixes','发现与修订'),('loop','整局回路'),('guidance','提示'),('reaction','人物与防刷'),('parties','阵容反例'),('maps','36关'),('whole','七条战役'),('review','从头复审'),('sources','参考来源')])+'</nav>')
add('<h2 id="evidence">实际执行了什么</h2>')
add(tab(['证据','本轮结果','适用范围'],[
 ['具名阵容完整战斗',f'{M["named_configurations"]}种配置、{M["attempts"]}次策略尝试；保留解法覆盖全部配置','36关/46种主目标选择；按加入时间选人；标准难度、天气A、固定出生槽位。每队比较两种策略、使用/不使用专长。'],
 ['人物差异',f'{benefits}种配置在轮数、伤害或AP上得到改善，分布于{changed}关','自动策略使用一级与三级专长；章节等级只用于同条件比较，不代表这些经验已在战役赚到。不是全部24技能、全部站位与装备排列的穷举。'],
 ['真实战斗接整局',str(len(C['scenarios']))+'条完整24日战役、'+str(C['checks']['actual_battles'])+'场保留战斗','资源、出勤、经验、个人凭据、关系与营地沿同一条时间线结算；包含全12支线、连续失误、故意失约和实际购买训练。'],
 ['防刷与提示边界',str(V['passed_count'])+'项定向断言；276条旧战斗轨迹×3提示模式＝828次调度回放','验证事件来源、去重、复核、实际贡献、关闭提示和状态保存；不是828次真人测试。'],
 ['前轮回归','重新运行原系统、技能、装备、三难度与两天气检查','保留0.6–0.8检查范围；不会把旧的通用角色轨迹冒充本轮全部具名阵容覆盖。'],
 ['正式工程','运行脚本、场景、项目配置哈希未变','没有启动正式开发；没有实际教程界面、手柄/触屏测试、真人体验计时或成品美术验收。']]))
add(para('这些策略会从几个完整尝试中选较好的结果，等于分析者掌握比较结果；真实玩家没有这种先验。因此“找到了可执行解法”不等于新手能找到、不等于关卡难度合适，也不是胜率。技能未被策略选用不证明它没有任何用途。'))
add('<h2 id="fixes">发现的问题已经改到规则和推演入口</h2>')
add(tab(['问题','本轮处理'],K['decisions']))
add(para('额外目标的一个具体修正：M15 的“任意两户”“全部三户”是成果条件，不是可交互的对象。现在按 north/east/west 的真实送达数量识别；S02、S04、S08 的“双目标”同理。同一关即使达到多个额外档，也只领取既定的一份额外物资，不叠两次奖励。'))
add('<h2 id="loop">整局回路：每个结果只有一个负责结算的位置</h2>')
add('<div class="flow">简报中的目标、期限与承诺<br>↓<br>实际阵容、技能和已购买装备 → 合法战斗动作<br>↓<br>完成／送达／损失、实际贡献、知情与责任凭据<br>↓<br>任务资源与经验 ＋ 单一人物评价入口<br>↓<br>营地项目竞争：恢复、训练、事实修复、设施、人物安排<br>↓<br>下一次出勤与合作条件 → 地区、职业、关系分别收束</div>')
add(para('任务账本仍管钱、物资、经验、伤势、出勤和个人线事实；新评价入口统一管情绪与信任，禁止旧账本再发共同贡献+4。任务成功只说明救援结果，不能顺手标记“过去的隐瞒已经被原谅”。训练、恢复和调查需要实际项目与记录；普通查看说明不会消费项目。'))
add(para('角色缺席时不发共同经历。战役中的基本任务没有指定角色钥匙；主角不足时按既有规则借调社区支援员，借调者没有个人专长和人物线收益。最高难度的永久医疗离队不会让已经离开的人在结尾突然继续现场工作。'))
add('<h2 id="guidance">提示：解释当前选择，保留玩家自己的解法</h2>')
add(tab(['情境','最终规则','本轮核验'],[
 ['第一次操作','M01最多3张自动短卡，分轮出现；普通任务最多1张；同轮最多1张。不夺焦点，不代点，不锁其他合法按钮','828次回放符合上限；不是阅读时长或屏幕遮挡测试'],
 ['主动求助','常驻目标、风险和费用；展开帮助才给两三类办法，再主动请求才给“一种合法示例”','内容规则已明确；本轮不声称已有动态建议UI'],
 ['关系受限','按钮旁常显原因和替代办法；只在准备相关合作时提供首次解释，不能因为队内有人怨气高就在开场讲一遍','无相关合作时不插入G07；M19有实际合作拒绝轨迹'],
 ['任务机会期限','提示从当前目标读取名称与轮数，不复制M06“第6轮”的写死句子','M06、M12、M18、S07分别按本关数据核对'],
 ['局面已经变化','未展示的旧提示撤下；主动帮助重新检查合法性，不能推荐已失去的目标或不能使用的技能','失效队列清除断言通过；渲染后的交互仍待正式实现'],
 ['关掉讲解','关闭自动讲解、保留目标预告和主动帮助；必要的不可逆决定确认独立存在','完整24日关闭模式0张自动讲解；仍保留路线确认'],
 ['不可逆决定','同一决定及同一后果状态只确认一次；伤势或风险改变后必须重新确认','保存后不重复同状态确认；改变后果重新确认'],
 ['所谓逃课','允许绕机器、合法跨障碍、分头抢目标、只完成最低目标、放弃支线；不能因比参考解快暗加敌人','检查结果按实际成果判定，不按是否做过教学指定动作']]))
add(para('轻提示与详细模式目前共用自动卡片上限；详细模式的差别应放在展开的信息深度，不靠更多弹窗实现。自动上限只约束讲解，不得藏起危险、费用、期限和拒绝理由。G14公开隐私、营地最终夜等界面触发仍是明确的内容规范，本轮战斗日志回放没有证明这些真实界面已经正确实现。'))
add('<h2 id="reaction">人物反应与防刷：先有事实，再有解释</h2>')
add(tab(['实际情境','应发生什么','禁止的推导'],[
 ['暴雨任务失败，所有人已按已知方案尽力','可疲惫、失落、自责；按个人倾向表达，并支持复核和分担','不能把天气直接变成对队友的违约记忆'],
 ['队长明确要求迟撤，搬运者执行','在已知承诺和提示前提下，责任写向队长；不同人物反应强度与表达可以不同','不能因为最后拿着伤员的是A，就让A替队长背锅'],
 ['B在意C，A这次确实帮了忙','B可以在C面前克制，也能承认A的具体贡献；相关普通不满可缓和','不能以C在场打折已核实的隐瞒或抹掉旧事故'],
 ['严格自责的人面对不可控失败','进入个人负荷与请求复核，不自动指责A；恢复和分担有实际安排','负荷满不等于临床诊断，也不随机抢走基础AP'],
 ['同一任务既有额外损失又核实违约','任务结果的压力/自责只计算一次；后续明确归责进入同源事件记忆','不能每救一个人、每对关系、每个复核步骤都再加一次个人压力'],
 ['受到重伤后康复','身体可恢复；没有责任事实就不生有向怨气。有未修复违约则仍保留','不能把治疗视为道歉，或把恢复等同于失忆'],
 ['达到冲突阈值','沿用分档迟滞、具体合作条件和冷却；基础行动仍在；长冲突每任务最多一次','不能把每次动作都变成争吵，也不能冷却结束就自动和解']]))
add('<h3>实际运行的反刷例子</h3>')
add(tab(['尝试','结果'],[
 ['把同一关结算改一个外部事件编号，再提交','关卡根凭据已结算，第二次不改变信任、记忆或个人负荷'],
 ['让三人轮流拿一下物资','单纯拾起、传手不算可靠贡献；需要救治、有效施工或最终送达路径上实际运输'],
 ['先搬出去再搬回来，让新搬运者占功','最终路径消去来回闭环；空转不产生额外贡献。合理避险绕行仍可计入'],
 ['目标已经完成，再补一个加速或标记技能','不把完成后的动作追认成贡献'],
 ['反复制造疑点、澄清误会','未核实猜疑没有先扣正式信任；澄清不给正奖励，重复提交无收益'],
 ['先制造一次伤害，再道歉补救，再正常合作','与“没有制造伤害，但完成同样合作”对照，制造伤害路线不能获得更高净信任'],
 ['造成损失的决定与补回损失改写成两个故事','同一因果来源不发新可靠贡献信用；新的真实合作仍然允许'],
 ['读档重新领评价、重放同一夜间恢复','参考状态序列化保留凭据与提示记录；同一夜晚不能再消费一次恢复结果']]))
for e in V['examples']:add('<details><summary>'+esc(e['case'])+'</summary><pre>'+esc(json.dumps(e,ensure_ascii=False,indent=2))+'</pre></details>')
add(para('贡献防刷不是要求每次救援都走数学最短路。新规则保留实际路径中的合理绕行；让另一人真实承担一段运输，本来就是合作，允许获得有限信用。每方向每任务最多+3，且同一任务不可重复领奖。修复只能返还该事件实际损失；如果误归责后来被证伪，恢复到本应有的水平是纠错，不是额外刷奖。'))
add(para('这里仍有范围边界：参考状态的JSON往返测试不是正式存档系统验收；本轮不是对玩家能想到的所有欺骗行为的完备证明。历史修复与96个剧情节点已有规范和前轮检查，但七条战役没有穷举每条历史关系修复分支。'))
add('<h2 id="parties">换人究竟改变了什么</h2>')
add(tab(['完整关卡对照','基础办法','专长/约定办法','实际体验差别'],[
 ['M23 林岚／许舟／苏棠，同等级同目标','8轮，33AP，0伤害','7轮，31AP，0伤害','林岚的救治与赶赴位置改变分工，把人力留给后续搬运'],
 ['S09 林岚／许舟／莫遥，同等级同目标','4轮，18AP，0伤害','3轮，18AP，0伤害','莫遥从远处分担停机工作；AP总量相同，但时间安排不同'],
 ['M19 许舟对队长处于条件合作档','拒绝一次相关协作，7轮、31AP，仍成功','有本次明确约定，6轮、30AP，仍成功','关系影响动作可接受条件，不要求先把怨气清零'],
 ['M23 同一强不满情境的反例','不启用受限协作：8轮、35AP','明确约定后策略用协作：8轮、40AP','合作不是自动优解；这种移动安排多花AP，允许不用，不奖励按钮使用次数'],
 ['M22 贺鸣保护别人主导（前轮全程凭据）','可以不带贺鸣，照样完成终端交接','合法站位与护盾实际拦截，生成保护者凭据','改变的是承担风险和个人证据，不是“贺鸣在场”一句对白']]))
comparison=[]
for mid,parties in [('M23',[['lin','xu','su'],['chen','ye','mo'],['xu','he','jiang']]),('S09',[['lin','xu','su'],['lin','xu','mo']])]:
 for party in parties:
  x=next(x for x in M['cases'] if x['mission']==mid and x['party']==party)
  comparison.append([mid,'／'.join(names[a] for a in party),str(x['rounds'])+'轮 / '+str(x['ap'])+'AP / '+str(x['damage'])+'伤害',','.join(x['skill_action_types']) or ('贺鸣搬运被动' if x['skills_enabled'] and 'he' in party else '通用行动')])
add(tab(['同关同目标','不同阵容','实际结果','选中策略中的专长'],comparison))
add(para('以上才是直接换人的结果。M23可以靠林岚缩短前期救治走位，也可以靠贺鸣搬运被动减少运输动作；施工与停机队完成救援同样合法。S09换入莫遥后总AP未减少，但远程分工提前一轮结束。这些比较固定出生槽位，未穷举换位；同阵容开关专长的对照用于进一步排除“只因换位”的解释。'))
add(para(f'必须保留的负面结果：{36-changed}关在本次主目标与自动策略范围内，没有得到专长改善的比较记录。M17、M21、M22尤其不能据此宣传“换阵容就像换游戏”。M17的两条路线与M20的不同目标形成不同结果，但路线差异也不能偷换成阵容差异。'))
add(para('本次直接改了莫遥的一级专长：原来先标记、再让别人施工加2，遇到只有1—2工量的开关常常没有收益；现在是4格内直接给已知停机开关1工量，每任务2次，不能用于主目标、资料或持续计时。普通交互仍能完成相同工作。调整后有指标改善的具名配置由历史同条件记录的171种增加到197种；这个变化不等于197种独特玩法。'))
add(para('弱差异关卡的设计处理是明确其职责：开局几关教通用规则；M17承担路线取舍；M21承担资源与现场目标取舍；M22承担保护、证据与隐私。不会为了每关都刷出角色优势而人为塞“必须带某人”的门锁。战术高峰要集中在需要分头、赶期限、保护与搬运交错的关卡。若定位改成硬核组队构筑游戏，目前证据不足以支持这种宣传。'))
add('<h2 id="maps">36关回填：解法、差异与反馈重点</h2>')
rows=[]
for x in M['maps']:
 b=B[x['mission']];focus='实际专长改变效率；奖励只认真实贡献' if x['benefit_cases'] else '本次主目标策略未见专长改善；不可用对白冒充'
 if b['id'] in ['M01','M02','M04']:focus+='；首次机制解释可跳过'
 if any(o.get('opportunity_deadline') for o in b['objectives']):focus+='；机会时限绑定本关数据'
 if b['id']=='M15':focus+='；救两户/三户额外奖按真实对象判断'
 if b['id']=='M17':focus+='；互斥路线提交前确认'
 if b['id']=='M22':focus+='；交接成功不等于隐私处理完成'
 if b['id']=='M24':focus+='；地区、职业、关系分别结算'
 rows.append([b['id']+' '+b['title'],str(x['solved'])+'/'+str(x['configurations']),str(x['benefit_cases']),b['decision'],focus])
add(tab(['关卡','具名配置找到解法','专长改善配置数','主要玩家选择','复审处理'],rows))
add(para('每关的坐标、敌人预告、物件、期限、前置和具体结局凭据仍在完整设计中。本表不把关卡只有一个自动策略结果解释为关卡只有一种解法；也不把自动策略未找到的个人路线当作玩家不可能做到。'))
add('<h2 id="whole">七条整局：不是每场结算后把人物清零</h2>')
rows=[]
for s in C['scenarios']:
 q=s['summary'];auto=sum(x['kind']=='nonmodal_card' for x in s['guidance']);conf=sum(x['kind']=='decision_confirmation' for x in s['guidance'])
 rows.append([q['name'],str(q['main_count'])+'主/'+str(q['side_count'])+'支',q['resources'],len(q['withdrawn']),len(q['verified_contracts']),str(auto)+'讲解/'+str(conf)+'确认',sum(b.get('protocol_actions',0) for b in s['battles'])])
add(tab(['轨迹','实际任务','结束资金/物资/零件','永久医疗离队','已验证个人承诺','提示次数','实际保护作业'],rows))
add(para('七条轨迹均到达结局。最高难度连续失误轨迹中，四人永久医疗离队、若干个人承诺未完成，但可用支援人员继续；后续修复地区仍可能让世界路线达到共同接管。世界状况修复不洗掉离队、失约与关系后记。这符合“仍能继续，但失去机会和部分好结果”，不等于失败完全没有代价。'))
add(para('反复失约轨迹故意在原本能满足的自愿撤离承诺上拖延，再尝试完成救援；这是对抗性设计情境，不是预测真实玩家会这样玩。三位常驻人物对队长留下严重负担和未修复后记，任务成功没有将其抵消。具体合作是否真的被尝试，仍取决于战术需要；不能把进入关系档位次数当成实际拒绝次数。'))
invest=C['scenarios'][-1];q=invest['summary']
add(para('另加实际投资轨迹：先用真实营地项目与物资训练林岚／苏棠的保护作业，再到开放日期购买远程停机探针与担架，争取额外目标；不是给测试角色凭空配满工具。实际训练协议：'+esc(q['trained_protocols'])+'；工具：'+esc(q['tools'])+'；保护作业执行'+str(sum(b.get('protocol_actions',0) for b in invest['battles']))+'次。装备不会叠加违反上限的移动能力。这条轨迹明确优先争取额外成果和一次真实合作经历，增加了主动靠近搭档的候选动作；靠近也支付AP。它不是最低AP的最优经济策略。'))
add(para('经济判断要直说：当前主线资源比较宽裕，几个基础策略即使不买新工具也能结束战役；现金不是生存压力核心。购买与训练路径说明投入确实能进入战斗，但一条轨迹中只有一次保护作业，不能据此称高级合作已经成为普遍有吸引力的养成目标。装备的用途应是提高效率、争取更多成果和改变分工，项目数、人员状态与任务时间才是主要约束。本轮保留这个取向，不通过突然增加房租或强制耗材把玩家逼进购买。没有证据支持“每一笔钱都很纠结”的宣传。'))
add('<h2 id="review">从玩家、产品与制作角度重新评审</h2>')
add(tab(['角度','判断','具体落地决定或证据'],[
 ['核心吸引','成立为清楚的产品方向，吸引强度尚未验证','玩家带着有旧事的人救人，亲眼看到分工、代价和责任；人物魅力与这些行为相连，不靠情绪公式长度卖点。'],
 ['目标用户与承诺','适合有意愿阅读、做战术取舍、关心角色的单机玩家；仍是待验证假设','不把动作爽感、无限沙盒和硬核构筑一并承诺。本轮不是新的市场规模、获客成本或付费意愿调查。'],
 ['一回合的可读性','规则明确；真实屏幕尚未验收','始终显示AP、目标前置、危险、期限；陌生概念渐进；主界面不同时摆八根情绪数值条。'],
 ['选择的意义','存在行动分配、目标取舍和个人事实差异；分布不均','M23、S09与M19有实际对照；弱差异关卡明确承担教学/路线/证据职责，不加角色门锁。'],
 ['支配策略与必选阵容','本次1432配置均找到基本办法，未发现通关必带角色','不等于已证明所有目标下没有最强队；固定出生位、两策略、有限技能选择可能遗漏构筑。'],
 ['角色公平与能动性','事实、猜测、克制、自责分开；基础控制权保留','合理反对发生在相关合作，非随机关机。队长决策不默认归罪执行者。'],
 ['养成与关系连接','经验改善选择，互信开放可选合作，凭据决定个人收束','投资轨迹支付真实训练成本；不能用参加一场就满足“曾保护过同伴”。'],
 ['经济与失败恢复','可继续且损失可保留，现金紧张度偏低','基本照护保底；真实离队、额外成果与个人承诺分别结算。保留宽裕设计，不虚称生存经营。'],
 ['防刷与系统复杂度','本轮堵住明确奖励漏洞；不追求模拟所有现实心理','根事件结算、贡献凭据、同源补救无净利、去重；只计算与当前处境相关因素。'],
 ['节奏与重复','有任务职责、路线与阵容差异；时长和新鲜感尚未实测','不靠重复刷关系、强制迟缓动画凑12—16小时；反复提示与冲突限频，低频重要变化集中结算。'],
 ['人物形象与叙事可信度','八人已有视觉、背景、性格规范；没有成品美术吸引力证据','继续2D立绘＋棋盘表现；衣着、装备、姿态说明职业和历史。灰色背景可通过物件与反应暗示，但关键责任事实必须可核实。'],
 ['内容规模与两人制作','2D固定规则与有限素材复用仍相对可控；不是工期已验证','不引入运行时AI、联机或大型3D。56种三人队伍不写56套主线，关键历史手写，普通反应组合且保持来源。'],
 ['存档与一致性','参考状态能保存去重凭据；正式适配尚未实施','存档要保留根事件、已消费奖励、提示状态、已接受承诺与因果修复；不能读档重置负面状态或刷新同源奖励。'],
 ['可访问性与交互设备','文字、图标和高亮并用的规范已确定','不只靠颜色；文字放大、可回看、可跳过。未实测字号、对比度、焦点、键盘/手柄操作，因此不盖“无障碍通过”章。'],
 ['结局与叙事一致性','世界、职业、关系分层能保留多种结果','地区修复≠原谅队长；医疗离队≠失去叙事后记；已经保住的伤员不会因后续任务失败被抹掉。']]))
add('<div class="note warn"><b>不把“纸面更完整”说成“最终体验已过关”。</b>现在有可复查的规则与完整参考行动证据，能排除本轮明确复现的矛盾。仍需要真人观察才能判断提示是否打断思考、人物是否讨喜、低差异关是否无聊、总时长是否合适；这几项不能用再跑一万次数值测试替代。本轮保持设计阶段，不以此作为启动正式开发的批准。</div>')
add(para('后续体验验收标准固定为：玩家能自己说出当前目标和退出办法；能提出两个可行方向；能解释一条关系变化的来源；受限合作时知道基础办法仍可用；能说出两套阵容至少一处实际分工变化。记录误解、误操作、自主解法和不愿继续的时点，而不是只问“觉得好不好玩”。这是一套待执行的验收协议，不伪装成已经收集的反馈。'))
add('<h2 id="sources">参考来源如何转化为这次评审</h2>')
for s in K['sources']:add('<p><a href="'+s['url']+'">'+esc(s['title'])+'</a>：'+esc(s['use'])+'</p>')
add(para('上面是原论文、开发者复盘与官方指南。本报告的卡片数量、信任上限、角色技能和现金取向是本项目的设计选择，不是这些来源替我们证明的最佳值；也没有把复盘里的成功直接当成我们的商业胜算。当前技能目录中没有可代替真人游戏测试的工具，本轮使用现有离线推演和反例检查。'))
add('<footer><a href="full-game-design.html">完整设计0.9</a> · <a href="integrated-party-matrix.json">1432配置与保留轨迹</a> · <a href="integrated-campaign-results.json">七条战役账本</a> · <a href="integrated-review-checks.json">定向检查</a> · <a href="tactical-playability-review.html">0.7装备/难度战术证据</a> · <a href="player-experience-design.html">0.8八人视觉与情境评价</a> · <a href="../game/data/final_design/integrated_review_contract.json">当前修订规范</a></footer>')
style='''<style>*{box-sizing:border-box}body{margin:0;background:#edf2ef;color:#213b43;font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}main{max-width:1240px;margin:auto;padding:45px;background:#fff}h1{font-size:36px;line-height:1.35;max-width:920px}h2{margin-top:50px;padding-top:18px;border-top:3px solid #078075;font-size:25px}h3{margin-top:30px}.kicker,footer{color:#526e74;font-size:13px}.lead{font-size:19px}.note{padding:20px 24px;background:#e9f5ef;border-left:4px solid #078075;margin:24px 0}.warn{background:#fff4de;border-color:#b67925}.flow{text-align:center;padding:22px;background:#edf5f3;border:1px solid #c8ded6}a{color:#00766e}nav{display:flex;flex-wrap:wrap;gap:10px 22px;border-block:1px solid #d7e1dd;padding:16px 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}th,td{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid #d7e1dd;min-width:95px}th{background:#edf4f1}details{padding:15px;border:1px solid #d7e1dd;margin:15px 0}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}footer{margin-top:40px}@media(max-width:760px){main{padding:22px}h1{font-size:28px}}@media print{main{padding:0}nav{display:none}}</style>'''
(O/'integrated-design-review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 36关整合与全局复审0.9</title>'+style+'<main>'+'\n'.join(P)+'</main></html>')
fragment=f'''<section id="integrated-review"><h2>36关整合与全局复审 · 0.9</h2><p>2026-11-02：当前修订覆盖单一人物结算、真实贡献防刷、提示来源与次数、额外成果标签，以及莫遥的远程停机分工。以下0.6–0.8章节保留各自证据范围，冲突处以0.9修订规范为准。</p><p>本轮1432具名配置、5728次尝试均有基本解法；{benefits}种配置在12关出现专长效率改善。另有{len(C['scenarios'])}条完整战役、{V['passed_count']}项定向检查和828次提示回放。换人不只是对白，但仍有24关在本次主目标策略下没有专长改善记录；不能宣称每关都有深阵容差异。</p><p>保留2D单机救援与群像方向，继续设计阶段。自动测试不是真人可玩性、最终时长、美术吸引力或商业可行性验收。</p><p><a href="integrated-design-review.html">查看逐关结果、漏洞修复、反例与十五角度复审</a> · <a href="integrated-campaign-results.json">完整战役结果</a></p></section>'''
(O/'integrated-review-section.html').write_text(fragment)
for file,values in [('game/docs/development.json',dict(date='2026-11-02',design_version='0.9-integrated-review',latest_review='../../outputs/integrated-design-review.html',project_stage='Design only. Named-party tactics, social rewards, guidance scheduling and complete campaigns reviewed offline; formal development remains paused.')),('game/data/product.json',dict(design_version='0.9-integrated-review'))]:
 p=ROOT/file;d=read(p);d.update(values);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'game/docs/logic-audit.json';d=read(p);d.update(current_revision='0.9-integrated-review',integrated_review_contract='data/final_design/integrated_review_contract.json',integrated_review_scope=K['scope']);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Wrote0.9 integrated review,36map table and master section.')
