from pathlib import Path
import json
import html

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs'
data = json.loads((OUT / 'balance-results.json').read_text())

def table(headers, rows):
    return '<div class="scroll"><table><thead><tr>' + ''.join('<th>'+str(v)+'</th>' for v in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in row)+'</tr>' for row in rows) + '</tbody></table></div>'

labels = {'relaxed': '从容', 'standard':'标准', 'hard':'严峻'}
sweep = table(['难度 / 关系', '候选任务', '无救援解，需拒绝', '通过可行性检查', '通过后仅一种不被支配的结果'], [
    [labels[r['difficulty']] + (' / 紧张' if r['strained'] else ' / 正常'), r['candidates'],
     r['rejected_no_rescue_plan'], r['accepted'], r['accepted_with_only_one_pareto_outcome']]
    for r in data['mission_sweep']])
sens = table(['事件强度', '小事消退半衰期', '紧张状态天数（不是争执次数）'], [
    [str(r['severity_multiplier'])+' 倍', str(r['ordinary_half_life'])+' 天', len(r['active_band_days'])]
    for r in data['sensitivity']])

content = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>关系驱动游戏：机制、平衡与重玩性立项补充</title>
<style>
:root{--ink:#21333d;--muted:#5e7079;--line:#d6e0e1;--accent:#087a71;--paper:#f4f6f2}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:1040px;margin:0 auto;padding:55px 46px 90px;background:#fff}header{border-bottom:3px solid var(--accent);padding-bottom:26px}h1{font-size:34px;line-height:1.35;max-width:850px}h2{font-size:25px;margin:46px 0 16px}h3{font-size:19px;margin:24px 0 10px}p{margin:12px 0}a{color:#006d70;text-underline-offset:3px}.eyebrow,.meta{font-size:13px;color:var(--muted)}.tag{padding:3px 10px;background:#e5f3ee;border-radius:5px;display:inline-block;margin:2px 5px 2px 0;font-size:13px}nav{line-height:2.2;margin:22px 0}nav a{margin-right:18px;white-space:nowrap}.callout{border-left:4px solid var(--accent);background:#edf7f3;padding:17px 21px;margin:24px 0}.warning{border-left-color:#bb7825;background:#fff6e8}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.65;margin:15px 0}th{text-align:left;background:#edf3f2;font-weight:650}th,td{border-bottom:1px solid var(--line);padding:12px 13px;vertical-align:top}code,pre{font:14px/1.7 ui-monospace,Menlo,monospace}pre{white-space:pre-wrap;background:#edf2f4;padding:20px;border-radius:6px}li{margin:7px 0}small{font-size:13px;color:var(--muted)}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.card{padding:18px;background:#f0f5f3}.big{font-size:28px;font-weight:700;display:block}footer{margin-top:45px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:13px}@media(max-width:680px){main{padding:25px 20px}h1{font-size:27px}.cards{grid-template-columns:1fr}th,td{padding:9px}}@media print{body{background:#fff}main{padding:0;max-width:none}nav{display:none}a{color:inherit}h2,h3{break-after:avoid}tr,.callout{break-inside:avoid}}
</style></head><body><main>
<header><div class="eyebrow">立项补充 / 系统设计 0.1 / 2026-10-31</div>
<h1>角色为什么会怨恨，玩家怎样改变局面，以及第二次为什么还值得玩</h1>
<p>针对“单机、两人协作开发、角色养成与队内关系”的机制研究。以暂定救援队题材举例；题材名称并未定案。</p>
<span class="tag">公开开发者资料</span><span class="tag">历史玩家反馈</span><span class="tag">可复算规则探针</span><span class="tag">尚未完成真人试玩</span>
</header>
<nav><a href="#decision">本轮结论</a><a href="#evidence">参考证据</a><a href="#model">计算规则</a><a href="#play">实际玩法</a><a href="#results">计算结果</a><a href="#difficulty">难度</a><a href="#replay">重玩性</a><a href="#validation">验证门槛</a><a href="#release">平台与时长</a></nav>

<h2 id="decision">先把产品判断说清楚</h2>
<p><strong>推荐继续验证的是“关系改变协作方式的单机策略游戏”，不是“不断积攒怨气、再花资源消怨气的游戏”。</strong>正面养成应带来新办法，冲突应迫使玩家重新安排合作条件。若删掉关系系统，玩家仍做完全相同的决策，只是效率数字变了，这个核心卖点就不成立。</p>
<p>第一版采用可解释的事件规则与有方向的关系记忆，不需要机器学习、情绪识别或运行时大模型。它们既不能替我们确定什么有趣，也会降低复现和调试的能力。本轮只验证部分规则与小型任务枚举，没有做出完整游戏，不能给出“已经好玩、已经平衡”的结论。</p>
<div class="callout"><strong>范围决策：</strong>先做 3 名角色、3 次连续任务、一次可追踪的失信和一次有代价的修复，目标体验 45–60 分钟；所有美术可暂用占位。只有玩家能理解、主动调整并愿意换一种方案再玩，才扩展角色与剧情。先前用 8 个主任务加 4 个变体就推定足够商业时长，没有依据，撤回。</div>

<h2 id="evidence">参考了什么，哪些结论能用</h2>
<p>本轮重点读公开讲稿、官方开发日志、作者自述和已有评论样本。没有声称亲自通关这些游戏，也没有将成功案例当作本项目的收入预测。旧版评论用于发现风险，不是对当前版本的缺陷判定；个别评论不能推算玩家占比。</p>
<table><thead><tr><th>来源与证据类型</th><th>读到的关键事实</th><th>对本方案的约束（我们的推论）</th></tr></thead><tbody>
<tr><td><a href="https://media.gdcvault.com/gdc2019/presentations/Giovannetti_Anthony_SlayTheSpire.pdf">《杀戮尖塔》GDC 2019 平衡讲稿</a>，开发者一手资料</td><td>强调各选项应有用途，结合指标、试玩反馈与分层难度迭代；数据本身不是结论。</td><td>不能追求所有搭配胜率相同。先找完全无用或普遍占优的选项，再用不同经验玩家解释原因。</td></tr>
<tr><td><a href="https://media.gdcvault.com/gdc2019/presentations/Into%20the%20Breach%20Postmortem%20Final.pdf">《陷阵之志》GDC 2019 设计复盘</a>，开发者一手资料</td><td>玩家回合的结果可确定；强调可读性、小数字；指出解谜式难度越过阈值就会无解。</td><td>争执不能无预告扣时间。生成任务要验证可行性；“时间减 1”不是平滑增加难度。</td></tr>
<tr><td><a href="https://wildermyth.com/wiki/Comic_Editor_Reference">《漫野奇谭》漫画编辑器参考</a>，官方站点模组文档</td><td>事件可要求人物、性格和关系条件，并设置触发次数、优先级和权重。</td><td>采用预写事件与条件匹配。随机选事件必须先满足因果和人物条件。</td></tr>
<tr><td><a href="https://eremitegames.com/ancient-hearth-update/">《风暴之城》Ancient Hearth 更新，2022-09-15</a>，开发日志</td><td>开发者调整过早过强的效果、难以被抽到的高阶效果，以及惩罚过重的地区。</td><td>检查恶劣条件组合出现的时间和强度，不能只分别平衡每一项。</td></tr>
<tr><td><a href="https://localthunk.com/blog/balatro-timeline-3aarh">LocalThunk：《Balatro》开发时间线</a>，个人开发者自述</td><td>早期方向、系统多次改变；朋友在测试版中投入数十小时的反馈，是继续扩展的重要信号。</td><td>先观察可玩的核心是否让人自发回头，再增加体量。作者本来以兴趣驱动，不能把路径当商业公式。</td></tr>
<tr><td><a href="https://www.reddit.com/r/gamedev/comments/1cp0ukt/a_postmortem_for_my_first_game_which_went_much/">《Our Adventurer Guild》作者复盘，2024</a>，个人开发者自述</td><td>开发约 2 年 10 个月，多次更换战斗方向；强调真实玩家反馈的帮助。</td><td>关系、养成、战斗、故事叠加的内容成本很高。先锁定核心操作，避免把全部系统一起开工。</td></tr>
</tbody></table>
<p>社区中的具体反例：</p>
<ul>
<li><a href="https://steamcommunity.com/id/thisiceaintnice/recommended/1940340/">《暗黑地牢 II》玩家评论，2024-08-11</a>：作者认为负面关系强制使用不想要的技能，削弱配置决策。对应验收：关系可以限制某种合作，但应提供可见的替代方案。</li>
<li><a href="https://steamcommunity.com/id/kaeshiva/recommended/2026000/">《Our Adventurer Guild》玩家评论，2025-08-30</a>：作者不满角色离队提示容易漏看，离队后自动存档造成损失。对应验收：重大不可逆结果必须有明确预告和确认，保留阶段存档。</li>
<li><a href="https://steamcommunity.com/id/ancient_eli/recommended/763890/">《漫野奇谭》玩家评论，2021-06-17</a>：作者喜欢第一次的故事，但认为后续对白和战斗重复。对应验收：第二次要有策略变化，不能以排列组合数冒充内容量。</li>
</ul>
<small>以上三条来自前次保存的公开 Steam 评论样本，本轮重新读取了存档文本；直达页本轮部分无法访问。它们是历史主观体验，不是全市场调查。</small>

<h2 id="model">怨气如何计算：把“原因”和“后果”拆开</h2>
<table><thead><tr><th>状态</th><th>含义与方向</th><th>游戏作用</th></tr></thead><tbody>
<tr><td>压力 S，0–100</td><td>每个人各自一份：疲劳、险情、伤势带来的当下紧张。</td><td>休息能降低，影响需要多少安全感；不会凭空指定某人为仇人。</td></tr>
<tr><td>怨气 R，0–100</td><td>A 对 B 与 B 对 A 分开。由 A 已知的具体负面记忆汇总。</td><td>影响某类合作的条件、对白和修复需求。</td></tr>
<tr><td>专业信任 T，0–100</td><td>A 对 B 的可靠性判断，独立于喜欢或讨厌。</td><td>允许托付、分工、接力等合作。可能“讨厌你，但认可你的能力”。</td></tr>
</tbody></table>
<p>6 名队员有 30 条队员之间的有向关系，再加 6 条对队长的关系。内部存储这些关系，不要求玩家逐条维护 36 根进度条。主界面只展示当前配队的重要关系、未解决的事件与将要影响的动作。</p>
<p>每条记忆记录：事件 ID、当事人、观察者、责任对象、类别、严重度、发生/获知时间、责任份额、是否严重、可用修复方式、修复进度。角色不知道的行为不会立即改变关系；得知真相才创建相应记忆，保证信息因果。</p>
<pre>事件初始强度 A = min(40, 严重度 × 角色对该类事件的敏感度) × 责任份额
当日记忆强度 M = A × 修复系数 × [记忆下限 + (1 − 记忆下限) × 2^(−经过天数 / 半衰期)]
怨气 R(A→B) = clamp(严重记忆之和 + 各普通类别中最强的 3 条记忆之和, 0, 100)

普通事件：半衰期先试 3 个游戏日，下限 0
严重失信：半衰期先试 8 个游戏日，未处理下限 35%
修复系数：未处理 1；针对事实认责 0.85；完成对应补救 0.45
完成补救后移除该记忆下限；叙事记录仍保留
紧张压力 Q = clamp(R + 0.25 × max(S − 40, 0), 0, 100)</pre>
<p><strong>这些数字是可调的第一版参数，不是心理学结论，也没有“行业通用怨气算法”。</strong>采用指数衰减，是因为可预测、易调试；采用记忆下限，是为了区分小摩擦与严重失信。严重事件可以留下痕迹，但其单条残余不应永久阻断所有合作。</p>
<p>进入“需要协商”状态的起始门槛先设为 R≥25 且 Q≥45；退出门槛为 R≤20 或 Q≤30。进入、退出采用不同阈值，避免在临界值附近反复变脸。<strong>达到阈值不等于立刻发生争执：</strong>还必须有相关动作、对应记忆、冷却已过；第一版每个队伍每次任务最多一次需要额外决策的关系事件。相关动作的既有约束仍然显示，不反复弹窗。</p>
<p>这部分使用的是<strong>带滞回的有限状态机</strong>。剧情事件使用<strong>条件过滤后加权抽取</strong>。小型任务使用<strong>枚举合法计划、检查约束与非支配结果</strong>。没有必要因为“游戏有很多算法”而全部加进来。</p>

<h3>怨气从哪些行为积攒</h3>
<table><thead><tr><th>玩家行为 / 事件</th><th>初始严重度建议</th><th>谁对谁产生变化</th><th>为什么不是无理由扣分</th></tr></thead><tbody>
<tr><td>当众否定已被验证的专业建议</td><td>8</td><td>被否定者 → 实施者</td><td>意见不一致本身不处罚；羞辱或无视已知风险才是事件。</td></tr>
<tr><td>违背公开约定，连续给同一人危险岗位</td><td>12</td><td>被安排者 → 队长</td><td>工作量账本按近期实际负担核对，自愿接班与公平轮换不算违约。</td></tr>
<tr><td>擅自占用已约定给队友的防护装备</td><td>12</td><td>受损者 → 决策责任人</td><td>在分配界面就显示受影响对象，不能让无辜队友背锅。</td></tr>
<tr><td>明确答应撤离，临时改变计划令队友独自承担风险</td><td>32，严重事件</td><td>受损者 → 失信者 / 批准者，按公开规则分责</td><td>责任份额合计≤1；同一事件不再以“失信、受伤、延误”重复扣三遍。</td></tr>
<tr><td>明知大家已同意风险，仍然发生不可避免的失败</td><td>不自动增加怨气</td><td>压力上升，按具体行为决定是否改变信任</td><td>坏结果不自动等于有人背叛，避免“失败→吵架→更失败”的自动循环。</td></tr>
</tbody></table>
<p>性格敏感度先限定在较窄区间，例如 0.8–1.3。人物故事解释底线，不能让一个悲惨过去自动变成到处加惩罚的被动技能。基本偏好提前可知，具体往事可逐步揭露。</p>
<p>正常摩擦的前三条堆叠上限用于防止琐事淹没严重事件；它不是第四次起免费伤害。重复失信仍降低信任。是否需要将长期反复行为归纳为“长期不公平”的专门事件，要在原型中验证，当前脚本尚未实现。</p>

<h2 id="play">玩家怎样处理新局面</h2>
<p>例：林岚对许舟已有 16 点有效怨气。新事件是双方原先同意撤退，许舟提出留下拿物资，玩家批准；界面提前说明这会违背对林岚的承诺。该事件严重度 32，林岚敏感度 1.25，按此事件规则许舟与队长各负一半责任。</p>
<pre>新增对许舟怨气 = 32 × 1.25 × 0.5 = 20
对许舟总怨气 = 16 + 20 = 36；另产生对队长的 20 点记忆
若林岚当前压力为 80：Q = 36 + 0.25 × (80 − 40) = 46
下一次需要许舟为她提供绳索保护时，出现协商条件。
如果是队长独自改变命令，责任就记给队长，不照搬这份 50/50 分责。</pre>
<p>角色提出的条件是：“这次要么加第二道保护，要么走不需要他保护的路线。”这是具体的不信任对象与危险情境，不是泛化的所有动作变慢。</p>
<table><thead><tr><th>处理方式</th><th>立刻得到什么</th><th>需要付出什么</th><th>后续如何变化</th></tr></thead><tbody>
<tr><td>加装独立保护设备</td><td>能执行该危险路线</td><td>装备位、耗材或提前准备</td><td>绕过当下依赖；不会凭空消除失信记忆。</td></tr>
<tr><td>改走安全路线</td><td>保持这组技能组合，减少互相托付</td><td>时间或放弃额外物资</td><td>兑现新约定后获得正常的合作信用。</td></tr>
<tr><td>换搭档、调整并行任务</td><td>让不同能力与关系解决当前任务</td><td>另一支小队能力下降或少接任务</td><td>换队不是抹除旧账，也不强迫每次必须修复。</td></tr>
<tr><td>认责并完成对应补救</td><td>降低那条事件的持续影响</td><td>实际补偿、训练时段或在新险情中履行承诺</td><td>撤掉严重记忆下限，逐步恢复可信程度；无法靠重复点击刷取。</td></tr>
<tr><td>暂时只维持专业合作</td><td>允许“关系不亲密，但工作可靠”的路线</td><td>采用正式交接和较独立的分工</td><td>避免把所有人物都哄成朋友变成唯一正确玩法。</td></tr>
</tbody></table>
<p><strong>正面养成也要改变动作。</strong>例如高专业信任加对应训练，允许一人先固定绳索、另一人先处理伤员；一般搭档只能一起完成。它是动作顺序与分工的变化，而不只是全属性加 10%。能力、装备、合作训练都应有互斥的投入机会，防止最后所有人全满、配谁都一样。</p>
<p>这需要关卡存在“托付、同步、独立工作”三类任务机会；若每个任务都只有同一条路，关系再复杂也只是在添堵。原型必须先做出至少两种操作上不同的救援办法。</p>
<p>通用道歉只能缓和当下压力，不能清空记忆。针对事实认责只能一次；补救要匹配受损事项。正常信任增长来自新的、真实的合作机会，按任务机会 ID 去重。玩家可以选择不和好，但必须能判断那样会失去哪些办法。</p>

<h2 id="results">实际计算发现了什么</h2>
<p>附件 <a href="relationship_model.py">relationship_model.py</a> 可用 Python 标准库直接运行，输出 <a href="balance-results.json">balance-results.json</a>。这是规则探针，不包含完整地图、升级经济、剧情选择器或游戏界面。</p>
<div class="cards"><div class="card"><span class="big">6,000</span>简化任务条件组合<br><small>1,000 种子 × 3 难度 × 2 关系状态</small></div><div class="card"><span class="big">203</span>开局无救援可行解<br><small>未经约束的候选生成结果</small></div><div class="card"><span class="big">20</span>通过的规则检查<br><small>含 100 条 × 100 日状态边界扫描</small></div></div>
<h3>发现一：不能随便扣一格时间</h3>
<p>探针枚举 3 条路线、3 种装备、救人或救人兼取药两类目标，并检查时间、现金与单装备位。每组最多 18 种计划。没有可行救援计划的候选应拒绝；这只是<strong>开局可行性</strong>，不保证玩家任何后续操作都能成功，也不要求所有目标能同时达成。</p>
__SWEEP__
<p>“非支配结果”表示不存在另一个方案在目标完成、现金花费、时间三项上全部不差且至少一项更好。它不是有趣程度。部分通过的任务仅有一种这样的结果，说明<strong>有解仍可能太单调</strong>。不能只以“全部可通关”为关卡验收。</p>
<p>下一版生成器应先检查任务模板、当前可用人员与基础装备，再抽取变体；失败时回退到已验证模板。玩家主动透支导致后续困难可以保留，但不得突然空投一个必须依赖已失去角色才可完成的强制主线。明确显示的撤退和低收益支援工作保证仍有可操作选择，不自动补齐玩家错过的奖励。</p>
<h3>发现二：之前的绞盘例子存在用途问题</h3>
<p>在探针的关系正常状态下，三个难度共 3,000 个候选中，绞盘从未出现在非支配方案上：它和更便宜的撬棍都只是省一点时间。在本模型里它被替代了。这不是现实绞盘没有价值，而是<strong>我们给装备写的规则太薄</strong>。</p>
<p>修正方向：绞盘应支持特定垂直运输、替代人工保护或解锁特定路径；撬棍对应破拆，两者服务不同障碍。不能只改价格掩盖同质化。该修正需要地图版原型验证，本轮没有冒称已完成。</p>
<h3>发现三：怨气参数不能拍脑袋定死</h3>
<p>固定输入为第 0、2、4 日各一次小摩擦，第 6 日一次严重失信，之后没有新摩擦且压力逐日下降。只改变事件强度和普通记忆半衰期，21 日观察窗内紧张状态持续 0–11 日。基准参数为 5 日。这不是玩家发生争执的频率，因为情境触发与冷却尚未接入。</p>
__SENS__
<p>普通 12 点记忆在第 0/3/6/12 日分别约为 12/6/3/0.75；严重 32 点记忆在第 0/6/12/24 日约为 32/23.57/18.55/13.8。完成对应补救可去除下限并加快总量降低；不是送礼删除往事。</p>
<h3>防刷与归责检查</h3>
<p>脚本检查了错误归责、方向性、未知事件、重复结算、100 次重复道歉、重复合作、错误补救、复用同一个补救凭证、压力单独触发、临界状态抖动及数值边界。还检查了初始信任 0–100 的“伤害后补救”是否获利。</p>
<p>实现时发现一个边界漏洞：信任已为 0 时，若按名义损失返还补救收益，就会凭空涨信任。现改为按<strong>实际扣掉的信任</strong>计算有限返还，101 个起始值检查通过。正式游戏仍需验证补救凭证真的来自玩法；当前函数输入的凭证视为已被验证，不能将这个脚本当作完整防刷系统。</p>
<div class="callout warning">尚未验证：真人觉得角色行为是否合理、最优队伍是否趋同、整局资源循环是否崩坏、故事是否动人、玩家是否愿意再开、是否愿意购买。这些不能用本轮 6,000 组计算代替。</div>

<h2 id="difficulty">三个难度，改外部条件，不改人物人格</h2>
<table><thead><tr><th>设置</th><th>从容</th><th>标准</th><th>严峻</th></tr></thead><tbody>
<tr><td>任务时间（探针已实现）</td><td>基准 +2</td><td>基准</td><td>基准 −1，必须通过可行性检查</td></tr>
<tr><td>正式版拟验证的资源压力</td><td>更充足恢复窗口</td><td>需权衡恢复与产出</td><td>更多互斥机会；恶劣条件组合有上限</td></tr>
<tr><td>关系计算 / 人物底线</td><td colspan="3">相同；不让高难度人物突然更小心眼或更随机。</td></tr>
<tr><td>信息与选择预告</td><td colspan="3">因果解释、代价与已知风险始终可看。提示开关独立，不以隐藏规则当高难度。</td></tr>
<tr><td>故事完整性</td><td colspan="3">全部难度可获得完整故事；不强制刷高难度才能看真正结局。</td></tr>
<tr><td>存档</td><td colspan="3">默认阶段存档与手动存档。铁人限制如要做，单独作为可选项。</td></tr>
</tbody></table>
<p>这不意味着高难度只能减时间。时间限制具有跳变风险，正式平衡还要比较可用路线、并行任务冲突与资源机会成本。先一个维度一个维度测试，再测试组合，不一次把时间、耗材、怨气倍率全部调坏。</p>

<h2 id="replay">稳定规则与可重玩并不冲突</h2>
<p>第一轮为了把当前局面处理好，第二轮应该因为“我想尝试另一种配队与承诺”回来。随机数只能产生新局面，不能替代足够深的决策。</p>
<table><thead><tr><th>保持稳定</th><th>允许变化</th><th>第二次的具体新问题</th></tr></thead><tbody>
<tr><td>人物身份、价值观、既有创伤</td><td>可信的开局资源、招募顺序、初始关系事件</td><td>这次熟悉的人更晚到，前期由谁承担另一项职责？</td></tr>
<tr><td>动作与装备规则</td><td>任务窗口、地形阻碍、物资位置与天气组合</td><td>上次用高信任双人配合，这次独立设备路线是否更划算？</td></tr>
<tr><td>事件的因果条件</td><td>满足条件的事件出现顺序、有限变体</td><td>修复旧承诺还是保住当前资源？后续哪个机会受影响？</td></tr>
<tr><td>完整的首次结局</td><td>行动导致的队伍结局、不同发展方向</td><td>能否在不重复上次牺牲的情况下完成这一季？</td></tr>
</tbody></table>
<pre>事件选择流程：
1. 先处理必须兑现的剧情后果与承诺，不让随机事件覆盖因果。
2. 过滤不符合在场角色、地点、已知信息、关系与冷却条件的事件。
3. 从剩余可选事件按权重抽取：基础权重 × 情境适合度 × 新鲜度。
4. 新鲜度优先照顾未见事件，但不因“没见过”破坏人物逻辑。
5. 没有合适事件就安静推进，不为凑冲突强行吵架。
6. 种子、事件记录和随机状态一起保存，保证能复现和调试。</pre>
<p>主线是章节式的有限战役，不先承诺无限 Roguelike。重复任务不能免费无限刷信任：游戏日推进会消耗机会、改变世界，合作奖励绑定真实任务机会。已读对白可快进，关键因果有摘要。重新开局提供跳过教程，不要求每次读相同长序章。</p>
<p>初期内容制作按事件家族计算：事件条件、2–3 个实质选项、状态后果、后续回响、缺角色情况与测试成本。不能把“6 人可以配出 15 对”直接宣传成 15 条完整人物线。先验证 3 人之间的少数因果链，再测一条合格事件的实际制作耗时。</p>
<p>如果多数测试者只想玩一遍，正确反应是判断它是否适合做扎实的单次体验，而不是强制多周目、数值解锁真结局或重复刷关。单机不必须无限重玩；但若我们的卖点是多种关系路线，就必须兑现这个承诺。</p>

<h2 id="validation">怎么把数值变成产品，而不是一张表</h2>
<p>平衡目标先限定为：每个主要方案有适用情境；坏结果能解释；关系造成有意义的选择；失误后仍有可操作的恢复路径。不是维持固定争执频率，更不是把角色培养好了又暗中补一场冲突。</p>
<ol>
<li><strong>规则层：</strong>自动检查归责、去重、循环收益、状态边界、事件条件冲突和任务可行性。本轮完成其中一部分，正式版逐步移植到游戏测试。</li>
<li><strong>策略层：</strong>有完整升级经济后，在相同种子比较固定最强搭档、轮换、设备优先、关系投资、牺牲可选目标等策略。看任务收益、损失、资源消耗和可用行动，不先捏一个总分把偏好的策略设成赢家。</li>
<li><strong>体验层：</strong>找 12–20 位目标玩家进行第一轮定性试玩，区分偏策略与偏人物故事的玩家。招募人数是执行计划，不是统计代表性样本，也不是已招到的人。</li>
<li><strong>商业层：</strong>在内容成立后测试演示视频、可玩 Demo 与价格预期，区分“礼貌说有趣”“实际下载试玩”“自发继续/再开”和“愿意付费”。目前没有付款或销售证据。</li>
</ol>
<table><thead><tr><th>原型要观察的事实</th><th>失败时怎么改</th></tr></thead><tbody>
<tr><td>玩家能否复述这次怨气归谁、为什么，以及两种处理方法？</td><td>若普遍说不清，先改信息展示和责任规则，不继续写人物故事。</td></tr>
<tr><td>同一位玩家换开局后，是否主动改变配队、路线或资源投入？</td><td>若始终同一方案，检查任务需求、能力重叠与装备支配关系。</td></tr>
<tr><td>玩家是否感到至少一次“培养这段关系改变了我能做的事”？</td><td>若只感到少扣一点数值，增强正向协作动作；必要时降低关系系统地位。</td></tr>
<tr><td>失误后是否愿意继续处理，而不是认为必须读档重来？</td><td>检查预告、永久损失、恢复成本和剩余决策是否有价值。</td></tr>
<tr><td>是否有人在未被要求的情况下愿意尝试第二种处理？</td><td>若两轮迭代后仍几乎没人想再玩，停止扩大体量，重审核心玩法。</td></tr>
</tbody></table>
<p>记录时同时看行为与口头解释：选项出现率、被选率、选择前状态、事件原因查看次数、读档位置、任务时间、第二次路线变化。胜率高不一定代表某角色强，也可能只有熟练玩家选择他；因此按难度与玩家经验分开分析，并看同一玩家的对照情况。</p>
<p>两个人的分工：我负责规则代码、事件工具、检查、日志分析与脚本迭代；你负责实际操作体验、审美与内容取舍、试玩组织及产品决策。外部试玩者是验证对象，不等于默认雇团队。美术模型可以后续替换，但无法替代这里的测试。</p>

<h2 id="release">Steam、退款与内容时长</h2>
<p><a href="https://store.steampowered.com/steam_refunds/">Steam 官方退款规则</a>通常是购买后 <strong>14 天内、游玩不足 2 小时</strong>，不是 14 小时；超出这些条件仍可提交申请，由平台审核。不能把超过 2 小时理解为绝对不退。</p>
<p><a href="https://partner.steamgames.com/doc/gettingstarted/appfee">Steam Direct 官方说明</a>为每款应用 100 美元或等值费用，可能另有税；费用本身不可退款，产品达到至少 1,000 美元调整后总收入后可在付款中回收。因此更准确地叫应用提交费，不是无条件退还的押金。</p>
<p><strong>平台建议仍是 Steam PC 买断制，先验证原型，再支付提交费筹备商店与 Demo。</strong>这项费用不值得倒逼整个玩法。不能为了绕开退款窗口把 90 分钟好内容拉成 3 小时。也不能指望换平台就解决没有吸引力的问题。</p>
<p>商业版本的初步体验目标改为<strong>首次完整战役约 4–6 小时，分章节随时保存；重玩是可选增值</strong>。这是设计目标，不是已测时长。预算可先按 12 个任务阶段 × 15–25 分钟，加 30–60 分钟分散的经营和故事，得到约 3.5–6 小时的假设；但若实测每关只有 5 分钟，必须承认不够，不能靠这个乘法证明内容成立。</p>
<p>前 15–20 分钟应让玩家做一次清楚的协作选择；45–60 分钟内体验一次“选择→关系后果→调整方案→可见回报”的完整链。可玩 Demo 应真实展示这条链。售价需在实际体量和目标玩家反馈后确定，本轮不再凭空报“稳赚价格”。基础收入来自完整游戏买断，不设计付费修复关系、抽卡充值或把必要结局拆出去卖。</p>
<p>《Our Adventurer Guild》作者在 2024 年复盘中披露，当时玩家游玩时长中位数约 6 小时 25 分钟，退款占销量 8.1%。这只是一个自报案例，不能用于预测我们的退款率，也不能解释退款原因；它提醒我们，长于 2 小时与不发生退款是两回事。</p>
<div class="callout"><strong>现在可以作出的决定：</strong>采用单机、可解释关系规则、可协商的冲突、有限章节战役和买断方向，先做核心试玩段。<strong>现在不能作出的承诺：</strong>已经平衡、足够重玩、能卖多少份或必然赚钱。本轮计算明确否定了部分早期假设；下一步应由能玩的结果决定是否扩大投入。</div>
<footer>资料核对日期：2026-10-31。所有游戏规则、系数、内容数量和测试规模均为本项目建议，除明确标注的开发者事实与平台条款外，不是竞品内部实现或行业统计。<br>复算：python3 relationship_model.py。附件的运行结果是合成输入下的设计检查，不是玩家成功率。原有宽泛立项报告中的外包预算不适用于当前仅你与 AI 协作的约束；本文件不恢复该预算假设。</footer>
</main></body></html>'''

content = content.replace('__SWEEP__', sweep).replace('__SENS__', sens)
(OUT / 'relationship-design.html').write_text(content, encoding='utf-8')
print('Report written:', OUT / 'relationship-design.html')
