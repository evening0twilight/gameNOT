extends RefCounted
## Optional presentation knowledge. Never grants gameplay unlocks or rewards.
const FOUNDATION=["stories","equipment","roster"]
const TOPICS=["projects","talk","stories","equipment","roster","supplies","medicine","growth","relationships","mentors","operations","city","journal","evidence","publish","route","history","groups"]
const Chapter=preload("res://scripts/domain/chapter_one.gd")
static func initialize(s: Dictionary) -> void:
	s.tutorial.camp_lessons={"known":["projects","talk"],"introduced_day":0,"completed_day":0}
static func active(s: Dictionary) -> bool:
	return s.tutorial.has("camp_lessons") and s.tutorial.get("first_shift",{}).get("enabled",false)
static func known(s: Dictionary) -> Array:return s.tutorial.get("camp_lessons",{}).get("known",[])
static func completed(s: Dictionary) -> bool:return s.tutorial.get("camp_lessons",{}).get("completed_day",0)>0
static func valid_topic(topic: String,content: Dictionary) -> bool:
	if topic in TOPICS:return true
	for item: Dictionary in content.domains.equipment.items:
		if topic=="purchase:"+item.id:return true
	for facility: Dictionary in content.domains.facilities:
		if topic=="facility:"+facility.id:return true
	return false
static func valid(value: Variant,content: Dictionary,day: int) -> bool:
	if not value is Dictionary or not value.get("known") is Array:return false
	for key: String in ["introduced_day","completed_day","purchase_day"]:
		var n: Variant=value.get(key,0) if key=="purchase_day" else value.get(key)
		if not (n is int or n is float) or not is_finite(float(n)) or n!=int(n) or n<0 or n>day:return false
	var unique: Array=[]
	for topic: Variant in value.known:
		if not topic is String or unique.has(topic) or not valid_topic(topic,content):return false
		unique.append(topic)
	if value.completed_day>0:
		if value.completed_day<4:return false
		for topic: String in FOUNDATION:
			if not unique.has(topic):return false
	return true
static func pending(s: Dictionary) -> String:
	for i: int in range(FOUNDATION.size()):
		if s.campaign.day>=i+2 and not known(s).has(FOUNDATION[i]):return FOUNDATION[i]
	return ""
static func available(s: Dictionary,content: Dictionary) -> Array:
	if s.campaign.phase!="camp":return []
	var topics: Array=["projects","talk"]
	for i: int in range(FOUNDATION.size()):
		if s.campaign.day>=i+2:topics.append(FOUNDATION[i])
	if s.campaign.day<5:return topics
	topics.append_array(["supplies","medicine","growth","relationships","groups","city","history"])
	for item: Dictionary in content.domains.equipment.items:
		if s.chapter_one.main_completed>=int(item.unlocked_after_main) and not s.product.owned.has(item.id):topics.append("purchase:"+item.id)
	for facility: Dictionary in content.domains.facilities:
		if s.product.facilities[facility.id]<2:topics.append("facility:"+facility.id)
	for teacher: String in s.journey.recruited:
		for student: String in s.journey.recruited:
			if Chapter.mentor_offer(s,teacher,student).error.is_empty():
				if not topics.has("mentors"):topics.append("mentors")
	if not s.operations.facilities.is_empty():topics.append("operations")
	if s.campaign.day>=6:topics.append("journal")
	if not Chapter.Full.reviewable(s,content).is_empty():topics.append("evidence")
	if s.campaign.day>=18 and not s.full_campaign.evidence.is_empty() and s.full_campaign.publications.size()<2:topics.append("publish")
	if s.campaign.day==23:topics.append("route")
	return topics
static func urgent(s: Dictionary,content: Dictionary) -> String:
	# Time-limited services and final-route decisions must not wait in a tutorial queue.
	if s.campaign.day==23 and s.full_campaign.route.is_empty():return "route"
	for id: String in s.operations.facilities:
		var f: Dictionary=s.operations.facilities[id]
		var spec: Dictionary=content.domains.field_operations.investments[id]
		if s.campaign.day<spec.first_day-1 or s.campaign.day>spec.last_day or f.used>=2:continue
		if f.qualified:
			if s.operations.assistance_day!=s.campaign.day and f.available_day<=spec.last_day:return "operations"
		elif s.campaign.day<spec.last_day and s.campaign.projects<2 and s.inventory.supplies>=spec.repair_supplies:
			return "operations"
	return ""
static func next_tool_has_use(id: String,board: Dictionary) -> bool:
	match id:
		"shield","insulation":
			for enemy: Dictionary in board.enemies:
				if (id=="shield" and enemy.type in ["scout","sentinel","hauler"]) or (id=="insulation" and enemy.type=="skimmer"):return true
		"winch","stretcher":
			for objective: Dictionary in board.objectives:
				if objective.kind not in ["cargo","rescue"]:continue
				if id=="stretcher":return true
				for row: String in board.rows:
					if "X" in row:return true
		"scanner":
			for control: Dictionary in board.controls:
				if control.interaction_tags.has("machine_shutdown"):return true
	return false

static func offer(s: Dictionary,content: Dictionary) -> String:
	if not active(s) or s.campaign.phase!="camp" or s.campaign.day<2:return ""
	var due: String=urgent(s,content)
	if not due.is_empty() and not known(s).has(due):return due
	if s.tutorial.camp_lessons.introduced_day==s.campaign.day:return ""
	var basic: String=pending(s)
	if not basic.is_empty():return basic
	if s.campaign.day<5:return ""
	var candidates: Array=[]
	# A record window closes when the player leaves camp. Keep the decision
	# ahead of purchases and evergreen lessons, and only offer unfinished work.
	if s.campaign.projects<2 and not Chapter.Full.reviewable(s,content).is_empty():candidates.append("evidence")
	candidates.append("mentors")
	if s.inventory.supplies<4 and s.inventory.credits>=content.domains.economy.supply_buy_cost:candidates.append("supplies")
	for a: String in s.journey.recruited:
		if s.actors[a].ready_day>s.campaign.day:candidates.append("facility:infirmary")
	for pair: String in s.social:
		var ids: PackedStringArray=pair.split(">")
		if s.journey.recruited.has(ids[0]) and s.journey.recruited.has(ids[1]) and s.social[pair].band in ["conditional","rupture"]:candidates.append("relationships")
	if int(s.campaign.day)%6==0:candidates.append_array(["city","journal"])
	if s.campaign.day>=18:candidates.append_array(["evidence","publish"])
	if s.full_campaign.medicine_stock==0 and s.product.owned.has("medkit") and s.inventory.supplies>=1:candidates.append("medicine")
	for a: String in s.journey.recruited:
		if s.actors[a].xp>=12:candidates.append("growth")
	for pair: String in s.social:
		if not preload("res://scripts/domain/history_repair.gd").proof(s,pair).is_empty():candidates.append("history");break
	var tired: int=0
	for a: String in s.journey.recruited:
		if s.actors[a].fatigue>=40:tired+=1
	if tired>=2:candidates.append_array(["groups","facility:rest_area"])
	# Leave room to use a tool or save up for it before recommending another.
	var next_board: Dictionary=content.boards["M%02d"%mini(24,int(s.campaign.day)+1)]
	if int(s.campaign.day)-int(s.tutorial.camp_lessons.get("purchase_day",0))>=3:
		for item: Dictionary in content.domains.equipment.items:
			if s.product.owned.has(item.id) or not next_tool_has_use(item.id,next_board):continue
			if s.inventory.credits>=item.price_credits and s.inventory.parts>=Chapter.Product.purchase_parts(s,item):
				candidates.append("purchase:"+item.id)
	if s.campaign.day in [16,17,18] and not known(s).has("evidence"):candidates.append("facility:communications")
	if s.product.owned.size()>=3:candidates.append("facility:workshop")
	var allowed: Array=available(s,content)
	for topic: String in candidates:
		if not allowed.has(topic) or known(s).has(topic):continue
		if topic.begins_with("facility:"):
			var facility_id: String=topic.get_slice(":",1)
			var affordable: bool=false
			for facility: Dictionary in content.domains.facilities:
				if facility.id!=facility_id:continue
				var cost: Array=facility.costs[int(s.product.facilities[facility_id])]
				affordable=s.campaign.projects<2 and s.product.facility_day!=s.campaign.day and s.inventory.credits>=cost[0] and s.inventory.parts>=cost[1]
			if not affordable:continue
		return topic
	return ""
static func accept(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	var topic: Variant=c.payload.get("topic")
	if not active(s) or s.campaign.phase!="camp" or not topic is String:return "invalid_target"
	if not known(s).has(topic):
		if not available(s,content).has(topic):return "invalid_target"
		s.tutorial.camp_lessons.known.append(topic)
		s.tutorial.camp_lessons.introduced_day=s.campaign.day
		if topic.begins_with("purchase:"):s.tutorial.camp_lessons.purchase_day=s.campaign.day
	return ""
static func record(s: Dictionary,before: Dictionary,c: Dictionary) -> void:
	if not active(s):return
	if c.kind=="finish_evening" and before.campaign.day>=4 and pending(before).is_empty() and not completed(s):
		s.tutorial.camp_lessons.completed_day=before.campaign.day
