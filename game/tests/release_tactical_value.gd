extends RefCounted
## Legal alternative previews fork a real guided state. The primary campaign never receives their rewards.
const Rules=preload("res://scripts/domain/campaign_rules.gd")

static func branch(s: Dictionary,content: Dictionary,kind: String,actor: String,payload: Dictionary={}) -> Dictionary:
	var cmd: Dictionary={"command_id":"value-%d-%s"%[s.revision,kind],"root_decision_id":"value","expected_revision":s.revision,"kind":kind,"actor_id":actor,"payload":payload}
	var result: Dictionary=Rules.reduce(s,cmd,content)
	return result.next_state if result.ok else {}

static func inspect(s: Dictionary,c: Dictionary,actor: String,out: Dictionary) -> void:
	if out.has(actor) or not s.actors.has(actor):return
	var h: Dictionary=s.battle.heroes[actor]
	if h.left or h.downed or h.ap<=0:return
	var b: Dictionary=s.battle
	var probe: Dictionary={}
	if actor in ["lin","mo"]:
		for o: Dictionary in b.objects.values():
			var distance: int=Rules.distance(h.cell,o.cell)
			if distance<=1:continue
			if actor=="lin" and (o.kind!="rescue" or o.stable):continue
			if actor=="mo" and (not o.get("interaction_tags",[]).has("machine_shutdown") or o.completed):continue
			var payload: Dictionary={"ability":actor+"_1","target":o.id}
			var advance: Dictionary=branch(s,c,"specialty",actor,payload)
			if advance.is_empty():continue
			var direct: Dictionary=branch(s,c,"stabilize" if actor=="lin" else "interact",actor,{"target":o.id})
			if not direct.is_empty():continue
			var after: Dictionary=advance.battle.objects[o.id]
			probe={"ability":payload.ability,"target":o.id,"distance":distance,"ordinary_from_same_tile":false,"ap_spent":int(h.ap)-int(advance.battle.heroes[actor].ap),"before":o.stable if actor=="lin" else o.progress,"after":after.stable if actor=="lin" else after.progress}
			break
	elif actor=="xu":
		for p: Dictionary in Rules.FieldLearning.payloads(s,c,"xu","ability:xu_1"):
			if Rules.move_cost(b,h.cell,p.cell,Rules.movement_budget(s,"xu"))>=0:continue
			var advance: Dictionary=branch(s,c,"specialty",actor,p)
			if advance.is_empty():continue
			var useful: String=""
			for group: Array in Rules.Full.groups(s,c.boards[b.mission_id]):
				for id: String in group:
					var o: Dictionary=b.objects[id]
					if not o.completed and not o.lost and Rules.distance(advance.battle.heroes.xu.cell,o.cell)<Rules.distance(h.cell,o.cell):useful=id
			if useful.is_empty():continue
			probe={"ability":"xu_1","origin":h.cell,"destination":p.cell,"toward_required":useful,"ordinary_one_ap_move":false,"ap_spent":int(h.ap)-int(advance.battle.heroes.xu.ap)}
			break
	elif actor=="su":
		for e: Dictionary in b.enemies.values():
			if e.hp<3 or e.disabled or Rules.distance(h.cell,e.cell)<=1 or Rules.distance(h.cell,e.cell)>4:continue
			for ally: Dictionary in b.heroes.values():
				if ally.id=="su" or Rules.distance(ally.cell,e.cell)!=1:continue
				var ordinary: Dictionary=branch(s,c,"attack",ally.id,{"target":e.id})
				if ordinary.is_empty():continue
				var marked: Dictionary=branch(s,c,"specialty","su",{"ability":"su_1","target":e.id})
				if marked.is_empty():continue
				var combined: Dictionary=branch(marked,c,"attack",ally.id,{"target":e.id})
				if combined.is_empty() or combined.battle.enemies[e.id].hp>=ordinary.battle.enemies[e.id].hp:continue
				probe={"ability":"su_1","target":e.id,"striker":ally.id,"striker_ap_spent":1,"additional_su_ap":1,"ordinary_hp":ordinary.battle.enemies[e.id].hp,"marked_hp":combined.battle.enemies[e.id].hp,"su_distance":Rules.distance(h.cell,e.cell)}
				break
			if not probe.is_empty():break
	elif actor in ["chen","ye","he"]:
		var skill: String=actor+"_1"
		for p: Dictionary in Rules.FieldLearning.payloads(s,c,actor,"ability:"+skill):
			var use: Dictionary=branch(s,c,"specialty",actor,p)
			if use.is_empty():continue
			var control: Dictionary=branch(s,c,"wait",actor)
			if control.is_empty():continue
			if actor=="ye":
				control=branch(control,c,"wait",actor)
				if control.is_empty():continue
			var advanced: Dictionary=branch(use,c,"end_round",actor)
			var ordinary: Dictionary=branch(control,c,"end_round",actor)
			if advanced.is_empty() or ordinary.is_empty():continue
			for category: String in ["heroes","objects"]:
				for id: String in advanced.battle[category]:
					var after: int=advanced.battle[category][id].get("hp",0)
					if not ordinary.battle[category].has(id):continue
					var other: int=ordinary.battle[category][id].get("hp",0)
					if after>other:
						probe={"ability":skill,"payload":p,"saved":id,"ordinary_hp":other,"specialty_hp":after,"same_ap":int(h.ap)-int(use.battle.heroes[actor].ap),"same_round_resolution":true}
						break
				if not probe.is_empty():break
			if not probe.is_empty():break
	elif actor=="jiang" and not h.carrying.is_empty():
		for ally: Dictionary in b.heroes.values():
			if ally.id==actor or not ally.carrying.is_empty() or Rules.distance(h.cell,ally.cell)<2:continue
			var pass_to: Dictionary=branch(s,c,"specialty",actor,{"ability":"jiang_1","target":ally.id,"consent":true})
			if pass_to.is_empty():continue
			var dropped: Dictionary=branch(s,c,"drop",actor)
			if dropped.is_empty():continue
			probe={"ability":"jiang_1","cargo":h.carrying,"distance":Rules.distance(h.cell,ally.cell),"specialty_carrier":pass_to.battle.objects[h.carrying].carrier,"after_ordinary_drop":dropped.battle.objects[h.carrying].carrier,"receiver_ap_unchanged":ally.ap==pass_to.battle.heroes[ally.id].ap}
			break
	if not probe.is_empty():
		probe.merge({"actor":actor,"day":s.campaign.day,"mission":b.mission_id,"round":b.round,"revision":s.revision,"xp":s.actors[actor].xp,"level":Rules.Specialties.level(s.actors[actor].xp),"acquired":s.journey.recruited[actor].duplicate()})
		out[actor]=probe
