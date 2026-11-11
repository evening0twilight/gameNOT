extends RefCounted
## Record the circumstances when a scene is read, so a later injury cannot rewrite it.
static func capture(s: Dictionary,node: Dictionary) -> Dictionary:
	var actors: Array=node.get("actors",[node.get("actor","")])
	var injured: Array=[];var absent: Array=[]
	for id: String in actors:
		if s.product.withdrawn.has(id):absent.append(id)
		elif s.actors[id].ready_day>s.campaign.day:injured.append(id)
	return {"mode":"letter" if not absent.is_empty() else ("recovery" if not injured.is_empty() else "present"),"day":s.campaign.day,"injured":injured,"absent":absent}
static func circumstances(s: Dictionary,node: Dictionary,record: Dictionary) -> Dictionary:
	if record.has("delivery"):return record.delivery
	# Legacy archives only recorded temporary injury. Do not rewrite a resolved scene.
	if not record.get("choice","").is_empty():return {"mode":"recovery" if record.get("injured",false) else "present","injured":[node.get("actor","")] if record.get("injured",false) else [],"absent":[],"day":record.get("day",1)}
	return capture(s,node)
static func valid(value: Variant,s: Dictionary) -> bool:
	if not value is Dictionary or value.get("mode") not in ["present","recovery","letter"]:return false
	if not (value.get("day") is int or value.get("day") is float) or value.day<1 or value.day>s.campaign.day:return false
	for key: String in ["injured","absent"]:
		if not value.get(key) is Array:return false
		for id: Variant in value[key]:
			if not id is String or not s.actors.has(id):return false
	return (value.mode=="letter")==not value.absent.is_empty()
