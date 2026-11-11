"""Human-readable final-product design with inspectable coordinate maps and branches."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data';F=D/'final_design';O=ROOT/'outputs'
def read(n):return json.loads((F/n).read_text())
def esc(x):return html.escape(str(x))
def table(headers,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def items(d):return '<dl>'+''.join('<dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd>' for k,v in d.items())+'</dl>'
B=read('boards.json')['boards'];S=read('stories.json');C=read('combat.json');P=read('progression_relationship.json');I=read('integration.json');A=read('abilities.json');E=read('equipment.json');N=read('enemies.json');FACS=read('facilities.json')
V=json.loads((O/'final-design-validation.json').read_text());EX=json.loads((O/'combat-design-example.json').read_text());CH=json.loads((D/'characters.json').read_text());names={c['id']:c['name'] for c in CH};names.update({e['id']:e['name'] for e in json.loads((D/'equipment.json').read_text())});names.update({e['id']:e['name'] for e in json.loads((D/'enemies.json').read_text())})
names['scanner']='远程停机探针'
APPROACH=read('approach_review_contract.json')
CHOICE=read('player_choice_contract.json') if (F/'player_choice_contract.json').exists() else None
SCOPE=read('production_scope.json') if (F/'production_scope.json').exists() and CHOICE and CHOICE['version'].startswith(('0.12','0.13','0.14','0.15','0.16','0.17')) else None
IDENTITY=read('growth_identity_contract.json') if SCOPE and SCOPE['version'].startswith(('0.13','0.14','0.15','0.16','0.17')) else None
AUDIT=read('full_audit_contract.json') if SCOPE and SCOPE['version'].startswith(('0.14','0.15','0.16','0.17')) else None
if SCOPE:
 A=[a for a in A if a['id'] in SCOPE['abilities']]
 E['items']=[e for e in E['items'] if e['id'] in SCOPE['equipment']]
if CHOICE:APPROACH['services']=CHOICE['services']
report=[]
def add(x):report.append(x)
add('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 可实施设计 0.10</title><style>
:root{--ink:#1e343e;--muted:#566d76;--accent:#007f79;--line:#d4e0df;--bg:#f1f5f3}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.8 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}main{max-width:1200px;margin:auto;background:#fff;padding:48px}h1{font-size:38px;line-height:1.3}h2{margin-top:60px;padding-top:20px;border-top:3px solid var(--accent)}h3{margin-top:28px}p{margin:12px 0}a{color:var(--accent)}nav{display:flex;flex-wrap:wrap;gap:12px 22px;padding:18px 0;border-block:1px solid var(--line)}.kicker,.muted{color:var(--muted);font-size:14px}.note{background:#eaf5f1;border-left:4px solid var(--accent);padding:18px 22px;margin:22px 0}.warning{background:#fff4dc;border-color:#b17c26}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px;margin:16px 0}td,th{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--line);min-width:90px}th{background:#ecf2f1}details{border:1px solid var(--line);border-radius:8px;padding:14px 18px;margin:14px 0}summary{font-weight:650;cursor:pointer}.grid{display:grid;grid-template-columns:minmax(280px,380px) 1fr;gap:28px}.board{width:100%;max-width:380px;display:block}code,pre{background:#eef3f2;font:13px/1.6 ui-monospace,monospace}pre{white-space:pre-wrap;padding:16px;overflow:auto}dt{font-weight:650;margin-top:12px}dd{margin:3px 0 12px}.tag{font-size:12px;background:#e9f3ef;padding:2px 8px;border-radius:8px;margin-right:8px}button,input,select{font:inherit;padding:9px;border:1px solid #abc0bd;border-radius:6px}button{cursor:pointer;background:#e9f3ef}.controls{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}.small{font-size:13px}.scene{margin-left:15px;border-left:3px solid var(--line);padding-left:18px}footer{margin-top:50px;font-size:13px;color:var(--muted)}@media(max-width:760px){main{padding:22px}.grid{display:block}h1{font-size:29px}}@media print{details{break-inside:avoid}nav,.controls{display:none}main{padding:0}a{color:inherit}}
</style><main><p class="kicker">最终产品可实施设计 · 0.10 · 2026-11-02</p><h1>夜潮事务所</h1><p>三人战术救援 × 八人群像养成 × 有后果、能继续的单机战役。</p><div class="note"><b>本次补齐的是设计本身：</b>36 个具体关卡的坐标与目标状态、8 条三段人物分支、战斗与装备的费用和边界、成长与关系的衔接、缺席和失败的处理。这里给出直接可实现的规则与数值基线；当前按用户最新指示继续完善设计，暂不进入正式开发；不把参考脚本当作全部战斗验证。</div><nav><a href="#approach-review">阵容与合作0.10</a><a href="#integrated-review">整合复审0.9</a><a href="#player-experience">引导与人物0.8</a><a href="#loop">玩家的一局</a><a href="#combat">战斗规则</a><a href="#builds">人物与成长</a><a href="#equipment">装备与设施</a><a href="#relations">关系与凭据</a><a href="#boards">36 个关卡</a><a href="#stories">人物分支</a><a href="#events">96 个节点</a><a href="#integration">系统衔接</a><a href="#whole">整局联动</a><a href="#system-audit">系统性审查0.6</a><a href="#tactical-audit">36关实推0.7</a><a href="#checks">检查与实例</a></nav>''')
if CHOICE and (O/'player-choice-section.html').exists():
 report[0]=report[0].replace('可实施设计 0.10','可实施设计 0.11').replace('设计 · 0.10','设计 · 0.11').replace('<nav>','<nav><a href="#player-choice-review">玩家选择0.11（当前）</a>')
 if SCOPE and (O/'cooperation-value-section.html').exists():
  report[0]=report[0].replace('可实施设计 0.11','可实施设计 0.12').replace('设计 · 0.11','设计 · 0.12').replace('玩家选择0.11（当前）','玩家选择0.11（历史）').replace('<nav>','<nav><a href="#cooperation-value-review">合作价值与制作范围0.12（当前）</a>')
  if IDENTITY:
   report[0]=report[0].replace('可实施设计 0.12','可实施设计 0.13').replace('设计 · 0.12','设计 · 0.13').replace('合作价值与制作范围0.12（当前）','合作价值与制作范围0.12（历史）').replace('<nav>','<nav><a href="#growth-identity-review">战斗形式与养成价值0.13（当前）</a>')
   if AUDIT:
    report[0]=report[0].replace('可实施设计 0.13','可实施设计 0.14').replace('设计 · 0.13','设计 · 0.14').replace('战斗形式与养成价值0.13（当前）','战斗形式与养成价值0.13（历史）').replace('<nav>','<nav><a href="#full-audit">全域审查0.14（当前）</a>')
    add((O/'full-audit-section.html').read_text())
    add('<details><summary>历史评审0.13：玩法取舍记录；医疗、工坊、改约、归责和状态规则见0.14</summary>'+(O/'growth-identity-section.html').read_text()+'</details>')
   else:add((O/'growth-identity-section.html').read_text())
   add('<details><summary>历史评审0.12：保留删减范围；5级加次数已由0.13用途升级替代</summary>'+(O/'cooperation-value-section.html').read_text()+'</details>')
  else:add((O/'cooperation-value-section.html').read_text())
  add('<details><summary>历史评审0.11：合作学习门槛由0.12撤销；高级合作价值已重新比较</summary>'+(O/'player-choice-section.html').read_text()+'</details>')
 else:add((O/'player-choice-section.html').read_text())
add('<details><summary>历史评审0.10：其中12处值守与通用维修已被0.11替换</summary>'+ (O/'approach-review-section.html').read_text()+'</details>' if CHOICE else (O/'approach-review-section.html').read_text())
add((O/'integrated-review-section.html').read_text())
add((O/'player-experience-section.html').read_text())
add('<h2 id="loop">玩家的一局：取舍围绕同一件事展开</h2><p>玩家协调民间救援队，在洪灾港城里救人、恢复设施，并处理旧事故留下的责任与关系。战斗对象主要是失控设备，目标是完成救援和撤离，不以清空敌人作为默认胜利条件。角色的专业与关系影响“怎样做”，不会夺走基础行动。</p>')
add(table(['层次','玩家做什么','明确后果'],[
 ['出发前','看目标、期限、敌人和关系条件；选3人、专长、共有装备、最多3份耗材','选擅长的办法，也可能放弃其他便利；零信任零装备有基础方案'],
 ['一回合','每人2 AP，交错移动、停机、施工、保护、搬运','预告让风险可判断；合作与工具改变行动分配，不靠命中抽奖'],
 ['一任务','完成必需组，决定是否争取额外成果，按期撤离','成果逐项保留；未完成不把已救的人抹掉'],
 ['一晚','2项重点安排＋最多2段短谈','恢复/训练/设施/实质补救竞争项目；阅读基本人物故事不另收项目费'],
 ['一章','看地区、人员、证据与承诺变化','失败改变可保住的成果；基础照护与补员保证还能继续'],
 ['终局','第24日前确认可用路线，再执行其具体目标','世界、地方、个人分别按事实收束；最高难度才可能战役内永久医疗离队']]))
add('<p>24 个主任务、12 个可选支线候选，首玩目标仍为约 12–16 小时。这个目标尚未计时验证；不能用重复刷钱、强制慢动画或无效长路去凑时长。重玩来自不同投资、人物边界、不同主目标路线与保留成果，不随机改写人物过去。</p>')
add('<h3>失败与资源的底线</h3><p>初始30资金/6物资/2零件；主任务成功10/1/1、部分7/0/0、失败6/0/0；支线6/0/0、3/0/0、0/0/0。明确交接目标另按0.15经济表奖励；旧的任意额外目标统一物资奖励已撤销。基础食宿与常规照护免费，物资4资金一份。重伤默认D+2恢复、加速治疗D+1恢复且每人2物资；设施折扣另见下表。合格主角不足3人才补社区支援员，每人扣4本次主任务资金，最低保留6，无预付债务。支援员没有专长和个人线。</p><p>主任务疲劳+18、支线+18、后勤+8；睡眠−12，完全未工作的白天另−16。出勤检查当前疲劳＋本次已知消耗≤100。专门恢复额外−12；阶段训练每人1物资/+6疲劳/+12经验；每章开放1阶段、未用保留，带教与普通训练共用学员阶段。每晚最多2项目，同一人至多参加一项。失败任务补助不能重复领取；旧世界成果不会因资源保底而恢复。</p>')
add('<h2 id="combat">战斗规则：动作、预告、伤势和结束顺序</h2><p>棋盘坐标从左上角(0,0)开始，默认8×8，四方向移动；普通地1、浅水/碎石2、墙和深水不可走。所有人默认10HP，基础攻击2点，每轮2AP；携带者移动预算2，空手3。角色模型的历史“技能评分”不再额外参与命中或隐形掷骰。</p>')
add(table(['动作','AP','合法条件与效果'],[[a['id'],a['ap'],esc(a['effect'])] for a in C['actions']]))
add('<p><b>回合顺序：</b>重置AP → 公布敌人与环境预告 → 玩家交错行动 → 按稳定ID结算敌人 → 环境伤害 → 备份/车辆/救援期限 → 结果检查。机器按最近站立队员选择方向，距离相同按角色ID；横纵偏移相同先横向。已经预告的攻击不追着移动后的角色重瞄；推移机器会平移其攻击范围，并在确认前重新显示。</p>')
add('<p>一次射线先被墙或盾挡住；水火同格环境伤害取较大值，不能重复按每格水域给同一人计伤。失能者本关不能复活刷AP；稳定只能延长期限一次。所有重大后果在提交动作前预览，已提交动作不被突然插入的冲突反向修改。</p>')
add(table(['机器','HP','具体行为'],[[names[n['id']],n['hp'],esc(n['rule'])] for n in N]))
add('<details><summary>伤势、撤退、难度与存档的完整边界</summary>'+items(C['damage'])+items(C['difficulty'])+'<p>'+esc(C['difficulty_constraints'])+'</p><p>'+esc(C['save_and_undo'])+'</p></details>')
add('<details><summary>目标状态机与空间规则</summary>'+items(C['objective_machine'])+items(C['geometry'])+items(C['archetype_planning_overrides'])+items(C['safeguard_producers'])+'<p>'+esc(C['objective_persistence'])+'</p></details>')
add('<h2 id="builds">人物、成长与配置：能力不是主线钥匙</h2><p>每人等级1–6，经验门槛0/12/28/48/72/100。'+('第1/3级获得两项固定专长，第5级强化其中一项的用途，详见人物表；次数不再统一增加。' if IDENTITY else '第1/3级获得两项固定专长，第5级将第一专长每任务次数从2提高到3，不新增第三种动作。' if SCOPE else '第1/3/5级解锁三个专长、最多装备两个；')+'第2级在施工与移动倾向中二选一，第4/6级各加1HP，第6级取得另一倾向。基础攻击不倍增。新成员按章节0/12/28/48补经验底线；营地免费切换L2倾向，战斗内锁定。</p>')
for c in CH:
 add('<details><summary>'+esc(c['name']+' · '+c['role'])+'</summary><p>'+esc(c['past'])+'</p><p><b>想要：</b>'+esc(c['want'])+'<br><b>局限：</b>'+esc(c['flaw'])+'</p>'+table(['等级/专长','AP/任务次数/距离','明确效果'],[[str(a['level'])+' / '+a['name'],f'{a["ap"]} / {a["charges_per_mission"] if a["charges_per_mission"] else "被动"} / {a["range"]}',esc(a['effect']+(' '+a.get('level5_effect','') if IDENTITY else ''))] for a in A if a['actor']==c['id']])+'</details>')
add('<p>'+esc(I['stacking_rules'])+'</p>')
add('<h2 id="equipment">装备、耗材和设施：付钱买到什么</h2><p>'+esc(E['inventory'])+'</p><p>'+esc(E['craft'])+'</p>')
add(table(['物品','开放/购买','槽位/AP/次数','实际用途'],[[names[e['id']],('开局' if e['unlocked_after_main']==0 else 'M'+str(e['unlocked_after_main']).zfill(2)+'结算后')+'<br>'+('每份'+str(e['consumable_supply_cost'])+'物资' if e['slot']=='consumable' else str(e['price_credits'])+'资金/'+str(e['price_parts'])+'零件'),f'{e["slot"]} / {e["action_ap"]} / '+('基础不限次' if e['uses_per_mission'] is None else str(e['uses_per_mission'])),esc(e['effect'])] for e in E['items']]))
add('<p>急救包本体不消耗，但其中的药剂每次1物资；总容量3，单品基础2，工坊II后单品3且急救包次数3。工具购买与耗材打包不额外占营地项目；只有设施升级占1项目，一级35资金+4零件、二级60+8；每晚最多升一次。</p>')
add(table(['设施','一级','二级'],[[{'infirmary':'医务室','workshop':'工坊','rest_area':'休息区','communications':'通信台'}[f['id']],esc(f['tier1']),esc(f['tier2'])] for f in FACS]))
add('<h2 id="relations">关系如何真正进入战术</h2><p>旧怨是定向的历史基数，事件记忆按责任、知情、敏感点与重复刺激增加；压力属于个人，不等于对某人的怨恨。Q进入45/65/80对应戒备、条件合作、冲突资格，退出35/50/60避免抖动。当前采用0.6活跃权重规则；完整公式、满值处理、归责与冷却见本页系统性审查。</p>')
add('<pre>R = G + 已分配活跃记忆总和（真实总量不超过100，无隐藏超额负担）\n新记忆 = min(40, 严重度 × 敏感度 × 责任份额\n × (1+0.7×(相关旧怨/100)²) × (1+0.8×(当前怨气/100)²)\n × (1+0.25×压力/100) × (1+min(0.4,0.1×近期同类刺激次数)))\nQ = clamp(R + 0.25×max(压力-40,0), 0,100)</pre><p>普通记忆3日半衰、同类最多3条活跃，总和最多24；超出按比例缩减幅度，归档条目不回填。严重记忆采用8日半衰与35%残余的混合公式；总记忆超过100-G也缩减已分配幅度，不隐藏溢出。身体疲劳只按工作计，不给同一事件再加疲劳处罚。压力单任务新增最多12，救援宽慰最多−4，夜间−8；仅放大关系事件，不随机扣行动。</p>')
initial=json.loads((D/'initial_relationships.json').read_text())
add('<details><summary>开局已存在的有向恩怨与信任</summary>'+table(['方向','旧怨/信任/亲近','实际历史'],[[names[r['observer']]+'→'+names.get(r['target'],'队长'),str(r['grudge'])+'/'+str(r['trust'])+'/'+str(r['closeness']),esc(r['history'])] for r in initial if r['grudge']>0 or (r['observer'],r['target']) in [('lin','su'),('su','lin')]])+'</details>')
add(table(['事件','基础强度/信任损失','何时才成立'],[[e['id'],str(e['severity'])+' / '+str(e['trust_loss']),esc(e['trigger'])] for e in P['memory_events']]))
add('<div class="note"><b>身体恢复与人际怨气分开：</b>重伤、同队出勤和等待免费恢复不自动加怨；隐瞒风险或违背明确约定才按知情与责任形成有向记忆。当前审查发现：普通同类记忆上限24会使反复失信卡在同一情绪水平，因此补入独立事件的持续失信升级规则，不能把同一事故算三次。本轮已明确满值、归责与冷却组合规则，并完成针对性回归；仍不能宣称零逻辑问题。<a href="systematic-logic-audit.html">查看系统性审查</a></div>')
add('<p>'+('；'.join(esc(v) for v in P['responsibility'].values()) if isinstance(P['responsibility'],dict) else esc(P['responsibility']))+'</p><p>'+esc(P['relationship_commit'])+'</p>')
add(table(['协议','双方消耗与条件','收益','关系不好时的基础办法'],[[p['name'],esc(p['cost']),esc(p['effect'] if SCOPE else p['effect']+'；0.10：'+APPROACH['protocols'].get(p['id'],'')),esc(p['baseline'])] for p in P['protocols']]))
add(('<p><b>当前范围：</b>人物专长16项、装备7种；四项协作是情境指令，不再形成独立养成分支。5级强化现有专长用途（0.13）；正向关系新增有限带教及改派接应，完整成本见本页首节。<a href="cooperation-value-review.html">依据和制作范围</a></p>' if SCOPE else '')+'<p>'+esc(P['protocol_training'])+'</p><p>'+esc(P['restriction_rules'])+'</p>')
add(table(['人物','动作标签','相关情境','需满足的保障'],[[names[k],esc(','.join(v['protocol_tags']) or '无战斗限制'),esc(','.join(v['when'])),esc(','.join(v.get('required_any',v.get('required_all',[]))))] for k,v in P['situational_cooperation'].items()]))
add('<p>'+esc(P['situational_rule'])+'</p>')
add('<p>'+esc(P['repair'])+'</p><details><summary>9条有向历史修复：谁需要做什么</summary>'+table(['方向','认责 −6','补救 −12','后续履约 −12'],[[names[x['pair'].split('>')[0]]+'→'+names[x['pair'].split('>')[1]],esc(x['stage1']),esc(x['stage2']),esc(x['stage3'])] for x in I['history_repair_routes']])+'<p>'+esc(I['repair_limits'])+'</p></details>')
# SVG maps include independent overlays, so fixtures and actors cannot be confused with walls.
def svg(b):
 w=36;off=25;out=[f'<svg class="board" role="img" aria-label="{esc(b["id"])}关卡坐标图" viewBox="0 0 330 340" xmlns="http://www.w3.org/2000/svg">']
 colors={'.':'#edf3ef','~':'#a9d9e8',':':'#ccbc9a','#':'#41545a','X':'#1b5369'}
 for x in range(8):out.append(f'<text x="{off+x*w+18}" y="17" text-anchor="middle" font-size="12">{x}</text>')
 for y,row in enumerate(b['rows']):
  out.append(f'<text x="12" y="{off+y*w+23}" text-anchor="middle" font-size="12">{y}</text>')
  for x,g in enumerate(row):out.append(f'<rect x="{off+x*w}" y="{off+y*w}" width="35" height="35" fill="{colors[g]}"/>')
 def mark(p,text,color,shape='circle'):
  x,y=p;cx=off+x*w+18;cy=off+y*w+18
  out.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="{color}"/><text x="{cx}" y="{cy+4}" font-size="10" text-anchor="middle" fill="white">{esc(text)}</text>')
 for p in b['exits']:mark(p,'出','#077e75')
 for j,p in enumerate(b['spawns']):mark(p,str(j+1),'#286a9b')
 for j,o in enumerate(b['objectives']):mark(o['cell'],chr(65+j),'#9a672d')
 for j,o in enumerate(b['controls']):
  x,y=o['cell'];out.append(f'<rect x="{off+x*w+2}" y="{off+y*w+2}" width="9" height="9" fill="#8064a9"><title>{esc(o["id"])}</title></rect>')
 for j,en in enumerate(b['enemies']):mark(en['cell'],'敌'+str(j+1),'#ad4650')
 out.append('<text x="25" y="334" font-size="11">蓝：出勤点 · 棕：目标 · 紫：停机开关 · 绿：出口</text></svg>');return ''.join(out)
add('<h2 id="boards">36个具体关卡：可按坐标制作</h2><p>地图展示地形、出勤点、敌人、出口、目标与停机开关。A/B/C等目标符号对应本关下表；同格分阶段对象分别列出。备用撤离坐标默认只是地图元数据；0.13允许满足R04/R10合作约定的队伍付费改派主线接应，替换通常出口，而非自动获得第二出口。M10和M21的现场出口仍按实际操作前置开启。标准限时见每关，从容+3轮；严峻使用每关单独设定的最高限时（见0.7审查表）。地图中的深水不可通行，后续涨水只新增浅水。</p><div class="controls"><input id="search" placeholder="搜索关卡编号、标题或目标" aria-label="搜索关卡"><select id="kind"><option value="">全部36关</option><option value="main">主线24关</option><option value="side">支线12关</option></select><button onclick="document.querySelectorAll(\'.encounter:not([hidden])\').forEach(x=>x.open=true)">展开筛选结果</button><button onclick="document.querySelectorAll(\'.encounter\').forEach(x=>x.open=false)">收起</button></div>')
for b in B:
 add(f'<details class="encounter" id="{b["id"]}" data-kind="{b["kind"]}"><summary>{b["id"]} {esc(b["title"])} <span class="tag">第{b["day"]}日</span><span class="tag">{b["round_limit"]}轮</span></summary><div class="grid"><div>'+svg(b)+'</div><div><p><b>主要取舍：</b>'+esc(b['decision'])+'</p><p><b>后续影响：</b>'+esc(b['consequence'])+'</p><p><b>目标判定：</b>'+esc(str(b.get('route_groups',b['mandatory_groups'])))+'；组间全部满足，组内任一满足。</p><p><b>额外目标：</b>'+esc(', '.join(b['optional']) or '无')+'</p><p>'+esc(b['optional_reward_rule'])+'</p></div></div>')
 if b['id'] in APPROACH['services']:
  sv=APPROACH['services'][b['id']]
  if CHOICE:
   add('<div class="note"><b>0.11可选现场操作：'+esc(sv['label'])+'</b><br>'+esc(sv['effect'])+'<br>位置／阶段'+esc(sv.get('stages',sv['posts']))+'；物理前置'+esc(sv.get('prerequisites',[]))+'；第'+str(sv['deadline'])+'轮末截止。每位置每轮1AP，基础主目标仍可独立完成。只有M05、M10有可选付费后勤修复，其他机体不产生营地维修账。<br><a href="player-choice-review.html">查看当前规则与投入价值验证</a></div>')
  else:
   add('<div class="note"><b>0.10可选现场成果：'+esc(sv['label'])+'</b><br>值守位置'+esc(sv['posts'])+'，需要'+str(sv['consecutive_rounds'])+'轮连续有效，机会到第'+str(sv['deadline'])+'轮末。每个位置每轮1AP、空手留到轮末；普通关停主线仍可完成。'+esc(sv['reason'])+' 拆毁指定设备后可不修，或在剩余营地花1项目与2物资恢复；不能补造已错过的服务。<br><a href="approach-design-review.html">查看保护、分工、普通工具与合法绕解的完整验证</a></div>')
 add(table(['图标/ID','目标与坐标','操作/前置'],[[chr(65+j)+' / '+o['id'],esc(o['label'])+' @ '+str(o['cell']),o['kind']+' · '+str(o['work'])+'工量；前置：'+(','.join(o['prerequisites']) or '无')+('；持续'+str(o['hold_rounds'])+'轮' if 'hold_rounds' in o else '')+('；额外机会期限第'+str(o['opportunity_deadline'])+'轮末' if 'opportunity_deadline' in o else '')+('；车辆路径'+str(o['waypoints']) if 'waypoints' in o else '')+('；撤离时需仍完好' if o['sustain_until_exit'] else '；完成成果保留')] for j,o in enumerate(b['objectives'])]))
 add(table(['机器','坐标/朝向','普通停机办法'],[[names[e['type']],str(e['cell'])+'/'+e['facing'],', '.join(e['disable_requires'])] for e in b['enemies']]))
 add('<p><b>开关：</b>'+esc('；'.join(o['id']+' @ '+str(o['cell'])+'，'+str(o['work'])+'工量' for o in b['controls']))+'</p><p><b>环境：</b>'+esc('第5轮新增浅水'+str(b['environment']['water_addition']['cells'])+'；第7轮火区'+str(b['environment']['fire_pulse']['cells'])+'。B方案浅水第6轮，火区提前至第6轮（若有）。')+'</p>')
 add('<p><b>人员时限：</b>'+esc(b['civilian_timer'])+'</p><p><b>环境工具：</b>漏口在(7,1)，泡沫延迟该次涨水而不删除事件；火区点燃后持续3次环境结算，灭火可以提前清除。目标类型与风险情境见关卡数据。</p>')
 if b['id']=='M02':add('<p>现场spare电池可以搬回出口领取额外成果，也可在携带状态下、邻接power且cut已完成时花1AP直接提供2供电工量；用掉即销毁货物，不再领取带回奖励。自带电池则另按耗材扣除。</p>')
 rr=[r for r in V['board_routes'] if r['mission']==b['id']]
 add('<details><summary>基础行动的路径与工量核算</summary><p>下表包含普通队员步行、施工、停机、搬运和撤离，并按坏天气/上关失败的移动成本计算；尚未模拟所有敌人动态攻击和人员占位冲突，因此是物流下限检查，不是通关保证。</p>'+table(['路线/目标选择','保守排程轮数','总AP','标准/最高限时'],[[r['route']+' / '+','.join(r['selection']),r['rounds'],r['sum_ap'],str(r.get('standard_deadline','—'))+'/'+str(r['hard_deadline'])] for r in rr])+'</details></details>')
add('<h2 id="stories">8条人物线：具体选择、兑现与缺席分支</h2><p>每条线三段：认识事实 → 作出具体安排 → 看兑现结果选择合作与生活方向。第二段占一个营地项目，其余是短谈；明确支付只在选择时扣一次。第三段“建立新关系”的选项需要凭据，专业距离和战后生活方向始终可选。玩家没看、推迟、没能履约和角色离队都各有合法结果，不硬塞和好台词。</p>')
for c in CH:
 actor=c['id'];p=S['profiles'][actor]
 add('<details><summary>'+esc(c['name'])+'：'+esc(' → '.join(c['arc']))+'</summary>')
 for n in [n for n in S['personal_nodes'] if n['actor']==actor]:
  add('<div class="scene"><h3>'+esc(n['title'])+f' <span class="tag">第{n["earliest_day"]}日可开始</span></h3><p>'+esc(n['opening'])+'</p>'+table(['选择','具体回应与结果','费用/条件'],[[ch['label'],esc(ch['response']),str(ch.get('credits',0))+'资金；'+(str(n['project_cost'])+'项目')+'；'+esc(','.join(ch.get('requires',[])) or '无需信任门槛')] for ch in n['choices']])+'</div>')
 add('<p><b>怎样才算兑现：</b>'+esc(p['verification'])+'</p><p><b>缺席/延迟：</b>'+esc(next(n['absent'] for n in S['personal_nodes'] if n['actor']==actor))+'</p><p><b>第三段尚未满足条件：</b>可以在第23日前继续兑现，或选择专业距离与战后生活方向。需未来主任务的计划有更早承诺截止日：苏棠21日、陈砚20日，林岚/许舟/贺鸣22日；其余23日。没有看完也有符合已发生事实的尾声。</p></details>')
if AUDIT:add('<p>'+esc(S['scheduler']['capacity_notice'])+'</p>')
add('<details><summary>可排入战役的主要人物与关系日历</summary><p>这是所有主要节点均被主动选择的一个阅读安排，证明窗口容量成立；并不意味着所有承诺凭据会自动达成，也不强迫玩家读完全部生活场景。</p>'+table(['日','短谈1/2','占用重点项目'],[[x['day'],', '.join(x['scenes']) or '可留给生活短谈',x['projects']] for x in V['story_calendar']])+'</details>')
add('<h2 id="events">96个叙事节点的职责与具体内容</h2><p>24个人节点已在上面展开。其余12重点关系、24社区回访、18生活短谈、18章节后果如下；节点数量表示已经登记的叙事状态与选择，不代表已经完成配音、最终演出或全部文学润色。</p>')
add('<details><summary>12个重点关系场景</summary>'+table(['场景/开放日','冲突来自什么','可选处理'],[[r['id']+' '+r['title']+' / '+str(r['earliest_day']),esc(r['opening']),'<br>'.join(esc(c['label']+'：'+c['effect']) for c in r['choices'])+('<br>'+esc(r.get('positive_payoff','')) if IDENTITY else '')] for r in S['relationship_nodes']])+'</details>')
add('<details><summary>24个社区回访：以本关实际结果选择版本</summary>'+table(['来源/回访','事实主题','选择'],[[r['source']+' '+r['title'],esc(r['facts']),'公开经核实的任务摘要 / 保留内部交接；不伪造证据、不提供无限好感'] for r in S['community_nodes']])+'<p>每个回访按success/partial/failed生成不同版本，具体已救居民、完成设施和丢失对象从该关回执填入；已死亡/失踪者不能出现在下一次轻松回访中。</p></details>')
add('<details><summary>18个生活短谈：人物有灾难以外的生活</summary>'+table(['人物/场景','选择A','选择B'],[[names[r['actor']]+' / '+r['title'],r['choices'][0]['label'],r['choices'][1]['label']] for r in S['recovery_nodes']])+'<p>尊重选择的短谈一次给对队长亲近+3，不清旧怨，不增加战斗数值；永久离队后仅有来信近况。高强度冲突后不会立即强插笑话。</p></details>')
add('<details><summary>18个章节后果：不重复发奖励、不抹去损失</summary>'+table(['来源/判定对象','保住时','没保住时'],[[r['source']+'/'+r['condition']['objective']+'：'+r['title'],r['true_text'],r['false_text']] for r in S['chapter_nodes']])+'</details>')
add('<h2 id="integration">系统必须按同一份事实工作</h2><p>每次动作记录稳定ID、角色、知情者、对象、前后状态、资源变动和承诺ID。任务结算一次性提交奖励、成长、关系、招募、地区与证据；失败时全部回滚，禁止一边发钱另一边未写完成。人物承诺根据具体行动回执兑现，不能读到一段好话就发奖励。</p>')
add(table(['已解决的矛盾','现在的规则'],[[esc(a),esc(b)] for a,b in I['resolved_contradictions']]))
add('<h3>证据、分支目标和结局</h3><p>E_ORDER来自M12的签名页＋成功带出的备份盘，或M21副本；E_MAINTENANCE来自M11/M17；E_WARNING来自M13/M22。第20/22/23日可用1项目核查1份公共副本；通信台一级新增第18日窗口，二级让一次核查可查2份。晚核查不撤销之前的违约和错过机会。</p><p>共同控制：设施合计≥10且两份不同证据，终战完成bus＋auth；分区重建：无证据门槛，终战完成west＋east；总撤离：始终可选，完成r1＋r2。终战失败也有完整撤离收束，但按实际损失写，不播放虚假的全员获救。M17隔离方案的设施上限损失已纳入路线资格。</p>')
add('<p>'+esc(I['late_breach_resolution'])+'</p><p>'+esc(I['responder_scope'])+'</p><p>'+esc(I['disclosure_followup'])+'</p>')
add('<p>'+esc(I['M17_override'])+'</p><p>'+esc(I['missing_actor'])+'</p><p>'+esc(I['injury_activity'])+'</p><p>'+esc(I['postgame'])+'</p>')
add((O/'whole-campaign-section.html').read_text())
add((O/'system-audit-section.html').read_text())
add((O/'tactical-audit-section.html').read_text())
add('<h2 id="checks">验证：明确哪些已经执行，哪些是设计判断</h2>')
add('<p>历史基础内容/状态检查通过'+str(V['passed_count'])+'项，覆盖36张地图、46种主目标组合的基础路径排程、224种人物选择与缺席状态路径，以及主要故事窗口容量。路径检查包含工量、搬运、撤离、前置和定时目标；这张旧的静态排程表不含敌人动态；本次另用0.7逐动作模型执行全部36关，范围和结果见上一节。检查数量不能等同于游戏好玩或全部实现。</p>')
add('<p>另执行'+str(json.loads((O/'story-contract-checks.json').read_text())['passed_count'])+'项承诺与结局检查：旧善举不能倒填新承诺、同一人的重复记录不能冒充两人贡献、不同任务不能拼成一次合作、支付对象不能替换、后续再次背约会改写早先的温暖结语。</p>')
add('<h3>M02：诊所备用电的可复算战斗案例</h3><p>使用本表棋盘，实际运行三个角色的AP、加权移动、结束位置占位、巡检机锁定预告/移动/伤害、断路前置、停机与全员撤离。固定同一操作策略，比较基础队员、2级施工倾向和一份电池。电池在M01结算后已可制作；2级案例是隔离成长效果的受控测试，第一周目的M02通常尚未达到该等级，不能把它当作开局可用配置。</p>')
add(table(['配置','结束轮数','实际AP','消耗物资','结果'],[[{'baseline':'基础队员，无装备合作','level2':'三人2级施工倾向','battery':'基础队员＋电池'}[x['style']],x['rounds'],x['ap_used'],x['supplies_used'],'完成供电，三人撤离，均10HP'] for x in EX['cases']]))
add('<p>电池省1次施工，却没有在这个操作安排下少一整轮；2级施工在三个不同对象上各生效一次，共省3AP。不能把“省AP”直接当作“整关必定更快”，也不能用这个教学关证明后期装备平衡。0.7把双人保护作业改为2总AP完成3工量并附一次机器防护，不叠加2级施工；低信任可用三次基础交互完成相同工量，成长可减少其中一次。</p>')
add('<details><summary>展开基础配置的逐动作记录</summary>'+table(['轮','行动者/事件','动作与状态'],[[x['round'],x.get('actor',x.get('event','')),esc(str({k:v for k,v in x.items() if k not in ['round','actor','event']}))] for x in EX['cases'][0]['log']])+'</details>')
add('<div class="note warning"><b>当前交付边界：</b>系统、关卡和人物分支已经给出具体设计，并通过上述范围的参考检查。正式Godot工程仍需把这些数据、战术表现和全部状态控制接起来，再进行真实玩家测试。接下来的实施不应重新猜目标、费用或缺席结果；实玩发现的节奏和强弱问题按本设计调整参数与布局，不能冒称已经证明最终胜率或时长。</div>')
add('<p>本轮没有出现必须改变你已确认边界的新选择，因此没有再把常规设计问题交回给你。</p><footer>可复核资料：<a href="final-design-validation.json">地图/分支检查记录</a> · <a href="combat-design-example.json">M02逐动作记录</a> · <a href="story-contract-checks.json">人物承诺检查</a> · <a href="../game/data/final_design/boards.json">关卡数据</a> · <a href="../game/data/final_design/stories.json">人物与事件数据</a> · <a href="../game/data/final_design/integration.json">系统衔接规范</a> · <a href="full-game-design-v03.html">0.3历史设计</a></footer>')
add('''</main><script>function filter(){let q=document.querySelector('#search').value.toLowerCase(),k=document.querySelector('#kind').value;document.querySelectorAll('.encounter').forEach(x=>{x.hidden=!!((k&&x.dataset.kind!==k)||(q&&!x.textContent.toLowerCase().includes(q)))})}document.querySelector('#search').addEventListener('input',filter);document.querySelector('#kind').addEventListener('change',filter);function showAnchor(){let el=document.getElementById(location.hash.slice(1));if(el&&el.tagName==='DETAILS'){el.open=true;el.scrollIntoView()}}addEventListener('hashchange',showAnchor);showAnchor();</script></html>''')
(O/'full-game-design.html').write_text('\n'.join(report))
# Keep an inspectable single-encounter export in sync with the full document.
whole='\n'.join(report);begin=whole.index('<details class="encounter" id="M17"');end=whole.index('<details class="encounter" id="M18"')
style=whole[whole.index('<style>'):whole.index('</style>')+8]
fragment=whole[begin:end].replace('id="M17"','id="M17" open',1)
(O/'mission-17-design.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>M17关卡设计</title>'+style+'<main><p><a href="full-game-design.html">返回完整设计</a></p>'+fragment+'</main></html>')
print('Wrote final design report:',len('\n'.join(report)),'characters')
