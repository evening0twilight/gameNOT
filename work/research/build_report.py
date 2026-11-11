import json, html, math, re
from pathlib import Path

ROOT=Path(__file__).parent
OUT=ROOT.parent.parent/'outputs'
OUT.mkdir(exist_ok=True)
markets=json.loads((ROOT/'markets.json').read_text())
corpus=json.loads((ROOT/'corpus.json').read_text())
lookup={(x['appid'],x['kind']):x for x in corpus}
esc=lambda x:html.escape(str(x),quote=True)

sources={
'post':('Our Adventurer Guild：开发者公开复盘，2024','https://www.reddit.com/r/gamedev/comments/1cp0ukt/a_postmortem_for_my_first_game_which_went_much/'),
'exo':('Northway Games：Exocolonist 发售公告，2022','https://northwaygames.com/exocolonist-release/'),
'volcano':('AUTOMATON：火山的女儿开发者访谈，2026-07-29','https://automaton-media.com/en/interviews/daughter-raising-sim-volcano-princess-aimed-to-reassure-players-that-any-life-you-lead-is-equally-wonderful-devs-reflect-on-the-games-breakout-success-and-complete-edition/'),
'dispatch':('Dispatch：Steam 官方商店','https://store.steampowered.com/app/2592160/Dispatch/'),
'dispatch-news':('GamesBeat：Dispatch 周年开发者采访，2026-10-22','https://gamesbeat.com/dispatch-surpasses-5-million-players-as-adhoc-announces-mobile-expansion/'),
'loc':('Allcorrect：公开本地化报价说明，2026-03-05','https://allcorrectgames.com/insights/localization-pricing/'),
'visibility':('Steamworks：商店曝光机制','https://partner.steamgames.com/doc/marketing/visibility'),
'utm':('Steamworks：UTM 归因','https://partner.steamgames.com/doc/marketing/utm_analytics'),
'direct':('Steam Direct：发行流程与费用','https://partner.steamgames.com/steamdirect'),
'ai':('Steamworks：内容调查与 AI 内容披露','https://partner.steamgames.com/doc/gettingstarted/contentsurvey'),
'nppa':('国家新闻出版署：出版国产网络游戏作品审批','https://www.nppa.gov.cn/bsfw/xksx/cbfxl/wlcbfwspsx/202210/t20221013_600725.html'),
'godot':('Godot：许可证与商业发行','https://docs.godotengine.org/en/stable/about/complying_with_licenses.html'),
'web':('Godot：网页导出约束','https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html'),
}
def s(k,label=None):
 name,url=sources[k];return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label or name)}</a>'
def game(a,label=None):
 name=next(x['name'] for x in markets if x['appid']==a)
 return f'<a href="https://store.steampowered.com/app/{a}/" target="_blank" rel="noopener">{esc(label or name)}</a>'

# Purposeful qualitative readings. These are summaries, not verbatim review republication.
selected=[
(763890,'recent',0,'玩家记住的是家庭关系与一次牺牲，而不仅是战斗胜负。','养成需要留下可叙述的共同经历。'),
(763890,'negative',3,'首轮新鲜感很强，之后事件与战斗构筑的重复削弱继续游玩的动力。','不要把有限事件包装成无限故事。'),
(763890,'chinese',1,'起初不喜欢画风，经朋友推荐购买，最终被角色经历打动。','口碑能跨过审美障碍，但这不证明美术不重要。'),
(365360,'negative',0,'随机损失角色后，重建队伍和重新培养的时间负担令玩家厌倦。','失败应产生新局面，避免长时间补回旧进度。'),
(601840,'helpful',3,'好恶关系能改变协助、交易与交涉，玩家感到选择与战斗相连。','关系应提供行动和后果，不只是背景介绍。'),
(601840,'helpful',4,'推荐游戏，但认为高难度下关系奖励会让角色扮演退化为收益优化。','给角色作选择与配最强增益之间存在张力。'),
(601840,'negative',4,'反复阅读相同对白、较长流程让多次游玩变得拖沓。','重复内容应跳过；时长不能依赖重复对话。'),
(601840,'chinese',1,'明确提到因中文游戏视频创作者的游玩内容而购买。','有创作者导购的个案证据，没有可外推的转化率。'),
(1940340,'negative',2,'认为负面关系强制使用不想用的技能，限制了策略控制；也不喜欢长局失败后的重复。','争执必须可预见、可应对，且损失与投入时间相称。'),
(1148760,'helpful',0,'人物与故事带来持续的情绪投入，并驱动多次游玩。','叙事用户愿意为人物体验返回游戏。'),
(1148760,'negative',0,'肯定开头的美术、音乐和故事，但对后期重复、恋爱状态反馈不足及结尾失望。','漂亮开场不能代替关系成立后的持续反应。'),
(1148760,'negative',2,'反感为了修正悲剧重复流程，认为部分选择更像寻找唯一正确答案。','悲剧和多周目不是天然的留存机制。'),
(1148760,'chinese',2,'画风吸引购买兴趣，同时明确提出中文支持的重要性。','美术负责进入漏斗，本地化决定能否继续体验。'),
(1148760,'chinese',4,'题材和身份表达有吸引力，但文字、数值成长和简单卡牌未形成乐趣。','题材认同不能替代实际游玩节奏。'),
(1340480,'negative',1,'喜欢早期卡牌制作、像素美术与音乐，不喜欢后半段转向政治经营的节奏。','前后半程应兑现同一种核心体验承诺。'),
(462770,'helpful',1,'喜欢大量阅读、角色和抉择，并提醒潜在玩家这是一款很重叙事的游戏。','宣传应明确阅读比例，筛选合适用户。'),
(462770,'negative',1,'肯定角色与演出，但高互动比赛和低互动长对白的节奏切换令人疲惫。','两种好玩法拼接起来仍可能互相打断。'),
(1266030,'helpful',3,'喜欢承受选择后果、带着不同局面继续推进的体验。','可继续的失败比频繁重来更适合角色依恋。'),
(1266030,'negative',3,'认为资源状态、角色绝望与某些对白承诺之间缺少一致性。','人物反应必须读取真实的任务和资源状态。'),
(1266030,'chinese',2,'希望增加中文，现有语言条件让游玩费力。','重文本产品的语言门槛真实存在；数量不能用于估算需求规模。'),
(2026000,'helpful',0,'喜欢职业培养、装备与训练，认为部分界面难懂，战斗鼓励对白重复而慢。','养成选择要丰富；重复人物表达要简短、可加速。'),
(2026000,'helpful',3,'喜欢多系统协同，尤其职业与战术；接受较轻、较套路的故事。','这类用户主要购买战术深度，不能假定会转向纯叙事。'),
(2026000,'negative',0,'希望更多队员间对话，认为角色成长没有得到足够的队伍互动呈现。','关系表达仍有改进机会，但不能据一条评测认定市场空白。'),
(2026000,'negative',1,'对战棋与经营的组合有兴趣，却因浅层系统和重复推进不愿继续。','每个系统都做一点，未必有一个足够强的购买理由。'),
(2026000,'negative',3,'漏看不幸福提示后，长期培养的角色离队且自动存档，引发强烈挫败。','离队等重大后果要有清晰预警和干预窗口。'),
(2026000,'chinese',0,'认可玩法，但明确不满意美术。','愿意容忍美术的现有买家，不代表被美术挡在门外的人不存在。'),
(1043260,'negative',2,'重复布阵、整理装备和缺少数值预览，使早期有趣的循环变成操作负担。','经营深度应来自选择，不能来自反复点击。'),
(1043260,'helpful',2,'以较低预期享受培养、搭配和战斗，但也提到缺陷。','价格与购买场景影响满意度；低价好评不等于高价支付意愿。'),
(1119600,'helpful',2,'喜欢不同社会背景的人逐渐互相了解，且关系影响合作。','共同处境与价值冲突能够支持群像关系。'),
(1119600,'negative',0,'难以理解好感、信任和士气到底产生了什么效果，也不满意表达和界面。','关系机制必须能解释因果，不能只有若干进度条。'),
(1119600,'negative',2,'觉得极端生存处境下部分拒绝合作不合人物逻辑，系统过多且难读。','冲突强度必须符合处境；生硬制造争执会破坏可信度。'),
(317820,'helpful',0,'喜欢独特的卡牌与地牢构筑，但提醒名称容易让人误以为是另一种 RPG。','类型描述与截图必须准确管理预期。'),
(317820,'negative',1,'欣赏美术、幽默和新意，却因重复死亡、重练与战斗循环而不推荐。','新颖设定和风格不能单独支撑长线体验。'),
]
evidence=[]
for i,(a,kind,index,observation,implication) in enumerate(selected,1):
 page=lookup[a,kind];r=page['reviews'][index]
 evidence.append(dict(id=f'E{i:02}',appid=a,game=page['name'],sampling_page=kind,url=r['url'],date_as_displayed=r['date'],recommendation=r['recommendation'],hours_as_displayed=r['hours'],observation=observation,implication=implication,limitation='个体主观体验；历史版本未复测。采样排序并非随机。'))
def e(*ids):
 return ' '.join(f'<a class="eref" href="#E{i:02}">[E{i:02}]</a>' for i in ids)

meta={
763890:('A','2021','11,723 / 95%','3,075 / 94%','$24.99','¥80','纸片人物＋回合制战术；关系、变形与代际故事','核心机制参照；不能假定继承其多年内容库'),
365360:('A','2017','15,650 / 89%','2,525 / 72%','$29.99','¥99','雇佣兵战术、构筑、损失与重建','强战术参照；人物情感并非同等重心'),
1940340:('A','2023','12,152 / 75%','5,083 / 65%','$39.99','¥138','组队、压力、关系与长局冒险','成熟 IP／制作规格较高，不作成本样板'),
601840:('A','2021','5,299 / 93%','6,190 / 94%','$19.99¹','¥48','战斗与交涉牌组、人际利益','卡牌与关系相互作用；并非队友群像模拟'),
1148760:('B','2022','4,013 / 96%','未单列²','$24.99','¥92','成长安排、卡牌检定、群像与多周目','关系养成核心参照；文本和分支投入高'),
1340480:('B','2023','2,948 / 93%','1,289 / 90%','$17.99','¥68','自制占卜牌、人物关系和分支叙事','美术互动与叙事结合；并非队伍战术'),
1266030:('B/C','2023','1,919 / 90%【全语言】','未单列²','$19.99','¥70','极地求生、资源分配、船员忠诚','与关系经营高度相邻；清晰处境支撑矛盾'),
462770:('B 邻接','2017','5,579 / 90%','995 / 89%','$19.99','¥76','群像视觉叙事＋竞技动作','参考角色与选择，不复制动作制作规格'),
2026000:('C/A','2024','1,842 / 95%','612 / 94%','$14.99','¥58','公会、培养、关系、探索、战棋','最直接的组合竞品；同样功能表不构成创新'),
1043260:('C','2024','1,650 / 80%','599 / 69%','$14.99 → $4.94','¥52 → ¥17.16','购买培养战士、布阵与自动战斗','经营/构筑参照；叙事关系并非核心'),
1119600:('C/B','2020','783 / 80%【全语言】','未单列²','$19.99 → $2.99','¥77 → ¥11.55','小队生存、任务分配、社会背景矛盾','关系＋资源已有人尝试；也暴露解释性风险'),
317820:('C 邻接','2015³','1,741 / 76%【全语言】','未单列²','$19.99','¥79','卡牌铺地牢、职业解锁','不是重关系公会经营；用于观察重复和预期'),
699330:('C/A','2023','771 / 76%【全语言】','未单列²','$24.99','¥148','雇佣兵公司、回合制战术、长期队伍','补充较低热度样本，防止只看头部'),
280320:('C','2014','492 / 59%【全语言】','未单列²','$4.99','¥21','冒险者管理与任务战斗','较老、低价弱表现样本；不代替当代失败率'),
1669980:('B 边界','2023','3,016 / 95%','38,896 / 97%','$10.99 → $7.14','¥35 → ¥22.75','女儿成长、日程、结局与情感陪伴','中文养成需求强证据；单角色核心不等于群像'),
1948980:('A 边界','2023','2,015 / 93%⁴','17,248 / 80%⁴','$17.99','¥69','武侠开放世界、人情与角色成长','题材边界；规模更大，不作首作工作量参照'),
}
rows=[]
for a,v in meta.items():
 g,year,en,cn,usprice,cnprice,loop,caveat=v
 rows.append(f'<tr><td>{game(a)}<small>{g} · 正式发行 {year}</small></td><td>{en}</td><td>{cn}</td><td>{usprice}<br>{cnprice}</td><td>{loop}<small>{caveat}</small></td></tr>')
competitors='<div class="tablewrap"><table class="competitors"><thead><tr><th>游戏 / 对照用途</th><th>英语评测数 / 好评率</th><th>简中评测数 / 好评率</th><th>美国 / 中国区售价</th><th>实际购买体验与比较边界</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

cost_rows=[
('美术、UI、有限演出',7,15,6,14,4,9),
('外部叙事编辑／部分事件协作',1,3,3,8,1,3),
('程序专项协助与审查',1,4,.5,2,.5,2),
('中译英、母语润色与语言测试',2.5,6,5,12,2,5),
('音乐、音效、音频整合外援',.8,2,.8,2,.5,1.5),
('外部功能测试与兼容测试',1.5,3.5,1.5,3.5,1,2.5),
('商店胶囊、预告片、小规模宣传测试',1.2,3.5,1.2,3.5,1,3),
('软件、素材授权、发行杂项',.3,.8,.3,.8,.3,.8),
]
costs={g:{'base_low':sum(r[1+2*i] for r in cost_rows),'base_high':sum(r[2+2*i] for r in cost_rows)} for i,g in enumerate('ABC')}
for c in costs.values():c.update(total_low=c['base_low']*1.25,total_high=c['base_high']*1.25)
costtable='<div class="tablewrap"><table><thead><tr><th>现金预算项（人民币万元）</th><th>A 战术 RPG</th><th>B 群像叙事</th><th>C 事务所经营</th></tr></thead><tbody>'
for r in cost_rows:costtable+='<tr><td>'+r[0]+'</td>'+''.join(f'<td>{r[i]:g}–{r[i+1]:g}</td>' for i in [1,3,5])+'</tr>'
costtable+='<tr><th>小计</th>'+''.join(f'<th>{c["base_low"]:.1f}–{c["base_high"]:.1f}</th>' for c in costs.values())+'</tr><tr><th>含 25% 预备金</th>'+''.join(f'<th>{c["total_low"]:.2f}–{c["total_high"]:.2f}</th>' for c in costs.values())+'</tr></tbody></table></div>'

body=f'''
<header><div class="eyebrow">立项调研 · 决策版 1.0 · 2026 年 10 月 30 日</div>
<h1>角色关系，能否成为<br>一款游戏的购买理由？</h1>
<p class="lead">关系驱动小队策略 RPG · 群像叙事养成 · 公会／事务所经营<br>基于竞品商店数据、玩家定性反馈与开发者公开复盘的比较。</p>
<div class="badges"><span>普通单机游戏</span><span>AI 辅助开发，不接入实时生成</span><span>产品优先，时间与预算待验证</span></div></header>
<nav><a href="#decision">结论</a><a href="#method">证据边界</a><a href="#market">市场与竞品</a><a href="#users">目标用户</a><a href="#directions">三方向比较</a><a href="#product">推荐玩法</a><a href="#art">美术</a><a href="#cost">制作成本</a><a href="#business">付费与发行</a><a href="#validation">验证与止损</a><a href="#evidence">玩家证据</a></nav>

<section id="decision"><div class="kicker">01 / 立项意见</div><h2>优先验证 C：关系驱动的小队事务所经营。暂不进入完整量产。</h2>
<p>推荐的产品核心是：<strong>你培养一群需要共同工作的人，决定谁和谁合作、谁承担代价；他们会记住这些决定，并改变后续协作。</strong>经营给关系提供实际压力，人物经历给资源决策提供情感分量。战斗和恋爱都可以有，但不应成为首版需要同时兑现的第二、第三款游戏。</p>
<div class="callout"><strong>这是“优先投入验证”的推荐，不是“已经证明能赚钱”。</strong>公开证据能够证明相邻需求存在、指出竞争门槛和失败方式；它不能证明陌生玩家会为我们尚不存在的产品付费。</div>
<div class="three"><article><span class="rank">第二优先</span><h3>A · 小队策略 RPG</h3><p>战术需求证据较强，角色关系也有成熟先例。但必须同时交付战斗深度、敌人／关卡内容和关系体验。适合在战斗原型已被玩家主动反复游玩的条件下升级。</p></article><article><span class="rank">条件性选择</span><h3>B · 群像叙事养成</h3><p>用户愿意为人物和抉择付费；不能据此推出“多写悲惨故事就有效”。剧本结构、状态反馈、演出和本地化成为主要成本，只有在角色与写作样章明显胜出时优先。</p></article><article class="recommended"><span class="rank">优先验证</span><h3>C · 小队事务所经营</h3><p>最容易直接验证组队、关系和培养是否构成乐趣，也最容易以有限场景控制工作量。主要风险是退化成派遣计时器，或成为少了战斗的 Our Adventurer Guild。</p></article></div>
<p><strong>推荐理由有三层：</strong>① 用户原始诉求是角色之间的关系，而非特定战斗形式；② 竞品反馈反复提供“关系影响选择”及“失去控制、重复、叙事与数值脱节”的正反实例；③ C 可以用一个短流程验证这些问题，失败时不必先付出大量战棋资产或长篇分支剧本成本。第①是已知需求，第②是定性证据，第③是制作判断。{e(5,6,9,19,23,25,30)}</p>
<p><strong>不构成差异化的卖点：</strong>“有好感度”“角色会吵架”“有悲惨过去”“公会经营加养成”“用 AI 画得更便宜”。Our Adventurer Guild 已覆盖多项组合；Help Will Come Tomorrow 已把背景冲突与合作结合；Dispatch 已把团队派遣、人际关系与职场群像做成清晰的商业产品。{game(2026000)}、{game(1119600)}、{s('dispatch')}。</p>
</section>

<section id="method"><div class="kicker">02 / 调研方法与可信度</div><h2>本次做了什么，哪些结论仍不能下</h2>
<p>采集日期为 <strong>2026-10-30</strong>。建立了 16 款游戏的中美区域商店快照；另纳入 Dispatch 作为较新、较高制作规格的邻接竞争参照。针对其中 12 款抓取公开社区评测页：每款各一页“最有帮助”与“负面评测”，六款增加近期和简中页；每页取前五条可渲染评测。共 36 页、180 次评测出现，按原文永久链接去重后为 <strong>173 条候选</strong>。本报告从中整理 <strong>{len(evidence)} 条有具体内容的定性证据</strong>，附原文链接、页面日期和推论。</p>
<p>这是一份公开资料桌面研究，未购买或试玩这些游戏，未开展玩家访谈、问卷或付费实验，也没有竞品的后台销售与用户画像。负面评测专门用于寻找风险，其出现频次不能当作所有玩家的意见比例。未把候选评论全部声称为全文精读。</p>
<table><thead><tr><th>证据层级</th><th>本次采用</th><th>允许支持的判断</th><th>不能支持</th></tr></thead><tbody>
<tr><td><span class="pill fact">公开事实</span></td><td>官方商店、开发者复盘、平台文档</td><td>商品形态、当日价格、评测规模、公开周期和规则</td><td>未披露利润、全行业成功率</td></tr>
<tr><td><span class="pill fact">个体体验</span></td><td>具备具体理由的玩家评测</td><td>存在某种购买动机或挫败方式</td><td>这种体验有多普遍、当前版本必然仍如此</td></tr>
<tr><td><span class="pill inference">分析判断</span></td><td>跨竞品对照、制作拆解</td><td>优先验证哪个风险、怎样缩范围</td><td>把我们的审美和玩法假设当作市场结论</td></tr>
<tr><td><span class="pill hypothesis">规划假设</span></td><td>预算、工时、验证门槛、候选定价</td><td>做投入决策和敏感性分析</td><td>充当画师报价、行业转化均值或销量预测</td></tr></tbody></table>
<p class="note">样本按机制相关性选择，包含高口碑、混合口碑和较低热度作品；不是全市场随机样本，也不是同年发售队列。老游戏累计更久，折扣、捆绑包、发行资源、IP 和内容更新都会影响数据。没有据此计算“三个赛道平均销量”或市场成功概率。历史负评用于设计风险分析，不能视为对当前版本的缺陷诊断。</p>
</section>

<section id="market"><div class="kicker">03 / 市场证据</div><h2>相邻购买需求真实存在，但“2D 玩家”不是一个可直接售卖的人群</h2>
<p>下表保留 Steam 实际显示的评测口径。<strong>英语评测不是全球评测；简中评测不等于中国大陆买家；所有评测也不是销量。</strong>价格为该日区域页面本体价格，箭头表示促销前后，不把历史低价、礼包总价当作本体定价。</p>
{competitors}
<p class="note">¹ Griftlands 的美国区本体 $19.99 来自本次浏览的商店页；本地抓取前两个购买块被试玩和礼包占用，未以礼包价替代。² 中文页面未单独展示简中汇总时写“未单列”，不是零中文用户；原始返回行保留在数据附件中。³ Guild of Dungeoneering 原版 2015，后有 Ultimate Edition，跨版本累计不可视作同一发行周期。⁴ 大侠立志传页面提示部分跑题评测区间不计入总评；此处沿用平台显示口径，不用它与无此标记游戏作精确排名。全部链接直达商店，数据会随时间改变。</p>

<h3>三个可以成立的市场判断</h3>
<ol><li><strong>A 的战术受众证据最成熟，但关系不是唯一购买理由。</strong>Battle Brothers、Wildermyth 与 Griftlands 的英语评测均达数千至万级；Our Adventurer Guild 的好评中也明确强调职业和战斗。一个“关系很丰富、战斗一般”的产品不能自动得到这些人的购买。{e(21,22)}</li>
<li><strong>B 的中文潜力不能低估，也不能拿《火山的女儿》直接外推。</strong>火山的女儿有 38,896 条简中评测，但它围绕“女儿成长与陪伴”组织体验，且本体常规国区价 ¥35。Exocolonist、宇宙之轮姐妹会和它不是同一人群、同一价格带、同一文本门槛。我们能确认中文养成需求存在，无法确认群像争执同样受欢迎。</li>
<li><strong>C 有小团队可触及的需求，也存在很明显的有限规模与品质风险。</strong>Our Adventurer Guild 是最直接的成功参照，但其英语评测为 1,842 条；Iron Oath 的全语言 771 条，Adventurer Manager 为 492 条且 59% 好评。它们不能推导本项目销量，却足以反驳“套上公会经营就自带大量用户”。</li></ol>

<h3>公开销量／用户量：只作为边界，不拿来相加</h3>
<table><thead><tr><th>样本</th><th>公开信息及时间</th><th>对本项目有用的部分</th></tr></thead><tbody>
<tr><td>Our Adventurer Guild</td><td>作者 2024 年复盘：累计 5,626 份 Steam units，退款 457 份；gross $73,684；1.0 前约 4,500 愿望单。{s('post','开发者自述')}</td><td>较接近小团队实际规模；只是当时快照，未审计，也不是截至今天的销量。gross 不是可支配利润；不能用销量除愿望单当转化率。</td></tr>
<tr><td>火山的女儿</td><td>2026-07 开发者访谈报道累计超过 150 万份。{s('volcano','原访谈')}</td><td>证明角色养成可以形成大需求；平台范围与净销量口径未在此进一步核实，不当作 Steam 单渠道销量或本项目期望。</td></tr>
<tr><td>Dispatch</td><td>2026-10-22 开发者采访报道超过 500 万玩家，涉及多个平台。{s('dispatch-news','原采访')}</td><td>验证职场群像与派遣的广泛吸引力，同时抬高演出预期。“玩家”不能擅自改写成付费销量。</td></tr></tbody></table>
<p><strong>用户基数的诚实答案：</strong>这些方向各自有已支付、可观察的相邻受众，小到数千份实际销售案例，大到百万级突破案例；但没有可可靠去重的“关系游戏总用户数”。评测总和、Steam 全站人数、二次元手游用户数都不能作为我们的 TAM。现在能回答“值得验证”，尚不能回答“我们能拿到多少买家”。后者要用真实商店流量、试玩行为与价格测试缩小范围。</p>

<h3>竞争不只是同题材独立游戏</h3>
<p>玩家还会在已有大作、折扣旧作、视频／动画与我们的游戏之间分配时间。尤其 Dispatch 已经明确售卖“问题队伍＋派遣＋关系”的体验，不能省略这个竞品后宣称自己发现空白。它的商店有完整配音、影视化演出和人物关系卖点；我们不具备按同一呈现规格竞争的基础。合理切入点是更系统化、可反复比较的组队决策与可控的短流程；这仍是待验证的定位，而不是尚无人做过的发明。{s('dispatch','官方产品说明')}</p>
<p>买断游戏不要求用户永久离开竞品。更现实的目标是成为他们通关或暂时玩够现有作品后愿意购买的下一款。我们争取的是下一次购买与数小时注意力，不是手游式每日登录替换。</p>
</section>

<section id="users"><div class="kicker">04 / 目标用户与获客切口</div><h2>先按购买动机划分，暂不编造年龄、性别比例</h2>
<table><thead><tr><th>方向与首要用户</th><th>为什么买／继续玩</th><th>可验证的切入承诺</th><th>容易错招的人</th></tr></thead><tbody>
<tr><td>A：已经购买战棋、队伍构筑游戏，且愿意阅读角色事件的人</td><td>阵容与技能组合、风险控制、从失败中成长；关系让战斗更有意义</td><td>展示同一任务换一对队友，战术选项与事后关系如何变化</td><td>只要大量关卡与极深数值的硬核战术玩家；只想阅读、不能接受复杂战斗的人</td></tr>
<tr><td>B：购买成长模拟、选择叙事、群像故事，愿意为人物读较多文本的人</td><td>理解人物、陪伴成长、发现隐藏关系与不同结局</td><td>用一个完整关系转折证明人物有声音、选择被记住</td><td>被“恋爱”吸引但实际没有足够恋爱内容的人；只要随机构筑的人</td></tr>
<tr><td>C：购买团队管理、资源决策游戏，同时愿意关心具体成员的人</td><td>安排有限人手、承受取舍、看着一群难合作的人建立默契</td><td>一次看得懂的组队难题；做完任务后队伍发生可见变化</td><td>期待大型建造自动化的人；期待 Dispatch 同规格动画演出的人；只想轻松收集漂亮卡面的人</td></tr></tbody></table>
<p><strong>C 的首批研究对象：</strong>优先找最近一年实际玩过 Our Adventurer Guild、The Pale Beyond、Help Will Come Tomorrow、Wildermyth 中至少一款的人，再以 Dispatch 的剧情受众作相邻对照组。不同组分别统计，不把“喜欢看人物互动”误当作“愿意做经营决策”。不以看过某部动画作为付费意愿替代指标。</p>
<h3>怎么争取竞品用户</h3>
<p>对喜欢 Our Adventurer Guild 战术的玩家，不能许诺“我们也一样丰富”后移除战斗；应明确提供<strong>更集中、更短的关系经营体验</strong>，接受部分人不匹配。对喜欢 The Pale Beyond 的玩家，展示具体选择和队员之间的后果；对喜欢 Dispatch 的玩家，先让他们看到系统玩法，筛掉仅追求演出的人。对只被立绘吸引的用户，美术可以促成点击，但要尽早显示真实界面与操作。</p>
<p>渠道先从同类内容创作者、Steam 试玩与社区讨论切入。中文 Griftlands 评测里有被视频带来购买的个案；但 Our Adventurer Guild 作者也报告过社媒和创作者联系成效有限。因此“做视频就会火”没有依据，需要逐个渠道核算访问、试玩与愿望单，不使用粉丝总数估算销量。{e(8)} {s('post','开发者营销复盘')}</p>
</section>

<section id="directions"><div class="kicker">05 / 三个方向的产品比较</div><h2>在相同小团队前提下，各自必须做好的东西不同</h2>
<p>比较范围统一为：PC 买断单机，8 名核心角色，有限据点和任务场景，中英文本，无全程语音、无开放世界、无联机、无付费抽卡；目标是一轮约 8–12 小时的完整体验，而非三种方案都达到头部竞品体量。时长是设计目标，必须通过测试确认，不能靠重复任务补足。</p>
<table><thead><tr><th>项目</th><th>A 小队策略 RPG</th><th>B 群像叙事养成</th><th>C 公会／事务所经营</th></tr></thead><tbody>
<tr><td>主循环</td><td>编队与构筑 → 战术任务 → 战损与关系事件 → 培养／换队</td><td>安排日程 → 事件与选择 → 人物状态变化 → 新支线／结局</td><td>接单与资源取舍 → 分配搭档 → 任务内干预 → 复盘关系 → 培养与再分配</td></tr>
<tr><td>关系必须改变什么</td><td>支援位置、协同技能、撤退与牺牲的选择</td><td>角色对同一事件的反应、可进入的场景与结局</td><td>信息共享、分工、对承诺的信任、接单边界</td></tr>
<tr><td>重玩来源</td><td>阵容／技能与敌人组合；有真实战术变化</td><td>不同关系视角与路径；避免只补漏文本</td><td>任务并发与资源压力改变同一队伍的合作方式</td></tr>
<tr><td>拟议差异化</td><td>关系提供可选择的战术解法，冲突可协商</td><td>队友之间有自己的关系弧，不只围绕玩家争宠</td><td>玩家的分工与承诺成为关系变化原因，可追溯、可修复</td></tr>
<tr><td>尚未解决的硬问题</td><td>不看故事时，战斗是否仍值得玩？</td><td>不靠悲剧反转时，角色是否仍有吸引力？</td><td>不播放长对白时，派遣决策是否仍有深度？</td></tr>
<tr><td>最大制作负担</td><td>战斗规则、敌人行为、关卡、平衡、战斗反馈与资产</td><td>成体系的剧本、跨场景一致性、演出、分支测试、本地化</td><td>任务决策的变化、可理解的关系状态、经营平衡、信息界面</td></tr>
<tr><td>最坏产品形态</td><td>平庸战棋，夹杂无法跳过的人物对白</td><td>精美立绘配模板化苦难，选择没有反应</td><td>点最强两人出门、等结算、刷好感，直到重复耗尽兴趣</td></tr>
<tr><td>付费交付物</td><td>完整战役、职业构筑、关系系统</td><td>完整故事与人物弧，清晰结局范围</td><td>完整经营战役、队伍成长与有差异的任务解决过程</td></tr></tbody></table>
<p>差异化必须是玩家能感受到的行为差异。将“关系从固定加成变为可追溯的分工与承诺”列为原型假设，是因为它直接回应控制感与叙事一致性的问题；但不能从竞品负评推出我们一定能解决，更不能断言竞品都没有类似设计。{e(6,9,19,25,30)}</p>
<h3>会改变推荐的条件</h3><ul><li>A 的低美术战斗原型获得明显的主动重玩，而 C 的派遣原型被认为只有算数：转向 A，接受更高内容成本。</li><li>B 的角色样章、选择反馈和继续阅读行为明显领先，用户却普遍跳过经营：转向 B，并引入有作品验证的叙事编辑。</li><li>只有美术吸引点击，三种原型都没人愿意继续：停止量产，重新找产品问题，不能靠再加角色挽救。</li></ul>
</section>
'''

body+=f'''
<section id="product"><div class="kicker">06 / 推荐方向需要怎样才成立</div><h2>不是“角色吵架”，而是“合作需要付出什么”</h2>
<p><span class="pill hypothesis">待验证产品定义</span> 一家承接困难委托的小型事务所。固定 8 人，每人有职业能力、价值偏好、当前压力，以及与他人共同经历的记录。玩家用有限人手和预算完成委托，同时决定如何兑现对队员的承诺。具体采用低魔公会、异能事务所还是港口救援题材，留给概念测试；本报告没有足够证据锁定题材。</p>
<div class="flow"><div><b>1. 接单</b><span>报酬、时限、风险与求助理由</span></div><i>→</i><div><b>2. 分工</b><span>能力互补、疲劳、既有矛盾</span></div><i>→</i><div><b>3. 干预</b><span>2–3 个任务节点，选择行动与代价</span></div><i>→</i><div><b>4. 复盘</b><span>报酬、伤势、承诺与关系变化</span></div><i>→</i><div><b>5. 成长</b><span>训练、休息、协商、下一次搭档</span></div></div>
<p>单个任务希望在 5–10 分钟内形成一个有起因、有选择、有结果的小故事；整轮经营持续推进更长人物弧。不要用现实时间倒计时和每日签到制造需求。任务内必须有需要玩家干预的选择，否则“经营”容易变成自动结算菜单。</p>
<h3>一个能够测试的组队难题</h3>
<p>疏散任务需要擅长判断危险的维修师和熟悉现场的向导。维修师坚持先加固，向导主张先救被困者；两人过去因一次迟到救援互相指责。玩家可以分拆任务但多付成本，要求先救人但承担伤势风险，或安排第三人协调但挤占另一张急单。任务中出现新信息，玩家还要决定是否履行出发前“危险超过阈值就撤回”的承诺。</p>
<p>结算不只显示“好感 +5”。它应告诉玩家：谁完成了什么、谁承担了代价、哪项承诺被兑现或违背；下次同类任务有什么新选项。角色可以仍然意见不合，却因为一次可靠合作而更愿意交付关键工作。<strong>喜欢、观点一致和专业信任不应被简单画上等号。</strong>首版只实现一个“合作信任”状态与少量共同经历标签，先不要同时堆五种情绪数值。</p>
<table><thead><tr><th>需要验证的设计</th><th>具体实现边界</th><th>防止的失败</th></tr></thead><tbody>
<tr><td>关系影响选项</td><td>信任足够时可分头行动；信任不足时需联络资源或同行</td><td>所有角色最终都只是几项百分比加成</td></tr>
<tr><td>冲突可预见</td><td>出发前显示已知分歧、触发风险与可干预办法；未知信息只来自合理情境</td><td>无预警吵架、锁技能、突然删掉培养成果</td></tr>
<tr><td>失败能够继续</td><td>任务可部分完成、欠下人情或增加后续代价；关键不可逆后果另设确认</td><td>玩家反复读档、重刷低价值流程</td></tr>
<tr><td>培养改变能力与行为</td><td>专业训练解锁行动；共同任务解锁分工；个人弧改变其可接受的工作边界</td><td>送礼万能、所有人刷满好感就结束</td></tr>
<tr><td>搭档不是固定最优</td><td>同时有不同任务需求、时限与疲劳；相处好仍可能专业能力不适配</td><td>固定最强两人、其他六人长期闲置</td></tr>
<tr><td>系统与文本一致</td><td>每个事件明确触发条件、参与者、承诺与结果；对白读取同一状态</td><td>刚牺牲过仍像陌生人、刚承诺却没有任何后果</td></tr></tbody></table>

<h3>首版内容边界：做少量真正反应，不写所有排列组合</h3>
<p>候选上限：8 名核心角色、每人一条个人弧；重点写 6 对搭档关系弧，其余关系以通用事件和状态反应覆盖。8 人已有 28 对无向组合；如果强制每对独立剧情，内容与回归测试很快失控。任务预计 20–30 个可复用结构、约 60 个短事件、3 个主线阶段与少量结局变体。这些是规模假设，不是已证明足够支撑 8–12 小时的内容量。</p>
<p>先不做程序生成全部人生、每人完整恋爱路线、全员可招募、装备刷词条、建造布局、付费抽卡或全程配音。卡片可以是呈现任务和人物的界面；如果加入牌组构筑，必须证明它改善了决策，而不是为了让产品看起来像“卡牌游戏”。</p>
<h3>悲伤经历怎样转成可玩的故事</h3>
<p>悲惨过去只能解释一个人为何这样行动。每个角色还需要当下目标、能力、普通生活、幽默或可爱之处，以及与别人利益相关的行为。比如失去过同伴的人可能拒绝冒险，也可能过度保护新人；这应表现为任务条件和协商，而不只是解锁一段长独白。不能把所有人都写成等待玩家治愈，也不能让每次亲近都触发死亡来制造眼泪。</p>
<p>写作可以用脚本和数据驱动：事件标识、参与者条件、前置记忆、选择、资源代价、后续标记与对白分开管理。AI 可以协助草稿、条件检查与变体整理，但角色声音、弧线和成稿必须经过一致性编辑。内容质量取决于审稿与修改，不取决于一天生成多少字。Exocolonist 的负面反馈提供了“关系已经成立，但文本仍不响应”的明确风险。{e(11,12,19)}</p>
</section>

<section id="art"><div class="kicker">07 / 美术与呈现</div><h2>2D 是候选制作方式，不是从市场调研得出的唯一答案</h2>
<p>竞品已经覆盖纸片、像素、风格化插画和较重动画；它们证明多种呈现可以售卖，不能证明其中一种画风直接导致成功。本次没有对生成模型做同题测试，因此不能负责任地承诺某个内置模型足以产出整套商用角色资产，也没有依据认定必须换模型。</p>
<table><thead><tr><th>候选方式</th><th>适合的体验</th><th>主要制作问题</th><th>本项目意见</th></tr></thead><tbody>
<tr><td>风格化 2D 肖像／半身像＋有限动作</td><td>面孔、情绪、分工界面与短事件</td><td>同一角色多表情一致、缩小后识别、构图与 UI 配合</td><td>C 最值得先测试；并非已经定稿</td></tr>
<tr><td>像素角色＋小场景</td><td>空间移动、日常活动和清晰的游戏感</td><td>动作帧、方向、轮廓、场景统一；像素并不天然廉价</td><td>若玩家需要看见角色共同工作，作为对照</td></tr>
<tr><td>3D／大量骨骼演出</td><td>强空间存在感与频繁姿态变化</td><td>建模、绑定、材质、镜头、动画和性能形成新制作链</td><td>当前核心玩法尚未证明需要，不作为首版基线</td></tr></tbody></table>
<h3>美术究竟有多重要</h3>
<p><strong>对点击和购买前判断很重要；对关系的识别与理解很重要；单独无法保证留存。</strong>Wildermyth 有玩家先被画风劝退再被口碑带回；Our Adventurer Guild 有用户接受玩法却嫌美术；Exocolonist 也有用户喜欢美术却不满意后期体验。它们是三种不同作用，不能压成“美术重要／不重要”的一个答案。{e(3,11,13,26)}</p>
<p>对于 C，优先级是角色辨识度、状态可读性、统一视觉语言、关键关系场景的情绪表达，再考虑卡面细节密度。对 B，故事与演出一致性更靠前；对 A，战场可读性和行动反馈比高分辨率静态卡图更接近核心体验。三条路线都需要合格的商店胶囊与首屏截图。</p>
<h3>模型、画师怎么选：先验收同一套任务</h3>
<ol><li>用同一角色设定做 2 名角色 × 4 个表情、一个双人互动、一张实际尺寸 UI。比较 AI 辅助方案与画师定稿方案，记录总工时、返工和资产可编辑性。</li><li>统一缩到真实界面尺寸，让目标玩家辨认身份、情绪和职业；再问视觉是否符合游戏气质。大图漂亮但缩小后分不清角色即不合格。</li><li>要求同一角色跨表情保留脸型、服装与标志物，双人接触自然；支持透明分层、后续改姿势和尺寸调整。把“每张需修多久”纳入单价。</li><li>将通过技术验收的两套风格用于同文案概念页，随机分组看点击与继续试玩行为。小样本只筛明显问题，不宣称统计胜出。</li></ol>
<p><strong>当前较稳妥的采购原则：</strong>人类美术负责风格基准、角色定稿、核心情绪场景、商店主视觉和最终验收；AI 是否用于草图或量产辅助取决于一致性与修正成本。预算允许买的是清晰的美术负责制，不是默认增加每张画的细节。委托时取得明确商用授权、源文件与修改范围。是否允许 AI 参与应事先约定。</p>
<p>本项目不含实时生成，但若最终发行的美术、叙事或本地化含 AI 辅助生成内容，仍需按 Steam 内容问卷如实披露；平台把开发效率工具与玩家实际消费的生成内容作了区分。不能因“普通单机”就假设这些规则消失。{s('ai')}</p>
</section>

<section id="cost"><div class="kicker">08 / 制作成本与周期</div><h2>成本按工作拆解，不把“我和 AI”折算成两名全职员工</h2>
<p>AI 可以协助实现、整理和检查，但产品判断、验收、试玩组织、资产整合与发行责任仍需要人承担。以下估算没有预先扣掉某个“AI 提效百分比”。必须先测量一段可玩的内容和一套角色资产的实际耗时，再修订。</p>
<div class="callout"><strong>公开制作锚点：</strong>Our Adventurer Guild 作者称独立开发约 2 年 10 个月，过程中多次改战斗形式、增加内容；Exocolonist 的作者称开发约五年，发行公告列有叙事、美术、音频、QA、移植与发行协作。这不意味着我们必须做同样久，却足以否定“2D 或小团队天然可快速做完”的推断。{s('post','公会复盘')} · {s('exo','Exocolonist 官方公告')}</div>

<h3>工作量估算：完成前述受控范围，而非复制竞品</h3>
<p><span class="pill hypothesis">规划假设，非报价</span> 单位为有效人时，包含我们自己做和外包承担的工作；1 人月按 160 小时换算。没有包含实时 AI、联网后端、主机移植与完整国内出版服务。</p>
<table><thead><tr><th>工作包</th><th>A</th><th>B</th><th>C</th></tr></thead><tbody>
<tr><td>系统设计、原型、数值迭代</td><td>300–500</td><td>200–350</td><td>300–500</td></tr>
<tr><td>程序、工具、存档、UI 逻辑</td><td>650–1,000</td><td>350–600</td><td>500–800</td></tr>
<tr><td>任务／关卡／事件／叙事内容</td><td>400–650</td><td>700–1,200</td><td>350–600</td></tr>
<tr><td>美术、UI 视觉、有限演出</td><td>350–650</td><td>450–850</td><td>250–450</td></tr>
<tr><td>整合、平衡、功能回归、修复</td><td>300–500</td><td>350–600</td><td>300–500</td></tr>
<tr><td>发行准备、页面、试玩、材料</td><td>120–200</td><td>150–250</td><td>120–200</td></tr>
<tr><th>主制作合计</th><th>2,120–3,500</th><th>2,200–3,850</th><th>1,820–3,050</th></tr>
<tr><td>折算人月</td><td>13.3–21.9</td><td>13.8–24.1</td><td>11.4–19.1</td></tr></tbody></table>
<p class="note">独立翻译、母语校对、音乐外包按现金包估列，不假装已换算为上述研发人时；大量返工也可能超出区间。代码生成不等于集成完成，脚本字数不等于可用剧情。没有把 8–12 小时目标直接乘一个通用行业单价。</p>
<p>以 C 为例，如果外包实际承担 500–800 小时主制作工作，创始人仍大约需要 1,020–2,550 小时。若每月可稳定交付 120 小时有效工作，约为 <strong>9–22 个月</strong>，再受人员交接、翻译和返工影响。它不是发布日期承诺；原型计时后可能明显缩短或延长。A/B 不应按“多一个系统只加两周”处理。</p>

<h3>现金预算：先给可讨论的范围，再拿报价替换</h3>
<p>假设程序主体、产品和初稿由我们完成，外部支持集中在美术、编辑、本地化、声音和测试。以下均为<strong>规划预留</strong>，没有向供应商询价，不是市场行情调查结果；差异主要来自资产量与文本量。表中已经包含验证期相关工作，不在总额上再重复加一遍。</p>
{costtable}
<p><strong>考虑预算取整，现金准备区间约为 A 约 19–48 万元、B 约 23–58 万元、C 约 13–34 万元。</strong>不包含创始人生活费、工资、税务差异、成立公司和国内出版服务费用，也不包含大规模买量。这是为商业完成度预留外援的方案；如果自己承担更多美术与编辑，现金可以降低，但总工时和品质风险不会自动消失。</p>
<p>不能把上表现金再加上“所有人时 × 全部外包时薪”，那会重复计算。更完整的经济成本是：<strong>实际现金支出＋创始人未领薪时间的机会成本＋未计入事项</strong>。例如 C 的创始人时间若按 100 元／小时作内部估值，再加约 10.2–25.5 万元；100 元是敏感性参数，不是工资调查结论。</p>

<h3>资产和文本假设，决定报价是否会偏离</h3>
<table><thead><tr><th>制作项</th><th>A</th><th>B</th><th>C</th></tr></thead><tbody>
<tr><td>共同人物基础</td><td colspan="3">8 人基本设定与表情，统一风格、实际 UI 尺寸验收；不要求每人完整多姿势动画库</td></tr>
<tr><td>额外美术工作</td><td>战斗单位、敌人、技能反馈、地形块与关卡</td><td>更多情绪演出与关键场景图，多场景背景</td><td>据点、任务地图、信息图标、少量双人关键场景</td></tr>
<tr><td>预计需编辑／本地化的独立中文文本</td><td>约 8–12 万字</td><td>约 16–26 万字</td><td>约 6–10 万字</td></tr>
<tr><td>最需要索取的实样报价</td><td>一套单位动作＋一场完整战斗</td><td>一段含分支的完整角色事件与演出</td><td>两角色全套表情＋真实任务 UI＋一次关系事件</td></tr></tbody></table>
<p>公开成本参照中，Allcorrect 的英语→简中标价为每英语词 €0.09–0.12，英语语言测试为 €48／小时、简中为 €34／小时。<strong>不能把英语词价直接乘中文字数，也不能当成中译英报价。</strong>它只说明本地化和游戏内测试是独立预算项。我们的中译英预留必须用最终文本、样章风格和测试范围询价校准。{s('loc','服务商公开价格页')}</p>
<p>优先支付小额完整样张／样章委托，要求包含一轮修改、源文件和授权条款；同一任务取得至少两份可比较报价。若人像一致性返工很高，或译文需要接近重写，必须先调整范围，而不是把差额藏进预备金。</p>
</section>

<section id="business"><div class="kicker">09 / 商业模式、平台与发行</div><h2>先以 PC 买断完整体验验证，网页承担试玩和招募</h2>
<p><strong>付费点是完整产品，候选首发价 C 为国区 ¥58–78／美区 $14.99–17.99。</strong>这个区间参考 Our Adventurer Guild 与宇宙之轮姐妹会等邻接产品，但不是支付意愿研究结果。最终价取决于演出、内容完成度、试玩表现和地区测试。A 若战术内容更完整可测试更高价；B 可按故事与演出定位测试，但不能用“字数多”作为加价理由。</p>
<p>首版不做付费抽卡、体力、月卡或按好感卖钥匙。它们会引入角色持续产出、运营和数值公平的新要求，也容易让玩家将关系视为收费障碍。随机招募或事件卡可以是玩法，不必成为现金抽卡。后续付费扩展应交付新的完整事件、角色关系与任务，不把基础故事的关键结尾拆走；原声和美术集只有在真实内容价值足够时才成立。</p>

<h3>需要多少销量才能覆盖投入</h3>
<p>采用“每份实际贡献”做敏感性分析：已经扣除渠道分成、折扣、退款和间接税等、可用于覆盖项目固定投入的平均金额。以下 ¥20／35／50 都是情景输入，不是 Steam 的统一到账规则，也不是从标价直接换算的收入。</p>
<table><thead><tr><th>待回收固定投入</th><th>每份贡献 ¥20</th><th>每份贡献 ¥35</th><th>每份贡献 ¥50</th></tr></thead><tbody>
<tr><td>¥150,000</td><td>7,500 份</td><td>4,286 份</td><td>3,000 份</td></tr><tr><td>¥300,000</td><td>15,000 份</td><td>8,572 份</td><td>6,000 份</td></tr><tr><td>¥500,000</td><td>25,000 份</td><td>14,286 份</td><td>10,000 份</td></tr></tbody></table>
<div class="calculator"><h3>可调整的回收测算</h3><label>待回收投入（元）<input id="budget" type="number" min="0" step="10000" value="300000"></label><label>每份贡献（元）<input id="net" type="number" min="1" step="1" value="35"></label><p id="break-even" aria-live="polite">需要约 8,572 份。</p><small>数量＝投入 ÷ 每份贡献，向上取整。只表示回收要求，不预测能卖多少。</small></div>
<p>一个接近我们的公开案例曾卖到数千份，不代表我们也能达到。若 C 按 30 万元固定投入、每份 ¥35，需要约 8,572 份；这时必须有可信的获客路径与玩家行为证据，否则预算“能接受”也不能成为扩大制作的理由。若把创始人工时和后续维护都计入，回收要求继续增加。</p>
<p>买量更应谨慎：假设一条愿望单最终购买概率为 10%、每份贡献 ¥35，则每条愿望单对应的预期贡献只有 ¥3.5，且尚未回收研发成本。10% 纯属演算假设。拿不到我们自己的转化数据时，不承诺付费获客可盈利。</p>

<h3>平台与开发选择</h3>
<table><thead><tr><th>选择</th><th>建议与理由</th><th>进入条件</th></tr></thead><tbody>
<tr><td>Windows／Steam 客户端</td><td>优先商业版本。竞品与可观察购买证据集中在这里；支持稳定存档、长时体验和试玩转购买路径</td><td>完整试玩、商店资产、功能测试；发行主体与收款资料落实</td></tr>
<tr><td>网页试玩／itch.io</td><td>早期降低招募摩擦；用于短原型，不把浏览量视为购买需求</td><td>保存策略、加载与浏览器兼容可接受；原型与正式版玩法一致</td></tr>
<tr><td>移动端／小程序</td><td>首版暂不进入，不能把 PC 重文本交互直接缩小；尚未研究其获客与付费路径</td><td>PC 需求验证后，另做触屏、会话长度、渠道与合规分析</td></tr>
<tr><td>主机与多平台</td><td>后续可选，不纳入当前销量或成本基线</td><td>稳定商业需求、移植合作与认证资源</td></tr></tbody></table>
<p>若我们没有已验证的 Unity 工作流，C 的原型与客户端可先用 <strong>Godot＋GDScript＋数据驱动事件</strong>。选择依据是 2D／UI 密集、无实时联网、需要桌面与短网页试玩；不是声称 Godot 会使游戏更好卖。Godot 为 MIT 授权，商业发行需保留相应许可；网页导出有 WebGL 2.0 等约束，Godot 4 的 C# 项目目前不能直接网页导出。若用户已有 Unity 工具链和经验，应以实际完成同一原型的成本决定，而不是重学引擎。{s('godot','许可文档')} · {s('web','网页导出文档')}</p>

<h3>中文用户与中国大陆正式发行，是两项不同决策</h3>
<p>建议首版计划简体中文与英文，以实际玩家反馈决定是否扩语种。本次中文商店与评测样本证明值得覆盖中文体验，但不能推出特定地区的销售份额，也不能把 Steam 国际商店存在当作完成国内出版手续。</p>
<p>若面向中国大陆正式出版运营，需要与合适出版／运营主体落实路径。国家新闻出版署办事指南把网络下载单机列入相关申报类型，并列出出版单位、运营资质与材料条件；写明的 80 个工作日自受理起算，不是从现在到拿到版号的承诺。当前预算未含此服务与可能的内容调整成本，不预估一个未经报价的包办金额。国际发行同样要落实主体、税务、资产授权与平台内容规则。{s('nppa','国家新闻出版署办事指南')}</p>
<p>Steam Direct 公开列出每个产品 $100 费用，以及新产品从付费到发行至少 30 天、商店“即将推出”至少两周等流程要求。它们只是发行准备的一部分，不能把上架手续费当作发行预算。{s('direct')}</p>

<h3>宣发要卖实际冲突，不卖抽象功能表</h3>
<ol><li><strong>定位素材：</strong>先做一段能完整看懂的 30–60 秒任务。观众看到“为什么派这两人—他们在哪分歧—我怎样处理—之后怎样变”，而不是只看角色轮播。</li><li><strong>中文与英文各自测试：</strong>中文测试组队取舍、职场群像和养成三个切入文案；英文也分别测“team management”“character relationships”“choices with consequences”对应素材。不预设两个语言市场购买动机相同。</li><li><strong>小规模创作者适配：</strong>根据最近实际覆盖的相邻游戏和观众反馈筛人；提供可玩的短版本、明确系统亮点与使用素材。长篇叙事有剧透风险，演示重点放在可变化的任务选择。</li><li><strong>Steam 试玩活动：</strong>在试玩能独立交付核心乐趣后参加合适活动；不为了赶最近一期活动把临时原型当产品承诺。不以“有 7,000 或 10,000 愿望单”作为自动成功标准。</li><li><strong>持续内容：</strong>展示新的两难决定、不同队伍结果和开发中改掉的问题，观察用户是否愿意讨论选择及继续试玩。不要只发“今天又画了一张卡”。</li></ol>
<p>Steam 官方说明，购买与游玩等响应影响曝光；愿望单除部分展示位置外通常不是算法曝光因素，访问量本身也不会自动提升推荐。UTM 能追踪一定条件下的访问及 72 小时内转化，但有登录和归因限制。我们要记录分渠道成本与行为，而不是承诺流量可以换取平台推荐。{s('visibility','官方曝光说明')} · {s('utm','归因说明')}</p>
</section>

<section id="validation"><div class="kicker">10 / 下一阶段的决策门槛</div><h2>现在应该投入验证，不应该先购买整套角色资产</h2>
<p>以下为研究后的行动建议，尚未执行。第一轮现金上限建议 <strong>1.5–4.5 万元</strong>，主要用于小份美术／编辑实样、玩家招募与必要外援；内部工作先控制在约 <strong>180–320 小时</strong>，超出就重估。这部分属于上面的总预算范围。若我们自己完成更多原型，现金可下降，但不能省去陌生目标用户的行为验证。</p>
<table><thead><tr><th>阶段</th><th>做什么</th><th>要解决的问题</th><th>继续／停止依据</th></tr></thead><tbody>
<tr><td>1. 购买动机访谈</td><td>12 位实际买过相邻游戏的人，按 A/B/C 动机各约 4 位；中文／英文均覆盖</td><td>最近一次为什么买、玩到哪停、愿意为下一款牺牲什么时间</td><td>只谈抽象“喜欢故事”却找不到购买行为时，不能确认人群。小样本只发现问题，不估算比例。</td></tr>
<tr><td>2. 三方向同规格纸面／低保真原型</td><td>同一组角色与处境，各 15–20 分钟核心选择；控制美术质量和介绍长度，轮换体验顺序</td><td>战术、叙事、经营哪种任务本身使人想继续</td><td>记录主动选择、停顿、退出和继续行为；喜欢精美概念图不算玩法胜出。</td></tr>
<tr><td>3. 优胜方向可玩切片</td><td>先按 C 规划：4 人、3 对重点关系、一个完整短经营周期、至少两种后续结果</td><td>关系真的影响选择，还是仅是文字装饰</td><td>引入无关系影响的对照版本；关系版若只增加阅读与挫败，修改或放弃。</td></tr>
<tr><td>4. 美术与写作生产验证</td><td>两人表情包、双人场景、真实 UI；一条完整关系弧及英文本地化</td><td>质量、返工、每单位实际工时，是否承担得起量产</td><td>角色不一致、难改、文本必须重写，先换制作方案；不靠累计废稿证明进度。</td></tr>
<tr><td>5. 外部试玩与价格</td><td>至少 20 位非熟人目标用户测试修订后的切片，记录完成、主动继续、再次返回；随后做真实价格呈现</td><td>是否值得买、可接受何种完成规格</td><td>区分口头意愿、愿望单与真实购买；尚未开放付费时，不能声称通过付费验证。</td></tr></tbody></table>
<h3>给 C 的临时验收标准</h3>
<p>以下只是项目内部提前约定的方向判断门槛，不是行业均值，也不构成统计显著性：20 位目标用户中，希望至少 14 位无需开发者救场完成核心循环，至少 12 位能准确复述某次分工如何影响关系，至少 10 位在不被催促的情况下选择继续一个额外任务。另记录 48–72 小时后是否有人主动返回、能记住谁和谁发生了什么，以及是否只是冲着奖励点击。小样本的偶然波动很大，接近边界时扩样或重测，不能硬判。</p>
<p><strong>对照最重要：</strong>不只问“好不好玩”，还要比较同一任务在“关系不影响行动”和“关系改变行动”两版里的选择与感受。若玩家不理解差异，关系系统没有被验证；若只把任务变难，则需要证明新增策略与情感价值超过成本。</p>
<h3>完整量产前还缺哪些证据</h3>
<ul><li><strong>目标人群：</strong>哪一组实际购买过相邻作品的人最愿意继续，中文／英文是否不同。</li><li><strong>核心乐趣：</strong>不依赖豪华美术和大量新剧情，短流程能否成立。</li><li><strong>内容可持续：</strong>第二、第三个周期仍有新决策，不能只凭前 20 分钟好评。</li><li><strong>生产能力：</strong>角色资产、事件、翻译与功能回归的实测工时及外包报价。</li><li><strong>商业路径：</strong>真实商店素材带来的合适用户、试玩表现与价格反馈，能否支撑回收要求。</li></ul>
<p><strong>停止条件：</strong>两轮针对性修改后，玩家依旧把关系当作随机惩罚，或普遍希望跳过它；内容必须不断大量新增才能维持几分钟兴趣；主要兴趣来源与我们的可交付规格不匹配；单位内容成本超预算且缩范围后失去购买理由。遇到这些情况，应暂停该方案或转向被行为支持的方向，不能靠更精美的立绘掩盖。</p>
<div class="callout finalcall"><strong>最终建议：</strong>现在批准 C 的验证投入，同时保留 A/B 的对照；不要批准完整生产预算。公开资料支持我们认真尝试“关系改变协作决策”的产品，也清楚提示它不是空白赛道。正式立项应在核心循环、人物吸引力与生产成本三项都得到自己的证据之后。</div>
</section>
'''

body+='''<section id="evidence"><div class="kicker">附录 A / 可追溯玩家证据</div><h2>定性摘读记录</h2><p>以下均为转述，没有复制完整评论。推荐／不推荐是原作者对当时游戏整体的判断，不等于只赞同或只反对表中一点。日期沿用采集页面的显示形式；不带年份的日期不擅自补年。包含早期访问与历史版本；本报告未进行现版本复测。鉴赏家、长时间玩家与主动写评测者各有选择偏差。</p><div class="tablewrap"><table class="evidence"><thead><tr><th>证据 / 游戏 / 日期</th><th>个体体验转述</th><th>设计启示（本报告推论）</th></tr></thead><tbody>'''
for r in evidence:
 body+=f'<tr id="{r["id"]}"><td><a href="{esc(r["url"])}" target="_blank" rel="noopener">{r["id"]} · {esc(r["game"])}</a><small>{esc(r["date_as_displayed"])}<br>{esc(r["recommendation"])} · {esc(r["hours_as_displayed"])}</small></td><td>{esc(r["observation"])}</td><td>{esc(r["implication"])}</td></tr>'
body+='</tbody></table></div></section>'
body+='''<section id="sources"><div class="kicker">附录 B / 来源与数据附件</div><h2>原始事实可以复核，判断可以推翻</h2><p>竞品数据链接在正文表格；玩家证据链接在附录 A。下面列出开发者复盘、采访和平台文档。报告旁附 <a href="research-evidence.json">research-evidence.json</a>，保留中美商店返回字段、33 条评测的转述与链接、候选评测元数据和预算参数；不包含玩家评论全文。浏览器也可将本页打印为 PDF。</p><ol class="source-list">'''
for k in sources:body+='<li>'+s(k)+'</li>'
body+='''</ol><p class="note">仍缺少：去重购买用户规模、竞品净利润、当前版本实玩对照、真实玩家访谈、可归因获客数据、画师与本地化实样报价。这些缺口限制收益预测，不妨碍当前优先验证路线的选择。整个推荐没有使用未经披露的竞争对手后台数据，也没有把宣传标签当作已验证玩法效果。</p></section><footer>研究快照：2026-10-30 · 产品决策研究，不是销量保证 · 所有预算与验收线均可在实测后修订</footer>'''

css='''
:root{--ink:#172b35;--muted:#5e6f76;--paper:#f4f5ef;--line:#d9e0d9;--accent:#12695b;--soft:#e5efea;--amber:#8a5b1e}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:70px}body{margin:0;background:var(--paper);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.85}main{max-width:1180px;margin:auto;padding:0 36px}header{padding:70px 0 36px;border-bottom:2px solid var(--ink)}.eyebrow,.kicker{font-size:12px;font-weight:700;letter-spacing:.12em;color:var(--accent)}h1{font-size:clamp(30px,4.8vw,54px);line-height:1.25;letter-spacing:-.035em;margin:22px 0}h2{font-size:28px;line-height:1.5;letter-spacing:-.02em;margin:12px 0 24px}h3{font-size:20px;line-height:1.5;margin:30px 0 12px}p{margin:14px 0}.lead{font-size:20px;line-height:1.8;color:var(--muted);max-width:850px}.badges{display:flex;flex-wrap:wrap;gap:8px;margin-top:26px}.badges span,.pill{font-size:12px;background:var(--soft);padding:4px 10px;border-radius:4px}.pill.hypothesis{color:var(--amber);background:#f5ead6}.pill.inference{background:#e6eaf5}nav{display:flex;gap:16px;flex-wrap:wrap;padding:18px 0;border-bottom:1px solid var(--line);font-size:13px}a{color:var(--accent);text-underline-offset:3px;text-decoration-thickness:1px}a:hover{color:#063d35}section{padding:50px 0;border-bottom:1px solid var(--line)}.callout{background:#e5efea;border-left:4px solid var(--accent);padding:20px 24px;margin:24px 0}.three{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:28px 0}.three article{padding:22px;background:#fff;border:1px solid var(--line);border-radius:8px}.three article.recommended{border-color:var(--accent);background:#edf5ef}.three h3{margin:12px 0;font-size:20px}.three p{font-size:14px}.rank{font-size:11px;color:var(--muted);letter-spacing:.14em}table{width:100%;border-collapse:collapse;font-size:14px;margin:22px 0;line-height:1.65;background:#fff}th{text-align:left;background:#e7ede8;font-weight:650}td,th{padding:13px 14px;border:1px solid var(--line);vertical-align:top}td small{display:block;color:var(--muted);font-size:12px;margin-top:8px}.tablewrap{overflow-x:auto}.competitors{min-width:920px}.competitors td:first-child{width:20%}.competitors td:nth-child(2),.competitors td:nth-child(3){width:15%}.competitors td:nth-child(4){width:16%}.evidence td:first-child{width:29%}.evidence td:nth-child(2){width:36%}.note{font-size:13px;color:var(--muted)}.eref{font-size:12px;font-weight:bold;white-space:nowrap}.flow{display:flex;align-items:center;gap:8px;margin:26px 0}.flow div{background:var(--soft);padding:15px;flex:1;min-height:112px;border-radius:6px}.flow b{display:block;font-size:15px}.flow span{display:block;font-size:12px;color:var(--muted)}.flow i{font-style:normal;color:var(--accent)}li{margin:10px 0}ul,ol{padding-left:26px}.calculator{padding:24px;border:1px solid var(--accent);border-radius:8px;background:white}.calculator h3{margin-top:0}.calculator label{display:inline-flex;flex-direction:column;gap:5px;margin-right:26px;font-size:13px}.calculator input{font:inherit;font-size:18px;width:200px;padding:9px;border:1px solid var(--line);border-radius:4px}.calculator p{font-size:25px;font-weight:bold;color:var(--accent);margin-bottom:4px}.calculator small{color:var(--muted)}.source-list{font-size:13px}.finalcall{font-size:18px}footer{font-size:12px;color:var(--muted);padding:35px 0 60px}
@media(max-width:760px){main{padding:0 18px}header{padding-top:38px}h2{font-size:24px}.lead{font-size:17px}.three{grid-template-columns:1fr}.flow{flex-direction:column;align-items:stretch}.flow div{min-height:0}.flow i{text-align:center;transform:rotate(90deg)}section{padding:34px 0}table{font-size:12px}td,th{padding:10px 8px}.calculator label{display:flex;margin:10px 0}.calculator input{width:100%}}
@media print{body{background:white;font-size:10pt;line-height:1.65}main{max-width:none;padding:0}header{padding:12px 0 20px}h1{font-size:30pt}h2{font-size:18pt}h3{font-size:13pt}section{padding:20px 0}nav,.calculator{display:none}table{font-size:8pt;line-height:1.5}td,th{padding:7px}.tablewrap{overflow:visible}.competitors{min-width:0}.callout,article,tr{break-inside:avoid}a{color:#12695b}.three{gap:8px}.three article{padding:12px}.three p{font-size:9pt}.note,small{font-size:8pt}.flow div{padding:8px;min-height:0}.flow span{font-size:8pt}.eyebrow,.kicker{font-size:8pt}.badges span{font-size:8pt}@page{size:A4;margin:16mm 13mm}
'''
js='''function calc(){const b=Number(document.getElementById('budget').value),n=Number(document.getElementById('net').value);document.getElementById('break-even').textContent=n>0&&b>=0?'需要约 '+Math.ceil(b/n).toLocaleString('zh-CN')+' 份。':'请输入有效的投入与正数贡献金额。'}document.querySelectorAll('.calculator input').forEach(x=>x.addEventListener('input',calc));calc();'''
report='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>角色关系游戏立项调研｜三方向比较与立项建议</title><style>'+css+'</style></head><body><main>'+body+'</main><script>'+js+'</script></body></html>'
(OUT/'game-project-research.html').write_text(report)

candidates={}
for page in corpus:
 for r in page.get('reviews',[]):
  if r['url'] not in candidates:candidates[r['url']]={k:v for k,v in r.items() if k!='text'}|{'game':page['name'],'appid':page['appid'],'sampled_on_pages':[]}
  candidates[r['url']]['sampled_on_pages'].append(page['kind'])
data={'as_of':'2026-10-30','method':'Purposive desk research, not a representative survey. 16 paired regional store snapshots, plus Dispatch as an adjacent benchmark in the report. 36 review pages × first 5 rendered cards; 180 appearances / 173 unique candidate permalinks. 33 selected qualitative summaries. No interviews or playtests conducted.','sources':sources,'store_snapshots':markets,'selected_review_evidence':evidence,'candidate_review_metadata':list(candidates.values()),'cash_budget_unit':'CNY 10,000; planning assumptions, not vendor quotes','cash_budget_rows':cost_rows,'cash_budget_totals':costs,'research_limitations':['Review counts are not sales; review language is not buyer country.','Prices are regional snapshots; discount and lifetime cohorts differ.','Historical reviews were not tested against current builds.','No verifiable deduplicated audience size, forecast sales, or project purchase intention.']}
(OUT/'research-evidence.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
print(json.dumps({'html':str(OUT/'game-project-research.html'),'characters':len(report),'selected_reviews':len(evidence),'unique_candidate_reviews':len(candidates),'costs':costs},ensure_ascii=False,indent=2))

