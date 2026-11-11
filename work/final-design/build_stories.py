"""Authored branching nodes with finite-state resolution and absent-role behaviour."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data';OUT=D/'final_design'
C={c['id']:c for c in json.loads((D/'characters.json').read_text())}
# Each line has a specific disclosure, a material policy decision, then a non-forced closure.
profiles={
'lin':dict(days=[2,9,16],peer='xu',proof={'mission':'M09','objective':'r1','kind':'saved'},opening=[
 '林岚把旧交班单压在杯子下面：“那天不是没人下过撤离令，是我直到最后才知道门已经关了。”',
 '新的病房转运排班又把她放在最后：“我可以留下。但这次，你要先告诉我谁来接，什么时候不再等。”',
 '她把诊所钥匙放在桌上：“我不需要你保证再也不会出事。我需要下一次不用一个人守到最后。”'],
 first=[('private','先让她决定交班单向谁公开','保留私人边界；目前不向许舟同步，后续可明确授权。'),('share','征得同意后安排双方核对','公开的是行动时间线，不要求她接受道歉；许舟知道她实际缺失的信息。')],
 commitment=[('rotation','制定轮换与明确接应','无资源费；下一次接应任务须把林岚以外的人设为救援执行者，且按已设期限撤离。'),('independent','给她保留独立处置权限','无资源费；可以继续独立工作；不发放双方修复凭据。')],
 verification='M09.r1被救出，且至少两个不同角色对其稳定/搬运/接应有贡献；其中一人不是lin。若任务已过去，用下一次含rescue的主任务实际达成同条件。不得回刷。',
 close=['重新建立有边界的信任','保留专业距离','战役结束后回到社区诊所'],line='林岚没有说“算了”。她重新填了一张所有人都能看见的交班单。'),
'xu':dict(days=[3,10,17],peer='lin',proof={'mission':'M12','objective':'drive','kind':'completed'},opening=[
 '许舟试着修旧接收器：“里面没有完整录音。缺的十七秒，我也补不出来。”',
 '他主动申请去最危险的一端：“这次让我证明。”队伍需要的是可靠行动，不是另一场偿还式冒险。',
 '撤离记录上第一次没有他擅自延长的时间：“按时回来，好像也算把事情做好。”'],
 first=[('record','如实登记缺失片段','记录证据边界，不替任何人补一句不存在的命令。'),('testimony','先分别保存当事人口述','口述标注未核实；对外不把它当技术证据。')],
 commitment=[('bounded','给任务范围与停止条件','无资源费；接受的撤离期限一旦接近，需放弃未承诺的额外目标或先得到改约同意。'),('solo','安排独立的基础岗位','无资源费；不强迫与林岚使用高级协议；他的贡献仍正常获得经验。')],
 verification='下一主任务有明确承诺截止轮；xu出勤且未失能，玩家在约定轮或之前发出撤离并且不触发违约。失败救援也可证明守约，成功却违约不可。',
 close=['以守约建立新的可靠性','做有边界的独立行动员','战役结束后去新的队伍'],line='旧接收器没有变成无罪证明。他留下的是下一次可以验证的约定。'),
'su':dict(days=[4,11,18],peer=None,proof={'mission':'M18','objective':'broadcast','kind':'completed'},opening=[
 '苏棠把三份同一时段的值班表翻给你看：“他们都说只是再帮一下。可这三下，是同一个晚上。”',
 '所有人都习惯在争执时叫她。“如果我今天不接，你会让谁接？”',
 '轮值表旁留出了一格休息：“我现在能听见电话响，也能等当班的人先接。”'],
 first=[('list','逐项核对她实际承担的工作','确认工作事实，不替任何人立刻认错。'),('listen','先听她说完再谈排班','她保留不公开私事的权利，工作统计仍能以后补。')],
 commitment=[('rota','建立额外调解轮值','无资源费；接下来两个值勤日不指定苏棠做后勤，并由其他可用者承担一次后勤。'),('specialist','保留她的专业调度但取消默认额外调解','无资源费；她可照常出勤，额外关系谈话不把她自动加入。')],
 verification='约定后的两个主任务均未把su放后勤，且至少一个其他主角有support_work receipt；即使其他任务失败也成立。无人可用则协议未履行，不能凭空成功。',
 close=['建立由多人承担的轮值制度','专注专业调度岗位','战役结束后休假再归队'],line='少接一个电话没有让她变得冷漠。她终于不必独自证明救援站还在工作。'),
'chen':dict(days=[5,12,19],peer='ye',proof={'mission':'M11','objective':'e','kind':'completed'},opening=[
 '陈砚指出验收附页上的一行字：“我写了要整改。”停顿之后，他承认自己仍然签了字。',
 '叶禾问：“修好这台机器，就能补上我家那几年吗？”工坊安静下来。',
 '旧铭牌拆下来了。陈砚这次没有把签名藏在技术说明后面。'],
 first=[('copy','保留完整附页及签名','保留条件与责任两部分，不剪掉有利或不利内容。'),('explain','先要求他逐条解释可验证的事实','没有证据的部分标为个人陈述，不当场定罪或免责。')],
 commitment=[('fund','公开说明签字责任并设维修补偿专项','支付8资金，一次性进入社区专项；未来成功完成一个work目标且陈砚有实际贡献，才算实质行动。'),('duty','严格执行新验收，不承诺当前付不起的补偿','无资源费；每次危险工作先完成断电/保护，未来仍可另议补偿；不送同等历史修复。')],
 verification='付清专项后，下一次主任务chen参与完成一个work目标；且公开说明获得Ye已知信息回执。叶禾缺席可收信确认，不要求她原谅。',
 close=['承担责任并参与长期补偿','保持严格履职与专业距离','战役结束后转幕后维修'],line='附页没有替他抹去签名，签名也没有抹去整改警告。两件事终于可以一起被记录。'),
'ye':dict(days=[8,14,21],peer='chen',proof={'mission':'M17','objective':'e','kind':'completed'},opening=[
 '叶禾带来的复印件已经折白了边：“我不是不愿意听解释，我不想再只拿到解释。”',
 '新的维护记录和旧文件有几处不同。她需要的是核对，不是被要求为了团队大局放下。',
 '她把新证据夹在旧纸后面：“这张纸说明了新的事，不会让以前的事没发生。”'],
 first=[('retain','把她的副本作为独立材料留存','不让陈砚改写她的记录；来历与未核实处清楚标记。'),('compare','征求同意后对照完整原件','只公开与事故有关的页；获得可核查清单。')],
 commitment=[('audit','用一次独立核查核对维护责任','无物资费，本节点占1项目；需要已获得E_MAINTENANCE；未取得时可登记等候，凭据到达后自动核查。'),('boundary','保留质疑并明确独立作业边界','无资源费；维持专业合作，不要求与陈砚装备危险联合协议。')],
 verification='E_MAINTENANCE实际取得，且ye已接收核查摘要。此动作只证明新事实已知；历史修复另需陈砚补救和后续安全合作，不由她单方面完成。',
 close=['继续追责，同时允许受约束的合作','承认专业能力但长期保持距离','战役结束后另组社区维修队'],line='她没有把复印件扔掉。工具箱里多了新的隔层，容得下不同年代的证据。'),
'he':dict(days=[11,16,20],peer='xu',proof={'mission':'M10','objective':'meeting','kind':'completed'},opening=[
 '贺鸣的名单上有一个名字一直没有划掉：“我下的撤退令。这个事实，不该因为大多数人活着就不提。”',
 '年轻人说想自己决定风险。他反问：“如果你回不来，谁替你收拾？”这次需要区分保护和代替决定。',
 '他站在出口旁，没有抢过别人的无线电：“位置我守着，下一步你自己报。”'],
 first=[('name','允许他保留失踪者的名字与不确定性','不擅自宣布死亡或写一个并无证据的团圆。'),('route','一起重看当时的撤退路线','区分当时信息与事后判断，避免全知式责怪。')],
 commitment=[('delegate','明确安全边界后把行动授权交给队员','无资源费；下一主任务he与另一人出勤，另一人完成目标，he不被安排替其完成全部目标。'),('discipline','维持统一撤离口令','无资源费；清楚告知出发前的限制，提供独立行动岗位，不承诺自由后再收回。')],
 verification='下一主任务he出勤并参与保护/救援，另一队员独立完成至少一个work或rescue里程碑且安全退出；无需指定许舟。',
 close=['成为能交出控制权的保障者','维持事先说明的严格纪律','战役结束后转向避难所'],line='他仍然会担心。不同的是，这份担心终于不再自动变成别人的命令。'),
'mo':dict(days=[14,18,23],peer='chen',proof={'mission':'M22','objective':'privacy','kind':'completed'},opening=[
 '莫遥拿出离线日志：“这段我亲眼看过。这段是别人转给我的。别把它们说成一样。”',
 '公开日志会带出一个与错误决策无关的同事姓名。隐去姓名，不等于隐去控制指令。',
 '对外的材料上保留了证据来源，也保留了核实范围：“我能保证的，就是这些。”'],
 first=[('classify','按亲历与转述分别登记','来源清楚；不把所有记录自动算作已核实证据。'),('verify','先核查技术签名再讨论公开','没有签名页就等待，不逼她捏造完整结论。')],
 commitment=[('redact','承诺只公开必要信息并脱敏','无资源费；下一次公开记录选择redacted，或完成M22.privacy；技术证据完整保留。'),('independent','将原件交独立核查机构，暂缓公开','无资源费；不立刻增加公开信任，也不阻断共同控制资格中的技术核实。')],
 verification='存在public_record_release receipt且privacy=redacted，或M22.privacy完成。公开未脱敏版本会永久使本次承诺失败；事后删帖不能伪造未发生。',
 close=['参与公开技术审计','留在有限互信的队伍','战役结束后离队并继续技术协助'],line='她没有交出每个人的全部生活。她交出的是足够承担责任的、能够核实的那部分。'),
'jiang':dict(days=[17,20,23],peer='su',proof={'mission':'S08','objective':'luggage','kind':'completed'},opening=[
 '江朔把拖欠清单和家人的旧短信放在一起：“我以前总觉得，再送完这一趟就来得及。”',
 '一艘船装不下所有物资。不能等船开了再告诉工人，他们的生活用品被当成最低优先级。',
 '这一次结算单送到了，消息也按时回了。他仍要决定之后把生活放在哪里。'],
 first=[('wages','先核对欠款与物资归属','没有授权不挪用工人工具，不用悲伤故事替代账本。'),('family','先让他处理家人的联系','不扣忠诚；生活选择不是对救援队的背叛。')],
 commitment=[('settle','结清一次明确拖欠并公示优先级','支付6资金给社区运输工人，获得收据；下一次cargo目标不以未告知改约方式挤掉已承诺人员。'),('negotiate','明确当前资金限制并重新约定','无资源费；工人同意后延期，不当作已经结清；保留独立合作关系。')],
 verification='实际支付6资金且获得工资收据；后续任务未发生与该事项同ID的priority_promise_breach。到第23日核对，不能用其他对象的付款顶替。',
 close=['经营共同所有的运输站','成为独立合作伙伴','战役结束后选择家人与另一座城'],line='不是每一笔遗憾都能结清。但这一次，他没有再拿下一趟航程代替答复。')}
N=[]
for actor,p in profiles.items():
 for stage in range(1,4):
  node=dict(id=f'P_{actor}_{stage}',actor=actor,stage=stage,title=C[actor]['arc'][stage-1],earliest_day=p['days'][stage-1],latest_day=23,requires_resolved=[] if stage==1 else [f'P_{actor}_{stage-1}'],opening=p['opening'][stage-1],project_cost=1 if stage==2 else 0,participants=[actor],required_peer=None,
   absent='暂时重伤：营地短谈/来信照常，不需战斗出勤；永久医疗离队：不再安排现场执行，已有选择转为书信结语且不补完成凭据。对方缺席仅用其已授权书面陈述，不替他发言。',
   defer='可推迟到第23日晚；不凭空扣好感。最终仍未读：用未解决/专业现状结语，不判作公开羞辱。',
   receipt_scope='node_id once; stable choice flag; loading and replaying UI never awards again')
  if stage==1:
   node['choices']=[dict(id=a,label=b,response=c,set_flags=[f'{actor}.disclosure.{a}'],credits=0) for a,b,c in p['first']]
  elif stage==2:
   node['choices']=[]
   for k,(a,b,c) in enumerate(p['commitment']):
    node['choices'].append(dict(id=a,label=b,response=c,credits=(8 if actor=='chen' else 6 if actor=='jiang' else 0) if k==0 else 0,set_flags=[f'{actor}.plan.{a}'],creates_contract=k==0,verification=p['verification'] if k==0 else 'explicit professional boundary; no restorative proof fabricated'))
   node['fallback_if_unaffordable']='第二项无资金成本且有完整职业/专业结局；不允许欠款或先领修复奖励再取消付款。'
  else:
   node['choices']=[dict(id='integrated',label=p['close'][0],requires=[f'{actor}.contract_verified'],response=p['line'],set_flags=[f'{actor}.ending.integrated']),dict(id='professional',label=p['close'][1],requires=[],response='双方明确保留边界；可以继续一起完成基础工作，不宣称旧事已经原谅。',set_flags=[f'{actor}.ending.professional']),dict(id='new_life',label=p['close'][2],requires=[],response='决定在本轮救援结束后执行；当前队伍仍可正常出勤，普通难度不会突然失去培养角色。',set_flags=[f'{actor}.ending.new_life'])]
   node['unmet_condition_dialogue']='如果尚未兑现约定，角色直接指出缺少的那件具体行动；可等到23日再谈，或选择专业距离/未来生活。不会展示虚假的已经和好台词。'
  node['after_choice_receipts']={'always':['story_choice(node_id,actor,choice_id)'], 'stage2':'create_contract(actor,choice_id,created_after_command_index) only for creates_contract; payments atomic; declaration and consent known_information emitted to actual participating/consenting roles', 'stage3':'store explicit ending preference; never set proof or revive actor'}
  if actor=='chen' and stage==2:node['after_choice_receipts']['fund']=['payment(purpose=chen_compensation,credits=8)','known_information(actor=ye,fact=chen_signed_responsibility) after written notice delivered; no forgiveness implied']
  if actor=='ye' and stage==2:node['after_choice_receipts']['audit']=['known_information(actor=ye,fact=maintenance_audit) only when E_MAINTENANCE is verified']
  if actor=='mo' and stage==2:node['after_choice_receipts']['redact']=['public_record_release(privacy=redacted) on next chosen public release; may be made from existing record after commitment, no resource reward']
  if actor=='jiang' and stage==2:node['after_choice_receipts']['settle']=['payment(purpose=jiang_wages,credits=6)']
  N.append(node)
# Twelve authored pair scenes: optional, do not invent 56 full romance routes.
pairs=[
 ('lin','xu',6,'最后的接应','林岚要求先说清谁留在出口。','写下撤离轮次','各自独立行动','dangerous_joint','independent_anchor'),
 ('chen','ye',9,'谁来碰开关','叶禾不愿在带电线路上只听一句相信我。','先断电再合作','分别处理不同装置','dangerous_joint','power_off'),
 ('xu','he',12,'口令之外','许舟要求把停止条件和自主范围一起说清。','预先划清授权','保持统一口令但分岗','partner_motion','explicit_authority'),
 ('su','jiang',17,'轮到谁留下','江朔发现额外搬运又默认交给苏棠协调。','另设轮值','减少承诺只做当班','handoff','named_receiver'),
 ('mo','chen',15,'签名与转述','陈砚追问哪些日志是亲眼见过的。','按来源逐条核实','先保存再等证据','information','source_labeled'),
 ('lin','su',3,'谁也不值最后一班','两个可靠的人都习惯把自己放到最后。','一起学习接力搬运','各自休息，日后再学','handoff','rest_boundary'),
 ('ye','mo',15,'复印件的背面','叶禾想公开名字，莫遥指出其中有无关人员。','保留责任事实并脱敏','暂缓公开交独立核查','information','redacted'),
 ('he','lin',12,'保护不是接管','贺鸣想替林岚决定谁先走。','由患者状态决定优先级','明确由当班医护判断','dangerous_joint','triage_order'),
 ('xu','jiang',18,'多带一箱','许舟提出多跑一次，江朔指向已承诺的发船时间。','先取得改约同意','放弃额外货物','handoff','deadline_confirmed'),
 ('su','mo',19,'没有接通的电话','苏棠担心未接通的呼叫，莫遥区分已确认与未知。','逐项登记而不编结果','先休息，次日核查','information','unknown_preserved'),
 ('chen','he',13,'修好以后谁负责','陈砚愿意修设备，贺鸣追问交接后的维护。','写入负责人和期限','只承诺本次修复','dangerous_joint','maintenance_owner'),
 ('ye','jiang',21,'箱子是谁的','工具既是救援设备也是工人的私人物品。','取得同意再借用','用公共基础工具替代','handoff','property_consent')]
R=[]
for k,(a,b,day,title,opening,opt1,opt2,tag,guard) in enumerate(pairs,1):
 R.append(dict(id=f'R{k:02}',actors=[a,b],earliest_day=day,latest_day=23,title=title,opening=opening,project_cost=0,
  choices=[{'id':'agreement','label':opt1,'effect':'记录双方已知的具体约定；后续真实履约才生成信任，不因选了这句话直接加数值。','guard':guard},{'id':'distance','label':opt2,'effect':'明确专业边界，不自动扣信任，也不伪造亲近。'}],
  relevant_tag=tag,absent='任一永久离队则不生成双人现场，写已发生事实的单人通信；没有对应事实不编修复。',
  scheduling='作为一次免费短谈；实际共同训练/治疗仍占原营地项目和资源；不得免费学协议。'))
# 24 local events are produced by actual mission records, rather than arbitrary mood randomness.
world=json.loads((D/'campaign_world_contract.json').read_text())
community=[]
for m in world['missions']:
 i=int(m['id'][1:]);community.append(dict(id=f'C{i:02}',source=m['id'],title=m['title']+'：回访',trigger='主线结算后一次',
  facts=m['carry_forward'],variants={'success':'呈现该关已完成的必要目标与具体获救名单；不自动宣称所有额外目标都完成。','partial':'同时列已做到与没做到的事项；回访者回应具体损失，避免一律斥责玩家。','failed':'说明地方后果与接下来的接管安排，不补发本关成果。'},
  choices=[{'id':'publish','label':'公开经核实的任务摘要','effect':'设置community_report.public=true；不包含私人信息；无金钱和好感奖励。'},{'id':'archive','label':'先留在内部交接记录','effect':'设置community_report.public=false；技术证据仍保留，不阻断世界路线。'}],
  project_cost=0,queue='任务结算页展示，不占夜间人物窗口',absent='由社区联络员传达，不要求特定主角'))
# Eighteen everyday recovery nodes, concrete scenes with bounded optional effects.
rest_specs=[
 ('lin','热汤','留一碗给夜班','自己先吃','care'),('xu','天气播报','听完模仿','请他关小声休息','humor'),('su','公用物品标签','一起贴标签','保留旧名字','humor'),('chen','漏汤的饭盒','帮他找密封圈','分享自己的盒饭','care'),('ye','亮色鞋带','问名字由来','一起修旧鞋','craft'),('he','练习的舞步','陪他练一段','替他录给家人','family'),('mo','旧广告牌','看看照片','讲讲街区过去','memory'),('jiang','船名争论','给新船起长名字','坚持短名字','humor'),
 ('lin','不完整的食谱','照记忆尝试','承认今天做不出来','craft'),('xu','咖啡口味','谢谢他记得','告诉他口味换了','care'),('su','屋顶电影','参加放映','安静休息','leisure'),('chen','小盆栽','挪到有光的地方','请别人代养','care'),('ye','修好的玩具','送还孩子','补写使用说明','craft'),('he','缝补痕迹','留着显眼的线','换成更结实的针脚','craft'),('mo','忘带的钥匙','帮她登记备用钥匙','先一起等值班人','humor'),('jiang','简单的甜点','分给轮班的人','留一份给家人','family'),('su','没安排的半小时','一起坐一会','让她独自待着','rest'),('lin','天气转晴','谈以后想做的事','先聊今晚吃什么','hope')]
rest=[]
for i,(actor,title,a,b,tag) in enumerate(rest_specs,1):
 rest.append(dict(id=f'L{i:02}',actor=actor,title=title,earliest_day=max(C[actor]['join']+1,2)+(1 if i>8 else 0),trigger='当事人在营地且本次未读；不在同晚紧接其严重冲突强插笑话',choices=[{'id':'a','label':a},{'id':'b','label':b}],effect='尊重选择的短谈给该角色对leader亲近+3，一次；不改变旧怨、专业信任、压力或AP。两项都是可接受回应。',project_cost=0,absence='永久离队改为来信近况，无亲近奖励；临时重伤仍可参与',category=tag))
# 18 chapter consequence beats, exact receipt selectors and non-exclusive loss reporting.
consequence_specs=[
 ('M03','货仓交接','crate','物资签收','补记未到物资'),('M04','桥下名单','worker','维修员回信','缺席席位'),('M06','第一轮潮后','r1','获救名单','继续寻找'),('M06','档案的去处','asset','修复档案','整理口述'),
 ('M08','运输恢复','truck','补给到站','调整配给'),('M09','屋顶之后','r2','病人转院','空出的病床'),('M10','预案演练','meeting','第二集合点','一条明确出口'),('M12','缺失的签名','e','原始签名','等待公共副本'),
 ('M14','药品之后','meds','移动诊疗','固定冷藏或损失'),('M15','三户人家','east','东楼回访','东楼缺席'),('M16','下船的人','people','居民安置','运输损失'),('M17','旧泵房的未来','repair2','继续排水','隔离或未完成'),
 ('M18','广播结束','broadcast','收到确认','无回应记录'),('M19','最后的病房','patient','稳定转运','长期接管'),('M20','避难所布局','east','东所保留','集中或损失'),('M21','去往码头','route','主路开放','应急接驳'),('M22','公开的范围','privacy','脱敏版本','等待处理'),('M23','重建的起点','rebuild','材料随船','轻装撤离')]
chap=[]
for i,(mid,title,obj,yes,no) in enumerate(consequence_specs,1):
 chap.append(dict(id=f'K{i:02}',source=mid,title=title,condition={'objective':obj,'state':'completed_or_saved'},true_text=yes,false_text=no,
 effect='只读取已经结算的地方事实；不再次发资源、不反向改角色记忆。',delivery='章末/终局摘要；多个片段按任务顺序组合，失去的居民不在后续背景中重新出现。'))
assert len(N)+len(R)+len(community)+len(rest)+len(chap)==96
save={'version':'0.4','personal_nodes':N,'relationship_nodes':R,'community_nodes':community,'recovery_nodes':rest,'chapter_nodes':chap,
 'profiles':profiles,
 'scheduler':{'camp_short_scenes':2,'priority':['用户主动打开已解锁人物节点','到第23日仍待处理的个人收束','兑现已触发冲突后果','关系短谈','生活场景'],
 'project_cost':'个人线第2段各占1项目；其他个人节点、关系短谈和生活短谈不占项目，但每晚至多2段。玩家可跳过对白读摘要并照常选择；所有已解锁未读内容在日志保留，到23日最后提醒。',
 'chapter_community':'在任务结算和章末摘要展示，不挤占营地短谈。每晚最多一次高强度冲突；后果先记账，延后的是长对白。',
 'unresolved':'未选/延期/条件未兑现均是合法状态。第23日晚先允许处理，确认进入第24日时再生成未解决状态，之后不返场刷条件。',
 'late_arc':'已到earliest且前节点已读，同晚第二窗口可读下一节点；3段至少占两晚。所有人物都有足够加入后窗口。',
 'guardrails':'免费短谈不提供训练/治疗效果；来自已读节点的亲近只发一次；资料核查、实际补救项目仍真实占用资源和时间。'},
 'ending_resolution':{'priority':['permanent_medical_withdrawal','later_unrepaired_relevant_breach_overrides_integrated','explicit_stage3_choice','verified_contract_without_stage3 -> professional_with_progress','unverified_or_unread -> professional_unresolved'],
 'career_change':'new_life只发生终战后的尾声；普通模式不会提前强制离队。',
 'loss_overlay':'已失去的居民、损坏设施、角色离队优先覆盖轻松对白；没有复活与自动遗忘。',
 'not_a_score':'不以善恶总分判定统一好结局；三类人物结局是合作方式/生活方向，世界成果独立计算。'}}
(OUT/'stories.json').write_text(json.dumps(save,ensure_ascii=False,indent=2)+'\n')
print('Authored 24 personal nodes, 12 pair scenes, 24 community nodes, 18 everyday scenes, 18 consequence nodes = 96.')
