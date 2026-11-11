"""0.11 player-motivation revision. Design data only."""
from pathlib import Path
from copy import deepcopy
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
def load(n):return json.loads((D/n).read_text())
def write(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
old=load('approach_review_contract.json');services={k:deepcopy(old['services'][k]) for k in ['M05','M10','M21','S11']}
services['M05'].update(label='分两段排出浅水',mode='accumulate',consecutive_rounds=2,prerequisites=['pump'],drain_stages=[[[6,3],[5,3]],[[6,4],[7,3]]],effect='先完成原泵体检修，再分段排水。每段有效操作后，标记浅水格在下一轮变为干地；中断只损失当轮，保留已排出的水。原漏口的未来涨水照常发生，不获得无限防洪。')
services['M10'].update(label='双端确认临时登船点',mode='simultaneous',consecutive_rounds=1,extra_exit=[6,1],exit_requires=['test1','test2'],effect='两个位置在同一轮有效即可；两个原测试目标完成后开放临时出口。测试与双端确认可先后安排。')
services['M21'].update(label='两端护送通过新桥',mode='consecutive',consecutive_rounds=2,extra_exit=[6,1],exit_requires=['route'],effect='两端连续保障两轮；中断重新计数，施工完成后开放新桥出口。全游戏只保留这一处双点连续驻守。')
services['S11'].update(label='先接备用电，再切换冷柜',mode='sequence',posts=[[6,2]],stages=[[[6,2]],[[6,3]]],prerequisites=['wire'],consecutive_rounds=2,deadline=8,effect='先完成原接线任务；再在冷柜旁确认备用电，然后去分路位置切换。两步各留到一轮末，中间可以移动或处理别的任务，第一步不因第二步中断而消失。')
removed={
 'M08':'删除双端值守；保留清障、补给车、备用物资与重机移位。牵引只是可选空间操作，不为它另造必做试验。',
 'M11':'删除名单值守；切开入口、取得记录与限时取证已足够，火场分工保留。',
 'M13':'删除故障采样值守；离线日志、现场证据与机器干扰已经构成取舍。',
 'M17':'删除带载值守；保留原修复/隔离分支及地区恢复上限，不在维修任务里再套一层值守。',
 'M22':'删除在线交接附加值守；保留原交接、证据与脱敏，不重复收费或重复授信。',
 'S01':'删除岸上值守；开局短支线只保留修船与船票运输。',
 'S04':'删除灌溉值守；菜园保留种子运输和架体修复，承担较轻的节奏。',
 'S10':'删除连续引航值守；灯具与航图处理保留，避免主线M21前再来一次站点等待。'}
roles=deepcopy(old['mission_roles']);roles.update(removed)
for mid,s in services.items():roles[mid]=s['label']+'：'+s['effect']
investments={mid:dict(label=label,repair_projects=1,repair_supplies=2,sessions=2,first_day=day+1,last_day=day+4,participants=2) for mid,day,label in [('M05',5,'泵房洗消后勤站'),('M10',10,'撤离站志愿后勤组')]}
c=dict(version='0.11-player-choice-review',date='2026-11-02',formal_development='paused_by_user',services=services,removed_services=removed,mission_roles=roles,investments=investments,
 maintenance_rules=[
 '取消0.10对12台机器的通用付费维修清单。只有M05、M10两个明确的后勤设施有战役投资项目；其他机体状态保留为行动事实，不新增营地欠账。',
 '完成该关原主目标并保全设备，自动获得与修复完全相同的后勤资格；拆毁再修复不会额外获奖，也不会延长有效期。',
 '设施修复仍花1项目和2物资。次日起可用2次外部后勤协助，每晚最多使用一处、每次最多2名健康成员。志愿者代办洗消、搬运与补给，不占角色的训练／剧情安排，也不占营地的2个项目名额。',
 '后勤协助减少疲劳与压力：疲劳-12（有休息区则-16），压力-16，不给经验、信任，不治重伤，不算心理恢复项目，不回填失约。记录实际恢复量。',
 'M05仅第6—9晚、M10仅第11—14晚可用，修得晚也不续期。无足够未来晚数、无人需要休整或已有其他重要安排时，可以不修；期限后仍可自愿公益修复，但明确只有社区后记回报。',
 '维修前显示剩余可用晚数、最多可用次数、当前可参与人员和成本；不把潜在满额收益显示成必得收益。',
 '两处维修定位为可选应急后勤和社区修复，不作为常规成长循环或必做进度。默认不弹催修提醒；只有玩家已安排的未来行动因疲劳不合法、且有效期内后勤可解除该限制时，才显示可选方案提示，仍并列休息与换人。未知的未来收益不预报。'],
 cooperation_training=dict(cost='普通双人训练原价：1项目＋2物资；协作能力不另收费',trust=60,unlocks=['relay_carry','coordinated_pull'],basic_actions=['protected_work','mutual_cover'],xp='沿用普通训练每人3经验，不额外发经验',rule='保护作业和交叉掩护为无需训练的现场协作，不设60信任门槛，但仍检查具体关系保障、AP与位置；接力和定向牵引在双向信任≥60的一次普通双人训练中一并学会，无独立购买菜单。高级动作信任不足时暂不可用，恢复后无需重买。'),
 evaluation=dict(player_questions=['这一轮在等什么，是否有正在改变的局面？','省出的项目接下来给谁用？','普通解法需要怎样的站位、工具和次序？','合作在同一局面下改变哪些可实现结果？'],dominance='在同一目标与初始状态下比较成果集合、伤亡、伤害、轮数、AP和学习/工具成本。保留普通路线胜出的案例；有限策略搜索不等于最优性证明。',cadence='24个主任务中3次附加现场操作，全36任务中4次；只有M21要求双点连续两轮。其余8处删除附加动作。'),
 carry_forward=['原主目标、加入日期、关卡期限和基础动作保留','额外目标可放弃；只有已经接受的具体承诺才可能产生失约','不模拟玩家偏好为客观满意度','不禁止普通移位、诱导、换人、暂停、绕路和提前关停'])
write('player_choice_contract.json',c)
progression=load('progression_relationship.json');progression['protocol_training']='0.11：保护作业和交叉掩护无需训练或60信任门槛，但仍检查动作条件与具体关系保障。接力与定向牵引由双向信任均≥60的二人，在一次普通双人训练中一并学会；只付原训练的1项目＋2物资，每人3经验／8疲劳，不另收费。高级动作信任回落时暂不可用，恢复后无需重买。';write('progression_relationship.json',progression)
# Clear retired affordances from CURRENT boards; historical0.10 contract stays readable.
bd=load('boards.json')
for b in bd['boards']:
 if b['id'] not in old['services']:continue
 s=old['services'][b['id']]
 for enemy in b['enemies']:
  if enemy['id']!=s['source_enemy']:continue
  enemy['recoverable_asset']=b['id'] in investments
  enemy['asset_disclosure']=('保全或修复可获得限期外部后勤协助；修复1项目＋2物资。' if b['id'] in investments else '机体损毁保留为现场后果，不新增付费维修项目。')
 for i,o in enumerate(x for x in b['controls'] if x['id'] in s['linked_controls']):
  if b['id'] in services:
   o['label']='现场联动分路'+str(i+1)+'（影响'+services[b['id']]['label']+'）';o['service_linked']=s['id'];o['service_shutdown_effect']=services[b['id']]['effect']
  else:
   o['label']='设备停机分路'+str(i+1);o.pop('service_linked',None);o.pop('service_shutdown_effect',None)
write('boards.json',bd)
exp=load('player_experience_contract.json');exp['approach_guides']=[dict(id='G16',first='首次预览当前现场操作',copy='这是可放弃的额外成果。界面显示本关是累计、同步、连续还是换位操作，以及中断会损失什么；同时列出当前可用的普通办法。',budget='仍与原教学共享每关一张自动卡，关闭后保留目标和风险标记'),dict(id='G17',first='首次预览损毁后勤设施',copy='显示保全/拆除的实际后果。只有M05、M10有可选后勤修复，明确成本、有效期与剩余次数；其他设备不提示虚假的维修债务。')];exp['approach_revision']='0.11-player-choice-review';write('player_experience_contract.json',exp)
print('Authored0.11:4distinct field tasks,8removed waits,2finite support investments,2basic guards and2advanced actions learned with ordinary pair training.')
