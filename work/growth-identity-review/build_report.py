from pathlib import Path
import json,html,collections
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
def load(f):return json.loads((O/f).read_text())
def esc(x):return html.escape(str(x))
def table(h,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in h)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>'
M=load('growth-identity-matrix.json');F=load('growth-identity-field.json');P=load('growth-identity-ports.json');C=load('growth-identity-campaigns.json');T=load('growth-identity-selective-campaigns.json');V=load('growth-identity-checks.json');PRE=load('growth-identity-pre-upgrade.json');G=json.loads((D/'growth_identity_contract.json').read_text());boards=json.loads((D/'boards.json').read_text())['boards'];names={c['id']:c['name'] for c in json.loads((ROOT/'game/data/characters.json').read_text())}
rows=M['rows'];gg=[r for r in rows if r['growth_gain']];meaningful=sum(r['states']['L5_specialists']['rounds']<r['states']['L3_specialists']['rounds'] or r['states']['L5_specialists']['damage']<r['states']['L3_specialists']['damage'] for r in gg)
css='''*{box-sizing:border-box}body{margin:0;background:#edf1ee;color:#20363a;font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1180px;margin:auto;padding:48px;background:white}h1{font-size:37px;line-height:1.35}h2{font-size:25px;margin-top:52px;border-top:2px solid #1b817a;padding-top:24px}h3{font-size:20px;margin-top:28px}p{margin:15px 0}a{color:#086f6b}.kicker,.muted{font-size:14px;color:#587078}.note{background:#e8f3ee;border-left:4px solid #1b817a;padding:18px 22px}.warning{background:#fff3dc;border-color:#ae782b}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:12px;vertical-align:top;border-bottom:1px solid #d5dfdc;min-width:90px}th{background:#ecf2ee}details{border:1px solid #d5dfdc;padding:16px;margin:18px 0;border-radius:8px}summary{cursor:pointer;font-weight:650}.grid{display:grid;grid-template-columns:410px 1fr;gap:28px}.statrow{display:flex;gap:16px;flex-wrap:wrap}.stat{padding:16px 24px;background:#f1f6f2;flex:1;min-width:180px}.stat b{display:block;font-size:28px}.board{width:100%;max-width:410px}nav{display:flex;gap:20px;flex-wrap:wrap;margin:24px 0}code{font-family:ui-monospace,monospace;background:#edf4ef;padding:2px 4px}footer{margin-top:45px;font-size:13px;color:#587078}@media(max-width:760px){main{padding:23px}h1{font-size:29px}.grid{display:block}}'''
parts=[]
def add(s):parts.append(s)
add('<section id="growth-identity-review"><p class="kicker">0.13 · 2026-11-02 · 仅设计与离线推演，未进入正式开发</p><h2>战斗形式、人物成长与阵容价值复审</h2>')
add('<div class="note"><b>当前决策：俯视2D空间战术救援。</b>固定8×8棋盘、3人出勤、每人每轮2AP，我方可以交错行动；之后结算已预告的机器与环境。剧情用角色立绘。人物成长改变现场可做的动作；装备提供通用解决办法。角色关系保留责任、边界和后果，并增加可选择的共同安排。</div>')
add('<p>这次发现的关键问题不是“删少了”：旧版五级加一次使用次数在这批路线中没有收益；叶禾与陈砚的早期作用重复；只教玩家修复关系会让关系像负担；频繁带教与无脑改派接应还会浪费投入。下文区分已经改动、实际复核结果和仍未获证实的吸引力，不把脚本通关当作玩家愿意购买或重玩。</p>')
add('<nav><a href="#form">战斗与表现</a><a href="#growth">培养价值</a><a href="#parties">阵容实证</a><a href="#positive">关系的正向用途</a><a href="#campaign">整局比较</a><a href="#coverage">36关覆盖</a><a href="#limits">证据边界</a></nav>')
add('<h3 id="form">先定战斗形式，再定装备和资产</h3>')
add(table(['形式','保留/失去什么','本项目决定'],[
 ['俯视2D格子回合','保留路径、站位、搬运接力、供电与撤离；需要可读棋子和通用动作反馈','采用。人物不会只在两排头像之间互相扣血。'],
 ['2D卡片战斗','插画资产便利，但若以抽牌打伤害为主，要另建抽牌、牌库和卡池平衡；不自动保留现场空间选择','不用作主战斗。角色资料卡只是界面形式。'],
 ['3D站位阵列回合','能展示人物模型；自由路线和现场操作要重写为抽象选项','不采用。与这36关依赖的空间操作不一致。'],
 ['3D格子战术','保留空间玩法；额外要处理模型、材质、导入、镜头、遮挡与战斗表现','现阶段不采用。没有证据说明这些增加的制作工作能改善当前核心选择。']]))
add('<p>回合制确实减少连续动作、追踪碰撞和实时操作的负担；但3D仍需辨认人物正在对谁做什么、何时命中、结果如何。动作可以简化，信息反馈不能省掉。2D同样要制作和整合移动、作业、受击、护盾吸收及状态变化。官方文档分别列出<a href="https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html">3D导入管线</a>与<a href="https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html">2D精灵动画流程</a>；这里的工作量比较是基于本项目需求的判断，不是外包报价或工期保证。</p>')
add('<p><b>武器设计收敛：</b>基础攻击是一种明确距离和伤害的破拆动作；不做几十把只差数值的随机武器。七种装备为撬棍、急救包、绞盘、便携盾、绝缘工具、远程停机探针、担架，承担开障、治疗、跨越、遮挡、防电、远程控制、搬运等用途。玩家给任何适合的人装通用工具；人物专长则提供不同的作业方式。换装备显示工具图标、目标预览及对应通用效果，不承诺逐武器握持模型、独立动作或服装换装。</p>')
add('<p><b>表现边界：</b>8套角色立绘和表情，8个能从职业轮廓及配色辨认的棋子；6种机器预告模式；少量可复用移动、工作、攻击和受击效果。立绘质量、棋子辨识度、文字节奏仍要做美术验收。这一决定没有证明最终画面已经好看，也不把“AI能生成图”当作一致性与资产整合已经完成。</p>')
# Real board, explicitly a layout diagram.
b=next(x for x in boards if x['id']=='S11');cell=42;off=28;svg=['<svg class="board" viewBox="0 0 390 400" role="img" aria-label="S11实际关卡坐标示意，不是最终美术" xmlns="http://www.w3.org/2000/svg">'];colors={'.':'#e7efe8','~':'#9acdda',':':'#c5b897','#':'#344a50','X':'#245972'}
for y,row in enumerate(b['rows']):
 for x,c in enumerate(row):svg.append(f'<rect x="{off+x*cell}" y="{off+y*cell}" width="41" height="41" fill="{colors[c]}"/>')
for i in range(8):svg.append(f'<text x="{off+i*cell+18}" y="18" font-size="12">{i}</text><text x="10" y="{off+i*cell+25}" font-size="12">{i}</text>')
def mark(p,label,color):
 x,y=p;svg.append(f'<circle cx="{off+x*cell+20}" cy="{off+y*cell+20}" r="15" fill="{color}"/><text x="{off+x*cell+20}" y="{off+y*cell+25}" font-size="12" text-anchor="middle" fill="white">{label}</text>')
for p in b['exits']:mark(p,'出','#14776c')
for i,p in enumerate(b['spawns']):mark(p,str(i+1),'#376a9a')
for o in b['objectives']:mark(o['cell'],'任','#977133')
for e in b['enemies']:mark(e['cell'],'机','#ad5145')
svg.append('<text x="28" y="385" font-size="12" fill="#526b71">坐标布局示意；重叠任务按原关卡分阶段处理</text></svg>')
add('<div class="grid">'+''.join(svg)+'<div><h3>玩家实际操作什么</h3><p>看机器下一轮威胁范围 → 选择谁先移动、谁留AP作业 → 决定停机、隔离、绕开或承受代价 → 搬运伤员/保住服务 → 选择撤离顺序。三人的2AP可穿插使用，角色不是各自自动放完技能。</p><p>图为S11的真实布局示意，不是战斗截图，也不是最终美术。新的美术资产必须服务这些信息：谁能到哪里、什么正在带电、什么需要继续供电、谁携带了伤员。</p></div></div>')
add('<h3 id="growth">培养：从“多一次”改为“学会一种更合适的做法”</h3>')
add('<p>仍保留六级，1/3级两项专长、2级倾向选择、4/6级体力成长；不加第三个主动技能或独立合作经验条。取消所有人五级统一多一次使用次数，改为强化一个已有技能。升级不删除原来可行的选择，苏棠在原移动支援与AP转交之间选择，共享次数。</p>')
add(table(['人物','五级用途','为什么会在某种局面下选他/她'],[
 [names[k.split('_')[0]],esc(v),why] for (k,v),why in zip(G['level5'].items(),[
 '隔开三格也能先稳住伤员，把自己的位置留给下一项任务。',
 '携带伤员也能过单格障碍；队友不必先部署绞盘，普通队伍仍可用工具或绕行。',
 '把自己的行动交给已经到位的专家，适合一人需连续作业/搬运的回合；全队总AP不增加。',
 '允许有血量的现场设备承受更大一次风险；没有威胁时不值得专门为此练级。',
 '为更长的一段带电路线安排保护；绝不改变深水通行性，也不穿墙。',
 '先建屏障再离开，队友可以之后使用这条保护线；3HP仍会被打掉。',
 '远处关停高工量开关，减少反复跑控制点；不能远程直接取得主目标/证据。',
 '两格直线接力改变人员布置；中间必须空旷干燥，不能隔墙传送。'
 ])]))
add(f'<p><b>受控结果：</b>初版80,192次路线试算中，五级额外次数的较优结果为0。用途升级后，同样1,432个日期合法阵容/目标情境中，五级相对三级有{len(gg)}个排序改善，其中{meaningful}个改善了回合或伤害，{len(gg)-meaningful}个仅少花AP；没有发现因此独占额外目标集合。不能把这三种收益混称为“新玩法”。</p>')
add('<p>这里还有一个需要正视的集中度：192个改善情境中，172个较优路线使用苏棠的支援，且搜索器对她的主动使用更充分。这个数字不足以证明她过强，也不足以证明其他七人五级价值平衡。许舟携带跨越等已用独立动作夹具核对合法性，但当前路线搜索没有充分主动寻找这些操作，因此不能拿脚本偏好替代阵容平衡结论。</p>')
add('<p><b>已经改掉无效投资引导：</b>不再每日催促训练，不把花完营地项目作为成功标准。普通训练每人1物资、3经验、8疲劳；训练经验封顶100，不收无效经验费用。界面显示下次计划出勤前的等级变化、具体解锁用途、占用项目与不能同时恢复的代价。常驻角色靠实际出勤成长；付费训练用于提前解锁或安排后备人选。</p>')
add('<h3 id="parties">阵容：先有不同做法，再看代价是否值得</h3>')
add('<p><b>叶禾的第一专长已重做：</b>邻接机器花2AP隔离危险输出，每任务一次；危险输出停止，设备占格与供电保留。陈砚则保留低成本的临时打断。普通停机仍然存在，代价是关掉对应供电；已经产生的火焰和已排队增援不会被隔离魔法般撤销。于是两人不再只是同一技能换名字。</p>')
frows=[r for r in F['rows'] if r['mission']=='S11' and r['party'] in [['lin','xu','su'],['lin','xu','chen'],['lin','xu','ye'],['lin','xu','mo']]]
add(table(['S11阵容（受控三级）','较优采样路线','回合/伤害','同样保住的结果'],[['、'.join(names[a] for a in r['party']),('叶禾靠近隔离，保供电作业' if 'ye_1' in r['best']['mechanisms'] else '普通操作赶窗口，承担带电现场伤害'),str(r['best']['rounds'])+' / '+str(r['best']['damage']),'主目标＋冷库切换服务'] for r in frows]))
add('<p>愿意少受伤的玩家有理由选叶禾；愿意承担少量伤害抢一轮的玩家可选更快的普通路线。这里比较过日期可用阵容与装备配置，不能只拿一个故意不使用普通工具的失败方案作陪衬。结果依然只是在这组有限策略中较优，并非人类能找到的绝对最优。完整13,728次现场操作试算覆盖四处现场任务的126种日期合法三人组合，全部找到主目标与现场服务兼得的路线。</p>')
add('<p>其他组合的玩法任务也固定下来：许舟＋江朔安排跨障与交接位置；莫遥＋陈砚把远程停机与临时打断错开；贺鸣配搬运者可以先建立保护线再离场；林岚负责远距稳定而不是必须随身贴着伤员。它们与通用工具、绕行、普通攻击、受控承伤都要保留竞争。后四项有合法动作与关卡支持，不在此声称每一组已证明比普通路线更值得培养。</p>')
add('<h3 id="positive">关系：共同安排有实际收益，但不是好感满就全队加伤</h3>')
add('<p>保留原有明确承诺、事件归责、严重记忆、冲突冷却与人物结局。此次补了两个正向模板，复用现有营地项目和后勤席位。关系短谈现在真实保存“共同约定/保持专业距离”，不能读完对白就自动获得信任和能力。共同安排需要双方在两次不同任务中各有有效目标贡献，相关任务没有已记录违约，当前也没有未解决的条件合作级冲突。</p>')
add(table(['共同安排','得到什么','完整成本与防刷规则'],[
 ['带教：已有12组关系人物对','导师帮学员把成长提前到本晚；最多6经验，不超过导师或100。不会复制导师专长。','1项目＋2物资，两人各8疲劳；导师无经验，每名学员每章一次。仅同队、交接刷动作、制造误会再修复不产生新教学资格。普通3经验训练仍可用。'],
 ['R04/R10改派接应','一人出勤、一人占原后勤席位，在已公开东侧点接应，改变撤离路线。','出发前2物资，加上放弃后勤正常1物资产出；后勤仍8疲劳/2经验。替换常规出口，不免费多开出口；一关只决定一次，支线不可用。'],
 ['选择专业距离','保留个人边界和对应叙事，不接受上述共同计划','不扣好感、不删除普通训练、不锁结局。基础行动及普通解决办法照常。']]))
add('<p><b>为什么不能全点：</b>13次带教的整局策略比普通临界训练多花21物资，合计多2回合、2点伤害；导师占用和疲劳影响了后续安排。五次改派接应又多花15物资，M20变慢一轮、M22快一轮，整局没有净提速。这个反例否定了“培养关系必定赚”。</p>')
add('<p><b>据此做的修正：</b>共同计划默认不勾选；带教面板比较普通训练与带教是否真能赶上下次出勤的解锁，接应面板并排显示两处出口、任务位置、已知风险和成本。重新跑的选择性策略只在第22夜安排一次带教，让叶禾提前于M23获得五级；此路线战绩没因此变好，所以带教定位为成长安排工具，不宣传为隐藏强度答案。只在M22改派接应，实际多花3物资、该关快1轮，其余任务目标不变。</p>')
add('<p>接应价值的全图几何对照也没有挑一个好例子：46种目标选择×2处出口均能完成；按伤害优先、回合其次比较，东侧13组更好、13组更差、20组相同。早期地图只是几何检查，关系尚未建立时不能据此获得东侧出口。实际战役只在已经达成关系和人手条件的后期使用。</p>')
add('<h3 id="campaign">放回24天、36关和真实成长后的结果</h3>')
allc=C['scenarios']+T['scenarios']
add(table(['预设游玩策略','任务胜利/尝试','总回合/伤害','末尾物资','带教/改派','实际结局'],[[esc(s['summary']['name']),str(sum(b['success'] for b in s['battles']))+'/'+str(len(s['battles'])),str(sum(b['rounds'] for b in s['battles']))+' / '+str(sum(b['damage'] for b in s['battles'])),s['summary']['resources']['supplies'],str(s['summary']['positive_relationships']['mentoring'])+' / '+str(s['summary']['positive_relationships']['dispatches']),{'shared_control':'共同监管','distributed_rebuild':'分布重建','evacuation':'撤离'}[s['summary']['world_ending']]] for s in allc]))
add('<p>上表是10个预设策略、348次实际状态衔接的任务。经验来自任务、训练和后勤，加入时间、疲劳、伤势、营地项目、人物承诺、资源与结局使用同一账本。标准场景没有永久失去主要角色；最高难度在指定的四次失误后苏棠和陈砚永久离队，仍完成24次主线并到达撤离结局。最高难度没有跑支线，因此不能把其总回合与36关路线直接比快慢。</p>')
add('<p>固定初始队伍加临界训练，合计少3回合、花8物资；轮换队伍加临界训练，合计少1回合、花9物资。说明普通训练不是每日必做。轮换路线的整体成绩优于这组固定路线，但换人的策略、疲劳、技能使用同时变化，不能把差异全部归因于某个专长。所有采样阵容均有普通通关方案，意味着没有“通关必带某人”的已见证据；不等于已经证明不存在最强效率阵容。</p>')
add('<p><b>重玩理由的定位：</b>第一遍优先保住人和完成任务；再玩可以换专业分工、处理未完成的人物约定、选择M17修复/隔离与最终监管/重建/撤离。已分别跑通三种结局，不随机重写人物过去，不靠每天换几句对白或刷关系奖励凑重玩。第二遍是否有足够惊喜、玩家是否愿意重玩，当前没有真人证据。</p>')
add('<h3 id="coverage">逐关覆盖表</h3><p>“专长改善”是三级专长相对同等级基础操作的回合/伤害/结果改善；“五级改善”还包含只少AP的情况。等级实验用于比较能力，不表示M01就能练到五级。现场服务另列，因为基础目标矩阵不强迫所有队伍值守。</p>')
add(table(['关卡','阵容/目标情境','普通主目标成功','三级专长改善','五级排序改善','现场服务可行阵容'],[[r['mission'],r['cases'],r['baseline'],r['specialty_gain'],r['L5_gain'],sum(x['service'] for x in F['rows'] if x['mission']==r['mission']) or '—'] for r in M['maps']]))
add('<h3 id="limits">检查了什么，仍不能声称什么</h3>')
add(f'<p>本轮{V["passed"]}项规则/账本断言通过：AP转交守恒、同轮限制、保留原移动选择；携带跨越；三格绝缘不穿墙；两格交接不穿障；远程工作不越权完成主目标；隔离保留供电且不抹掉既成危险；带教费用/上限/同章防重复；接应后勤费用/经验不双算；失败提交回滚与结算不重复；低好感基础合作仍可用。手工状态夹具与完整战役证据分别保留。</p>')
add('<div class="note warning"><b>还不能盖章的部分：</b>新能力的使用覆盖不均，尤其五级收益集中在苏棠使用充分的路线；普通成功路线很宽裕，样本中没有形成“只有某专长才能多拿一个目标”的结果；物资余额较高，不能宣传存在强经济压迫。当前保留自由解法，不用强制职业门锁、恶意加伤或把普通路线削差来制造价值。已经将带教降为可选成长安排、撤销无收益的加次数、明确操作差异和实际成本；角色魅力、学习负担、长局节奏仍需真实玩家的操作和反馈验证。离线审查不能替代这些证据。</div>')
add('<p><b>开发能力判断：</b>上述边界在规则结构上适合现有Godot单机桌面方向；我可以协助写规则、关卡数据、界面和自动检查。但完整稳定的发行版仍包含存档迁移、预览与实际执行一致性、交互、字体/分辨率适配、资源整合和人工验收。此次正式运行时文件的哈希逐项未变；没有偷偷开发一个网页演示版，也没有宣称游戏已完成或工期已验证。</p>')
add('<details><summary>可复核证据与重建入口</summary><p><a href="growth-identity-matrix.json">80,192次受控路线与逐关汇总</a> · <a href="growth-identity-field.json">13,728次现场组合</a> · <a href="growth-identity-ports.json">92组出口几何对照</a> · <a href="growth-identity-campaigns.json">8条完整账本</a> · <a href="growth-identity-selective-campaigns.json">2条选择性投入账本</a> · <a href="growth-identity-checks.json">规则断言</a> · <a href="growth-identity-pre-upgrade.json">旧加次数方案的负结果</a></p><p>当前修订源：work/growth-identity-review/；权威规则：game/data/final_design/growth_identity_contract.json。全量重建：python3 work/final-design/rebuild.py。只重做当前审查：python3 work/growth-identity-review/rebuild.py。历史负结果保留为修订前证据，当前重建重新生成当前方案，不把历史报告计为当前复核。</p></details></section>')
section='\n'.join(parts);(O/'growth-identity-section.html').write_text(section)
(O/'growth-identity-review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 0.13养成与战斗形式复审</title><style>'+css+'</style><main><h1>保住人物与阵容的吸引力<br>先把战斗形式定清楚</h1><p><a href="full-game-design.html">返回完整36关设计</a></p>'+section+'<footer>此文为产品设计审查，不是试玩反馈或市场需求证明。</footer></main></html>')
print('Built0.13report and master section')
