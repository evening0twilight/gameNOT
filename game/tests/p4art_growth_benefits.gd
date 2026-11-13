extends "res://tests/p4close_growth_campaign.gd"
var comparisons: Array=[]
func run() -> void:
	output_prefix="p4art-benefits"
	super.run()
func preview_action(snapshot: Dictionary,kind: String,actor: String) -> Dictionary:
	return Rules.reduce(snapshot,{"command_id":"benefit-%d-%d"%[snapshot.revision,comparisons.size()],"root_decision_id":"benefit-review","expected_revision":snapshot.revision,"kind":kind,"actor_id":actor,"payload":{}},content)
func has_benefit(snapshot: Dictionary,payload: Dictionary,actor: String) -> bool:
	var command: Dictionary={"command_id":"benefit-candidate","root_decision_id":"benefit-review","expected_revision":snapshot.revision,"kind":"specialty","actor_id":actor,"payload":payload}
	var with_action: Dictionary=Rules.reduce(snapshot,command,content)
	if not with_action.ok:return false
	var alternative: Dictionary=preview_action(snapshot,"wait",actor)
	if not alternative.ok:return false
	var left: Dictionary=with_action.next_state;var right: Dictionary=alternative.next_state
	for step: int in range(2):
		if left.campaign.phase!="battle" or right.campaign.phase!="battle":return false
		var a: Dictionary=preview_action(left,"end_round",actor);var b: Dictionary=preview_action(right,"end_round",actor)
		if not a.ok or not b.ok:return false
		left=a.next_state;right=b.next_state
		for group: String in ["heroes","objects"]:
			for id: String in left.battle[group]:
				if right.battle[group].has(id) and left.battle[group][id].get("hp",0)>right.battle[group][id].get("hp",0):return true
	return false
func tick(actor: String,goal: String,board: Dictionary) -> bool:
	if actor==focus and actor=="chen" and Rules.Specialties.level(s.actors[actor].xp)>=3 and s.battle.heroes[actor].ap>0:
		for object: Dictionary in s.battle.objects.values():
			if object.kind=="work" and observe(actor,{"ability":"chen_3","target":object.id},"protected a live device against forecast damage; compared with a legal equal-AP wait"):return true
	return super.tick(actor,goal,board)
func observe(actor: String,payload: Dictionary,reason: String) -> bool:
	if payload.ability in ["chen_3","he_1","mo_3"]:
		var key: String=focus+":"+payload.ability+":"+str(Rules.Specialties.level(s.actors[actor].xp))
		if advanced.has(key) or not has_benefit(s,payload,actor):return false
	var before: Dictionary=s.duplicate(true)
	var accepted: bool=super.observe(actor,payload,reason)
	if not accepted or payload.ability not in ["chen_3","he_1","mo_3"]:return accepted
	# Compare a legal wait using the same AP against the real ability decision; never remove protection from a state by hand.
	var ordinary: Dictionary=preview_action(before,"wait",actor)
	if not ordinary.ok:return accepted
	var with_ability: Dictionary=s.duplicate(true)
	var without_ability: Dictionary=ordinary.next_state
	var rounds: Array=[]
	for step: int in range(2):
		if with_ability.campaign.phase!="battle" or without_ability.campaign.phase!="battle":break
		var left: Dictionary=preview_action(with_ability,"end_round",actor)
		var right: Dictionary=preview_action(without_ability,"end_round",actor)
		if not left.ok or not right.ok:break
		with_ability=left.next_state;without_ability=right.next_state
		var saved: Array=[]
		for group: String in ["heroes","objects"]:
			for id: String in with_ability.battle[group]:
				if not without_ability.battle[group].has(id):continue
				var a: Dictionary=with_ability.battle[group][id];var b: Dictionary=without_ability.battle[group][id]
				if a.get("hp",0)>b.get("hp",0):saved.append({"group":group,"id":id,"hp_with":a.hp,"hp_without":b.hp})
		rounds.append({"round":with_ability.battle.round,"damage_prevented":saved,"intents_with":with_ability.battle.intents.duplicate(true),"intents_without":without_ability.battle.intents.duplicate(true)})
	comparisons.append({"actor":actor,"ability":payload.ability,"xp":before.actors[actor].xp,"day":before.campaign.day,"mission":before.battle.mission_id,"payload":payload,"actual_campaign_snapshot_revision":before.revision,"alternative":"legal wait, equal AP; then identical end_round commands on both branches","rounds":rounds})
	var file:=FileAccess.open("res://../outputs/p4art-growth-benefits"+focused+".json",FileAccess.WRITE);file.store_string(JSON.stringify({"comparisons":comparisons,"scope":"Counterfactual legal command branches from a real continuous progression route; not a human balance verdict"},"\t"));file.close()
	return accepted
