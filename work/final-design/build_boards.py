"""Explicit v0.4 encounter content, coordinates and state predicates."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data';OUT=D/'final_design'
registry={m['id']:m for m in json.loads((D/'mission_registry.json').read_text())}
# Distinct authored reusable location geometry; objectives/enemies/hazards are per encounter.
layouts={
 'ferry':['........','..##....','........','....XX..','....XX..','........','........','........'],
 'clinic':['...#....','...#....','........','.##..##.','........','...#....','........','........'],
 'warehouse':['.##..##.','........','..#..#..','........','.##..##.','........','........','........'],
 'bridge':['..X..X..','..X..X..','........','..X..X..','..X..X..','........','........','........'],
 'pump':['........','.##.....','....##..','........','.##..#..','........','........','........'],
 'gate':['..#..#..','........','..#..#..','........','..#..#..','........','........','........'],
 'factory':['........','.##...#.','........','...#....','.##.....','........','........','........'],
 'roof':['....X...','....X...','........','....X...','........','..##....','........','........'],
 'housing':['.##..##.','........','...#....','........','.##..##.','........','........','........'],
 'control':['........','..##....','........','....##..','........','..##....','........','........'],
 'shelter':['........','...##...','........','.##..##.','........','........','........','........'],
 'coldstore':['........','.##...#.','........','...##...','........','........','........','........']}

def task(i,label,pos,kind='work',work=2,pre=(),**kw):
 return dict(id=i,label=label,cell=list(pos),kind=kind,work=work,prerequisites=list(pre),hp=6 if kind!='rescue' else 4,**kw)
def work(i,label,x,y,n=2,pre=(),**kw):return task(i,label,(x,y),'work',n,pre,**kw)
def rescue(i,label,x,y,pre=(),**kw):return task(i,label,(x,y),'rescue',0,pre,initial_stable=False,**kw)
def cargo(i,label,x,y,pre=(),**kw):return task(i,label,(x,y),'cargo',0,pre,initial_stable=True,**kw)
def channel(i,label,x,y,pre=(),**kw):return task(i,label,(x,y),'channel',1,pre,hold_rounds=2,**kw)
B=[]
def board(mid,layout,objs,groups,enemies,limit,bonus,decision,consequence,wet=(),fire=(),rail=None):
 reg=registry[mid];rows=[list(r) for r in layouts[layout]]
 # Fixtures may be placed in open door recesses; record the authored opening, never erase X.
 for o in objs:
  x,y=o['cell'];assert rows[y][x]!='X',(mid,o['id']);rows[y][x]='.'
 for x,y in wet:
  if rows[y][x]=='.':rows[y][x]='~'
 units=[];controls=[]
 positions=[(7,2),(4,0),(7,4)]
 if len(enemies)>1 and enemies[1]=='skimmer':positions[0],positions[1]=positions[1],positions[0]
 for j,kind in enumerate(enemies):
  x,y=positions[j];rows[y][x]='~' if kind=='skimmer' else '.'
  uid=f'{mid}_enemy{j+1}';u=dict(id=uid,type=kind,cell=[x,y],facing='south',rail=rail if kind=='hauler' else None)
  if kind=='hauler':u['rail']=rail or [[7,2],[7,3],[7,4],[7,5]]
  units.append(u)
  if kind=='sentinel':
   for k,cell in enumerate([[5,3],[6,5]]):controls.append(task(f'{uid}_cut{k}',f'守闸机分路开关{k+1}',cell,work=1,disables=uid))
   u['disable_requires']=[f'{uid}_cut0',f'{uid}_cut1']
  else:
   cell=[[6,3],[4,2],[5,5]][j]; controls.append(task(f'{uid}_cut','就地停机/制动',cell,work=2,disables=uid));u['disable_requires']=[f'{uid}_cut']
 for c in controls:
  x,y=c['cell']
  if rows[y][x] in '#X':rows[y][x]='.'
 if 'skimmer' in enemies:
  for x,y in [(7,2),(7,3),(7,4),(7,5),(6,3),(6,4)]:
   if rows[y][x]=='.':rows[y][x]='~'
 # Alternative variant only changes two dry traversable cells into shallow water.
 occupied={tuple(o['cell']) for o in objs+controls}|{tuple(u['cell']) for u in units}
 variants=[p for p in [(1,3),(6,2),(3,4),(2,2),(5,1)] if tuple(p) not in occupied and rows[p[1]][p[0]]=='.'][:2]
 base=dict(id=mid,title=reg['title'],kind=reg['kind'],day=reg['day'],location=layout,rows=[''.join(r) for r in rows],spawns=[[1,7],[2,7],[3,7]],exits=[[0,7],[0,6]],backup_exit=[7,7],objectives=objs,mandatory_groups=groups,optional=bonus,controls=controls,enemies=units,round_limit=limit,
 environment={'water_addition':{'round':5,'cells':[[x,y] for x,y in variants]},'fire_pulse':{'round':7,'cells':[list(p) for p in fire],'damage':1},'briefing':'涨水只变成浅水，不把已知必经道路突然变成深水；火区在上一轮预告。失控机器电击按各自预告。'},
 variant={'A':'本表环境','B':{'water_round':6,'water_cells':list(reversed([list(p) for p in variants])),'fire_round':6 if fire else 7},'selection':'首玩A；重玩按种子选A/B；扫描仪允许出发前改选。顺序变化不改变人物历史或目标。'},
 reinforcement={'cap':0 if mid=='M01' else 2,'cells':[[7,0],[7,6]],'spawn_hp':3,'warning_rounds':1},
 decision=decision,consequence=consequence,
 failure_modifier={'next_main_only':True,'effect':'下一次主任务开局，一处标记为干地的非出口格变为碎石（代价2），由简报明确标出；最多一格，不修改敌人数量、目标或救援期限。','preferred_cells':[[1,5],[2,5],[3,5]],'expiry':'下一主任务结算后清除，不累积'},
 completion='达到 mandatory_groups 后仍可继续可选目标；玩家确认撤离或到时结算。所有组内 any_of，组间 all_of。',
 loss_receipts='每名居民/装置/货物用稳定ID单独记录 saved/completed/lost/unresolved；设施总分不覆盖这些事实。')
 B.append(base)
# Main encounter-specific atomic objectives, not recycled labels.
board('M01','ferry',[rescue('r1','前舱居民',2,2),rescue('r2','后舱居民',6,2),work('map','取线路图',6,0,1)],[['r1'],['r2']],['scout'],12,['map'],'先分头稳定两名居民，或三人集中关停巡检机后再搬运。伤员倒计时在第一次接触后启动；开局说明其仍有临时保护。','线路图保留为社区记录；未救居民写入损失。')
board('M02','clinic',[work('cut','切断错误回路',2,2),work('power','手摇恢复诊所电源',6,2,2,['cut']),cargo('spare','带回备用电池',6,0)],[['cut'],['power']],['scout'],12,['spare'],'断路后可以两次人工交互恢复，或花一份自带电池加速；现场电池带回与供电不可重复记账。','成功影响医疗区设施；现场电池作为bonus仅+1物资，不凭空给永久工具。',wet=[(3,2),(4,2)])
board('M03','warehouse',[work('door','打开货仓锁',3,2),cargo('crate','转运救援箱',6,2,['door']),work('parts','收集工具部件',6,0,1)],[['door'],['crate']],['welder'],13,['parts'],'先停焊接机更安全；撬棍缩短开门，但不用撬棍也能手动解锁。','工具解锁只看本关结算，额外部件+1零件。')
board('M04','bridge',[work('brace1','北桥加固',3,1),work('brace2','南桥加固',6,2),rescue('worker','接维修员离开',3,3,['brace1','brace2']),work('rail','固定临时护栏',6,0)],[['brace1'],['brace2'],['worker']],['scout'],15,['rail'],'先加固两点才可移动被困维修员；工人保护棚在加固前不计伤员倒计时。','桥区状态变化；陈砚在结算后派驻，与工人是否救回分开。')
board('M05','pump',[work('isolate','隔离失控泵',3,2),work('pump','启动排水',6,3,2,['isolate']),work('module','保存控制模块',6,0,1)],[['isolate'],['pump']],['skimmer'],13,['module'],'浅水捷径更近但受电击；绕干地关停涉水机后可稳定施工。','泵区成果与模块独立；失控机器破坏不等于目标泵破坏。',wet=[(3,3),(4,3),(5,3),(6,3),(7,3)])
board('M06','gate',[rescue('r1','接应老人',3,1),rescue('r2','接应儿童',6,2),cargo('asset','社区档案箱',6,0)],[['r1'],['r2']],['hauler','scout'],15,['asset'],'搬运机在右侧轨道巡行；取档案不能挤掉已承诺的人员撤离。','首章末保留救出名单，未来失败不抹去本次救援。')
board('M07','factory',[work('cut','切断作业电源',3,2),rescue('worker','接出维修员',6,2,['cut']),work('serial','抄录旧编号',6,0,1)],[['cut'],['worker']],['welder','scout'],14,['serial'],'记录编号不等于公开指控；有叶禾尚未入队，所以现场可先留存资料。','M07_serial供叶禾第一段说明，失败可读她带来的复印件；后者不补本关奖励。')
board('M08','warehouse',[work('block1','清除西障碍',3,2),work('block2','清除东障碍',6,2),task('truck','护送补给车',(3,4),'convoy',1,['block1','block2'],waypoints=[[3,4],[3,5],[2,5],[1,5],[0,5],[0,6]]),work('alt','标记备用线',6,0,1)],[['block1'],['block2'],['truck']],['hauler','scout'],16,['alt'],'清路后还需调度车辆，不是按两次开关自动完成；队员不能堵住车辆下一格。','工坊区恢复；备用线事实留到运输故事。')
board('M09','roof',[rescue('r1','转移呼吸机病人',2,2),rescue('r2','转移行动受限病人',6,2),cargo('med','便携医疗设备',6,0)],[['r1'],['r2']],['scout','welder'],15,['med'],'跨屋顶抛索只送自己；带伤员必须走连廊或先布绞盘。','救出病人与保住设备分别结算，不以设备未取到取消基本照护。')
board('M10','bridge',[work('test1','测试南向出口',3,2),work('test2','测试返向入口',6,2),work('meeting','标记第二集合点',6,0,1)],[['test1'],['test2']],['sentinel'],13,['meeting'],'双开关停守闸机比10HP硬拆更省行动；任意三人都能完成。','贺鸣按轮调加入；标记集合点为其第二段提供实证。')
board('M11','factory',[work('cut','切断工业门动力',3,2),work('lock','解除工业门',6,2,2,['cut']),work('e','保存维护记录',6,0,1)],[['cut'],['lock']],['welder','relay'],14,['e'],'拿到维护记录不会自动替陈砚免责；关门控制与敌人中继分别供电。','e完成生成E_MAINTENANCE及现场来源凭据。',fire=[(5,2),(6,2)])
board('M12','gate',[channel('backup','持续备份记录',3,2),cargo('drive','带出备份盘',3,2,['backup']),work('e','附带指令签名页',6,0,1)],[['backup'],['drive']],['sentinel','scout'],15,['e'],'备份要跨两次环境结算，不能靠高等级瞬间跳过；先关停攻击可保护终端。','e与drive都完成才得到E_ORDER；只拿到设备没有签名页不是完整证据。')
board('M13','control',[work('cut','隔离故障节点',3,2),work('log','日志安全下线',6,2,2,['cut']),work('e','保存报警覆盖记录',6,0,1)],[['cut'],['log']],['relay','skimmer'],14,['e'],'中继持续召来巡检机会吃掉取证时间；可取消增援或完成节点后撤出。','e完成生成E_WARNING；莫遥随后派驻，不要求她提前在场。',wet=[(7,2),(7,3),(6,3)])
board('M14','coldstore',[cargo('meds','转移冷库药品',2,2),work('cold','恢复冷库电源',6,2),work('ledger','留存药品交接表',6,0,1)],[['meds','cold']],['scout','welder'],12,['meds+cold','ledger'],'救走现有药品或让冷库继续运作，完成任一即主目标成功；两者都完成另有社区收益。','不会把两种合理方案都判成失败；额外兼顾只结算一次。')
board('M15','housing',[rescue('north','北楼求援',2,1),rescue('east','东楼求援',6,2),rescue('west','西楼求援',1,4)],[['north','east','west']],['scout','hauler'],12,['any_two','all_three'],'一次接一个呼叫承诺，未接受的求援也有损失但不自动归罪队友；承诺面板标明队伍能力。','分别记录三户的结果；只救一处仍完成明确的最低目标。')
board('M16','ferry',[work('lane','清运输通道',3,2),rescue('people','带居民登船',6,2,['lane']),cargo('goods','生活物资箱',6,0)],[['lane'],['people']],['hauler','relay'],15,['goods'],'先保证人的座位，再决定拿生活物资；财物不是阻断居民登船的钥匙。','江朔签订合作后加入；不增加每日口粮税。')
board('M17','pump',[work('repair1','修泵前断路',3,2,1),work('repair2','重建泵机控制',6,2,3,['repair1'],branch='repair'),work('isolate','封闭危险支路',2,4,2,branch='isolate'),work('e','取维护副本',6,0,1)],[['repair2','isolate']],['skimmer','sentinel'],15,['e'],'修复保住排水能力但位置更危险、工量更多；隔离较近但该地区上限本局降至2。第一次分支操作确认后互斥。','repair成功设施+1；isolate成功设施0且地区上限2，保障通行；两种均推进主线。e给E_MAINTENANCE。',wet=[(7,2),(6,3),(7,3)])
board('M18','control',[work('relay','解除广播干扰',3,2),channel('broadcast','持续发出通告',6,2,['relay']),work('backup','保存广播备份',6,0,1)],[['relay'],['broadcast']],['relay','welder'],15,['backup'],'护住广播终端两轮，派第三人处理机器；替代基础做法是先关敌再开台。','第20日公共通信恢复仍按外部抢修完成；本关成功提前改善地区，不垄断后续核查资格。')
board('M19','clinic',[rescue('patient','转移高危病人',2,2),work('shelter','加固临时集合点',6,2),cargo('device','医疗电源',6,0)],[['patient'],['shelter']],['skimmer','welder'],15,['device'],'同一小队拆分救人与加固；贺鸣的搬运优势不能代替另一端的施工。','最后风暴前清楚展示已保住与未保住的地区。',wet=[(6,3),(7,3),(7,2)])
board('M20','shelter',[work('west','西避难所防护',2,2),work('east','东避难所防护',6,2),rescue('transfer','转移两所之间伤员',3,4)],[['west','east']],['sentinel','relay'],13,['west+east','transfer'],'集中护住一所即成功；兼顾两所或转运伤员是额外任务，不临时改成功标准。','每所单独记成果，设施总分最多+1；第20日晚核查开放。')
board('M21','bridge',[work('route','恢复最终撤离线',3,2),work('e','旧闸指令副本',6,0,1),work('marker','给替代路径做标记',6,4,1)],[['route']],['hauler','sentinel'],14,['e','marker'],'修主路、核对档案和标记后备线竞争不同位置；任务失败仍有市级总撤离。','e给E_ORDER；marker仅改善撤离叙述，不暗藏必要路线资格。')
board('M22','control',[channel('handover','完成终端交接',3,2),work('e','核验最后报警记录',6,0,1),work('privacy','去除无关人员信息',6,4,1)],[['handover']],['relay','sentinel'],14,['e','privacy'],'完整记录可带回，但公开版本需要脱敏；不脱敏不会失去技术证据，只改变人物信任与公开后果。','e给E_WARNING；privacy对应莫遥第三段依据，公开前仍可在营地选择脱敏。')
board('M23','ferry',[rescue('r1','优先组登船',2,2),rescue('r2','第二组登船',6,2),cargo('rebuild','重建材料箱',6,0)],[['r1'],['r2']],['hauler','skimmer','scout'],16,['rebuild'],'最后一日可选任务与营地有明确提示；玩家知道继续拿材料会消耗多少回合。','重建材料增加结局资产事实，不提高被隐藏的真结局分数。',wet=[(7,2),(7,3),(6,3)])
board('M24','gate',[work('bus','切断错误总线',3,2),work('auth','交接公开权限',6,2,2,['bus'],route='shared_control'),work('west','隔离西支路',2,4,2,route='distributed_rebuild'),work('east','隔离东支路',6,4,2,route='distributed_rebuild'),rescue('r1','撤离末班居民',2,1,route='evacuation'),rescue('r2','撤离末班伤员',6,1,route='evacuation'),work('archive','保住已核实的现场备份',6,0,1)],[['bus'],['auth']],['sentinel','relay','skimmer'],17,['archive'],'进入前选路线；共同控制走bus+auth，分区重建走west+east，总撤离走r1+r2；三条路线不互相追加隐藏要求。','按已选目标实际结果收束；任何路线未达成仍写出撤离代价，不显示成功假动画。',wet=[(7,2),(7,3),(6,3)])
B[-1]['route_groups']={'shared_control':[['bus'],['auth']],'distributed_rebuild':[['west'],['east']],'evacuation':[['r1'],['r2']]}
# Sides each offer a distinct local outcome; no mandatory recruit or ending key.
sides=[
 ('S01','ferry',[work('engine','修好联络船',3,2),cargo('tickets','带回船票登记册',6,0)],[['engine']],['scout'],10,['tickets'],'船修好能恢复社区往来，登记册是额外的小故事。','社区联络船可用；bonus +1物资。'),
 ('S02','clinic',[cargo('med','药箱',2,2),cargo('books','旧书',6,2)],[['med','books']],['welder'],11,['both'],'药箱和书都值得带走；首箱即目标完成，第二箱增加生活成果。','记录药物/读书角分别是否保留；不把选择书籍写成道德失败。'),
 ('S03','warehouse',[work('cut','断开电梯驱动',3,2),rescue('passenger','接出电梯乘客',6,2,['cut'])],[['cut'],['passenger']],['scout'],12,[],'手动断电再开门；直接破门不可跳过驱动风险提示。','乘客可以在后续营地通信回信，没救回则没有那封信。'),
 ('S04','roof',[cargo('seed','菜园种箱',2,2),work('rack','固定灌溉架',6,2)],[['seed','rack']],['scout'],11,['both'],'搬走种子或留下可继续使用的菜园，目标不同但都合理。','结局生活片段引用种箱/菜园实际状态。'),
 ('S05','factory',[work('isolate','隔离配电柜',3,2),cargo('cloth','带回绝缘布',6,2,['isolate'])],[['isolate'],['cloth']],['skimmer'],12,[],'绝缘布是额外耗材来源，不是后续主线的唯一绝缘来源。','成功额外+2物资，最多一次。'),
 ('S06','housing',[work('locate','确认住户位置',3,2,1),rescue('resident','接出住户',6,2,['locate']),cargo('meal','送回保温盒',2,2)],[['locate'],['resident']],['scout'],12,['meal'],'确认位置后才知道人是否需要搬运，不能从标题推断只送外卖。','保温盒让苏棠的生活对话多一句回应，不强加好感。'),
 ('S07','control',[rescue('clerk','救出记录员',3,2),cargo('copy','独立备份',6,2)],[['clerk']],['relay'],12,['copy'],'救人是主目标，档案是额外；档案不另发必需证据ID。','保住口述记录，补充莫遥的知情边界。'),
 ('S08','warehouse',[cargo('luggage','工人行李',2,2),cargo('tools','工作工具箱',6,2)],[['luggage','tools']],['hauler'],12,['both'],'私人行李与未来谋生工具的取舍，不能都叫无价值财物。','江朔故事可引用实物归还收据，不靠对话刷责任。'),
 ('S09','housing',[work('class','加固临时教室',3,2),cargo('books','教学材料',6,2)],[['class']],['welder'],12,['books'],'加固以后仍可决定拿书，有限时间内先保人可接受。','社区儿童的后续生活不同；本关无人质死亡噱头。'),
 ('S10','gate',[work('light','修复备用引航灯',3,2),work('chart','校验航线',6,2)],[['light']],['sentinel'],12,['chart'],'双开关关守闸机或绕路施工；校验航线是额外。','撤离尾声增加清楚的指引事实，不把此支线设成总撤离门槛。'),
 ('S11','clinic',[work('wire','诊所后备供电',3,2),work('cold','保留药柜冷藏',6,2)],[['wire']],['skimmer'],12,['cold'],'没有购买电池也可以两次手摇交互；带电池更快。','诊所重建片段；与医疗设施升级不同，不扣免费基础照护。'),
 ('S12','bridge',[cargo('box','社区名册箱',3,2),cargo('photo','家庭照片箱',6,2)],[['box']],['scout'],12,['photo'],'最后一天告知完成后仍有一次营地，明天终战；可跳过，不隐藏真结局。','名单/照片分别进入尾声；原有已救居民记录不会因箱子未拿而抹掉。')]
for row in sides:board(*row)
# Uniform bonus accounting avoids different phrases being interpreted as duplicate rewards.
for b in B:
 for o in b['objectives']:
  o['sustain_until_exit'] = o['id'] in {'M02':['power'],'M04':['brace1','brace2','rail'],'M05':['pump'],'M14':['cold'],'M17':['repair2'],'M19':['shelter'],'M20':['west','east'],'S01':['engine'],'S04':['rack'],'S09':['class'],'S10':['light'],'S11':['wire','cold']}.get(b['id'],[])
  o['secured_rule'] = 'completed and hp>0 at settlement' if o['sustain_until_exit'] else 'completed milestone receipt; rescue/cargo requires delivered, channel requires full hold, convoy requires final waypoint'
 b['optional_reward_rule']='每关完成任意一个额外目标，额外+1物资；M03额外改为+1零件；S05成功额外+2物资。其余额外目标只增加明确的地方事实，不反复发钱。'
 if b['id']=='M02':
  next(o for o in b['objectives'] if o['id']=='spare')['use_instead_of_deliver']={'target':'power','work':2,'ap':1,'requires_carried':True,'prerequisites':['cut'],'consumes_self':True,'blocks_optional_delivery':True}
 for o in b['objectives']:
  if o['kind']=='rescue':o['stabilize_deadline']={'mode':'none' if b['id']=='M01' else ('prerequisite_round_plus_2' if o['prerequisites'] else 'fixed_round'),'round':None if b['id']=='M01' or o['prerequisites'] else 6}
 b['civilian_timer']='普通伤员在第6轮末前需要稳定，简报即显示；存在前置的伤员由临时保护支撑到前置完成，期限为前置完成轮+2轮末。稳定后不再失血倒计时，但仍会受现场攻击。M01教学关只受整关时限。倒计时不由走近或重复点击重置。'
 b['objective_dependencies']='fixtures prerequisites refer to objective.completed, never unit presence. An unavailable specialty never changes the graph.'
 b['fallback_loadout']='3名10HP、2AP、移动3、搬运2的通用队员；无专长、无装备、无合作协议。'
 b['no_goal_collision']='同格backup/drive分阶段出现；fixture不阻塞行走。多个目标同格只能在各自前置成立时交互，UI列出对象。'
 if b['id']=='M12':b['evidence_receipt']={'id':'E_ORDER','requires':['e','drive']}
 elif b['id'] in ['M11','M17']:b['evidence_receipt']={'id':'E_MAINTENANCE','requires':['e']}
 elif b['id'] in ['M13','M22']:b['evidence_receipt']={'id':'E_WARNING','requires':['e']}
 elif b['id']=='M21':b['evidence_receipt']={'id':'E_ORDER','requires':['e']}
 else:b['evidence_receipt']=None
(OUT/'boards.json').write_text(json.dumps({'version':'0.4','boards':B},ensure_ascii=False,indent=2)+'\n')
print(f'Authored {len(B)} encounters with coordinates, mandatory groups, controls, variants and consequences.')
