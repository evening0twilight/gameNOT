"""Inspectable design decisions, bounded evidence and complete campaign receipts."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
def load(p):return json.loads(p.read_text())
K=load(D/'player_choice_contract.json');M=load(O/'player-choice-matrix-results.json');C=load(O/'player-choice-campaign-results.json');V=load(O/'player-choice-checks.json');A=load(O/'player-choice-dominance.json');W={r['witness_name']:r for r in load(O/'player-choice-witnesses.json')};PAID=load(O/'player-choice-paid-guard-diagnostic.json');B={b['id']:b for b in load(D/'boards.json')['boards']}
def e(x):return html.escape(str(x))
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
p=[]
def add(s):p.append(s)
add('<p class="eyebrow">夜潮事务所 · 玩家选择审查0.11 · 2026-11-02 · 设计阶段</p><h1>值得做，才是一项选择</h1><p>本轮从玩家的操作、注意力、成长投入和替代办法重新评审。0.10留下的三个问题确实成立：12处相同的两轮值守重复；通用维修主要换取结尾状态；一次失败的普通走法不足以证明高级合作值得投资。本修订直接删减和重组，不保住旧设计的数量。</p>')
add('<div class="note"><b>当前决策：</b>12处附加值守减为4处不同节奏；8处取消额外等待。通用逐台维修清单取消，仅保留两座有期限、有实际后勤回报的设施。保护与交叉掩护改为无需训练的现场协作；接力和定向牵引附带于合格的普通双人训练，不另收费。基础操作、普通工具、诱导与绕行均保留。</div>')
add('<nav>'+''.join('<a href="#'+a+'">'+b+'</a>' for a,b in [('field','12关取舍'),('repair','维修回报'),('cooperation','合作与普通解法'),('campaign','整局对照'),('maps','36关'),('boundaries','验证边界')])+'</nav>')
add('<h2 id="field">玩家还要等什么：删除重复，保留四种现场问题</h2>')
rows=[]
for mid in ['M05','M08','M10','M11','M13','M17','M21','M22','S01','S04','S10','S11']:
 s=K['services'].get(mid)
 rows.append([mid+' '+B[mid]['title'],s['label'] if s else '删除附加值守',s['effect'] if s else K['removed_services'][mid],('位置'+str(s.get('stages',s['posts']))+'；截止轮'+str(s['deadline'])+'；前置'+str(s.get('prerequisites',[]))) if s else '原主目标和额外目标保留'])
add(table(['关卡','当前安排','玩家实际处理的问题','边界'],rows))
add('<p>M05操作会真的把标记浅水改为干地，不是只改结尾文字；原漏口将来的涨水不会凭空消失。M10、M21会在原测试／施工也完成后开放临时出口，因此存在新的撤离路线。S11要求换位操作并管理一次性绝缘工具。原本的停机、拆除、保护、暂控、换人和放弃额外成果仍合法。</p>')
add('<p>24个主任务中只有3次新增现场操作，全36关是4次；双点连续两轮只保留在M21。M08与S04不再在同一天重复站点，S10也不再紧挨M21安排一次同类等待。这是结构和输入次数的减少，不宣称已经证明玩家不会厌倦。</p>')
add('<h2 id="repair">维修要换来可用的安排，不能只是营地里的欠账</h2>')
add(table(['设施','保全或修复后的资格','修复成本','可使用的晚数'],[[x['label'],'2次外部后勤协助，每次最多2人；每晚全队最多用一处','1项目＋2物资',str(x['first_day'])+'—'+str(x['last_day'])+'晚'] for x in K['investments'].values()]))
add('<p>志愿者代办洗消、搬运和补给，减少疲劳12，有休息区则减16，压力减16。它不占营地两个项目名额，也不占角色的训练／剧情安排，不触发人物恢复项目的额外效果。修复当晚不可用，不治重伤、不加经验和信任、不消除失约。保全设施直接取得相同资格，破坏再修复没有额外奖励。</p>')
add(table(['玩家的当前处境','为什么可能愿意修','为什么可能不修'],[
 ['想持续使用偏好队伍，接下来几晚有人需要休整','一次项目投入，换取两晚由外部承担恢复，把营地项目留给其他人或设施','维修当晚的项目可能更需要用于关键训练或人物节点，后勤回报要到次晚才开始'],
 ['当前就需要恢复或推进人物节点','没有即时优势：新修设施要到次晚才可用','直接安排现有恢复／人物项目更符合眼前需要'],
 ['轮换充分，成员已经休息好','可为了社区恢复自愿投入','恢复量可能为0，不把“有两次资格”写成必得收益'],
 ['接近支援截止，或已经过期','仍可自愿做公益修复，社区设备会恢复','剩余一晚最多只能用一次；过期后明确只有社区后记回报，不续期']]))
add('<p>只有M05、M10提供这种战役投资。其他被毁机体保留为现场结果，不再弹出一串“1项目＋2物资”的维修债务。维修界面提前列出成本、剩余有效晚数、可用次数和当前合格人员；保底照护不依赖这些设施。</p>')
add('<h2 id="cooperation">普通办法更好时就让它更好；合作按用途收费</h2>')
add('<p><b>不再把弱价值动作当成高级培养奖励：</b>保护与交叉掩护无需训练，也不设60信任门槛，仍检查AP、位置与具体关系保障。需要培养的是接力和定向牵引：双向信任达到60的二人进行一次普通训练，付原价1项目＋2物资，每人获得原有3经验，同时学会这两种操作，不额外收费。高级动作信任不足时暂不可用，恢复后不用重买。新手按当前局面逐步接触动作，不增加四次强制教程。</p>')
add(table(['合作','值得使用的局面','普通替代为何保留'],[
 ['保护／交叉掩护','承受非致命机器冲击仍完成该轮工作；两个位置需要不同的保障安排','能靠躲预告、屏障或任务顺序安全完成，就没有理由强迫玩家用合作。它也不防电击、水火或失能'],
 ['接力','改变谁带物件离开、谁留下救援；接收者沿自己选定的路径移动','普通放下、拾取、搬运仍可用，有时更快或更合适；不能只凭一个对照宣称普通操作全都无解'],
 ['牵引','两人站在合法侧面，也能选择普通推手站不到的一侧方向','能走到对面普通推移，或带绞盘解决，就保留这些办法。删除M08的额外试验，避免为证明牵引价值而造任务']]))
add(table(['完整地图对照','主目标','额外成果','轮数／AP'],[[name,r['success'],str(r['secured']),str(r['rounds'])+'／'+str(r['ap'])] for name,r in [(n,W[k]) for n,k in [('M06普通交接','ordinary_handoff'),('M06接力','relay'),('M08牵引但不附加值守','pull_without_added_wait'),('M22普通分工','M22_ordinary_no_added_wait')]]]))
add('<p>M08另有精确几何检查：重机在(7,5)，两名人物位于(7,4)、(7,6)，可以牵到(6,5)；同一状态下向西普通推移需要站在地图外的(8,5)。这证明了一个方向能力的区别，并不证明整关只能用牵引。M22已直接移除重复值守，普通分工继续能完成交接、证据和脱敏。</p>')
earned=next(s for s in C['scenarios'] if s['summary']['name'].startswith('真实养成后'));learn=next(r for r in earned['receipts'] if r['kind']=='coordination_bundle' and set(r['actors'])=={'lin','su'});played=next(r for r in earned['receipts'] if r['kind']=='advanced_actions_used' and r['mission']=='M06')
add('<p>接力也已接回完整战役：对应的完整战役在第'+str(learn['day'])+'晚实际完成林岚／苏棠的普通双人训练，第6日使用当时真实的经验、信任和已学能力，执行接力并带回档案，然后继续到第24日。没有临时赠送技能或抬高角色等级。这条策略明确偏好档案成果，不宣称比选择更早撤离更适合所有玩家。</p>')
add('<h3>把全部已尝试的普通方案拿来比较</h3>')
add('<p>修订过程中的付费掩护候选方案共有'+str(sum(r['cooperation_attempts'] for r in PAID['rows']))+'条成功主目标尝试，其中'+str(sum(r['dominated_if_owned'] for r in PAID['rows']))+'条在已有工具的条件下被采样普通方案支配。因此撤销掩护的付费解锁，把培养回报集中到运输和空间操作。这个统计只覆盖四关里的掩护策略，不能扩大成所有合作的胜率。</p>')
add(table(['关卡','实际用了掩护且主目标成功的尝试','已有工具／训练时被普通方案支配','从零购买时被普通方案支配','找到非支配掩护方案的配置'],[[r['mission'],r['cooperation_attempts'],r['dominated_if_owned'],r['dominated_if_new_purchase'],str(r['cases_with_non_dominated_cooperation'])+'/'+str(r['cases'])] for r in A['rows']]))
add('<p>这里的“支配”要求普通方案成果不少、设备状态不差，而且伤亡、伤害、轮数、AP与相关投入均不更高，至少有一项更好。已拥有工具／训练和首次购买分开比较，不给不同资源硬凑一个偏好分数。分母是策略尝试或配置，不是玩家数；没有被采样普通方案支配，也不等于证明最优。合作在部分安排中输给普通办法的结果照实保留，不削弱普通动作来改漂亮数字。</p>')
add('<h2 id="campaign">玩家投进去的项目，最后实际换到了什么</h2>')
rows=[]
for s in C['scenarios']:
 q=s['summary'];support=q['external_support'];rows.append([q['name'],str(q['main_count'])+'主/'+str(q['side_count'])+'支',q['operational_summary']['repair_projects'],sum(support['uses'].values()),support['fatigue_recovered'],sum(r['kind']=='training' for r in s['receipts']),sum(q['xp'].values()),q['resources'],len(q['withdrawn'])])
add(table(['策略','任务','维修项目','实际外部后勤协助','实际恢复疲劳','训练次数','总经验','剩余资源','永久医疗离队'],rows))
compare=[C['scenarios'][i] for i in [4,5,6]]
add('<h3>同样拆除、同样可使用保全设施：只比较维修增加的收益</h3>')
add(table(['安排','M05修复成本','M05带来的外部后勤协助','M05实际恢复疲劳','M10原本保全的公共收益'],[[s['summary']['name'],str(sum(r['kind']=='equipment_restored' and r['mission']=='M05' for r in s['receipts']))+'项目／'+str(2*sum(r['kind']=='equipment_restored' and r['mission']=='M05' for r in s['receipts']))+'物资',sum(r.get('external_facility')=='M05' for r in s['receipts']),sum(r.get('fatigue_recovered',0) for r in s['receipts'] if r.get('external_facility')=='M05'),sum(r.get('external_facility')=='M10' for r in s['receipts'])] for s in compare]))
add('<h3>更高出勤压力下的同条件比较</h3>')
add(table(['策略','完成主／支线','主线仍用初始三人组的次数','训练次数','总经验','借调支援员人次'],[[s['summary']['name'],str(s['summary']['main_count'])+'／'+str(s['summary']['side_count']),sum(b['mission'].startswith('M') and set(b['party'])=={'lin','xu','su'} for b in s['battles']),sum(r['kind']=='training' for r in s['receipts']),sum(s['summary']['xp'].values()),s['summary']['borrowed_slots']] for s in C['scenarios'][-2:]]))
add('<p>总经验和物资不能只按“每修一次就少练一次”推算：修复先占项目，后续外部后勤协助又会改变疲劳、可出勤人员与可用于训练的营地项目。表中使用真实账本；共同拥有的M10支援没有算成M05维修的回报。自动策略使用可用后勤，并在人物和资源足够时以训练填满剩余项目，不声称它代表所有玩家，也不声称“修复必定更强”。</p>')
add('<p><b>这个回报的限制也已实测：</b>高出勤的两条对照均完成24主线＋12支线，主线均能24次使用初始三人组，没有借调；不维修训练14次、总经验666，及时维修训练13次、总经验660。维修增加48点实际疲劳恢复，却没有增加该策略的出勤或结局。因此不把它包装成常规成长收益，定位为可选应急后勤与社区修复，默认不催修。只有已安排的未来行动因疲劳受阻、有效期内后勤确实可解除限制时才提示，并列休息、换人。定向边界检查中，98疲劳无法训练，后勤减12后训练增加8，结束为94，确实恢复了一项原本不可用的安排；这证明条件性用途，不证明常规战役频繁需要它。</p>')
add('<h2 id="maps">放回36关的节奏与目标</h2><label>筛选关卡 <input id="filter" placeholder="M05、运输、删除……"></label>')
add('<div class="scroll"><table id="maps"><thead><tr><th>关卡</th><th>本轮处理后的职责</th><th>基础解法配置</th><th>额外现场操作</th></tr></thead><tbody>')
for m in M['maps']:
 mid=m['mission'];add('<tr>'+''.join('<td>'+e(x)+'</td>' for x in [mid+' '+m['title'],K['mission_roles'][mid],str(m['baseline_solved'])+'/'+str(m['cases']),K['services'][mid]['mode'] if mid in K['services'] else '无新增值守'])+'</tr>')
add('</tbody></table></div>')
add('<h2 id="boundaries">这轮解决了什么，以及证据的边界</h2>')
add(table(['发现的问题','当前修正'],[
 ['用12个同一规则制造“内容很多”的感觉','取消8个额外目标，保留4种不同节奏；基础目标不加新门槛'],
 ['维修主要换结尾状态，成长玩家不愿投入','两处限期外部后勤协助；其他通用维修项目移除；保全与修复待遇一致'],
 ['付费掩护在严格替代比较中经常被普通方案支配','掩护两项改为无需训练的现场协作，接力与牵引附带于普通双人训练；保留普通方案胜出的结果'],
 ['外部支援仍占用人物安排，参考计划又闲置第二个训练项目','改为志愿者代办后勤，不占角色安排；参考计划按现有规则使用剩余的两个项目，避免把模拟器闲置误判为收益'],
 ['没有修好泵／接好线，却提前获得现场成果','现场操作增加明确物理前置，出口也需原测试或施工完成'],
 ['换位任务误把一次性绝缘垫重复使用','只记录真实剩余次数，参考策略把垫子留给实际湿地；换阶段不刷新次数'],
 ['累计任务中失败轮次的协助可能混入成功贡献','当轮协助单独记录，只在该阶段有效时计入；失败不会抹掉此前真实阶段成果'],
 ['停止通用维修后仍可能弹出旧维修账','新提示只针对两处实际投资设施，其他机体只记录现场后果']]))
add(table(['验证','结果','能支持的结论'],[
 ['36关具名配置',str(M['configurations'])+'配置／'+str(M['attempts'])+'次策略尝试／基础未找到解法'+str(len(M['unfound'])),'标准难度、天气A、固定出生槽位；不是所有输入序列穷举'],
 ['难度与天气','276组原主目标×难度×天气上下文，全部找到基础解法','固定初始三人、1级、不开技能的保底检查，不表示所有额外目标均可全拿'],
 ['完整战役',str(len(C['scenarios']))+'条／'+str(C['actual_battles'])+'场战斗','真实加入日期、经验、信任、物资、项目和支援期限；战术候选选择使用事后信息'],
 ['定向检查',str(V['passed_count'])+'项通过','物理前置、任务阶段、工具、合作几何、休整、维修、训练与提示预算'],
 ['正式工程','运行脚本、场景及项目配置哈希未变','仅设计规范和离线参考推演，未开始正式开发']]))
add('<p>这次不把“能通关”当成“值得选择”。已证明的是：等待输入减少、部分现场行为会改变地面与出口、维修有实际且有限的后勤回报、合作存在不同的局面用途，也存在被普通方案替代的情况。玩家是否感到紧张、提示是否清楚、愿不愿为社区结果投资，以及反复游玩是否有趣，都还不是离线模型能替真人回答的问题。</p>')
add('<footer>'+ ' · '.join('<a href="'+f+'">'+t+'</a>' for f,t in [('full-game-design.html','完整设计0.11'),('player-choice-matrix-results.json','完整策略矩阵'),('player-choice-campaign-results.json','整局账本'),('player-choice-witnesses.json','逐动作案例'),('player-choice-dominance.json','普通替代对照'),('player-choice-paid-guard-diagnostic.json','撤销掩护付费的依据'),('player-choice-checks.json','验证记录'),('../game/data/final_design/player_choice_contract.json','当前规则')])+'</footer>')
style='<style>*{box-sizing:border-box}body{margin:0;background:#edf2ef;color:#203d43;font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1280px;margin:auto;padding:42px;background:white}h1{font-size:36px}h2{margin-top:46px;padding-top:18px;border-top:3px solid #0a8072;font-size:25px}h3{margin-top:30px}.eyebrow,footer{font-size:13px;color:#536b70}.note{padding:22px;background:#e7f3eb;border-left:4px solid #0a8072}nav{display:flex;gap:22px;flex-wrap:wrap;margin:26px 0}a{color:#087b6c}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px;margin:22px 0}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #d5e1da;min-width:90px}th{background:#eef5f0}input{font:inherit;padding:7px}footer{margin-top:38px}@media(max-width:760px){main{padding:20px}}</style>'
script='<script>document.querySelector("#filter").addEventListener("input",function(){for(const r of document.querySelectorAll("table#maps tbody tr"))r.hidden=!r.textContent.toLowerCase().includes(this.value.toLowerCase());});</script>'
# Distinct table ID avoids duplicating the section anchor.
body='\n'.join(p).replace('<table id="maps">','<table id="maps-table">');script=script.replace('table#maps ','table#maps-table ')
(O/'player-choice-review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 玩家选择审查0.11</title>'+style+'<main>'+body+'</main>'+script+'</html>')
(O/'player-choice-section.html').write_text(f'<section id="player-choice-review"><h2>玩家选择与投入价值 · 0.11（当前规则）</h2><p>0.10的12处值守减为4处不同操作，8处删除；通用维修清单改为两座限期支援设施。掩护两项无需训练，接力和牵引附带于合格的普通双人训练，不另收费，不禁止普通解法。M05累计排水改变地面，M10单次同步确认与M21连续保障在原建设完成后开放出口，S11分两步换位切电。后勤项目成本与未来收益均已放回整局账本。</p><p>{M["configurations"]}配置、{M["attempts"]}次策略尝试，276组基础难度/天气上下文，{len(C["scenarios"])}条完整战役、{V["passed_count"]}项定向检查。仅设计与离线推演；旧评审保留为历史，不应继续执行其中已撤销的12处值守和通用维修。</p><p><a href="player-choice-review.html">查看12关删改、维修实际回报、普通方案支配对照与36关回填</a></p></section>')
for file,values in [('game/docs/development.json',dict(design_version='0.11-player-choice-review',latest_review='../../outputs/player-choice-review.html',project_stage='Design only. Repetition, voluntary support investments and ordinary alternatives reviewed offline; formal development paused.')),('game/data/product.json',dict(design_version='0.11-player-choice-review')),('game/docs/logic-audit.json',dict(current_revision='0.11-player-choice-review',player_choice_contract='data/final_design/player_choice_contract.json'))]:
 f=ROOT/file;d=load(f);d.update(values);f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Built0.11 player-choice review,36-map table and current-design section.')
