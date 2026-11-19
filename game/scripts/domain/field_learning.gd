extends RefCounted
## Saved knowledge, not gameplay unlocks. Suggestions use the production reducer.
const BASIC=["move","stabilize","pickup","extract","leave_site","interact","attack","push","drop","cross_anchor","service_watch","restore_power","prepare_safety","authorize","promise_retreat","declare_priority"]
const PROTOCOLS=["protected_work","relay_carry","mutual_cover","coordinated_pull"]
static func active(s: Dictionary) -> bool:
	return s.campaign.phase=="battle" and s.battle.mission_id!="M01" and s.tutorial.get("first_shift",{}).get("enabled",false)
static func token(c: Dictionary) -> String:
	match c.kind:
		"specialty":return "ability:"+str(c.payload.get("ability",""))+(":ap" if c.payload.get("mode","")=="ap" else "")
		"use_tool":return "tool:"+str(c.payload.get("item",""))
		"protocol":return "protocol:"+str(c.payload.get("protocol",""))
	return c.kind if c.kind in BASIC else ""
static func known(s: Dictionary) -> Array:
	if s.tutorial.has("field_lessons"):return s.tutorial.field_lessons.known.duplicate()
	var result: Array=["move"]
	for kind: String in s.tutorial.get("first_shift",{}).get("actions",[]):
		if kind in BASIC and not result.has(kind):result.append(kind)
	# Prior first-shift builds saved commands but not individual ability/tool lessons.
	for raw: String in s.commands.values():
		var c: Variant=JSON.parse_string(raw)
		if c is Dictionary and c.has("kind") and c.get("payload") is Dictionary:
			var topic: String=token(c)
			if not topic.is_empty() and not result.has(topic):result.append(topic)
	return result
static func ensure(s: Dictionary) -> void:
	if not s.tutorial.has("field_lessons"):s.tutorial.field_lessons={"known":known(s),"quiet":false}
static func record(s: Dictionary,before: Dictionary,c: Dictionary) -> void:
	if not s.tutorial.has("first_shift") or c.kind in ["undo","field_lesson","tutorial_ack"]:return
	if s.campaign.phase=="battle" and before.campaign.phase!="battle":ensure(s);s.tutorial.field_lessons.quiet=false;return
	if before.campaign.phase!="battle":return
	ensure(s)
	var topic: String=token(c)
	var new_topic: bool=not topic.is_empty() and not s.tutorial.field_lessons.known.has(topic)
	if new_topic:s.tutorial.field_lessons.known.append(topic)
	var object: Dictionary=before.battle.objects.get(c.payload.get("target",""),{})
	if c.kind=="interact" and object.get("kind","") in ["channel","convoy"]:
		var mechanic: String="objective:"+object.kind
		if not s.tutorial.field_lessons.known.has(mechanic):s.tutorial.field_lessons.known.append(mechanic);new_topic=true
	# Let the player perform a familiar action before introducing another feature.
	s.tutorial.field_lessons.quiet=new_topic
static func valid_topic(topic: String,content: Dictionary) -> bool:
	if topic in BASIC or topic in ["objective:channel","objective:convoy"]:return true
	if topic.begins_with("protocol:"):return topic.trim_prefix("protocol:") in PROTOCOLS
	if topic.begins_with("tool:"):
		for item: Dictionary in content.domains.equipment.items:
			if topic=="tool:"+item.id:return true
	if topic.begins_with("ability:"):
		for spec: Dictionary in content.domains.abilities:
			if topic=="ability:"+spec.id or (spec.id=="su_3" and topic=="ability:su_3:ap"):return true
	return false
static func compact(s: Dictionary) -> Dictionary:
	var trial: Dictionary=s.duplicate();trial.battle=s.battle.duplicate();trial.battle.undo=[]
	return trial
static func legal(s: Dictionary,content: Dictionary,actor: String,kind: String,payload: Dictionary) -> bool:
	var rules: GDScript=load("res://scripts/domain/campaign_rules.gd")
	return rules.reduce(compact(s),{"kind":kind,"actor_id":actor,"payload":payload,"command_id":"learning-probe-%d"%s.revision,"root_decision_id":"learning-probe","expected_revision":s.revision},content).ok
static func describe(topic: String,content: Dictionary,state: Dictionary={}) -> Dictionary:
	var rows: Dictionary={
		"prepare_safety":["先做保障","关系紧张时，协作可能需要有人先站稳保护位置。","站在伙伴旁的干地，选择保障对象和类型；消耗与本轮有效条件会显示在预览。"],
		"authorize":["明确授权","许舟在关系紧张时，需要明确授权才愿意进行部分协作。","选择许舟后确认授权。这会形成现场承诺记录，并越过撤销边界。"],
		"promise_retreat":["约定撤退","可以主动向团队约定离场期限；承诺之后需要按时撤出。","确认前核对期限：本场时限前两轮。作出承诺会越过撤销边界，之后要按约撤出。"],
		"declare_priority":["声明优先事项","同时有人员和物资时，可明确这次交接优先什么。","选择人员或物资优先；它只声明取舍，不替你完成目标。"],
		"move":["移动","靠近任务目标，或离开危险区域。","点移动，再点亮格；看清路线和消耗后确认。"],
		"interact":["交互","施工和停机都用交互。进度达到要求，目标才算完成。","先靠近装置，点「交互」，再点字母目标。查看进度和费用后确认。"],
		"attack":["攻击","机器挡住路线时，可以消耗行动点削减它的生命。救援不要求清空所有机器。","点攻击，再点机器；确认伤害和消耗。也可以绕开或寻找停机开关。"],
		"push":["推撞","把相邻机器移开，给行动路线腾位置。重型机器有额外条件。","点推撞，再点相邻机器；先检查落点、费用和是否需要后续配合。"],
		"stabilize":["稳定","伤员需要先稳伤，才能搬运。","靠近后点稳定，再点伤员，检查预览后确认。"],
		"pickup":["拾起","把伤员或物资带往出口。背在身上还不算完成救援。","靠近目标，点拾起并选目标；伤员需要先稳定。"],
		"extract":["交付","把携带的伤员或物资真正送达。","携带者站在出口，点交付并确认。"],
		"leave_site":["撤出","队员也需要回到出口离开现场。","站在出口后点撤出，先核对未完成的目标和离场后果。"],
		"drop":["放下","需要腾出双手或调整搬运时，可以把携带物放回现场。","点放下再选位置；之后仍需要拾起并送达，放下不会完成救援。"],
		"cross_anchor":["跨锚点","已部署的绞盘提供携带伤员跨深水的路线。","靠近锚点，点跨锚点，再点另一端；每次仍消耗行动点。"],
		"objective:channel":["持续作业","这项任务启动后还需要持续满足现场条件，不能把启动当成完成。","交互启动后，核对持续轮数与供电条件。等待期间保护装置，完成后再离场。"],
		"objective:convoy":["护送目标","护送物会沿路线推进，需要保护到达终点。","靠近并交互启动；查看位置、进度与生命，安排队员沿途照应。"],
		"service_watch":["现场值守","有些设施需要供电和人员连续值守，才能产生服务效果。","站到标出的岗位，再选择值守；下一轮仍须检查供电、岗位与时限。"],
		"restore_power":["恢复供电","停机会影响相连设施。需要继续使用设施时，可以恢复对应回路。","选择已经完成的关联开关，查看恢复供电的预览后确认。"],
		"protocol:protected_work":["掩护作业","相邻伙伴一起投入行动点，提高一次施工进度并提供掩护。","选择目标与参与伙伴，查看两人的费用、实际进度和保障条件，再确认。"],
		"protocol:relay_carry":["接力搬运","相邻伙伴接过携带物并移动，原携带者可以腾出手。","选择接收人和落点；预览会核对双方行动点、同意与安全条件。"],
		"protocol:mutual_cover":["互相掩护","机器即将攻击时，两位附近伙伴可以共同提供掩护。","选择伙伴，先看两人费用和防护效果；它不能替代离开危险区。"],
		"protocol:coordinated_pull":["协同牵引","重型机器需要两位相邻伙伴配合才能移开。","选择机器、伙伴和相邻落点；先核对双方费用和落点是否合法。"]}
	if rows.has(topic):return {"topic":topic,"title":rows[topic][0],"why":rows[topic][1],"how":rows[topic][2],"kind":topic if not topic.contains(":") else "interact"}
	for spec: Dictionary in content.domains.abilities:
		if topic=="ability:"+spec.id or topic=="ability:"+spec.id+":ap":
			var method: String="点专长，再点对应目标；先看费用和次数，确认后才使用。"
			if spec.id in ["xu_1","ye_3","he_1"]:method="点专长，再点地图上的落点或铺设格；先检查预览，再确认。"
			if spec.id in ["lin_3","mo_3"]:method="先点专长和目标，再点移动或布设位置；最后核对预览。"
			var effect: String=spec.effect
			var experience: int=state.get("actors",{}).get(spec.actor,{}).get("xp",0)
			var level: int=preload("res://scripts/domain/p1_specialties.gd").level(experience)
			if topic.ends_with(":ap"):
				effect=spec.level5_effect
			elif spec.id!="su_3":
				if level>=5 and spec.has("level5_effect"):effect=spec.level5_effect
				elif level>=3 and spec.has("level3_effect"):effect=spec.level3_effect
			if spec.id=="he_3":method="搬起目标后直接移动，预览会显示这次能走到哪里。"
			return {"topic":topic,"title":spec.name+(" · 行动点支援" if topic.ends_with(":ap") else ""),"why":effect,"how":method,"kind":"specialty","ability":spec.id,"passive":spec.id=="he_3"}
	for item: Dictionary in content.domains.equipment.items:
		if topic=="tool:"+item.id:return {"topic":topic,"title":item.name if item.has("name") else item.id,"why":item.effect,"how":{"crowbar":"点撬棍，再点相邻的轻障碍。先看增加的施工进度，再确认。","scanner":"点扫描器，再点附近的停机装置；检查进度和剩余次数。","medkit":"点医疗包，再点身旁受伤的伙伴。确认前检查药剂与恢复量。","shield":"点屏障，再点身旁的空地。先看费用和布设位置，避免挡住通路。","insulation":"点绝缘工具，再点需要铺设的位置；预览会核对距离与费用。","winch":"先选一侧锚点，再选深水另一侧。布设后可使用跨锚点。","stretcher":"被动生效：装备者搬运时自动应用，不需要另外按一个技能。"}.get(item.id,""),"kind":"use_tool","item":item.id,"passive":item.id=="stretcher"}
	return {}
static func neighbors(cell: Array) -> Array:
	return [[cell[0]-1,cell[1]],[cell[0]+1,cell[1]],[cell[0],cell[1]-1],[cell[0],cell[1]+1]]
static func payloads(s: Dictionary,content: Dictionary,actor: String,topic: String) -> Array:
	var rules: GDScript=load("res://scripts/domain/campaign_rules.gd")
	var b: Dictionary=s.battle;var h: Dictionary=b.heroes[actor];var result: Array=[]
	var danger: Array=[]
	# Match the material to the actual attack. Insulation cannot stop a fire,
	# and a shield does not absorb an electrical discharge.
	if topic in ["ability:he_1","tool:shield","ability:ye_3","tool:insulation"]:
		var electric: bool=topic in ["ability:ye_3","tool:insulation"]
		for enemy: Dictionary in b.enemies.values():
			if enemy.get("paused_round",0)==b.round:continue
			if electric and (enemy.type!="skimmer" or int(b.round)%2!=0):continue
			if not electric and enemy.type not in ["scout","sentinel","hauler"]:continue
			danger.append_array(rules.Hazards.footprint(b,enemy,rules))
	elif topic=="protocol:mutual_cover":
		danger=load("res://scripts/presentation/guidance.gd").danger(b,rules)
	if topic in ["attack","push","interact","stabilize","pickup","restore_power"]:
		for object: Dictionary in (b.enemies.values() if topic in ["attack","push"] else b.objects.values()):
			if rules.distance(h.cell,object.cell)<=1:result.append({"target":object.id})
	elif topic in ["extract","leave_site","drop","authorize","promise_retreat"]:result.append({})
	elif topic=="declare_priority":result=[{"priority":"people"},{"priority":"cargo"}]
	elif topic=="prepare_safety":
		for partner: Dictionary in b.heroes.values():
			if partner.id!=actor and rules.distance(h.cell,partner.cell)==1:
				for kind: String in ["protected_work","mutual_cover"]:result.append({"target":partner.id,"protocol":kind})
	elif topic=="service_watch":
		for i: int in range(rules.Field.posts(b).size()):
			if rules.same(h.cell,rules.Field.posts(b)[i]):result.append({"post":i})
	elif topic.begins_with("ability:"):
		var id: String=topic.get_slice(":",1)
		if id=="chen_3" and not b.get("service",{}).is_empty():result.append({"ability":id,"target":"live_service"})
		if id=="xu_1":
			for n: int in [2,3]:
				for cell: Array in [[h.cell[0]-n,h.cell[1]],[h.cell[0]+n,h.cell[1]],[h.cell[0],h.cell[1]-n],[h.cell[0],h.cell[1]+n]]:
					var obstacle: bool=false
					for step: int in range(1,n):
						var mid: Array=[h.cell[0]+signi(cell[0]-h.cell[0])*step,h.cell[1]+signi(cell[1]-h.cell[1])*step]
						if rules.terrain(b,mid) in ["X","#"]:obstacle=true
					if obstacle:result.append({"ability":id,"cell":cell})
		elif id in ["he_1","ye_3"]:
			for cell: Array in danger:
				if rules.distance(h.cell,cell)<=3 and (id=="he_1" or not rules.contains_cell(b.insulation,cell)):result.append({"ability":id,"cell":cell})
		else:
			var targets: Array=b.objects.values() if id in ["lin_1","lin_3","chen_3","mo_1"] else (b.heroes.values() if id in ["xu_3","su_3","jiang_1","jiang_3"] else b.enemies.values())
			for target: Dictionary in targets:
				if rules.distance(h.cell,target.cell)>5:continue
				if id=="su_3" and not topic.ends_with(":ap") and b.move_bonuses.has(target.id):continue
				var p: Dictionary={"ability":id,"target":target.id,"consent":true,"mode":"ap" if topic.ends_with(":ap") else "move"}
				if id in ["lin_3","mo_3"]:
					for cell: Array in neighbors(target.cell) if id=="lin_3" else neighbors(h.cell):
						var at: Dictionary=p.duplicate();at.cell=cell;result.append(at)
				else:result.append(p)
	elif topic.begins_with("tool:"):
		var id: String=topic.trim_prefix("tool:")
		if id in ["shield","insulation"]:
			for cell: Array in danger:
				if rules.distance(h.cell,cell)<=1:result.append({"item":id,"cell":cell})
		elif id=="winch":
			for cell: Array in [h.cell]+neighbors(h.cell):
				for other: Array in [[cell[0]-2,cell[1]],[cell[0]+2,cell[1]],[cell[0],cell[1]-2],[cell[0],cell[1]+2]]:
					if other[0]>=0 and other[0]<8 and other[1]>=0 and other[1]<8 and rules.terrain(b,[int((cell[0]+other[0])/2),int((cell[1]+other[1])/2)])=="X":result.append({"item":id,"cell":cell,"other":other})
		else:
			for target: Dictionary in b.heroes.values() if id=="medkit" else b.objects.values():
				if rules.distance(h.cell,target.cell)<=4:result.append({"item":id,"target":target.id})
	elif topic=="cross_anchor":
		for anchor: Dictionary in b.deployed_tools.values():
			for cell: Array in [anchor.cell,anchor.other]:result.append({"cell":cell})
	elif topic.begins_with("protocol:"):
		var id: String=topic.trim_prefix("protocol:")
		for partner: Dictionary in b.heroes.values():
			if partner.id==actor or partner.left or partner.downed or partner.ap<1 or rules.distance(h.cell,partner.cell)>2:continue
			var p: Dictionary={"protocol":id,"partner":partner.id,"consent":true}
			if id=="protected_work":
				for post: int in range(rules.Field.posts(b).size()):
					var at: Dictionary=p.duplicate();at.post=post;result.append(at)
				for object: Dictionary in b.objects.values():
					if object.kind=="work" and not object.completed and rules.distance(h.cell,object.cell)<=1:
						var at: Dictionary=p.duplicate();at.target=object.id;result.append(at)
			elif id=="relay_carry" and not h.carrying.is_empty():
				for cell: Array in neighbors(partner.cell):
					var at: Dictionary=p.duplicate();at.cell=cell;result.append(at)
			elif id=="mutual_cover" and (rules.contains_cell(danger,h.cell) or rules.contains_cell(danger,partner.cell)):result.append(p)
			elif id=="coordinated_pull":
				for enemy: Dictionary in b.enemies.values():
					if enemy.type in ["hauler","sentinel"] and rules.distance(h.cell,enemy.cell)==1:
						for cell: Array in neighbors(enemy.cell):
							var at: Dictionary=p.duplicate();at.target=enemy.id;at.cell=cell;result.append(at)
	return result
static func available(s: Dictionary,content: Dictionary,actor: String) -> Array:
	var result: Array=BASIC.duplicate()
	var h: Dictionary=s.battle.heroes.get(actor,{})
	if h.is_empty():return result
	var rules: GDScript=load("res://scripts/domain/campaign_rules.gd")
	for spec: Dictionary in content.domains.abilities:
		if s.actors.has(actor) and spec.actor==actor and spec.level<=rules.Specialties.level(int(s.actors[actor].xp)) and spec.production_status=="active":result.append("ability:"+spec.id)
	if actor=="su" and rules.Specialties.level(int(s.actors.su.xp))>=5:result.append("ability:su_3:ap")
	for item: String in s.battle.equipment.get(actor,{}).values():
		if not item.is_empty():result.append("tool:"+item)
	for protocol: String in PROTOCOLS:result.append("protocol:"+protocol)
	for object: Dictionary in s.battle.objects.values():
		if object.kind in ["channel","convoy"] and not result.has("objective:"+object.kind):result.append("objective:"+object.kind)
	return result
static func example(s: Dictionary,content: Dictionary,actor: String,topic: String) -> Dictionary:
	var info: Dictionary=describe(topic,content,s)
	if topic.begins_with("protocol:"):info.kind="protocol"
	for payload: Dictionary in payloads(s,content,actor,topic):
		if legal(s,content,actor,info.kind,payload):
			info.payload=payload;info.actor=actor
			info.cell=payload.get("cell",s.battle.objects.get(payload.get("target",""),s.battle.enemies.get(payload.get("target",""),s.battle.heroes.get(payload.get("target",""),{}))).get("cell",[]))
			return info
	return {}
static func offer(s: Dictionary,content: Dictionary,actor: String) -> Dictionary:
	if not active(s) or s.tutorial.get("field_lessons",{}).get("quiet",false):return {}
	var learned: Array=known(s)
	var next: Dictionary=load("res://scripts/presentation/guidance.gd").next_step(s,content,actor)
	if next.get("action","") in BASIC and not learned.has(next.action):return describe(next.action,content)
	for object: Dictionary in s.battle.objects.values():
		if object.completed or object.lost or object.has("unavailable_reason"):continue
		if object.kind in ["work","channel","convoy"] and not learned.has("interact"):return describe("interact",content)
		var topic: String="objective:"+object.kind
		if object.kind in ["channel","convoy"] and not learned.has(topic):return describe(topic,content)
	var h: Dictionary=s.battle.heroes.get(actor,{})
	if h.is_empty() or h.left or h.downed or h.ap<=0:return {}
	var rules: GDScript=load("res://scripts/domain/campaign_rules.gd")
	var service: Dictionary=s.battle.get("service",{})
	if not learned.has("service_watch") and not service.is_empty() and not service.done and not service.failed and s.battle.round<=service.definition.deadline:
		for cell: Array in rules.Field.posts(s.battle):
			if rules.distance(h.cell,cell)<=2:
				var info: Dictionary=describe("service_watch",content);info.why=s.battle.service.definition.label+"："+info.why;return info
	# Match the safeguard to the person and situation; a promise is voluntary.
	if actor=="xu" and tense(s,actor) and not learned.has("authorize"):
		for other: Dictionary in s.battle.heroes.values():
			if other.id!=actor and rules.distance(h.cell,other.cell)<=2:
				var info: Dictionary=example(s,content,actor,"authorize")
				if not info.is_empty():return info
	if actor=="jiang" and tense(s,actor) and not h.carrying.is_empty() and not learned.has("declare_priority"):
		return describe("declare_priority",content)
	if actor!="lin" and s.battle.heroes.has("lin") and tense(s,"lin") and not learned.has("prepare_safety"):
		var lin: Dictionary=s.battle.heroes.lin
		for object: Dictionary in s.battle.objects.values():
			if object.get("risk_context",[]).has("fall") and not object.completed and rules.distance(lin.cell,object.cell)<=1 and rules.distance(h.cell,lin.cell)==1:
				var payload: Dictionary={"target":"lin","protocol":"protected_work"}
				if legal(s,content,actor,"prepare_safety",payload):
					var info: Dictionary=describe("prepare_safety",content);info.payload=payload;info.actor=actor;info.cell=lin.cell.duplicate();return info
	# During the four foundation nights, anchor the field card to the
	# current job. The handbook remains available for other legal choices.
	if s.campaign.day<=4:
		match s.battle.mission_id:
			"M03":
				if not learned.has("tool:crowbar") and s.battle.equipment.get(actor,{}).get("tool","")=="crowbar":
					return example(s,content,actor,"tool:crowbar")
			"M04","S01":
				if not learned.has("protocol:protected_work"):
					return example(s,content,actor,"protocol:protected_work")
			"S02":
				if not learned.has("protocol:relay_carry"):
					return example(s,content,actor,"protocol:relay_carry")
		return {}
	var topics: Array=available(s,content,actor)
	# Character/tool opportunities first, then ordinary combat and cooperation.
	for topic: String in topics:
		if learned.has(topic) or not topic.contains(":") or topic.begins_with("objective:"):continue
		var info: Dictionary=describe(topic,content,s)
		if info.get("passive",false):
			if not h.carrying.is_empty():return info
			continue
		var offered: Dictionary=example(s,content,actor,topic)
		if not offered.is_empty():return offered
	for topic: String in ["service_watch","restore_power","cross_anchor","attack","push"]:
		if not learned.has(topic):
			var offered: Dictionary=example(s,content,actor,topic)
			if not offered.is_empty():return offered
	return {}
static func accept(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	if not active(s):return "invalid_phase"
	if not s.battle.heroes.has(c.actor_id):return "unavailable_actor"
	var topic: String=str(c.payload.get("topic",""))
	if not valid_topic(topic,content):return "invalid_target"
	if c.payload.get("manual",false):
		if not available(s,content,c.actor_id).has(topic):return "ability_unavailable"
	elif offer(s,content,c.actor_id).get("topic","")!=topic:return "invalid_target"
	ensure(s)
	if not s.tutorial.field_lessons.known.has(topic):s.tutorial.field_lessons.known.append(topic)
	s.tutorial.field_lessons.quiet=true
	return ""

static func tense(s: Dictionary,actor: String) -> bool:
	for pair: String in s.social:
		if pair.begins_with(actor+">") and s.social[pair].band in ["conditional","rupture"]:return true
	return false
