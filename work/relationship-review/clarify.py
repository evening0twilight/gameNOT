"""Design-only clarification and counterexample, not a runtime patch."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design';O=ROOT/'outputs'
# Compare the existing ordinary-memory cap with a specifically authored repeated-breach escalation.
def trace(old_grudge,escalate):
 memories=[];rows=[]
 def resentment(day):
  ordinary=sorted([m['amplitude']*2**(-(day-m['day'])/3) for m in memories if not m['serious']],reverse=True)
  severe=sum(m['amplitude']*(.35+.65*2**(-(day-m['day'])/8)) for m in memories if m['serious'])
  return min(100,old_grudge+min(24,sum(ordinary[:3]))+severe)
 for day in [1,2,3]:
  before=resentment(day);serious=escalate and day==3;severity=18 if serious else 12
  amplitude=min(40,severity*1.25*(1+.7*(old_grudge/100)**2)*(1+.8*(before/100)**2)*1.025*(1+min(.4,.1*(day-1))))
  memories.append(dict(day=day,amplitude=amplitude,serious=serious))
  rows.append(dict(day=day,before=round(before,2),new_strength=round(amplitude,2),serious=serious,resentment=round(resentment(day),2)))
 return rows
old=trace(42,False);new=trace(42,True);fresh=trace(0,True)
assert old[-1]['resentment']==66 and new[-1]['resentment']>=80
contract={
 'version':'0.5.1-design-clarification',
 'body_vs_relationship':'身体恢复只改变身体状态；不自动清除、增加或翻倍人际怨气。伤势可造成个人压力，怨气需要针对某人的已知、可归责事件。',
 'no_auto_resentment':['同队出勤','在已知风险下诚实执行任务但失利','资源不足而未承诺能立即治疗','正常等待免费恢复','已解释并获得同意的改约'],
 'attribution':'隐瞒风险、违背明确接应/治疗约定、未经同意追加承担等才建立有向记忆。队长作出决定不能默认让执行队员背责；只知道结果但不知道责任时保留未知，不凭空读心。',
 'one_incident':'同一事件即使同时造成受伤、撤离失败和延迟治疗，也不重复创建三份同义怨气；严重后果用于该事件的严重度/性质，个人压力另有上限。',
 'repeated_breach_escalation':{'id':'persistent_breach','category':'promise','severity':18,'trust_loss':12,'serious':True,'conditions':['观察者已知同一责任对象的行为','连续3个值勤日窗口内，第三次独立明确承诺被违背','三个承诺/事件ID不同，同一失约不能通过重复点击或重复结算计数','每次均有真实责任份额；事故或医疗中断不计','第三次行动提交前明确预告会被视为持续失信'],'effect':'将第三次事件以严重记忆登记一次，不同时再加一份普通记忆；此前事件保留。不是普通拌嘴自动升级，也不暗改阈值。'},
 'thresholds':'Q=R+0.25*max(压力-40,0)，封顶100。45戒备、65相关条件合作、80达到冲突资格；还需相关情境和已提示。100没有额外强制动作，不随机伤害队友、不删除装备、不因关系强制医疗离队。',
 'at_max':'本队每任务最多一次长冲突，限制仍在对应行动预览中持续显示。玩家可以提供真实保障、换职责/搭档、走基础独立办法、放弃额外目标或撤退；不能靠反复点确认刷出合作。爆发不会自动清零怨气。',
 'recovery':'休息降低个人压力，普通事件随时间变淡；具体认责、实质补救和后续守约作用于各自事件；历史旧怨需相关历史处理。亲近、专业信任与怨气分别保留，不强制所有人和好。',
 'known_remaining_audit':'满值后有效记忆的总量、同因事件合并、对话冷却与持续限制必须继续做组合审查。当前没有证据支持宣称所有逻辑已无问题；这份澄清不作为零漏洞承诺。',
 'reference_examples':{'conditions':'三个不同日、三个不同已知承诺、同一方向；敏感度1.25、责任1、压力10；不含任务后其他事件或实际战斗。','old_rule_old_grudge42':old,'new_rule_old_grudge42':new,'new_rule_no_old_grudge':fresh}}
(D/'relationship_edge_cases.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
(O/'relationship-edge-checks.json').write_text(json.dumps({'ordinary_only_cap_counterexample':old,'repeat_escalation_old_grudge':new,'repeat_escalation_no_grudge':fresh,'checks':['same-category ordinary cap prevents further growth above old_grudge+24','third distinct warned breach as serious memory can reach rupture without double-counting','same event is one source, not three separate memories'],'scope':'Design calculation, not runtime implementation or a full balance test.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'existing_rule':old,'specified_escalation':new,'no_old_grudge':fresh},ensure_ascii=False,indent=2))
