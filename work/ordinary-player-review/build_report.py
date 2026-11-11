from pathlib import Path
import json,html,re,hashlib,collections
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design';O=ROOT/'outputs'
def read(p):return json.loads(p.read_text())
def esc(v):return html.escape(str(v))
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
# Reuse reader layout, not historical test results. Add current conditional variants.
src=(ROOT/'work/player-ready-review/build_report.py').read_text().split("M=read(O/'player-ready-matrix.json')")[0]
src=src.replace('中文剧本定稿基线1 · 0.15','中文剧本修订基线2 · 0.16').replace('href="player-ready-review.html"','href="ordinary-player-review.html"')
src=src.replace("('later_breach','后来再次违约')", "('later_breach_self','确证本人责任'),('later_breach_other','确证他方责任'),('later_breach_shared','确证共同责任'),('later_breach_unknown','原因尚未查清')")
needle="  for outcome,text in n.get('variants',{}).items():"
insert="""  if kind=='personal':
   body.append('<div class="choice"><b>暂时重伤：替换现场开场与选项回应</b>'+''.join('<p>'+esc(t)+'</p>' for t in n['injured_opening']))
   for choice,lines in n['injured_choices'].items():body.append('<p><b>'+esc(choice)+'</b>：'+esc(' / '.join(lines))+'</p>')
   body.append('<p class="muted">归责补句只用于角色已知、与本人相关的后续事件，并附实际事件摘要；不得替代履约凭据。</p></div>')
"""
src=src.replace(needle,insert+needle);scope={'__file__':str(ROOT/'work/player-ready-review/build_report.py')};exec(compile(src,str(ROOT/'work/player-ready-review/build_report.py'),'exec'),scope);page=scope['page']
C=read(O/'ordinary-player-after-campaigns.json');R=read(O/'ordinary-player-after-routes.json');G=read(O/'ordinary-player-growth.json');T=read(O/'ordinary-player-checks.json');P=read(O/'ordinary-player-opportunities.json');PB=read(O/'ordinary-player-before-opportunities.json')
names={x['id']:x['name'] for x in read(ROOT/'game/data/characters.json')};bn={'main_only':'只做主线','cautious':'谨慎推进','collector':'收集与投资','favorite':'偏爱固定人物','dismantler':'先拆威胁','mixed':'偶尔犹豫/晚出发'};en={'evacuation':'撤离','distributed_rebuild':'分布重建','shared_control':'共同监管'}
def span(vals):
 a,b=min(vals),max(vals);return str(a) if a==b else f'{a}–{b}'
def countwins(r):return sum(b['success'] for b in r['battles'])
parts=['<section id="ordinary-review"><p class="muted">夜潮事务所 · 0.16 · 2026-11-03 · 设计与离线审查，未进入正式开发</p><h1>普通走法能继续，<br>培养与提示必须有实际用处</h1><p>本轮保留走错一步、少拿奖励、偏爱角色、先买暂时用不到的工具、犹豫与晚撤离等行为。任务只执行预先指定的一种策略，不在结束后挑最好的结果。</p><nav><a href="#scope">覆盖范围</a><a href="#money">经济与疲劳</a><a href="#growth">培养是否值得</a><a href="#facts">对白与事实</a><a href="#missions">36关结果</a><a href="#limits">验证边界</a><a href="character-script-final.html">完整人物剧本</a><a href="full-game-design.html">整套设计</a></nav><div class="note"><b>结论：</b>当前样本没有经济卡死；训练推荐确实有过度催促的风险；前置失败、误购、贡献归属、承诺与兑现、重伤对白及失效提示已有具体修订。不能由自动通关推出“所有玩家都会觉得好玩”，也不把有限路线枚举称为所有操作序列穷尽。</div>']
parts.append('<h2 id="scope">实际测了什么</h2>'+table(['层次','实际数量','包含与限制'],[
 ['关卡目标与选择', '4,248次独立执行','108个已编写主目标/可选目标意图组合，6种行为、3难度、2环境，再含现场值守选择。受控三级初始队。'],
 ['阵容与等级','11,456次独立执行','46个主目标分支，1,432个日期合法三人组/分支情境，4种普通策略×三级/五级；标准难度A环境。不是这些维度与上一层的全笛卡尔积。'],
 ['真实整局',f"{len(C['scenarios'])}条 / {C['actual_battles']:,}场任务",'实际经验、加入日期、疲劳、项目、伤势、资金和消耗品串联；6行为×3难度×2环境×3结局意向。'],
 ['培养对照',f"{len(G['scenarios'])}条 / {G['actual_battles']}场任务",'5名后加入角色×2行为×不额外训练/临界训练/尽量每晚训练；全部保留真实成本。'],
 ['现场专长提示',f"{len(P['rows'])}情境 / {P['trials']}次执行",'M10/M21/S11、含叶禾合法阵容、三级/五级、标准/困难、A/B；提示前后各一次，不择优。'],
 ['对白状态',str(T['dialogue_combinations'])+'组合','24个人节点的选项×在场/重伤/离队×履约证据×7种知情归责情境；不是96场对白所有排列。'],
 ['规则与事务',str(T['passed'])+'项通过','包括原482项回归、实际选项保存、第三段选择门槛、依赖链、退款、退役道具入口和提示失效。']]))
parts.append('<p>整局中的“成功任务”采用较严口径：目标成立且三名队员健康撤出。任务报酬仍按实际完成和保全成果结算，因此“撤离慢导致任务测试失败”不等于所有报酬归零。失败样本保留，不重抽天气、不自动读档。</p>')
rows=[]
for be,label in bn.items():
 a=[r for r in C['scenarios'] if r['spec']['behavior']==be and r['spec']['difficulty']=='standard']
 rows.append([label,span([countwins(r) for r in a])+'/'+span([len(r['battles']) for r in a]),' / '.join(str(min(p['resources'][k] for r in a for p in r['pressure'])) for k in ['credits','supplies','parts']),' / '.join(span([r['summary']['resources'][k] for r in a]) for k in ['credits','supplies','parts']),span([sum(s.get('reason')=='side_window_expired' for s in r['skipped']) for r in a])])
parts.append('<h2 id="money">经济压力主要来自想全部兼得，疲劳更容易让人累</h2><p>下表每行是标准难度的6条整局，涵盖两种环境和三个结局。最低余额是每晚实际检查点的最低数，不冒充每笔交易中的最低瞬间。初始30资金/6物资/2零件。</p>'+table(['普通走法','成功/出勤任务','最低夜间资金/物资/零件','期末资金/物资/零件','每局支线过期'],rows))
parts.append('<p><b>无需为继续游戏刷支线。</b>只做主线、无后勤产出、无可选奖励的走法依然完成24主线，期末256资金；本轮不继续削减基础补助。全部108条整局均到第24关和结局，三种结局各36次。资金充足不代表全部设施都能买齐：零件、项目、出勤与机会仍有取舍。</p><p><b>收集走法的代价保留，但把原因讲清。</b>同时买五种工具、升工坊、习惯性训练的路线最低只有2资金/1物资，并因人手疲劳错过两条支线。已允许在原有次日截止前再次安排；不会第一天人手不足就把支线悄悄关掉。没有因此延长全局日历或保证全收集。</p>')
parts.append(table(['触发处境','已经修改的规则','防止新漏洞'],[
 ['误买工具','尚未参加任何新任务可撤销购买，返还这笔实际资金和零件；购买前显示近期用途','初始免费工具不可退钱；出勤后关闭退款；恢复原折扣，不能重复退款或套利。'],
 ['习惯性每天训练','默认正常出勤成长；只有已知下一任务有具体用途、能及时跨级、训练后仍能按计划出勤才给一次可选建议','不是见到经验临界就推荐；不设每日培养红点；不训练不扣好感。'],
 ['今日人手不足','支线入口明确保留到次日；显示次日可能出勤者及训练对疲劳的影响','过期是损失机会，不从任务清单静默消失，也不强制重开。'],
 ['低资源仍受伤','基础照护、自然恢复与主线借调继续存在；药剂花真实库存','不把每晚照护变成生存税；加速治疗仅在真的提前恢复时可选。'],
 ['历史道具残留','已删切割器不能购买；旧电池不能制作或装包','拒绝操作整笔回滚，不留下扣款和半次出勤。']]))
parts.append('<h2 id="growth">角色值得使用，不等于每天额外训练都值得</h2><p>五名后加入角色在“偏爱并持续出勤”的样本中，不额外训练也能达到五级；这不代表任意轮换都能如此。正常使用角色本身就是培养。我们不应靠压低自然经验，让玩家为了看到专长被迫付费训练。</p>')
small=[]
for who in ['chen','ye','he','mo','jiang']:
 a=[r for r in G['scenarios'] if r['spec']['training_actor']==who and r['spec']['behavior']=='favorite']
 for r in a:
  tr=sum(x['kind']=='training' for x in r['receipts']);small.append([names[who],{'none':'不额外训练','targeted':'临界训练','favorite':'尽量每晚训练'}[r['spec']['training']],str(tr)+'物资 / '+str(tr)+'项目 / '+str(8*tr)+'累计疲劳',r['summary']['levels'][who],f"{countwins(r)}/{len(r['battles'])}",sum(x['rounds'] for x in r['battles']),sum(x['damage'] for x in r['battles'])])
parts.append('<details open><summary>同样偏爱阵容，实际支付培养成本后的结果</summary>'+table(['角色','训练安排','额外成本','最终等级','成功任务','全局战斗轮数','累计受伤HP'],small)+'<p>累计疲劳是训练产生总量，睡眠与休息仍正常消除；不是结局疲劳。战斗轮数不是现实游玩分钟数，受伤HP不是重伤人数。</p></details>')
parts.append('<p><b>不漂亮的结果也保留：</b>叶禾的这条走法额外训练12晚，从五级到六级，仍为28/29成功、226轮、21受伤HP，没有明显回报。谨慎走法的陈砚临界训练两晚，成功任务反而29→28，说明跨级收益可能抵不过疲劳改变出勤。江朔一晚临界训练在此样本里结果不变，不能宣传为“推荐必做”。这些训练留作主动选择，系统不按经验数字催促。表中的“临界训练”只看经验，是用于暴露旧推荐问题的压力测试；修改后的推荐还须满足可见用途与出勤条件，当前尚未实现为正式游戏界面。</p>')
parts.append(table(['改动','具体价值','不能过度宣称'],[
 ['贺鸣五级屏障：3HP→5HP，持续整场','同一合法位置连续承受两次3伤害射线时，旧屏障后的队友8HP，新屏障11HP；更适合需要留在现场的路线','仍1AP、两次；不挡水火和爆炸；安全绕行时无需屏障。自然成长已可获得，不是付费训练专属。'],
 ['叶禾五级隔离：邻接→直线两格','保留供电而隔离危险输出，可不踏进相邻危险位置；仍2AP、一次','不能穿墙、机器、队友或屏障；既有火焰不消失。三组整局未证明它让所有普通路线更优。'],
 ['许舟与江朔的实际搬运贡献','抛索带人、远距交接按货物真实移动记入贡献，与步行共用规则','来回折返消除进度；不能通过重复交接刷关系或履约。'],
 ['其余专长维持分工','陈砚保全装置，莫遥远距处理已知开关，江朔接力；基础普通解法继续开放','没有新增指定角色门锁；苏棠仍较泛用、接力角色仍挑站位，不声称完全等强。']]))
for lev in [3,5]:
 a=[r for r in P['rows'] if r['level']==lev];old=[r for r in PB['rows'] if r['level']==lev]
 gained=sum(r['states']['True']['service_secured'] and not r['states']['False']['service_secured'] for r in a);lost=sum(r['states']['False']['success'] and not r['states']['True']['success'] for r in a)
 parts.append('<p>'+str(lev)+'级现场专长策略：192个情境中，隔离思路比原普通策略多完成'+str(gained)+'次现场值守；因该策略丢掉原本任务成功的情况为'+str(lost)+'次。<b>这比较的是完整行动策略，含移动、站位和其他技能，不是把全部收益归给叶禾技能或五级升级。</b>两种策略仍各有84个较难情境未达严格成功，额外服务不能抹掉出勤风险。</p>')
parts.append('<h2 id="facts">发现的事实矛盾与实际修复</h2>'+table(['问题','旧行为','当前规则与复现结果'],[
 ['M12前置目标失败','持续备份记录丢失，依赖它的备份盘带出任务一直“待办”，队伍等满15轮，0人健康撤出','依赖链同步标记不可达，保留其他目标与撤离；完全相同案例7轮、3人健康撤出，任务仍失败，不伪造成功。'],
 ['第1段人物选择','玩家选share，账本却写private','所有第一段选项保存实际ID；台词、后续判断与存档共用这次选择。'],
 ['莫遥的发布承诺','刚选择脱敏发布方案，就自动产生“已发布”凭据','许诺只建计划；后续另用1项目完成真实资料核验发布，或M22实际隐私处理。人物没有兑现就不读已经兑现的结尾。'],
 ['后续争执归责','出现冲突就让角色认错，可能认了别人造成的损失','已知责任分为本人/他人/共同/未知；未知不指定责任；没听说、与本人无关的事不强插对白。'],
 ['重伤人物的现场动作','休养期仍可能在开场搬运、值岗或立即接调度','个人节点使用休养开场和意愿回应，现场职责任务交接；恢复日期按伤势，读剧情不提前治好。'],
 ['离队与个人结尾','漂亮结尾可能与履约不足或人已离队冲突','实际第三段选项按证据门槛；离队只来信，不返回现场。已履约者也可以主动选职业距离/新生活。'],
 ['过时的示例提示','值守已完成，示例策略仍追电源，M10从7轮成功拖成13轮失败','完成/失败/过期即撤下该提示；同一M10恢复7轮成功。384情境中由该问题造成的8个新增失败归零。']]))
parts.append('<p>96场正文阅读稿已同步。其中2352组合检查针对24个人节点的条件选句；社区与章末叙事继续按实际保全事实选择，原结构回归已重跑。归责补句是事件事实说明，不能替代角色各自的核心对白。没有真人通读或实际游戏UI，本轮不宣称文学质量与呈现节奏已验收。</p>')
parts.append('<h2 id="missions">36关逐关汇总：保留失败，不靠降低要求做满分</h2><p>以下为15,704次固定策略执行的逐关计数。前两列含不同难度和可选目标意图，后一组为标准难度A、全部日期合法三人组、三级与五级。它们是覆盖计数，不是玩家胜率。</p>')
missionrows=[]
for mid in dict.fromkeys(r['mission'] for r in R['rows']):
 a=[r for r in R['rows'] if r['mission']==mid and r['layer']=='structural'];b=[r for r in R['rows'] if r['mission']==mid and r['layer']=='rosters'];s=[r for r in a if r['difficulty']=='standard'];missionrows.append([mid,f"{sum(x['success'] for x in a)}/{len(a)}",f"{sum(x['success'] for x in s)}/{len(s)}",f"{sum(x['success'] for x in b)}/{len(b)}"])
parts.append(table(['关卡','目标/行为全难度成功','其中标准难度成功','合法阵容三级/五级成功'],missionrows))
parts.append('<p>仍有失败集中在持续保全、困难难度额外值守、晚撤离和多目标贪取。没有为让每种走法都成功而增加装置HP或延长倒计时。持续保全装置即使施工完成，也须继续显示受威胁状态；不能用绿色完成勾号误导玩家已经永久安全。M05阵容矩阵仍有6次失败，应通过目标保护/撤离取舍处理，不据此强制带某个人。</p><p>全体阵容均至少有一种所测普通策略成功：这是本轮要核验的“没有必须换成指定阵容才能继续”，不是“任意操作都能获胜”。实际成立与否由最后的覆盖断言检查，不用平均成功数遮掩无解组。</p>')
parts.append('<h2 id="limits">本轮能确认与不能确认的边界</h2><p>本轮完成设计规则、脚本条件和可复现离线执行的修订。有限的所有已编写目标组合已覆盖，阵容按另一条轴覆盖；未穷尽每一格移动、任意事件顺序、全部关系状态与所有装备的联合组合。路径仍使用合法最短路求解，人物台词检查仍是确定性的条件检查，不等于邀请了普通玩家。</p><p>提示内容、撤销入口和预览是明确的最终版设计要求，正式鼠标界面尚未实现。HTML做结构、链接和脚本语法检查；本地浏览器预览曾被URL安全策略阻止，本轮没有绕过该限制，也不声称已做视觉验收。</p><div class="note">目前保留的关键风险：额外训练的泛用价值低于自然出勤；部分低风险路线保护职业存在感较低；完整收集可能消耗更多现实时间。已通过可选培养、具体专长用途、可撤销误购、清晰疲劳预览处理可判定的问题。真实的阅读负担、点击疲劳和人物吸引力仍需成品界面及玩家测试，不能通过加大自动测试次数证明。</div>')
links=['ordinary-player-after-routes.json','ordinary-player-after-campaigns.json','ordinary-player-growth.json','ordinary-player-opportunities.json','ordinary-player-checks.json','ordinary-player-before-bugs.json','ordinary-player-inputs.json','ordinary-player-final-checks.json']
parts.append('<footer><p>'+ ' · '.join('<a href="'+f+'">'+f+'</a>' for f in links)+'</p><p>当前领域权威入口：<a href="../game/data/final_design/design_manifest.json">design_manifest.json</a>。历史0.15报告保留作对照；本报告明确修订处以0.16为准。正式Godot文件不变。</p></footer></section>')
section='\n'.join(parts)
for anchor in ['scope','money','growth','facts','missions','limits']:section=section.replace('id="'+anchor+'"','id="ordinary-'+anchor+'"').replace('href="#'+anchor+'"','href="#ordinary-'+anchor+'"')
(O/'ordinary-player-section.html').write_text(section);(O/'ordinary-player-review.html').write_text(page('夜潮事务所 · 普通玩家全流程审查0.16',section))
p=O/'full-game-design.html';master=p.read_text();master=re.sub(r'<!-- ORDINARY_START -->.*?<!-- ORDINARY_END -->','',master,flags=re.S)
if '<details id="historical-015">' not in master:master=re.sub(r'<!-- PLAYER_READY_START -->(.*?)<!-- PLAYER_READY_END -->',r'<details id="historical-015"><summary>历史0.15：人物定稿与经济基础；普通走法、条件对白和成长修订以0.16为准</summary>\1</details>',master,flags=re.S)
master=master.replace('<main>','<main><!-- ORDINARY_START -->'+section+'<!-- ORDINARY_END -->',1).replace('可实施设计 0.15','可实施设计 0.16');p.write_text(master)
proof={'version':'0.16','design_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'game/data/campaign_economy_contract.json',ROOT/'game/data/characters.json']+sorted(F.glob('*.json'))},'reference_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'work/growth-identity-review/model.py',ROOT/'work/growth-identity-review/relationships.py',ROOT/'work/campaign-review/ledger_review.py']+sorted((ROOT/'work/ordinary-player-review').glob('*.py'))},'formal_runtime_changed':False}
(O/'ordinary-player-inputs.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print('Built0.16report and96scene reader')
