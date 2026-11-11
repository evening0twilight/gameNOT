extends RefCounted
## Read-only suggestions. History is persisted with the next successful player command.
static func card(s: Dictionary,content: Dictionary) -> Dictionary:
	if s.campaign.phase!="battle":return {}
	var b: Dictionary=s.battle
	var history: Array=s.tutorial.get("history",[])
	var shown: int=0
	for entry: Dictionary in history:
		if entry.mission==b.mission_id:
			shown+=1
			if entry.round==b.round:return {}
	if shown>=(3 if b.mission_id=="M01" else 1):return {}
	var id: String=""
	var target: String=""
	if b.mission_id=="M01":
		if b.round==1:id="first_move"
		elif b.round==2:id="forecast"
		elif b.round>=3:
			for h: Dictionary in b.heroes.values():
				if not h.carrying.is_empty():id="return";target=h.carrying;break
	else:
		for o: Dictionary in b.objects.values():
			if o.completed or o.lost or o.has("unavailable_reason"):continue
			if o.kind in ["channel","convoy"]:id=o.kind;target=o.id;break
			if o.kind=="rescue":id="rescue";target=o.id
			elif id.is_empty() and o.kind=="work":id="work";target=o.id
	if id.is_empty():return {}
	for entry: Dictionary in history:
		if entry.id==id:return {}
	return {"id":id,"mission":b.mission_id,"round":b.round,"target":target}
static func record(s: Dictionary,snapshot: Dictionary,c: Dictionary,content: Dictionary) -> void:
	var supplied: Variant=c.payload.get("tutorial_card")
	if not supplied is Dictionary or supplied!=card(snapshot,content) or supplied.is_empty():return
	if not s.tutorial.has("history"):s.tutorial.history=[]
	s.tutorial.history.append(supplied.duplicate(true))

## Suggestions reference mandatory groups and a legal next move, never mutate state.
static func secured(o: Dictionary) -> bool:
	return o.completed and (not o.sustain_until_exit or o.hp>0)
static func danger(b: Dictionary,rules: GDScript) -> Array:
	var cells: Array=[]
	for enemy: Dictionary in b.enemies.values():
		if enemy.get("paused_round",0)==b.round:continue
		for cell: Array in rules.Hazards.footprint(b,enemy,rules):
			if not rules.contains_cell(cells,cell):cells.append(cell)
	var fire: Dictionary=b.environment.fire_pulse
	if b.round>=fire.round and b.round<int(fire.round)+int(fire.duration_rounds):
		for cell: Array in fire.cells:
			if not rules.contains_cell(cells,cell):cells.append(cell)
	return cells
static func cell_key(cell: Array) -> String:return str([int(cell[0]),int(cell[1])])
static func movement(s: Dictionary,actor: String,goals: Array,key: String,rules: GDScript) -> Dictionary:
	var b: Dictionary=s.battle
	var hero: Dictionary=b.heroes[actor]
	var distances: Dictionary={}
	var queue: Array=[]
	for cell: Array in goals:
		if rules.blocked(b,cell) or (rules.occupied(b,cell) and not rules.same(hero.cell,cell)):continue
		distances[cell_key(cell)]=0;queue.append(cell)
	while not queue.is_empty():
		var cell: Array=queue.pop_front()
		for offset: Array in [[0,-1],[-1,0],[1,0],[0,1]]:
			var next: Array=[int(cell[0])+offset[0],int(cell[1])+offset[1]]
			if rules.blocked(b,next):continue
			var cost: int=int(distances[cell_key(cell)])+(2 if rules.terrain(b,cell) in ["~",":"] else 1)
			if cost>=int(distances.get(cell_key(next),999)):continue
			distances[cell_key(next)]=cost;queue.append(next)
	var hazards: Array=danger(b,rules)
	var best: Array=[]
	var score: int=99999
	for cell: Array in rules.reachable_cells(s,actor):
		var distance: int=int(distances.get(cell_key(cell),999))
		if distance>=999:continue
		var value: int=distance*10+(100 if rules.contains_cell(hazards,cell) else 0)
		# Do not spend AP circling without getting closer, unless leaving a danger cell.
		if distance>=int(distances.get(cell_key(hero.cell),999)) and not rules.contains_cell(hazards,hero.cell):continue
		if value<score:score=value;best=cell
	if best.is_empty():return {"key":"blocked","action":"","cell":[]}
	return {"key":"risky_move" if rules.contains_cell(hazards,best) else key,"action":"move","cell":best,"payload":{"cell":best}}
static func next_step(s: Dictionary,content: Dictionary,actor: String) -> Dictionary:
	if s.campaign.phase!="battle" or not s.battle.heroes.has(actor):return {}
	var rules: GDScript=load("res://scripts/domain/campaign_rules.gd")
	var b: Dictionary=s.battle
	var hero: Dictionary=b.heroes[actor]
	var board: Dictionary=content.boards[b.mission_id]
	if hero.left or hero.downed or hero.ap<=0:
		for h: Dictionary in b.heroes.values():
			if not h.left and not h.downed and h.ap>0:return {"key":"no_ap" if hero.ap<=0 else "choose_crew","action":"","actor":h.id,"cell":[]}
		return {"key":"round_ready","action":"end_round","payload":{},"cell":[]}
	if not hero.carrying.is_empty():
		if rules.contains_cell(b.get("exits",board.exits),hero.cell):return {"key":"deliver","action":"extract","payload":{},"cell":hero.cell,"target":hero.carrying}
		return movement(s,actor,b.get("exits",board.exits),"return",rules)
	var required: Array=[]
	var all_done: bool=true
	for group: Array in rules.Full.groups(s,board):
		var done: bool=false
		for id: String in group:done=done or secured(b.objects[id])
		if done:continue
		all_done=false
		for id: String in group:
			if not required.has(id):required.append(id)
	# Rescue a downed teammate before directing the remaining crew off the map.
	for object: Dictionary in b.objects.values():
		if object.has("crew_id") and not object.delivered and not object.lost:required.push_front(object.id);all_done=false
	if all_done:
		if rules.contains_cell(b.get("exits",board.exits),hero.cell):return {"key":"leave","action":"leave_site","payload":{},"cell":hero.cell}
		return movement(s,actor,b.get("exits",board.exits),"leave_move",rules)
	var candidate: Dictionary={}
	var best: int=9999
	var carried: bool=false
	for id: String in required:
		var object: Dictionary=b.objects[id]
		if object.lost or object.has("unavailable_reason"):continue
		if not object.carrier.is_empty():carried=true;continue
		if object.has("branch") and not b.branch.is_empty() and object.branch!=b.branch:continue
		var visited: Array=[]
		while not object.id in visited:
			visited.append(object.id)
			var predecessor: Dictionary={}
			for prerequisite: String in object.prerequisites:
				if not b.objects[prerequisite].completed:predecessor=b.objects[prerequisite];break
			if predecessor.is_empty():break
			object=predecessor
		if object.lost or object.has("unavailable_reason"):continue
		var score: int=rules.distance(hero.cell,object.cell)+(0 if object.kind=="rescue" else 10)
		if object.get("active",false):score+=100
		if object.has("crew_id"):score-=100
		if score<best:best=score;candidate=object
	if candidate.is_empty():
		if carried:
			for h: Dictionary in b.heroes.values():
				if not h.carrying.is_empty() and h.ap>0 and not h.left:return {"key":"carrier","action":"","actor":h.id,"cell":h.cell}
			return {"key":"round_ready","action":"end_round","payload":{},"cell":[]}
		return {"key":"retreat","action":"emergency_retreat","payload":{"confirmed":true},"cell":[]}
	if candidate.get("active",false):return {"key":"active","action":"end_round","payload":{},"cell":candidate.cell,"target":candidate.id}
	if rules.distance(hero.cell,candidate.cell)>1:
		var cell: Array=candidate.cell
		return movement(s,actor,[cell,[int(cell[0])-1,int(cell[1])],[int(cell[0])+1,int(cell[1])],[int(cell[0]),int(cell[1])-1],[int(cell[0]),int(cell[1])+1]],"approach",rules)
	var kind: String="interact"
	var key: String="work"
	if candidate.kind=="rescue":kind="pickup" if candidate.stable else "stabilize";key=kind
	elif candidate.kind=="cargo":kind="pickup";key="pickup"
	return {"key":key,"action":kind,"payload":{"target":candidate.id},"cell":candidate.cell,"target":candidate.id}
