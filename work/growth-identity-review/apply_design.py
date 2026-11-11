from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design'
def read(n):return json.loads((D/n).read_text())
def write(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
upgrades={
 'lin_1':'5级：稳定距离2→3，AP与任务次数不变。',
 'xu_1':'5级：携带伤员时也可使用个人抛索，无需另设锚点；仍只跨最多一格障碍、落在干地，支付原AP与次数。',
 'su_3':'5级：同一指令可选择原移动预算+1，或将自己的1AP交给3格内自愿队友；两种方式共享任务次数。同一接收者每轮最多接受一次，当前AP不超过3，不凭空增加全队AP。',
 'chen_3':'5级：同一装置一次性护盾3→6；仍不能复活装置或重复加固同一目标。',
 'ye_3':'5级：直线绝缘最多2格→3格；遇墙/深水不越过，不改变可通行性。',
 'he_1':'5级：屏障由持续到下轮改为持续本任务，仍3HP，可被击破且不能在占用格落脚。',
 'mo_1':'5级：对已知停机开关单次工量1→2；仍不作用于救援、证据、主目标或计时操作。',
 'jiang_1':'5级：交接距离1→2；远距必须直线且中间是无占用的可通行干地，不能越墙/机器/深水。AP分配、接收者和关系检查不变。'}
A=read('abilities.json')
for a in A:
 if a['id']=='ye_1':a.update(name='分路隔离',ap=2,charges_per_mission=1,range=1,effect='邻接机器支付2AP，隔离本任务的危险输出，机体仍占格并保留供电；每任务一次。已经产生的火焰/增援不消失，不能复活已毁机器。普通停机仍合法，但会关闭同一供电分路。')
 if a['id']=='xu_1':a['effect']='沿直线跨最多一格墙/深水到空干地，通常不能携带伤员；未满5级的携带例外需已部署winch锚点。花1AP、每任务2次。'
 if a['id']=='jiang_3':a['effect']='花1AP使用一份已打包医疗药剂，为相邻站立队友恢复3HP；自身可在携带时使用。不能复活或生成药剂；0.13没有其他耗材转用分支。'
 a.pop('level5_effect',None)
 if a['id'] in upgrades:a['level5_effect']=upgrades[a['id']]
write('abilities.json',A)
contract=dict(version='0.13-growth-identity',date='2026-11-02',formal_development=False,
 battle_form=dict(mechanics='固定8×8网格的空间战术救援',presentation='固定俯视2D：有职业剪影的角色棋子、场景插画/地块、立绘剧情',turns='我方全队回合，每人2AP，玩家交错操作三人；结束后按预告结算机器和环境，无速度条',not_chosen=['抽牌组牌对撞','3D站桩阵列回合','实时动作','3D网格场景'],reason='现有乐趣依赖地形、搬运、供电与撤离路线；站桩阵列会丢掉这些选择，3D网格仅增加表现管线而不增加当前核心玩法。',
 feedback=['选中及合法目标轮廓','路线与受击范围预览','短移动/作业/发射提示','命中与护盾吸收反馈','资源/伤势/目标状态变化'],
 art_budget='8套角色立绘及表情、8个可辨识棋子主体，通用移动/作业/受击效果。换装备显示图标及通用效果，不承诺逐武器握持模型和专属动作。棋盘图仅为布局规范，不是最终美术质量证明。',
 weapon_policy='不新增随机武器词条和独立武器树。基础攻击是统一破拆动作；7种救援装备改变可做的操作和站位。2D同样需要目标规则、反馈、平衡和说明，不能把换一串伤害数值当新武器内容。'),
 level5=upgrades,
 training=dict(normal='每人1物资、+min(3,100-当前经验)、+8疲劳；1项目，同人当晚一次。已经100经验者不接受付费经验训练。',presentation='显示今晚训练能否让下一次出勤前达到2/3/5级，以及实际获得经验；不把下一任务结束后才取得的经验当作开局能力。默认不催促每日训练。',purpose='常驻成员主要靠行动成长；主动投入用来提前一个任务取得专长或让后备成员赶上。不是为通关制造每日刷经验义务。'),
 positive_relationships=dict(
  eligibility='关系短谈明确选择合作约定；双方在两次不同任务中各有真实有效目标贡献，且这些任务无已记录违约；目前没有双方未解决的条件合作级冲突。仅同队、反复交接、点击对白或事后修好自己制造的事故不能生成新资格。',
  mentorship='适用于已有12组关系节点的人物对。1项目、2物资、两人各+8疲劳；导师不获经验，学员最多+6，不能超过导师当前经验或100。每学员每章一次，只有实际增益大于普通3经验时可安排。不能教会另一个人的专长，不发信任或冲突修复奖励。',
  dispatch='R04苏棠/江朔或R10苏棠/莫遥形成有效合作后，可在后续主线让一人出勤、一人占用原有后勤席位，支付2物资改派到已公开东侧接应点(7,7)。替换原常规出口而非白送一个出口；原后勤+1物资收益取消，后勤8疲劳和2经验照常。普通出口选择始终免费。',
  limits='接应不改变目标、车辆固定目的地、敌人和期限；M10/M21已完成的现场出口仍按原规则开放。每任务一次出发前决定，不在战斗里来回切换；不能在支线使用。人手/资源不足、重伤或离队时不提供方案，不影响基础出勤和结局。',
  independence='选择保持专业距离不扣好感、不删除普通训练、不锁结局。改选共同计划需要新的明确同意，不抹去旧记忆；已用带教章次数不会刷新。'),
 replay='来自不同专业分工、人物共同计划/独立边界、M17修复或隔离及最终治理/重建/撤离路线的组合；人物过去不随机改写。天气变体和同一关省AP不单独充当重玩承诺。',
 added_complexity='新增机器危险输出隔离与全队守恒的AP转交；其余L5用既有范围、工量、护盾、持续时间和路径检查。正向关系新增两种营地/出勤模板，不新增56套合击动画或一套合作经验货币。',
 evidence_limits=['有限策略搜索和预设偏好账本不是玩家访谈或真人测试','等级对照是能力试验，实际可取得时间另由完整战役核对','已采样日期合法阵容均有基本通关路线；不据此宣称穷尽天气、配装与关系状态，不以剥夺普通操作制造专业价值'])
contract['training']['recommendation']='带教和训练不默认勾选、不每日催促。预览计划中的下一次出勤、当前经验、普通训练及带教分别何时解锁、导师/学员占用和恢复机会；超出普通训练3经验的临界解锁才提示考虑带教，不承诺更高任务奖励。'
contract['positive_relationships']['dispatch_preview']='出发前并排显示免费出口和改派出口、目标位置、预计搬运路径与成本；只提供几何与已知风险预览，不泄露未知事件或替玩家求最优路线。改派替换常规出口，不能在失败后免费改回。'
write('growth_identity_contract.json',contract)
P=read('progression_relationship.json');P['levels']['L5']='强化本人的一项现有专长用途，见growth_identity_contract.level5；不再统一增加一次使用次数，不增加第三个技能按钮。';P['positive_relationships_ref']='growth_identity_contract.json';P['training_rule']=contract['training']['normal'];write('progression_relationship.json',P)
scope=read('production_scope.json');scope['version']='0.13-growth-identity';scope['growth']['L5']=P['levels']['L5'];scope['battle_form']=contract['battle_form'];scope['positive_relationships_ref']='growth_identity_contract.json';scope['added_complexity']=contract['added_complexity'];write('production_scope.json',scope)
choice=read('player_choice_contract.json');choice['version']='0.13-growth-identity';write('player_choice_contract.json',choice)
stories=read('stories.json')
for n in stories['relationship_nodes']:
 n['scheduling']='免费短谈占当晚短谈次数；保存agreement/distance选择，不直接加信任、经验或学习技能。'
 n['positive_payoff']='符合两次真实合作与当前关系条件后可带教；不强迫亲密。'+('另可安排东侧接应，一人出勤一人后勤，支付实际成本。' if n['id'] in ['R04','R10'] else '')
write('stories.json',stories)
combat=read('combat.json');combat['carrying_exception']='江朔交接/实际药剂补给，以及许舟抛索：5级可携带；未满5级须从已部署winch锚点邻接出发。其他AP、次数、落点与关系条件仍检查。';combat['growth_identity_ref']='growth_identity_contract.json';write('combat.json',combat)
for file in ['development.json','logic-audit.json']:
 p=ROOT/'game/docs'/file
 if p.exists():
  d=json.loads(p.read_text());d.update(design_version='0.13-growth-identity',latest_review='../../outputs/growth-identity-review.html');d['authored_this_revision']=['2D空间战术形式与武器表现约束','五级现有专长用途强化，取消统一额外次数','关系带教和有限的出发前接应方案','36关受控对照与真实成长战役复审'];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Applied0.13:2Dspatial rescue; differentiated growth and2finite positive relationship templates.')
