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
	for key: String in ["introduced_day","completed_day"]:
		var n: Variant=value.get(key)
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
	if int(s.campaign.day) in [20,22,23] or (s.campaign.day==18 and s.product.facilities.communications>=1):topics.append("evidence")
	if s.campaign.day>=18 and not s.full_campaign.evidence.is_empty():topics.append("publish")
	if s.campaign.day==23:topics.append("route")
	return topics
static func urgent(s: Dictionary,content: Dictionary) -> String:
	# Time-limited services and final-route decisions must not wait in a tutorial queue.
	if s.campaign.day==23:return "route"
	for id: String in s.operations.facilities:
		var f: Dictionary=s.operations.facilities[id]
		var spec: Dictionary=content.domains.field_operations.investments[id]
		if s.campaign.day<=spec.last_day and s.campaign.day>=spec.first_day-1 and f.used<2:return "operations"
	return ""
static func offer(s: Dictionary,content: Dictionary) -> String:
	if not active(s) or s.campaign.phase!="camp" or s.campaign.day<2:return ""
	var due: String=urgent(s,content)
	if not due.is_empty() and not known(s).has(due):return due
	if s.tutorial.camp_lessons.introduced_day==s.campaign.day:return ""
	var basic: String=pending(s)
	if not basic.is_empty():return basic
	if s.campaign.day<5:return ""
	var candidates: Array=[]
	if s.inventory.supplies<4:candidates.append("supplies")
	for a: String in s.journey.recruited:
		if s.actors[a].ready_day>s.campaign.day:candidates.append("facility:infirmary")
	for pair: String in s.social:
		var ids: PackedStringArray=pair.split(">")
		if s.journey.recruited.has(ids[0]) and s.journey.recruited.has(ids[1]) and s.social[pair].band in ["conditional","rupture"]:candidates.append("relationships")
	candidates.append("mentors")
	if s.campaign.day%6==0:candidates.append_array(["city","journal"])
	if s.campaign.day>=18:candidates.append_array(["evidence","publish"])
	if s.full_campaign.medicine_stock==0 and s.product.owned.has("medkit"):candidates.append("medicine")
	for a: String in s.journey.recruited:
		if s.actors[a].xp>=12:candidates.append("growth")
	for pair: String in s.social:
		if not preload("res://scripts/domain/history_repair.gd").proof(s,pair).is_empty():candidates.append("history");break
	var tired: int=0
	for a: String in s.journey.recruited:
		if s.actors[a].fatigue>=40:tired+=1
	if tired>=2:candidates.append_array(["groups","facility:rest_area"])
	# Offer purchases one at a time, only once their actual unlock is reached.
	for item: Dictionary in content.domains.equipment.items:
		if not s.product.owned.has(item.id) and s.inventory.credits>=item.price_credits and s.inventory.parts>=item.price_parts:candidates.append("purchase:"+item.id)
	if s.campaign.day>=18:candidates.append("facility:communications")
	if s.product.owned.size()>=3:candidates.append("facility:workshop")
	var allowed: Array=available(s,content)
	for topic: String in candidates:
		if allowed.has(topic) and not known(s).has(topic):return topic
	return ""
static func accept(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	var topic: Variant=c.payload.get("topic")
	if not active(s) or s.campaign.phase!="camp" or not topic is String:return "invalid_target"
	if not known(s).has(topic):
		if not available(s,content).has(topic):return "invalid_target"
		s.tutorial.camp_lessons.known.append(topic)
		s.tutorial.camp_lessons.introduced_day=s.campaign.day
	return ""
static func record(s: Dictionary,before: Dictionary,c: Dictionary) -> void:
	if not active(s):return
	if c.kind=="finish_evening" and before.campaign.day>=4 and pending(before).is_empty() and not completed(s):
		s.tutorial.camp_lessons.completed_day=before.campaign.day
