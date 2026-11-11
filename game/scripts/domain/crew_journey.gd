extends RefCounted
## Recruitment is a settlement fact, never a day-number UI unlock.
static func initialize(s: Dictionary) -> void:
	if s.has("journey"):return
	s.journey={"recruited":{},"introduced":[],"next_mission":"M01","draft":{},"declined_sides":[],"night_reviewed":false}
	for id: String in s.actors:
		if int(s.actors[id].join)==1:s.journey.recruited[id]={"mission":"initial","day":1,"revision":0}
static func joined(s: Dictionary,id: String) -> bool:
	return s.actors.has(id) and s.get("journey",{}).get("recruited",{}).has(id)
static func recruit(s: Dictionary,mission: String) -> Array:
	var result: Array=[]
	if not mission.begins_with("M"):return result
	for id: String in s.actors:
		if not joined(s,id) and int(s.actors[id].join)==int(mission.substr(1)):
			s.journey.recruited[id]={"mission":mission,"day":s.campaign.day,"revision":s.revision+1}
			result.append(id)
	return result
static func migrate(s: Dictionary) -> void:
	if s.has("journey"):
		load("res://scripts/domain/field_operations.gd").ensure(s)
		load("res://scripts/domain/appraisal.gd").ensure(s)
		for checkpoint: Dictionary in s.battle.get("undo",[]):migrate(checkpoint)
		return
	initialize(s)
	load("res://scripts/domain/field_operations.gd").ensure(s)
	load("res://scripts/domain/appraisal.gd").ensure(s)
	# Preserve crew already available in legacy saves; never re-award XP/resources.
	for id: String in s.actors:
		if int(s.actors[id].join)<=int(s.campaign.day):
			s.journey.recruited[id]={"mission":"legacy","day":s.campaign.day,"revision":s.revision}
			s.journey.introduced.append(id)
	s.journey.next_mission="M%02d"%mini(24,int(s.chapter_one.main_completed)+1)
	for checkpoint: Dictionary in s.battle.get("undo",[]):migrate(checkpoint)
static func ready_ids(s: Dictionary,day: int=-1) -> Array:
	var ids: Array=[]
	var on_day: int=s.campaign.day if day<0 else day
	for id: String in s.actors:
		var a: Dictionary=s.actors[id]
		if joined(s,id) and not s.product.withdrawn.has(id) and a.ready_day<=on_day and a.fatigue+18<=100:ids.append(id)
	return ids
static func prepare_initial(s: Dictionary) -> void:
	s.campaign.phase="briefing"
	for a: Dictionary in s.actors.values():a.fatigue=0
	s.chapter_one.worked=[]
	s.journey.next_mission="M01"
	s.journey.draft={"roster":["lin","xu","su"],"support":"","medicine":0,"difficulty":s.campaign.difficulty,"dispatch":false,"loadout":s.product.loadout.duplicate(true),"tendencies":{}}
static func draft(s: Dictionary,c: Dictionary) -> String:
	if s.campaign.phase!="briefing":return "invalid_phase"
	var value: Variant=c.payload.get("draft")
	if not value is Dictionary or not valid_draft(s,value):return "invalid_target"
	if not value.get("roster") is Array or value.roster.size()>3:return "invalid_roster"
	for id: Variant in value.roster:
		if not id is String or not joined(s,id):return "unavailable_actor"
	s.journey.draft=value.duplicate(true)
	return ""

static func valid_draft(s: Dictionary,d: Variant) -> bool:
	if not d is Dictionary:return false
	if not d.get("roster",[]) is Array or d.get("roster",[]).size()>3:return false
	var seen: Array=[]
	for id: Variant in d.get("roster",[]):
		if not id is String or not joined(s,id) or seen.has(id):return false
		seen.append(id)
	if not d.get("support","") is String or (d.get("support","")!="" and not joined(s,d.support)):return false
	if not d.get("dispatch",false) is bool or d.get("difficulty",s.campaign.difficulty) not in ["relaxed","standard","hard"]:return false
	var amount: Variant=d.get("medicine",0)
	if not (amount is int or amount is float) or not is_finite(float(amount)) or amount!=int(amount) or amount<0 or amount>3:return false
	if not d.get("loadout",{}) is Dictionary or not d.get("tendencies",{}) is Dictionary:return false
	for id: Variant in d.get("loadout",{}):
		if not id is String or not s.actors.has(id) or not d.loadout[id] is Dictionary:return false
		for slot: String in ["tool","support"]:
			if not d.loadout[id].get(slot,"") is String:return false
	for id: Variant in d.get("tendencies",{}):
		if not id is String or not joined(s,id) or d.tendencies[id] not in ["work","move"]:return false
	return true
static func valid(s: Dictionary,content: Dictionary) -> bool:
	var j: Variant=s.get("journey")
	if not j is Dictionary or not j.get("recruited") is Dictionary or not j.get("introduced") is Array or not j.get("declined_sides") is Array or not j.get("night_reviewed") is bool:return false
	if not content.boards.has(j.get("next_mission")) or not str(j.next_mission).begins_with("M") or not valid_draft(s,j.get("draft")):return false
	for id: Variant in j.recruited:
		var record: Variant=j.recruited[id]
		if not s.actors.has(id) or not record is Dictionary or not record.get("mission") is String:return false
		for field: String in ["day","revision"]:
			if not (record.get(field) is int or record.get(field) is float) or record[field]<0:return false
		if record.day>s.campaign.day or record.revision>s.revision:return false
	for id: Variant in j.introduced:
		if not j.recruited.has(id):return false
	for id: Variant in j.declined_sides:
		if not content.boards.has(id) or content.boards[id].kind!="side":return false
	return true

static func overnight_fatigue(s: Dictionary,id: String,value: int) -> int:
	var idle: int=16 if not s.chapter_one.worked.has(id) and int(s.journey.recruited[id].day)<s.campaign.day else 0
	return maxi(0,value-12-idle)
