extends RefCounted
## Campaign scheduling; legacy state key is retained for P1/P2 migration.
const Crew=preload("res://scripts/domain/crew_journey.gd")
const Product=preload("res://scripts/domain/product_systems.gd")
const Full=preload("res://scripts/domain/full_campaign.gd")
const MAIN_LAST: int=24
static func ensure(s: Dictionary) -> void:
	Full.ensure(s)
	Product.ensure(s)
	if s.has("chapter_one"):return
	var completed: int=0
	for id: String in s.campaign.settled:
		if id.begins_with("M"):completed=maxi(completed,int(id.substr(1)))
	s.chapter_one={"main_completed":completed,"side_day":0,"attempted":[],"worked":[],"roster":[],"finished":false,"scenes":{},"flags":{}}
	if s.battle.has("heroes"):
		for id: String in s.battle.heroes:
			if s.actors.has(id):s.chapter_one.worked.append(id)
static func side_available(s: Dictionary,content: Dictionary) -> Array:
	ensure(s)
	var available: Array=[]
	if s.campaign.day>=24 or s.chapter_one.side_day==s.campaign.day:return available
	for board: Dictionary in content.boards.values():
		if board.kind=="side" and s.campaign.day>=board.day and s.campaign.day<=board.day+1 and not s.chapter_one.attempted.has(board.id) and not s.journey.declined_sides.has(board.id):available.append(board.id)
	return available
static func eligible(s: Dictionary) -> Array:
	var result: Array=[]
	for id: String in s.actors:
		var actor: Dictionary=s.actors[id]
		if not s.product.withdrawn.has(id) and Crew.joined(s,id) and actor.ready_day<=s.campaign.day and actor.fatigue+18<=100:result.append(id)
	return result
static func roster(s: Dictionary,requested: Variant,side: bool) -> Dictionary:
	var ready:=eligible(s)
	if not requested is Array:return {"ok":false,"error":"invalid_roster"}
	var party: Array=requested.duplicate()
	if party.is_empty():party=ready.slice(0,3)
	if party.size()>3:return {"ok":false,"error":"invalid_roster"}
	var seen: Array=[]
	for id: Variant in party:
		if not id is String or not ready.has(id) or seen.has(id):return {"ok":false,"error":"invalid_roster"}
		seen.append(id)
	if party.size()<mini(3,ready.size()):return {"ok":false,"error":"invalid_roster"}
	if side and party.size()!=3:return {"ok":false,"error":"side_requires_three"}
	return {"ok":true,"party":party}
static func command(s: Dictionary,c: Dictionary,content: Dictionary,rules: GDScript) -> String:
	ensure(s)
	var preparation_error: String=Product.prepare(s,c)
	if not preparation_error.is_empty():return preparation_error
	if c.kind=="start_side":
		var mission: String=str(c.payload.get("mission",""))
		if s.campaign.phase!="settlement" or not side_available(s,content).has(mission):return "side_unavailable"
		var chosen:=roster(s,c.payload.get("roster",[]),true)
		if not chosen.ok:return chosen.error
		s.chapter_one.roster=chosen.party
		var preparation: String=Full.prepare(s,c)
		if not preparation.is_empty():return preparation
		s.chapter_one.attempted.append(mission);s.chapter_one.side_day=s.campaign.day
		rules.deploy(s,content,mission)
		return ""
	if c.kind=="next_mission":
		var error: String=finish_evening(s,content,rules)
		if not error.is_empty():return error
		return depart(s,c,content,rules)
	return "unknown_command"
static func settled(s: Dictionary,board: Dictionary) -> void:
	ensure(s)
	if board.kind=="main":s.chapter_one.main_completed=maxi(s.chapter_one.main_completed,int(board.id.substr(1)))
static func group_project(s: Dictionary,c: Dictionary) -> String:
	var ids: Variant=c.payload.get("participants",[c.actor_id])
	var capacity: int=3 if (c.kind=="rest" and Product.tier(s,"rest_area")>=2) or (c.kind=="treat" and Product.tier(s,"infirmary")>=2) else 2
	if not ids is Array or ids.size()<1 or ids.size()>capacity:return "invalid_target"
	if s.campaign.phase!="camp" or s.campaign.day>=24:return "invalid_phase"
	if s.campaign.projects>=2:return "project_used"
	var seen: Array=[]
	for id: Variant in ids:
		if not id is String or not s.actors.has(id) or seen.has(id):return "invalid_target"
		var actor: Dictionary=s.actors[id]
		if not Crew.joined(s,actor.id) or s.product.withdrawn.has(id):return "unavailable_actor"
		if s.campaign.used.has(id):return "project_used"
		if c.kind=="train" and (actor.ready_day>s.campaign.day or Full.stages(s,id)<=0 or actor.xp>=100 or actor.fatigue+6>100):return "training_unavailable"
		
		if c.kind=="treat" and actor.ready_day<=s.campaign.day+1:return "invalid_target"
		seen.append(id)
	var cost: int=ids.size()*(2 if c.kind=="treat" else (1 if c.kind=="train" else 0))
	var discounted: bool=c.kind=="treat" and Product.tier(s,"infirmary")>=1 and s.product.treatment_day!=s.campaign.day
	if discounted:cost-=1
	if s.inventory.supplies<cost:return "insufficient_resources"
	s.inventory.supplies-=cost
	if c.kind=="treat":s.product.treatment_day=s.campaign.day
	for id: String in ids:
		var actor: Dictionary=s.actors[id]
		match c.kind:
			"train":actor.xp=mini(100,int(actor.xp)+12);actor.fatigue+=6;actor.training_completed+=1
			"treat":actor.ready_day=s.campaign.day+1
			"rest":actor.fatigue=maxi(0,int(actor.fatigue)-(16 if Product.tier(s,"rest_area")>=1 else 12));actor.stress=maxi(0,int(actor.stress)-16);actor.self_load=maxf(0,float(actor.self_load)-4)
		s.campaign.used.append(id)
	s.campaign.projects+=1
	return ""

static func mentor_offer(s: Dictionary,teacher: String,student: String) -> Dictionary:
	var offer: Dictionary={"gain":0,"ordinary":0,"reasons":[],"error":""}
	if teacher==student or not s.actors.has(teacher) or not s.actors.has(student):return {"gain":0,"ordinary":0,"reasons":["需要两位不同的已加入伙伴"],"error":"invalid_target"}
	var learner: Dictionary=s.actors[student]
	offer.ordinary=mini(12,100-int(learner.xp))
	offer.gain=maxi(0,mini(24,mini(int(s.actors[teacher].xp)-int(learner.xp),100-int(learner.xp))))
	if s.campaign.projects>=2:offer.reasons.append("今晚两个项目已经用完");offer.error="project_used"
	for id: String in [teacher,student]:
		var actor: Dictionary=s.actors[id]
		if s.product.withdrawn.has(id) or not Crew.joined(s,id) or actor.ready_day>s.campaign.day or actor.fatigue+6>100:offer.reasons.append(actor.name+" 当前不能参与带教");offer.error="unavailable_actor"
		if s.campaign.used.has(id):offer.reasons.append(actor.name+" 今晚已经参与一个项目");offer.error="project_used"
		var other: String=student if id==teacher else teacher
		var relation: Dictionary=s.social[id+">"+other]
		if relation.band in ["conditional","rupture"]:offer.reasons.append(actor.name+" 仍有需要保障的关系条件")
		if relation.agreement!="cooperate":offer.reasons.append(actor.name+" 尚未同意共同合作")
		if relation.contribution_missions.size()<2:offer.reasons.append(actor.name+" 只有%d/2场无相关违约的真实共同贡献"%relation.contribution_missions.size())
	if s.full_campaign.mentored.has("%s:%d"%[student,Full.chapter(s.campaign.day)]):offer.reasons.append("学员本章已接受一次带教")
	if Full.stages(s,student)<=0:offer.reasons.append("学员没有剩余训练阶段")
	if offer.gain<=offer.ordinary:offer.reasons.append("实际带教收益%d不高于普通训练%d；可保留阶段或选择普通训练"%[offer.gain,offer.ordinary])
	if s.inventory.supplies<2:offer.reasons.append("需要2物资");offer.error="insufficient_resources"
	if not offer.reasons.is_empty() and offer.error.is_empty():offer.error="mentorship_unavailable"
	return offer
static func mentor(s: Dictionary,c: Dictionary) -> String:
	var teacher: String=c.actor_id
	var student: String=str(c.payload.get("student",""))
	if not c.payload.get("consent",false):return "consent_required"
	var offer: Dictionary=mentor_offer(s,teacher,student)
	if not offer.error.is_empty():return offer.error
	s.inventory.supplies-=2;s.actors[student].xp+=offer.gain;s.actors[student].training_completed+=1
	s.full_campaign.mentored["%s:%d"%[student,Full.chapter(s.campaign.day)]]=true
	for id: String in [teacher,student]:s.actors[id].fatigue+=6;s.campaign.used.append(id)
	s.campaign.projects+=1
	return ""

static func finish_evening(s: Dictionary,content: Dictionary,rules: GDScript) -> String:
	if s.campaign.phase!="camp" or s.campaign.day>=24:return "invalid_phase"
	if s.campaign.day==23 and not Full.routes(s).has(s.full_campaign.route):return "route_required"
	s.campaign.day+=1
	for actor: Dictionary in s.actors.values():
		if not Crew.joined(s,actor.id):continue
		var idle: int=16 if not s.chapter_one.worked.has(actor.id) and int(s.journey.recruited[actor.id].day)<s.campaign.day-1 else 0
		actor.fatigue=maxi(0,int(actor.fatigue)-12-idle)
		actor.stress=maxi(0,int(actor.stress)-8);actor.self_load=maxf(0,float(actor.self_load)-2)
		rules.Appraisal.self_band(s,actor.id)
	for pair: String in s.social:
		var relation: Dictionary=s.social[pair]
		s.social[pair]=rules.Social.refresh(relation,s.campaign.day,int(s.actors[relation.observer].stress))
	s.campaign.projects=0;s.campaign.used=[];s.campaign.talked=[];s.chapter_one.worked=[]
	s.campaign.phase="briefing";s.journey.next_mission="M%02d"%(s.chapter_one.main_completed+1)
	var available: Array=eligible(s)
	var party: Array=[]
	for id: String in s.journey.draft.get("roster",s.battle.heroes.keys()):
		if available.has(id) and not party.has(id) and party.size()<3:party.append(id)
	for id: String in available:
		if party.size()<3 and not party.has(id):party.append(id)
	s.journey.draft={"roster":party,"support":"","medicine":0,"difficulty":s.campaign.difficulty,"dispatch":false,"loadout":s.product.loadout.duplicate(true),"tendencies":{}}
	return ""
static func depart(s: Dictionary,c: Dictionary,content: Dictionary,rules: GDScript) -> String:
	if s.campaign.phase!="briefing":return "invalid_phase"
	var payload: Dictionary=s.journey.draft.duplicate(true)
	payload.merge(c.payload,true)
	if not Crew.valid_draft(s,payload):return "invalid_target"
	var prepared: Dictionary=c.duplicate(true);prepared.payload=payload
	var error: String=Product.prepare(s,prepared)
	if not error.is_empty():return error
	var chosen: Dictionary=roster(s,payload.get("roster",[]),false)
	if not chosen.ok:return chosen.error
	s.chapter_one.roster=chosen.party
	var used: Array=[]
	for actor: String in payload.get("loadout",{}):
		if not s.actors.has(actor):return "unavailable_actor"
		if not Crew.joined(s,actor):
			if payload.loadout[actor].values().any(func(v: Variant):return v!=""):return "unavailable_actor"
			continue
		for slot: String in ["tool","support"]:
			var item: String=str(payload.loadout[actor].get(slot,""))
			if not item.is_empty():
				if used.has(item) or not s.product.owned.has(item) or Product.item(content,item).get("slot")!=slot:return "tool_unavailable"
				used.append(item)
			s.product.loadout[actor][slot]=item
	for id: String in payload.get("tendencies",{}):
		if not Crew.joined(s,id) or payload.tendencies[id] not in ["work","move"]:return "invalid_target"
		s.actors[id].tendency=payload.tendencies[id]
	error=Full.prepare(s,prepared)
	if not error.is_empty():return error
	rules.deploy(s,content,s.journey.next_mission)
	return ""
