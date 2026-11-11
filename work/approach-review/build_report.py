"""Player-facing design revision with complete traces and bounded conclusions."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
def load(p):return json.loads(p.read_text())
M=load(O/'approach-matrix-results.json');C=load(O/'approach-campaign-results.json');V=load(O/'approach-review-checks.json');W=load(O/'approach-protocol-witnesses.json');K=load(D/'approach_review_contract.json');B={b['id']:b for b in load(D/'boards.json')['boards']};N={c['id']:c['name'] for c in load(ROOT/'game/data/characters.json')}
def e(x):return html.escape(str(x))
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'
P=[]
def add(x):P.append(x)
def p(x):add('<p>'+x+'</p>')
add('<p class="eyebrow">夜潮事务所 · 0.10 · 2026-11-02 · 继续设计，未进入正式开发</p><h1>让搭配改变处理问题的办法</h1>')
p('本轮保留所有原主目标与基础通关办法，在12关增加与现场相符的可选服务成果，并把高级合作用于保护、分点值守、中转运输和改变重机位置。比较重点改成“保住哪些成果、承担哪些风险、占用哪些后续项目”，不再只比较少了几个AP。')
add('<div class="note"><b>已经得到的结果：</b>M06的接力方案多用一轮，却保住了普通交接对照里失去的档案；M22的保护值守可以同时保住在线交接与设备；拆毁威胁的办法也能完成服务，但事后维修会与训练争夺营地项目。本轮检查的全部基础配置均找到解法，不设人物钥匙。</div>')
add('<nav>'+''.join('<a href="#'+k+'">'+v+'</a>' for k,v in [('rules','改了什么'),('protocols','四种合作'),('examples','完整对照'),('maps','36关回填'),('campaign','整局代价'),('fixes','发现的矛盾'),('validation','验证边界')])+'</nav>')
add('<h2 id="rules">安全、连续服务与设备保留形成不同的选择</h2>')
add(table(['处理方向','当场怎么做','得到什么／放弃什么','后续负担'],[
 ['安全隔离','用所有人都能做的普通关停，再完成原主目标','保留设备、减少暴露；可能错过有明确时间窗的在线服务','没有维修债务；原救援与证据仍有效'],
 ['拆除失控执行机构','用基础攻击处理威胁，保持总线供电，再安排值守','可保住连续服务；损失这台设备的完整性','可不修，或花1营地项目＋2物资恢复；不阻挡主线'],
 ['保护与分工','留人值守，用保护、临时控制、通用屏障或绝缘争取连续窗口','有机会同时保住服务与设备；队伍不能全去抢别的目标','消耗真实行动、专长次数或工具配置；训练先占真实项目'],
 ['改造现场再复位','先安全停机，推移/牵引重机改变危险位置，再恢复分路','保留设备与总线，改变通路和威胁方向','准备步骤较多，必须赶得上窗口；允许这种合法绕解']]))
p('值守是可选的现场成果，不是隐藏主目标。每个标记位置每轮付1AP、空手留到轮末；要求两轮连续有效。需要两个位置时，必须是两个实际操作者。断电、离位、失能或没有防住的冲击会中断这一轮，连续计数归零；可以在窗口内换人再尝试。已完成的服务不会因随后断电而被抹掉。')
p('截止时间来自具体现场事件：试航、车辆放行、社区终端在线交接等。它与主线撤离期限分开显示。玩家可以先完成服务再断电，也可以先断电处理危险、复位后再值守；不会为了保持设计者预想路线而禁止这些办法。')
p('设备损毁与服务错过也分开记录。维修只修复物理设备，不能补造过去的不断供、在线见证或已失约的承诺。没有接受相应承诺时，放弃额外服务、断电或拆设备不自动增加怨气。')
p('只有简报已标记的委托设备才进入可选维修清单，其他威胁没有隐藏维修账。联动开关明确标出“全部关停会暂停现场服务”，展开后显示受影响的现场任务与原因，不再只写“制动”却事后扣掉服务成果。')
add('<h2 id="protocols">高级合作各自负责不同问题</h2>')
add(table(['合作','现在的实际用途','必须承担的成本与边界','基础或装备替代'],[
 ['保护作业','一人负责精细值守，一人保护；操作者一次非致命机器冲击不打断当轮工作。原施工3工量版本保留','双方各1AP，保护者必须邻接并留在现场；不防电击、水火、离位和失能，不能替代第二个值守点','暂控机器、绕开预告、通用屏障、拆除威胁；也可以放弃这项服务'],
 ['交叉掩护','两个已开始值守的人互相掩护，保护两个位置，而不是把三个人都堆在同一处','双方各1AP、距离≤2；各一次机器减伤及一次不中断；几何位置不满足就不能使用','分别控制威胁、摆放屏障或选择只做主目标'],
 ['接力搬运','把物件交给实际接收者并沿选定路线移动，让原搬运者留在现场继续救援','双方各1AP，最多3地形代价，一次只交接一个真实物件；普通搬运仍存在','普通放下、拾起、移动；可能选择更快结束，但少保住一项限时成果'],
 ['协同牵引','从当前可站的位置把重机移向玩家指定的合法方向，改变危险或通路而不切断总线','双方各1AP、同时邻接重机、落点空且合法；机体完整但准备可能很慢','普通推移、停机、拆毁或绕行；普通推移也遵守同样空间规则']]))
p('高级合作仍要求实际训练和双向信任，关系恶化时还要满足人物具体的保障条件。林岚对坠落的顾虑不能扩展成拒绝一切终端操作；叶禾要求的绝缘必须真的铺好，陈砚要求的加固与绝缘也不能用一句“已经安排保障”替代。基础行动始终保留。')
p('牵引还暴露出一个空间问题：重机被移出轨道后，旧参考行为可能在下一轮跳回轨道。现在离轨就停驶，移回合法轨道才按当前位置继续；普通推移与高级牵引一致。利用这一点保留供电是允许的现场解法。')
add('<h2 id="examples">能逐动作复查的完整案例</h2>')
by={x['witness_name']:x for x in W}
add('<h3>M05：人员专长与拆除后维修之间的选择</h3>')
p('本日可用的四种三人组合全部保留基础通关办法。三种包含陈砚的组合找到用实际临时控制技能 chen_1 保住现场排水及设备的办法；林岚／许舟／苏棠组合也找到7轮完成主目标和排水的拆除路线，设备随后可选择维修。这里的区别是现场处理手段与后续项目占用，不是“缺陈砚就不能玩”。本轮没有据此断言不带陈砚在所有人工安排下都无法完整保全。')
add('<h3>M06：多用一轮，换来档案也被带回</h3>')
add(table(['同一前半段安排','完整救援','档案','整关轮数','总AP'],[[label,'两项均完成' if r['success'] else '未全完成','保住' if 'asset' in r['secured'] else '错过窗口',r['rounds'],r['ap']] for label,r in [('普通交接',by['ordinary_handoff']),('接力搬运',by['relay'])]]))
p('两条都从正常出生点出发，途中真的走路、稳定伤员、拾取和交接。接力在第4轮发生，接收者带走档案，原搬运者继续现场救援；档案在期限内送达。这个例子证明的是同一安排下的一项成果取舍，不证明其他普通路线绝对拿不到档案。更快的普通路线也不是错误答案。')
add('<h3>M22：同样拿到记录，交接状态和设备结果可以不同</h3>')
rows=[]
for x in V['counterfactuals']:
 if x['mission']=='M22':rows.append(['独立值守' if x['mode']=='independent' else '保护值守',x['success'],x['service_secured'],x['machinery_intact'],x['rounds'],x['damage']])
add(table(['同队同配置对照','原主目标完成','在线交接完成','设备完整','轮数','伤害'],rows))
p('独立值守仍能拿到主线记录，但受冲击后连续窗口中断；有明确搭档保护时，承受的非致命冲击不会打断那一轮。这里改变了在线交接是否完成，不只是结算里的好感对白。通用屏障也能提供另一条办法，需要购买、携带和摆放，因此没有把林岚、苏棠或某一对关系变成主线钥匙。')
r=by['ordinary_parallel_M22']
p('扩大任务组合后，还找到完全不用技能、合作和购买装备的普通分工路线：同一初始队伍和等级，改由另一人值守，其他人同时处理取证与脱敏，'+str(r['rounds'])+'轮、'+str(r['ap'])+'AP、承受'+str(r['damage'])+'点伤害，交接、证据、脱敏与现场服务全部完成，设备保全。这条完整行动记录已经保留。它改变了任务安排，所以不能并进上面的同计划反事实；也说明保护合作提供一种解法，而不是获得好结果的必要条件。')
add('<h3>M10／M21：两个人分别工作，合作保住同步窗口</h3>')
add(table(['关卡／同队同位置','计划','原主目标','连续服务','设备','实际抵住的中断'],[[x['mission'],'独立' if x['mode']=='independent' else '交叉掩护',x['success'],x['service_secured'],x['machinery_intact'],x['protocol_effects']] for x in V['counterfactuals'] if x['mission']!='M22']))
p('这与单点保护不同：两个人都要在各自位置工作，剩下的人处理主目标或现场威胁。若两点距离不满足掩护要求，就要换工具、站位和任务顺序；不能把保护一个人直接算作两个位置都有人。')
add('<h3>M08：允许先停机、改位置、再复位</h3>')
r=by['pull'];add(table(['实际动作','结果'],[
 ['先走到开关并普通停机，再用基础推移把重机移到较宽的轨道段','全部移动、停机和两次推移均支付真实AP'],
 ['两人分别站到重机旁，选择横向牵引','机体被移离轨道，不会下一轮瞬移回去，也没有被拆毁'],
 ['走回开关恢复分路，两人再去值守','连续服务：'+str(r['service_secured'])+'；原主目标：'+str(r['success'])+'；设备完整：'+str(r['machinery_intact'])],
 ['完成撤离',str(r['rounds'])+'轮，'+str(r['ap'])+'AP；这是完整可行路线，不宣称最优路线']]))
p('这条路线的准备比直接断电复杂。它的价值是保住供电与机体，同时改变危险的位置；玩家仍可以选择更简单的安全路线，不要求为了使用高级合作而表演这一套动作。')
add('<h2 id="maps">36关逐一回填</h2>')
p('同时推演只完成主目标、争取原有额外目标，以及把原有额外目标与新增现场服务一起争取的情况，检查留人值守是否挤占救援和运输。本轮没有给36关都塞进同一套新机关。12关增加在线服务机会；开局教学保留清晰的基础问题；已有多目标运输和救援的关卡改用完整成果比较；S03、S05保留短任务职责，没有为了“显得复杂”添加额外门锁。')
add('<div class="controls"><label>筛选关卡 <input id="filter" placeholder="编号、标题或玩法"></label><label><input id="newonly" type="checkbox">只看12关新增机会</label></div>')
add('<div class="scroll"><table id="maps-table"><thead><tr>'+''.join('<th>'+x+'</th>' for x in ['关卡','玩法职责','新窗口与位置','基础解法','在线服务／同时保全设备','再加原有额外目标：基础动作／全部方案'])+'</tr></thead><tbody>')
for m in M['maps']:
 mid=m['mission'];s=K['services'].get(mid);full=[0,0]
 if s:
  for case in [c for c in M['cases'] if c['mission']==mid]:
   targets=set(case['ambition']['goals'])|set(case['ambition']['extra'])|{'live_service'}
   found=[o for o in case['live_options'] if o['success'] and o['machinery_intact'] and targets<=set(o['secured'])]
   full[0]+=any(o['approach']=='independent' and not o['skills_enabled'] and not o['gear'] for o in found)
   full[1]+=bool(found)
 vals=[mid+' '+m['title'],m['role'],('位置'+str(s['posts'])+'；连续'+str(s['consecutive_rounds'])+'轮；第'+str(s['deadline'])+'轮末截止') if s else '保留原有目标结构',str(m['baseline_solved'])+'/'+str(m['cases']),str(m['service_solved'])+'/'+str(m['cases'])+'；完整设备 '+str(m['intact_service']) if s else '本轮不添加服务目标',(str(full[0])+'／'+str(full[1])+'（共'+str(m['cases'])+'配置）') if s else '沿用原目标对照']
 add('<tr data-new="'+('yes' if s else 'no')+'">'+''.join('<td>'+e(x)+'</td>' for x in vals)+'</tr>')
add('</tbody></table></div>')
p('“在线服务／同时保全设备”是这一组限定策略找到的结果数，不是玩家成功率，也不是某角色独有解法的证明。矩阵中的训练和购买条件逐条注明；真实战役另按实际信任、经验、开放日期和项目预算执行。')
p('最后一列要求主目标、原有额外目标、连续服务与设备完整性同时成立。“基础动作”也能拿全的情况会照实保留；全部方案的提升包括专业能力、合作与通用装备，不能把它全部归功于人物关系。找不到全收集方案时，仍允许放弃额外目标，不能反过来惩罚基础通关。')
add('<h3>不同搭配要付出的准备并不相同</h3>')
rows=[]
for party in [['lin','xu','su'],['chen','ye','he'],['xu','mo','jiang']]:
 case=next(x for x in M['cases'] if x['mission']=='M22' and x['party']==party)
 native=[x for x in case['live_options'] if x['success'] and x['service_secured'] and x['machinery_intact'] and not any(k in x['gear'] for k in ['shield','insulation'])]
 kit=[x for x in case['live_options'] if x['success'] and x['service_secured'] and x['machinery_intact'] and 'shield' in x['gear']]
 dismantle=[x for x in case['live_options'] if x['success'] and x['service_secured'] and not x['machinery_intact']]
 rows.append(['／'.join(N[a] for a in party),'找到' if native else '本次策略未找到','找到' if kit else '本次策略未找到','找到' if dismantle else '本次策略未找到','均可普通完成主目标'])
add(table(['M22阵容','不借通用屏障的服务＋完整设备','通用屏障替代','拆除后维持服务','基本解法'],rows))
p('阵容可以改变依赖的是关系训练、人物专业能力还是通用装备，也改变谁必须留在现场、谁能处理别的目标。最终都可能成功，这本来就是希望保留的自由；不能为了让表格出现差异，强迫某一队永远失去好结果。')
add('<h2 id="campaign">把选择放回整局：维修挤占了什么</h2>')
rows=[]
for s in C['scenarios']:
 q=s['summary'];a=q['operational_summary'];rows.append([q['name'],str(q['main_count'])+'主/'+str(q['side_count'])+'支',str(a['service_delivered'])+'/'+str(len(s['operational'])),str(a['intact'])+'原本完好／'+str(a['repaired'])+'修复／'+str(a['unrepaired'])+'未修',a['repair_projects'],q['resources'],len(q['withdrawn'])])
add(table(['整局策略','任务','完成服务','设备状态','维修占用项目','最终资源','永久医疗离队'],rows))
repair=C['scenarios'][3];leave=C['scenarios'][4]
add(table(['同样选择拆除威胁','修复设备','保留项目与物资'],[
 ['主线是否完成',repair['summary']['main_count']==24,leave['summary']['main_count']==24],
 ['实际维修项目',repair['summary']['operational_summary']['repair_projects'],leave['summary']['operational_summary']['repair_projects']],
 ['维修直接消耗物资',2*repair['summary']['operational_summary']['repair_projects'],0],
 ['实际训练次数',sum(x['kind']=='training' for x in repair['receipts']),sum(x['kind']=='training' for x in leave['receipts'])],
 ['最终人物总经验',sum(repair['summary']['xp'].values()),sum(leave['summary']['xp'].values())],
 ['未修复的设备',repair['summary']['operational_summary']['unrepaired'],leave['summary']['operational_summary']['unrepaired']]]))
p('最终剩余物资差额不一定等于维修直接花费：维修占用了项目，可能因此少做消耗物资的训练。这里按实际账本分别列出，不能把这种机会成本藏起来。基本照护仍免费，维修不形成债务，不修也能到结局。')
p('保留的操作后果进入地区与人物结尾的事实记录；主世界结局、设备状态、连续服务、职业选择和未修复的失约分别判断。公开技术证据也不等于已经脱敏。新服务失败不会自动变成对执行者的怨气。')
p('本轮的服务成果是额外任务结果；设备维修的回报是恢复社区设备，不提供额外战力、好感或隐藏结局钥匙。参考结尾已分别输出“当时完成／错过窗口”和“原本保全／后来修复／未修复”。这部分价值包含叙事偏好；如果玩家只追求战斗成长，不维修就是合法选择，不能声称所有人都会愿意付出项目。')
add('<h2 id="fixes">推演中发现并处理的矛盾</h2>')
add(table(['问题','最终处理'],[
 ['为了保住服务，自动策略可能一直让低生命值的人硬撑','允许随时免费放弃额外机会；参考策略在值守者濒危时撤回，恢复主目标优先。玩家仍自主决定，危险与代价必须可见'],
 ['同一人先后摸两个位置可能冒充同时值守','每轮按实际操作者和位置登记，禁止一人承担两个同步点；中途离开不能结算'],
 ['保护作业可能被解释成免疫所有伤害','只允许一次非致命机器冲击不中断，仍扣真实HP；电击、水火、位移和失能不能被这条规则洗掉'],
 ['换人失败的旧值守贡献可能残留并刷信任','连续窗口中断时清空这次窗口的贡献；只把实际完成窗口的工作交给统一关系入口'],
 ['复位开关可能刷新其他机器预告或重复增援','只更新该设备的警告，保留其他预告与既有增援队列；复位花AP，不复活被拆毁的机器'],
 ['重机被牵离轨道，下一轮却沿旧轨道瞬移','普通推移与牵引统一处理离轨停驶，移回合法轨道才继续'],
 ['关系限制被泛化成任何场景都拒绝','按具体危险标签检查人物边界，再验证真正的锚点、绝缘、加固、撤退条件或明确授权'],
 ['修复设备可能顺手修复过去的失约','维修凭据明确只管设备；不补造服务、不返还怨气、不发新好感'],
 ['“有新选项”被当作“每个阵容都更有深度”','把任务目标差异、同队合作反事实、不同阵容办法和整局成本分开报告；未找到的路线仍列出，不当作数学上无解']]))
add('<h3>新机制如何提示而不打断</h3>')
p('保持每任务最多一张自动讲解的上限；首次预览值守时解释它是可放弃的成果。位置、剩余连续轮数、期限和供电关系常驻在目标信息中。只有即将拆毁指定可修复设备时，单独确认“失去设备完整性、维修可选且有成本”；不是每次攻击都弹一次。')
p('这轮验证的是提示触发记录和调度预算，不声称真实屏幕上的预览位置、阅读负担和遮挡已经验收。正式实现时仍须在提交动作前呈现后果，不能把离线日志里的事后记录当作玩家已经提前看见的提示。')
add('<h2 id="validation">检查结果和能够支持的结论</h2>')
add(table(['检查','结果','边界'],[
 ['36关／46种主目标选择',str(M['configurations'])+'个具名配置，'+str(M['attempts'])+'次实际策略尝试；基础无解记录'+str(len(M['unfound'])),'标准难度／天气A／固定出生槽位；不是全部技能、装备与位置的穷举'],
 ['高级合作改变成果的同条件对照',str(len(M['support_comparisons']))+'条保护／独立值守对照改变了服务是否完成','固定初始状态、值守位置和目标集合；不把单纯省AP计入这项数量'],
 ['三难度与两天气','12个新增机会×6环境＝72组，每组4条策略，基础办法均保留','林岚／许舟／苏棠固定3级的受控压力试验；早期实际成长另见整局，不承诺可选成果全拿'],
 ['整局',str(len(C['scenarios']))+'条完整战役、'+str(C['actual_battles'])+'场战斗','真实预算与成长；参考策略比较候选结果，具有事后信息，不能称为新手胜率'],
 ['定向规则与凭据检查',str(V['passed_count'])+'项通过','包含机器／电击、同步位置、训练与信任、复位、空间、服务窗口、实际维修和完整协议案例'],
 ['正式运行工程','脚本、场景、项目配置哈希一致','仅设计规范与离线参考推演；未进入正式开发或真人测试']]))
p('本轮可以支持的判断是：高级合作已有能够改变保留成果和后续安排的用途，通用装备与基本行动保留替代路线；不能扩大成“36关都已经同样精彩”或“玩家一定愿意重玩”。M01—M04的教学与S03、S05的短任务继续保留节奏职责，不靠强行加机制凑差异。')
add('<footer><a href="full-game-design.html">完整设计0.10</a> · <a href="approach-matrix-results.json">阵容与方案矩阵</a> · <a href="approach-campaign-results.json">整局凭据</a> · <a href="approach-protocol-witnesses.json">接力、普通交接、牵引与普通分工的完整行动</a> · <a href="approach-review-checks.json">检查及完整对照</a> · <a href="../game/data/final_design/approach_review_contract.json">当前权威修订</a></footer>')
style='''<style>*{box-sizing:border-box}body{margin:0;background:#eef3f0;color:#213d43;font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}main{max-width:1260px;margin:auto;background:white;padding:44px}h1{font-size:36px;line-height:1.35}h2{font-size:25px;border-top:3px solid #087e72;padding-top:18px;margin-top:48px}h3{margin-top:32px}.eyebrow,footer{font-size:13px;color:#526e72}.note{background:#e8f5ee;border-left:4px solid #087e72;padding:20px 24px;margin:24px 0}nav,.controls{display:flex;flex-wrap:wrap;gap:12px 22px;padding:18px 0}nav{border-block:1px solid #d3e0d9}a{color:#08776b}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0}th,td{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid #d3e0d9;min-width:95px}th{background:#edf5f0}input{font:inherit;padding:8px}footer{margin-top:40px}@media(max-width:760px){main{padding:22px}h1{font-size:28px}}@media print{main{padding:0}nav,.controls{display:none}}</style>'''
script='''<script>const filter=document.querySelector('#filter'),only=document.querySelector('#newonly');function update(){for(const row of document.querySelectorAll('#maps-table tbody tr'))row.hidden=!row.textContent.toLowerCase().includes(filter.value.toLowerCase())||(only.checked&&row.dataset.new!=='yes');}filter.addEventListener('input',update);only.addEventListener('change',update);</script>'''
(O/'approach-design-review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 阵容解法与高级合作0.10</title>'+style+'<main>'+'\n'.join(P)+'</main>'+script+'</html>')
section=f'''<section id="approach-review"><h2>阵容解法与高级合作 · 0.10</h2><p>12关新增可放弃的现场服务窗口；原主目标、基础动作与人物控制权保留。安全隔离、拆除后可选维修、保护值守、通用工具及改变设备位置分别承担不同代价。高级合作已有完整对照显示成果改变：M06接力保住限时档案；M22保护保住在线交接；M08可先停机、牵移再复位。</p><p>{M['configurations']}个具名配置、{M['attempts']}次策略尝试；另有72组难度/天气上下文、{len(C['scenarios'])}条整局和{V['passed_count']}项定向检查。仍只是设计推演，不是最终体验验收；没有启动正式开发。旧章节的范围与结论保留为历史记录，新机制以本修订为准。</p><p><a href="approach-design-review.html">查看36关回填、完整操作与整局机会成本</a> · <a href="approach-protocol-witnesses.json">协议完整行动凭据</a></p></section>'''
(O/'approach-review-section.html').write_text(section)
for file,values in [('game/docs/development.json',dict(date='2026-11-02',design_version='0.10-approach-review',latest_review='../../outputs/approach-design-review.html',project_stage='Design only. Operational alternatives, cooperation outcomes and optional equipment repairs reviewed offline; formal development remains paused.')),('game/data/product.json',dict(design_version='0.10-approach-review')),('game/docs/logic-audit.json',dict(current_revision='0.10-approach-review',approach_review_contract='data/final_design/approach_review_contract.json'))]:
 pth=ROOT/file;data=load(pth);data.update(values);pth.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Wrote0.10 approach report and master section.')
