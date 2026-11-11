extends RefCounted
static func number(value: Variant,minimum: float=0,maximum: float=10000000) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and value>=minimum and value<=maximum
static func valid(s: Dictionary,content: Dictionary) -> bool:
	var o: Variant=s.get("operations")
	if not o is Dictionary or not o.get("assets") is Dictionary or not o.get("facilities") is Dictionary or not number(o.get("assistance_day"),0,24) or not o.get("dispatch") is bool:return false
	for id: String in o.assets:
		var a: Variant=o.assets[id]
		if not content.domains.field_operations.asset_registry.has(id) or not a is Dictionary or not a.get("intact") is bool or not a.get("service_done") is bool or not a.get("history") is Array or not number(a.get("day"),1,24):return false
	for id: String in o.facilities:
		var f: Variant=o.facilities[id]
		if not content.domains.field_operations.investments.has(id) or not f is Dictionary or not f.get("qualified") is bool or not f.get("repaired") is bool or not number(f.get("used"),0,2) or not number(f.get("available_day"),1,25) or not f.get("receipts") is Array:return false
	for r: Variant in s.social.values():
		if not relation(r,s):return false
	var b: Dictionary=s.battle
	for mark: Variant in b.get("safety",[]):
		if not mark is Dictionary or not b.heroes.has(mark.get("actor")) or not b.heroes.has(mark.get("target")) or mark.get("protocol") not in ["protected_work","mutual_cover"] or not number(mark.get("round"),1,b.limit) or not preload("res://scripts/infrastructure/content_catalog.gd").cell_valid(mark.get("origin")):return false
	if not b.get("exits") is Array or b.exits.is_empty() or not b.get("service") is Dictionary:return false
	for cell: Variant in b.exits:
		if not preload("res://scripts/infrastructure/content_catalog.gd").cell_valid(cell):return false
	if not b.service.is_empty():
		var f: Dictionary=b.service
		if not content.domains.field_operations.services.has(b.mission_id) or f.get("definition")!=content.domains.field_operations.services[b.mission_id]:return false
		for key: String in ["done","failed","reinforced"]:
			if not f.get(key) is bool:return false
		for key: String in ["watches","steady"]:
			if not f.get(key) is Dictionary:return false
		if not f.get("history") is Array or not f.get("contributors") is Array or not number(f.get("ticks"),0,2) or not number(f.get("shield"),0,6):return false
		for id: Variant in f.contributors:
			if not b.heroes.has(id):return false
		for w: Variant in f.watches.values():
			if not w is Dictionary or not b.heroes.has(w.get("actor")) or not w.get("interrupted") is bool or not preload("res://scripts/infrastructure/content_catalog.gd").cell_valid(w.get("origin")):return false
		for m: Variant in f.steady.values():
			if not m is Dictionary or not m.get("used") is bool or not m.get("guard") is String or not m.get("origin") is Array:return false
			if m.guard!="" and (not b.heroes.has(m.guard) or not preload("res://scripts/infrastructure/content_catalog.gd").cell_valid(m.origin)):return false
	var a: Variant=s.get("appraisal")
	if not a is Dictionary:return false
	for field: String in ["events","support_days","self_bands","provisional","positive","relief"]:
		if not a.get(field) is Dictionary:return false
	for field: String in ["personal_missions","conflicts","scene_missions"]:
		if not a.get(field) is Array:return false
	for e: Variant in a.events.values():
		if not e is Dictionary or not e.get("root") is String or not s.actors.has(e.get("observer")) or not e.get("family") is String or not e.get("reason") is String or not content.boards.has(e.get("mission")) or not number(e.get("day"),1,24) or not e.get("shares") is Dictionary or not e.get("directions") is Dictionary:return false
		for key: String in ["first_known_day","occurrence_day"]:
			if e.has(key) and not number(e[key],1,24):return false
		var total: float=0
		for target: String in e.shares:
			if not s.social.has(e.observer+">"+target) or not number(e.shares[target],0,1):return false
			total+=e.shares[target]
		if total>1.000001:return false
		for d: Variant in e.directions.values():
			if not d is Dictionary or not relation(d.get("base"),s) or not number(d.get("amplitude"),0,100) or not number(d.get("loss"),0,100) or not number(d.get("stress"),0,100):return false
	for field: String in ["personal_missions","scene_missions"]:
		for mission: Variant in a[field]:
			if not mission is String or not content.boards.has(mission):return false
	for id: String in a.support_days:
		if not s.actors.has(id) or not number(a.support_days[id],1,24):return false
	for id: String in a.self_bands:
		if not s.actors.has(id) or not number(a.self_bands[id],0,2) or a.self_bands[id]!=int(a.self_bands[id]):return false
	for value: Variant in a.relief.values():
		if not number(value,0,6):return false
	for value: Variant in a.positive.values():
		if value is Dictionary:
			if not number(value.get("gain"),0,3) or not value.get("object") is String or not value.get("witness") is String or not s.social.has(value.get("pair")):return false
		elif not number(value,0,3):return false
	for id: String in s.actors:
		if not number(s.actors[id].self_load,0,100) or not number(s.actors[id].stress,0,100):return false
	for p: Variant in a.provisional.values():
		if not p is Dictionary or not s.actors.has(p.get("observer")) or not p.get("root") is String or not p.get("target") is String or not content.boards.has(p.get("mission")) or not number(p.get("day"),1,24) or not p.get("reason") is String or p.get("status") not in ["unverified","verified","disproved"] or not number(p.get("strength"),0,4):return false
	for c: Variant in a.conflicts:
		if not c is Dictionary or not s.social.has(c.get("pair")) or not c.get("reason") is String or not c.get("event") is String or not content.boards.has(c.get("mission")) or not number(c.get("day"),1,24) or not c.get("long_scene") is bool or c.get("status") not in ["pending","acknowledged","scheduled","professional","repaired"]:return false
	return true

static func relation(r: Variant,s: Dictionary) -> bool:
	if not r is Dictionary or not s.actors.has(r.get("observer")) or (r.get("target")!="leader" and not s.actors.has(r.get("target"))):return false
	for field: String in ["grudge","trust","closeness"]:
		if not number(r.get(field),0,100):return false
	if r.get("band") not in ["calm","guarded","conditional","rupture"] or not number(r.get("history_stage"),0,3) or not number(r.get("cooldown_until_day"),-1,26) or not r.get("last_rupture_mission") is String:return false
	for field: String in ["seen_events","repair_tokens","contribution_missions","grudge_categories"]:
		if not r.get(field) is Array:return false
		for value: Variant in r[field]:
			if not value is String:return false
	if not r.get("memories") is Array:return false
	for m: Variant in r.memories:
		if not m is Dictionary:return false
		for field: String in ["id","category","remedy"]:
			if not m.get(field) is String:return false
		if not number(m.get("amplitude"),0,40) or not number(m.get("actual_trust_loss"),0,100) or not number(m.get("day"),1,24) or not number(m.get("stage"),0,2) or m.stage!=int(m.stage) or not number(m.get("half_life"),.01,100) or not number(m.get("floor"),0,1) or not m.get("serious") is bool:return false
		if m.has("refunded") and not number(m.refunded,0,m.actual_trust_loss):return false
	return true
