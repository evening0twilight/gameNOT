from pathlib import Path
import json,html,re,hashlib,collections
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design';O=ROOT/'outputs'
def read(p):return json.loads(p.read_text())
def e(x):return html.escape(str(x))
def table(h,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in h)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def spread(v):return str(min(v)) if min(v)==max(v) else f'{min(v)}–{max(v)}'
css='''*{box-sizing:border-box}body{margin:0;background:#eff3f2;color:#253b3e;font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1160px;margin:auto;background:white;padding:40px}h1{font-size:36px;line-height:1.4}h2{margin-top:40px;border-top:2px solid #368478;padding-top:20px}a{color:#08746c}nav{display:flex;flex-wrap:wrap;gap:16px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:12px;vertical-align:top;text-align:left;border-bottom:1px solid #d8e2df;min-width:90px}th{background:#edf4f1}.note{padding:18px;background:#e8f3ee;border-left:4px solid #278378}.warn{background:#fff2d9;border-color:#ad822d}.muted{color:#657c7b}details{padding:14px;border:1px solid #cbdad5;border-radius:6px;margin:16px 0}summary{cursor:pointer;font-weight:bold}footer{margin-top:35px;border-top:1px solid #ccc;padding-top:20px}@media(max-width:650px){main{padding:18px}h1{font-size:28px}}'''
def page(body):return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所 · 额外训练价值审查0.17</title><style>'+css+'</style><main>'+body+'</main></html>'
D=read(O/'training-campaigns.json');rows=D['scenarios'];S=read(O/'training-specialty.json');M=read(O/'training-mentorship.json');GEN=read(O/'training-general-campaigns.json');T=read(O/'training-checks.json');chars=read(ROOT/'game/data/characters.json');names={c['id']:c['name'] for c in chars};joins={c['id']:c['join'] for c in chars};formations={'fixed':'持续作为主力','rotate':'按疲劳轮换','reserve':'先后备再启用'}
def key(r):return tuple(r['spec'][k] for k in ['training_actor','formation','exposure','difficulty','variant'])
groups=collections.defaultdict(dict)
for r in rows:groups[key(r)][r['spec']['training_rule']]=r
current=[r for r in rows if r['spec']['training_rule']=='current'];legacy=[r for r in rows if r['spec']['training_rule']=='legacy'];none=[r for r in rows if r['spec']['training_rule']=='none']
def training(r):return [x for x in r['receipts'] if x['kind']=='training']
def wins(r):return sum(b['success'] for b in r['battles'])
def first(r,who,level):return next((b['mission'] for b in r['battles'] if who in b['party'] and b['levels'][who]>=level),'未在出勤时达到')
def total(r,k):return sum(b[k] for b in r['battles'])
cf=[(r,b,b['without_paid_growth']) for r in current for b in r['battles'] if b.get('without_paid_growth')];scf=[(r,b,b['without_paid_growth']) for r in S['scenarios'] for b in r['battles'] if b.get('without_paid_growth')]
parts=['<section id="training-value"><p class="muted">夜潮事务所 · 0.17 · 2026-11-03 · 设计、数值与离线验证；未进入正式开发</p><h1>训练买的是提前上场的能力，<br>不是每天打卡的一点经验</h1><p>本轮修改了训练的收益、疲劳、次数与带教关系。自然出勤经验、入队经验、等级阈值、自然恢复及任务奖励保持不变。旧训练的问题不能只靠隐藏推荐解决。</p><nav><a href="#tr-rules">当前规则</a><a href="#tr-roles">八角色与入队时机</a><a href="#tr-cost">资源和疲劳</a><a href="#tr-combat">实际任务价值</a><a href="#tr-mentor">关系带教</a><a href="#tr-evidence">覆盖与边界</a><a href="full-game-design.html">整套设计</a></nav><div class="note"><b>本轮判断：</b>将零碎重复训练改为可保留的阶段课程，主要价值是提前取得本人专长、减少为了补课而安排的出勤、为喜欢的替补准备上场。训练没有凭空增加任务奖励，也不保证所有角色、所有路线都值得投资。</div>']
parts.append('<h2 id="tr-rules">已经写回的训练规则</h2>'+table(['方式','经验与支出','限制与取舍'],[
 ['自然出勤（不变）','主线成功/部分/失败：5/3/1经验；支线3/1/0；后勤2','主线18疲劳、支线18、后勤8；同时得到任务成果、资源和实际合作经历。'],
 ['阶段训练（新）','每人1物资、+12经验、+6疲劳；1–2人合用1个晚间项目','每章开放1阶段；没用的保留。每人每晚仍只参加1项目。到100经验截断；不返还已实际训练的资源。'],
 ['共同带教（同步修改）','1项目、2物资、两人各+6疲劳；学员最多+24经验，不能超过导师经验或100','占学员1阶段，导师不获经验；每学员每章最多一次带教。须已有约定、两次真实共同任务贡献与当前合作条件。实际增益不超过普通训练时不提供。'],
 ['休息（不变）','专门恢复0物资，1项目，额外−12疲劳','训练与休息占同一个人的晚间机会；自然睡眠−12、白天未工作额外−16照常。']]))
parts.append('<p><b>为什么选12而不是继续给3？</b>入队12经验的成员，一次课程再加一次成功主线，达到29经验，可取得三级专长；只靠成功主线需四次才能跨过28。四级48到五级72的跨度为24，两个阶段能补齐，但阶段按章节逐步开放。6和8经验候选也执行过比较，跨级时机改善较小；12的设计依据是现有能力节点，并非宣称数学上唯一最优。</p><p><b>为什么不让玩家天天练？</b>阶段数量有限、单次收益明确，避免把培养变成23晚重复购买。没用的阶段不在章末消失，可以等决定换人再补做。入队前的章节不补发，已体现在12/28等入队基础经验。所有现有角色仅靠普通付费课程和初始经验都达不到五级，任务成长仍有作用；带教也不能超过已经实际成长的导师。</p><p>短谈不会消耗训练阶段；训练不增加信任、不清怨气、不算共同救援或履约。不得把“我们练过”写成“我们一起救过人”。两人一起普通训练各得12、共花2物资且只占1项目；带教则把投入集中到一名落后学员，不是总经验永远更多。</p>')
role_rows=[]
for who in names:
 g=groups[(who,'fixed','main','standard','A')];a,b=g['none'],g['current'];role_rows.append([names[who],f'第{joins[who]}日',len(training(b)),first(a,who,3)+' → '+first(b,who,3),first(a,who,5)+' → '+first(b,who,5),f'{wins(a)}/{len(a["battles"])} → {wins(b)}/{len(b["battles"])}'])
parts.append('<h2 id="tr-roles">八个人物：什么时候得到能力，什么时候用得上</h2><p>下面是标准难度A、仅主线、持续使用该角色的成对整局。每行只改变目标角色的额外训练；训练与出勤均实际扣资源和疲劳。首次五级出勤不等于那一关必须使用五级能力。</p>'+table(['角色','入队日','新训练晚数/物资','首次三级出勤：自然→训练','首次五级出勤：自然→训练','成功/出勤任务：自然→训练'],role_rows))
all_roles=[]
for who,formation in __import__('itertools').product(names,formations):
 g=groups[(who,formation,'main','standard','A')];a,b=g['none'],g['current'];all_roles.append([names[who],formations[formation],len(training(b)),first(a,who,5),first(b,who,5),sum(who in z['party'] for z in a['battles']),sum(who in z['party'] for z in b['battles'])])
parts.append('<details><summary>同一角色换成轮换或后备：24组成对例子</summary>'+table(['角色','安排','训练晚数','自然首次五级','训练首次五级','自然出勤数','训练后出勤数'],all_roles)+'<p>后备启用日为max(第7日,入队日+5)。按疲劳轮换是固定的普通策略，同疲劳时按名单先后；它可能长期没有使用最后加入者，因此出现“训练了却没有上场”。这是可见的低价值选择，不应拿来证明该角色本身弱，也不能假设未来一定会上场而推荐付费。</p></details>')
parts.append('<p><b>玩家为什么愿意付钱：</b>不想为了让喜欢的替补解锁自己的玩法，连续占用数关出勤席位；或者已经看见下一任务需要某项专长，希望在进场前取得。<b>什么时候应留着阶段：</b>当前阵容自然成长已经够用，尚未决定启用角色，或者跨级后依然没有具体用途。未用阶段保留，等待本身是合法选择。</p>')
parts.append('<h2 id="tr-cost">资源、疲劳、项目：训练并不自动稳赚</h2>')
metrics=[]
for mode,label in [('legacy','旧3经验/8疲劳'),('current','新阶段12经验/6疲劳')]:
 rs=[g[mode] for g in groups.values()];train_count=sum(len(training(r)) for r in rs);better=sum(wins(g[mode])>wins(g['none']) for g in groups.values());same=sum(wins(g[mode])==wins(g['none']) for g in groups.values());worse=len(groups)-better-same
 metrics.append([label,len(rs),train_count,train_count*(8 if mode=='legacy' else 6),f'{better} / {same} / {worse}',sum(total(r,'rounds') for r in rs)])
parts.append(table(['安排','整局数量','目标角色训练总次数/物资','训练产生的累计疲劳','成功任务数较不训练：多/相同/少','整局战斗轮数合计'],metrics))
parts.append('<p>上述成功数量是整局取得的成功任务数，包含因疲劳改变而多做或少做的支线，不能解读为单场胜率或玩家满意度。累计疲劳包含后来正常恢复的部分，不是结局疲劳。三种安排均以预先确定的策略执行，没有事后选优。</p><p><b>一个不能靠经验覆盖的反例：</b>当晚66经验、90疲劳。训练后78经验，确实取得五级；睡眠后84疲劳，次日再出勤18将达102，无法安排。若选择休息，睡眠后66疲劳，能正常出勤。训练与休息的疲劳差是18，不只是训练卡片上的+6。此时应推迟培训，不降低出勤检查来制造“训练一定有用”。</p>')
before=read(O/'ordinary-player-after-campaigns.json')['scenarios'];br={r['spec']['name']:r for r in before};general=[]
for behavior,label in [('main_only','只做主线'),('collector','收集、买工具与投资'),('favorite','偏爱固定人物'),('mixed','犹豫/晚出发与轮换')]:
 a=[r for r in GEN['scenarios'] if r['spec']['behavior']==behavior and r['spec']['difficulty']=='standard'];old=[br[r['spec']['name']] for r in a]
 general.append([label,spread([wins(r) for r in old])+'/'+spread([len(r['battles']) for r in old]),spread([wins(r) for r in a])+'/'+spread([len(r['battles']) for r in a]),spread([sum(x.get('reason')=='side_window_expired' for x in r['skipped']) for r in old])+' → '+spread([sum(x.get('reason')=='side_window_expired' for x in r['skipped']) for r in a]),' / '.join(spread([r['summary']['resources'][k] for r in a]) for k in ['credits','supplies','parts'])])
parts.append('<p>把规则放回原来的108条整局，再比较已经跑过的0.16版本：</p>'+table(['普通安排','旧成功/任务','新成功/任务','每局支线过期：旧→新','新期末资金/物资/零件'],general)+'<p>训练花掉的1物资也可以做一剂药；缺物资时购买价为4资金。晚间项目还与治疗、设施、复盘竞争。新规则没有提高任务报酬来补偿训练支出；投资路线更宽松，主要因为少了重复培训和疲劳挤占。</p>')
PL=read(O/'training-planned.json');pc=collections.Counter()
for r in PL['scenarios']:
 baseline=groups[key(r)]['none'];pc['多' if wins(r)>wins(baseline) else '少' if wins(r)<wins(baseline) else '相同']+=1
parts.append('<p><b>进一步反证：</b>另跑96条“只在跨级且次日仍能出勤时训练”的走法，成功任务数较不训练：'+str(pc['多'])+'条更多、'+str(pc['相同'])+'条相同、'+str(pc['少'])+'条更少。仅有“跨级＋明天能上场”仍不足以判定值得：它没有保证更晚的轮换、休息和角色分工都受益。因此当前规则要求先看具体高阶能力和实际用途，不自动替玩家买课；这项风险保留在结果里。</p>')
parts.append('<h2 id="tr-combat">实际能力收益：与整局成本分开核验</h2><p>除完整成对整局外，取实际赚得经验的出勤快照，固定阵容、物资、关系限制和行动意图，仅减去已付费获得的经验再执行一次。这能检验能力提前的直接作用；它不替代整局对照，因为真实不训练也会改变疲劳和人员安排。输入装备已独立复制，避免贺鸣的三级搬运被错误带到低等级对照。</p>')
combat_rows=[]
for who in names:
 cases=[(r,b,q) for r,b,q in cf if r['spec']['training_actor']==who];focused=[(r,b,q) for r,b,q in scf if r['spec']['training_actor']==who]
 combat_rows.append([names[who],len(cases),sum(b['success'] and not q['success'] for r,b,q in cases),sum(q['success'] and not b['success'] for r,b,q in cases),sum(b['rounds']<q['rounds'] for r,b,q in cases),sum(b['damage']<q['damage'] for r,b,q in cases),sum(b['rounds']<q['rounds'] for r,b,q in focused)])
parts.append(table(['角色','普通策略快照对照数','额外成功','额外失败','轮数减少','受伤HP减少','另按职业意图：轮数减少'],combat_rows))
examples=[]
for r,b,q in cf+scf:
 who=r['spec']['training_actor']
 if b['success'] and not q['success'] or b['damage']<q['damage'] or b['rounds']<q['rounds']:
  if not any(z[0]==names[who] for z in examples):examples.append([names[who],r['spec']['name'],b['mission'],f"{q['levels'][who]} → {b['levels'][who]}",f"{q['success']}/{q['rounds']}轮/{q['damage']}伤害 → {b['success']}/{b['rounds']}轮/{b['damage']}伤害"])
parts.append('<details open><summary>可回查的实际例子（完整失败结果同样保留在证据中）</summary>'+table(['角色','预定策略','任务','只改变等级','无付费经验→有付费经验'],examples)+'</details>')
parts.append('<div class="note warn"><b>不把解锁提前冒充收益：</b>林岚、叶禾、江朔在部分甚至全部所测直接对照中，任务结果没有可见改善；常用基础急救、隔离及交接原本就已具备。不能因为经验变多就断言他们值得额外培养。新训练对这些人是有明确高阶用途时的提前准备，不是常规必买；没有该用途就保留阶段和物资。没有为抬高回报把基础能力挪到高等级，或削弱普通解法。</div>')
parts.append('<h2 id="tr-mentor">带教：集中追赶需要导师，也要比普通训练多做成事</h2><p>普通训练加强后，旧6经验带教会被完全替代，已改为最多24经验。它相当于把两份物资集中给一个学员，消耗一个学员阶段和导师当晚机会；经验不能超过导师。若差距不足、普通训练同样够用，就没有必要付第二份物资。</p>')
mentors=[]
for r in M['scenarios']:
 for x in r['receipts']:
  if x['kind']=='mentorship':
   who=r['spec']['training_actor'];plain=groups[(who,r['spec']['formation'],'all','standard','A')]['current'];mentors.append([names[x['mentor']]+' → '+names[x['learner']],x['day'],x['xp'],r['spec']['name'],first(plain,who,5)+' → '+first(r,who,5),f'{wins(plain)}/{len(plain["battles"])} → {wins(r)}/{len(r["battles"])}'])
parts.append(table(['真实导师/学员','日期','实际经验','整局','首次五级出勤：普通→带教','成功任务：普通→带教'],mentors))
parts.append('<p>24条按已有合作条件尝试带教的整局中，实际触发'+str(len(mentors))+'次。多数安排没有满足经验差、共同经历、阶段余量和当晚人手；保留这个结果，不给测试凭空补好感或两次共同任务。带教是有条件的追赶渠道，不应包装为全员每天可用的第二种训练。</p>')
counts=[['候选筛选',len(read(O/'training-screen.json')['scenarios']),'自然/旧规则/6/8/12经验，8角色×3安排，标准A、主线；候选阶段当时未加未用保留，属于筛选证据。'],['主要成对整局',len(rows),f"{D['actual_battles']:,}场实际任务；8角色×3安排×主线/请求全部支线×旧/新/不训练×2难度×2环境。"],['按职业意图整局',len(S['scenarios']),f"{S['actual_battles']:,}场任务；主动分配搬运/绳路/设备/湿地处置，同样意图用于训练与不训练。"],['关系带教整局',len(M['scenarios']),f"{M['actual_battles']:,}场任务；真实费用、经历与日期。"],['跨级及次日出勤策略',len(PL['scenarios']),f"{PL['actual_battles']:,}场任务，A环境，标准/困难；不是最优训练日程。"],['原普通整局回归',len(GEN['scenarios']),f"{GEN['actual_battles']:,}场任务，6行为×3难度×2环境×3结局意向。"],['同出勤状态减去付费经验',len(cf)+len(scf),'额外执行的受控对照；不冒充另一条完整自然成长整局。'],['规则与回归',T['passed'],f"含原{T['inherited']}项回归，以及阶段、入队日期、跨章保留、带教、存读、资源与疲劳边界。"]]
parts.append('<h2 id="tr-evidence">36关与整局验证的范围</h2>'+table(['验证层','数量','具体范围'],counts))
mission_rows=[]
for mid in sorted({b['mission'] for r in rows for b in r['battles']}):
 x=[]
 for mode in ['none','legacy','current']:
  bs=[b for r in rows if r['spec']['training_rule']==mode for b in r['battles'] if b['mission']==mid];x.append(f'{sum(b["success"] for b in bs)}/{len(bs)}')
 mission_rows.append([mid]+x)
parts.append('<details><summary>36关逐关执行结果</summary>'+table(['任务','不训练：成功/执行','旧训练：成功/执行','新训练：成功/执行'],mission_rows)+'<p>支线执行数不同来自实际疲劳、伤势和截止日；它们不是同一状态的单场胜率。难度与阵容不同也计入本表。</p></details>')
parts.append('<p>36条完全不使用训练的原整局，其逐场结果、期末资源及等级与0.16完全一致。本轮没有改战斗动作、地图目标、自然成长或奖励来迎合训练；只给离线战斗构造器加了装备快照隔离。先前受控三级/五级阵容矩阵仍是历史战斗证据，本轮不把它计成新执行次数。正式Godot代码与场景哈希未变。</p><p>限制：这些是预设普通策略、有限职业意图与真实账本对照，不是普通玩家访谈，也不是所有操作路径。额外训练的可选价值已有具体规则和实际案例；“所有角色练了都应提升胜率”没有被证实，也不设为设计目标。课程点击、说明可读性与玩家愿意付出的真实时间，尚需正式界面和真人试玩。</p>')
links=['training-planned.json','training-campaigns.json','training-specialty.json','training-mentorship.json','training-general-campaigns.json','training-checks.json','training-inputs.json','training-final-checks.json']
parts.append('<footer>'+ ' · '.join('<a href="'+f+'">'+f+'</a>' for f in links)+'<p><a href="ordinary-player-review.html">历史0.16审查</a> · <a href="../game/data/final_design/training_value_contract.json">当前训练规范</a> · <a href="../game/data/final_design/design_manifest.json">权威索引</a></p></footer></section>')
body='\n'.join(parts);(O/'training-value-section.html').write_text(body);(O/'training-value-review.html').write_text(page(body))
p=O/'full-game-design.html';s=p.read_text();s=re.sub(r'<!-- TRAINING_START -->.*?<!-- TRAINING_END -->','',s,flags=re.S)
if '<details id="historical-016">' not in s:s=re.sub(r'<!-- ORDINARY_START -->(.*?)<!-- ORDINARY_END -->',r'<details id="historical-016"><summary>历史0.16：普通走法审查；训练规则与价值以0.17为准</summary>\1</details>',s,flags=re.S)
s=s.replace('<main>','<main><!-- TRAINING_START -->'+body+'<!-- TRAINING_END -->',1);p.write_text(s)
inputs=[ROOT/'game/data/rules.json',ROOT/'game/data/campaign_economy_contract.json',ROOT/'work/growth-identity-review/relationships.py',ROOT/'work/growth-identity-review/model.py',ROOT/'work/ordinary-player-review/campaigns.py']+list(F.glob('*.json'))+list((ROOT/'work/training-value-review').glob('*.py'))
proof=dict(version='0.17',sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},runtime_unchanged=True)
(O/'training-inputs.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print('BUILT trainingreview')
