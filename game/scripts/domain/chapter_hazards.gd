extends RefCounted
## Shared telegraph geometry for rules and presentation, all six authored machine types.
static func definition(content: Dictionary,id: String) -> Dictionary:
	for entry: Dictionary in content.domains.enemies:
		if entry.id==id:return entry
	return {}
static func water_region(b: Dictionary,start: Array,rules: GDScript) -> Array:
	var cells: Array=[]
	if rules.terrain(b,start)!="~":return cells
	cells.append(start);var queue: Array=[start]
	while not queue.is_empty():
		var cell: Array=queue.pop_front()
		for direction: Array in [[0,-1],[-1,0],[1,0],[0,1]]:
			var next: Array=[int(cell[0])+direction[0],int(cell[1])+direction[1]]
			if rules.terrain(b,next)=="~" and not rules.contains_cell(cells,next):cells.append(next);queue.append(next)
	return cells
static func footprint(b: Dictionary,e: Dictionary,rules: GDScript) -> Array:
	if not b.intents.has(e.id) or e.hp<=0 or e.disabled or e.get("isolated",false) or e.get("off_rail",false):return []
	var d: Array=b.intents[e.id]
	var cells: Array=[]
	match e.type:
		"relay":return []
		"sentinel":
			if int(b.round)%2==1:return []
			for step: int in range(1,4):
				var cell: Array=[int(e.cell[0])+d[0]*step,int(e.cell[1])+d[1]*step]
				if rules.terrain(b,cell)=="#" or not rules.Product.valid_cell(cell):break
				cells.append(cell)
				if b.barriers.has(str(cell)):break
		"welder":
			if int(b.round)%2==1:return cells
			for offset: int in [-1,0,1]:
				var cell: Array=[int(e.cell[0])+d[0]-d[1]*offset,int(e.cell[1])+d[1]+d[0]*offset]
				if rules.terrain(b,cell)!="#":cells.append(cell)
		"skimmer":
			if int(b.round)%2==0:return water_region(b,e.cell,rules)
			if e.has("locked_step"):
				var destination: Array=[int(e.cell[0])+e.locked_step[0],int(e.cell[1])+e.locked_step[1]]
				return [destination] if not rules.same(destination,e.cell) and rules.terrain(b,destination)=="~" and not rules.occupied(b,destination) and not rules.blocked(b,destination) else []
			var best: Array=e.cell;var nearest: int=999
			for candidate: Array in [[0,-1],[-1,0],[0,0],[1,0],[0,1]]:
				var cell: Array=[int(e.cell[0])+candidate[0],int(e.cell[1])+candidate[1]]
				if rules.terrain(b,cell)!="~" or rules.occupied(b,cell) or (not rules.same(cell,e.cell) and rules.blocked(b,cell)):continue
				var distance: int=999
				for hero: Dictionary in b.heroes.values():
					if not hero.left and not hero.downed:distance=mini(distance,rules.distance(cell,hero.cell))
				if distance<nearest:best=cell;nearest=distance
			if not rules.same(best,e.cell):cells.append(best)
		"hauler":
			var rail: Array=e.rail
			var index: int=0
			for i: int in range(rail.size()):
				if rules.same(rail[i],e.cell):index=i
			var direction: int=int(e.get("rail_direction",1))
			for step: int in range(2):
				if index+direction<0 or index+direction>=rail.size():direction=-direction
				index+=direction
				if rules.blocked(b,rail[index]):break
				cells.append(rail[index])
		_:
			for step: int in range(1,4):
				var cell: Array=[int(e.cell[0])+d[0]*step,int(e.cell[1])+d[1]*step]
				if rules.blocked(b,cell):break
				cells.append(cell)
	return cells
static func damage_object(o: Dictionary,damage: int) -> void:
	var shield: int=mini(int(o.get("shield",0)),damage)
	if shield>0:o.shield-=shield
	o.hp=maxi(0,int(o.hp)-damage+shield)
	if o.hp==0:o.lost=true
static func resolve(b: Dictionary,e: Dictionary,rules: GDScript) -> void:
	if e.get("paused_round",0)==b.round or e.get("isolated",false):return
	var cells:=footprint(b,e,rules)
	for cell: Array in cells:
		if e.type in ["scout","sentinel","hauler"] and b.barriers.has(str(cell)):
			if not b.protection.has(b.barriers[str(cell)].actor):b.protection.append(b.barriers[str(cell)].actor)
			b.barriers[str(cell)].hp-=enemy_damage(b,3 if e.type=="sentinel" else 2)
			if b.barriers[str(cell)].hp<=0:b.barriers.erase(str(cell))
			break
		var carried_before: Array=[]
		for hero: Dictionary in b.heroes.values():
			if not hero.carrying.is_empty():carried_before.append(hero.carrying)
		var hit: bool=false
		var origin: Array=e.cell.duplicate()
		for h: Dictionary in b.heroes.values():
			if h.left or h.downed or not rules.same(h.cell,cell):continue
			if e.type=="skimmer" and int(b.round)%2==1:hit=true;continue
			if e.type=="hauler":
				var destination: Array=[int(cell[0])+signi(int(cell[0])-int(origin[0])),int(cell[1])+signi(int(cell[1])-int(origin[1]))]
				if not rules.blocked(b,destination) and not rules.occupied(b,destination):h.cell=destination
			if e.type=="skimmer" and (b.electrified_hits.has(h.id) or rules.contains_cell(b.insulation,h.cell)):continue
			var before_hp: int=h.hp
			var cover: int=0 if e.type=="skimmer" else int(b.cover.get(h.id,0))
			rules.hurt(b,h,maxi(0,enemy_damage(b,3 if e.type=="sentinel" else 2)-cover))
			if e.type!="skimmer":b.cover.erase(h.id)
			rules.Field.on_hit(b,h.id,before_hp-h.hp,"electric" if e.type=="skimmer" else "machine",rules)
			if e.type=="skimmer":b.electrified_hits.append(h.id)
			hit=true
		for o: Dictionary in b.objects.values():
			if not carried_before.has(o.id) and not o.has("crew_id") and not o.lost and not o.delivered and o.carrier.is_empty() and rules.same(o.cell,cell):
				if not (e.type=="skimmer" and int(b.round)%2==1):damage_object(o,enemy_damage(b,3 if e.type=="sentinel" else 2))
				hit=true
		if e.type=="scout" and hit:break
		if e.type=="hauler" and hit:
			if rules.occupied(b,cell):break
		if e.type in ["scout","hauler"] or (e.type=="skimmer" and int(b.round)%2==1):
			if hit and e.type=="skimmer":break
			e.cell=cell.duplicate()
			if e.type=="hauler":
				if rules.same(cell,e.rail[-1]):e.rail_direction=-1
				elif rules.same(cell,e.rail[0]):e.rail_direction=1
static func environment(b: Dictionary,board: Dictionary,rules: GDScript) -> void:
	reinforcements(b,board,rules)
	var fire: Dictionary=b.get("environment",board.environment).fire_pulse
	if b.round>=fire.round and b.round<int(fire.round)+int(fire.duration_rounds):
		for cell: Array in fire.cells:
			if rules.terrain(b,cell) in ["#","X"]:continue
			for hero: Dictionary in b.heroes.values():
				if rules.same(hero.cell,cell) and not b.electrified_hits.has(hero.id):
					var before_hp: int=hero.hp
					rules.hurt(b,hero,int(fire.damage))
					rules.Field.on_hit(b,hero.id,before_hp-hero.hp,"fire",rules)
					if before_hp>hero.hp:
						if not b.has("weather_exposed"):b.weather_exposed=[]
						if not b.weather_exposed.has(hero.id):b.weather_exposed.append(hero.id)
	for o: Dictionary in b.objects.values():
		if not o.get("active",false) or o.lost or o.completed:continue
		if o.kind=="channel":
			if not channel_power(b,o):continue
			o.timer+=1
			o.completed=o.timer>=int(o.hold_rounds)
		elif o.kind=="convoy":
			var next: int=int(o.waypoint)+1
			if next<o.waypoints.size() and not rules.blocked(b,o.waypoints[next]) and not rules.occupied(b,o.waypoints[next]):
				o.waypoint=next;o.cell=o.waypoints[next].duplicate()
				if next==o.waypoints.size()-1:o.completed=true;o.delivered=true
	for o: Dictionary in b.objects.values():
		if o.lost or o.delivered:continue
		var prerequisites_met: bool=true
		for id: String in o.prerequisites:
			if not b.objects[id].completed:
				prerequisites_met=false
				if b.objects[id].lost or b.objects[id].has("unavailable_reason"):o.unavailable_reason=id
		if prerequisites_met and not o.has("unlocked_round"):o.unlocked_round=b.round
		if not o.stable and prerequisites_met:
			var deadline: int=rescue_deadline(b,o)
			if deadline>0 and b.round>=deadline:o.lost=true
		if o.has("opportunity_deadline") and b.round>=int(o.opportunity_deadline)+deadline_grace(b) and not o.completed:o.lost=true

		if o.lost and not o.carrier.is_empty():b.heroes[o.carrier].carrying="";o.carrier=""

static func reinforcements(b: Dictionary,board: Dictionary,rules: GDScript) -> void:
	for pending: Dictionary in b.queued_reinforcements.duplicate():
		if pending.due>b.round:continue
		if rules.occupied(b,pending.cell) or rules.blocked(b,pending.cell):
			if pending.delayed:b.queued_reinforcements.erase(pending)
			else:pending.due+=1;pending.delayed=true
			continue
		var id: String="reinforcement_%d" % pending.index
		b.enemies[id]={"id":id,"type":"scout","cell":pending.cell.duplicate(),"hp":int(board.reinforcement.spawn_hp),"disabled":false,"disable_requires":[],"rail":null}
		b.queued_reinforcements.erase(pending)
static func plan_reinforcements(b: Dictionary,rules: GDScript) -> void:
	if not int(b.round) in [3,6] or b.spawn_count>=int(b.reinforcement.cap):return
	for e: Dictionary in b.enemies.values():
		if e.type!="relay" or e.hp<=0 or e.disabled or e.get("isolated",false):continue
		for cell: Array in b.reinforcement.cells:
			if rules.occupied(b,cell) or rules.blocked(b,cell):continue
			b.spawn_count+=1
			b.queued_reinforcements.append({"cell":cell.duplicate(),"due":b.round+1,"delayed":false,"index":b.spawn_count})
			break
		if b.spawn_count>=int(b.reinforcement.cap):break

static func enemy_damage(b: Dictionary,raw: int) -> int:
	if b.difficulty=="relaxed":return maxi(1,raw-1)
	return raw+1 if b.difficulty=="hard" and int(b.get("balance_revision",1))==2 else raw

static func plan_skimmer(b: Dictionary,e: Dictionary,rules: GDScript) -> void:
	e.erase("locked_step")
	if not b.intents.has(e.id):b.intents[e.id]=[0,1]
	var cells: Array=footprint(b,e,rules)
	e.locked_step=[0,0] if cells.is_empty() else [int(cells[0][0])-int(e.cell[0]),int(cells[0][1])-int(e.cell[1])]

static func deadline_grace(b: Dictionary) -> int:
	return 2 if b.difficulty=="relaxed" and int(b.get("balance_revision",1))==2 else 0
static func rescue_deadline(b: Dictionary,o: Dictionary) -> int:
	if not o.has("stabilize_deadline"):return 0
	var timer: Dictionary=o.stabilize_deadline
	if timer.mode=="none":return 0
	if timer.mode=="prerequisite_round_plus_2":
		return int(o.unlocked_round)+2+deadline_grace(b) if o.has("unlocked_round") else 0
	return int(timer.round)+deadline_grace(b) if timer.get("round")!=null else 6+deadline_grace(b)

static func channel_power(b: Dictionary,o: Dictionary) -> bool:
	var condition: Variant=o.get("power_condition",true)
	if condition is bool:return condition
	if condition is String:return b.objects.has(condition) and b.objects[condition].completed
	if condition is Dictionary:
		for id: String in condition.get("all_of",[]):
			if not b.objects.has(id) or not b.objects[id].completed:return false
		for id: String in condition.get("not_disabled",[]):
			if not b.enemies.has(id) or b.enemies[id].disabled:return false
	return true
