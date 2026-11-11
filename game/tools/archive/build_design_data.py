raise SystemExit("Archived v0.2 authoring script: do not execute. Use current data and game/tools/build_product_document.py.")
"""Authoring source for the initial full-product design registry (not finished content)."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)

def write(name, value):
    (DATA / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

characters = [
 dict(id='lin', name='林岚', age=31, role='急救 / 稳定伤员', join=1, skills=[4,1,2,2],
      past='三年前撤离事故中导师没能出来。她知道许舟执行了提前封闸，但不知道指令被改写的全过程。',
      want='让一个人被放弃之前，至少有人认真解释过为什么。', flaw='把控制风险变成独自承担一切，不愿承认自己也需要帮助。',
      ordinary='收集旧食谱，给夜班的人留热汤；在安全时刻会说很冷的笑话。',
      trigger='被隐瞒风险、明确撤退承诺再次失效', sensitivity={'promise':1.25,'fairness':1.0,'humiliation':0.9},
      rupture='要求替代保护人或独立保护设备；拒绝的是危险联合动作，不停止全部救援。',
      arc=['未寄出的交班单','谁替谁签了字','把最后一班交给别人'],
      endings=['重新建立有边界的信任','维持专业合作','离开一线但留在社区诊所'],
      abilities=['稳定生命','移动急救','快速分诊']),
 dict(id='xu', name='许舟', age=29, role='机动 / 绳索救援', join=1, skills=[1,2,4,1],
      past='曾在错误与不完整指令中提前关闭闸门，救出一组人却切断了另一组的退路。他承担责任，也抗拒被简化为凶手。',
      want='用一次足够漂亮的成功证明自己仍值得托付。', flaw='急于证明价值，容易提出超过安全余量的承诺。',
      ordinary='修收音机，喜欢模仿天气播报；会偷偷记住每个人的咖啡口味。',
      trigger='当众将他定义为不可信、取消已约定的自主权', sensitivity={'promise':1.0,'fairness':0.9,'humiliation':1.25},
      rupture='要求明确的行动授权或换位；若被拒绝则执行基础任务，事后要求重新分工。',
      arc=['坏掉的接收器','没有录下来的十七秒','一次按时撤离'],
      endings=['以可靠而不是逞强定义自己','优秀的独立行动员','离开旧队伍重新开始'],
      abilities=['抛索','牵引位移','安全锚点']),
 dict(id='su', name='苏棠', age=28, role='沟通 / 调度', join=1, skills=[1,1,2,4],
      past='曾在大停电中连续值守，事后把每一个没有接通的呼叫都当成自己的失败。她没有万能的安慰能力。',
      want='建立不用靠某个人不断牺牲才能运作的救援站。', flaw='习惯替别人答应，压住不满直到精力耗尽。',
      ordinary='组织屋顶电影夜，给公用物件写夸张标签；有正常的朋友和生活期待。',
      trigger='未经同意替她承诺、长期把调解工作默认交给她', sensitivity={'promise':1.1,'fairness':1.25,'humiliation':0.8},
      rupture='暂停额外调解与支援值班，提出明确轮班条件；已承诺的当班支援照常完成。',
      arc=['无人接听','总有人说你最合适','不接这一次电话'],
      endings=['建立轮值制度','成为专业调度员','短暂离开后回归'],
      abilities=['标记威胁','现场协调','撤离呼叫']),
 dict(id='chen', name='陈砚', age=42, role='工程 / 控制装置', join=4, skills=[1,4,1,2],
      past='曾签署附带整改条件的设备验收，却未坚持停机。厂方忽略条件后的事故使叶禾的父亲失去劳动能力。',
      want='把仍能修好的东西修好，但不愿面对过去那份签字。', flaw='用技术解释替代承担责任。',
      ordinary='爱养小盆栽，认真研究哪种盒饭不会漏汤。',
      trigger='隐去技术警告、要求他再次签署不实保证', sensitivity={'promise':1.2,'fairness':1.0,'humiliation':1.0},
      rupture='拒绝签署危险方案，提出断电、加固或延期；不会随机拆坏设备。',
      arc=['验收附页','署名人的责任','亲手拆掉的铭牌'],
      endings=['公开承担并参与长期补偿','严格履职但关系疏远','退回幕后维修'],
      abilities=['断路','临时加固','重设控制器']),
 dict(id='ye', name='叶禾', age=24, role='工程 / 电力破拆', join=7, skills=[1,3,3,1],
      past='父亲在旧设备事故中受重伤，家庭几年都在赔偿与康复中度过。她记得陈砚的签字。',
      want='让技术记录不再成为推卸责任的纸。', flaw='容易把回避解释成再次掩盖，把所有妥协视作背叛。',
      ordinary='给工具取名字，喜欢亮色鞋带，会教孩子修玩具。',
      trigger='隐瞒事故证据、绕过必要保护后再谈大局', sensitivity={'promise':1.3,'fairness':1.2,'humiliation':1.0},
      rupture='公开质询并暂停与责任人的危险接线协作；独立破拆与基础行动仍可用。',
      arc=['工具箱里的复印件','修好机器不是赔偿','允许新的证据存在'],
      endings=['追责同时建立合作边界','长期保持距离但承认专业能力','另组社区维修队'],
      abilities=['电磁脉冲','绝缘通道','精准破拆']),
 dict(id='he', name='贺鸣', age=46, role='防护 / 搬运', join=10, skills=[2,2,1,3],
      past='曾因坚持撤离令与年轻队员分道扬镳；那次决定保住大多数人，却让一个没能及时到达的人失踪。',
      want='让年轻人活着拥有下一次选择。', flaw='保护欲有时剥夺别人的自主决定。',
      ordinary='认真练习女儿推荐的舞步，会把缝补的痕迹留得很漂亮。',
      trigger='把队员当可替换消耗品、把撤离预案当怯懦', sensitivity={'promise':1.2,'fairness':1.2,'humiliation':0.8},
      rupture='要求人员轮换或追加撤离保障；重度失信后提出下一班停止带队。',
      arc=['从未撤销的名单','保护与替人决定','把指挥权交出去'],
      endings=['成为可靠的保障者','维持严格纪律','转向避难所工作'],
      abilities=['架盾','安全搬运','掩护撤退']),
 dict(id='mo', name='莫遥', age=27, role='侦察 / 远程干扰', join=13, skills=[1,2,3,3],
      past='前巡检设备公司的外勤，发现固件警报被压下后保留了记录；她不是事故的全知揭密者。',
      want='纠正问题但不把仍在公司工作的同事一概当敌人。', flaw='依赖隐瞒来保护别人，削弱了队友对她的判断。',
      ordinary='喜欢给废弃广告牌拍照，方向感很好却经常忘记带钥匙。',
      trigger='逼迫公开无关人员隐私、未核实就定罪', sensitivity={'promise':1.2,'fairness':0.9,'humiliation':1.1},
      rupture='停止分享未经核实的私人线索，提出有限公开或第三方核查；任务情报不被暗扣。',
      arc=['离线日志','一个名字的代价','能够公开的部分'],
      endings=['成为公开审计者','留在有限互信的队伍','离开并持续提供技术帮助'],
      abilities=['扫描扇区','诱导信标','远程干扰']),
 dict(id='jiang', name='江朔', age=34, role='运输 / 社区交涉', join=16, skills=[2,1,3,3],
      past='经营小型水运合作社，曾为保住工资优先运货，错过与家人最后一次正式团聚；没有单一反派能解释这份遗憾。',
      want='让这次撤离之后社区还有重新生活的基础。', flaw='习惯把关系中的事情也算成交换。',
      ordinary='擅长做简单甜点，喜欢与人争论船名应该起几个字。',
      trigger='把普通劳动者利益视作随时可舍弃、答应后拒绝结算', sensitivity={'promise':1.1,'fairness':1.25,'humiliation':0.9},
      rupture='要求重新明确物资和人员优先级；不挟持伤员或偷走船只。',
      arc=['未结的工钱','最后一艘空船','留下来的理由'],
      endings=['经营共同所有的运输站','成为独立合作伙伴','选择家人与另一座城市'],
      abilities=['快速转运','应急补给','路线协调'])
]
write('characters.json', characters)

# All directions are explicit. These values are design inputs, not equilibria.
relations=[]
for a in characters:
    for b in [c['id'] for c in characters if c['id'] != a['id']] + ['leader']:
        relations.append(dict(id=a['id']+'>'+b, observer=a['id'], target=b,
                              grudge=0.0, trust=50.0, closeness=20.0,
                              grudge_categories=[], history='', active_memories=[]))
overrides={
 'lin>xu':(42,34,25,['promise'],'旧封闸事故：林岚认为许舟违背共同撤离承诺。'),
 'xu>lin':(12,70,45,['humiliation'],'许舟认可她的能力，也怨她将责任归于自己一人。'),
 'ye>chen':(55,32,5,['promise','fairness'],'父亲的设备事故与陈砚的签字。'),
 'chen>ye':(8,55,25,['humiliation'],'内疚与防御并存，不能简单反向复制怨恨。'),
 'su>xu':(10,45,50,['promise'],'几次由苏棠承担了许舟额外承诺的收尾。'),
 'xu>su':(0,65,60,[],'熟悉的老搭档。'),
 'he>xu':(25,40,30,['promise'],'对冒险倾向不放心。'),
 'xu>he':(28,60,20,['fairness'],'反感未经协商就被收回自主权。'),
 'mo>chen':(15,65,25,['promise'],'怀疑他仍选择用术语回避责任。'),
 'chen>mo':(5,60,30,['fairness'],'认可技术，但担忧未经核实公开记录。'),
 'jiang>su':(0,65,55,[],'曾得到公平调度。'),
 'su>jiang':(0,60,45,[],'认可兑现承诺的能力。')}
for r in relations:
 if r['id'] in overrides:
  g,t,c,cats,h=overrides[r['id']]
  r.update(grudge=g,trust=t,closeness=c,grudge_categories=cats,history=h)
write('initial_relationships.json',relations)

chapters=[
 ('断线之夜',['最后一班渡轮','诊所的备用电','被锁住的仓库','高架桥下','旧泵房来电','第一次涨潮'],['渡轮','诊所','仓库','桥梁','泵站','闸门']),
 ('一张旧名单',['工具箱的名字','断开的补给线','屋顶上的病房','撤离预案','需要签字的门','闸下的记录'],['工厂','仓库','住宅','桥梁','工厂','闸门']),
 ('水面以下',['会说谎的日志','冷库里的电池','三条同时响起的电话','没有空位的船','修复或拆除','广播塔的盲区'],['控制站','仓库','住宅','渡轮','泵站','广播塔']),
 ('天亮以前',['只剩一夜','两座避难所','旧路与新桥','最后一份记录','撤离顺序','天亮以前'],['诊所','避难所','桥梁','控制站','渡轮','主闸'])]
objective_types=['evacuate','restore_power','retrieve','escort','disable_control','hold_and_extract']
missions=[]
for ci,(chapter,titles,places) in enumerate(chapters):
 for si,(title,place) in enumerate(zip(titles,places)):
  n=ci*6+si+1
  missions.append(dict(id=f'M{n:02}',title=title,chapter=ci+1,day=n,kind='main',
    location=place,objective=objective_types[si],prerequisite_resolved=[] if n==1 else [f'M{n-1:02}'],
    recruits=[c['id'] for c in characters if c['join']==n and n!=1],
    failure_continues=True,optional_objective='保存物资、设备或额外居民；具体配置待关卡制作',
    baseline_fallback='基础队员动作 + 公开撤离路线，不要求特定主角专属技能',
    target_minutes=[20,25],status='outline_only'))
side_titles=['维修船票','旧书与药箱','电梯里的灯','屋顶菜园','剩余的绝缘布','一份未送达的饭',
             '失联的记录员','工人的行李','临时课堂','备用引航灯','留给诊所的电','不能沉下去的箱子']
for i,title in enumerate(side_titles):
 side_day=min(2*i+2,23)
 missions.append(dict(id=f'S{i+1:02}',title=title,chapter=i//3+1,day=side_day,kind='side',
  location=chapters[i//3][2][i%3],objective=objective_types[i%6],prerequisite_resolved=[f'M{side_day:02}'],
  recruits=[],failure_continues=True,optional_objective='另一个社区目标',
  baseline_fallback='可拒绝；不锁主线，不重复刷新',target_minutes=[15,20],status='outline_only'))
write('mission_registry.json',missions)

gear_specs=[
 ('winch','独立绞盘','越过指定垂直障碍、替代人工保护；不加全局信任','support',2),
 ('crowbar','破拆工具','拆除门与轻障碍；不能承担绳索保护','tool',1),
 ('medkit','急救包','额外稳定或恢复；每次消耗通用物资','support',1),
 ('shield','折叠盾','遮挡一条明确攻击线；占据地块','tool',2),
 ('foam','封堵泡沫','封堵一处漏水口，持续有限回合','consumable',1),
 ('insulation','绝缘垫','提供局部导电地形安全通路','support',1),
 ('battery','备用电池','向一台装置供电；与设施目标竞争','consumable',1),
 ('scanner','扫描仪','任务前显示一种隐藏布局条件；不揭露人物秘密','support',1),
 ('beacon','诱导信标','改变尚未锁定目标的巡检机选择，已预告攻击不暗改','consumable',1),
 ('cutter','切割器','拆除重障碍，产生公开噪声与回合成本','tool',2),
 ('stretcher','拖行担架','单人拖运稳定伤员，降低移动距离','support',2),
 ('extinguisher','灭火罐','清除局部火势并压低焊接设备输出一轮','consumable',1)]
write('equipment.json',[dict(id=i,name=n,effect=e,slot=s,weight=w,status='design_only') for i,n,e,s,w in gear_specs])
enemy_specs=[('scout','巡检机',3,'直线扫描后冲撞','诱导、推离攻击线'),('welder','焊接机',5,'前方扇形灼烧','断电、灭火、改变朝向'),
 ('hauler','搬运机',8,'沿固定轨道推动障碍','轨道改道、卡位'),('relay','中继机',4,'预告下一轮联动增援','优先关停、干扰'),
 ('skimmer','涉水机',4,'在相连水域释放电击','绝缘、断路、离水'),('sentinel','守闸机',10,'充能后攻击三格直线','掩体、断电、目标切换')]
write('enemies.json',[dict(id=i,name=n,hp=h,intent=t,counter=c,status='design_only') for i,n,h,t,c in enemy_specs])

req_specs=[
 ('CORE-01','完整战役状态流','新游戏→值勤计划→任务→结算→营地→下一日→结局','每种失败结果也有可达后继，不依赖成功才能推进'),
 ('CORE-02','任务与回合操作','3 人，8×8 为主的棋盘，每人每轮 2 AP','移动、基础攻击、稳定、搬运、互动、撤离都有明确合法性'),
 ('CORE-03','预告与结算','玩家阶段→锁定敌人动作→环境→目标检查→下一轮','预告使用与实际结算相同的数据；不暗改目标'),
 ('CORE-04','空间与资源','位置、视线、掩体、水、电、出口','移动寻路考虑实际地形代价；碰撞不重复结算'),
 ('CORE-05','撤退与伤势','任务失败或主动撤离→物资损失与伤势→恢复','不因一次漏看提示永久删除主角；出口与紧急撤离费用预告'),
 ('REL-01','有向旧怨','开局历史→旧怨锚点→同类事件非线性放大','相同刺激下有旧怨者增长更快；反方向不自动复制'),
 ('REL-02','事件归责','已知事件→责任份额→记忆与信任','责任份额≤1；未知、重复与无责事件不错误加怨'),
 ('REL-03','爆发闭环','平静→戒备→条件合作→冲突→协议/分开/补救','有上下阈值、情境门槛与冷却；绝不随机杀伤队友'),
 ('REL-04','修复与重复刺激','认责→实质补救→未来守约','道歉不能刷，低信任边界不能刷，旧怨不靠休息直接归零'),
 ('REL-05','正向关系','信任+训练→联合动作；亲近→人物交流与主动支持','至少四种通用合作协议；低亲近仍可专业合作'),
 ('CHAR-01','招募与缺席','8 人，3 人初始，5 人按章节加入','招募节点结算即加入或明确延期；重要能力有基础替代'),
 ('CHAR-02','成长','经验→等级 1–6→专长与配置','新招募有章节经验底线；不靠无限支线刷级'),
 ('CHAR-03','身体与情绪','HP/伤势/疲劳/压力→派遣限制与情绪展示','不让同一事件在多个状态上重复施加等价惩罚'),
 ('CHAR-04','人物内容','每人三段个人线，稳定人格与个人目标','缺席分支有补写或摘要；不要求每个人最终和好'),
 ('ECO-01','资源账本','资金/通用物资/零件→任务、恢复、升级→能力','无负库存、重复结算或买卖套利'),
 ('ECO-02','基地建设','4 个设施，各 2 次升级','升级改变可用办法；有限资源使单局存在投资取舍'),
 ('ECO-03','经济恢复','失败/缺粮→救济/支援工作/出售非必需品→继续行动','每章一次救济不能无限刷；没钱仍能执行基础动作'),
 ('WORLD-01','世界后果','任务结果→地区状态/社区信用→后续配置','失败改变代价而非直接把全部主线锁死'),
 ('WORLD-02','日程','24 个主线值勤日与有限可选任务','休息也推进日程；任务奖励只能结算一次'),
 ('EVENT-01','叙事调度','强制后果优先→条件过滤→可选权重','无匹配不强塞事件；固定种子和版本可重现'),
 ('EVENT-02','信息与秘密','世界真相、角色已知、玩家已知分层','不靠角色读心触发怨气；重要证据有多个可达来源'),
 ('END-01','结局','世界路线×社区结果×人物状态→结局片段','全难度可看完整结局；缺席角色也有结局回退'),
 ('REPLAY-01','第二轮','固定人物+可信开局变体+投入与任务变化','不重置人格，不强制刷周目看真结局'),
 ('DIFF-01','难度','从容/标准/严峻控制外部压力','关系人格和故事内容一致；组合约束经过验证'),
 ('UI-01','操作界面','任务简报/战术/队伍/关系/营地/结局','关键行动预览消耗、后果、责任与可撤销边界'),
 ('UI-02','可访问性','字号、字幕、色形双编码、速度、减少动态','1280×720 与 1920×1080 验收；不只靠颜色表达威胁'),
 ('SAVE-01','存档','槽位+版本+随机状态+命令记录','临时文件写入成功后换名；保留上一份完整存档'),
 ('SAVE-02','恢复与迁移','坏档/版本不符→报错/备份/迁移','失败加载不覆盖当前游戏；不静默丢失角色'),
 ('TECH-01','可复现规则','纯规则模块+数据表+表现层','同版本/种子/命令序列得到相同状态'),
 ('TECH-02','内容检查','稳定 ID、前置、引用、分支与缺席条件','构建时检查悬空引用、循环依赖、不可达主线'),
 ('TECH-03','性能与平台','Godot 4 标准版/2D/桌面客户端','目标 Windows；macOS 开发验证不冒充 Windows 实机通过'),
 ('ASSET-01','资产规范','角色头像/表情/棋子/地图/音效/字体','统一风格、透明边缘、命名、许可与替换尺寸'),
 ('AUDIO-01','声音反馈','环境/战术提示/情绪/音乐分轨','关键信息同时有视觉提示；音量独立设置'),
 ('QA-01','自动与人工验证','单元/整章回归/内容遍历/真人体验','规则通过不等于有趣；记录不同玩家的真实行为'),
 ('SCOPE-01','正式版范围','8 人/4 章/24 主线/12 支线候选/6 敌人原型','内容数量是生产预算，不是假装已经制作完成'),
 ('SCOPE-02','商业边界','完整买断；暂定国区 68 元/美区 14.99 美元','无付费抽卡或关系修复；发行另开对话')]
requirements=[dict(id=i,title=t,flow=f,acceptance=a,status='specified_not_implemented') for i,t,f,a in req_specs]
write('requirements.json',requirements)

product=dict(schema_version=1,design_version='0.2-full-product-preparation',title='夜潮事务所',title_status='working_title',
 genre='单机群像养成与回合制战术救援',world='架空近未来港城，洪灾使自治巡检与防护设备失去可靠指令，救援队需要穿越危险区域并处理旧事故留下的关系。',
 scope=dict(characters=8,chapters=4,main_missions=24,side_candidates=12,expected_side_per_run=6,
            story_event_budget=96,enemy_archetypes=6,equipment_archetypes=12,base_facilities=4,
            target_first_play_hours=[12,16],target_is_measured=False),
 price_proposal=dict(CNY=68,USD=14.99,original_short_version_CNY=[38,48],status='internal_proposal_not_store_price'),
 modes=['从容','标准','严峻'],death_policy='默认重伤与有预告的离队；永久死亡不是当前主线循环的随机结果。用户尚可调整。',
 start_resources=dict(credits=120,supplies=18,parts=4),daily_upkeep='2 + ceil(在站队员数 / 3) 通用物资',
 reward_design=dict(main_credits=[25,40],main_supplies=[3,5],main_parts=[1,2],partial_credits=12,
                    supply_purchase_credit_cost=4,support_supply_cap_per_day=1,emergency_relief_per_chapter=1),
 chapter_titles=[c[0] for c in chapters],
 non_goals=['实时 AI 对话','联网或服务器','3D 动作与动作捕捉','付费抽卡','全语音','开放世界','无限过程生成战役','首版创意工坊'],
 implementation_status='准备工程；内容与系统远未完成，不能作为可出售版本')
write('product.json',product)
print('Design registry:', len(characters),'characters,',len(relations),'directed relationships,',len(missions),'mission outlines,',len(requirements),'requirements')
