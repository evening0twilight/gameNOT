from pathlib import Path
import json,html,collections,hashlib,re
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
def load(n):return json.loads((O/n).read_text())
def esc(v):return html.escape(str(v))
def table(h,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(v)+'</th>' for v in h)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>'
V=load('full-audit-checks.json');M=load('full-audit-matrix.json');C=load('full-audit-campaigns.json');SUB=load('full-audit-subsystems.json');SYS=load('system-audit-results.json');EXP=load('player-experience-checks.json');ST=load('story-contract-checks.json')
assert all(x['exit_code']==0 for x in SUB) and all(x['success'] for x in M['named']+M['baseline'])
findings=[
 dict(id='F01',kind='设计价值漏洞',title='工坊II扩容没有实际收益',before='删减后只剩医疗药剂一种耗材，单品上限2；总容量3升4仍最多带2份。',after='工坊II改为药剂单品2→3、急救包次数2→3，总容量维持3；每份仍付1物资，每次治疗仍1AP。',proof='两级升级实际扣95资金/12零件；3份药剂扣3物资。3次治疗可执行，第四次拒绝；失败后只退未用药剂。',status='已修正规则和参考模型'),
 dict(id='F02',kind='参考模型错误',title='绞盘部署后锚点被清空',before='为五级个人抛索临时加入锚点的清理代码，误用于全部工具动作；真实winch部署也被还原。',after='仅清理个人抛索临时锚点；实际部署锚点保留整个任务。',proof='先花2AP部署，下一轮三级许舟携带跨越成功；锚点仍保留；非法跨越不残留临时锚点。',status='已修正并重现前后差异'),
 dict(id='F03',kind='参考模型错误',title='医疗上限与高等级HP脱节，也能错误治疗已离场者',before='基础治疗按10HP截断；四/六级最大HP已是11/12。江朔补给还漏查接收者是否离场。',after='按接收者当前最大HP恢复；满血、失能、离场均不可治疗；合法治疗扣真实药剂/AP。',proof='1/4/5/6级上限测试、满血与离场拒绝测试；拒绝不扣物品、不产生贡献。',status='已修正并重现前后差异'),
 dict(id='F04',kind='参考模型与规则边界',title='装备绑定不完整，动作入口依赖调用者代查条件',before='部分工具只通过策略路径使用，没有统一绑定到实际持有者；新能力入口缺少统一拒绝回滚和实际关系复核。',after='七种现役装备统一绑定；同人同槽冲突拒绝。直接命令核对角色/目标、获得等级、具体关系条件；失败整体恢复状态。',proof='16专长＋7装备全部逐项执行；错误索引、占槽冲突、具体关系拒绝与明确同意、非法抛索均有断言。',status='已补齐当前参考入口'),
 dict(id='F05',kind='文档矛盾',title='携带跨越、技能次数和合作门槛仍残留旧版说法',before='部分规则仍要求已删除的xu_5锚点；另有60信任通用门槛、第一专长一律2次，以及仍要求配置专长的旧引导。苏棠AP上限文字也未区分接收前后。',after='携带例外统一读取combat.carrying_exception；无统一信任门槛；次数按各技能定义；两项专长固定，营地切换L2倾向；接收前AP≤2、接收后≤3。',proof='领域权威清单统一；当前说明副本同步，历史条目保持retired，不重新激活。',status='已同步当前规范'),
 dict(id='F06',kind='设计入口空缺',title='说可以重新协商，却没有可执行流程',before='约定可选共同计划/专业距离，但已读节点不能再次进入；没有重新协商入口与消耗定义。',after='营地关系页重新协商占1短谈，同一对每日最多改一次；相同选择不消费。不能清记忆、返成本或重置带教章节次数，D24不再补谈。',proof='改约、同日反复切换、次日重选、已用带教次数和终局截止的回归通过。',status='已补齐流程和参考动作'),
 dict(id='F07',kind='归责错误',title='无关第三人的违约牵连这对角色',before='合作资格排除了任务中出现任何违约的整场任务，导致A/B的真实合作被C/D纠纷抹掉。',after='只排除涉及这两人的已记录违约。缺少责任元数据的旧记录保守处理；同队仍不等于合作，资格本身不发信任。',proof='无关第三人违约保留两次合作；涉及本人则该次资格失效。',status='已修正'),
 dict(id='F08',kind='状态规格空缺',title='新增关系与战术状态没有统一进入保存清单',before='旧清单没有明确带教次数、改约日、接应安排、AP转交标记、危险输出隔离等。社交状态和营地投影的恢复顺序也未明确。',after='补充逐域状态清单；情绪事件以社交状态为权威，加载后同步营地投影，不重新发奖励；规则版本不匹配须迁移校验。',proof='参考状态做JSON往返，锚点、AP转交限制、带教/接应、事件去重、关系阶段和教程已读状态保持。正式存档仍未实现。',status='规格与离线状态样本已补齐'),
 dict(id='F09',kind='内容容量说明空缺',title='未明确一周目能否看完所有营地短谈',before='23晚×2段＝46窗口；24个人节点＋12关系节点＋18生活短谈共54段，还要容纳认责与改约。',after='核心36段可排入；生活短谈与修复选择共享剩余窗口，不要求一周目全看、不因未读扣好感或锁全部人物结局。日志不伪造未发生的共同经历。',proof='逐人三段窗口、96节点ID和既有49项承诺/结局检查；明确容量上限，未将54段同时可看作为承诺。',status='已澄清最终规则')]
findings.append(dict(id='F10',kind='出发流程空缺',title='未定义接应草案取消和换队后的处理',before='只有选择接应和出发扣费，没有明确返回免费出口或换队后清除失效草案的流程。',after='出发前选择/取消均免费；换队或人员不可用时撤销失效草案，显示普通出口并重新确认出发预览。已经出发才锁定。',proof='选择后取消、改为无对应人物的阵容、出勤者疲劳超限均正确清草案且不扣资源；deploy仍重新验证并只扣一次。',status='已补齐流程与参考动作'))
(O/'full-audit-findings.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2)+'\n')
domains=[
 ['关卡与分支','36关的目标引用、依赖环、坐标、出口、期限、M17/M24选择','全部结构检查通过；276个难度/环境/目标情境均有基线路线','不是所有行动序列的无死局证明'],
 ['战斗与装备','16现役专长、7现役装备、实际持有、AP、次数、医药、锚点与拒绝回滚','修正F02–F04；23种动作均有受控执行例','动作能执行不等于经常值得选择'],
 ['成长与经济','等级HP、训练封顶、带教、物资转库存、消费/退还、设施投资','修正工坊无效升级和治疗上限；没有新增付费通关门槛','资金选择压力、各等级收益还未获真人证据'],
 ['情绪与归责','记忆满值、归档、重复事故、修复、知情、自责、冷却、第三人观感','重跑既有情绪/体验检查，修正F07','数学模型是角色反应设计，不是心理学诊断'],
 ['共同约定','合作历史资格、专业距离、带教章节次数、改约、接应费用','补齐F06/F08；不能通过切换或修复循环刷次数','带教是成长安排，不承诺高额战斗收益'],
 ['整局与失败','招募、疲劳、项目、支线、重伤、永久医疗离队、终战失利','4条真实任务衔接到结局；另测全8人不可用的借调账本路径','全员离队测试是极端账本状态，不伪称玩家实测'],
 ['故事与结局','8人三段、个人履约、后续背约、缺席与职业选择、世界结局','49项承诺/结局检查通过；F09澄清短谈容量','96节点不等于96段完成的文学脚本'],
 ['引导与信息','提示额度、关闭/延后、失效提示、可用解法、不可逆确认','73项体验规则检查与1200上下文样本重跑通过','未运行真正的游戏界面或新手试玩'],
 ['存档与事务','新状态完整性、重复结算、退出重进、防刷新、恢复权威','192项当前检查包含拒绝回滚与JSON往返样本','生产存档格式、磁盘故障与迁移实现仍待开发'],
 ['制作与表现','2D战斗形式、8角色/6机器/16专长/7装备范围与资产职责','范围维持，未为了补洞重新扩张成3D/实时战斗','美术一致性、动作反馈和完整文案尚未验收']]
parts=[]
def add(s):parts.append(s)
add('<section id="full-audit"><p class="kicker">0.14 · 全域设计审查 · 2026-11-02 · 未进入正式开发</p><h2>全量检查结论：发现了缺口，不能把通关当作设计完成</h2><div class="note"><b>本轮处理10类问题：</b>无效投资、参考模型错误、旧规则冲突、约定入口、归责范围、存档状态和叙事容量。能明确修正的已写回当前规范与离线模型。当前可确认全部36关仍有已采样可行路线，不能确认所有玩家都会愿意培养、换队和重玩。</div>')
add('<p>审查对象为当前单机、俯视2D、8×8空间战术救援方案。三人出勤、六种机器、八个人物、24主线＋12支线保持不变。本次不做正式游戏实现，也不以尚未写界面/美术/正式存档本身充当“设计逻辑错误”。发行另行讨论。</p>')
add('<nav><a href="#issues">已发现与修正</a><a href="#domains">全域覆盖</a><a href="#examples">具体反例</a><a href="#runs">整局与关卡</a><a href="#gaps">仍未证实</a><a href="#authority">当前权威与证据</a></nav>')
add('<h3 id="issues">发现的问题与处理结果</h3>')
add(table(['编号/类别','问题','当前修正','验证及边界'],[[x['id']+'<br>'+x['kind'],esc(x['title'])+'<p>'+esc(x['before'])+'</p>',esc(x['after']),esc(x['proof'])] for x in findings]))
add('<h3 id="domains">逐域检查，而非只检查怨气</h3>'+table(['领域','检查内容','结果','不能据此推导'],domains))
add('<h3 id="examples">几个能明确复现的案例</h3>')
add('<p><b>投入有花费、却没有收益：</b>旧工坊II把总容量3改4，但只有药剂一种且单品最多2。玩家花60资金和8零件，能带的药剂仍是2。现在工坊II允许带3份并把急救包上限提高至3次；每份仍真实制作，不能只把上限改成3却忘了工具只能用2次。测试实际支付两级费用95资金/12零件、制作3份药剂；使用两份后失败，只退剩余一份。这个案例验证效果和收支，不证明所有玩家都应该购买工坊II。</p>')
add('<p><b>成长以后反而无法补满血：</b>六级角色最大12HP，受伤剩10HP，旧医疗判断却认为已经满血。现在恢复以接收者的11/12HP上限计算，且完整检查其是否已离场、失能或真的受伤。不能用治疗复活角色、重置行动，不能在拒绝后还扣药剂。</p>')
add('<p><b>真实装备被临时技能的清理代码误删：</b>三级许舟先花2AP部署锚点，下一轮才有AP携带跨越。旧模型在工具动作结束时恢复了“部署前锚点集合”，导致装备失效；旧路线测试没有主动使用它，所以没暴露。现在永久部署与五级个人跨越所需的临时状态分开处理，并加入了先部署、后跨越、保存后仍存在的测试。</p>')
add('<p><b>第三人的过错不应清掉两人的合作：</b>A/B在两次任务中各自有真实目标贡献，C在其中一场对D违约。过去整场任务作废，A/B失去共同安排资格；现在只在已知责任涉及A/B时排除那次经历。共同资格只表示可以安排合作，不直接发信任，也不能靠往返交接获得。</p>')
add('<p><b>重新协商不能变成洗状态：</b>本章已经带教，玩家改为专业距离，次日再约定合作，原带教使用记录仍在。改约占短谈，不清旧怨、不退之前付出的成本；同一天反复切换和重复点击当前选择不会再给收益。第24日没有临时补出一个营地。</p>')
add('<h3 id="runs">本次实际重新执行的验证</h3>')
add(table(['验证','数量与结果','说明'],[
 ['当前动作、边界、结构、账本与状态检查',str(V['passed'])+'项通过','其中覆盖全部16专长与7装备；夹具不冒充完整任务。'],
 ['旧有向记忆/归责/冷却回归',str(SYS['passed_count'])+'项通过','复用未改动的情绪模块；不能把其中历史经济夹具当作0.14全部经济验证。'],
 ['人物评价与引导规则回归',str(EXP['passed_count'])+'项通过；'+str(EXP['property_sample_count'])+'个上下文样本','没有真实屏幕操作或真人行为数据。'],
 ['人物履约与结局',str(ST['passed_count'])+'项通过','验证真实凭据、后续违约与结局优先级。'],
 ['日期合法阵容/目标旧路线重放','1432/1432保留可行结果','受控三级，重放上一轮较好路线，不声称全部是自然成长时已取得。'],
 ['所有目标选择×三难度×两环境','276/276有基础路线；共试算552条路线','初始三人、一级、无专长装备；所有采样结果无人失能。'],
 ['完整战役','4条、'+str(C['actual_battles'])+'次实际任务衔接，均到达结局','使用真实经验、疲劳、物资、招募与人物事实，不免费发等级。']]))
add('<p>上述断言之间可能覆盖同一条规则，因此不相加宣传成独立问题数量。此次矩阵共1984条路线试算；1432条重放的回合与伤害结果和旧记录一致。证明修正没有破坏这些已知解法，不证明不存在其他死局、更好的普通解法或最强效率阵容。</p>')
add(table(['完整路线','主/支线','任务成功','结局','永久医疗离队','末尾资金/物资/零件'],[[esc(s['summary']['name']),str(s['summary']['main_count'])+'/'+str(s['summary']['side_count']),str(sum(b['success'] for b in s['battles']))+'/'+str(len(s['battles'])),{'shared_control':'共同监管','distributed_rebuild':'分布重建','evacuation':'撤离'}[s['summary']['world_ending']],'、'.join(s['summary']['withdrawn']) or '无',' / '.join(str(s['summary']['resources'][k]) for k in ['credits','supplies','parts'])] for s in C['scenarios']]))
add('<p>“所有8人均不可用”的额外极端账本测试也能沿借调规则完成24次主线并进入撤离结局；它用指定失败结果检验经济与人员兜底，没有冒充24场全员失能的实际战斗录像。标准模式仍没有永久失去主要角色，最高难度的遗留失能才进入永久医疗离队边界。</p>')
add('<details><summary>36关逐关覆盖结果</summary>'+table(['关卡','命名阵容/目标重放','难度/环境/目标情境','是否均成功'],[[mid,sum(x['mission']==mid for x in M['named']),sum(x['mission']==mid for x in M['baseline']),'是' if all(x['success'] for x in M['named']+M['baseline'] if x['mission']==mid) else '否'] for mid in dict.fromkeys(x['mission'] for x in M['named'])])+'</details>')
add('<h3 id="gaps">还存在的空缺：分清设计、证据与制作</h3>')
add(table(['类型','当前缺口','本轮确定的处理','完成判断'],[
 ['吸引力证据','五级收益集中于搜索器使用充分的苏棠；部分角色只有合法操作证明，缺少充分机会价值证据。','保留当前专业分工与普通解法，不为制造优势而增加职业门锁；报告不再宣称人物培养已平衡。','比较同一目标下更好的普通路线、实际培养成本和玩家的选择原因；不是再多跑一遍相同策略。'],
 ['经济体验','当前成功路线资源较富余。','经济定位为可选投资与失败缓冲，不宣传生存匮乏；修复工坊无效投资，不直接砍基础收入逼人买装备。','玩家是否理解投资用途、是否有愿意放弃的其他安排；存钱本身不能算玩法失败。'],
 ['叙事内容','96个节点已经有状态与职责，不等于完整对白及演出已经定稿。','明确核心36段与可选日常容量；未读不恶意扣关系；后续补文必须使用既有知情/归责/缺席规则。','逐场完整对白、玩家选择、角色反应与全部分支文字审核。'],
 ['可用性证据','轻提示、菜单、预览和信息密度只有规则与调度测试。','保留可跳过帮助、多个解法和合法逃课；拒绝原因、成本和不可逆对象必须具体展示。','真人能否在不被强制提示打断的情况下理解并自主行动。'],
 ['呈现与节奏','角色立绘、棋子辨识、音效、阅读/操作时长尚未验收。','2D范围和资产职责已明确，不靠变3D弥补人物或玩法吸引力；不把估计时长写成测量结果。','真实资产一致性及完整局计时与阅读体验。'],
 ['正常开发待办','正式存档/迁移、预览执行一致、界面和兼容尚未实现。','已补保存字段及权威顺序，当前只做离线状态检查；遵守暂不开发。','进入开发后再做真实运行验收，此项不是本次设计自相矛盾。']]))
add('<div class="note warning"><b>当前结论：</b>发现的具体矛盾已经处理，已采样的36关与整局链条仍成立；但“所有逻辑永远无问题”“培养一定吸引人”“必然愿意二周目”没有证据支持。当前不是可以跳过内容与体验验证的最终验收状态。没有需要替用户决定的新题材、永久损失边界或收费模式，本轮没有额外提出审批。</div>')
add('<h3 id="authority">当前规范、复核资料和工程边界</h3><p>当前权威入口为 <code>game/data/final_design/design_manifest.json</code>；0.14字段清单与边界在 <code>full_audit_contract.json</code>。历史0.13报告保留为上一轮证据，不覆盖本次医疗、工坊、改约、归责与状态修正。正式运行时 .gd/.tscn/project.godot 的哈希完全未变。</p>')
add('<p><a href="full-audit-findings.json">问题与修正清单</a> · <a href="full-audit-before.json">三个模型错误的修正前重现</a> · <a href="full-audit-checks.json">当前规则检查</a> · <a href="full-audit-matrix.json">全部关卡矩阵</a> · <a href="full-audit-campaigns.json">整局结果</a> · <a href="full-audit-subsystems.json">既有子系统重新执行记录</a></p><p>仅重建本轮：<code>python3 work/full-audit/rebuild.py</code>。从基础内容重建：<code>python3 work/final-design/rebuild.py</code>。新规则是当前正式产品方案的设计工具，没有另做待丢弃的演示游戏。</p></section>')
section='\n'.join(parts);(O/'full-audit-section.html').write_text(section)
old=(O/'growth-identity-review.html').read_text();css=re.search(r'<style>(.*?)</style>',old,re.S).group(1)
(O/'full-audit-review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 0.14全域设计审查</title><style>'+css+'</style><main><h1>全量审查：哪里缺了，<br>哪里前后不一致</h1><p><a href="full-game-design.html">返回完整设计</a></p>'+section+'</main></html>')
proof={'version':'0.14','data_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in D.glob('*.json')},'reference_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'work/growth-identity-review/model.py',ROOT/'work/growth-identity-review/relationships.py',ROOT/'work/campaign-review/ledger_review.py']},'scope':'Fingerprint of rules accompanying this audit; not a product save compatibility implementation.'}
(O/'full-audit-inputs.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print('Built0.14 full audit report')
