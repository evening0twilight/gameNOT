extends RefCounted
static func cycle(id: String,graph: Dictionary,visiting: Dictionary,done: Dictionary) -> bool:
	if done.has(id):return false
	if visiting.has(id):return true
	visiting[id]=true
	for next: String in graph.get(id,[]):
		if not graph.has(next) or cycle(next,graph,visiting,done):return true
	visiting.erase(id);done[id]=true;return false
static func validate(domains: Dictionary,actors: Dictionary,boards: Dictionary) -> String:
	for key: String in ["abilities","enemies","equipment","facilities","stories","scripts","field_operations","initial_relationships","economy"]:
		if not domains.has(key):return "missing_domain"
	if actors.size()!=8 or boards.size()!=36 or domains.abilities.size()!=16 or domains.enemies.size()!=6 or domains.equipment.items.size()!=7 or domains.facilities.size()!=4:return "invalid_content_count"
	var enemy_types: Dictionary={}
	for e: Dictionary in domains.enemies:enemy_types[e.id]=true
	var abilities: Dictionary={}
	for a: Dictionary in domains.abilities:
		if abilities.has(a.id) or not actors.has(a.actor) or int(a.level) not in [1,3]:return "invalid_ability"
		abilities[a.id]=true
	var graph: Dictionary={};var nodes: Dictionary={}
	for group: String in ["personal_nodes","relationship_nodes","recovery_nodes"]:
		for n: Dictionary in domains.stories[group]:
			if nodes.has(n.id):return "duplicate_story"
			nodes[n.id]=n;graph[n.id]=n.get("requires_resolved",[])
			for id: String in n.get("actors",[n.get("actor","")]):
				if not actors.has(id):return "invalid_story_actor"
	var done: Dictionary={}
	for id: String in graph:
		if cycle(id,graph,{},done):return "story_dependency_cycle"
	var scripts: Dictionary={};var total: int=0
	for group: String in ["personal","relationships","life","community","chapter"]:
		for n: Dictionary in domains.scripts[group]:
			if scripts.has(n.id):return "duplicate_script"
			scripts[n.id]=n;total+=1
			if group in ["community","chapter"] and not boards.has(n.source):return "invalid_story_source"
	if total!=96:return "invalid_scene_count"
	for id: String in nodes:
		if not scripts.has(id):return "missing_story_script"
		for choice: Dictionary in nodes[id].choices:
			if not scripts[id].get("choices",{}).has(choice.id):return "missing_choice_script"
	var relationships: Dictionary={}
	for r: Dictionary in domains.initial_relationships:
		if relationships.has(r.id) or not actors.has(r.observer) or (r.target!="leader" and not actors.has(r.target)) or r.observer==r.target:return "invalid_relationship"
		relationships[r.id]=true
	for a: String in actors:
		for b: String in actors.keys()+["leader"]:
			if a!=b and not relationships.has(a+">"+b):return "missing_relationship"
	for board: Dictionary in boards.values():
		var objects: Dictionary={};var enemies: Dictionary={};graph={};done={}
		for o: Dictionary in board.objectives+board.controls:objects[o.id]=o;graph[o.id]=o.prerequisites
		for e: Dictionary in board.enemies:
			if not enemy_types.has(e.type):return "invalid_enemy_type"
			enemies[e.id]=e
			for id: String in e.disable_requires:
				if not objects.has(id) or objects[id].get("disables")!=e.id:return "invalid_control_reference"
		for id: String in graph:
			if cycle(id,graph,{},done):return "objective_dependency_cycle"
		for o: Dictionary in objects.values():
			if o.has("disables") and not enemies.has(o.disables):return "invalid_enemy_reference"
			for field: String in ["waypoints"]:
				for cell: Variant in o.get(field,[]):
					if not cell_valid(cell):return "invalid_object_route"
		for group: Array in board.mandatory_groups:
			if group.is_empty():return "invalid_mandatory_group"
			for id: String in group:
				if not objects.has(id):return "invalid_mandatory_reference"
		for groups: Array in board.get("route_groups",{}).values():
			for group: Array in groups:
				for id: String in group:
					if not objects.has(id):return "invalid_route_reference"
	var field: Dictionary=domains.field_operations
	if field.services.size()!=4 or field.investments.size()!=2 or field.asset_registry.size()!=12:return "invalid_field_count"
	for id: String in field.asset_registry:
		if not boards.has(id):return "invalid_asset_board"
		var found: bool=false
		for e: Dictionary in boards[id].enemies:found=found or e.id==field.asset_registry[id].source_enemy
		if not found:return "invalid_asset_enemy"
	for id: String in field.services:
		if not id in ["M05","M10","M21","S11"]:return "invalid_service_board"
		var spec: Dictionary=field.services[id];var objects: Dictionary={}
		for o: Dictionary in boards[id].objectives+boards[id].controls:objects[o.id]=o
		for object: String in spec.linked_controls+spec.get("prerequisites",[])+spec.get("exit_requires",[]):
			if not objects.has(object):return "invalid_service_reference"
		for cell: Variant in spec.posts:
			if not cell_valid(cell):return "invalid_service_post"
	for r: Dictionary in domains.economy.objective_rewards:
		if not boards.has(r.mission):return "invalid_reward_mission"
		var found: bool=false
		for o: Dictionary in boards[r.mission].objectives:found=found or o.id==r.objective
		if not found:return "invalid_reward_object"
	return ""
static func cell_valid(value: Variant) -> bool:
	if not value is Array or value.size()!=2:return false
	for n: Variant in value:
		if not (n is int or n is float) or not is_finite(float(n)) or n!=int(n) or n<0 or n>7:return false
	return true
