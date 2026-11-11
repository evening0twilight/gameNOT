extends RefCounted
static func apply(s: Dictionary,c: Dictionary,rules: Script) -> String:
	var b: Dictionary=s.battle
	var p: Dictionary=c.payload
	var partner: String=str(p.get("partner",""))
	if partner==c.actor_id or not b.heroes.has(c.actor_id) or not b.heroes.has(partner):return "invalid_target"
	var a: Dictionary=b.heroes[c.actor_id]
	var other: Dictionary=b.heroes[partner]
	if a.left or a.downed or other.left or other.downed:return "unavailable_actor"
	if a.ap<1 or other.ap<1:return "insufficient_ap"
	var kind: String=str(p.get("protocol",""))
	var pair: Array=[a.id,other.id];pair.sort()
	var key: String=kind+":"+":".join(pair)
	if b.round_markers.has(key):return "already_used"
	if not p.get("consent",false):return "consent_required"
	var safeguard: String=conditions(s,c,rules)
	if not safeguard.is_empty():return safeguard
	match kind:
		"relay_carry":
			if rules.distance(a.cell,other.cell)!=1 or a.carrying.is_empty() or not other.carrying.is_empty():return "invalid_target"
			if not preload("res://scripts/domain/p1_specialties.gd").valid_cell(p.get("cell")):return "invalid_target"
			if rules.move_cost(b,other.cell,p.cell,3)<0:return "invalid_target"
			# The selected, consenting receiver is the factual named-receiver safeguard.
			var object: Dictionary=b.objects[a.carrying]
			other.carrying=a.carrying
			a.carrying=""
			object.carrier=other.id
			rules.record_transport(object,other.id,other.cell,p.cell)
			other.cell=p.cell.duplicate()
		"coordinated_pull":
			var enemy: Dictionary=b.enemies.get(str(p.get("target","")),{})
			var cell: Variant=p.get("cell")
			if enemy.is_empty() or enemy.hp<=0 or enemy.type not in ["hauler","sentinel"] or not rules.Product.valid_cell(cell):return "invalid_target"
			if not a.carrying.is_empty() or not other.carrying.is_empty() or rules.distance(a.cell,enemy.cell)!=1 or rules.distance(other.cell,enemy.cell)!=1:return "invalid_target"
			if rules.distance(enemy.cell,cell)!=1 or rules.blocked(b,cell) or rules.occupied(b,cell) or b.barriers.has(str(cell)):return "invalid_target"
			enemy.cell=cell.duplicate();enemy.erase("push_marker")
			if enemy.type=="hauler":enemy.off_rail=not rules.contains_cell(enemy.rail,cell)
		"protected_work":
			if p.has("post"):
				if rules.distance(a.cell,other.cell)!=1 or not other.carrying.is_empty():return "invalid_target"
				var error: String=rules.Field.watch(s,c,rules)
				if not error.is_empty():return error
				other.ap-=1;b.cover[a.id]=2
				b.service.steady[a.id]={"guard":other.id,"origin":other.cell.duplicate(),"used":false}
				b.round_markers[key]=true;return ""
			if not a.carrying.is_empty() or not other.carrying.is_empty() or rules.distance(a.cell,other.cell)!=1:return "invalid_target"
			var object: Dictionary=b.objects.get(str(p.get("target","")),{})
			if object.is_empty() or object.kind!="work" or object.completed or object.lost or rules.distance(a.cell,object.cell)>1:return "invalid_target"
			for prerequisite: String in object.prerequisites:
				if not b.objects[prerequisite].completed:return "prerequisite_required"
			var protector: String=safety_actor(b,a,other,rules)
			for observer: String in [a.id,other.id]:
				for responsible: String in [other.id if observer==a.id else a.id,"leader"]:
					var r: Dictionary=s.social.get(observer+">"+responsible,{})
					if observer=="lin" and r.get("band","") in ["conditional","rupture"] and object.get("risk_context",[]).has("fall") and protector.is_empty() and not anchored(b,b.heroes[observer],rules):return "relationship_safeguard_required"
			if b.mission_id=="M17" and object.has("branch"):
				if not b.branch.is_empty() and b.branch!=object.branch:return "branch_locked"
				b.branch=object.branch
			for observer: String in [a.id,other.id]:
				for responsible: String in [other.id if observer==a.id else a.id,"leader"]:
					var relation: Dictionary=s.social.get(observer+">"+responsible,{})
					if relation.get("band","") not in ["conditional","rupture"]:continue
					if observer in ["chen","ye"] and object.get("risk_context",[]).has("electrical"):
						var insulated: bool=rules.contains_cell(b.insulation,b.heroes[observer].cell)
						var power_off: bool=object.has("disables") and b.enemies[object.disables].disabled
						if not power_off and not (insulated and (observer=="ye" or int(object.get("shield",0))>0)):return "relationship_safeguard_required"
			if not protector.is_empty():
				if not object.contributors.has(protector):object.contributors.append(protector)
				b.safety=b.safety.filter(func(mark):return mark.actor!=protector)
			object.progress=mini(int(object.work),int(object.progress)+3)
			object.completed=object.progress>=object.work
			for id: String in [a.id,other.id]:
				if not object.contributors.has(id):object.contributors.append(id)
			if object.completed and object.has("disables"):rules.shutdown(b,object.disables)
			b.cover[a.id]=2
		"mutual_cover":
			if rules.distance(a.cell,other.cell)>2 or not a.carrying.is_empty() or not other.carrying.is_empty():return "invalid_target"
			b.cover[a.id]=2;b.cover[other.id]=2
			var protector: String=safety_actor(b,a,other,rules,kind)
			if not protector.is_empty():
				b.safety=b.safety.filter(func(mark):return mark.actor!=protector)
				if not b.protection.has(protector):b.protection.append(protector)
			if not b.get("service",{}).is_empty():
				for w: Dictionary in b.service.watches.values():
					if w.actor in [a.id,other.id]:b.service.steady[w.actor]={"guard":"","origin":[],"used":false}
		_:return "invalid_target"
	a.ap-=1;other.ap-=1
	b.round_markers[key]=true
	return ""

static func anchored(b: Dictionary,hero: Dictionary,rules: Script) -> bool:
	for anchor: Dictionary in b.deployed_tools.values():
		if anchor.get("kind")=="winch" and (rules.distance(hero.cell,anchor.cell)<=1 or rules.distance(hero.cell,anchor.other)<=1):return true
	return false
static func safety_actor(b: Dictionary,a: Dictionary,other: Dictionary,rules: Script,kind: String="protected_work") -> String:
	for mark: Dictionary in b.get("safety",[]):
		if mark.actor in [a.id,other.id] or not mark.target in [a.id,other.id] or mark.round!=b.round or mark.protocol!=kind:continue
		var hero: Dictionary=b.heroes.get(mark.actor,{})
		if not hero.is_empty() and not hero.left and not hero.downed and rules.same(hero.cell,mark.origin) and rules.distance(hero.cell,b.heroes[mark.target].cell)==1:return mark.actor
	return ""

static func conditions(s: Dictionary,c: Dictionary,rules: Script) -> String:
	var b: Dictionary=s.battle
	var a: Dictionary=b.heroes[c.actor_id]
	var other: Dictionary=b.heroes[str(c.payload.get("partner",""))]
	var kind: String=str(c.payload.get("protocol",""))
	var object: Dictionary=b.objects.get(c.payload.get("target",""),{})
	var context: Array=object.get("risk_context",[]).duplicate()
	var electrical_live: bool=false
	var nearby_shield: int=0
	if kind=="mutual_cover":
		for candidate: Dictionary in b.objects.values():
			if mini(rules.distance(a.cell,candidate.cell),rules.distance(other.cell,candidate.cell))<=1:
				if candidate.get("risk_context",[]).has("electrical"):
					electrical_live=electrical_live or not (candidate.has("disables") and b.enemies[candidate.disables].disabled)
					nearby_shield=maxi(nearby_shield,int(candidate.get("shield",0)))
				for risk: String in candidate.get("risk_context",[]):
					if not context.has(risk):context.append(risk)
	if c.payload.has("post") and not b.get("service",{}).is_empty():
		if b.enemies[b.service.definition.source_enemy].type=="skimmer":context.append("electrical")
		if b.mission_id in ["M10","M21"]:context.append("fall")
	for observer: String in [a.id,other.id]:
		var restricted: bool=false
		for responsible: String in [other.id if observer==a.id else a.id,"leader"]:restricted=restricted or s.social.get(observer+">"+responsible,{}).get("band","") in ["conditional","rupture"]
		if not restricted:continue
		var h: Dictionary=b.heroes[observer]
		if observer=="lin" and kind in ["protected_work","mutual_cover"] and context.has("fall") and not anchored(b,h,rules) and safety_actor(b,a,other,rules,kind).is_empty():return "relationship_safeguard_required"
		if observer=="xu" and kind=="coordinated_pull" and not b.authorizations.has(observer):return "relationship_safeguard_required"
		if observer in ["chen","ye"] and kind in ["protected_work","mutual_cover"] and context.has("electrical"):
			var live: bool=rules.Field.power(b) if c.payload.has("post") else not (object.has("disables") and b.enemies[object.disables].disabled)
			var shield: int=b.service.shield if c.payload.has("post") else int(object.get("shield",0))
			if kind=="mutual_cover":live=electrical_live;shield=nearby_shield
			if live and (not rules.contains_cell(b.insulation,a.cell) or not rules.contains_cell(b.insulation,other.cell) or (observer=="chen" and shield<3)):return "relationship_safeguard_required"
		if observer=="he" and kind in ["protected_work","mutual_cover"]:
			var reachable: bool=false
			for cell: Array in b.get("exits",[]):
				if rules.same(h.cell,cell) or rules.move_cost(b,h.cell,cell,64)>=0:reachable=true
			if not reachable or b.limit<=0:return "relationship_safeguard_required"
		if observer=="jiang" and kind=="relay_carry" and b.get("handoff_priority","") not in ["people","cargo"]:return "relationship_safeguard_required"
	return ""
