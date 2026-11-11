"""Current reader generated from the frozen baseline, never from patch history."""
from pathlib import Path
from html import escape as e
import json
R=Path(__file__).resolve().parents[2];F=R/'game/data/final_design';O=R/'outputs'
B=json.loads((F/'release_baseline.json').read_text());D=B['domains'];C=json.loads((O/'predevelopment-checks.json').read_text())
def text(v):return e(str(v))
def render(v):
 if isinstance(v,dict):return '<dl>'+''.join('<dt>'+text(k)+'</dt><dd>'+render(x)+'</dd>' for k,x in v.items())+'</dl>'
 if isinstance(v,list):return '<ol>'+''.join('<li>'+render(x)+'</li>' for x in v)+'</ol>'
 return '<span>'+('是' if v is True else '否' if v is False else '无 / 不适用' if v is None else text(v))+'</span>'
def table(headers,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+text(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+text(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def sec(id,title,body):return '<section id="'+id+'"><h2>'+title+'</h2>'+body+'</section>'
CSS='''*{box-sizing:border-box}body{margin:0;background:#f3f4f1;color:#21312f;font:16px/1.75 system-ui,"PingFang SC",sans-serif}main{max-width:1180px;margin:auto;padding:36px 28px 80px}h1{font-size:34px;line-height:1.25}h2{font-size:24px;margin:0 0 20px}h3{font-size:19px}p{max-width:940px}.eyebrow{color:#486961;font-size:14px;letter-spacing:1px}.lead{font-size:20px}.note{background:#fff5d8;border-left:4px solid #c68b24;padding:16px 22px}.good{background:#e6eee7;border-left:4px solid #487a5a;padding:16px 22px}nav{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}a{color:#1b6769;text-decoration-thickness:1px;text-underline-offset:3px}nav a{padding:6px 12px;background:white;border:1px solid #d9e1da;border-radius:5px}section{background:white;border:1px solid #dce2da;border-radius:10px;margin:22px 0;padding:26px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:11px 13px;border:1px solid #dce2da;text-align:left;vertical-align:top}th{background:#eef2ec}.scroll{overflow-x:auto}details{border-top:1px solid #dce2da;padding:14px 0}summary{cursor:pointer;color:#235b50;font-weight:650}dl{margin:8px 0}dt{font-weight:650;color:#47685c;margin-top:12px;overflow-wrap:anywhere}dd{margin:2px 0 12px 18px;border-left:2px solid #e1e8df;padding-left:16px}ol{padding-left:25px}li{margin-bottom:8px}code{overflow-wrap:anywhere}footer{font-size:13px;color:#60756b}.flow{padding:18px;background:#eef2ec;line-height:2.2}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}.card{padding:18px;border:1px solid #dce2da;border-radius:6px}small{color:#64786d}@media(max-width:650px){main{padding:20px 12px}section{padding:18px}h1{font-size:28px}dd{margin-left:5px;padding-left:8px}}'''
def page(title,body,nav=''):
 return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+' · 0.18</title><style>'+CSS+'</style></head><body><main><div class="eyebrow">夜潮事务所 · 0.18 开发前基线 · 2026-11-04</div><h1>'+title+'</h1>'+nav+body+'<footer>由当前 release_baseline.json 生成。旧版审查是历史证据，不能覆盖本版。HTML已检查结构和本地链接；本轮没有浏览器视觉验收，也没有正式游戏UI或真人试玩验收。</footer></main></body></html>'
nav='<nav>'+''.join('<a href="#'+k+'">'+v+'</a>' for k,v in [('decision','开工判断'),('game','产品范围'),('flow','完整流程'),('people','人物与培养'),('maps','36关'),('production','制作清单'),('acceptance','验收'),('rules','完整规则')])+'</nav>'
body=sec('decision','当前结论','<p class="lead">设计层面可以进入同一最终项目的开发；本轮没有启动正式开发。</p><p>已处理13类版本、规则或实现口径冲突，未发现仍须用户先决定的基础玩法阻碍。当前仍有正式集成、美术质量和真实玩家理解等交付风险；这些必须通过下述生产验收解决，不能由纸面审查宣称已消除。</p><div class="good">本轮重跑1174项离线规则检查，以及108组整局、3420场战斗，覆盖全部36图。战斗结果、最终状态及中间资源/疲劳记录与0.17对应组一致；跨进程贡献排序与贺鸣履约条件另有专项检查。</div><p><a href="predevelopment-review.html">查看本轮冲突修订与具体案例</a> · <a href="predevelopment-checks.json">查看实际检查记录</a> · <a href="../game/data/final_design/design_manifest.json">唯一版本入口</a></p>')
body+=sec('game','产品和首发边界','<p>离线单机群像成长与回合制救援。玩家经营民间救援事务所，选择三人出勤，在洪灾中的失控设备、居民、设施和证据之间作取舍；任务经历会改变人物关系、培养机会和战后去向。关系提供共同带教和接应安排，也产生具体条件，不只扣分或换对白。</p>'+table(['维度','定稿'],[
 ['战斗形式','俯视2D、固定8×8网格、三人各2AP交错行动；敌人与环境按已知预告结算'],['养成','8角色，每人2项能力；L5强化既有用途；7工具+1药剂，无额外武器树'],['战役','4章、24主线、12可选支线，24日/23营地夜；96完整场景不等于一周目全部发生'],['合作','4项免费情境协作；无独立高级合作培养树或统一信任门槛'],['失败','仍然走到结局，失去资源/机会/好结果；常规难度重伤，严峻难度明示救援期限后的永久医疗离队'],['首发','Windows 11 x64、键鼠、简体中文；Godot 4.7.2/GDScript/Compatibility'],['商业边界','买断方向；本轮不定价、不接商店SDK、不处理发行'],['时长','12–16小时仅未实测的内容节奏目标；不为时长重复劳动，不据此承诺售价或退款表现']])+render(D['release_scope']['not_in_first_release']))
body+=sec('flow','从开局到结局的完整流程','<div class="flow">主菜单 → 新局/有效存档 → 晨间简报 → 配队与出勤快照 → 主线战斗 → 唯一结算 → 可选支线/延期/跳过 → 营地2项目＋2短谈 → 一次夜间恢复 → 下一日<br>D23最后安排 → D24终战准备 → 实际目标结算 → 世界、地区、人物四层结局 → 只读回顾/新存档</div>'+table(['容易遗漏的节点','明确处理'],[
 ['无钱/无人可出勤','基本生活免费，主线借调补真实空位，免费动作/恢复继续；支线不借调，可跳过'],['支线今天不打','保留至次日、最多D23；每天只一场；已出发再撤退也算已尝试'],['目标已永久失败','一次提示依赖链失效，仍能保其他成果或撤退；不锁玩家等到超时'],['难度变更','仅出发前允许，按部署快照生效；不撤销已发生伤亡，严峻首次明示确认'],['AP用完','不自动结束；0AP可放下或紧急撤退，正常出口离场仍需1AP'],['读档坏了/版本不兼容','保留原档，显示原因与备份；可选另一槽或返回，不静默覆盖'],['最后一晚','仅一次未处理事项/路线条件提示，玩家确认结束D23；D24没有补开的训练或核查'],['后续破约/重伤','分别叠加关系后果/医疗状态；已履约历史和职业方向不会被总标签抹掉']])+ '<details><summary>完整暂停、保存、难度及流程规则</summary>'+render(D['player_flow'])+'</details>')
people='<div class="grid">'
for a in D['characters']:
 people+='<article class="card"><h3>'+text(a['name'])+' · D'+str(a['join'])+'</h3><strong>'+text(a['role'])+'</strong><p>'+text(a['past'])+'</p><p>想要：'+text(a['want'])+'</p><p>日常：'+text(a['ordinary'])+'</p><p>矛盾：'+text(a['flaw'])+'</p></article>'
people+='</div><h3>培养的实际取舍</h3>'+table(['方式','收益','成本与限制'],[
 ['自然出勤','主线5/3/1XP，支线3/1/0，后勤2；阈值0/12/28/48/72/100','保持原收益，不为训练有用而削弱'],['普通训练','每人最多+12XP；可提早获得下一能力','每人1物资、+6疲劳，1–2人共享1项目；入队后每章1课程，可积存'],['共同带教','学员最多+24，不超过导师或100','2物资、1项目、两人各+6疲劳；实际收益大于普通训练才提供，共用课程及每章学员限次'],['自然恢复/专门休息','保住下一次出勤资格和项目安排','训练还要比较放弃休息的机会成本，不能只看跨级'],['共同接应','替换为东侧出口，改变搬运路径和风险分配','需要真实约定与共同经历、现场/后勤分工，2物资并放弃常规后勤1物资收益'],['专业距离','仍可完成主线、普通培养及人物职业结局','不开放需双方同意的共同计划；不因拒绝亲密扣基础能力']])
people+='<p><a href="character-script-final.html">阅读96场景完整剧本与条件</a>。8人各2套服装、8种表情语义差分；人物吸引力的实际画面仍需样张验收。</p><details><summary>情绪、归责、记忆和修复算法</summary>'+render(D['progression_relationship'])+render(D['experience']['appraisal'])+'</details>'
body+=sec('people','人物、培养和关系',people)
rows=[]
for b in D['boards']['boards']:
 labels={x['id']:x['label'] for x in b['objectives']};goals='；'.join(' / '.join(labels[x] for x in g) for g in b['mandatory_groups'])
 rows.append([b['id']+' '+b['title'],'D'+str(b['day']),goals,D['field_operations']['mission_roles'][b['id']],b['decision']])
body+=sec('maps','36关的目标和不同处理思路','<p>每行对应已著写地图、目标前置、敌人、预告、环境变体和后果。表格是阅读索引；完整坐标、各世界路线目标组和奖励对象见下方boards/economy域。不同解法不要求强行更换阵容，额外成果可放弃。</p>'+table(['关卡','开放','主目标组','关卡作用/额外选择','现场取舍'],rows))
scope=D['release_scope']
prod='<p>由我们两人推进；外部采购或雇人不作为隐含前提。生成、挑选、修图、许可核验和实机反馈仍是工作，不能把“AI生成”算作零工时。</p>'+table(['资产','数量','具体内容'],[(a['unit'],a['quantity'],a['detail']) for a in scope['assets']])
prod+='<h3>16个界面/功能页</h3>'+table(['ID','界面','必要信息'],scope['screens'])
prod+='<h3>正式项目内的制作顺序</h3>'+table(['阶段','产出','内容','退出条件'],scope['production_milestones'])
prod+='<details><summary>分工、成本口径、架构与美术验收</summary>'+render({k:scope[k] for k in ['work_allocation','cost_model','architecture','asset_quality','platform']})+'</details>'
body+=sec('production','制作范围、资产和分工',prod)
body+=sec('acceptance','什么算可以开工，什么算可以交付','<p>D项是设计准入；本轮只有这些检查有离线证据。R项是正式程序/资产验收，H项是真人体验；后两类全部待做。测试数量不替代玩家喜欢，也不宣称全部路线已穷举。</p>'+table(['编号','领域','通过标准','当前阶段'],[(c['id'],c['area'],c['pass_condition'],'本轮静态/离线检查，详见记录' if c['status']=='current_check' else '待正式程序/真人/资产验收') for c in D['acceptance']['criteria']])+ '<details><summary>36条原始需求到验收标准的对应</summary>'+table(['需求','名称','验收编号'],[(r['id'],r['title'],', '.join(r['acceptance_ids'])) for r in D['requirements']])+'</details>')
titles={'scope':'核心范围','economy':'资金、物资与奖励','product':'产品定义','confirmed_policy':'用户已确认边界','characters':'角色数据','initial_relationships':'初始有向关系','abilities':'16项专业能力','enemies':'6种机器','equipment':'7种工具与药剂','facilities':'4类设施','combat':'战斗精确规则','progression_relationship':'成长、曲线、记忆与冲突','growth':'角色差异和正向关系','training':'课程与带教','experience':'性格评价、引导与视觉','field_operations':'现场操作和限期设施','world':'地区与世界后果','coordination':'日程协调','campaign':'整局账本','integration':'人物凭据和结局整合','stories':'96节点触发与分支','scripts':'96场景正文','boards':'36地图详细配置','player_readiness':'玩家交互','persistence_inventory':'完整保存字段','player_flow':'完整流程','release_scope':'首发制作清单','acceptance':'验收标准','decisions':'本轮解决的矛盾','compatibility_rules':'兼容规则视图','mission_index':'任务索引','requirements':'需求映射'}
allrules='<p>以下直接读取唯一基线的全部32个领域，不依赖历代补丁覆盖。领域JSON是导出视图；更改时应从基线统一生成并检查一致性。</p><p><a href="../game/data/final_design/release_baseline.json">下载/读取完整JSON基线</a> · <a href="../game/data/final_design/design_manifest.json">领域与投影视图清单</a></p>'
for key,value in D.items():allrules+='<details id="domain-'+key+'"><summary>'+text(titles.get(key,key))+' · '+text(key)+'</summary>'+render(value)+'</details>'
body+=sec('rules','完整当前规则',allrules)
(O/'full-game-design.html').write_text(page('最终版设计基线与开发验收手册',body,nav))
review='<p class="lead">完成版本统一、流程收口、首发范围和验收标准四项审查。没有已知的设计层开工阻碍；尚未开始正式开发。</p><p>这不是对“永远不会出现逻辑问题”的保证。验证覆盖的是明确输入和有限策略；真正的交互、内容节奏和人物吸引力需要在正式产品中验收。</p>'
review+=sec('changes','本轮直接解决的13类问题',table(['编号','冲突','旧问题','定稿处理'],[(x['id'],x['topic'],x['conflict'],x['resolution']) for x in D['decisions']['resolved']]))
review+=sec('evidence','实际跑过的验证',table(['检查','实际结果','边界'],[
 ['规则回归','1174项通过','含合法/非法交易、全部脚本选项、事件归责、补救、训练上限；是离线模型'],['整局回归','108组、3420场、覆盖36图','六种行为偏好×三难度×两环境×三世界路线；不是108名玩家'],['与0.17对应组比较','战斗结果、最终状态、中间资源/疲劳记录一致','新改口径未偷偷降低自然成长；不代表所有可能路线都相同'],['新增专项','按角色L2、跨进程贡献排序、贺鸣证据、流程图、字段/引用/版本检查通过','详细逐条结果见JSON，模板流程检查不等于UI已实现'],['正式代码边界','所有.gd、.tscn和project.godot的哈希与审查前一致','只改设计数据、离线验证工具和文档'],['本地引擎','--version确认4.7.2.stable.official.ed1daf0bf','只确认现有工具链，不把它当完整游戏运行测试']])+ '<p><a href="predevelopment-checks.json">当前检查明细与指纹</a> · <a href="predevelopment-rule-checks.json">1174项规则明细</a> · <a href="predevelopment-campaigns.json">108局逐关记录</a></p>')
review+=sec('cases','具体案例及判定',table(['案例','修订或预期','验证性质与结果'],[
 ['M02回收备用组件','先断路再人工恢复电源；组件带回只发2零件，不存在电池消耗捷径','数据奖励引用及重复结算拒绝检查通过；36图经济回归保持原结果'],['贺鸣先协助一下，另一人继续做目标，贺鸣再保护并全队撤出','不因他排在贡献名单第一就否认放手；必须实际存在他人贡献','正例通过；仅伪造primary字段、无他人贡献、无保护、不同任务和未撤出五个反例均被拒绝'],['同一运输路径在不同进程重放','按有效贡献先后稳定记录，不能由集合顺序指定首位','5个hash seed的旧逻辑输出不同；修订后全为同一顺序'],['XP66、疲劳90时训练','经验到78跨L5，但训练+6、夜间−12后84，再出勤+18=102不可部署；专门恢复则下一次84可出勤','回归中的实际账本边界检查通过；需要向玩家同时显示经验和疲劳取舍'],['资金0且所有已入队主角不可用，连续主线失败','免费借调与保底允许到D24撤离结局；不会假造个人角色在场','24日账本边界检查通过；这是给定失败结果的账本测试，不是证明三借调能救全目标'],['居民已救出但陈砚重伤','目标成功、人员受伤、个人压力、承诺状态分别显示','结果语义已定稿；正式界面的文字/反馈组合仍列R05/R06待验收']]))
review+=sec('gate','剩余风险和开发判断','<div class="good"><strong>没有仍需你先拍板的基础设计阻碍。</strong>以后进入开发时沿用同一个最终项目，从可保存的完整循环逐步接入36关；各阶段实现保留进最终版。</div><p>仍未通过的部分：正式战役集成、预览执行一致性、完整存档及Windows实机验证；最终角色/场景/声音资产；新玩家引导、真实培养选择和整局疲劳感。这些是接下来开发必须完成的验收，当前不能宣称产品已好玩或已能发布。</p><p>当前指令仍是“暂不进入正式开发”，因此本轮止于可实施设计与验收基线，不创建战斗界面或控制器。</p><p><a href="full-game-design.html">打开完整当前手册</a> · <a href="character-script-final.html">打开96场景剧本</a> · <a href="full-game-design-v017.html">0.17历史快照（不再作为现行规则）</a></p>')
(O/'predevelopment-review.html').write_text(page('最后一次开发前审查',review))
scripts='<p>96场景完整中文正文与条件数据；触发/付款/真实履约由当前规则判断，台词不能凭空生成证据。正文已有，最终文学审读与演出仍未验收。</p><p><a href="full-game-design.html#people">返回当前设计手册</a></p>'
for key,title in [('profiles','人物底稿'),('personal','24段个人线'),('relationships','12段关系线'),('life','18段生活场景'),('community','24段社区回应'),('chapter','18段章节事件')]:
 content=D['scripts'][key]
 if isinstance(content,dict):scripts+=sec('script-'+key,title,render(content));continue
 chunk=''
 for node in content:chunk+='<details id="scene-'+node['id']+'"><summary>'+text(node['id']+' · '+node.get('title',node.get('actor','')))+'</summary>'+render(node)+'</details>'
 scripts+=sec('script-'+key,title,chunk)
(O/'character-script-final.html').write_text(page('人物剧本全文与分支条件',scripts))
print('Generated current handbook, audit, and96-scene reader from one baseline')
