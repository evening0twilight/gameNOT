extends RefCounted
## A read-only timeline of an already committed command. Never advances gameplay.
const Rules=preload("res://scripts/domain/campaign_rules.gd")
static func build(before: Dictionary,after: Dictionary,command: Dictionary,pathfinder: Callable) -> Dictionary:
	if before.campaign.phase!="battle" or before.battle.mission_id!=after.battle.mission_id or command.kind=="undo":return {}
	var kind: String=command.kind
	var actor: String=command.actor_id
	var a: Dictionary=before.battle
	var b: Dictionary=after.battle
	var plan: Dictionary={"kind":kind,"actor":actor,"target":command.payload.get("target",""),"duration":.85,"impact":.34,"paths":{},"events":[],"machines":[],"before":a.duplicate(true)}
	for id: String in b.heroes:
		if not a.heroes.has(id):continue
		if not Rules.same(a.heroes[id].cell,b.heroes[id].cell):
			var path: Array=pathfinder.call(a,a.heroes[id].cell,b.heroes[id].cell)
			if path.size()<2:path=[a.heroes[id].cell,b.heroes[id].cell]
			plan.paths[id]=path
	if kind in ["move","cross_anchor"] or (kind=="specialty" and not plan.paths.is_empty()):
		var steps: int=1
		for path: Array in plan.paths.values():steps=maxi(steps,path.size()-1)
		plan.duration=maxf(.48,steps*.22+.12);plan.impact=plan.duration-.1
		for step: int in range(steps):plan.events.append({"at":.08+step*.22,"sound":"move"})
	elif kind=="end_round":
		plan.events.append({"at":0.0,"sound":"end_round"})
		var at: float=.25
		for id: String in a.enemies:
			var enemy: Dictionary=a.enemies[id]
			if enemy.hp<=0 or enemy.disabled or enemy.get("paused_round",0)==a.round:continue
			var cells: Array=Rules.Hazards.footprint(a,enemy,Rules)
			if cells.is_empty() and Rules.same(enemy.cell,b.enemies.get(id,enemy).cell):continue
			plan.machines.append({"id":id,"at":at,"cells":cells})
			plan.events.append({"at":at+.18,"sound":"machine_"+enemy.type})
			at+=.52
		plan.impact=at;plan.duration=at+.65
	else:
		plan.events.append({"at":plan.impact,"sound":{"attack":"attack","push":"push","stabilize":"stabilize","pickup":"pickup","service_watch":"work","restore_power":"work","interact":"work","drop":"drop","extract":"extract","leave_site":"extract","use_tool":"work","protocol":"work","specialty":"work"}.get(kind,"ui_confirm")})
	for id: String in b.heroes:
		if a.heroes.has(id) and b.heroes[id].hp<a.heroes[id].hp:
			plan.events.append({"at":plan.impact,"sound":"injury"});break
	if after.campaign.phase!="battle":
		plan.events.append({"at":plan.duration-.15,"sound":"ending" if after.chapter_one.finished else "objective"})
	plan.events.sort_custom(func(x: Dictionary,y: Dictionary):return x.at<y.at)
	return plan
static func progress(plan: Dictionary,seconds: float) -> float:
	return clampf(seconds/maxf(.01,float(plan.get("duration",.85))-.12),0,1)
static func step_position(path: Array,t: float) -> Vector2:
	if path.is_empty():return Vector2.ZERO
	if path.size()==1:return Vector2(path[0][0],path[0][1])
	var segment: float=clampf(t,0,1)*(path.size()-1)
	var index: int=mini(floori(segment),path.size()-2)
	return Vector2(path[index][0],path[index][1]).lerp(Vector2(path[index+1][0],path[index+1][1]),segment-index)
static func direction(path: Array,t: float) -> Vector2:
	if path.size()<2:return Vector2.RIGHT
	var index: int=mini(floori(clampf(t,0,1)*(path.size()-1)),path.size()-2)
	return Vector2(path[index+1][0]-path[index][0],path[index+1][1]-path[index][1]).normalized()
