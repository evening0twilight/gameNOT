"""Every authored specialty/tool/protocol gets an executable controlled fixture.
These test actions and alternatives, NOT the accessibility of fixture positions in a campaign.
"""
from pathlib import Path
from copy import deepcopy
import json
from actions import Lab, ABILITIES, EQUIPMENT
from encounter import HP
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data/final_design';O=ROOT/'outputs'
BASE=json.loads((D/'boards.json').read_text())['boards'][0]
checks=[];coverage=[]
def check(name,ok):assert ok,name;checks.append(name)
def fixture(key=None):
 b=deepcopy(BASE);b.update(rows=['........']*8,spawns=[[2,4],[3,4],[1,4]],exits=[[0,4]],backup_exit=[2,5],enemies=[],controls=[],objectives=[dict(id='task',kind='work',cell=[2,3],work=4,hp=6,prerequisites=[],interaction_tags=['engineering','heavy_obstacle','light_obstacle','power_socket'],power_off=True),dict(id='r1',kind='rescue',cell=[2,3],work=0,hp=4,prerequisites=[],initial_stable=False,stabilize_deadline={'mode':'none'}),dict(id='r2',kind='rescue',cell=[3,4],work=0,hp=4,prerequisites=[],initial_stable=False,stabilize_deadline={'mode':'none'})])
 l=Lab(b,['task'],style='attack');l.gear.update(med_dose=2,battery_stock=1,foam_stock=1,beacon_stock=1,extinguisher_stock=1)
 l.e['unit']=dict(id='unit',type='scout',p=(2,2),hp=3,disabled=False,disable_requires=[],skip=0,intent=[],step=(0,1),rail=None)
 if key in ABILITIES:l.h[0]['name']=ABILITIES[key]['actor'];l.h[0]['abilities']=[key]
 elif key:l.h[0]['tools']=[key]
 return l
def reject(l,fn,name):
 before=deepcopy(l.__dict__)
 try:fn();bad=False
 except AssertionError:bad=True
 check(name,bad and before==l.__dict__)
def result(key,description,l):coverage.append(dict(id=key,scope='controlled_fixture',meaning=description,ap=l.ap_used,log=l.log))

for key in ABILITIES:
 l=fixture(key);target=None;dest=None;description=''
 if key=='lin_1':target='r1';description='1AP在两格范围稳定，独立基础办法需走近后稳定'
 elif key=='lin_3':target='r1';dest=(2,3);l.objects['r1']['p']=(2,2);description='移动1格并稳定，1AP；基础移动＋稳定2AP'
 elif key=='lin_5':target=['r1','r2'];description='1AP稳定两个不同对象，基础需要2AP'
 elif key=='xu_1':dest=(4,4);l.rows[4][3]='X';l.h[1]['p']=(3,5);description='1AP跨单格障碍；可沿已有普通道路绕行'
 elif key=='xu_3':target=1;l.h[1]['p']=(4,4);dest=(3,4);description='转移一格位置，付的是许舟AP，受拉者保留AP'
 elif key=='xu_5':dest=(2,3);description='锚点提供明确的携带跨越例外，不是全体免费移动'
 elif key=='su_1':target='unit';description='分担前排攻击AP；标记后下一击3，合计不声称比连续两次基础攻击总伤更高'
 elif key=='su_3':target=1;description='给队友移动预算+1，不增AP，多个来源取最大'
 elif key=='su_5':dest=(2,5);description='打开地图既定第二出口，改变搬运返程'
 elif key in ['chen_1','ye_1']:target='unit';l.e['unit']['p']=(2,3);description='本轮停止威胁，目标下个整轮免疫临时控制'
 elif key=='chen_3':target='task';description='给存活设备3保护，不能复原已毁设备'
 elif key=='chen_5':target='task';l.objects['task']['work']=2;description='断电后的两工量工程1AP完成；不能加速取证'
 elif key=='ye_3':dest=(2,2);description='铺两格绝缘，挡电不挡火，不改变深水通行'
 elif key=='ye_5':target='task';description='2工量静音拆障，与切割器的噪音风险不同'
 elif key=='he_1':dest=(2,3);description='临时屏障截断射线，替代绕开或停机'
 elif key=='he_3':description='搬运预算3，释放担架的支援装备槽'
 elif key=='he_5':target=[1,2];description='两名队友各挡一次机器2伤害，不能挡电火'
 elif key=='mo_1':target='task';l.control_ids.add('task');l.objects['task'].update(work=2,disables='unit');description='4格内直接给停机开关1工量；不生成资料或额外AP'
 elif key=='mo_3':target='unit';dest=(2,5);description='只改变下轮选敌，当前预告不追踪改写'
 elif key=='mo_5':target='unit';l.e['unit']['type']='relay';l.pending=[dict(source='unit',p=(7,0),due=2,delayed=False)];description='取消未生成波次，不删除已生成敌人'
 elif key=='jiang_1':target=1;l.h[0]['carry']='r1';l.objects['r1']['carrier']=0;l.objects['r1']['stable']=True;description='1AP交接，接收者0AP，不能直接记已救出'
 elif key=='jiang_3':target=1;l.h[1]['hp']=5;description='用已打包药剂远程补给，无免费库存；医疗实例不要求医疗包占槽'
 elif key=='jiang_5':dest=(2,3);l.rows[3][2]=':';description='长期去除一格碎石，单次经过不一定赚AP，适合反复转运'
 l.use(0,key,target,dest)
 check(key+' executes without AP minting',0<=l.h[0]['ap']<=2)
 if key.startswith('lin_'):check(key+' really stabilizes',l.objects['r1']['stable'])
 elif key=='xu_1':check('rope reached declared dry landing',l.h[0]['p']==(4,4))
 elif key=='xu_3':check('pull preserves recipient AP',l.h[1]['p']==(3,4) and l.h[1]['ap']==2)
 elif key=='xu_5':check('anchor actually exists',(2,3) in l.anchors)
 elif key=='su_1':check('mark actually exists','unit' in l.marks)
 elif key=='su_3':check('coordination changes move budget',l.budget(l.h[1])==4)
 elif key=='su_5':check('alternate exit added',(2,5) in l.exits)
 elif key in ['chen_1','ye_1']:check(key+' stops current intent',not l.working(l.e['unit']))
 elif key=='chen_3':check('reinforcement really adds3 protection',l.objects['task']['shield']==3)
 elif key=='chen_5':check('reset completes engineering target',l.objects['task']['done'])
 elif key=='ye_3':check('two insulation cells exist',len(l.insulated)==2)
 elif key=='ye_5':check('demolition contributes2 work',l.objects['task']['progress']==2)
 elif key=='he_1':check('temporary barrier has3HP',l.barriers[(2,3)]['hp']==3)
 elif key=='he_3':l.h[0]['carry']='r1';check('safe carrying budget3',l.budget(l.h[0])==3)
 elif key=='he_5':check('two distinct shields applied',l.h[1]['shield']==l.h[2]['shield']==2)
 elif key=='mo_1':check('remote shutdown actual work is real',l.objects['task']['progress']==1 and not l.objects['task']['done'])
 elif key=='mo_3':check('decoy waits until next round',l.decoys['unit']['from_round']==2)
 elif key=='mo_5':check('pending wave canceled',not l.pending)
 elif key=='jiang_1':check('transfer neither doubles nor delivers casualty',l.h[0]['carry'] is None and l.h[1]['carry']=='r1' and not l.objects['r1']['secured'])
 elif key=='jiang_3':check('supply heals and consumes actual dose',l.h[1]['hp']==8 and l.used['med_dose']==1)
 elif key=='jiang_5':check('route rubble actually removed',l.rows[3][2]=='.')
 result(key,description,l)

for key in EQUIPMENT:
 l=fixture(key);target=None;dest=None
 if key in ['crowbar','cutter','battery']:target='task'
 elif key=='medkit':target=1;l.h[1]['hp']=5
 elif key in ['winch','shield','insulation']:dest=(2,3)
 elif key=='foam':l.b['environment']['water_addition']['source']['cell']=[2,3];dest=(2,3)
 elif key=='scanner':target='task';l.control_ids.add('task');l.objects['task']['disables']='unit';l.e['unit']['disable_requires']=['task']
 elif key=='beacon':dest=(2,5)
 elif key=='extinguisher':dest=(2,3);l.fire={(2,3),(3,3)}
 l.use(0,key,target,dest);check(key+' has executable use',l.ap_used>=0)
 if key in ['crowbar','cutter','battery']:check(key+' adds work',l.objects['task']['progress']==2)
 if key=='stretcher':l.h[0]['carry']='r1';check('stretcher carrying3',l.budget(l.h[0])==3)
 if key=='foam':check('foam spans three environment resolutions',l.foam_until==3)
 if key=='scanner':check('probe provides real shutdown work',l.objects['task']['progress']==1 and l.ap_used==1)
 if key=='extinguisher':check('extinguisher clears existing area',not l.fire)
 if key=='medkit':check('medkit requires and consumes dose',l.h[1]['hp']==8 and l.spent_supplies==1)
 result(key,'受控动作效果；全关装备对比另见战术矩阵',l)

for key in ['relay_carry','protected_work','mutual_cover','coordinated_pull']:
 l=fixture();l.h[0]['protocols']=l.h[1]['protocols']=[key]
 target='task'
 if key=='relay_carry':l.h[0]['carry']='r1';l.objects['r1']['carrier']=0;l.objects['r1']['stable']=True
 if key=='coordinated_pull':target='unit';l.e['unit']['type']='hauler';l.e['unit']['p']=(2,3);l.h[1]['p']=(3,3)
 before=deepcopy(l);reject(l,lambda:l.protocol(key,0,1,target,blocked=True),key+' refusal leaves all AP and objects unchanged')
 if key in ['protected_work','mutual_cover']:l.prepare_safety(2,0,1,key)
 else:l.agree(key,0,1)
 l.protocol(key,0,1,target,blocked=True,safeguard=True)
 check(key+' charges both actors',l.h[0]['ap']==l.h[1]['ap']==1)
 if key=='protected_work':check('protected work3 does not stack L2 bonus',l.objects['task']['progress']==3 and l.h[0]['first_work'])
 if key=='relay_carry':check('relay moves actual recipient while preserving cargo identity',l.h[1]['p']!=(3,4) and l.objects['r1']['carrier']==1)
 if key=='mutual_cover':check('cover blocks only one machine hit',l.h[0]['shield']==l.h[1]['shield']==2)
 if key=='coordinated_pull':check('heavy unit actually moves',l.e['unit']['p']!=(2,3))
 reject(l,lambda:l.protocol(key,0,1,target),key+' cannot repeat same pair in same round')
 result(key,'关系拒绝→提供保障→真实行动；基础办法仍独立存在',l)

l=fixture('xu_1');l.h[0]['abilities']=['xu_1','xu_5'];l.h[0]['carry']='r1';l.objects['r1']['carrier']=0;l.objects['r1']['stable']=True;l.h[1]['p']=(3,5);l.rows[4][3]='X'
reject(l,lambda:l.use(0,'xu_1',destination=(4,4)),'carrying rope needs deployed anchor')
l.h[0]['carry']=None;l.objects['r1']['carrier']=None;l.use(0,'xu_5',destination=(2,3));l.execute_task(l.h[0],dict(target='r1',route=[l.h[0]['p']],action='pickup'));l.rnd=2;l.h[0]['ap']=2;l.use(0,'xu_1',destination=(4,4));check('anchor exception makes carrying rope legal',l.h[0]['p']==(4,4) and l.h[0]['carry']=='r1')
l=fixture('chen_1');l.use(0,'chen_1','unit');l.h[0]['ap']=2;l.rnd=2
reject(l,lambda:l.use(0,'chen_1','unit'),'same machine cannot be stunlocked next round');l.rnd=3;l.use(0,'chen_1','unit');check('control returns at D+2 rounds',not l.working(l.e['unit']))
l=fixture('chen_5');l.objects['task']['work']=2;l.objects['task']['interaction_tags']=['record']
reject(l,lambda:l.use(0,'chen_5','task'),'controller reset cannot fabricate evidence')
l=fixture('jiang_1');l.h[0]['carry']='r1';l.objects['r1']['carrier']=0;l.objects['r1']['stable']=True
reject(l,lambda:l.use(0,'jiang_1',1,blocked=True),'handoff specialty respects the same relationship boundary as protocol')
l=fixture('he_5');l.use(0,'he_5',[1,2]);l.hit_hero(l.h[1],2,'beam');l.hit_hero(l.h[1],2,'beam')
check('cover is consumed once, not permanent invulnerability',l.h[1]['hp']==8)
l=fixture('ye_3');l.use(0,'ye_3',destination=(2,2));l.h[1]['p']=(2,3);l.hit_hero(l.h[1],2,'water',electric=True);l.hit_hero(l.h[1],1,'fire')
check('insulation blocks electricity but not fire',l.h[1]['hp']==9)
l=fixture('shield');l.e['unit'].update(type='sentinel',hp=10,p=(2,1));l.use(0,'shield',destination=(2,3));l.rnd=2;l.publish();l.environment()
check('shield really intercepts beam before actor',l.h[0]['hp']==10 and l.barriers[(2,3)]['hp']==1)
l=fixture();l.e['unit']['p']=(2,1);l.publish();locked=list(l.e['unit']['intent']);l.h[0]['p']=(4,4);l.environment()
check('scout follows locked footprint after player moves',l.e['unit']['intent']==locked and l.e['unit']['p'][0]==2)
l=fixture();l.e['unit'].update(type='welder',hp=5);l.publish();check('welder odd round has no attack',not l.e['unit']['intent']);direction=l.e['unit']['step'];l.h[0]['p']=(6,2);l.rnd=2;l.publish()
check('welder retains charged facing next round',l.e['unit']['step']==direction and bool(l.e['unit']['intent']))
l=fixture();l.e['unit'].update(type='hauler',hp=8,rail=[[2,2],[2,3],[2,4],[2,5]],rail_index=0,rail_direction=1);l.publish();l.environment()
check('hauler pushes actual actor and stops at two rail steps',l.e['unit']['p']==(2,4) and l.h[0]['p']==(2,5) and l.h[0]['hp']==8)
l=fixture();l.b['reinforcement']['cap']=2;l.e['unit'].update(type='relay',hp=4);l.rnd=3;l.publish();check('relay warns before spawning',len(l.pending)==1 and l.spawned==0);l.environment();l.rnd=4;l.publish();l.environment()
check('relay new unit has no unannounced same-round attack',l.spawned==1 and not l.e['reinforcement_1']['intent'])
l=fixture();l.e['unit'].update(type='skimmer',hp=4);l.rows[2][2]=l.rows[3][2]=l.rows[4][2]='~';l.rnd=2;l.publish();l.environment()
check('skimmer connected component damages actor once',l.h[0]['hp']==8)
for mode in ['standard','hard']:
 l=fixture();l.difficulty=mode;l.h[1]['p']=(1,4);l.hit_hero(l.h[1],11,'fixture');o=l.objects['downed_1']
 l.execute_task(l.h[0],dict(target='downed_1',route=[l.h[0]['p']],action='stabilize'));l.execute_task(l.h[0],dict(target='downed_1',route=[l.h[0]['p']],action='pickup'))
 check(mode+' downed hero stabilization grants only one extra round',l.h[1]['deadline']==4)
 if mode=='standard':
  l.rnd=2;l.h[0]['ap']=2;l.move(l.h[0],[(2,4),(1,4),(0,4)]);l.complete(o);l.spend(l.h[0],'extract',target='downed_1');l.h[0]['carry']=None;o['carrier']=None
  check('real transport retrieves injured hero without reviving',l.h[1]['left'] and l.h[1]['down'] and l.h[1]['rescued'])
 else:
  l.rnd=4;l.environment();check('hard expiry while carried clears cargo and withdraws casualty',l.h[0]['carry'] is None and l.h[1]['permanent'] and o['lost'])
l=fixture('su_3');l.gear['he_3']=1;l.h[1]['carry']='r1';l.use(0,'su_3',1)
check('movement support cannot stack carrying above3',l.budget(l.h[1])==3)
l=fixture();l.objects['task']['opportunity_deadline']=1;l.rnd=1;l.environment()
reject(l,lambda:l.complete(l.objects['task']),'expired optional target cannot be revived by completion receipt')
l=fixture();l.h[0]['protocols']=l.h[1]['protocols']=['protected_work']
reject(l,lambda:l.protocol('protected_work',0,1,'task',blocked=True,safeguard=True),'a bare safeguard flag never overrides refusal')
l.prepare_safety(2,0,1,'protected_work');l.h[2]['p']=(0,0)
reject(l,lambda:l.protocol('protected_work',0,1,'task',blocked=True),'protector moving away invalidates condition')
l.trust[(0,1)]=59
reject(l,lambda:l.protocol('protected_work',0,1,'task'),'learned protocol unavailable below actual mutual trust threshold')
l=fixture();l.e['unit'].update(type='hauler',hp=8,p=(2,3));l.basic_push(0,'unit');check('heavy basic push needs second AP',l.e['unit']['p']==(2,3));l.basic_push(0,'unit');check('two paid same-direction pushes move heavy enemy',l.e['unit']['p']==(2,2) and l.h[0]['ap']==0)
l=fixture();l.e['unit'].update(type='hauler',hp=8,p=(2,3));l.basic_push(0,'unit');l.rnd=2;l.h[0]['ap']=2;l.basic_push(0,'unit');check('heavy push progress does not survive round end',l.e['unit']['p']==(2,3))
for mode in ['standard','hard']:
 l=fixture();l.difficulty=mode;l.complete(l.objects['task']);l.hit_hero(l.h[1],11,'fixture');l.emergency_retreat()
 check(mode+' retreat preserves completed goal and basic continuation',l.objects['task']['secured'] and l.ended and not l.h[0]['permanent'] and l.h[1]['permanent']==(mode=='hard'))
check('all24specialties12equipment4protocols covered',len(coverage)==40 and len({x['id'] for x in coverage})==40)
out={'scope':'Isolated legal-state fixtures; not proof of reaching every fixture during a whole mission. Offline design scripts only.','passed_count':len(checks),'checks':checks,'coverage':coverage}
(O/'tactical-mechanic-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Mechanic fixture checks:',len(checks),'coverage:',len(coverage))
