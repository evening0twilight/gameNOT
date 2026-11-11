"""Readable evidence report, generated from the revised design and executed checks."""
from pathlib import Path
from collections import Counter
import json,html
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data/final_design'
R=json.loads((O/'system-audit-results.json').read_text());C=json.loads((D/'system_audit_contract.json').read_text());L=json.loads((O/'whole-campaign-review.json').read_text())
def e(v):return html.escape(str(v))
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
findings=[
 ('01','关系','满值只截显示，实际记忆可能远大于100；补救后仍100','真实活跃权重限制在100-G；保留事实，不保留隐藏数值债；普通同类被归档条目也不回填','数值反例＋8000次状态转换'),
 ('02','关系','严重记忆公式一处用max(衰减,35%)，一处用35%+65%衰减','统一混合残余公式；40强度第8天应27，不是20；补救后去残余','数值回归'),
 ('03','归责','同一个决定导致伤势、撤离失利、治疗延迟，可能被算三次','按源决定＋观察者＋责任对象合并；新隐瞒须是新决定；后果升级只补差额','合并、修订、重复、误归责纠正回归'),
 ('04','归责','全局事件ID去重可能挡掉第二个合法责任方向','同事件允许林岚→队长与林岚→提议者各一条；同方向重复提交无效','真实账本两方向回归'),
 ('05','合作','已有队长归责，但现场只检查搭档；退出阈值未被真正使用','查对搭档和队长两方向；保存阶段，退出严格按<35/<50/<60','账本回归＋40804种阶段输入'),
 ('06','冲突','长场景冷却与持续拒绝没有明确分离','两天只限制重复长场景；条件持续。到期本身不插戏，需要新的相关触发；一任务全队最多1次','冷却边界与顺序回归'),
 ('07','战斗','携带失能者是否暂停期限、最后一轮救回/超时先后不明','携带不暂停；送达在期限判定前；到期转运清携带槽；稳定只延1轮','期限优先级参考；0.7另补棋盘搬运、掉落与实际送达检查'),
 ('08','战斗','失能伤害文本与救援计时规则冲突；物件叠格可能无处放下','失能队员只计救援时限；平民仍有HP。同格允许多个地面对象，以对象ID选择','状态规范修订；动态空间组合尚需实现后验证'),
 ('09','战斗','携带禁推/禁技能可能被双人协议绕过；重机推力可疑跨轮累积','明确携带动作白名单，接力是唯一携带协议；重机同轮同方向两次推力，位移/换轮清零','规范修订；尚未覆盖全部技能实战'),
 ('10','资源','任意ID都能制作，耗材可能按零价格当永久工具买；数量接受小数/布尔值','配方、解锁、槽位、正整数全检；失败回滚全部账本','真实制作/购买/结算拒绝回归'),
 ('11','成长','未知协议也可能付费写入学习记录；已学与装备槽概念混在一起','只认4项定义；学习按人物对，装备按协议种类占槽；低风险学习与现场使用分离','未知协议与重复学习回归；槽位规则明确'),
 ('12','设施','通信台二级脚本让D18也查两份，与设施定义不符；重复证据未拒绝','D18最多1份，D20/22/23可2份；证据名单必须互异','真实核查回归'),
 ('13','人物','苏棠两次主线可能混入支线；仅安排后勤就算完成','两次不同主任务＋至少一条匹配的真实他人后勤回执','人物验证器正反案例'),
 ('14','人物','许舟撤离守约字段缺失被默认true；贺鸣全员撤回被写成无人受伤','缺凭据不发信用；被实际带回的重伤队友也算带回','账本＋人物验证器回归'),
 ('15','人物','晚到的计划仍收费，但剩余关卡可能无法兑现；林岚对白比验证器多一个隐含时限','按后续实际任务给最晚承诺日；迟读保留完整专业选择；时限须单独明确承诺','关卡数据＋拒绝/专业替代回归'),
 ('16','结局','兑现后医疗离队可能抹掉完成记录；一个关系破裂标签影响全部关系','已完成事项、持续义务、职业、在队状态、有向关系分别记录；具体补救只解决原事件','完成后离队、后续泄密、局部修复回归'),
 ('17','叙事','永久离队仍可能读出双人现场；M24社区回访似乎需要不存在的晚间','缺席用有据来信/摘要，不发共同经历；M24内容放结局档案','场景回归＋内容引用检查'),
 ('18','世界','结局结果包可夹带别条路线目标，世界资格与关卡成果脱节','先锁路线，只接收该路线对象与archive；M17隔离同时截当前地区值和上限','错误路线/地区门槛/部分撤离回归')]
parts=[]
def add(x):parts.append(x)
add('<section id="system-audit"><h2>系统性逻辑审查 · 0.6</h2><p class="muted">2026-11-01 · 设计修订与参考验证 · 正式开发仍暂停</p>')
add('<div class="note"><b>结论：</b>本轮记录并处理了18组矛盾或未定义边界。包括可在旧验证脚本中复现的缺陷，也包括此前只有口头概念、没有完整操作规则的地方。下表逐项区分“已执行回归”与“规则已明确但未执行全部战斗组合”，不把两者混为已证实可玩。</div>')
add('<p>核对链路：具体决策与知情 → 战斗对象/救援事实 → 成果与消耗结算 → 经验、伤势、疲劳与关系 → 营地安排及人物计划 → 次日任务/地区 → 世界路线和人物后记。各模块不能自行生成互不一致的“成功”。</p>')
add(table(['编号','系统','原问题','采用的修订','验证程度'],findings))
add('<h3>满值案例：补救不再被隐藏的怨气吞掉</h3>')
x=R['examples'][0]
add('<p>旧怨42，三条严重事件各40。旧规则把实际162显示成100；把其中一条补救到原来的45%后，实际仍140，因此显示还为100。玩家确实做了补救，却看不出效果。</p>')
add(table(['方案','补救前显示','补救后显示','剩余事实'],[['旧截断规则',x['old_before'],x['old_after'],'有隐藏超额负担'],['0.6活跃权重分配',x['new_before'],x['new_after'],'三件事仍留档；仅被针对的那件标记补救，另外两件未解决']]))
add('<p>86.98仍是高怨，不意味着立即和好。保障条件可能继续存在；界面能解释剩余来源和下一步。新增恶意仍会扣实际信任、留下新事实并影响后记，但不会在100背后再堆一个200。</p>')
add('<h3>从一场事故到后续结局的具体案例</h3>')
cases=[
 ('队长要求追加一趟，林岚受伤且没赶上原约定撤离','若许舟只是执行者：林岚→队长建立一次违约记忆，许舟不背责；伤势和压力另算，不把延迟治疗再复制为第二份怨。若许舟知情并主动提议，两责任方向各承担0.5。'),
 ('第6天爆发，第7天又安排危险协作','不会再播长冲突，但缺少真实保护仍拒绝这项高级合作。基础移动/独立救援可执行。第8天仅因冷却到期也不突然插戏；新的相关请求才可能触发。'),
 ('失能者最后期限第6轮，队友第6轮玩家阶段送到出口','先记送达、清携带槽，再做轮末期限检查。最高难度也是可恢复重伤；如果仅在背上未送到，期限继续，不能靠拾起规避最高难度代价。'),
 ('许舟参与任务成功，但没有按约定时间撤出凭据','成功奖励可以发，个人撤离承诺不能自动判兑现；战斗成功、人员带回、是否按约定时限是三个不同事实。'),
 ('第22晚才读到陈砚的补偿施工计划','M23没有work对象，不能收8资金后等玩家落空。该计划在0.7收紧至D20；M22只有记录类work，不能冒充施工；D21以后仍可选完整专业分支。苏棠需两次后续主任务，同样最迟D21。'),
 ('林岚已兑现轮换计划，后来在最高难度永久医疗离队','尾声保留“曾兑现轮换”的事实，呈现长期康复；不再让她出现在现场双人对话，不把过去的履约改成未完成。'),
 ('莫遥曾完成脱敏公开，但之后玩家又公开未脱敏资料','保留曾完成的工作，同时标记后续持续义务被破坏；不能用早期温暖结语洗掉新行为，也不取消她已选的战后职业。'),
 ('终战只救出了r1，r2没送达','使用带具体损失的撤离后记，保留r1获救；不会因全关未成功把r1抹掉，也不会播放“两批人都获救”。')]
add(table(['玩家经历','现在的结算和反馈'],cases))
add('<h3>已执行的检查</h3>')
counts=Counter(x['group'] for x in R['checks'])
labels={'memory':'记忆与补救','attribution':'归责与事件去重','conflict':'阶段、冷却与合作','combat':'救援时序参考','transaction':'错误操作整体拒绝','economy':'资源与设施','story':'人物计划与缺席','ending':'人物后记','world':'地区与终局','properties':'组合不变量','content':'关卡/叙事引用','scope':'开发边界'}
add(table(['本轮检查类别','通过的具名断言'],[[labels.get(k,k),v] for k,v in counts.items()]))
add('<p>本轮共<b>'+str(R['passed_count'])+'项具名断言</b>。其中组合检查额外遍历8000次固定随机种子的关系状态转换，以及40804种阶段/怨气/压力输入；它们是两个性质测试的样本量，不能说成48804个独立玩法已验证。保留每条断言及案例输出，失败会停止构建。</p>')
add(table(['既有检查重新运行','通过数/范围'],[['内容、基础路径与分支',str(R['existing_suites']['content'])+'项；36关、46种主目标组合、224种人物选择/缺席路径'],['人物承诺',str(R['existing_suites']['story'])+'项'],['整局统一账本',str(R['existing_suites']['ledger'])+'项；3个24日情境＋2个医疗耗材敏感性情境'],['装备目标/开放时机',str(R['existing_suites']['equipment'])+'项'],['M02战斗参考','基础/2级施工/电池三种固定操作；没有扩称为36关实战']]))
add('<h3>整局后果是否还能接到结局</h3>')
rows=[]
for scenario in L['scenarios']:
 x=scenario['summary'];rows.append([x['name'],f"{x['main_count']}主线/{x['side_count']}支线",x['world_ending'],len(x['withdrawn']),'/'.join(str(x['resources'][k]) for k in ['credits','supplies','parts'])])
add(table(['给定结果的推演情境','完成任务','世界收束','永久医疗离队','结束资金/物资/零件'],rows))
add('<p>极端失败情境能继续到结局，不代表玩家能保住好的结果：8名主要人物均进入医疗离队收束，依靠仅填空位的社区人员继续主线。反过来，常规情境资金有结余，当前主要限制是人员与晚间项目，不能把它宣传成已经平衡的生存经济。</p>')
add('<h3>修订后的完整规则</h3>')
section_names={'memory_budget':'记忆、满值与修复','attribution':'归责与知情','conflict_state':'情绪阶段与冷却','combat_resolution':'战斗、携带、时限和装备','economy_growth':'资源、训练与设施','story_and_ending':'人物分支与结局','validation_boundary':'验证边界'}
for key,rows in C['sections'].items():
 add('<details><summary>'+e(section_names[key])+'</summary>'+''.join('<p><b>'+e(k)+'</b>：'+e(v)+'</p>' for k,v in rows.items())+'</details>')
add('<h3>不能用这次审查替代的验证</h3><p>0.7已另补36关六类敌人、占位与撤离的逐动作推演，详见战术审查；全部人物专长与装备的笛卡尔积仍未穷尽。归责和角色反应在真实玩家眼里是否公平、故事是否有吸引力、首玩是否达到12–16小时、资源价格与商业表现，也不能由这些断言证明。当前已把规则写清并修复本轮能复现的问题；没有证据支持“从此不会再有任何逻辑问题”。</p>')
add('<p>本轮没有更改既有游戏脚本、场景或工程配置；逐文件SHA-256核对一致。修改对象是设计数据、文档和参考验证脚本。没有新增必须交由你裁决的产品边界选择。</p>')
add('<p><a href="system-audit-results.json">逐项验证结果与案例数值</a> · <a href="../game/data/final_design/system_audit_contract.json">0.6修订规则</a> · <a href="full-game-design.html">完整产品设计</a> · <a href="whole-campaign-review.json">逐日账本</a></p></section>')
fragment='\n'.join(parts);(O/'system-audit-section.html').write_text(fragment)
style='''<style>*{box-sizing:border-box}body{background:#edf2f1;color:#20373e;font:16px/1.8 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;margin:0}main{max-width:1200px;margin:auto;background:white;padding:44px}h1{font-size:34px}h2,h3{margin-top:38px}a{color:#067a73}.muted{color:#5e747a}.note{background:#e8f4ee;border-left:4px solid #137b70;padding:18px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}th,td{vertical-align:top;text-align:left;padding:12px;border-bottom:1px solid #d5e2de;min-width:90px}th{background:#eaf1ee}details{padding:14px 18px;border:1px solid #d6e1dd;margin:12px 0}summary{font-weight:600;cursor:pointer}@media(max-width:700px){main{padding:20px}h1{font-size:28px}}@media print{body{background:white}main{padding:0}details{break-inside:avoid}}</style>'''
(O/'systematic-logic-audit.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 系统性逻辑审查0.6</title>'+style+'<main><h1>夜潮事务所：设计逻辑与跨系统审查</h1>'+fragment+'</main></html>')
print('Wrote systematic audit report:',len(findings),'issue groups,',R['passed_count'],'named checks.')
