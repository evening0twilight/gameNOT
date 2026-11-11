"""0.9 revisions to authored design. No production implementation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
p=D/'abilities.json';abilities=json.loads(p.read_text())
for a in abilities:
 if a['id']=='mo_1':a.update(name='远程检修',effect='1AP对4格内已知停机开关直接提供1工量，每任务2次；遵守开关前置，不叠L2施工，不作用于主目标、资料或计时环节。原标记后+2工量规则废止。',target='machine_shutdown_control',mechanic='remote_shutdown_work')
p.write_text(json.dumps(abilities,ensure_ascii=False,indent=2)+'\n')
p=D/'player_experience_contract.json';c=json.loads(p.read_text());c['integrated_revision']='0.9-integrated-review'
c['tutorial_policy']['automatic_budget']='默认自动讲解每任务至多1张，M01可分轮3张；同轮最多1张，不夺焦点、不代点。首次未展示的机制保留帮助入口，只有后续重新相关才提醒；失效排队项删除。不可逆后果确认不受讲解配额影响，同决定状态只确认一次。'
c['appraisal']['canonical_sources']='正式结果只认mission_id+authored_object/decision根事件；操作日志行号、重复搬放、客户端自拟编号、未送达目标不产生信用。每个角色从同一事件初始状态评价；方向信用最多3/任务，个人压力与自责每任务结果只结算一次。'
c['appraisal']['contribution']='救治、有效施工或最终送达路径上的实际搬运才算贡献；搬运路径消去来回闭环，保留合理绕行，不能仅按直线距离评功。摸一下、无意义传手、目标完成后补技能不记信用。'
c['tutorial_policy']['context_binding']='合作卡只在相关动作预览/受限时出现，不因队内任意怨气弹出。机会时限与对象名称读取本关权威数据。不可逆决定按决定及后果状态去重，局面改变必须重新确认。'
c['appraisal']['single_owner']='0.9整局启用external_social：禁止旧账本再加共同贡献+4与旧压力奖惩。战斗结果→评价所有者→统一账本，夜间压力只减一次；恢复自责必须引用真正占项目的恢复记录。'
c['appraisal']['exploit_boundary']='故意违背已知承诺所造成的同源损失及其补回，不算额外可靠贡献；修复最多恢复该事件实际损失，证伪猜疑不给信用。允许之后新的真实合作，比较的是同等合作机会下“无害路线”和“制造伤害再修复路线”的净收益。'
p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
contract=dict(version='0.9-integrated-review',formal_development='paused_by_user',scope='具名阵容战术、评价所有者、整局资源、帮助调度和防刷取的离线整合；不声称真人可玩性通过。',decisions=[
 ['旧共同贡献+4与新入口+3可能重复奖励','0.9整局使用单一评价所有者，旧信任/压力奖惩关闭；历史0.7脚本保留对照模式并明确版本'],
 ['一个任务分多个对象可能重复计压力、自责','对象只产出可靠贡献；个人任务结果统一结算；归责更正不再重复冲击个人状态'],
 ['用任意事件ID或未交付工作冒充新合作','固定关卡对象/决定为根事件，完成且有效才发；同任务重复结算拒绝'],
 ['给自己制造损失，再完成补救当新贡献','同源损失与补回不发额外可靠信用；纠错和补救不超过实际扣除，真实新合作正常计算'],
 ['首次提示同时触发可能排队淹没操作','非模态、每轮一张；M01最多3张，其余任务1张；主动帮助随时可开；失效项删除，重要后果确认单独保留'],
 ['莫遥标记+2在1—2工量开关上常无实际收益','改为4格内直接给停机开关1工量，两次/任务；远程分工有效，普通交互仍可完成'],
 ['只比较通用动作使具名阵容变成换对白','具名专长实际执行，带/不带技能同阵容比较；报告无收益、变差与等效配置，不强行说每关都不同'],
 ['额外奖励的any_two/both标签被误当对象ID','额外目标先解析为真实目标谓词；M15救两户/三户及三处双目标支线都按实际送达判定，本关额外物资仍只发一次'],
 ['搬运只按直线距离评功会漏算合理绕行','改用最终实际运输路径，消去来回闭环后统计真实承担；拒绝摸物与完成后补技能'],
 ['固定教学文案可能把其他关卡期限写错','当前关卡对象与时限动态绑定；只在尝试相关合作时讲拒绝，后果改变重新确认'],
 ['普通成功不能替代严重事件和事实修复','保留历史G、严重记忆、职业与关系后记分离；附来源的具体因果反馈优先于多根数值条']
 ],sources=[
 {'title':'MDA：从玩家体验反推系统动态','url':'https://www.cs.northwestern.edu/~hunicke/MDA.pdf','use':'区分规则存在、实际行为变化与玩家体验，逐层检查因果，不把系统复杂度当深度。'},
 {'title':'Into the Breach开发复盘／Matthew Davis','url':'https://media.gdcvault.com/gdc2019/presentations/Into%20the%20Breach%20Postmortem%20Final.pdf','use':'以可读性、小团队约束、明确预告和有意义的选择审查战术与长线层；尤其检查复杂但不深的系统。'},
 {'title':'Xbox可访问性指南114：界面上下文','url':'https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/114','use':'操作前知道控件用途、不会被无预期切换上下文，提示关联正确对象。'},
 {'title':'Xbox可访问性指南115：错误与不可逆操作','url':'https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/115','use':'区分普通帮助和重大后果确认；说明错误位置、原因与补救方式。'}])
(D/'integrated_review_contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
print('Applied0.9 single-owner,source,help budget and Mo remote-work revisions.')
