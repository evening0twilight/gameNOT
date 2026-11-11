"""Authoring source for v0.4 implementable design; not the game runtime."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'game/data/final_design'
def save(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
combat={
 'version':'0.4','coordinates':'Zero-based [x,y], top-left origin. Orthogonal movement and Manhattan ranges. Board glyphs: .=dry, ~=water cost2, :=rubble cost2, #=wall, X=deep water impassable. Exits and objects are separate overlays.',
 'turn_order':['start_round: reset 2 AP per active hero and once-per-round markers','publish enemy intents and environmental footprints','player interleaves all three heroes; no real-time clock','resolve surviving enabled enemies by stable unit ID','apply announced environmental damage once per cell and source','advance active objective work and evacuation deadline counters','check mission success, retreat and time limit; otherwise next round'],
 'information':'All tactical units, hazards, objectives, deadlines and costs visible at deployment. No surprise enemy attack, fog-of-war miss chance or critical hits. Future scheduled hazard footprints at least one round ahead.',
 'stats':{'hero_hp':10,'ap':2,'move_budget':3,'carrying_move_budget':2,'attack_damage':2,'push_collision_damage':1,'civilian_hp':4,'object_hp':6},
 'geometry':{'range':'Manhattan unless an explicit straight line is required','line_of_sight':'Same row/column; walls and intact shields block, occupants do not. Range excludes source includes target. Ability specifying no LOS ignores this check.','movement':'Weighted shortest paths; no diagonal; may pass through standing allies but not finish on one; no pass through enemies, walls or deep water. Carrying actors cannot use rope jumps.','occupancy':'A tile holds at most one standing actor plus one downed actor/civilian/object overlay. Stationary machines occupy their tile; interactable fixtures do not. Civilians await pickup and never autonomously enter danger.','push':'Adjacent target, one cardinal tile directly away; no chain push. Blocked destination deals 1 collision damage to pushed enemy only. Cannot push allies/civilians into hazards or deep water. Enemies cannot push units into X; blocked push deals 1 instead.'},
 'actions':[
  {'id':'move','ap':1,'effect':'Move along legal path up to 3 terrain cost, or 2 while carrying; unused movement expires. Zero-length movement invalid.'},
  {'id':'attack','ap':1,'effect':'Adjacent machine takes 2 damage. No attack against people. No kill XP, loot or action refund.'},
  {'id':'push','ap':1,'effect':'Push adjacent machine one tile; heavy hauler/sentinel require two consecutive push progress on the same round, reset at round end. Progress shown.'},
  {'id':'stabilize','ap':1,'effect':'Adjacent unstable casualty becomes stable. For a hero: once per downing extends rescue deadline by 1 round; never restores AP/HP in this mission. Stabilizing the same state again is illegal.'},
  {'id':'pickup','ap':1,'effect':'Pick up one adjacent stable casualty/cargo, remove its board overlay and attach to carrier. Carrier capacity 1; cannot attack, push or use active specialties until put down; can interact/extract.'},
  {'id':'drop','ap':0,'effect':'Place carried target in own or adjacent legal unoccupied overlay tile. Does not trigger cooperation, training, trust, objective or recovery rewards.'},
  {'id':'interact','ap':1,'effect':'At Manhattan <=1 of a fixture add 1 work, subject to declared prerequisites. A two-work fixture can be worked by two actors same round. Completed fixtures cannot be farmed.'},
  {'id':'extract','ap':1,'effect':'On an exit, offload cargo/casualty permanently to safety; actor stays. For actor withdrawal use leave_site below.'},
  {'id':'leave_site','ap':1,'effect':'At exit, withdraw self and carried target; no return this mission. Mission settles when last active hero leaves or player confirms extraction after goals met.'},
  {'id':'wait','ap':0,'effect':'End selected hero actions; can undo before end_round. No free time ticks.'},
  {'id':'emergency_retreat','ap':0,'effect':'Team command available any player phase, explicit confirmation. End mission; retain completed objective receipts, lose unfinished bonuses; ordinary modes all stranded heroes recover injured; hard mode stranded downed heroes permanently withdraw. Standing heroes reach emergency transport and receive recoverable injury if not already at exit. No cash fee.'}
 ],
 'objective_machine':{'work':'Atomic increments 0..required_work; prerequisites all_of validated before each increment. No work decay unless explicitly timed channel.','rescue':'stable->carried->delivered_at_exit. Only delivery completes. Civilian killed/deadline missed is irreversible lost, no replay by heal.','channel':'Interact starts active timer; at environment step advance by 1 only if fixture alive and power condition true. Interrupt pauses; destroyed becomes failed.','convoy':'Interact after blockers complete dispatches; at each environment step move one waypoint if next cell free; blocked waits, does not teleport or attack; reaches final waypoint -> delivered.','choice':'Exclusive branch committed at first branch-specific action after confirmation; common preparation persists. M14/M20 explicitly nonexclusive.','outcome':'success if every mandatory group satisfied (each group any_of its alternatives); partial if any mandatory atomic milestone completed without all groups; failed otherwise. Optional steps never upgrade failed to partial. A destroyed/lost target cannot become completed. Complete mandatory groups does not force end before player resolves optional tasks or exits; task clock still runs.','deadline':'Player phase of round limit is available; settle after that round environment. Fulfilled objective receipts remain; no recovery of destroyed items via summary.'},
 'intent':{'creation':'At round start each enemy chooses a cardinal axis toward nearest active hero (distance, hero ID tie), locks origin/footprint/route; if no target use listed patrol direction. Player sees exact footprint and order.','locked':'Hero movement never retargets locked attack. Pushing enemy translates locked footprint by its displacement, retaining orientation; preview recomputes immediately. Destroy/disable cancels. Telegraphed paths obstructed at resolution stop at first blocker.','activation':'Spawn warns one round in advance; new unit appears end-round, first intent next round. No more than board reinforcement budget.','preview':'Preview and commit read same state revision; reject stale commands without AP spend. No hidden random reroll. Confirm irreversible conflict/loss only once per command.'},
 'damage':{'resolution':'For each source apply max(0,raw-cover-shield); same water connected-component attack hits each occupant once, not per wet cell. No friendly fire from hero abilities.','hazards':'Fire 1 and live water 2; where both coincide use max 2 environmental damage, not sum. Water alone costs movement but no damage. Shield blocks machine ray; does not block electricity or fire. Insulation blocks water electricity only.','downing':'At HP<=0 set downed, AP0, release held cargo on tile; no same-mission revival. Rescue deadline=end of current round+2, stabilization once adds1. Downed units cannot be damaged to reset timer.','deadline_expiry':'Remove casualty from tactical board via secondary rescue. Ordinary modes recoverable injury; hard mode long-term hospital withdrawal. Explain the difference as severity/prolonged exposure, not random refusal of rescue.','end_mission':'Non-downed heroes reset HP next deployment. Downed heroes obey camp injury recovery. Goal loss does not automatically down everyone.'},
 'difficulty':{'relaxed':{'deadline_bonus':3,'enemy_damage_delta':-1,'min_enemy_damage':1,'hero_loss':'injury'},'standard':{'deadline_bonus':0,'enemy_damage_delta':0,'hero_loss':'injury'},'hard':{'deadline_bonus':-1,'enemy_damage_delta':0,'hero_loss':'withdrawal_if_not_retrieved'}},
 'difficulty_constraints':'Enemy HP/AI and personality unchanged across modes. Hard does not add hidden enemies or multiply all economy penalties. All maps have at least two rounds of basic-action logistics slack before hard modifier; finite enemy control is separately checked in playtests.',
 'objective_persistence':'work/channel/convoy nodes marked sustain_until_exit must still have HP>0 when the team leaves or time expires. Their earlier completion remains a milestone for partial outcome, but not a secured success. Cargo/rescue delivered and copied evidence receipts persist. Destroyed objectives cannot be healed back into completion. Carrying protects the carried target from duplicate area damage; if the carrier goes down it drops, and subsequent sources can hit it.',
 'archetype_planning_overrides':{'welder_and_sentinel':'奇数轮锁定朝向并展示蓄能，下一偶数轮保持该朝向攻击，不重新追踪；推移只平移攻击原点。下个奇数轮才重新选朝向。','hauler':'按本关有序轨道前进，到末端后下一轮反向；每轮最多2格。前方机器/不可移动装置阻挡则停止；人员按推移规则处理；屏障承受2伤害但本轮仍阻停。','skimmer':'奇数轮从当前及相邻合法浅水格中选择离最近站立角色曼哈顿距离最小的格，平局按y再x；被占用不可选。偶数轮不移动，预告当前连通浅水区域；断电/地形变化后预览同步重算，执行只使用确认后的同一状态。','relay':'按地图reinforcement.cells顺序选择第一个无站立单位的出生格，先预告再生成；两格均不可用时按既定延迟规则取消，绝不临时另找未预告的格。'},
 'enemy_targeting':'Only standing heroes determine facing; greatest absolute axis offset wins, horizontal on ties, hero stable ID for equal distance. Charged lines stop at walls/shields. Enemy attacks affect each standing/downed person and fragile fixture in the declared footprint once; objective damage is collateral, never hidden retargeting.',
 'save_and_undo':'Manual save at stable player phases and camp; persist board, locked intent, cooldowns, objective flags and seeded variant. Undo before committing an informational reveal or irreversible objective; opening menu never rerolls. Autosave pre-deployment, each round start and before terminal settlement.'}
combat['actions'][0]['effect']='花1AP沿合法路线移动，空手最多3点地形代价，搬运时2点；不能原地空移动。'
combat['actions'][1]['effect']='攻击相邻机器，固定2伤害；不能攻击人，没有击杀经验、掉落或返还AP。'
combat['actions'][2]['effect']='将相邻机器推开1格；搬运机/守闸机需同轮累计两次推移工量；受阻仅机器承受1碰撞伤害。'
combat['actions'][3]['effect']='稳定相邻伤员；失能队员的救援期限只可延长1轮，不恢复本关生命或AP，不能重复刷。'
combat['actions'][4]['effect']='拾起一个相邻且稳定的伤员/货物；每人最多携带1个。携带时不能攻击、推移或使用专长，可交互和撤离。'
combat['actions'][5]['effect']='将携带物放在自己或邻接合法格；不触发贡献、经验、信任或恢复奖励。'
combat['actions'][6]['effect']='距离装置不超过1格，检查前置后增加1工量；两人可以同轮接力施工；完成后不能重复操作。'
combat['actions'][7]['effect']='在出口卸下携带目标，记为永久送达；操作者仍留场。'
combat['actions'][8]['effect']='在出口撤出自己及所携带目标，本关不再返回；最后一位撤出后结算。'
combat['actions'][9]['effect']='结束当前队员安排，回合结束前可恢复操作；不推进世界时间。'
combat['actions'][10]['effect']='任何玩家阶段可发出全队紧急撤退；需确认具体后果。保留已完成成果，普通模式遗留者重伤；严峻模式遗留的失能者永久医疗离队。站立者到达紧急接驳，但未到出口者计可恢复重伤；无金钱门槛。'
save('combat.json',combat)
enemies=[
 ('scout',3,2,'charge','Every round: declare up to 3 straight path cells, advance in order then hit first blocking actor for2; stop before actor. A wall stops without attack. Can be disabled by adjacent universal interact requiring2 work.','mobile'),
 ('welder',5,2,'fan','Odd rounds charge, even rounds hit 3-cell fan one tile ahead (forward and two forward diagonals). No movement. Turn toward nearest hero only at next intent creation. Local cutoff fixture disables permanently.','fixed'),
 ('hauler',8,2,'rail','Advance up to2 along authored rail waypoints, push first blocking actor1 and damage2; if push blocked stop. Cannot leave track; local brake fixture2 work disables.','rail'),
 ('relay',4,0,'spawn','On rounds3 and6 warn listed spawn tile; spawn scout next round end if tile empty; otherwise defer1 round then cancel. Maximum2 spawns shared with board budget. Local cutoff2 work disables future calls, not existing scouts.','fixed'),
 ('skimmer',4,2,'water','Odd rounds relocate at most1 on connected shallow water; even rounds electrify its current connected water component with2 damage. Cannot cross dry. Local breaker fixture2 work permanently disables.','water'),
 ('sentinel',10,3,'beam','Odd rounds charge, even rounds hit next3 cells in facing line for3. No movement, line blocked by walls/shields. Two distributed cutoffs with1 work each disable; universal attacks can also destroy.','fixed')]
enemy_rules={
'scout':'每轮预告最多3格直线冲撞路径；沿线前进，遇第一名角色在其前停下并造成2伤害，墙会直接阻停。也可用就地停机开关完成2工量永久关闭。',
'welder':'奇数轮蓄能、偶数轮灼烧前方3格扇形（正前与两侧前斜格），伤害2；不移动，下轮生成预告时才转向。就地断路2工量可永久关闭。',
'hauler':'沿本关轨道最多前进2格，遇人推1格并伤害2；推不动则停止，不能离开轨道。制动开关2工量可关闭。',
'relay':'第3/6轮预告出生格，下一轮末出现巡检机；占位则延后1轮仍占则取消。全关共享最多2次增援额度。关停只阻止未来增援，不删除已登场单位。',
'skimmer':'奇数轮在连通浅水内移动最多1格，偶数轮对当前连通水域放电2伤害；离开水域或断电可规避，每名受影响者只结算一次。',
'sentinel':'奇数轮蓄能、偶数轮对朝向前3格直线攻击3伤害；不移动，墙和屏障截断射线。两个分路开关各1工量能永久关闭，或通过基础攻击拆除。'}
save('enemies.json',[dict(id=i,hp=hp,damage=d,kind=k,rule=enemy_rules[i],mobility=m,defeat_reward=0) for i,hp,d,k,r,m in enemies])
# Abilities are optional accelerators; universal objective actions remain complete.
A=[]
def ability(actor,level,name,ap,charges,rng,effect,tags=()):A.append(dict(id=f'{actor}_{level}',actor=actor,level=level,name=name,ap=ap,charges_per_mission=charges,range=rng,effect=effect,tags=list(tags)))
ability('lin',1,'稳定生命',1,2,2,'稳定一名伤员，可隔一个空格；不回血复活。')
ability('lin',3,'移动急救',1,2,2,'走最多2点地形代价后稳定相邻一名伤员；整项消耗1 AP；路径必须合法。')
ability('lin',5,'快速分诊',1,1,1,'稳定自身周围至多两名不同伤员；同一人不能叠加延长期限。')
ability('xu',1,'抛索',1,2,3,'自身沿直线跨过最多1格X/墙到空的干地；不携带伤员，不穿过连续两障碍；落点须可见。')
ability('xu',3,'牵引位移',1,2,2,'将一名自愿站立队友沿直线拉近1格安全空地；对同一目标每轮一次。',['partner_motion'])
ability('xu',5,'安全锚点',1,1,1,'邻格设置锚点持续本任务；与其邻接的抛索行动可携带稳定伤员，移动仍花AP；提供独立保护条件。')
ability('su',1,'标记威胁',1,2,4,'标记一机器到下轮开始；下一次基础攻击对它+1伤害，消费标记；不叠加。')
ability('su',3,'现场协调',1,2,3,'一名自愿队友获得本轮下一次移动预算+1；不增加AP，不与其他移动加成叠加。',['partner_motion'])
ability('su',5,'撤离呼叫',1,1,3,'在指定的备用登陆点打开第二出口，必须是地图已列出且可达的干地；不能任意生成出口。')
ability('chen',1,'断路',1,2,2,'关闭一机器本轮已预告动作；下轮重启；同机器最多每两轮一次，不修改其他机器。')
ability('chen',3,'临时加固',1,2,1,'一个任务装置获得3点护盾，持续本任务；同目标只一次，不恢复已毁装置。')
ability('chen',5,'重设控制器',1,1,1,'对断电后的任一2工量设备直接完成剩余工作；不能跳过前置、计时备份、搬运或取证。')
ability('ye',1,'电磁脉冲',1,2,1,'相邻单机失能本轮；与陈砚断路共用该目标两轮控制间隔。')
ability('ye',3,'绝缘通道',1,1,2,'沿直线铺两格绝缘地，持续本任务；不改变深水可通行性。')
ability('ye',5,'精准破拆',1,2,1,'完成轻/重障碍的2点拆除工量；不作用于活机器、资料或不可破墙。')
ability('he',1,'架盾',1,2,1,'邻格放置3HP屏障到下轮开始；阻挡机器射线，友军可穿过但不落脚；每次最多一块。')
ability('he',3,'安全搬运',0,0,0,'被动：携带时移动预算3，仍花1 AP；不与担架或移动协议叠加。')
ability('he',5,'掩护撤退',1,1,2,'范围内两名不同队友各获得一次机器伤害-2护盾，至下轮开始；不防水火，不叠加。')
ability('mo',1,'扫描扇区',1,2,4,'标记一个机器，让下一次相邻通用关停交互增加2工量；不能用于任务目标或伤害。')
ability('mo',3,'诱导信标',1,2,3,'指定空干地作为一台巡检机下一轮选敌目标；本轮锁定动作不变，届时预告完整显示。')
ability('mo',5,'远程干扰',1,1,4,'取消一台中继机尚未生成的下一批增援；不删除已登场单位，无法无限拖延刷奖励。')
ability('jiang',1,'快速转运',1,2,1,'把自己所携带目标交给相邻空手自愿队友；接收者不花AP；不能额外结算救出。',['handoff'])
ability('jiang',3,'应急补给',1,1,1,'自身或相邻队友从本队已携带耗材中使用一份并完成该物品效果；只付这一AP，不生成免费库存。')
ability('jiang',5,'路线协调',1,1,2,'指定一格碎石本任务移动代价变1；不能用于水、火、深水或墙。')
save('abilities.json',A)
E=[]
def equip(i,day,price,parts,slot,ap,rng,uses,effect,recipe=0):E.append(dict(id=i,unlocked_after_main=day,price_credits=price,price_parts=parts,slot=slot,action_ap=ap,range=rng,uses_per_mission=uses,effect=effect,consumable_supply_cost=recipe))
equip('crowbar',0,0,0,'tool',1,1,None,'邻接轻障碍/门增加2工量；基础交互是1。开局共有一件；不是人物专属。')
equip('medkit',0,0,0,'support',1,1,2,'站立队友回复3HP，不能复活；每用一次消耗已打包的一份医疗耗材。开局共有一件空包。',1)
equip('winch',3,20,2,'support',2,1,1,'部署独立锚点；相邻人员每次花1 AP可沿直线跨过单格X并携带伤员，终点必须干地。代替危险绳索协作，不提升信任。')
equip('shield',4,18,1,'tool',1,1,1,'放置4HP屏障，持续本任务，友军可穿过不可落脚；拾回1 AP，不能拾回补HP。')
equip('foam',5,0,0,'consumable',1,2,None,'封住一个已列出的漏口，阻止其后续水位扩张3轮，不清除已有水；消耗一份。',1)
equip('insulation',7,20,2,'support',1,1,1,'铺一格绝缘垫持续本任务；不能在深水铺，绝缘只免电伤。')
equip('battery',1,0,0,'consumable',1,1,None,'向指定可接受电池的目标提供2工量的供电步骤；不跳过断路前置，不开启任意门。',2)
equip('scanner',10,16,1,'support',0,0,1,'配队时显示本关两个已验证环境变体并允许二选一；不隐藏当前危险，不揭示人物秘密。进入任务后不使用。')
equip('beacon',11,0,0,'consumable',1,3,None,'空地落下诱饵，持续两次选敌；只影响巡检机下次计划，不暗改当前预告。',1)
equip('cutter',13,26,3,'tool',1,1,2,'相邻重障碍增加2工量；若未耗尽本关增援额度，预告下一轮最近合法出生格来一台巡检机；无合法格则取消。')
equip('stretcher',16,24,2,'support',0,0,None,'被动：搬运移动预算3；不与贺鸣或其他移动加成相加；稳定与拾起照常花AP。')
equip('extinguisher',18,0,0,'consumable',1,2,None,'清除相邻十字最多5格现有火，抑制该区域下一次火源；该区域焊接机当轮伤害-1。',1)
save('equipment.json',{'items':E,'inventory':'每种永久工具全队最多一件，六个人物槽是三人各tool/support各一。没有额外重量规则；旧weight字段退役。耗材独立队伍槽总容量3，医疗包的药剂也占位，单品最多2份。未用耗材结算归还，即使撤退；已用不返。永久工具只需购买一次，不因角色离队丢失。','craft':'在配队/营地按配方从通用物资转为耗材，无额外项目。购买按主线结算解锁，不要求成功。没有出售、复制、拆解退款。不能在战斗中访问仓库。','baseline':'无装备、无专长、零信任也能用通用交互完成主线必需步骤。装备缩短工量/路线或保住可选成果，不能成为必需钥匙。'})
P=[
 {'id':'relay_carry','name':'接力搬运','tags':['handoff'],'cost':'双方各1AP，邻接；一人携带一人空手','effect':'交接后接收者立即沿合法路径移动最多3地形代价，总预算不受担架等再加成；每对每轮一次。','baseline':'原携带者drop0，接收者pickup1，再move1；协议减少原地交换后的人力占用差异，不刷信任。'},
 {'id':'protected_work','name':'保护作业','tags':['dangerous_joint'],'cost':'双方各1AP，彼此邻接，执行者邻接目标','effect':'装置增加2工量，执行者获得一次机器伤害-2到下轮；不跳过前置、计时或专门路线。','baseline':'两次普通交互，同样2总AP但无临时护盾。'},
 {'id':'mutual_cover','name':'交叉掩护','tags':['dangerous_joint'],'cost':'双方各1AP，距离<=2','effect':'两人各得一次机器伤害-2至下轮，不防水火；同角色同类护盾取最大。','baseline':'躲开预告、拆敌或用屏障；保护不是基础移动的前提。'},
 {'id':'coordinated_pull','name':'协同牵引','tags':['partner_motion'],'cost':'双方各1AP，邻接同一重型机器','effect':'直接把重机推移一格，替代同轮两次基本推移；可选择任意空合法方向，不能推入X。','baseline':'两次基本推移总2AP，只能沿推手相反方向。'}]
save('progression_relationship.json',{
 'levels':{'thresholds':[0,12,28,48,72,100],'L1':'获得本人的第一个专长','L2':'选耐心施工（每任务第一次通用交互+1工量）或稳步移动（每任务第一次未搬运移动预算+1）','L3':'解锁第二专长，仍最多装备两项','L4':'基础HP+1','L5':'第三专长解锁，三选二','L6':'基础HP+1；获得另一项L2被动，两种各每任务一次，不同时重复触发同一交互','respec':'营地免费更换L2选择、专长和协议；不重置HP、次数、关系或任务状态；任务内锁定。','new_recruit':'使用加入任务所属章节的经验底线0/12/28/48；仍未达到100不强制满级。'},
 'protocols':P,'protocol_training':'两人在营地各花1物资，共占1训练项目，获得原训练XP与疲劳；双方T>=60且当前不拒绝相关标签时学会所选一项。记在pair+protocol，不因掉信任遗忘，但低于门槛暂不可用；恢复后无需重买。每人最多装备2协议，双方都装备才可用。不能同一项目免费学全部协议。',
 'relationship_commit':'负面记忆与限制在触发行动前预览，提交后即时影响未来动作，绝不反改已提交的动作。正向共同贡献在任务结算时按有向对发一次，单任务上限+4信任；不能当场互相搬运刷出协议。亲近不增加伤害或命中。',
 'stress':{'range':[0,100],'initial':10,'own_downing':8,'witness_downing_each_unique_actor':4,'known_mandatory_target_lost':4,'negative_gain_cap_per_mission':12,'meaningful_rescue_relief_cap':4,'night':-8,'dedicated_rest_extra':-16,'effect':'仅影响情绪与关系事件放大，不减少AP、不使基础动作随机失败。同一后果给压力，不再额外给疲劳；疲劳只按工作排班。'},
 'memory_events':[
 {'id':'promise_breach','severity':12,'trust_loss':8,'category':'promise','trigger':'玩家确认违背仍有效且当事人已知的具体承诺；单承诺一次；已提前同意的改约不是违约'},
 {'id':'risk_concealment','severity':16,'trust_loss':10,'category':'promise','trigger':'知道真实风险后选择隐瞒，并据此要求危险联合行动；不是缺少玩家尚未知的信息'},
 {'id':'unfair_assignment','severity':8,'trust_loss':4,'category':'fairness','trigger':'已约定轮值上限后再次要求额外关系服务；普通战斗派遣疲劳高不自动算不公'},
 {'id':'public_blame','severity':12,'trust_loss':6,'category':'humiliation','trigger':'对白中明确把未核实罪责公开归给某人；查看资料不是羞辱'},
 {'id':'honest_failure','severity':0,'trust_loss':0,'category':'promise','trigger':'如实报告风险、按约努力但任务失败；不自动惩罚所有关系'}],
 'responsibility':'队长确认违约且角色未主动提议时leader=1；角色主动提出且队长批准时leader=.5/proposer=.5；被迫执行或未获信息的队员=0。只有已知事件者建立记忆。普通事故无归责时只改变压力和世界。',
 'restrictions':{'lin':'对责任对象的dangerous_joint要求独立锚点/第三人保护；基础救援不受限','xu':'对责任对象的partner_motion要求任务前明确授权；可改为自主移动','su':'对责任对象的handoff要求先确认接应位置；额外营地调解可拒绝，基础班次不拒绝','chen':'dangerous_joint要求断电或加固；不签不实安全保证，通用交互仍可进行','ye':'对责任对象的dangerous_joint要求断电/绝缘；可独立操作','he':'危险协作需有效出口与救援期限；不剥夺别人控制权','mo':'拒绝公开无关私人信息，战术公开情报不扣留；无基础战斗限制','jiang':'handoff前确认人员/货物优先级；不偷拿物资'},
 'restriction_rules':'旧怨G本身不锁基础功能。进入Q>=65在相关标签施加条件，Q>=80且本任务尚无长冲突则进入一次协商。可明确分工无战术AP代价，部署物理保障按其动作付AP；不因点击确认自动加T。关系对可同时有多个条件，全显示。没有条件的协议不能为制造冲突而被禁用。',
 'repair':'认责只修该记忆一次(.85)；实质补救只一次(.45并去严重残余下限)，返还min(4,实际信任损失/2)；新守约另走任务贡献上限。旧怨的6/12/12修复只用于有证据的相关阶段，不是所有人物故事自动减怨。',
 'history_story_rule':'涉及双方历史的认责记录、实际补救、后续守约各产生一个稳定token；另一方缺席可记录证据但不立即改变其已知关系。回队/来信确认后生效；永久离队则只记叙事事实，不为刷数值召回。'
})
save('facilities.json',[
 {'id':'infirmary','tier1':'每晚第一个加速治疗病人物资成本2→1，第二人仍2；不与别的折扣叠加','tier2':'治疗项目可包含3人，第一人1其余2；不能让当天重伤在同一天支线出勤','costs':[[35,4],[60,8]]},
 {'id':'workshop','tier1':'每次主线后第一次永久工具购买零件成本-1，最低0；不补发旧购买退款','tier2':'队伍耗材总容量3→4，单品仍最多2；永久工具无额外副本','costs':[[35,4],[60,8]]},
 {'id':'rest_area','tier1':'专门恢复每人额外减疲劳12→16；基础睡眠不变','tier2':'每个恢复项目人数2→3；同一人一晚仍只能参加一项目','costs':[[35,4],[60,8]]},
 {'id':'communications','tier1':'新增一次第18日的公共记录核查窗口；仍每份耗一个项目，不提前凭空得证据','tier2':'第20/22/23日一项核查可核实两份不同记录；不返还过去已经投入的项目','costs':[[35,4],[60,8]]}
])
print('Authored combat, six enemies, 24 abilities, 12 equipment items, four protocols and eight facility tiers.')
