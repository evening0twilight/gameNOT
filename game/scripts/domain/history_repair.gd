extends RefCounted
const Crew=preload("res://scripts/domain/crew_journey.gd")
## Directed historical repair: explicit acknowledgement, then distinct later factual receipts.
const Social=preload("res://scripts/domain/campaign_social.gd")
static func choice(s: Dictionary,id: String,value: String) -> bool:
	return s.chapter_one.scenes.get(id,{}).get("choice","")==value
static func contract(s: Dictionary,id: String,value: String) -> bool:
	var c: Dictionary=s.full_campaign.contracts.get(id,{})
	return c.get("choice","")==value and c.get("fulfilled",false) and not c.get("breached",false)
static func acknowledgement_ready(s: Dictionary,pair: String) -> bool:
	match pair:
		"lin>xu","xu>lin":return choice(s,"P_lin_1","share") and s.full_campaign.evidence.has("E_ORDER")
		"ye>chen","chen>ye","mo>chen":return s.full_campaign.evidence.has("E_MAINTENANCE") and s.full_campaign.known.get("chen_signed_responsibility",false)
		"su>xu":return choice(s,"P_su_1","list")
		"xu>he","he>xu":return choice(s,"R03","agreement")
		"chen>mo":return choice(s,"P_mo_1","classify") or choice(s,"R05","agreement")
	return false
static func together(result: Dictionary,pair: String,rescue: bool=false,safe: bool=false) -> bool:
	var actors: PackedStringArray=pair.split(">")
	var facts: Dictionary=result.get("rescues" if rescue else "contributions",{})
	for id: String in facts:
		if facts[id].has(actors[0]) and facts[id].has(actors[1]):
			if not safe:return true
			var prerequisites: Dictionary={"M02:power":"cut","M05:pump":"isolate","M07:worker":"cut","M11:lock":"cut","M13:log":"cut","M17:repair2":"repair1","S03:resident":"cut","S05:cloth":"isolate"}
			var prerequisite: String=prerequisites.get(result.mission+":"+id,"")
			if not prerequisite.is_empty() and result.facts.get(prerequisite,"")=="completed":return true
	return false
static func funded_work(s: Dictionary,r: Dictionary) -> bool:
	if not contract(s,"chen","fund") or not r.mission.begins_with("M"):return false
	for object: Dictionary in r.get("authored_work",[]):
		if object.kind=="work" and object.interaction_tags.has("engineering") and r.get("contributions",{}).get(object.id,[]).has("chen"):return true
	return false
static func delegated_rescue(s: Dictionary,r: Dictionary) -> bool:
	if not contract(s,"he","delegate") or not r.get("all_extracted",false) or not r.get("roster",[]).has("he"):return false
	var rescue: bool=r.get("protection",[]).has("he")
	var other: bool=false
	for actors: Array in r.get("rescues",{}).values():rescue=rescue or actors.has("he")
	for actors: Array in r.get("contributions",{}).values():
		for id: String in actors:other=other or (id!="he" and s.actors.has(id))
	return rescue and other
static func proof(s: Dictionary,pair: String) -> Dictionary:
	if not s.social.has(pair):return {}
	var actors: PackedStringArray=pair.split(">")
	for id: String in actors:
		if not s.actors.has(id) or not Crew.joined(s,id) or s.product.withdrawn.has(id):return {}
	var stage: int=int(s.social[pair].history_stage)+1
	if stage>3:return {}
	if stage==1:return {"source":"acknowledgement","mission":"","revision":s.revision+1} if acknowledgement_ready(s,pair) else {}
	var previous: Dictionary=s.product.history_proofs.get(pair+":"+str(stage-1),{})
	if previous.is_empty():return {}
	if (pair=="xu>lin" and stage==2) or (pair=="chen>mo" and stage==2):
		for event: Dictionary in s.receipts:
			if int(event.source_state_revision)<int(previous.revision):continue
			var c: Variant=JSON.parse_string(s.commands.get(event.command_id,"{}"))
			if not c is Dictionary:continue
			var valid: bool=(pair=="xu>lin" and c.get("kind")=="community_report" and c.payload.get("choice")=="publish") or (pair=="chen>mo" and c.get("kind")=="publish_record" and c.payload.get("privacy")=="redacted")
			if valid:return {"source":event.id,"mission":event.id.split("/")[1],"revision":int(event.source_state_revision)+1}
	for r: Dictionary in s.campaign.settled.values():
		if int(r.get("revision",0))<=int(previous.revision) or r.mission==previous.mission:continue
		var valid: bool=false
		var kept: bool=r.get("promise",{}).get("kept",false)
		match pair:
			"lin>xu":valid=contract(s,"xu","bounded") and r.get("standing",[]).has("xu") and kept if stage==2 else r.mission.begins_with("M") and together(r,pair,true) and not s.full_campaign.contracts.get("xu",{}).get("breached",false)
			"xu>lin":valid=stage==3 and together(r,pair)
			"ye>chen":valid=funded_work(s,r) if stage==2 else together(r,pair,false,true) and s.social[pair].agreement=="cooperate"
			"chen>ye":valid=together(r,pair)
			"su>xu":valid=r.mission.begins_with("M") and r.get("standing",[]).has("su") and r.get("standing",[]).has("xu") and kept
			"xu>he":valid=delegated_rescue(s,r) if stage==2 else together(r,pair)
			"he>xu":valid=contract(s,"xu","bounded") and r.get("standing",[]).has("xu") and kept if stage==2 else together(r,pair) and kept
			"mo>chen":valid=funded_work(s,r) if stage==2 else together(r,pair)
			"chen>mo":valid=stage==3 and together(r,pair) and not s.full_campaign.contracts.get("mo",{}).get("breached",false)
		if valid:return {"source":r.mission,"mission":r.mission,"revision":r.revision}
	return {}
static func apply(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	if s.campaign.phase!="camp" or s.campaign.day>=24:return "invalid_phase"
	var pair: String=str(c.payload.get("pair",""))
	var allowed: bool=false
	for route: Dictionary in content.domains.integration.history_repair_routes:
		if route.pair==pair:allowed=true
	if not allowed:return "invalid_target"
	if not c.payload.get("consent",false):return "consent_required"
	if s.campaign.talked.size()>=2:return "project_used"
	var receipt: Dictionary=proof(s,pair)
	if receipt.is_empty():return "history_proof_required"
	var stage: int=int(s.social[pair].history_stage)+1
	var token: String=pair+":"+str(stage)+":"+receipt.source
	s.social[pair]=Social.refresh(Social.Legacy.repair_history(s.social[pair],stage,token),s.campaign.day,s.actors[pair.split(">")[0]].stress)
	# Confirmation revision is the lower bound for the next stage, not the old source revision.
	receipt.source_revision=receipt.revision;receipt.revision=s.revision+1
	s.product.history_proofs[pair+":"+str(stage)]=receipt
	s.campaign.talked.append("history:"+token)
	return ""
