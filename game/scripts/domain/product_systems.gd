extends RefCounted
const Crew=preload("res://scripts/domain/crew_journey.gd")
## Product rules use the same reducer as ordinary actions; no presentation-owned balances.
static func ensure(s: Dictionary) -> void:
	if not s.has("product"):
		s.product={"owned":["crowbar","medkit"],"loadout":{},"facilities":{"infirmary":0,"workshop":0,"rest_area":0,"communications":0},"purchases":{},"discount_main":-1,"facility_day":0,"treatment_day":0,"variant":"A","difficulty_history":[],"withdrawn":[],"history_proofs":{}}
	for id: String in s.actors:
		if not s.product.loadout.has(id):s.product.loadout[id]={"tool":"","support":""}
	if not s.battle.is_empty():
		if not s.battle.has("balance_revision"):s.battle.balance_revision=1
		if not s.battle.has("safety"):s.battle.safety=[]
		if not s.battle.has("equipment"):s.battle.equipment={}
		if not s.battle.has("tool_uses"):s.battle.tool_uses={}
		if not s.battle.has("medicine_limit"):s.battle.medicine_limit=2
static func tier(s: Dictionary,id: String) -> int:
	return int(s.get("product",{}).get("facilities",{}).get(id,0))
static func pack_limit(s: Dictionary) -> int:return 3 if tier(s,"workshop")>=2 else 2
static func item(content: Dictionary,id: String) -> Dictionary:
	for entry: Dictionary in content.domains.equipment.items:
		if entry.id==id:return entry
	return {}
static func limit(board: Dictionary,difficulty: String) -> int:
	return int(board.hard_round_limit) if difficulty=="hard" else int(board.round_limit)+(3 if difficulty=="relaxed" else 0)
static func weather(board: Dictionary,variant: String) -> Dictionary:
	var result: Dictionary=board.environment.duplicate(true)
	if variant=="B":
		result.water_addition.round=board.variant.B.water_round
		result.water_addition.cells=board.variant.B.water_cells.duplicate(true)
		result.fire_pulse.round=board.variant.B.fire_round
	return result
static func prepare(s: Dictionary,c: Dictionary) -> String:
	ensure(s)
	var difficulty: Variant=c.payload.get("difficulty",s.campaign.difficulty)
	if difficulty not in ["relaxed","standard","hard"]:return "invalid_target"
	if difficulty=="hard" and s.campaign.difficulty!="hard" and not c.payload.get("hard_acknowledged",false):return "hard_confirmation_required"
	s.campaign.difficulty=difficulty
	return ""
static func deploy(s: Dictionary,board: Dictionary) -> void:
	ensure(s)
	var b: Dictionary=s.battle
	b.difficulty=s.campaign.difficulty;b.variant=s.product.variant;b.balance_revision=3
	b.limit=limit(board,b.difficulty);b.environment=weather(board,b.variant)
	b.medicine_limit=pack_limit(s);b.equipment={};b.tool_uses={}
	for id: String in b.heroes:
		b.equipment[id]=s.product.loadout.get(id,{"tool":"","support":""}).duplicate()
	for purchase: Dictionary in s.product.purchases.values():purchase.deployed=true
	if not s.product.difficulty_history.has(b.difficulty):s.product.difficulty_history.append(b.difficulty)
static func camp(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	ensure(s)
	if s.campaign.phase!="camp" or s.campaign.day>=24:return "invalid_phase"
	var p: Dictionary=c.payload
	var id: String=str(p.get("item",""))
	var definition: Dictionary=item(content,id)
	match c.kind:
		"buy_supplies":
			var cost: int=int(content.domains.economy.supply_buy_cost)
			if s.inventory.credits<cost:return "insufficient_resources"
			s.inventory.credits-=cost;s.inventory.supplies+=1
		"buy_tool":
			if definition.is_empty() or s.product.owned.has(id) or s.chapter_one.main_completed<int(definition.unlocked_after_main):return "tool_unavailable"
			var discounted: bool=tier(s,"workshop")>=1 and s.product.discount_main!=s.chapter_one.main_completed
			var parts: int=maxi(0,int(definition.price_parts)-(1 if discounted else 0))
			if s.inventory.credits<definition.price_credits or s.inventory.parts<parts:return "insufficient_resources"
			s.inventory.credits-=definition.price_credits;s.inventory.parts-=parts
			s.product.owned.append(id)
			s.product.purchases[id]={"credits":definition.price_credits,"parts":parts,"discounted":discounted,"main":s.chapter_one.main_completed,"deployed":false}
			if discounted:s.product.discount_main=s.chapter_one.main_completed
		"refund_tool":
			if not s.product.purchases.has(id) or s.product.purchases[id].deployed:return "refund_unavailable"
			var purchase: Dictionary=s.product.purchases[id]
			s.inventory.credits+=purchase.credits;s.inventory.parts+=purchase.parts
			if purchase.discounted:s.product.discount_main=-1
			s.product.purchases.erase(id);s.product.owned.erase(id)
			for gear: Dictionary in s.product.loadout.values():
				for slot: String in gear:
					if gear[slot]==id:gear[slot]=""
		"equip_tool":
			if not s.actors.has(c.actor_id) or not Crew.joined(s,c.actor_id) or s.product.withdrawn.has(c.actor_id):return "unavailable_actor"
			var slot: String=str(p.get("slot",definition.get("slot","")))
			if slot not in ["tool","support"]:return "invalid_target"
			if not id.is_empty():
				if not s.product.owned.has(id) or definition.slot!=slot:return "tool_unavailable"
				for gear: Dictionary in s.product.loadout.values():
					if gear[slot]==id:gear[slot]=""
			s.product.loadout[c.actor_id][slot]=id
		"upgrade_facility":
			var facility: String=str(p.get("facility",""))
			if not s.product.facilities.has(facility) or tier(s,facility)>=2:return "invalid_target"
			if s.product.facility_day==s.campaign.day or s.campaign.projects>=2:return "project_used"
			var cost: Array=[]
			for row: Dictionary in content.domains.facilities:
				if row.id==facility:cost=row.costs[tier(s,facility)]
			if s.inventory.credits<cost[0] or s.inventory.parts<cost[1]:return "insufficient_resources"
			s.inventory.credits-=cost[0];s.inventory.parts-=cost[1]
			s.product.facilities[facility]+=1;s.product.facility_day=s.campaign.day;s.campaign.projects+=1
		_:return "unknown_command"
	return ""
static func use_tool(s: Dictionary,c: Dictionary,content: Dictionary,rules: GDScript) -> String:
	var b: Dictionary=s.battle
	if not b.heroes.has(c.actor_id):return "unavailable_actor"
	var h: Dictionary=b.heroes[c.actor_id]
	if h.left or h.downed:return "unavailable_actor"
	var p: Dictionary=c.payload
	if c.kind=="cross_anchor":
		var target: Variant=p.get("cell")
		if not valid_cell(target):return "invalid_target"
		for anchor: Dictionary in b.deployed_tools.values():
			if anchor.get("kind")!="winch":continue
			if (rules.same(h.cell,anchor.cell) and rules.same(target,anchor.other)) or (rules.same(h.cell,anchor.other) and rules.same(target,anchor.cell)):
				if h.ap<1:return "insufficient_ap"
				if rules.blocked(b,target) or rules.occupied(b,target) or b.barriers.has(str(target)) or rules.terrain(b,target)!=".":return "invalid_target"
				if not h.carrying.is_empty():rules.record_transport(b.objects[h.carrying],h.id,h.cell,target)
				h.cell=target.duplicate();h.ap-=1;return ""
		return "invalid_target"
	if not h.carrying.is_empty():return "carrying_restriction"
	var id: String=str(p.get("item",""))
	var definition: Dictionary=item(content,id)
	if definition.is_empty() or not b.equipment.get(h.id,{}).values().has(id) or id=="stretcher":return "tool_unavailable"
	var used: int=int(b.tool_uses.get(id,0))
	var maximum: Variant=b.medicine_limit if id=="medkit" else definition.uses_per_mission
	if maximum!=null and used>=int(maximum):return "already_used"
	if h.ap<int(definition.action_ap):return "insufficient_ap"
	var target: String=str(p.get("target",""))
	match id:
		"crowbar","scanner":
			var o: Dictionary=b.objects.get(target,{})
			if o.is_empty() or o.lost or o.completed or rules.distance(h.cell,o.cell)>int(definition.range):return "invalid_target"
			if not o.get("interaction_tags",[]).has("light_obstacle" if id=="crowbar" else "machine_shutdown"):return "invalid_target"
			for prerequisite: String in o.prerequisites:
				if not b.objects[prerequisite].completed:return "prerequisite_required"
			o.progress=mini(int(o.work),int(o.progress)+(2 if id=="crowbar" else 1));o.completed=o.progress>=o.work
			if not o.contributors.has(h.id):o.contributors.append(h.id)
			if o.completed and o.has("disables"):rules.shutdown(b,o.disables)
		"medkit":
			if not b.heroes.has(target):return "invalid_target"
			var patient: Dictionary=b.heroes[target]
			var lv: int=rules.Specialties.level(int(s.actors.get(target,{}).get("xp",0)))
			var hp_max: int=10+(1 if lv>=4 else 0)+(1 if lv>=6 else 0)
			if patient.left or patient.downed or patient.hp>=hp_max or rules.distance(h.cell,patient.cell)>1:return "invalid_target"
			if b.medicine<1:return "insufficient_resources"
			b.medicine-=1;patient.hp=mini(hp_max,int(patient.hp)+3)
		"shield","insulation","winch":
			var cell: Variant=p.get("cell")
			if not valid_cell(cell) or rules.distance(h.cell,cell)>1:return "invalid_target"
			if rules.terrain(b,cell) in ["#","X"]:return "invalid_target"
			if id=="shield":
				if rules.occupied(b,cell) or rules.blocked(b,cell) or b.barriers.has(str(cell)):return "invalid_target"
				b.barriers[str(cell)]={"cell":cell.duplicate(),"hp":4,"expires":0,"actor":h.id}
			elif id=="insulation":
				if rules.contains_cell(b.insulation,cell):return "already_used"
				b.insulation.append(cell.duplicate())
			else:
				var other: Variant=p.get("other")
				if not valid_cell(other) or rules.distance(cell,other)!=2 or (cell[0]!=other[0] and cell[1]!=other[1]):return "invalid_target"
				var gap: Array=[int((cell[0]+other[0])/2),int((cell[1]+other[1])/2)]
				if rules.terrain(b,cell)!="." or rules.terrain(b,other)!="." or rules.terrain(b,gap)!="X" or rules.blocked(b,cell) or rules.blocked(b,other):return "invalid_target"
				b.deployed_tools[id]={"kind":"winch","cell":cell.duplicate(),"other":other.duplicate(),"actor":h.id}
		_:return "invalid_target"
	h.ap-=int(definition.action_ap);b.tool_uses[id]=used+1
	return ""
static func valid_cell(value: Variant) -> bool:
	if not value is Array or value.size()!=2:return false
	for n: Variant in value:
		if not (n is int or n is float) or not is_finite(float(n)) or n!=int(n) or n<0 or n>7:return false
	return true
