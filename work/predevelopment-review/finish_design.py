from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]; W=Path(__file__).parent; D=R/'game/data'; F=D/'final_design'
def read(p):return json.loads(p.read_text())
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
base=read(F/'release_baseline.json');V=base['version'];ds=base['domains'];views=read(W/'views.json')
def add(key,name,x):
 x={'version':V,**x};ds[key]=x;views['game/data/final_design/'+name+'.json']=key;write(F/(name+'.json'),x)
flow=read(D/'campaign_flow.json')
flow.update(version=V,status='authoritative_design_state_graph_not_runtime',start='title',terminals=['ending','title'],terminal='ending')
flow['transitions']=[
 {'from':'title','to':'new_game','on':'new'},
 {'from':'new_game','to':'briefing','on':'confirm_empty_slot_difficulty_variant'},
 {'from':'new_game','to':'title','on':'cancel'},
 {'from':'title','to':'load','on':'choose_saved_slot'},
 {'from':'load','to':'restore_checkpoint','on':'valid_schema_hash_and_receipts'},
 {'from':'load','to':'load_error','on':'invalid_or_incompatible'},
 {'from':'load_error','to':'load','on':'select_backup_or_other_slot'},
 {'from':'load_error','to':'title','on':'cancel_preserve_all_files'},
 *flow['transitions'],
 {'from':'ending','to':'postgame','on':'finish_or_skip_epilogue'},
 {'from':'postgame','to':'title','on':'return'},
 {'from':'title','to':'settings','on':'open_settings'},
 {'from':'settings','to':'title','on':'close'}]
flow['side_decisions']={
 'prepare':'点击支线先打开准备页；出发前允许取消，退出准备不消耗该支线。',
 'defer':'不接受不等于解决；开放日及下一日内仍在待办，截止最多D23。一天最多一场支线。',
 'decline':'本日跳过返回营地，仍可在截止前再选；只有明确放弃整项或过期才关闭。',
 'active':'出发后成功/部分/失败/撤退均算已尝试，不反复刷同一任务。',
 'no_crew':'主线允许免费借调补足真实空位；支线没有借调，不够三人就延期或跳过。'}
flow['pause']={'entry':'任何玩家控制稳定点可暂停；动画期间先完成原子动作再暂停。','actions':['继续','设置','帮助/日志','保存','读取','回主菜单','退出桌面'],'return':'暂停/帮助/设置关闭回原阶段与原选中对象，不自动结束回合。','save_failure':'写入失败显示可重试/改槽/取消，旧有效档保留；回主菜单提示最后有效保存时间。'}
flow['difficulty']={'initial':'默认标准，开局并列展示三个难度和严峻的永久医疗离队边界；选择严峻须勾选理解。','change':'只在主线/支线出发前准备页可改，下一次deploy生效；任务中锁定，恢复已存难度。','history':'改变难度不复活或退还过去损失；结局日志记录用过的难度，不设计纯难度限定奖励或成就。','variant':'首次周目A；通关记录只解锁新存档A/B选项，不携带资源/等级；不覆盖旧存档。'}
flow['planning']={'preview':'同一规则函数预览AP、工量、落点、伤害、次数、风险和关系条件；更改队伍/装备/项目即重算。','defaults':'未分配工具留仓；有效原阵容可保留；不能用隐藏自动补药扣资源。L2默认work但出发前可改。','deployment':'检查人物资格、真实空位、预测疲劳、槽位、包容量、费用、出口与世界路线，再整体提交；校验失败不扣任何资源。','battle':'队员2AP可交错行动→玩家明确结束→按敌人ID→环境→持续目标/运输→救援期限→整关时限。0AP仍可放下或紧急撤退，正常离场要1AP。','undo':'一组指令回滚AP/HP/库存/贡献/知情/记忆；跨敌方环境、新信息、结算、公开隐私或M17分支确认边界后不能战术撤销，可读合法保存点。'}
flow['camp_order']=['进入营地展示剩余2项目、2短谈与各自占用；个人第二段选择需同时有短谈和项目余量。','玩家按任意合法顺序安排训练/恢复/治疗/设施/核查/人物计划；同人每夜最多参加一个项目。','0项目也可结束夜晚；0资金仍可睡眠和免费恢复，不收取维持费。','已确认项目立即结算，未确认草案不收费；跨项目不能假定未来设施已建成。','D23只提示一次未结承诺与路线资格，允许继续安排；明确结束这夜才进入终局准备。','D24仍有主线配队、难度和现有库存安排；没有新训练/核查/营地或补签个人线。']
flow['failure_policy']=['任意主线结果推进下一日；失败修饰只影响下一主线的一格碎石，不累计。','损失目标依赖项立刻标不可达，允许保其他成果或撤退；不要求穷耗AP等时限。','普通重伤按恢复日返队，保留XP/关系/课程记录；伤势恢复不自动加减怨气。','严峻失能者只有在明示期限内未救回/明确放弃才医疗离队；站立紧急撤退按可恢复重伤。','队伍无人可出勤仍可借调继续主线；终战未达路线目标走撤离结局。']
flow['persistence']={'slots':'10个手动槽；每个存档1个滚动自动槽和1个上次有效备份。覆盖其他周目明确确认；新游戏默认空槽，不删除旧档。',
 'write_points':'稳定玩家阶段、准备页、营地项目提交后；每个主/支线出发前、唯一结算后、夜间推进后自动保存。边界确认前先保存，动作动画和敌方结算中不保存半状态。',
 'atomicity':'整个状态+receipt集合+版本/内容指纹写临时文件→读回校验→保留上一有效备份→原子替换。失败不发布半档；重复读档不补发奖励。',
 'restore':'有效档恢复保存的阶段、难度、所有领域状态和可见预告；清空纯UI草案。只在白名单稳定阶段恢复；不能从日志猜测遗漏次数。',
 'incompatible':'首发只保证本版schema。相同schema且在显式兼容清单内的内容修订才可载入；不在清单则说明原因并保留原档，绝不无声按新规则重算旧事件。后续需迁移时先离线迁移副本并独立验收。',
 'corrupt':'拒绝坏档，显示备份时间并由玩家选择备份/另一槽/返回；不自动覆盖原文件。',
 'catalogue':'完整必存字段见persistence_inventory域，所有新增字段必须进入往返测试。',
 'exit':'退出不强制上传或联网；未保存时列出最后成功存档，不以保存失败锁住程序退出。'}
flow['endings']={'world':'按D23锁定可选路线及M24实际目标决定；未达目标回落撤离，不能靠汇总分补造目标。','people':'presence→career→personal_plan→逐方向关系附注。已兑现计划不被后来重伤抹去，未完成计划因医疗中断不写成恶意背约。','postgame':'只读已发生全文/支线错失/事实摘要；未发生内容不伪造为本周目经历。可另开新周目；不返场刷资料。'}
ds.pop('flow',None);views['game/data/campaign_flow.json']='player_flow';write(D/'campaign_flow.json',flow)
add('player_flow','player_flow',flow)
locations=sorted({b['location'] for b in ds['boards']['boards']})
scope={
 'product':'同一最终项目内实现的离线单机；固定俯视2D空间救援、群像成长和有因果的关系；无运行时生成式AI。',
 'platform':{'primary':'Windows 11 x64桌面，键鼠，简体中文。','development_host':'macOS只作为当前开发环境；macOS公开发行、手柄、移动端、网页均不计首发承诺。','engine':'已存在本地Godot 4.7.2 stable官方标准版，GDScript、Compatibility；本轮--version已确认。沿用当前工程，不创建另一演示项目。','ui':'1440×900设计基准；覆盖1280×720、1920×1080、2560×1440及窗口缩放；正文三档，复杂页可滚动。'},
 'content':{'characters':8,'main_maps':24,'side_maps':12,'days':24,'camp_nights':23,'abilities':16,'equipment':7,'consumable_types':1,'enemy_archetypes':6,'situational_cooperation':4,'field_operations':4,'repairable_logistics_facilities':2,'camp_facilities':4,'facility_tiers':2,'story_scenes':96,'world_endings':3,'environment_variants':2},
 'screens':[
 ['title','主菜单','新游戏/继续/读档/设置/退出；通关解锁状态'],['slots','存档管理','空槽、覆盖确认、版本/日期、备份、失败恢复'],['new_game','新局设置','三难度披露和环境变体'],['briefing','城市/任务简报','今日主线、地区事实、支线期限、已知环境'],['deployment','出勤准备','3人/后勤、装备、L2、药剂、关系条件、可选接应'],['battle','战斗棋盘','操作、预告、目标/期限、上下文协作、撤退确认'],['settlement','结果','目标/人员/承诺分开，资源XP和关系逐条原因'],['side_offer','支线待办','接受/稍后/过期/已尝试状态'],['camp','营地安排','2项目2短谈、疲劳预览、睡眠及D23终局提示'],['growth','角色与培养','等级专长、真实课程/带教成本、未来出勤'],['supply','装备与设施','购买/未出勤撤销、制作、库存打包、升级用途'],['relations','关系事实','方向/记忆/条件/认责补救/约定，不显示误会为定罪'],['story','人物对话','表情、选择/延期、摘要跳过、重伤/来信变体'],['journal','任务与证据日志','已知事实、核查/发布范围、未发生内容占位'],['ending','结局/回顾','世界+各地+人物四层收束、另开存档'],['settings_help','暂停/设置/帮助','音量、字号、速度、动效、键位、保存和返回']
 ],
 'assets':[
 {'id':'character_design','quantity':8,'unit':'角色设定板','detail':'正侧/三分之二设定、职业装备、色板；先8人轮廓与96px头像辨识。'},
 {'id':'portraits','quantity':16,'unit':'基础服装立绘','detail':'每人现场/日常各1套；共64个表情语义差分（8人×8种），用分层脸部复用两服装，不等于每表情再画两张完整人体。'},
 {'id':'hero_tokens','quantity':8,'unit':'棋子主体','detail':'俯视职业剪影，选中/受伤/搬运用状态层；不做方向骨骼或武器动作组。'},
 {'id':'responders_civilians','quantity':6,'unit':'通用标记','detail':'借调队员2种、居民成人/儿童/伤员/工作人员4种；按ID区分，不加可培养人物。'},
 {'id':'enemies','quantity':6,'unit':'敌人主体','detail':'六种机器各有意图、停机/损毁层，动画用通用反馈。'},
 {'id':'location_kits','quantity':12,'unit':'地点套件','detail':'对应'+','.join(locations)+'；共享地面/水/碎石/墙/深水，不为36图各画整张不可复用背景。'},
 {'id':'narrative_backgrounds','quantity':8,'unit':'剧情背景','detail':'事务所、诊所、码头、旧城、工厂、水闸、屋顶、避难点；昼夜/雨用色调与叠层。结局复用，不新增独立CG。'},
 {'id':'icons','quantity':48,'unit':'图标预算','detail':'16专长+7工具+1药剂+4协作+4设施+3资源+13状态/导航；使用统一尺寸和文字辅助。'},
 {'id':'vfx','quantity':10,'unit':'通用反馈模板','detail':'选择、路径、作业、命中、护盾、治疗、供电、停机、搬运交接、目标完成；无逐武器专属动画。'},
 {'id':'music','quantity':6,'unit':'循环曲','detail':'主菜单/营地、两种任务强度、人物日常、沉重事件、结局；交叉淡入淡出，不做动态作曲。'},
 {'id':'sfx','quantity':24,'unit':'短音效预算','detail':'界面6、动作8、机器/环境6、目标/伤势提示4；不做全语音。'}
 ],
 'asset_quality':'以上为制作清单和复用计划，不是假称已经生成的资产。先做8人轮廓+2个代表人物的完整立绘/棋子+一张任务场景并由用户审美确认，标准固定后批量制作；这是生产内验收，不另做丢弃游戏。',
 'work_allocation':{'assistant':'规则数据、正式工程实现、工具/自动检查、文案与素材整理、构建和缺陷修复；不得用离线通过替代实机证据。','user':'产品和人物审美决策、实际操作反馈、持有素材与账号、Windows运行测试/试玩组织；可用其他模型生成素材。','hiring':'不把雇人作为交付前提，也不擅自外包。若最终美术/音乐未达标准，先修订现有素材；确需购买或委托时提供具体对象/用途/许可/报价后另决策。'},
 'cost_model':{'confirmed_cash':'本轮新增支出0；未采购或委托。','categories':['生成模型额度（用户自选，按实际用量）','确有需要才购买的音乐/音效/字体或美术授权','Windows测试设备/环境（已有可用则不重复买）'],'estimation':'不按角色数量凭空报现金总预算；先由清单得出产出量、挑选/返工耗时，再按实际工具套餐或授权报价核算。开发工时是主要投入，首个生产里程碑完成后用实际速度重估。','publishing':'商店费、宣传、本地化、发行成本本次不估，用户已另行安排。'},
 'architecture':{'rules':'一个纯状态转换入口供合法性、预览、执行使用；UI不能维护第二套数值。','state':'campaign/battle/actors/inventory/social/story/receipts/tutorial/save元数据，保存同一一致快照。','events':'稳定root_decision和对象ID；先指令预检，原子提交行动事实，再由单一结算发布后果。','content':'36关和96场景使用同一数据契约与编辑校验，不做36套独立战斗脚本。','presentation':'规则事件驱动动画/声音；跳过动画不改变逻辑或重复结算。','offline_referee':'Python探针只作设计证据；正式GDScript需通过同一输入/期望夹具，不复制探针所有实验/搜索代码到产品。'},
 'production_milestones':[
 ['P1','正式规则内核与持久化','当前工程内打通指令、预览、存档和M01→结算→营地→M02；完成物直接保留。','所有核心字段往返、失败不中断、预览与执行相同'],
 ['P2','第一章完整可玩与美术标准','六主线及本章支线、训练/关系/人物项目和代表素材。','普通玩家能读懂目标、结束回合和解决条件；低资源可继续'],
 ['P3','全四章内容接入','余下地图、人物分支、96场景及三世界结局。','全36图有实机路径记录，24日正反结果闭环'],
 ['P4','完整产品验收','最终素材、中文显示、存档恢复、Windows与真人试玩。','无阻断缺陷，达到acceptance域产品标准，未通过项修复后再谈发行']
 ],
 'not_in_first_release':['3D/骨骼战斗动画','抽卡/充值/联网/服务器','实时AI对话','程序生成关卡或无限刷取','第三专长/随机武器树','56套专属双人合击','全语音/独立结局CG','Mod/创意工坊','手柄/网页/移动端','云存档/成就等商店SDK（发行讨论再定）']}
add('release_scope','release_scope',scope)
criteria=[
 ('D01','规则权威','只有本版baseline生效；投影视图逐字匹配，36关/16能力/7装备/96剧本引用完整，无历史数值重新启用。','static','current_check'),
 ('D02','完整流程','新局/读档/主支线/营地/终局/退出有定义；D24无营地；零资源和零健康主角仍有主线及结局路径。','offline','current_check'),
 ('D03','培养与阵容','自然XP和恢复不削弱；训练/带教共用有限课程；默认阵容结果回归相同；L2倾向按角色生效不串人。','offline','current_check'),
 ('D04','经济与来源','唯一目标奖励表；重复结算、退款、无效操作不改变余额；已消费+归还=带出，额外目标无通用奖励。','offline','current_check'),
 ('D05','人物与关系','真实知情/责任/同源事件去重；信任每方向每任务最多3；无误会修复刷取；职业/履约/在场/关系分开。','offline','current_check'),
 ('D06','边界与范围','能力/装备/现场操作及修复范围固定；严重难度永久离队已告知；不可把旧报告视作本版通过。','static','current_check'),
 ('R01','预览执行','全部动作类型在合法/非法/过期状态夹具上：预览效果=提交差分；取消/非法操作零写入；跳动画不变结果。','runtime','pending'),
 ('R02','36关与低资源整局','全部36图在正式程序跑A/B和三难度各至少一条可继续路径；完整主线零付费训练、少支线、偏爱固定队、重伤轮换四类存档走到结局；不要求每条路径全成果。','runtime','pending'),
 ('R03','伤势与永久离队','期限最后一轮救出/少一轮超时/站立紧急撤退/全队失能在三难度各测；结果与披露一致；基础行动不因关系被夺走。','runtime','pending'),
 ('R04','保存与中断','每种稳定阶段往返得到相同下一预告/奖励/情绪；模拟写入失败、坏档、重复结算、未知版本；有效旧档保留。退出/崩溃不丢失此前成功自动存档。','runtime','pending'),
 ('R05','人物分支','96节点每一选项在正常/重伤/离队和已知/未知责任下检查适用内容；不在场不说现场台词，没发生不说已发生，承诺未核验不生成已履约结语。','runtime_editorial','pending'),
 ('R06','教程与输入','M01最多3张分回合、其余每关最多1首次卡；开关不改规则，过期目标撤下提示；无AP有结束/撤退入口；键鼠/文字缩放不藏确认/取消。','runtime_human','pending'),
 ('R07','首发硬件','在记录CPU/GPU/内存的Windows 11 x64 8GB参考机测试；1080p棋盘目标60fps（稳定场景95%帧≤16.7ms），冷启动≤10s，输入反馈≤100ms，连续2小时内存无持续增长趋势；未实测不发布最低配置。','runtime_device','pending'),
 ('R08','素材与授权','清单素材可追溯来源/使用权，8人96px辨识一致；字号三档无遮挡，重要信息不只靠颜色；独立音量与静音生效；用户确认代表素材后再批量。','asset_human','pending'),
 ('H01','新人能上手','至少5名未看方案的目标玩家；至少4名无需口头教学能在M01说明目标、预告、撤离及一种替代解法；记录卡住位置，不能用测试者背设计文档冒充。','human','pending'),
 ('H02','选择有意义','至少5名玩过一章者能各自解释一次培养/放弃培养与换人/留队的具体原因；每角色至少一个实际可获得时点的独特收益场景，不要求各人同胜率。若只是多说对白或普通路线全方位替代，回调关卡与收益。','human_runtime','pending'),
 ('H03','经济和整局疲劳','至少5份完整周目观察，包含主线为主/支线积极/固定喜好队；记录每夜管理耗时、被迫恢复/等待、资源短缺、阅读与战斗时长；无因经济无法继续；若多数报告同一步骤反复无意义，修交互/节奏后复测。','human','pending'),
 ('H04','品质停止线','任何存档丢失、剧情根事实自相矛盾、无法操作/继续、错误永久离队均阻止发布；影响选择的数值/解释错也必须修。允许记录不影响结果的小视觉瑕疵，不用其掩盖玩法问题。','release_gate','pending')]
acceptance={'definition':'current_check表示本轮离线/静态验收目标，具体是否通过只认predevelopment-checks.json；pending全部尚未验收。',
 'criteria':[dict(id=i,area=a,pass_condition=p,method=m,status=s) for i,a,p,m,s in criteria],
 'gate_policy':{'development_ready':'D01–D06实际通过、无待用户决定的基础玩法矛盾、范围和接口明确；可以建议进入同一最终项目开发。','release_ready':'R01–R08、H01–H04全部有实际证据且阻断缺陷为0；本轮不能给出发布通过。','authorization':'本轮只审查；即使设计达到开工条件也不开始写正式运行代码。'},
 'coverage_limits':['不能穷举全部行动序列、所有记忆组合和全部玩家偏好。','统计是脚本策略结果，不是真人胜率、留存率、付费率或市场证明。','通过检查意味着已知范围可实施，不保证后续没有新bug。'],
 'existing_evidence':['0.17训练审查的868局/26364场属于明确输入的历史证据；本轮重新跑1174条规则回归和108局整局回归，另加版本/流程/L2检查。','旧33条Godot基础模块检查仅涵盖旧情绪与保存容器，不等于本版完整运行验收。'],
 'change_control':'后续发现会改玩法的矛盾，更新唯一baseline、测试期望和手册并记决策；显示/实现bug可直接修。新增系统须替换已有范围或重新评估成本，不静默扩张。'}
add('acceptance','acceptance',acceptance)
decisions=[
 ['旧资源/奖励和装备数量','60/8/2、主任务24/2/2、12装备与新经济并存','统一30/6/2与10/1/1、7/0/0、6/0/0；仅7装备；不重新提高自然成长成本。'],
 ['地图额外奖励','36图都写任意额外成果+物资','只按22条任务对象奖励表，不存在全图通用补贴；原例表和叙述一并改。'],
 ['已删除电池与屏障拾回','教程/两关仍建议电池；屏障拾回语义未实现','M02组件仅回收2零件，S11人工供电；屏障一次部署不拾回，任务后工具回仓。保留普通解法。'],
 ['关系多入口重复记账','旧共同贡献+4、旧压力和新评价+3并存','唯一评价入口；基础2，见证至多额外1，方向任务总计3；用现行事件强度表。'],
 ['冲突阈值','R和Q混写、满值隐藏负债风险','统一Q阈值与滞回，R<25平静；满值只压缩已分配权重，事实和责任保留。'],
 ['高级合作/现场服务数量','学习门槛/第三技能及12处值守残留','4情境合作无学习树；4现场操作，2限期修复；12处原设施记录只存事实。'],
 ['任务成败与人物反应','全员未安全撤出可能被写成目标失败','目标、队员、个人感受、承诺四种结果分别保存；对白引用准确维度。'],
 ['人物结局覆盖','后续冲突可覆盖整个好结局/职业','在场、职业、履约、方向关系正交；新背约不抹旧履约，重伤不等于恶意。'],
 ['L2配置和L5次数','文档只许营地改L2、探针用全队移动开关；旧适配器L5加次数','出发前按角色配置L2，任务内锁定；离线适配器按角色，L5只用各人明确升级。'],
 ['存档字段与异常路径','没有完整新局/错误读档/难度变更流程','固定槽位、原子写/备份、内容指纹、失败出口；课程数/AP转交标记纳入快照。'],
 ['96场景与短谈容量','全文已写仍标未完成，且可能误认为一周目全看','96全文有据；46晚间窗口不保证54段营地对话全发生；正文质量与演出仍待验收。'],
 ['开发通过和发行通过','离线推演容易被解读成所有玩法已证实','D/R/H三类标准，限定覆盖；当前不启动正式开发，不承诺未知实机/真人结果。']]
decisions.append(['跨进程贡献排序','S12运输贡献由集合顺序生成，导致六组回执首位贡献者不稳定','按真实有效动作/运输路径的首次出现顺序去重；不以列表首位推断责任、领导或剧情资格。加入不同hash seed复现检查。'])
add('decisions','predevelopment_decisions',{'resolved':[dict(id=f'C{i:02}',topic=a,conflict=b,resolution=c) for i,(a,b,c) in enumerate(decisions,1)],'user_decisions_required_now':[]})
ds['campaign']['contribution_order']='贡献名单按有效施工记录、消环后运输路径中首次真实贡献的顺序去重，稳定跨进程。primary_contributor只兼容旧展示，不能据此认定责任、指挥或人物履约资格，后者必须读取具体动作回执。'
ds['integration']['story_verifiers']['he']['all'][1]={'receipt':'objective_completed','contributors_include_actual_actor_other_than':'he'}
ds['integration']['story_verifiers']['he']['meaning']='同一主/支任务，其他正式成员至少有一次有效目标贡献，贺鸣实际保护/救援且全队撤出。允许他顺手协助，不能因先帮一次就判没有放手；排序字段不构成凭据。'
ds['decisions']['resolved'][-1]['resolution']+=' 贺鸣放手分支改验同任务他人的实际目标贡献、他的真实保护/救援、全队撤出；不再用名单首位判定，不因他帮一下就抹掉放手。'
ds['experience']['scope']='本版情境评价、引导与视觉规范；战斗读combat域，记忆读progression_relationship域，不再继承历史补丁。'
ds['compatibility_rules']=read(W/'compatibility-rules.json');views['game/data/rules.json']='compatibility_rules'
ds['mission_index']=read(D/'mission_registry.json');views['game/data/mission_registry.json']='mission_index'
mapping={'CORE-01':['D02','R02'],'CORE-02':['R01','R06'],'CORE-03':['R01'],'CORE-04':['D04','R02'],'CORE-05':['R03'],
 'REL-01':['D05'],'REL-02':['D05','R05'],'REL-03':['D05','R03'],'REL-04':['D05'],'REL-05':['D03','H02'],
 'CHAR-01':['R03','R05'],'CHAR-02':['D03','H02'],'CHAR-03':['D05','R05'],'CHAR-04':['R05','R08'],
 'ECO-01':['D04','R04'],'ECO-02':['D04','H03'],'ECO-03':['D02','R02'],'WORLD-01':['D02','R02'],'WORLD-02':['D02','R05'],
 'EVENT-01':['R05','R06'],'EVENT-02':['D05','R05'],'END-01':['D05','R05'],'REPLAY-01':['D02','H02'],
 'DIFF-01':['R03'],'UI-01':['R06','H01'],'UI-02':['R06','R08'],'SAVE-01':['R04'],'SAVE-02':['R04'],
 'TECH-01':['R01','R04'],'TECH-02':['D01'],'TECH-03':['R07'],'ASSET-01':['R08'],'AUDIO-01':['R08'],'QA-01':['H01','H02','H03','H04'],'SCOPE-01':['D06'],'SCOPE-02':['D06']}
req=read(D/'requirements.json')
for item in req:
 item['acceptance_ids']=mapping[item['id']];item['status']='design_defined_runtime_acceptance_pending'
 if item['id']=='SAVE-02':item['acceptance']='坏档和未知版本保留原文件并可回退备份/返回；首发不承诺兼容设计探针旧档。以后新增迁移要单独验收。'
ds['requirements']=req;views['game/data/requirements.json']='requirements'
for path,key in views.items():write(R/path,ds[key])
base['domains']=ds;write(F/'release_baseline.json',base);write(W/'views.json',views)
manifest={'version':V,'date':'2026-11-04','stage':'design_only','authority':'release_baseline.json','domains':{k:'release_baseline.json#/domains/'+k for k in ds},'precedence':'只有本baseline为当前规则；以下兼容文件是逐域导出视图，不单独编辑。旧版报告/补丁仅历史证据，不能覆盖本版。发现投影不一致视为构建失败，禁止按较大版本号猜测。','generated_views':views,'validation':'../../../outputs/predevelopment-checks.json','reader':'../../../outputs/full-game-design.html','historical_reports':'outputs下除当前手册、predevelopment审查及当前剧本阅读页以外的旧审查报告均为历史；新测试不改写旧报告。'}
write(F/'design_manifest.json',manifest)
# Mark non-authoritative old contracts without rewriting their historical evidence.
for p in F.glob('*.json'):
 if p.name in ['release_baseline.json','design_manifest.json'] or str(p.relative_to(R)) in views:continue
 x=read(p)
 if isinstance(x,dict):x['authority_status']='historical_evidence_only';x['current_authority']='design_manifest.json';write(p,x)
dev=read(R/'game/docs/development.json');dev.update(date='2026-11-04',design_version=V,project_stage='Design baseline frozen; formal development has NOT started.',design_authority='data/final_design/design_manifest.json',latest_review='../../outputs/predevelopment-review.html',formal_development_started=False,outstanding_user_preference=None)
dev['implemented']=['现有基础工程和旧版关系/存档准备模块；不视为0.18完整规则已接入。']
dev['design_complete']=['单一当前规则基线','36地图、8角色、96完整场景数据','完整流程、首发制作范围、D/R/H验收标准']
dev['not_implemented']=['0.18完整战役/战斗/成长/关系的Godot集成','正式UI、预览执行、剧情演出和完整保存恢复','最终美术音乐及授权核验','Windows性能兼容和真人试玩验收']
dev['commands']['design_validation']='python3 work/predevelopment-review/verify.py';write(R/'game/docs/development.json',dev)
(R/'game/README.txt').write_text('''夜潮事务所 — 0.18 开发前设计基线（2026-11-04）

本轮仍未进入正式开发。当前Godot工程只有基础准备模块，不是完整可玩游戏。
当前手册：../outputs/full-game-design.html
本轮审查：../outputs/predevelopment-review.html
唯一规则入口：data/final_design/design_manifest.json
唯一规则内容：data/final_design/release_baseline.json
领域JSON是生成投影，不可独立改成另一份规则。旧报告仅保留历史证据。

当前范围：俯视2D 8×8、3人2AP、8角色、24主线+12支线、16能力、7装备、4情境协作。
本地引擎：../work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot
Godot 4.7.2 standard / GDScript / Compatibility；首发Windows 11 x64键鼠简体中文。

设计回归：python3 work/predevelopment-review/regression.py （在工作区根目录）
整局回归：python3 work/ordinary-player-review/campaigns.py --output predevelopment-campaigns.json
本轮检查：python3 work/predevelopment-review/verify.py
当前阅读页生成：python3 work/predevelopment-review/build_report.py
旧work/*/apply_design.py、sync.py、rebuild.py均是旧版重建工具，不用于当前版本；运行会被投影/指纹检查发现。
正式程序与真人验收标准见data/final_design/acceptance.json，不用离线通过替代实机证据。
''')
print('Frozen',len(ds),'domains;',len(criteria),'acceptance criteria; no runtime edits')
