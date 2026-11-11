extends RefCounted
const I18n=preload("res://scripts/presentation/localization.gd")
const Stories=preload("res://scripts/domain/chapter_stories.gd")
const Delivery=preload("res://scripts/domain/story_delivery.gd")
static var data: Dictionary={}
static func catalog() -> Dictionary:
	if data.is_empty():data=JSON.parse_string(FileAccess.get_file_as_string("res://data/presentation/character_journey.json"))
	return data
static func contact(id: String) -> Dictionary:return catalog().contacts[id]
static func actor_name(s: Dictionary,id: String) -> String:
	return I18n.t("leader") if id=="leader" else s.actors.get(id,{}).get("name",I18n.t("journey.unknown"))
static func scene(s: Dictionary,content: Dictionary,id: String) -> Dictionary:
	var node: Dictionary=Stories.nodes(content)[id]
	var record: Dictionary=s.chapter_one.scenes[id]
	var script: Dictionary=Stories.script(content,node)
	var delivery: Dictionary=Delivery.circumstances(s,node,record)
	var staging: Dictionary=catalog().scenes[id]
	var lines: Array=[];var field: String="opening"
	if delivery.mode=="letter":
		lines=[catalog().letters.get(id,script.get("letter",script.get("withdrawn",script.get("absent",node.get("absent","")))))]
		field="letter"
	elif delivery.mode=="recovery":
		if script.has("injured_opening"):
			lines=script.injured_opening.duplicate();lines[0]=catalog().recovery_openings[id];field="injured_opening"
		elif node.category=="recovery_nodes":lines=[catalog().injured_life[id]];field="injured_life"
		else:lines=[I18n.t("journey.recovery_scene")]+script.opening
	else:lines=script.get("opening",[])
	var pages: Array=[]
	for index: int in range(lines.size()):pages.append(page(content,node,staging,"opening",index,str(lines[index]),delivery))
	if not record.choice.is_empty():
		var choices: Dictionary=script.get("injured_choices",script.choices) if delivery.mode=="recovery" else script.choices
		if delivery.mode=="recovery" and node.category=="recovery_nodes":choices=catalog().injured_life_choices.get(id,choices)
		for index: int in range(choices.get(record.choice,[]).size()):
			var line: String=choices[record.choice][index]
			if line.begins_with("本次只记录意愿和安排"):
				line=catalog().recovery_close[node.actor]
			pages.append(page(content,node,staging,"choices."+record.choice,index,line,delivery))
	return {"pages":pages,"delivery":delivery,"field":field,"location":"clinic" if delivery.mode=="recovery" else staging.location,"tone":staging.tone,"node":node,"record":record,"script":script}
static func page(content: Dictionary,node: Dictionary,staging: Dictionary,field: String,index: int,line: String,delivery: Dictionary) -> Dictionary:
	var actors: Array=node.get("actors",[node.get("actor","")])
	var direction: Array=staging.directions.get(field,[])
	var frame: Dictionary=direction[mini(index,direction.size()-1)].duplicate(true) if not direction.is_empty() else {"speaker":actors[0],"expressions":{}}
	frame.text=line
	for actor: String in actors:
		if line.begins_with(content.actors[actor].name+"："):frame.speaker=actor
		if delivery.injured.has(actor):frame.expressions[actor]="injured"
	if delivery.mode=="letter":frame.expressions={};frame.speaker=""
	return frame
static func district_name(id: String) -> String:return I18n.t("journey.district."+id)
static func situation(s: Dictionary,content: Dictionary,mission: String) -> Array[String]:
	var lines: Array[String]=[]
	var board: Dictionary=content.boards[mission]
	for entry: Dictionary in content.domains.world.missions:
		if entry.id!=mission:continue
		var district: String=entry.district
		lines.append(I18n.t("journey.district_state")%[district_name(district),s.campaign.districts[district],s.full_campaign.district_caps[district]])
	var water: Dictionary=board.environment.water_addition
	var variant: bool=s.product.get("variant","A")=="B"
	var wr: int=board.variant.B.water_round if variant else water.round
	lines.append(I18n.t("journey.water")%[s.product.get("variant","A"),wr])
	if not board.environment.fire_pulse.cells.is_empty():lines.append(I18n.t("journey.fire")%(board.variant.B.fire_round if variant else board.environment.fire_pulse.round))
	lines.append(board.environment.briefing)
	if s.campaign.failure_modifier:lines.append(I18n.t("journey.rubble"))
	for objective: Dictionary in board.objectives:
		if objective.kind=="rescue" and mission!="M01":lines.append(I18n.t("journey.rescue_clock")%objective.label)
	return lines
static func reactions(s: Dictionary,content: Dictionary) -> Array:
	var rows: Array=[]
	for e: Dictionary in s.appraisal.events.values():
		if e.mission!=s.battle.mission_id:continue
		var concern: String=""
		for profile: Dictionary in content.domains.experience.actors:
			if profile.id==e.observer:concern=profile.appraisal
		var details: Array[String]=[]
		if e.family=="personal":details.append(I18n.t("journey.personal_change")%[e.stress,e.self_load])
		else:
			for target: String in e.get("directions",{}):
				var d: Dictionary=e.directions[target]
				details.append(I18n.t("journey.trust_loss")%[actor_name(s,target),float(d.loss)])
				var relation: Dictionary=s.social.get(e.observer+">"+target,{})
				if relation.get("band","") in ["conditional","rupture"]:details.append(content.actors[e.observer].rupture)
			for effect: Variant in e.get("consequences",[]):
				if effect is String:details.append(effect)
		rows.append({"actor":e.observer,"fact":e.reason,"concern":concern,"change":"\n".join(details)})
	for key: String in s.appraisal.positive:
		var p: Variant=s.appraisal.positive[key]
		if not p is Dictionary or not key.begins_with(s.battle.mission_id+":"):continue
		var ids: PackedStringArray=p.pair.split(">")
		var object: Dictionary=s.battle.objects.get(p.object,{})
		rows.append({"actor":ids[0],"fact":I18n.t("journey.shared_result")%[actor_name(s,ids[1]),object.get("label",I18n.t("journey.field_service"))],"concern":I18n.t("journey.shared_concern"),"change":I18n.t("journey.trust_gain")%[actor_name(s,ids[1]),p.gain]})
	for p: Dictionary in s.appraisal.provisional.values():
		if p.mission!=s.battle.mission_id:continue
		rows.append({"actor":p.observer,"fact":p.reason,"concern":I18n.t("journey.unverified"),"change":I18n.t("journey.verification."+p.status)})
	return rows
static func memory_text(s: Dictionary,memory: Dictionary) -> String:
	for entry: Dictionary in s.appraisal.events.values():
		for target: String in entry.get("directions",{}):
			if entry.root+":"+entry.observer+":"+target==memory.id:return entry.reason
	return I18n.t("journey.memory."+str(memory.get("category","promise")))
