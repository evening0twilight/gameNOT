from pathlib import Path
import json,html,collections,re
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs';D=ROOT/'game/data';F=D/'final_design'
def read(p):return json.loads(p.read_text())
def e(x):return html.escape(str(x))
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(h)+'</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
C=read(F/'whole_campaign_contract.json');R=read(O/'whole-campaign-review.json');T=read(O/'equipment-target-review.json');names={c['id']:c['name'] for c in read(D/'characters.json')};names.update({x['id']:x['name'] for x in read(D/'equipment.json')})
names['scanner']='远程停机探针'
parts=[]
def add(s):parts.append(s)
add('<p><a href="systematic-logic-audit.html">查看0.6系统性审查与具体回归结果</a></p>')
add('<h2 id="whole">整局联动设计 · 0.6</h2><div class="note"><b>当前阶段：继续设计，暂不进入正式开发。</b>本轮把战斗结果、养成、关系、资源和剧情放进同一份状态账本推演；没有制作另一套演示游戏，也没有接入Godot运行系统。</div>')
add('<p>接下来实施时，各模块不能各自保存一份“任务成功”或“关系已经修复”。目标、投入、贡献、伤势和承诺来自同一组事实；报酬、经验、地区与结局都从这些事实推导。</p>')
add(table(['阶段','读什么','改变什么','离开阶段前保证什么'],[[x['phase'],e(x['input']),e(x['writes']),e(x['exit'])] for x in C['phases']]))
add('<h3>这次明确解决的衔接问题</h3>'+table(['容易矛盾的地方','采用的规则'],[[e(a),e(b)] for a,b in C['decisions']]))
add('<h3>结局拆为四个部分</h3><p>“战后回诊所”“一项承诺兑现”“与许舟仍有隔阂”可以同时成立。关系受损应改变相应的关系后记，不应该无故取消角色已经选定的职业去向。</p>'+table(['部分','规则'],[[e(k),e(v)] for k,v in C['epilogue_components'].items()]))
add('<h3>从第1天推演到第24天</h3><p>下列情境共用同一套资源、人物、关系与项目规则。任务成败、对象贡献、保护行为是预先给定的输入，<b>并未模拟这些关卡的全部战斗</b>。它们检查后果如何衔接，不代表这三种玩法的胜率。</p>')
rows=[]
for s in R['scenarios']:
 x=s['summary'];k=collections.Counter(v['kind'] for v in s['receipts']);rows.append([x['name'],str(x['main_count'])+'主线 / '+str(x['side_count'])+'支线',str(k['recovery'])+'恢复 / '+str(k['training'])+'训练 / '+str(x['story_projects'])+'人物计划',{'shared_control':'共同控制','evacuation':'撤离'}[x['world_ending']],str(len(x['withdrawn']))])
add(table(['情境','任务数量','重点项目安排','到达的世界结局','永久医疗离队人数'],rows))
add('<p>固定队伍与轮换都没有被安排成“必然错误”：固定队伍把经验集中在常用角色，但使用更多恢复项目；轮换留出更多训练空间，经验分布更均匀。极端失败情境中，全部主角逐步医疗离队后，主线仍由临时人员接续，但所有对应人物都进入康复收束，不能继续演正常在队的过场。</p>')
add('<details><summary>固定队伍和轮换的成长结果</summary>'+table(['人物']+[x['summary']['name'] for x in R['scenarios'][:2]],[[names[a]]+[str(x['summary']['levels'][a])+'级 / '+str(x['summary']['xp'][a])+'经验' for x in R['scenarios'][:2]] for a in names if a in R['scenarios'][0]['summary']['levels']])+'<p>这只展示同一账本下的经验分布；没有计算由此产生的战斗胜率，不据此认定哪种阵容更强。</p></details>')
add('<h3>资源不能只看“每关几乎不用耗材”的情境</h3><p>初始推演只消耗一份电池，会留下较多物资。为避免把这个结果误读成经济已经平衡，又增加“每个主任务使用两份医疗耗材”的成本情境；打包、使用、回仓仍经过同一库存规则。合法医疗使用作为已给定的任务事实，不意味着玩家每关必然受这些伤。</p>')
rows=[]
for s in R['scenarios'][:2]+R['consumption_sensitivity']:
 x=s['summary'];res=x['resources'];rows.append([x['name'],res['credits'],res['supplies'],res['parts']])
add(table(['情境','结束资金','结束原始物资','结束零件'],rows))
add('<p><b>设计判断：</b>当前最明显的长期约束是晚间项目和人员排班；物资压力对实际治疗/耗材需求敏感。暂不把所有费用整体调高来人为制造缺钱，也不宣称经济强度已经验证。货币用于装备、建设和补救；基础继续资格保持免费。</p>')
add('<h3>装备到关卡对象的对应</h3><p>泡沫的漏口已落实为每关(7,1)的环境对象；重障碍、电源插口和轻障碍均有类型标记。M19和S09加入灭火器开放后可处理的明确火区。效果、目标类型和开放时机必须同时成立。</p>')
add(table(['装备','开放后可用的关卡例子','对应对象'],[[names[x['item']],x['example']['mission'],e(', '.join(x['example']['targets']))] for x in T['examples']]))
add('<h3>一次合法任务结果包要包括什么</h3>'+table(['字段','必须表达的事实'],[[e(k),e(v)] for k,v in C['settlement_packet'].items()]))
add('<h3>玩家看见的反馈</h3>'+table(['位置','呈现要求'],[[e(k),e(v)] for k,v in C['counter_ui'].items()]))
for scenario in R['scenarios']:
 x=scenario['summary'];add('<details><summary>'+e(x['name'])+'：逐任务与逐晚记录</summary>')
 rows=[]
 for r in scenario['daily_trace']:
  n=r.get('night');res=n['resources'] if n else r['resources_after_mission'];rows.append([str(r['day'])+' / '+r['mission'],e('、'.join(names[a] for a in r['party']) or '全部临时支援')+'<br>借调'+str(r['reserves'])+'位',{'success':'成功','partial':'部分','failed':'失败'}[r['outcome']],'/'.join(str(res[k]) for k in ['credits','supplies','parts']),str(n['projects'])+'项目 / '+str(n['scenes'])+'短谈' if n else '此行后尚未夜间结算',e('、'.join(names[a] for a in n['available_next'])) if n else '—'])
 add(table(['日/任务','出勤者','结果','资金/物资/零件','夜间','次日合格主角'],rows)+'</details>')
add('<div class="note"><b>本轮检查：</b>'+str(R['passed_count'])+'项统一账本与异常路径检查，'+str(T['passed_count'])+'项装备目标/开放时机检查。明确检查了重复结算不双领奖、未打包物品不能消费、同一人不能重复占项目、治疗不提前到当天生效，以及后续关系破裂不吞掉职业选择。</div><p>仍须区分“设计规则已明确”和“玩家实际体验已验证”。这里没有执行36关全战术、全部历史修复组合或真人游玩；不会把设计推演称为正式游戏已打通。当前继续留在设计阶段。</p><p><a href="whole-campaign-review.json">完整统一账本推演记录</a> · <a href="equipment-target-review.json">装备目标检查</a> · <a href="../game/data/final_design/whole_campaign_contract.json">统一状态与流程规范</a></p>')
fragment='\n'.join(parts);(O/'whole-campaign-section.html').write_text(fragment)
master=(O/'full-game-design.html').read_text();style=re.search(r'<style>.*?</style>',master,re.S).group(0)
(O/'whole-campaign-design.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>夜潮事务所·整局联动设计0.6</title>'+style+'<main><p><a href="full-game-design.html">返回完整产品设计</a></p>'+fragment+'</main></html>')
print('Wrote whole-campaign design review and master-document section.')
