"""Authoritative v0.5 design-only amendments applied after v0.4 content generation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
def read(n):return json.loads((D/n).read_text())
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
bundle=read('boards.json');bundle['version']='0.5-design-review'
light={('M03','door'),('M08','block1'),('M11','lock')};heavy={('M08','block2'),('M21','route')};power={('M02','power'),('M05','pump'),('M14','cold'),('S10','light'),('S11','wire'),('S11','cold')}
for b in bundle['boards']:
 water=b['environment']['water_addition'];water['source']={'id':b['id']+'_leak','cell':[7,1],'tag':'leak_source','targetable':bool(water['cells']),'blocks_movement':False}
 water['foam_rule']='泡沫覆盖含施放轮在内的3个环境结算；若原定涨水时点落在封堵期间，将该次涨水延后到封堵结束后的第一次环境结算，并提前一轮预告；不吞掉事件，不清现有水。每漏口同一轮不能重复覆盖刷时长，后续再封堵需另付耗材/AP。'
 if b['id'] in ['M19','S09']:b['environment']['fire_pulse']['cells']=[[3,2],[4,2]]
 b['environment']['fire_pulse']['duration_rounds']=3
 b['environment']['fire_pulse']['rule']='预告点火后，所列格持续3次环境结算，各1伤害；灭火立即清除并抑制下一次点火。浅水电伤与火同格取较大值，不双扣。不可燃的墙/深水不点燃。'
 for o in b['objectives']:
  tags=['objective',o['kind']]
  if (b['id'],o['id']) in light:tags.append('light_obstacle')
  if (b['id'],o['id']) in heavy:tags.append('heavy_obstacle')
  if (b['id'],o['id']) in power:tags.append('power_socket')
  o['interaction_tags']=tags;o['risk_context']=['electrical'] if (b['id'],o['id']) in power else ['heavy_load'] if (b['id'],o['id']) in heavy else []
 for o in b['objectives']:
  if b['location'] in ['bridge','roof']:o['risk_context'].append('fall')
 for c in b['controls']:c['interaction_tags']=['machine_shutdown','work'];c['risk_context']=['electrical']
 b['equipment_targeting']='物品/专长按interaction_tags验证目标，再检查前置、距离、工量、次数和库存；名称相似不代表能用。环境漏口独立于任务成果，不产生额外奖励。'
save('boards.json',bundle)
prog=read('progression_relationship.json')
prog['protocol_training']='两人T均>=60，在营地各花1物资、共占1训练项目，获得原训练XP与疲劳，学会选定的一项协议。低风险训练不等于同意未来带电/悬空协作；现场风险条件在使用时检查。学习记录按pair+protocol保留，低于信任门槛暂不可用，恢复后不重复收费。每人最多装备2项，双方都装备才可用。'
prog['situational_cooperation']={
 'lin':{'protocol_tags':['dangerous_joint'],'when':['fall'],'required_any':['independent_anchor','third_person_protection']},
 'xu':{'protocol_tags':['partner_motion'],'when':['any'],'required_any':['explicit_authority']},
 'su':{'protocol_tags':['handoff'],'when':['any'],'required_any':['named_receiver']},
 'chen':{'protocol_tags':['dangerous_joint'],'when':['electrical'],'required_any':['power_off','reinforced_and_insulated']},
 'ye':{'protocol_tags':['dangerous_joint'],'when':['electrical'],'required_any':['power_off','insulated']},
 'he':{'protocol_tags':['dangerous_joint'],'when':['any'],'required_all':['valid_exit','retrieval_deadline_known']},
 'mo':{'protocol_tags':[],'when':[],'required_any':[]},
 'jiang':{'protocol_tags':['handoff'],'when':['any'],'required_any':['declared_personnel_cargo_priority']}}
prog['restriction_rules']='进入Q>=65后，只有协议标签与现场风险都相关才要求保障；Q>=80且满足情境与冷却时，每任务最多一次长冲突。不同条件继续显示，基础行动始终可用。低风险营地学习与现场使用分开判断。'
prog['situational_rule']='Q>=65且行为标签与现场风险均相关时才检查该角色的条件；保障条件来自当前有效的部署、断电、授权或约定记录，不能由客户端传一个true绕过。协议已学会不代表能无视条件。基础行动无条件保留。'
edge_path=D/'relationship_edge_cases.json'
if edge_path.exists():
 edge=json.loads(edge_path.read_text());rule=edge['repeated_breach_escalation'];prog['relationship_edge_cases_ref']='relationship_edge_cases.json';prog['repeated_breach_escalation']=rule
 prog['memory_events']=[x for x in prog['memory_events'] if x['id']!='persistent_breach']
 prog['memory_events'].append({'id':'persistent_breach','severity':rule['severity'],'trust_loss':rule['trust_loss'],'category':'promise','serious':True,'trigger':'连续3个值勤日内第三次独立、知情、明确同类失约；三个事件和承诺ID不同；第三次提交前预告持续失信；事故和医疗中断不计；同一次事件不重复登记普通记忆。'})
save('progression_relationship.json',prog)
combat=read('combat.json');combat['version']='0.5-design-review';
combat['actions']=[a for a in combat['actions'] if a['id']!='prepare_safety']
combat['actions'].append({'id':'prepare_safety','ap':1,'effect':'第三名站立队员在被保护者相邻干地准备一次保护；不是协议双方本人。指定被保护者和协议，标记持续到本轮结束，最多被一次联合动作消费。保护人移动、失能、离开相邻位置即失效。它提供第三人保护条件，本身不减伤、不增AP、不发信用；只有后续真实动作使用它才记有效支援。'})
combat['safeguard_producers']={'independent_anchor':'本任务已实际部署winch或xu_5，行动双方位于其明确保护范围；未部署的库存物品不算。','third_person_protection':'本轮有效prepare_safety标记，消费时再次检查保护者在场、站立与相邻。','power_off':'该对象指定供电前置/就地断路已完成，对象current_power=false；停掉无关机器不算。','insulated':'当前操作格处于已放置绝缘垫/叶禾绝缘通道。','reinforced_and_insulated':'同对象有效加固且当前操作格绝缘，两者都要有。','explicit_authority':'本任务确认过的行动授权记录包含该角色与动作类型；改约需确认，不凭点击重复发信任。','named_receiver':'当前交接的接收者已被明确指派，仍在场、空手并愿意接收；换人后重查。','declared_personnel_cargo_priority':'简报中明确选择人员与货物优先次序；违背时先显示改约/违约后果。','valid_exit':'当前有至少一条基础通行路线到未关闭出口；不把必须用被拒协议才能通过的路线当作保障。','retrieval_deadline_known':'本次行动对应救援期限已向玩家和角色明确展示。'}
combat['target_tags']='轻障碍用于crowbar；重障碍用于cutter/ye_5；power_socket用于battery；环境leak_source用于foam；fire格/焊接机用于extinguisher。通用interact始终可完成主线工量；道具不得跳过前置或把证据当成可拆物。';save('combat.json',combat)
eq=read('equipment.json');targets={'crowbar':['light_obstacle'],'cutter':['heavy_obstacle'],'battery':['power_socket'],'foam':['leak_source'],'extinguisher':['active_fire','welder'],'medkit':['standing_wounded_hero'],'insulation':['shallow_water'],'winch':['valid_anchor_and_one_cell_gap'],'shield':['empty_walkable_cell'],'scanner':['authored_environment_variant'],'beacon':['empty_dry_cell'],'stretcher':['equipped_actor_carrying_stable_casualty']}
for e in eq['items']:e['valid_target_tags']=targets[e['id']]
save('equipment.json',eq)
integ=read('integration.json');integ['version']='0.5-design-review';integ['whole_campaign_authority']='whole_campaign_contract.json';integ['late_breach_resolution']='最终结局拆为presence/personal_plan/career/relationship_overlays。后续破约覆盖相应关系台词，不覆盖人物已选职业；只有指向原违约事件的实际补救才能修复，不用无关个人计划替代。永久医疗离队仍优先改变现场/康复呈现。';integ['resolved_contradictions'].extend([['有工具但缺少合法目标','每关增加显式漏口，轻/重障碍与电源插口加类型，后期关卡加入灭火器开放后可用的火源。'],['学习协议被现场条件一并锁死','学习与使用分开；现场按动作标签、危险类型和实际保障判断。'],['关系破裂覆盖职业选择','职业去向与关系后记分开存储，避免一个结局标签包办所有后果。']]);integ['resolved_contradictions']=list({a:b for a,b in integ['resolved_contradictions']}.items());save('integration.json',integ)
print('Applied v0.5 target, contextual-cooperation and epilogue design amendments.')
