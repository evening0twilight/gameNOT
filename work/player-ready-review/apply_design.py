"""0.15 design authoring and offline referee changes; no product runtime edits."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data';F=D/'final_design';V='0.15-player-ready'
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
e=read(D/'campaign_economy_contract.json');e['version']=V;e['start']=dict(credits=30,supplies=6,parts=2)
e['main_rewards']={'success':dict(credits=10,supplies=1,parts=1),'partial':dict(credits=7,supplies=0,parts=0),'failed':dict(credits=6,supplies=0,parts=0)}
e['side_rewards']={'success':dict(credits=6,supplies=0,parts=0),'partial':dict(credits=3,supplies=0,parts=0),'failed':dict(credits=0,supplies=0,parts=0)}
# Only explicit physical caches / task reimbursements. No paying per rescued person or evidence disclosure.
spec=[('M02','spare','parts',2),('M03','parts','parts',3),('M05','module','parts',3),('M08','alt','credits',8),('M09','med','supplies',3),('M14','meds','supplies',3),('M16','goods','credits',12),('M19','device','parts',3),('M23','rebuild','parts',3),('S01','tickets','credits',10),('S02','med','supplies',4),('S02','books','credits',12),('S04','seed','supplies',2),('S04','rack','parts',2),('S05','cloth','supplies',3),('S06','meal','supplies',2),('S08','luggage','credits',12),('S08','tools','parts',3),('S09','books','credits',12),('S10','chart','credits',8),('S11','cold','supplies',3),('S12','box','parts',2)]
e['objective_rewards']=[dict(mission=m,objective=o,reward={k:n},source=('物资/零件实物签收' if k!='credits' else '社区专项运输或线路核验补助；不出售居民私物'),condition='secured',once='mission+objective') for m,o,k,n in spec]
e['objective_reward_policy']='取代旧的任意可选目标统一+1物资及S05自动+2；仅实际保全并交接的指定目标发一次，结算失败也保留确已交回成果；不因取得资料、公开隐私或多救一人额外发货币。任务预览列全奖励，档案/照片的价值是事实与叙事，不用隐藏现金强推。'
e['budget_intent']='24次必要主线可继续到结局；12支线是可选择的资源与故事机会。不能让全部设施、全部工具、持续训练同时无代价。失败保底6不削减；日常生活、基础治疗、基础行动免费。'
write(D/'campaign_economy_contract.json',e)
a=read(F/'abilities.json')
for x in a:
 if x['id']=='su_3':x['level5_effect']='5级：每任务最多一次，将自身1AP转交3格内自愿队友；接收前最多2AP、之后最多3AP，同接收者每轮一次。与原移动预算+1共享现场协调总计2次；另一次仍可选择移动协调。失败指令不扣次数。'
 if x['id']=='chen_3':x['range']=2;x['effect']='2格内一个未毁任务装置获得3点护盾，持续本任务；1AP，每任务2次，同目标一次；不穿越未知目标限制。'
 if x['id']=='mo_1':x['range']=5;x['effect']=x['effect'].replace('4格','5格')
write(F/'abilities.json',a)
g=read(F/'growth_identity_contract.json');g['version']=V
for x in a:
 if x.get('production_status')=='active' and x.get('level5_effect'):g['level5'][x['id']]=x['level5_effect']
g['balance_policy']='同一目标比较普通解法、职业解法及真实取得日期。苏棠行动转交限每任务1次；不延迟初始角色加入来掩盖强度。陈砚加固2格、莫遥远程检修5格。其他角色不一律加数值，保留救援/搬运/隔离/供电/路径各自任务机会。'
write(F/'growth_identity_contract.json',g)
# Current model: small existing-mechanic adjustments, not a new combat system.
p=ROOT/'work/growth-identity-review/model.py';s=(ROOT/'work/player-ready-review/before/work/growth-identity-review/model.py').read_text()
s=s.replace("if h['level']>=5 and key=='su_3' and destination!='movement':\n   y=", "if h['level']>=5 and key=='su_3' and destination!='movement':\n   assert not self.used.get(('ap_transfer_mission',actor))\n   y=")
s=s.replace("self.used[token]=1;return", "self.used[token]=1;self.used[('ap_transfer_mission',actor)]=1;return")
s=s.replace("or not self.usable(h,'su_3') or h['carry']:continue", "or not self.usable(h,'su_3') or h['carry'] or self.used.get(('ap_transfer_mission',h['id'])):continue")
s=s.replace("distance(h['p'],o['p'])<=1 and not self.used.get(('reinforce'", "distance(h['p'],o['p'])<=2 and not self.used.get(('reinforce'")
p.write_text(s)
# Economy settlement remains atomic and based on secured objective identity.
p=ROOT/'work/campaign-review/ledger_review.py';s=p.read_text();old="  if b['id']=='S05' and result=='success':rewards['supplies']+=2\n  elif bonus_ids:rewards['parts' if b['id']=='M03' else 'supplies']+=1"
new="""  if 'objective_rewards' in EC:
   for bonus in EC['objective_rewards']:
    if bonus['mission']==b['id'] and bonus['objective'] in secured:
     for k,v in bonus['reward'].items():rewards[k]+=v
     self.receipt('objective_reward',mission=b['id'],object=bonus['objective'],reward=deepcopy(bonus['reward']))
  elif b['id']=='S05' and result=='success':rewards['supplies']+=2
  elif bonus_ids:rewards['parts' if b['id']=='M03' else 'supplies']+=1"""
if old in s:s=s.replace(old,new)
p.write_text(s)
comfort={
 'version':V,'formal_development':False,
 'controls':{'select':'单击角色或目标先预览；再次确认合法命令才执行。右键/Esc撤销选中，永不顺带结束回合。','end_turn':'空格打开结束回合预览；有未救队友、已知致命区域或未用AP且危险任务临近期限才确认。可关闭普通剩余AP提醒，致命/放弃对象确认保留。AP耗尽不自动结束，仍可放下、撤离。','undo':'玩家阶段可撤回尚未跨越提交边界的已知战术指令，整组回滚AP、物品、伤害、贡献、知情与记忆；敌方/环境结算、揭示新信息、任务结算、隐私发布及M17最终分支提交是边界。边界前自动存档，可按当前单机规则读档。最高难度不额外偷偷禁存档。'},
 'preview':['行动AP、路径地形消耗、有效范围、实际剩余次数和装备主人','已知敌方预告、完成与撤离各自期限、缺少的前置','关系条件写成具体人物/已知原因/可满足条件；提供普通行动和取消入口','出发时显示任务后疲劳、后勤替代收益、接应费用、支线截止；换队重算','购买前显示本次能做的新动作/次数与会失去的另一项投资；训练显示下次出勤前是否跨等级','奖励明确区分基础报酬、已交回资源、可选事实，不预先收取未确认花费'],
 'guidance':{'quota':'通常每关最多1张首次规则卡；M01最多3张且分开在不同回合。只标出一个可尝试方案并注明也可绕行/另选；不要求按唯一顺序完成。','nonmodal':'提醒不遮棋盘、不夺输入；危险预告常驻图层，教程卡可关/稍后/历史重看。已掌握机制不重复弹窗。','story':'可跳过演出阅读摘要后选择，不能自动替玩家选。未读不每天红点催促，不因为不谈话扣关系。短谈2次与项目2次分别显示。'},
 'pacing':{'default':'动画速度可调/跳过重复过程，背景音/效果音独立，字体至少3档、文字不自动跳页，颜色并用图形与文字。','failure':'失败结算明确保住的成果、失去的机会、下一次仍能做什么；无资源仍可借调、免费基础行动、等待普通恢复。','replay':'通关后可只读回顾已发生全文；新周目不强制重复教程，不以全收集作为正确结局条件。'},
 'verification_limit':'当前完成流程与离线规则验证；未生成正式界面，不能宣称已经保证玩家体验流畅。'
}
write(F/'player_ready_contract.json',comfort)
c=read(F/'combat.json');c['version']=V;c['save_and_undo']=comfort['controls']['undo'];write(F/'combat.json',c)
m=read(F/'design_manifest.json');m['version']=V;m['domains']['player_readiness']='player_ready_contract.json';m['domains']['economy']='../campaign_economy_contract.json';m['domains']['authored_dialogue']='character_scripts.json';write(F/'design_manifest.json',m)
print('Applied 0.15 rules')
