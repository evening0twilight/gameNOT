"""Evidence, rejected claims, current scope and capacity limits in one review."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
def load(n):return json.loads((O/n).read_text())
M=load('cooperation-value-matrix.json');F=load('cooperation-frontier-challenge.json');A=load('cooperation-value-campaign.json');K=load('cooperation-equal-training-controls.json');C=load('cooperation-current-campaign.json');V=load('cooperation-current-matrix.json');S=json.loads((D/'production_scope.json').read_text());P=load('cooperation-focused-ordinary.json')
def e(v):return html.escape(str(v))
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(v)+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>'
BOARDS={b['id']:b for b in json.loads((D/'boards.json').read_text())['boards']}
def goal_names(mid,ids):
 labels={o['id']:o['label'] for o in BOARDS[mid]['objectives']}
 return '、'.join(labels.get(k,k) for k in ids)
parts=[]
def add(s):parts.append(s)
add('<p class="eyebrow">夜潮事务所 · 0.12 · 2026-11-02 · 仅设计及离线推演</p><h1>合作有用，不等于值得单独培养</h1><div class="note"><b>本轮决定：</b>撤销独立高级合作养成分支，保留四项情境协作。人物培养收敛到每人两项专长及已有被动；5级强化第一专长次数。正式范围由24项专长／12种装备缩到16项／7种。36关、人物线、关系责任与失败到结局规则保留。没有改Godot运行代码。</div>')
add('<nav>'+''.join('<a href="#'+a+'">'+b+'</a>' for a,b in [('routes','反例与替代路线'),('cost','培养成本'),('decision','实际修改'),('capacity','两人制作范围'),('validation','36关与整局复核')])+'</nav>')
add('<h2 id="routes">先推翻弱论据，再决定是否保留养成系统</h2><p>0.11只有指定接力路线与较弱普通路线的对照，不能说明投资价值。本轮普通方案主动搜索任务归属、顺序、关停、攻击、交接与角色专长；合作获得同样的任务分工候选，以及接力和重机牵引计划。没有改档案期限、削弱普通搬运或把某个阵容设为通关钥匙。</p>')
rows=[]
for mid in ['M06','M08']:
 q=next(r for r in P if r['mission']==mid)
 rows.append([mid,'三人分工，不用高级合作',q['rounds'],q['damage'],q['ap'],goal_names(q['mission'],q['secured'])])
old=load('player-choice-witnesses.json')
for key in ['relay','pull_without_added_wait']:
 q=next(x for x in old if x['witness_name']==key);rows.append([q['mission'],'0.11指定合作路线（旧对照）',q['rounds'],q['damage'],q['ap'],goal_names(q['mission'],q['secured'])])
add(table(['关卡','路线','轮数','伤害','AP','成果'],rows))
add('<p>M06的普通分工把档案、老人、儿童分别交给三人，6轮全部送达。林／许／苏、林／许／陈、林／苏／陈、许／苏／陈四种当时可用阵容都找到6轮、0伤害、32AP的普通路线。无需专长或装备。M08四组早期阵容均找到10轮、0伤害、30AP的普通路线，同时拿到备用线；旧牵引路线用了12轮且没有这个额外成果。边界位置的牵引几何仍成立，但不能再拿它代替完整关卡的投资论据。</p>')
add(table(['搜索层次','实际范围','结论及限制'],[
 ['36关扩展比较',str(M['cases'])+'具名配置／'+str(M['trials'])+'次策略尝试','46种主目标选择、全部按加入日期可用的三人组合；固定出生顺序、章节等级、标准难度／天气A。合作伙伴假定达到60信任，属于能力上限试验，不是已付清的养成成本。'],
 ['普通路线再次挑战',str(F['trials'])+'次，复查71个配置留下的76条合作候选','提高任务归属搜索密度；不买工具与已拥有担架分开。担架实际需24资金＋2零件，M16后才可购买。'],
 ['成果层面的差异','采样中未找到合作独有的获救／取证成果集合','未证明所有普通路线最优，也未证明合作永远无用。'],
 ['仍保留的合作优势','最终留下10条S09候选','9条为相同成果、伤害、AP下由6轮变5轮；1条是同为5轮时少1AP。只是一关的效率优势，不能据此承诺整局都值得培养。']]))
add('<p>重新分类了贺鸣的安全搬运：它是已经取得的角色专长，不是购买担架。比较“未买装备”的普通路线时保留它，否则会人为压低普通阵容表现。掩护、现场值守不是本轮高级培养价值矩阵的主目标；四种现场操作在当前版本另行回归。</p>')
add('<h2 id="cost">把成长本身与合作解锁拆开比较</h2><p>旧方案没有额外协议费用，但仍占1个营地项目、两名角色当晚安排、2物资，并让两人各增加8疲劳、取得3经验。初始28种人物对中仅林岚／苏棠、苏棠／江朔、陈砚／莫遥3对双向信任达到门槛；还必须等待人物加入。其余组合不能假装训练一次就自动满足信任。</p>')
camp_rows=[]
for s in A['scenarios']+K['scenarios']:
 q=s['summary'];camp_rows.append([q['name'],str(q['main_count'])+'／'+str(q['side_count']),q['training_bundles'],sum(r['kind']=='training' for r in s['receipts']),sum(q['xp'].values()),q['resources'],sum(r['kind']=='advanced_actions_used' for r in s['receipts'])])
add(table(['完整战役策略','主／支线','学会的搭档组合','训练次数','总经验','剩余资源','实际使用高级动作的任务数'],camp_rows))
add('<p>三组处理为：普通安排；优先培养实际满足条件的搭档且允许高级动作；完全相同的搭档培养但禁用高级动作。每项都运行固定偏好、轮换、最高难度和连续失误四种完整战役。未人为增加信任、人物等级或库存。战术候选使用事后比较，不能视为真人游玩胜率。</p>')
differences=[]
for s in A['scenarios']:
 if not s['summary']['name'].endswith('_cultivate'):continue
 prefix=s['summary']['name'].removesuffix('_cultivate');control=next(x for x in K['scenarios'] if x['summary']['name']==prefix+'_trained_no_actions')
 fields=['resources','xp','world_ending','character_endings','withdrawn','main_count','side_count'];same=all(s['summary'][k]==control['summary'][k] for k in fields)
 differences.append([prefix,'一致' if same else '存在差异，详见账本',sum(r['kind']=='advanced_actions_used' for r in s['receipts'])])
add(table(['相同培养的反事实','资源／经验／结局／离队结果','实际高级动作任务数'],differences))
add('<p>修正过一次比较偏差：准备牵引时，先关停机器、移动站位有时就找到了更好的普通路线，即使最终没有牵引。现在这些合法的关停和站位候选同时给普通组，不能把搜索器发现的路线算成高级动作的贡献。培养分配改变经验、疲劳、出勤与故事机会，净成本必须看账本，不能把所有搭档训练都当额外损失，也不能把一般成长收益记成合作收益。</p>')
add('<h2 id="decision">修改的是产品结构，不是继续降价推销弱奖励</h2>')
add(table(['项目','0.12当前规则','为什么这样改'],[
 ['独立高级合作培养','删除合作技能树、人物对学习标记、统一60信任解锁及跌破阈值失效','当前证据不足以支持一个独立养成理由；不靠限制普通路线制造需求'],
 ['接力／牵引／保护／掩护','保留为情境协作，沿用距离、AP、路径、次数与具体关系保障','局部有用时玩家可以用；它们不再承担“投入培养必有回报”的宣传'],
 ['人物成长','每人保留1级、3级两项专长；5级将第一专长每任务次数2→3','不新增第三种动作和三选二配装分支。培养回报是该人物已有专业能力更可靠'],
 ['关系成长','保留责任记忆、具体承诺、风险边界和履约修复','不是刷满信任换战斗许可证；有具体旧怨时仍需要真实保障，等级不能绕过'],
 ['装备','保留撬棍、医疗包、锚点、屏障、绝缘垫、停机探针、担架','移除泡沫、电池、诱导信标、切割器、灭火器的制作和购买入口；没有任务要求这些工具才能过'],
 ['提示','协作放在目标的情境菜单，显示当前位置／搭档／保障要求','不追加养成教程或合作经验条，避免把可选操作变成玩家的待办清单']]))
add('<p>移除的是培养分支而非人物关系。比如涉及坠落风险的危险合作，林岚仍可能要求锚点或第三人保护；玩家可落实保障、换合作对象，或用基础行动完成目标。曾经发生的失约和实际补救仍由同一事件账本结算，不因协作开放而清零。</p>')
add('<h2 id="capacity">战斗已经偏重：能写算法，不等于两人已能交付整套体验</h2><p>当前仓库的正式工程仍主要是数据加载与基础领域模块，完整Godot战役、战术界面和展示尚未完成。本轮没有继续堆战斗机制。二维小棋盘也不天然代表小项目：Matthew Davis的GDC复盘简介明确写到《Into the Breach》开发历时四年，并经历多年内容删减与迭代；这只能说明范围控制的重要性，不能拿来估算我们的工期。<a href="https://gdcvault.com/play/1025772/-Into-the-Breach-Design">开发者GDC复盘简介</a></p>')
add(table(['制作层','实际工作和当前边界','如何控制'],[
 ['规则实现','移动、目标、机器预告、伤势、道具与关系条件的交叉结算；离线已可执行，Godot整合未完成','一个状态转换同时驱动预览与执行；确定性网格，不依赖实时物理'],
 ['界面与输入','选目标／搭档／路径、显示后果、失败解释、键鼠操作；目前没有完整产品界面','目标情境菜单，显示适用动作；不另造合作养成页或第三专长配装页'],
 ['存档与结算','跨关保存、读取后预告一致、资源和关系只结算一次','只在稳定阶段保存；稳定事件ID；不能用Python通过替代正式引擎回归'],
 ['人物与表现','8人立绘与表情、棋盘标记、通用移动和命中特效、剧情文本与声音','2D插画＋棋盘表现；不承诺高质量3D建模、逐角色骨骼战斗动画或大量专属合击演出'],
 ['关卡内容','36关目标、布局、前置、4种现场操作和人物剧情衔接','复用已经定义的目标／机器模板；新机制必须替换旧机制，不能无限累加'],
 ['最终质量','新手理解、提示遮挡、读字压力、存档损坏恢复与目标设备兼容','这些必须在同一个最终产品中验收；当前不能给出已经通过或可靠完成日期的保证']]))
add('<p><b>能力判断：</b>收敛后的单机2D确定性方案有明确实施路径，我可以承担规则、工具、数据、界面代码和自动检查；你需要参与产品取舍、素材审美、实际游玩与目标设备验收。但“我们已经能稳定交付原来所有战斗细节”没有依据。当前不要求雇人，也不把未发生的专业支持写成已解决；若未来某项表现达不到标准，先调整范围，再讨论额外支持。暂不开始这些开发工作。</p>')
add('<h2 id="validation">新规则重新放回36关与整局</h2>')
add(table(['复核','当前结果','边界'],[
 ['具名配置',str(len(V['rows']))+'组全部找到基础解法','沿用旧方案的强普通路线，并比较当前协作候选；不是全序列穷举'],
 ['难度／天气',str(len(V['baseline']))+'组全部找到基础解法','固定初始三人、1级、不用装备与专长；只保证采样主目标基础路径'],
 ['当前完整战役',str(len(C['scenarios']))+'条／'+str(C['actual_battles'])+'场实际参考战斗','使用0.12专长次数、装备范围、真实资源与加入日期；无协议学习标记'],
 ['关系与可选现场','见定向检查记录','低信任不再一刀切禁用；具体冲突仍生效；四处操作沿用物理前置和期限'],
 ['正式开发','运行文件哈希保持不变','没有把参考推演当成可发布游戏']]))
add(table(['当前战役','主／支线','资源','永久医疗离队人数','合作学习标记'],[[s['summary']['name'],str(s['summary']['main_count'])+'／'+str(s['summary']['side_count']),s['summary']['resources'],len(s['summary']['withdrawn']),len(s['summary']['trained_protocols'])] for s in C['scenarios']]))
add('<h3>36关逐项回填</h3><label>筛选 <input id="filter" placeholder="输入M06或S09"></label>')
rows=[]
for m in M['maps']:
 r=[x for x in V['rows'] if x['mission']==m['mission']];rows.append([m['mission'],m['cases'],m['ordinary_success'],m['frontier_cases'],m['qualitative_cases'],str(sum(x['success'] for x in r))+'/'+str(len(r))])
add(table(['关卡','旧方案比较配置','普通路线成功配置','初次保留合作候选的配置','采样合作独有成果配置','当前范围基础解法'],rows))
add('<p>本轮能够否定旧的单案例论据、定位残留局部价值、核对真实培养成本，并缩小实施范围。不能据此宣布所有组合平衡、玩家一定喜欢或商业可行。最终的可玩性感受还需真人在正式产品中验证。</p>')
links=[('full-game-design.html','完整设计'),('cooperation-value-matrix.json','扩展路线矩阵'),('cooperation-frontier-challenge.json','更强普通路线复查'),('cooperation-value-campaign.json','培养整局账本'),('cooperation-equal-training-controls.json','相同培养控制组'),('cooperation-current-matrix.json','当前规则矩阵'),('cooperation-current-campaign.json','当前整局'),('cooperation-current-checks.json','定向检查'),('../game/data/final_design/production_scope.json','正式制作范围')]
add('<footer>'+ ' · '.join('<a href="'+f+'">'+s+'</a>' for f,s in links)+'</footer>')
style='<style>*{box-sizing:border-box}body{margin:0;background:#edf2ef;color:#203d43;font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1280px;margin:auto;padding:44px;background:white}h1{font-size:36px}h2{margin-top:46px;padding-top:18px;border-top:3px solid #0a8072;font-size:25px}.note{padding:22px;background:#e7f3eb;border-left:4px solid #0a8072}nav{display:flex;gap:22px;flex-wrap:wrap;margin:26px 0}a{color:#087b6c}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px;margin:22px 0}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #d5e1da;min-width:90px}th{background:#eef5f0}.eyebrow,footer{font-size:13px;color:#536b70}input{font:inherit;padding:7px}footer{margin-top:38px}@media(max-width:760px){main{padding:20px}}</style>'
body='\n'.join(parts);script='<script>document.querySelector("#filter").addEventListener("input",function(){const t=document.querySelectorAll("table");for(const r of t[t.length-1].querySelectorAll("tbody tr"))r.hidden=!r.textContent.toLowerCase().includes(this.value.toLowerCase());});</script>'
(O/'cooperation-value-review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>高级合作价值与制作范围0.12</title>'+style+'<main>'+body+'</main>'+script+'</html>')
(O/'cooperation-value-section.html').write_text('<section id="cooperation-value-review"><h2>高级合作价值与制作范围 · 0.12（当前）</h2><p>更强普通分工推翻M06接力的旧优势论据。取消独立合作养成树、人物对学习和统一60信任门槛；四项协作保留具体关系条件。正式范围为16项专长、7种装备，5级强化第一专长次数。旧0.11报告是历史对照，不能继续执行其培养门槛。36关及完整战役按新规则另行复核。</p><p><a href="cooperation-value-review.html">查看普通路线、培养控制组、当前复核与两人制作范围</a></p></section>')
print('Built cooperation-value-review0.12')
