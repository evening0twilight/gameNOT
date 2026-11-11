extends RefCounted
const Crew=preload("res://scripts/domain/crew_journey.gd")
static func ensure(s: Dictionary) -> void:
	if not s.has("operations"):s.operations={"assets":{},"facilities":{},"assistance_day":0,"dispatch":false}
static func deploy(s: Dictionary,content: Dictionary) -> void:
	ensure(s)
	s.battle.exits=content.boards[s.battle.mission_id].exits.duplicate(true)
	if s.operations.dispatch:s.battle.exits=[[7,7]]
	s.battle.service={}
	if content.domains.field_operations.services.has(s.battle.mission_id):
		s.battle.service={"definition":content.domains.field_operations.services[s.battle.mission_id].duplicate(true),"ticks":0,"done":false,"failed":false,"watches":{},"steady":{},"contributors":[],"history":[],"shield":0,"reinforced":false}
static func exits(b: Dictionary,board: Dictionary) -> Array:return b.get("exits",board.exits)
static func power(b: Dictionary) -> bool:
	var f: Dictionary=b.get("service",{})
	if f.is_empty():return false
	for id: String in f.definition.linked_controls:
		if not b.objects[id].completed:return true
	return false
static func posts(b: Dictionary) -> Array:
	var f: Dictionary=b.get("service",{})
	if f.is_empty():return []
	if f.definition.mode=="sequence":return f.definition.stages[mini(f.ticks,f.definition.stages.size()-1)]
	return f.definition.posts
static func watch(s: Dictionary,c: Dictionary,rules: GDScript) -> String:
	var b: Dictionary=s.battle
	var f: Dictionary=b.get("service",{})
	if f.is_empty() or f.done or f.failed or b.round>f.definition.deadline:return "service_unavailable"
	var post: Variant=c.payload.get("post")
	if not (post is int or post is float) or post!=int(post) or post<0 or post>=posts(b).size():return "invalid_target"
	for id: String in f.definition.get("prerequisites",[]):
		if not b.objects[id].completed:return "prerequisite_required"
	if not power(b):return "power_required"
	if not b.heroes.has(c.actor_id):return "unavailable_actor"
	var h: Dictionary=b.heroes[c.actor_id]
	if h.left or h.downed or not h.carrying.is_empty():return "unavailable_actor"
	if not rules.same(h.cell,posts(b)[post]):return "invalid_target"
	if h.ap<1:return "insufficient_ap"
	if f.watches.has(str(post)):return "already_used"
	for w: Dictionary in f.watches.values():
		if w.actor==h.id:return "already_used"
	f.watches[str(post)]={"actor":h.id,"origin":h.cell.duplicate(),"interrupted":false}
	h.ap-=1
	return ""
static func on_hit(b: Dictionary,id: String,actual: int,source: String,rules: GDScript) -> void:
	var f: Dictionary=b.get("service",{})
	if f.is_empty():return
	for w: Dictionary in f.watches.values():
		if w.actor!=id:continue
		var marker: Dictionary=f.steady.get(id,{})
		var guard: Dictionary=b.heroes.get(marker.get("guard",""),{})
		var physical: bool=not marker.is_empty() and (guard.is_empty() and marker.get("guard","")=="" or not guard.is_empty() and not guard.left and not guard.downed and rules.same(guard.cell,marker.origin) and rules.distance(guard.cell,b.heroes[id].cell)==1)
		if actual>0:
			if source=="machine" and physical and not marker.used and not b.heroes[id].downed:marker.used=true
			else:w.interrupted=true
		if physical and not guard.is_empty() and source=="machine" and not f.contributors.has(guard.id):f.contributors.append(guard.id)
static func end_round(s: Dictionary,rules: GDScript) -> void:
	var b: Dictionary=s.battle
	var f: Dictionary=b.get("service",{})
	if f.is_empty():return
	var spec: Dictionary=f.definition
	if not f.done and not f.failed:
		var valid: bool=power(b) and f.watches.size()==posts(b).size()
		for w: Dictionary in f.watches.values():
			var h: Dictionary=b.heroes[w.actor]
			valid=valid and not h.left and not h.downed and not w.interrupted and rules.same(h.cell,w.origin)
		for marker: Dictionary in f.steady.values():
			if marker.guard!="":
				var guard: Dictionary=b.heroes[marker.guard]
				valid=valid and not guard.left and not guard.downed and rules.same(guard.cell,marker.origin)
		var previous: int=f.ticks
		if valid:
			f.ticks+=1
			for w: Dictionary in f.watches.values():
				if not f.contributors.has(w.actor):f.contributors.append(w.actor)
			if spec.mode=="accumulate":
				for cell: Array in spec.drain_stages[previous]:
					if rules.terrain(b,cell)=="~":rules.set_terrain(b,cell,".")
		elif spec.mode=="consecutive":f.ticks=0;f.contributors=[]
		f.history.append({"round":b.round,"valid":valid,"powered":power(b),"ticks":f.ticks,"operators":f.watches.values().map(func(w: Dictionary):return w.actor)})
		if f.ticks>=spec.consecutive_rounds:f.done=true
		elif b.round>=spec.deadline:f.failed=true
	if f.done and spec.has("extra_exit"):
		var ready: bool=true
		for id: String in spec.exit_requires:ready=ready and b.objects[id].completed
		if ready and not rules.contains_cell(b.exits,spec.extra_exit):b.exits.append(spec.extra_exit.duplicate())
	f.watches={};f.steady={}
static func restore(s: Dictionary,c: Dictionary,rules: GDScript) -> String:
	var b: Dictionary=s.battle
	var o: Dictionary=b.objects.get(c.payload.get("target",""),{})
	var h: Dictionary=b.heroes.get(c.actor_id,{})
	if o.is_empty() or h.is_empty() or not o.has("disables") or not o.completed or h.left or h.downed or not h.carrying.is_empty():return "invalid_target"
	if rules.distance(h.cell,o.cell)>1:return "invalid_target"
	if h.ap<1:return "insufficient_ap"
	o.completed=false;o.progress=0;b.enemies[o.disables].disabled=false;h.ap-=1
	rules.lock_intents(b)
	return ""
static func dispatch_ready(s: Dictionary,party: Array,support: String) -> bool:
	for other: String in ["jiang","mo"]:
		if not ((party.has("su") and support==other) or (party.has(other) and support=="su")):continue
		var eligible: bool=true
		for pair: String in ["su>"+other,other+">su"]:
			var r: Dictionary=s.social[pair]
			eligible=eligible and r.agreement=="cooperate" and r.contribution_missions.size()>=2 and r.band not in ["conditional","rupture"]
		var node: String="R04" if other=="jiang" else "R10"
		var scene: Dictionary=s.chapter_one.scenes.get(node,{})
		if eligible and scene.get("status","")=="resolved" and scene.get("choice","") in ["agreement"]:return true
	return false
static func prepare(s: Dictionary,c: Dictionary) -> String:
	ensure(s);s.operations.dispatch=false
	if not c.payload.get("dispatch",false):return ""
	if c.kind=="start_side":return "dispatch_unavailable"
	if not dispatch_ready(s,s.chapter_one.roster,str(c.payload.get("support",""))):return "dispatch_unavailable"
	if s.inventory.supplies<2:return "insufficient_resources"
	s.inventory.supplies-=2;s.operations.dispatch=true
	return ""
static func settled(s: Dictionary,content: Dictionary) -> void:
	ensure(s)
	var id: String=s.battle.mission_id
	var registry: Dictionary=content.domains.field_operations.asset_registry
	if registry.has(id):
		var intact: bool=s.battle.enemies[registry[id].source_enemy].hp>0
		s.operations.assets[id]={"intact":intact,"day":s.campaign.day,"service_done":s.battle.get("service",{}).get("done",false),"history":s.battle.get("service",{}).get("history",[]).duplicate(true)}
		if content.domains.field_operations.investments.has(id):
			var qualified: bool=intact and s.campaign.last_result.outcome=="success"
			s.operations.facilities[id]={"qualified":qualified,"repaired":false,"available_day":s.campaign.day+1,"used":0,"receipts":[]}
	var service: Dictionary=s.battle.get("service",{})
	if not service.is_empty():s.campaign.last_result.field_service={"done":service.done,"ticks":service.ticks,"failed":service.failed,"history":service.history.duplicate(true),"contributors":service.contributors.duplicate()}
static func camp(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	ensure(s)
	var id: String=str(c.payload.get("facility",""))
	if not s.operations.facilities.has(id):return "facility_unavailable"
	var f: Dictionary=s.operations.facilities[id]
	var spec: Dictionary=content.domains.field_operations.investments[id]
	if c.kind=="repair_field_facility":
		if f.qualified:return "already_used"
		if s.campaign.projects>=2:return "project_used"
		if s.inventory.supplies<2:return "insufficient_resources"
		s.inventory.supplies-=2;s.campaign.projects+=1;f.qualified=true;f.repaired=true;f.available_day=s.campaign.day+1
		return ""
	if not f.qualified or s.campaign.day<f.available_day or s.campaign.day<spec.first_day or s.campaign.day>spec.last_day or f.used>=2 or s.operations.assistance_day==s.campaign.day:return "facility_unavailable"
	var ids: Variant=c.payload.get("participants",[])
	if not ids is Array or ids.is_empty() or ids.size()>2:return "invalid_target"
	var seen: Array=[];var receipt: Dictionary={"day":s.campaign.day,"actors":{}}
	for actor: Variant in ids:
		if not actor is String or not Crew.joined(s,actor) or seen.has(actor) or s.product.withdrawn.has(actor) or s.actors[actor].ready_day>s.campaign.day:return "unavailable_actor"
		seen.append(actor)
	for actor: String in ids:
		var a: Dictionary=s.actors[actor]
		var fatigue: int=mini(a.fatigue,16 if s.product.facilities.rest_area>=1 else 12)
		var stress: int=mini(a.stress,16)
		a.fatigue-=fatigue;a.stress-=stress;receipt.actors[actor]={"fatigue":fatigue,"stress":stress}
	f.receipts.append(receipt);f.used+=1;s.operations.assistance_day=s.campaign.day
	return ""
