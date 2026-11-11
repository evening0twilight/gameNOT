extends RefCounted
const Delivery=preload("res://scripts/domain/story_delivery.gd")
const Crew=preload("res://scripts/domain/crew_journey.gd")
static func nodes(content: Dictionary) -> Dictionary:
	var result: Dictionary={}
	for group: String in ["personal_nodes","relationship_nodes","recovery_nodes"]:
		for node: Dictionary in content.domains.stories[group]:
			var entry:=node.duplicate(true);entry.category=group;result[node.id]=entry
	return result
static func available(s: Dictionary,content: Dictionary) -> Array:
	var result: Array=[]
	for node: Dictionary in nodes(content).values():
		if node.earliest_day>s.campaign.day or s.campaign.day>node.get("latest_day",23):continue
		var prerequisites: bool=true
		for id: String in node.get("requires_resolved",[]):
			if s.chapter_one.scenes.get(id,{}).get("status","")!="resolved":prerequisites=false
		if not prerequisites:continue
		var participants: Array=node.get("actors",[node.get("actor","")])
		var valid: bool=true
		for id: String in participants:
			if not s.actors.has(id) or not Crew.joined(s,id):valid=false
		if node.category=="recovery_nodes":
			for relation: Dictionary in s.social.values():
				if relation.observer!=node.actor:continue
				for memory: Dictionary in relation.memories:
					if memory.serious and memory.day==s.campaign.day:valid=false
		if valid:result.append(node.id)
	return result
static func script(content: Dictionary,node: Dictionary) -> Dictionary:
	var group: String={"personal_nodes":"personal","relationship_nodes":"relationships","recovery_nodes":"life"}[node.category]
	for entry: Dictionary in content.domains.scripts[group]:
		if entry.id==node.id:return entry
	return {}
static func apply(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	if s.campaign.phase!="camp":return "invalid_phase"
	var id: String=str(c.payload.get("node",""))
	if not available(s,content).has(id):return "story_unavailable"
	var node: Dictionary=nodes(content)[id]
	var record: Dictionary=s.chapter_one.scenes.get(id,{"seen":false,"choice":"","status":"unread"})
	if c.kind=="story_open":
		if record.seen:return "already_used"
		if s.campaign.talked.size()>=2:return "project_used"
		record.seen=true;record.status="seen";record.day=s.campaign.day
		record.delivery=Delivery.capture(s,node)
		if record.delivery.mode=="letter":record.status="resolved"
		record.injured=s.actors[node.actor].ready_day>s.campaign.day if node.has("actor") else false
		s.campaign.talked.append("story:"+id);s.chapter_one.scenes[id]=record
		return ""
	if not record.seen:return "story_not_opened"
	if not record.choice.is_empty():return "already_used"
	if Delivery.circumstances(s,node,record).mode=="letter":return "unavailable_actor"
	for actor: String in node.get("actors",[node.get("actor","")]):
		if s.product.withdrawn.has(actor):return "unavailable_actor"
	if c.kind=="story_defer":record.status="deferred";s.chapter_one.scenes[id]=record;return ""
	var choice: Dictionary={}
	for option: Dictionary in node.choices:
		if option.id==c.payload.get("choice"):choice=option;break
	if choice.is_empty():return "invalid_target"
	if node.get("stage",0)==3 and choice.id=="integrated":
		var contract: Dictionary=s.full_campaign.contracts.get(node.actor,{})
		if not contract.get("fulfilled",false) or contract.get("breached",false):return "proof_required"
	if choice.get("creates_contract",false) and s.campaign.day>choice.get("latest_creation_day",23):return "story_unavailable"
	var project_cost: int=int(node.get("project_cost",0))
	if s.campaign.projects+project_cost>2:return "project_used"
	if project_cost>0:
		for actor: String in node.get("participants",[node.get("actor","")]):
			if s.campaign.used.has(actor):return "project_used"
	if s.inventory.credits<int(choice.get("credits",0)):return "insufficient_resources"
	s.inventory.credits-=int(choice.get("credits",0));s.campaign.projects+=project_cost
	if project_cost>0:
		for actor: String in node.get("participants",[node.get("actor","")]):s.campaign.used.append(actor)
	if choice.get("creates_contract",false):
		s.full_campaign.contracts[node.actor]={"node":id,"choice":choice.id,"created_revision":s.revision+1,"created_day":s.campaign.day,"paid":int(choice.get("credits",0)),"fulfilled":false,"proof":"","fulfilled_day":0}
		if node.actor=="chen":s.full_campaign.known.chen_signed_responsibility=true
		if node.actor=="ye":s.full_campaign.known.maintenance_audit=true
	record.choice=choice.id;record.status="resolved";record.resolved_day=s.campaign.day
	s.chapter_one.scenes[id]=record
	for flag: String in choice.get("set_flags",[]):s.chapter_one.flags[flag]=true
	if id=="R10" and choice.id=="agreement":
		preload("res://scripts/domain/appraisal.gd").record(s,content,{"root":"R10:unanswered-calls","observers":["su","mo"],"known":false,"visible_doubt":true,"shares":{},"family":"cost_overrun","reason":"未接通的呼叫尚无结果证据；不能推定有人故意不接或已遇难。"})
	if node.category=="recovery_nodes":
		var pair: String=node.actor+">leader"
		s.social[pair].closeness=minf(100,float(s.social[pair].closeness)+3)
	elif node.category=="relationship_nodes":
		for pair: String in [node.actors[0]+">"+node.actors[1],node.actors[1]+">"+node.actors[0]]:
			s.social[pair].agreement="cooperate" if choice.id=="agreement" else "professional"
			s.social[pair].renegotiated_day=s.campaign.day
	preload("res://scripts/domain/full_campaign.gd").verify(s,content)
	return ""
