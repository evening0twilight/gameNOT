extends RefCounted
## All eight crew members' authored specialties. No filesystem or UI dependencies.
static func level(xp: int) -> int:
	var result: int=1
	for threshold: int in [12,28,48,72,100]:
		if xp>=threshold:result+=1
	return result
static func apply(s: Dictionary,c: Dictionary,content: Dictionary,rules: Script) -> String:
	var b: Dictionary=s.battle
	if not b.heroes.has(c.actor_id) or not s.actors.has(c.actor_id):return "unavailable_actor"
	var h: Dictionary=b.heroes[c.actor_id]
	var p: Dictionary=c.payload
	var id: String=str(p.get("ability",""))
	var spec: Dictionary={}
	for a: Dictionary in content.domains.abilities:
		if a.id==id:spec=a;break
	var lv: int=level(int(s.actors[c.actor_id].xp))
	if spec.is_empty() or spec.actor!=c.actor_id or lv<int(spec.level) or spec.production_status!="active":return "ability_unavailable"
	if h.left or h.downed:return "unavailable_actor"
	if h.ap<int(spec.ap):return "insufficient_ap"
	if int(b.ability_uses.get(id,0))>=int(spec.charges_per_mission):return "ability_exhausted"
	if not h.carrying.is_empty() and not (id=="xu_1" and (lv>=5 or load("res://scripts/domain/p1_protocols.gd").anchored(b,h,rules))) and id not in ["jiang_1","jiang_3"]:return "carrying_restriction"
	var target: String=str(p.get("target",""))
	var o: Dictionary=b.objects.get(target,{})
	var other: Dictionary=b.heroes.get(target,{})
	match id:
		"lin_1","lin_3":
			if o.is_empty() or o.kind!="rescue" or o.stable or o.lost or o.completed or not o.carrier.is_empty():return "invalid_target"
			for prerequisite: String in o.prerequisites:
				if not b.objects[prerequisite].completed:return "prerequisite_required"
			if id=="lin_3":
				var destination: Variant=p.get("cell")
				if not valid_cell(destination):return "invalid_target"
				if rules.move_cost(b,h.cell,destination,2)<0 or rules.distance(destination,o.cell)>1:return "invalid_target"
				h.cell=destination.duplicate()
			elif rules.distance(h.cell,o.cell)>(3 if lv>=5 else 2):return "invalid_target"
			o.stable=true
			if o.has("crew_id"):b.heroes[o.crew_id].deadline+=1;b.heroes[o.crew_id].stabilized=true
			if not o.contributors.has(h.id):o.contributors.append(h.id)
		"xu_1":
			var cell: Variant=p.get("cell")
			if not valid_cell(cell) or rules.terrain(b,cell)!="." or rules.blocked(b,cell) or rules.occupied(b,cell) or b.barriers.has(str(cell)):return "invalid_target"
			var dist: int=rules.distance(h.cell,cell)
			if dist<1 or dist>3 or (h.cell[0]!=cell[0] and h.cell[1]!=cell[1]):return "invalid_target"
			var d: Array=[signi(int(cell[0])-int(h.cell[0])),signi(int(cell[1])-int(h.cell[1]))]
			var obstacles: int=0
			for step: int in range(1,dist):
				var at: Array=[h.cell[0]+step*d[0],h.cell[1]+step*d[1]]
				if rules.terrain(b,at) in ["#","X"]:obstacles+=1
				elif rules.blocked(b,at) or rules.occupied(b,at):return "invalid_target"
			if obstacles>1:return "invalid_target"
			var origin: Array=h.cell.duplicate()
			h.cell=cell.duplicate()
			if not h.carrying.is_empty():rules.record_transport(b.objects[h.carrying],h.id,origin,h.cell)
		"su_1":
			if not b.enemies.has(target) or b.enemies[target].hp<=0 or rules.distance(h.cell,b.enemies[target].cell)>4:return "invalid_target"
			b.marks[target]=b.round
		"xu_3","su_3":
			if other.is_empty() or other.id==h.id or other.left or other.downed or not p.get("consent",false):return "invalid_target"
			if rules.distance(h.cell,other.cell)>int(spec.range):return "invalid_target"
			for observer: String in [h.id,other.id]:
				for responsible: String in [other.id if observer==h.id else h.id,"leader"]:
					var relationship: Dictionary=s.social.get(observer+">"+responsible,{})
					if relationship.get("band","") in ["conditional","rupture"] and observer=="xu" and not b.authorizations.has(observer):return "relationship_safeguard_required"
			if id=="xu_3":
				if b.round_markers.has("pull:"+target):return "already_used"
				if h.cell[0]!=other.cell[0] and h.cell[1]!=other.cell[1]:return "invalid_target"
				var cell: Array=[int(other.cell[0])+signi(int(h.cell[0])-int(other.cell[0])),int(other.cell[1])+signi(int(h.cell[1])-int(other.cell[1]))]
				if rules.terrain(b,cell)!="." or rules.blocked(b,cell) or rules.occupied(b,cell) or b.barriers.has(str(cell)):return "invalid_target"
				other.cell=cell
				b.round_markers["pull:"+target]=true
			elif p.get("mode","move")=="ap":
				if lv<5 or b.used_markers.has("su_ap") or b.round_markers.has("ap:"+target) or other.ap>2:return "ability_unavailable"
				other.ap+=1
				b.used_markers.su_ap=true
				b.round_markers["ap:"+target]=true
			else: b.move_bonuses[target]=1
		"chen_1":
			if not b.enemies.has(target) or b.enemies[target].hp<=0 or b.enemies[target].disabled or rules.distance(h.cell,b.enemies[target].cell)>2:return "invalid_target"
			var enemy: Dictionary=b.enemies[target]
			if b.round-int(enemy.get("last_pause_round",-2))<2:return "already_used"
			enemy.paused_round=b.round;enemy.last_pause_round=b.round
		"chen_3":
			if target=="live_service":
				if b.get("service",{}).is_empty() or b.service.reinforced or rules.distance(h.cell,rules.Field.posts(b)[0])>2:return "invalid_target"
				b.service.shield=6 if lv>=5 else 3;b.service.reinforced=true
				h.ap-=int(spec.ap);b.ability_uses[id]=int(b.ability_uses.get(id,0))+1;return ""
			if o.is_empty() or o.kind!="work" or o.lost or o.hp<=0 or o.get("reinforced",false) or rules.distance(h.cell,o.cell)>2:return "invalid_target"
			o.shield=6 if lv>=5 else 3;o.reinforced=true
		"ye_1":
			if not b.enemies.has(target):return "invalid_target"
			var enemy: Dictionary=b.enemies[target]
			if enemy.hp<=0 or enemy.disabled or enemy.get("isolated",false):return "invalid_target"
			if rules.distance(h.cell,enemy.cell)>(2 if lv>=5 else 1):return "invalid_target"
			if rules.distance(h.cell,enemy.cell)==2:
				if h.cell[0]!=enemy.cell[0] and h.cell[1]!=enemy.cell[1]:return "invalid_target"
				var middle: Array=[int((h.cell[0]+enemy.cell[0])/2),int((h.cell[1]+enemy.cell[1])/2)]
				if rules.blocked(b,middle) or rules.occupied(b,middle) or b.barriers.has(str(middle)):return "invalid_target"
			enemy.isolated=true
		"ye_3":
			var cell: Variant=p.get("cell")
			if not valid_cell(cell):return "invalid_target"
			if h.cell[0]!=cell[0] and h.cell[1]!=cell[1]:return "invalid_target"
			var length: int=rules.distance(h.cell,cell)
			if length<1 or length>(3 if lv>=5 else 2):return "invalid_target"
			var direction: Array=[signi(int(cell[0])-int(h.cell[0])),signi(int(cell[1])-int(h.cell[1]))]
			for step: int in range(1,length+1):
				var at: Array=[h.cell[0]+step*direction[0],h.cell[1]+step*direction[1]]
				if rules.terrain(b,at) in ["#","X"]:return "invalid_target"
			for step: int in range(1,length+1):
				var at: Array=[h.cell[0]+step*direction[0],h.cell[1]+step*direction[1]]
				if not rules.contains_cell(b.insulation,at):b.insulation.append(at)
		"he_1":
			var cell: Variant=p.get("cell")
			if not valid_cell(cell) or rules.distance(h.cell,cell)!=1 or rules.terrain(b,cell)!="." or rules.blocked(b,cell) or rules.occupied(b,cell) or b.barriers.has(str(cell)):return "invalid_target"
			b.barriers[str(cell)]={"cell":cell.duplicate(),"hp":5 if lv>=5 else 3,"expires":0 if lv>=5 else b.round+1,"actor":h.id}
		"mo_1":
			if o.is_empty() or not o.get("interaction_tags",[]).has("machine_shutdown") or o.completed or o.lost or rules.distance(h.cell,o.cell)>5:return "invalid_target"
			for required: String in o.prerequisites:
				if not b.objects[required].completed:return "prerequisite_required"
			o.progress=mini(o.work,int(o.progress)+(2 if lv>=5 else 1));o.completed=o.progress>=o.work
			if not o.contributors.has(h.id):o.contributors.append(h.id)
			if o.completed:rules.shutdown(b,o.disables)
		"mo_3":
			var cell: Variant=p.get("cell")
			if not b.enemies.has(target) or b.enemies[target].type!="scout" or b.enemies[target].hp<=0 or b.enemies[target].disabled:return "invalid_target"
			if not valid_cell(cell) or rules.distance(h.cell,cell)>3 or rules.terrain(b,cell)!="." or rules.blocked(b,cell) or rules.occupied(b,cell) or b.barriers.has(str(cell)):return "invalid_target"
			b.beacons[target]={"cell":cell.duplicate(),"round":b.round+1}
		"jiang_1":
			if h.carrying.is_empty() or other.is_empty() or not other.carrying.is_empty() or other.left or other.downed or not p.get("consent",false):return "invalid_target"
			var length: int=rules.distance(h.cell,other.cell)
			if length<1 or length>(3 if lv>=5 else 2 if lv>=3 else 1):return "invalid_target"
			if length>1:
				if h.cell[0]!=other.cell[0] and h.cell[1]!=other.cell[1]:return "invalid_target"
				var direction: Array=[signi(int(other.cell[0])-int(h.cell[0])),signi(int(other.cell[1])-int(h.cell[1]))]
				for step: int in range(1,length):
					var at: Array=[h.cell[0]+step*direction[0],h.cell[1]+step*direction[1]]
					if rules.terrain(b,at)!="." or rules.blocked(b,at) or rules.occupied(b,at):return "invalid_target"
			for observer: String in [h.id,other.id]:
				if not s.actors.has(observer):continue
				for responsible: String in [other.id if observer==h.id else h.id,"leader"]:
					if observer=="jiang" and s.social.get(observer+">"+responsible,{}).get("band","") in ["conditional","rupture"] and b.get("handoff_priority","") not in ["people","cargo"]:return "relationship_safeguard_required"
			var carried: Dictionary=b.objects[h.carrying]
			rules.record_transport(carried,h.id,h.cell,other.cell)
			other.carrying=h.carrying;carried.carrier=other.id;h.carrying=""
		"jiang_3":
			if other.is_empty() or other.left or other.downed or not other.carrying.is_empty() or rules.distance(h.cell,other.cell)>1:return "invalid_target"
			var maximum: int=10
			if s.actors.has(target):maximum+=int(level(s.actors[target].xp)>=4)+int(level(s.actors[target].xp)>=6)
			if other.hp>=maximum or b.medicine<1:return "insufficient_resources"
			b.medicine-=1;other.hp=mini(maximum,other.hp+3)
		_:return "ability_unavailable"
	h.ap-=int(spec.ap)
	b.ability_uses[id]=int(b.ability_uses.get(id,0))+1
	return ""
static func valid_cell(cell: Variant) -> bool:
	if not cell is Array or cell.size()!=2:return false
	for n: Variant in cell:
		if not (n is int or n is float) or not is_finite(float(n)) or n!=int(n) or n<0 or n>7:return false
	return true
