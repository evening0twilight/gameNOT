"""Player-facing audit; distinguish complete encounters, controlled fixtures and judgments."""
from pathlib import Path
from collections import Counter
import json,html,hashlib
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
def read(p):return json.loads(p.read_text())
R=read(O/'tactical-matrix-results.json');W=read(O/'tactical-full-witnesses.json');Q=read(O/'tactical-replay-checks.json');K=read(O/'tactical-mechanic-checks.json');C=read(O/'campaign-from-tactical-results.json');H=read(O/'he-personal-full-witness.json');U=read(O/'system-audit-results.json');V=read(O/'final-design-validation.json');B=read(D/'boards.json')['boards'];T=read(D/'tactical_review_contract.json')
names={x['id']:x['name'] for x in read(ROOT/'game/data/characters.json')};names.update({x['id']:x['name'] for x in read(ROOT/'game/data/equipment.json')});names.update({x['id']:x['name'] for x in read(D/'abilities.json')});names.update({x['id']:x['name'] for x in read(D/'progression_relationship.json')['protocols']});names['scanner']='远程停机探针'
styles={'controls':'先停机','rush':'主目标优先','attack':'先拆机器','optional_first':'额外目标优先'}
def e(x):return html.escape(str(x))
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def fmt(x):return f"{x['rounds']}轮 / {x['ap']} AP / {x['damage']}伤害"
def gear(mid,item,holder,goals,style='controls'):return next(x for x in R['gear_runs'] if x['mission']==mid and x['item']==item and x['holder']==holder and x['goals']==goals and x['style']==style)
def opt(mid,style):return next(x for x in R['optional_runs'] if x['mission']==mid and x['style']==style)
parts=[]
def add(s):parts.append(s)
add('<p class="eyebrow">夜潮事务所 / 设计审查 0.7 / 2026-11-01</p><h1>36关，是否真有办法玩下去？</h1><p class="lead">把战斗行动、装备取舍、人物边界和整局后果放进同一套规则推演。正式游戏开发仍暂停。</p>')
add('<div class="verdict"><b>本轮结论：</b>在已检查的配置里，36关均存在主目标完成、三人无重伤撤出的基础行动解法；没有发现必须指定某位主角或购买某件装备才能继续主线的关卡。发现并修订了无实际收益的付费工具、被成长挤掉的合作收益、携带例外冲突、人物计划截止日以及额外目标缺乏取舍等问题。<br><b>不能由此断言：</b>所有阵容同样强、所有玩法都有同样吸引力，或真人一定觉得好玩。本文把实际运行、规则审查与仍需真人体验的结论分开。</div>')
add('<nav><a href="#evidence">证据范围</a><a href="#changes">具体修改</a><a href="#choices">玩家怎么选</a><a href="#levels">36关逐关结果</a><a href="#mechanics">40项能力与工具</a><a href="#campaign">战斗接整局</a><a href="#system">全系统复核</a><a href="#limits">结论边界</a></nav>')
add('<h2 id="evidence">验证的是可执行的操作，不只是数值范围</h2>')
add(table(['推演层次','已执行范围','可以支持的判断'],[
 ['完整地图',f"36关、46种目标组合 × 3难度 × 2环境＝{len(R['cases'])}配置；每配置4种行动优先级，共{R['attempt_count']}次",'逐轮走格、AP、前置工量、停机后占位、六类敌人锁定预告、增援、环境、目标受损与三人撤离'],
 ['装备／成长／关系组合',f"{R['counts']['equipment_growth_relationship_attempts']}次比较；另736组交叉配置、1472次策略尝试",'交叉为46目标组合×2成长×有无一件工具×可否高级合作×2难度；不是所有角色与全部道具的笛卡尔积'],
 ['额外目标与容错','184次额外目标尝试；184次开局空耗一轮尝试','标准难度下46种主目标仍都找到延误后的完整解法；不是任意失误都无代价'],
 ['逐条回放',f"{Q['witnesses_replayed']}条完整解法，{Q['player_commands_checked']}个玩家命令、{Q['enemy_environment_steps_replayed']}次敌人/环境结算",'重放不调用寻找策略的函数；重新检查AP、连续路径、落脚占位、目标合法性与最终结果。仍使用同一规则模型，不冒称独立实现'],
 ['单动作受控实验',f"24专长＋12装备＋4协议；{K['passed_count']}项检查",'AP、实际效果、次数、目标类型、基础替代、保障条件与拒绝。受控场景不等于每关都能达到该情境'],
 ['战斗到整局','标准、最高各24场真实推演结果进入逐日账本','出勤、加入、疲劳、成长、晚间项目、人物凭据、世界路线、结局连续结算']]))
add('<p>四种策略是固定启发式：先停机、主目标优先、先拆机器、额外目标优先。它们会交错三人的行动，不假设所有角色同时站到目标旁。选取解法优先无失能、再比较轮数、伤害和AP；这不是最优求解，也不是玩家胜率统计。</p><p>基础解法均使用三名10HP队员的通用动作，不用人物专长、工具和高级协议。正式阵容成员只要可出勤，就共有这些动作；这是“不把人物当主线钥匙”的证据，不能写成已经独立跑完56个具名阵容。</p>')
add('<h2 id="changes">已直接写回设计的修订</h2>')
add(table(['原问题','修订'],T['decisions']+[
 ['陈砚晚接受计划却无真实施工可做','最晚接受改D20；M21仍有工程。M22的记录类work不能冒充施工，M23没有工程。迟读保留专业分支，不收无法兑现的计划费用。'],
 ['说明文档与执行模型可能用不同版本','当前规则顺序为基础定义→0.6系统审查→0.7明确修订；同步完整设计、人物验证器、装备目标与报告。最高限时不再沿用旧的统一减1。']]))
add('<p>推演工具本身也修正了几处错误：停机机器错误地消失、已过期携带物可能再次交付、最后携带者撤出多算一次交付、M22盾牌本该挡的射线被旧墙提前挡住。随后使用修正后的同一规则重跑原版/新版，不把模型缺陷当作游戏机制的成功。</p>')
add('<h2 id="choices">选择有没有意义：用实际结果回答</h2>')
add('<h3>1. 先安全处理，还是先抢机会？</h3>')
rows=[]
for mid in ['M06','M12','M18','S07']:
 for style in ['controls','optional_first']:
  x=opt(mid,style);rows.append([mid,styles[style],fmt(x),'全部额外目标取得' if x['all_requested_secured'] else '有额外目标失去',','.join(x['secured']),','.join(x['lost']) or '无'])
add(table(['关卡','策略','实际代价','额外结果','保住的对象','失去的对象'],rows))
add('<p>M06档案第6轮末必须送出，先抢档案的路线可兼顾救人，但本次操作承受2点伤害；先处理风险可以零伤完成救援，却会错过档案。M12签名页第3轮末、M18备份第3轮末、S07副本第5轮末失去机会，均在免费简报和棋盘倒计时提前显示。主任务成功条件不临时加码，后期公共核查保留世界路线补救，但不倒填错过的现场故事与奖励。</p><p>这四处是刻意设置的机会取舍，不给36关全部套上额外倒计时。其他关允许熟练玩家兼顾，避免把救援做成每次必丢一样东西的强制惩罚。</p>')
add('<h3>2. 关系改善是方便，还是通关门票？</h3>')
x=gear('M17','cooperation',[0,2],['repair2']);y=gear('M17','refusal',[0,2],['repair2'])
add(table(['同一M17修复目标与策略','结果','含义'],[['已学习且允许保护作业',fmt(x),'本次两个位置合适的角色配合，少2AP'],['拒绝该高级合作',fmt(y),'改普通施工；同样完成修复并三人撤离']]))
add('<p>旧版保护作业花两个人各1AP只做2工量，成长后经常比普通操作更差。现在做3工量并附一次机器防护，不叠成长加成。若人物要求第三人保护，第三人确实要站到合适位置、付1AP；含保障的总成本是3AP，不能把这项准备隐去后宣传“永远赚AP”。既有队友和对队长的有向关系都要检查，冷却只限制重复长冲突，不会清除合作条件。</p><p>并非任意两人站在任意位置都有收益：M17的另两组已学习配对在同一策略里没有省AP。若拒绝，玩家可独立施工、先停机或重新站位；无需刷礼物后才能继续主线。</p>')
add('<h3>3. 装备给谁，比只买不买更重要</h3>')
rows=[]
for mid,item,holder,goals in [('M17','scanner',0,['repair2']),('M21','cutter',1,['route']),('M23','stretcher',0,['r1','r2'])]:
 a=gear(mid,item,holder,goals);base=opt(mid,'controls');rows.append([mid,names[item]+'→队员'+str(holder+1),fmt(base),fmt(a),'同一目标集合、同一优先策略；位置与后续分工会随能力改变'])
add(table(['关卡','配置','基础','带装备','比较范围'],rows))
add('<p>远程探针省的是走近停机开关的路程与前排工作；切割器增加重障碍工量，但有提前预告的有限增援；担架给实际搬运者才有意义，不叠贺鸣的同类优势。工具仍占槽，不能全员共享同一件工具的远程效果。某些固定启发式在换装备后反而绕得更差，这只能说明需要重排动作，不能断言道具本身降低能力。</p><p>原来付费选择A/B天气的扫描仪，在46种基础目标的最佳解中没有改变轮数/AP/伤害，因此撤销这项收费价值主张。天气免费公示，扫描仪改为有实际工量作用的探针；不再拿A/B切换冒充已经验证的重玩吸引力。</p>')
add('<h3>4. 玩家能犯错，但不同策略不保证同样结果</h3>')
add(table(['实际反例','发生什么','玩家仍能怎么处理'],[
 ['M11最高，先拆机器，A/B均出现','7轮内完成cut和lock；三人都没失能，但只有两人正常撤出','目标成果保留；未正常撤出者按紧急撤退规则处理。先完成工作再走有完整解法，不要求重开整局'],
 ['M15只救一户','满足明确公布的最低主目标；另外两户损失单独记录','可以争取更多救援，不能把最低成功的结算播放成全楼获救'],
 ['高怨且冷却中的危险合作','不重复播冲突，但拒绝仍在','可准备真实保障、换执行者、先关危险源或独立行动；不会突然禁止基础移动/施工'],
 ['伤员在最后一轮仍被背着','拾起不算已经获救，计时不暂停','最后允许轮仍可移动并送达；送达先于轮末期限判定。最高难度救不回才可能医疗离队']]))
add('<h3>5. 战斗真能生成个人成长证据</h3>')
add(f'<p>M22以林岚、许舟、贺鸣出勤，不带装备，只使用贺鸣1级架盾：<b>{H["rounds"]}轮／最高限时{H["limit"]}轮，{H["ap"]}AP，{H["damage"]}伤害，三人全部撤出</b>。第一轮林岚走到操作区，贺鸣走侧路；第二轮林岚启动终端，贺鸣到(4,1)，花1AP在(3,1)架盾，实际拦住(3,0)守闸机射线。终端由林岚完成，贺鸣获得真实保护凭据。此前接受计划、暂不提前收束第三段即可走该分支；没有凭据则保留专业方向，不强制写成和解。</p>')
add('<details><summary>M22保护与撤离完整动作记录</summary>'+table(['轮','动作','细节'],[[x['round'],x['action'],{k:v for k,v in x.items() if k not in ['round','action']}] for x in H['log']])+'</details>')
add('<h2 id="levels">36关逐关审查与操作证据</h2><p>表中为不使用专长/装备/高级协议的标准A环境解法。分支关逐条列出；“最高解/限时”使用同目标最高难度A环境的完整解法。每关六种难度环境组合均已运行。所有动作细节可展开，完整276条另有JSON记录。</p>')
allrows=[]
for b in B:
 ss=[x for x in R['cases'] if x['mission']==b['id'] and x['difficulty']=='standard' and x['variant']=='A'];hh=[x for x in R['cases'] if x['mission']==b['id'] and x['difficulty']=='hard' and x['variant']=='A']
 for s in ss:
  h=next(x for x in hh if x['goals']==s['goals'] and x['route']==s['route']);allrows.append([b['id']+' '+b['title'],s['route']+' / '+','.join(s['goals']),styles[s['style']],fmt(s),str(h['rounds'])+'/'+str(h['limit']),len(s['successful_strategies'])])
add(table(['关卡','目标组合','本次选取策略','标准：轮/AP/伤害','最高解/限时','找到完整解的策略数/4'],allrows))
add('<div class="filters"><input id="find-map" aria-label="查找关卡" placeholder="输入 M17、关卡名或取舍关键词"><button id="expand">展开筛选结果</button></div>')
for b in B:
 add('<details class="map" id="review-'+b['id']+'"><summary>'+e(b['id']+' '+b['title'])+'</summary><p><b>玩家取舍：</b>'+e(b['decision'])+'</p><p><b>结算与后续：</b>'+e(b['consequence'])+'</p><p><a href="full-game-design.html#'+b['id']+'">查看坐标地图、目标前置和敌人配置</a></p>')
 for w in [x for x in W if x['mission']==b['id'] and x['difficulty']=='standard' and x['variant']=='A']:
  add('<details><summary>'+e(w['route']+' / '+','.join(w['goals'])+' · '+styles[w['style']]+' · '+fmt(w))+'</summary>'+table(['轮','行动/事件','实际记录'],[[x['round'],x['action'],{k:v for k,v in x.items() if k not in ['round','action']}] for x in w['log']])+'</details>')
 add('</details>')
add('<h2 id="mechanics">24专长、12装备、4协议逐项价值审查</h2><p>以下40项均执行了合法受控场景。它们证明“存在具体用途与基础替代”，不证明每关都值得带。全地图自动策略只组合了其中明确列出的工具和保护作业；其余不能混算成整关验证。</p>')
effects={x['id']:x['effect'] for x in read(D/'abilities.json')};effects.update({x['id']:x['effect'] for x in read(D/'equipment.json')['items']});effects.update({x['id']:x['effect'] for x in read(D/'progression_relationship.json')['protocols']})
add(table(['能力/物品','明确收益与边界','受控实验中的实际比较','实验AP（含前置保护）'],[[names[x['id']],effects[x['id']],x['meaning'],x['ap']] for x in K['coverage']]))
add('<p>苏棠标记、许舟牵引等不是“凭空赚总行动”：它们把工作移给另一位置、另一人的AP。角色叠加也有上限：携带移动最多3，空手最多4；临时控制同一机器有间隔；护盾同类取最大；接力不反复生成奖励；同一物件不可既消耗供电又带回领赏。最高难度仍不更改角色性格和怨气公式。</p>')
add('<h2 id="campaign">从战斗结果接到24日整局</h2>')
add(table(['整局情境','主线','世界路线','结余资金/物资/零件','实际兑现的个人计划'],[[x['summary']['name'],x['summary']['main_count'],x['summary']['world_ending'],' / '.join(str(x['summary']['resources'][k]) for k in ['credits','supplies','parts']),'、'.join(names[a] for a in x['summary']['verified_contracts'])] for x in C['scenarios']]))
add('<p>这次不预先填“任务成功”：每场实际运行地图，把对象完成、送达与贡献者映射到当天可出勤角色，再计算奖励、经验、疲劳、营地项目和后续路线。此参考策略主动轮换、按已有日历读故事，未购买新装备、未打支线；战斗保守只用10HP通用动作，不把较高等级的实际人物当作额外伤害优势。</p><p>两条整局都能得到共同控制路线；七人的计划有实际凭据，贺鸣未被自动判兑现，另用上面的M22完整保护路线证明可达。三十六段重点个人/关系场景在此安排中可读完；不等于所有生活短谈一局都能读到，更不等于已实测12–16小时。</p><p><b>经济审查的判断：</b>结余622/32/50说明此设计不是持续贫困求生。资金作用是采购和补给，主要机会成本是人员、工具槽、任务期限与23晚46个项目。保留这个产品定位，不临时添加每日口粮税或修理费去制造耗钱。当前参考策略能不买新装备过主线，符合保底；它不能证明装备价格有足够吸引力，因此不把“购买率、经济平衡”标为通过。</p>')
add('<details><summary>标准整局逐日：实际出勤、战斗与贡献</summary>'+table(['日/任务','出勤','战斗结果','实际完成','贡献归属'],[[x['day'],'、'.join(names[a] for a in x['party']),f"{x['rounds']}/{x['limit']}轮 · {x['ap']}AP · {x['damage']}伤害",','.join(x['completed']),{k:[names[a] for a in v] for k,v in x['actual_contributors'].items()}] for x in C['scenarios'][0]['battles']])+'</details>')
add('<h2 id="system">再次全量复核：每个系统怎样影响玩家</h2>')
audit=[
 ['目标与路线','成功条件开局明确；最低完成、额外成果、全员正常撤离分别记','276完整解＋M11两条未全撤反例；M15逐户结算；M24三路线分别运行','已执行具体路径，未穷尽所有动作'],
 ['空间与敌人','停止危险、改变站位、抢操作窗口各有办法','六敌种预告、停机仍占格、射线/墙/盾、同轮推移、有限增援、车辆落点检查','全地图基础行为＋受控边界'],
 ['伤势与撤退','知道救人需实际送达，不会因同队或受伤自动结怨','普通重伤可恢复；最高失能者遗留才可永久医疗离队；搬运不暂停期限；送达先判','战术受控边界＋旧整局极端失败账本'],
 ['库存与装备','准备有用途，但没有某件工具也能行动','所有12物品有合法目标；解锁、唯一持有、耗材容量、用掉/退回守恒；工具不因离队丢失','装备84项＋账本51项及本轮动作'],
 ['成长与配置','解锁办法、分工和小幅容错，避免等级墙','等级不倍增基础伤害；2专长槽；2级被动不叠工具/协议；晚加入经验底线；两整局实际成长','受控高等级不是开局可用性宣称'],
 ['关系与满值','玩家能看到由谁、哪件事造成，补救实际减少负担','真实活跃权重≤100；事实不消失；归档不回填；普通3日/严重混合残余；重伤恢复不清旧账','89项系统回归含8000转换样本'],
 ['归责与冲突','不让替队长执行命令的人无故背锅','按源决定/观察者/责任对象合并；责任份额≤1；阶段有退出阈值；冷却与拒绝独立','40804阶段输入＋账本方向检查'],
 ['合作与边界','可以准备保障，也可以独立行动','队友和队长两方向；合作标签同样检查个人技能；保护须真实站位/AP；基础动作始终保留','736交叉配置＋实际拒绝/保障实验'],
 ['疲劳与人手','轮换有意义，不因连续失败卡死','工作/睡眠/休息分别结算；加入只看主任务结算；真正缺人主线才补社区人员','实际两整局＋旧极端失败情境'],
 ['营地与资源','训练、恢复、设施、实质补救竞争安排','每晚2项目，同人不重复；短谈不吃项目；照护免费；错过支线不扣基本生存','真实账本与项目冲突检查'],
 ['故事与承诺','玩家选的是能兑现的承诺，不能领奖后改历史','旧善举不倒填新约定；真实贡献/实际保护；陈砚最晚D20；职业与关系后记分别处理','49人物凭据检查＋224分支/缺席路径＋M22全关'],
 ['证据与地区','早拿事实有时间价值，晚补救仍能继续','原件/公开副本不重复奖励；晚副本不修复早违约；M17隔离截地区上限；终局读实际路线成果','账本路线门槛与实际24场结局'],
 ['结算与失败','保住的人不因任务总体失败被抹掉','唯一结果包、幂等发奖、完成/持续有效区分；无D24营地；缺席人物用有据摘要/来信','既有全链回归重新运行'],
 ['存档与重复进入','不能靠重进刷新奖励或清掉风险','状态需保留已公布意图、AP、消耗、目标计时、记忆事实与冷却；退出不推进一天','规则审查；正式存读档尚未实现，不标执行通过'],
 ['信息与操作负担','作决定前知道代价，决定后知道原因','显示路径AP、危害、期限、拒绝原因与基础替代；重大离队预告；结算逐项呈现损失','设计要求已明确；界面理解成本未真人验证'],
 ['重复游玩与节奏','不同目标路线、人物计划、保住的社区事实组成不同经历','不随机改人物过去，不用刷钱和拖动画凑时长；A/B天气不再作为已证实卖点','具体分支可达；重玩欲与阅读/战斗配比待真人体验']]
add(table(['系统','主动设置的可玩点','闭环与反例处理','证据边界'],audit))
add('<p>原有内容488项、人物49项、整局账本51项、装备目标84项、系统审查89项重新运行。8000次随机关系转换与40804个阶段输入是性质测试样本，不累计冒充数万种独立玩法。</p>')
add('<h2 id="limits">哪些结论成立，哪些现在不能保证</h2>')
distribution=Counter(x['style'] for x in R['cases'] if x['difficulty']=='standard' and x['variant']=='A')
add('<p><b>可以确认：</b>上述配置中有真实基础解法，条件合作不会封死基础行动；装备、位置、目标先后存在可观察的结果差异；战斗产生的事实能接入人物与结局；本轮复现的问题已写回设计并回归，而非只列待办。</p>')
add('<p><b>仍然需要警惕的产品判断：</b>按优先用更少轮数的选择标准，46组标准A结果中，'+ '、'.join(styles[k]+str(v)+'组' for k,v in distribution.items())+'。主目标优先出现较多，说明当前主线奖励快速救援，不能把“每次清光机器”作为玩法卖点，也不能据此宣称四种策略完全平衡。标准难度给充分容错；最高按关缩短期限；额外成果承担一部分风险取舍。没有为了制造战斗次数把清场改成全关强制要求。</p>')
add('<p><b>尚未证实：</b>新玩家是否理解预告并能发现这些路线；40种能力是否同样值得装备；人物是否让人愿意持续投入；阅读和战斗是否重复；真实时长、价格和市场接受度。固定策略存在解法和单动作有用途，都不能替代这些答案。尤其“无必选角色的通关门槛”与“没有最强阵容”是两件事，本轮只为前者提供了证据。</p><p>因此当前状态是：<b>完成这次有范围、可复核的设计逻辑与战术审查，保持正式开发暂停；不把设计文件盖章为已通过真人可玩性测试。</b>本轮没有出现需要改变你已确认产品边界的分歧。</p>')
add('<footer>复核资料：<a href="full-game-design.html">完整设计0.7</a> · <a href="tactical-matrix-results.json">配置矩阵与失败记录</a> · <a href="tactical-full-witnesses.json">276完整动作轨迹</a> · <a href="tactical-replay-checks.json">回放结果</a> · <a href="tactical-mechanic-checks.json">40项动作实验</a> · <a href="campaign-from-tactical-results.json">战斗驱动的两整局</a> · <a href="he-personal-full-witness.json">M22人物线实证</a> · <a href="systematic-logic-audit.html">关系/归责/失败系统审查</a> · <a href="../game/data/final_design/tactical_review_contract.json">0.7修订规则</a></footer>')
style='''<style>:root{--ink:#203d44;--muted:#597179;--accent:#087b72;--line:#d5e2df}*{box-sizing:border-box}body{margin:0;background:#eef3f1;color:var(--ink);font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}main{max-width:1260px;padding:48px 52px;margin:auto;background:white}h1{font-size:40px;line-height:1.35;letter-spacing:-1px}h2{margin-top:58px;border-top:3px solid var(--accent);padding-top:22px;font-size:25px}h3{font-size:20px;margin-top:30px}.eyebrow{font-size:13px;letter-spacing:1px;color:var(--muted)}.lead{font-size:19px}.verdict{background:#e8f4ee;border-left:5px solid var(--accent);padding:20px 24px;margin:26px 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0}td,th{vertical-align:top;text-align:left;border-bottom:1px solid var(--line);padding:12px;min-width:100px;overflow-wrap:anywhere}th{background:#edf4f1}a{color:var(--accent)}nav{display:flex;flex-wrap:wrap;gap:8px 23px;border-block:1px solid var(--line);padding:18px 0}details{border:1px solid var(--line);border-radius:8px;padding:14px 18px;margin:12px 0}summary{font-weight:600;cursor:pointer}details details table{font-size:12px}input,button{font:inherit;padding:10px;border:1px solid #adc4be;border-radius:5px}button{background:#e8f3ef;cursor:pointer}.filters{display:flex;gap:12px;margin:25px 0}footer{margin-top:45px;color:var(--muted);font-size:14px}p{margin:14px 0}@media(max-width:760px){main{padding:24px}h1{font-size:30px}table{font-size:13px}.filters{display:block}}@media print{main{padding:0}nav,.filters{display:none}details{break-inside:avoid}}</style>'''
script='''<script>let q=document.getElementById('find-map');q.addEventListener('input',()=>{document.querySelectorAll('details.map').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(q.value.toLowerCase()))});document.getElementById('expand').onclick=()=>document.querySelectorAll('details.map:not([hidden])').forEach(x=>x.open=true);</script>'''
(O/'tactical-playability-review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 36关战术与可玩性审查0.7</title>'+style+'<main>'+'\n'.join(parts)+'</main>'+script+'</html>')
fragment='<section id="tactical-audit"><h2>36关逐动作与可玩性审查 · 0.7</h2><p>36关/46目标组合/三难度/两环境的276组配置均找到基础动作全员撤离解法；另执行736组装备×成长×合作边界×难度交叉配置。不是所有阵容全技能穷举或真人测试。</p>'+table(['实际修改','结果'],T['decisions'])+'<p>陈砚计划接受截止提前D20；M22贺鸣保护、他人施工、全员撤离有完整6轮案例。标准与最高各24场实际战斗结果已接入营地、人物凭据和世界结局。基本通关不锁人物，但没有证据证明不存在最强阵容或所有道具价格已平衡。</p><p><a href="tactical-playability-review.html">打开36关逐关结果、完整动作、取舍比较与全系统审查</a> · <a href="tactical-matrix-results.json">配置矩阵</a></p></section>'
(O/'tactical-audit-section.html').write_text(fragment)
print('Wrote 0.7 tactical report:',len(''.join(parts)),'characters,36 maps,40 mechanic rows.')
