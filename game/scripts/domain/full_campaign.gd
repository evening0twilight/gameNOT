extends RefCounted
const Crew=preload("res://scripts/domain/crew_journey.gd")
## Four-chapter state and post-action evidence. No IO and no retrospective invented acts.
static func ensure(s: Dictionary) -> void:
	if s.has("full_campaign"):return
	s.full_campaign={"route":"","ending":"","evidence":{},"district_caps":{},"contracts":{},"mentored":{},"support":"","known":{},"scene_delivery":{},"migrated":false,"medicine_stock":0,"packed":0,"publications":[]}
	for id: String in s.campaign.districts:s.full_campaign.district_caps[id]=3
static func chapter(day: int) -> int:return mini(4,1+int((day-1)/6))
static func stages(s: Dictionary,id: String) -> int:
	return maxi(0,chapter(s.campaign.day)-chapter(s.actors[id].join)+1-int(s.actors[id].training_completed))
static func groups(s: Dictionary,board: Dictionary) -> Array:
	if board.id=="M24":return board.route_groups[s.full_campaign.route if not s.full_campaign.route.is_empty() else "evacuation"]
	return board.mandatory_groups
static func objective_active(s: Dictionary,board: Dictionary,o: Dictionary) -> bool:
	if board.id!="M24":return true
	if o.id=="archive" or o.has("disables"):return true
	for group: Array in groups(s,board):
		if group.has(o.id):return true
	return false
static func routes(s: Dictionary) -> Array:
	var result: Array=["distributed_rebuild","evacuation"]
	var total: int=0
	for value: int in s.campaign.districts.values():total+=value
	if total>=10 and s.full_campaign.evidence.size()>=2:result.push_front("shared_control")
	return result
static func command(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	ensure(s)
	if s.campaign.phase!="camp" or s.campaign.day>=24:return "invalid_phase"
	if c.kind=="craft_medicine":
		if s.inventory.supplies<1:return "insufficient_resources"
		s.inventory.supplies-=1;s.full_campaign.medicine_stock+=1
		return ""
	if c.kind=="publish_record":
		if s.campaign.day<18 or s.full_campaign.evidence.is_empty():return "record_unavailable"
		var privacy: String=str(c.payload.get("privacy",""))
		if privacy not in ["redacted","unredacted"]:return "invalid_target"
		if s.full_campaign.publications.has(privacy):return "already_used"
		s.full_campaign.publications.append(privacy)
		if s.full_campaign.contracts.has("mo"):
			var contract: Dictionary=s.full_campaign.contracts.mo
			if privacy=="redacted" and not contract.get("breached",false):contract.fulfilled=true;contract.proof=c.command_id;contract.fulfilled_day=s.campaign.day
			if privacy=="unredacted":breach(s,"mo",c,content)
		return ""
	if c.kind=="select_route":
		if s.campaign.day!=23 or not routes(s).has(c.payload.get("route")):return "route_unavailable"
		s.full_campaign.route=c.payload.route
		return ""
	if c.kind=="review_record":
		var product=preload("res://scripts/domain/product_systems.gd")
		var ids: Variant=c.payload.get("records",[c.payload.get("evidence","")])
		var capacity: int=2 if product.tier(s,"communications")>=2 and int(s.campaign.day) in [20,22,23] else 1
		if not ids is Array or ids.is_empty() or ids.size()>capacity:return "invalid_target"
		var unique: Array=[]
		for id: Variant in ids:
			if not id is String or not content.domains.world.evidence.has(id) or unique.has(id):return "record_unavailable"
			if not content.domains.world.evidence[id].review_days.has(float(s.campaign.day)) and not (s.campaign.day==18 and product.tier(s,"communications")>=1):return "record_unavailable"
			if s.full_campaign.evidence.has(id):return "already_used"
			unique.append(id)
		if s.campaign.projects>=2:return "project_used"
		s.campaign.projects+=1
		for id: String in ids:s.full_campaign.evidence[id]={"source":"review","day":s.campaign.day,"revision":s.revision+1}
		verify(s,content)
		return ""
	return "unknown_command"
static func prepare(s: Dictionary,c: Dictionary) -> String:
	var amount: Variant=c.payload.get("medicine",0)
	if not (amount is int or amount is float) or amount!=int(amount) or amount<0 or amount>preload("res://scripts/domain/product_systems.gd").pack_limit(s) or amount>s.full_campaign.medicine_stock:return "insufficient_resources"
	s.full_campaign.medicine_stock-=int(amount);s.full_campaign.packed=int(amount)
	var support: String=str(c.payload.get("support",""))
	if not support.is_empty():
		if s.product.withdrawn.has(support) or not s.actors.has(support) or not Crew.joined(s,support) or s.actors[support].ready_day>s.campaign.day or s.actors[support].fatigue+8>100 or s.chapter_one.roster.has(support):return "invalid_support"
		s.actors[support].fatigue+=8
		if not s.chapter_one.worked.has(support):s.chapter_one.worked.append(support)
	var dispatch_error: String=preload("res://scripts/domain/field_operations.gd").prepare(s,c)
	if not dispatch_error.is_empty():return dispatch_error
	s.full_campaign.support=support
	return ""
static func settlement(s: Dictionary,content: Dictionary) -> void:
	var board: Dictionary=content.boards[s.battle.mission_id]
	var result: Dictionary=s.campaign.last_result
	s.full_campaign.medicine_stock+=int(s.battle.medicine);s.battle.medicine=0
	result.authored_work=[]
	for object: Dictionary in board.objectives:
		if object.kind=="work":result.authored_work.append({"id":object.id,"kind":"work","interaction_tags":object.interaction_tags.duplicate()})
	result.day=s.campaign.day;result.revision=s.revision+1
	result.roster=s.battle.heroes.keys();result.support=s.full_campaign.support
	result.all_extracted=true;result.standing=[];result.contributions={};result.rescues={}
	for h: Dictionary in s.battle.heroes.values():
		result.all_extracted=result.all_extracted and h.left
		if h.left and not h.downed:result.standing.append(h.id)
	for o: Dictionary in s.battle.objects.values():
		if o.completed and (not o.sustain_until_exit or o.hp>0):
			result.contributions[o.id]=o.contributors.duplicate()
			if o.kind=="rescue":result.rescues[o.id]=o.contributors.duplicate()
	result.protection=s.battle.protection.duplicate()
	result.promise=s.battle.get("retreat_promise",{}).duplicate(true)
	var evidence: Variant=board.get("evidence_receipt")
	if evidence is Dictionary:
		var secured: bool=true
		for id: String in evidence.requires:secured=secured and s.battle.objects.has(id) and s.battle.objects[id].completed
		if secured:s.full_campaign.evidence[evidence.id]={"source":board.id,"day":s.campaign.day,"revision":s.revision+1}
	if board.id=="M17" and s.battle.get("branch","")=="isolate":
		s.full_campaign.district_caps.floodgates=2
		if result.outcome=="success":s.campaign.districts.floodgates-=1
	for id: String in s.campaign.districts:s.campaign.districts[id]=mini(s.campaign.districts[id],s.full_campaign.district_caps[id])
	if board.kind=="main" and not s.full_campaign.support.is_empty():
		var old_xp: int=s.actors[s.full_campaign.support].xp
		s.actors[s.full_campaign.support].xp=mini(100,old_xp+2)
		result.xp_receipts[s.full_campaign.support]={"before":old_xp,"after":s.actors[s.full_campaign.support].xp,"source":"support"}
		if not s.operations.dispatch:
			s.inventory.supplies+=1;result.reward.supplies+=1;result.reward_rows.append({"reason":"后勤支援带回物资","resources":{"supplies":1}})
	s.campaign.settled[board.id]=result.duplicate(true)
	for node: Dictionary in content.domains.stories.community_nodes:
		if node.source==board.id:s.full_campaign.scene_delivery[node.id]={"source":board.id,"variant":result.outcome}
	if board.kind=="main" and int(s.campaign.day)%6==0:
		for node: Dictionary in content.domains.stories.chapter_nodes:
			if s.campaign.settled.has(node.source):s.full_campaign.scene_delivery[node.id]={"source":node.source,"secured":s.campaign.settled[node.source].facts.get(node.condition.objective,"") in ["saved","completed"]}
	for actor: String in s.product.withdrawn:
		if s.full_campaign.contracts.has(actor) and not s.full_campaign.contracts[actor].fulfilled and not s.full_campaign.contracts[actor].get("breached",false):s.full_campaign.contracts[actor].interrupted_by_injury=true
	verify(s,content)
	if board.id=="M24":
		s.full_campaign.ending=s.full_campaign.route if result.outcome=="success" else "evacuation"
		if s.full_campaign.ending.is_empty():s.full_campaign.ending="evacuation"
		s.chapter_one.finished=true
static func verify(s: Dictionary,content: Dictionary) -> void:
	for actor: String in s.full_campaign.contracts:
		var contract: Dictionary=s.full_campaign.contracts[actor]
		if contract.fulfilled or contract.get("breached",false) or contract.get("interrupted_by_injury",false):continue
		var matches: Array=[]
		for r: Dictionary in s.campaign.settled.values():
			if int(r.get("revision",0))>contract.created_revision:matches.append(r)
		var proof: String=""
		for r: Dictionary in matches:
			var main: bool=r.mission.begins_with("M")
			match actor:
				"lin":
					if main:
						for id: String in r.get("rescues",{}):
							if r.rescues[id].size()>=2:proof=r.mission+":"+id
				"xu":
					if main and r.get("standing",[]).has("xu") and r.get("promise",{}).get("kept",false):proof=r.mission
				"chen":
					if main and contract.paid==8 and s.full_campaign.known.get("chen_signed_responsibility",false):
						for id: String in r.get("contributions",{}):
							for o: Dictionary in content.boards[r.mission].objectives:
								if o.id==id and o.kind=="work" and o.interaction_tags.has("engineering") and r.contributions[id].has("chen"):proof=r.mission+":"+id
				"he":
					if r.get("all_extracted",false) and r.roster.has("he"):
						var rescue: bool=r.get("protection",[]).has("he");var other: bool=false
						for ids: Array in r.get("rescues",{}).values():rescue=rescue or ids.has("he")
						for ids: Array in r.get("contributions",{}).values():
							for id: String in ids:other=other or (id!="he" and s.actors.has(id))
						if rescue and other:proof=r.mission
				"mo":
					if r.mission=="M22" and r.facts.get("privacy")=="completed":proof="M22:privacy"
		if actor=="su":
			var mains: Array=[]
			for r: Dictionary in matches:
				if r.mission.begins_with("M"):mains.append(r)
			if mains.size()>=2 and mains[0].get("support","")!="su" and mains[1].get("support","")!="su" and (not mains[0].get("support","").is_empty() or not mains[1].get("support","").is_empty()):proof=mains[0].mission+"/"+mains[1].mission
		if actor=="ye" and s.full_campaign.evidence.has("E_MAINTENANCE") and s.full_campaign.known.get("maintenance_audit",false):proof="E_MAINTENANCE"
		if actor=="jiang" and s.campaign.day>=23 and contract.paid==6:proof="jiang_wages"
		if not proof.is_empty():contract.fulfilled=true;contract.proof=proof;contract.fulfilled_day=s.campaign.day

static func breach(s: Dictionary,actor: String,c: Dictionary,content: Dictionary) -> void:
	var contract: Dictionary=s.full_campaign.contracts[actor]
	if contract.get("breached",false):return
	contract.breached=true;contract.breach_id=c.command_id;contract.breach_day=s.campaign.day
	preload("res://scripts/domain/appraisal.gd").record(s,content,{"root":contract.node+":accepted-plan-breach","observers":[actor],"known":true,"shares":{"leader":1.0},"family":"breach","deliberate":true,"warned":true,"reason":"已接受的个人计划发生明确违约"})

static func after_action(s: Dictionary,c: Dictionary,content: Dictionary) -> void:
	if c.kind!="pickup" or not s.full_campaign.contracts.has("jiang"):return
	var object: Dictionary=s.battle.objects.get(c.payload.get("target",""),{})
	if object.get("kind","")!="cargo":return
	for other: Dictionary in s.battle.objects.values():
		if other.kind=="rescue" and not other.delivered and not other.lost:
			breach(s,"jiang",c,content);return
