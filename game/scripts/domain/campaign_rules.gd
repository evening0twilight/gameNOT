extends RefCounted
const Appraisal=preload("res://scripts/domain/appraisal.gd")
const Field=preload("res://scripts/domain/field_operations.gd")
const Crew=preload("res://scripts/domain/crew_journey.gd")
const Product=preload("res://scripts/domain/product_systems.gd")
const Full=preload("res://scripts/domain/full_campaign.gd")
const Hazards=preload("res://scripts/domain/chapter_hazards.gd")
const Chapter=preload("res://scripts/domain/chapter_one.gd")
const Social=preload("res://scripts/domain/campaign_social.gd")
const Specialties=preload("res://scripts/domain/p1_specialties.gd")
## Pure campaign transitions. All callers, including previews, use reduce.
static func fresh(content: Dictionary, campaign_id: String,options: Dictionary={}) -> Dictionary:
	var s := {"campaign":{"id":campaign_id,"day":1,"phase":"battle","mission_id":"M01","settled":{},"projects":0,"used":[],"talked":[],"difficulty":"standard","failure_modifier":false,"districts":content.domains.world.district_initial.duplicate(true)},"revision":0,"actors":{},"inventory":content.domains.economy.start.duplicate(true),"social":{},"story":{},"tutorial":{},"receipts":[],"commands":{},"rng":{"seed":"9223372036854775806","state":"9223372036854775806"},"battle":{}}
	for id: String in content.actors:
		var a: Dictionary = content.actors[id]
		s.actors[id] = {"id":id,"name":a.name,"join":int(a.join),"xp":[0,12,28,48][Full.chapter(int(a.join))-1],"fatigue":0,"ready_day":1,"training_completed":0,"tendency":"work","stress":10,"self_load":0}
	for relationship: Dictionary in content.domains.initial_relationships:
		s.social[relationship.id] = Social.create(relationship)
	Crew.initialize(s)
	Field.ensure(s)
	Appraisal.ensure(s)
	Chapter.ensure(s)
	Product.ensure(s)
	if options.get("difficulty","standard") in ["relaxed","standard","hard"]:s.campaign.difficulty=options.get("difficulty","standard")
	if options.get("variant","A") in ["A","B"]:s.product.variant=options.get("variant","A")
	deploy(s, content, "M01")
	return s

static func begin_campaign(content: Dictionary,campaign_id: String,options: Dictionary={}) -> Dictionary:
	var state: Dictionary=fresh(content,campaign_id,options)
	Crew.prepare_initial(state)
	return state

static func deploy(s: Dictionary, content: Dictionary, mission: String) -> void:
	Chapter.ensure(s)
	var board: Dictionary = content.boards[mission]
	s.campaign.mission_id = mission
	s.campaign.phase = "battle"
	var b := {"mission_id":mission,"round":1,"limit":int(board.round_limit),"rows":board.rows.duplicate(),"heroes":{},"objects":{},"enemies":{},"intents":{},"variant":"A","difficulty":"standard","used_markers":{},"queued_reinforcements":[],"deployed_tools":{},"undo":[],"ability_uses":{},"marks":{},"move_bonuses":{},"round_markers":{},"authorizations":[],"cover":{},"barriers":{},"insulation":[],"beacons":{},"medicine":0,"branch":"","spawn_count":0,"protection":[],"reinforcement":board.reinforcement.duplicate(true)}
	s.battle = b
	b.medicine=s.full_campaign.packed;s.full_campaign.packed=0
	var party: Array = s.chapter_one.roster.duplicate()
	s.chapter_one.roster=[]
	for id: String in content.actors:
		var a: Dictionary = s.actors[id]
		if not s.product.withdrawn.has(id) and Crew.joined(s,id) and a.ready_day <= s.campaign.day and a.fatigue + 18 <= 100 and party.size() < 3 and not party.has(id):
			party.append(id)
	while party.size() < 3:
		party.append("responder_%s_%d" % [mission,party.size()])
	for i: int in range(3):
		var id: String = party[i]
		b.heroes[id] = {"id":id,"cell":board.spawns[i].duplicate(),"hp":10,"ap":2,"carrying":"","left":false,"downed":false,"stabilized":false,"deadline":0}
		if s.actors.has(id):
			var lv: int=Specialties.level(int(s.actors[id].xp))
			b.heroes[id].hp=10+(1 if lv>=4 else 0)+(1 if lv>=6 else 0)
			s.actors[id].fatigue += 18
			if not s.chapter_one.worked.has(id):s.chapter_one.worked.append(id)
	for source: Dictionary in board.objectives + board.controls:
		if not Full.objective_active(s,board,source):continue
		var o := source.duplicate(true)
		o.merge({"sustain_until_exit":source.get("sustain_until_exit",false),"progress":0,"completed":false,"delivered":false,"lost":false,"carrier":"","stable":source.get("initial_stable",false),"contributors":[],"transport_path":[]},true)
		b.objects[o.id] = o
	for source: Dictionary in board.enemies:
		var e := source.duplicate(true)
		e.hp = Hazards.definition(content,e.type).get("hp",3)
		e.disabled = false
		b.enemies[e.id] = e
	if s.campaign.failure_modifier and board.kind=="main":
		for cell: Array in board.failure_modifier.preferred_cells:
			if terrain(b,cell) == "." and not contains_cell(board.exits,cell):
				set_terrain(b,cell,":")
				break
	Product.deploy(s,board)
	Field.deploy(s,content)
	lock_intents(b)

static func same(a: Array, b: Array) -> bool:
	return int(a[0]) == int(b[0]) and int(a[1]) == int(b[1])
static func contains_cell(cells: Array, cell: Array) -> bool:
	for c: Array in cells:
		if same(c,cell): return true
	return false
static func distance(a: Array,b: Array) -> int:
	return absi(int(a[0])-int(b[0]))+absi(int(a[1])-int(b[1]))
static func terrain(b: Dictionary,c: Array) -> String:
	if c.size()!=2 or c[0]<0 or c[0]>7 or c[1]<0 or c[1]>7: return "#"
	return b.rows[int(c[1])].substr(int(c[0]),1)
static func set_terrain(b: Dictionary,c: Array,glyph: String) -> void:
	var row: String = b.rows[int(c[1])]
	b.rows[int(c[1])] = row.substr(0,int(c[0]))+glyph+row.substr(int(c[0])+1)
static func blocked(b: Dictionary,c: Array) -> bool:
	if terrain(b,c) in ["#","X"]: return true
	for e: Dictionary in b.enemies.values():
		if e.hp>0 and same(e.cell,c): return true
	return false
static func occupied(b: Dictionary,c: Array) -> bool:
	for h: Dictionary in b.heroes.values():
		if not h.left and not h.downed and same(h.cell,c): return true
	return false
static func move_cost(b: Dictionary,start: Array,target: Array,budget: int) -> int:
	if same(start,target) or blocked(b,target) or occupied(b,target): return -1
	var queue: Array = [[start,0]]
	var best: Dictionary = {str(start):0}
	while not queue.is_empty():
		var entry: Array = queue.pop_front()
		for d: Array in [[0,-1],[-1,0],[1,0],[0,1]]:
			var c: Array = [int(entry[0][0])+d[0],int(entry[0][1])+d[1]]
			if blocked(b,c): continue
			var cost: int = int(entry[1]) + (2 if terrain(b,c) in ["~",":"] else 1)
			if cost>budget or cost>=best.get(str(c),999): continue
			best[str(c)] = cost
			queue.append([c,cost])
	return int(best.get(str([int(target[0]),int(target[1])]),-1))

static func lock_intents(b: Dictionary) -> void:
	Hazards.plan_reinforcements(b,load("res://scripts/domain/campaign_rules.gd"))
	b.intents = {}
	for id: String in b.enemies:
		var e: Dictionary = b.enemies[id]
		if e.hp<=0 or e.disabled: continue
		var nearest: Dictionary = {}
		var ids: Array = b.heroes.keys()
		ids.sort()
		for hero_id: String in ids:
			var h: Dictionary = b.heroes[hero_id]
			if h.left or h.downed: continue
			if nearest.is_empty() or distance(e.cell,h.cell)<distance(e.cell,nearest.cell): nearest=h
		if e.type=="skimmer" and int(b.round)%2==1:Hazards.plan_skimmer(b,e,load("res://scripts/domain/campaign_rules.gd"))
		if e.type in ["welder","sentinel"] and int(b.round)%2==0 and e.has("charge_direction"):
			b.intents[id]=e.charge_direction.duplicate();continue
		if b.beacons.has(id) and b.beacons[id].round==b.round:nearest={"cell":b.beacons[id].cell}
		var direction: Array = [0,1]
		if not nearest.is_empty():
			var dx: int = int(nearest.cell[0])-int(e.cell[0])
			var dy: int = int(nearest.cell[1])-int(e.cell[1])
			direction = [signi(dx),0] if absi(dx)>=absi(dy) else [0,signi(dy)]
		b.intents[id] = direction
		if e.type in ["welder","sentinel"]:e.charge_direction=direction.duplicate()

static func reject(code: String,revision: int) -> Dictionary:
	return {"ok":false,"error_code":code,"expected_revision":revision,"events":[],"costs":{},"risk_disclosure":[]}

static func reduce(snapshot: Dictionary,command: Dictionary,content: Dictionary) -> Dictionary:
	var revision: int = int(snapshot.revision)
	for field: String in ["command_id","kind","actor_id","root_decision_id"]:
		if not command.get(field) is String or (field != "actor_id" and command[field].is_empty()): return reject("invalid_command",revision)
	if not command.get("payload") is Dictionary or not command.has("expected_revision"): return reject("invalid_command",revision)
	if snapshot.commands.has(command.command_id):
		if snapshot.commands[command.command_id] != JSON.stringify(command,"",true): return reject("command_id_conflict",revision)
		return {"ok":true,"error_code":"","next_state":snapshot.duplicate(true),"events":[],"costs":{},"risk_disclosure":[],"expected_revision":revision,"next_rng":snapshot.rng.duplicate(),"duplicate":true}
	if command.expected_revision != revision: return reject("stale_revision",revision)
	var s := snapshot.duplicate(true)
	var before_count: int = s.receipts.size()
	if command.kind=="undo":
		if s.campaign.phase!="battle" or s.battle.undo.is_empty():return reject("undo_boundary",revision)
		var history: Array=s.battle.undo.duplicate(true)
		var restored: Dictionary=history.pop_back()
		restored.battle.undo=history
		restored.commands=s.commands.duplicate(true)
		restored.revision=revision
		s=restored
		before_count=s.receipts.size()
	elif s.campaign.phase=="battle" and command.kind not in ["end_round","emergency_retreat","authorize","promise_retreat"]:
		var checkpoint:=snapshot.duplicate(true)
		checkpoint.battle.undo=[]
		s.battle.undo.append(checkpoint)

	var error: String = "" if command.kind=="undo" else apply(s,command,content)
	if not error.is_empty(): return reject(error,revision)
	if s.battle.has("safety") and snapshot.battle.mission_id==s.battle.mission_id:
		s.battle.safety=s.battle.safety.filter(func(mark):return mark.round==s.battle.round and s.battle.heroes.has(mark.actor) and same(s.battle.heroes[mark.actor].cell,mark.origin) and not s.battle.heroes[mark.actor].left and not s.battle.heroes[mark.actor].downed)
	Full.after_action(s,command,content)
	preload("res://scripts/presentation/guidance.gd").record(s,snapshot,command,content)
	if command.kind in ["end_round","emergency_retreat","authorize","promise_retreat"] or s.campaign.phase!="battle" or s.battle.get("branch","")!=snapshot.battle.get("branch","") or (command.kind=="pickup" and s.full_campaign.contracts!=snapshot.full_campaign.contracts):s.battle.undo=[]
	s.revision += 1
	s.commands[command.command_id] = JSON.stringify(command,"",true)
	var event := {"id":"%s/%s/%d/%s/%s" % [s.campaign.id,s.campaign.mission_id,s.revision,command.kind,command.actor_id],"seq":s.receipts.size()+1,"command_id":command.command_id,"source_state_revision":revision,"campaign_day":s.campaign.day,"round":s.battle.round,"actor_ids":[command.actor_id],"observer_ids":s.battle.heroes.keys(),"object_id":command.payload.get("target",""),"previous_state":{"revision":revision},"next_state":{"revision":s.revision},"resource_delta":{},"promise_id":"","information_scope":"team","root_decision_id":command.root_decision_id,"first_known_day":s.campaign.day,"occurrence_day":s.campaign.day,"responsibility_shares":{},"kind":command.kind}
	for key: String in s.inventory:
		event.resource_delta[key] = s.inventory[key]-snapshot.inventory[key]
	s.receipts.append(event)
	for pair: String in s.social:
		if s.social[pair]==snapshot.social[pair]:continue
		var social_event: Dictionary=event.duplicate(true)
		social_event.kind="relationship_changed"
		social_event.object_id=pair
		social_event.id="%s/%s/%d/relationship_changed/%s" % [s.campaign.id,s.battle.mission_id,s.revision,pair]
		social_event.seq=s.receipts.size()+1
		social_event.previous_state=snapshot.social[pair].duplicate(true)
		social_event.next_state=s.social[pair].duplicate(true)
		social_event.resource_delta={}
		social_event.appraisal_roots=[]
		for key: String in s.appraisal.events:
			var fact: Dictionary=s.appraisal.events[key]
			if fact.observer==pair.split(">")[0] and fact!=snapshot.appraisal.events.get(key,{}):social_event.appraisal_roots.append(key)
		s.receipts.append(social_event)
	if s.campaign.settled.size()>snapshot.campaign.settled.size():
		var settled: Dictionary = event.duplicate(true)
		settled.kind="mission_settled"
		settled.object_id=s.battle.mission_id
		settled.id="%s/%s/%d/mission_settled/%s" % [s.campaign.id,s.battle.mission_id,s.revision,s.battle.mission_id]
		settled.seq=s.receipts.size()+1
		settled.next_state=s.campaign.last_result.duplicate(true)
		s.receipts.append(settled)
		for object_id: String in s.campaign.last_result.facts:
			var fact: Dictionary = event.duplicate(true)
			fact.kind="objective_result"
			fact.id="%s/%s/%d/objective_result/%s" % [s.campaign.id,s.battle.mission_id,s.revision,object_id]
			fact.seq=s.receipts.size()+1
			fact.object_id=object_id
			fact.resource_delta={}
			fact.next_state={"result":s.campaign.last_result.facts[object_id]}
			s.receipts.append(fact)
	var ap_cost: int = 0
	if snapshot.battle.heroes.has(command.actor_id) and s.battle.heroes.has(command.actor_id): ap_cost = maxi(0,int(snapshot.battle.heroes[command.actor_id].ap)-int(s.battle.heroes[command.actor_id].ap))
	return {"ok":true,"error_code":"","next_state":s,"events":s.receipts.slice(before_count),"costs":{"ap":ap_cost,"resources":event.resource_delta},"risk_disclosure":s.campaign.get("last_result",{}),"expected_revision":revision,"next_rng":s.rng.duplicate()}

static func apply(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	var kind: String = c.kind
	var p: Dictionary = c.payload
	var b: Dictionary = s.battle
	var board: Dictionary = content.boards[b.mission_id]
	Chapter.ensure(s)
	if kind in ["use_tool","cross_anchor"]:
		if s.campaign.phase!="battle":return "invalid_phase"
		return Product.use_tool(s,c,content,load("res://scripts/domain/campaign_rules.gd"))
	if c.kind=="community_report":
		if s.campaign.phase!="settlement" or not s.battle.mission_id.begins_with("M"):return "invalid_phase"
		var flag: String="community."+s.battle.mission_id+".public"
		if s.chapter_one.flags.has(flag):return "already_used"
		if not c.payload.get("choice") in ["publish","archive"]:return "invalid_target"
		s.chapter_one.flags[flag]=c.payload.choice=="publish"
		return ""
	if kind=="plan_next_roster":
		if s.campaign.phase!="camp" or not Crew.valid_draft(s,p):return "invalid_target"
		s.journey.draft=p.duplicate(true);s.journey.next_mission="M%02d"%(s.chapter_one.main_completed+1);return ""
	if kind=="declare_priority":
		if s.campaign.phase!="battle" or p.get("priority") not in ["people","cargo"]:return "invalid_target"
		b.handoff_priority=p.priority;return ""
	if kind=="decline_side":
		if s.campaign.phase!="settlement" or not Chapter.side_available(s,content).has(p.get("mission")):return "side_unavailable"
		s.journey.declined_sides.append(p.mission);return ""
	if kind=="save_preparation":return Crew.draft(s,c)
	if kind=="acknowledge_recruit":
		var recruit_id: String=str(p.get("actor",""))
		if not Crew.joined(s,recruit_id):return "unavailable_actor"
		if s.campaign.phase not in ["briefing","camp","settlement"]:return "invalid_phase"
		if p.has("roster"):
			var draft: Dictionary=s.journey.draft.duplicate(true)
			draft.roster=p.roster
			if draft.get("support","") in draft.roster:draft.support=""
			if not Crew.valid_draft(s,draft) or not draft.roster.has(recruit_id):return "invalid_roster"
			s.journey.draft=draft
			if s.campaign.phase!="briefing":s.journey.next_mission="M%02d"%mini(24,s.chapter_one.main_completed+1)
		if not s.journey.introduced.has(recruit_id):s.journey.introduced.append(recruit_id)
		return ""
	if kind=="depart":return Chapter.depart(s,c,content,load("res://scripts/domain/campaign_rules.gd"))
	if kind=="start_side":return Chapter.command(s,c,content,load("res://scripts/domain/campaign_rules.gd"))
	if kind == "enter_camp":
		if s.campaign.phase != "settlement" or s.campaign.day>=24: return "invalid_phase"
		s.campaign.phase = "camp"
		return ""
	if s.campaign.phase == "camp": return camp(s,c,content)
	if s.campaign.phase != "battle": return "invalid_phase"
	if kind=="service_watch":return Field.watch(s,c,load("res://scripts/domain/campaign_rules.gd"))
	if kind=="restore_power":return Field.restore(s,c,load("res://scripts/domain/campaign_rules.gd"))
	if kind=="protocol":return preload("res://scripts/domain/p1_protocols.gd").apply(s,c,load("res://scripts/domain/campaign_rules.gd"))
	if kind=="specialty":return Specialties.apply(s,c,content,load("res://scripts/domain/campaign_rules.gd"))
	if kind=="authorize":
		if not b.heroes.has(c.actor_id):return "unavailable_actor"
		if b.authorizations.has(c.actor_id):return "already_used"
		b.authorizations.append(c.actor_id)
		return ""
	if kind=="promise_retreat":
		if b.has("retreat_promise"):return "already_used"
		b.retreat_promise={"deadline":b.limit-2,"id":c.command_id,"resolved":false}
		return ""
	if kind == "emergency_retreat":
		if not p.get("confirmed",false): return "confirmation_required"
		settle(s,content)
		return ""
	if kind == "end_round":
		resolve_round(s,content)
		return ""
	if not b.heroes.has(c.actor_id): return "unavailable_actor"
	var h: Dictionary = b.heroes[c.actor_id]
	if h.left or h.downed: return "unavailable_actor"
	var cost: int = 0 if kind in ["drop","wait"] else 1
	if h.ap<cost: return "insufficient_ap"
	var target: String = str(p.get("target",""))
	var o: Dictionary = b.objects.get(target,{})
	match kind:
		"prepare_safety":
			if not h.carrying.is_empty():return "carrying_restriction"
			if not b.heroes.has(target) or target==h.id or b.heroes[target].left or b.heroes[target].downed or distance(h.cell,b.heroes[target].cell)!=1 or terrain(b,h.cell)!=".":return "invalid_target"
			if p.get("protocol") not in ["protected_work","mutual_cover"]:return "invalid_target"
			for mark: Dictionary in b.safety:
				if mark.actor==h.id and mark.round==b.round:return "already_used"
			b.safety.append({"actor":h.id,"target":target,"protocol":p.protocol,"round":b.round,"origin":h.cell.duplicate()})
		"move":
			var cell: Variant = p.get("cell")
			if not cell is Array or cell.size()!=2: return "invalid_target"
			for coordinate: Variant in cell:
				if not (coordinate is float or coordinate is int) or not is_finite(float(coordinate)) or coordinate!=int(coordinate): return "invalid_target"
			var budget: int=movement_budget(s,h.id)
			var passive: bool=movement_passive(s,h.id)
			if b.barriers.has(str([int(cell[0]),int(cell[1])])) or move_cost(b,h.cell,cell,budget)<0: return "invalid_target"
			var previous_cell: Array=h.cell.duplicate()
			h.cell = [int(cell[0]),int(cell[1])]
			if not h.carrying.is_empty():record_transport(b.objects[h.carrying],h.id,previous_cell,h.cell)
			if passive:b.used_markers["move:"+h.id]=true
			b.move_bonuses.erase(h.id)
		"push":
			if not h.carrying.is_empty(): return "carrying_restriction"
			if not b.enemies.has(target) or b.enemies[target].hp<=0 or distance(h.cell,b.enemies[target].cell)!=1: return "invalid_target"
			var enemy: Dictionary = b.enemies[target]
			var destination: Array = [2*int(enemy.cell[0])-int(h.cell[0]),2*int(enemy.cell[1])-int(h.cell[1])]
			if enemy.type in ["hauler","sentinel"]:
				var marker: Dictionary=enemy.get("push_marker",{})
				var direction: Array=[int(destination[0])-int(enemy.cell[0]),int(destination[1])-int(enemy.cell[1])]
				if marker.get("round",0)!=b.round or marker.get("direction",[])!=direction:marker={"round":b.round,"direction":direction,"count":0}
				marker.count+=1;enemy.push_marker=marker
				if marker.count<2:h.ap-=cost;return ""
				enemy.erase("push_marker")
			if blocked(b,destination) or occupied(b,destination) or (enemy.type=="hauler" and not contains_cell(enemy.rail,destination)):enemy.hp=maxi(0,int(enemy.hp)-1)
			else:enemy.cell=destination
		"attack":
			if not h.carrying.is_empty(): return "carrying_restriction"
			if not b.enemies.has(target) or b.enemies[target].hp<=0 or distance(h.cell,b.enemies[target].cell)!=1: return "invalid_target"
			b.enemies[target].hp = maxi(0,int(b.enemies[target].hp)-(3 if b.marks.has(target) else 2))
			b.marks.erase(target)
		"stabilize","pickup","interact":
			if o.is_empty() or o.lost or o.completed or not o.carrier.is_empty() or distance(h.cell,o.cell)>1: return "invalid_target"
			for prerequisite: String in o.prerequisites:
				if not b.objects[prerequisite].completed: return "prerequisite_required"
			if kind == "stabilize":
				if o.kind != "rescue" or o.stable: return "invalid_target"
				o.stable = true
				if o.has("crew_id"):
					b.heroes[o.crew_id].deadline+=1
					b.heroes[o.crew_id].stabilized=true
			elif kind == "pickup":
				if not o.kind in ["rescue","cargo"] or not o.stable or not h.carrying.is_empty(): return "invalid_target"
				h.carrying = target
				o.carrier = h.id
			else:
				if o.kind in ["channel","convoy"]:
					if o.get("active",false):return "already_used"
					o.active=true;o.timer=0;o.waypoint=0
					if not o.contributors.has(h.id):o.contributors.append(h.id)
					h.ap-=cost
					return ""
				if o.kind != "work": return "invalid_target"
				if b.mission_id=="M17" and o.has("branch"):
					if not b.branch.is_empty() and b.branch!=o.branch:return "branch_locked"
					b.branch=o.branch
				var amount: int=1
				var actor: Dictionary=s.actors.get(h.id,{})
				if not actor.is_empty() and Specialties.level(int(actor.xp))>=2 and (actor.tendency=="work" or Specialties.level(int(actor.xp))>=6) and not b.used_markers.has("work:"+h.id):
					amount=2
					b.used_markers["work:"+h.id]=true
				o.progress = mini(int(o.work),int(o.progress)+amount)
				o.completed = o.progress>=o.work
				if o.completed and o.has("disables"): shutdown(b,o.disables)
			if kind!="pickup" and not o.contributors.has(h.id): o.contributors.append(h.id)
		"drop":
			if h.carrying.is_empty(): return "invalid_target"
			b.objects[h.carrying].carrier=""
			var destination: Variant=p.get("cell",h.cell)
			if not Product.valid_cell(destination) or distance(h.cell,destination)>1 or blocked(b,destination) or b.barriers.has(str(destination)) or (not same(h.cell,destination) and occupied(b,destination)):return "invalid_target"
			b.objects[h.carrying].cell=destination.duplicate()
			h.carrying=""
		"extract","leave_site":
			if not contains_cell(Field.exits(b,board),h.cell): return "invalid_target"
			if kind=="extract" and h.carrying.is_empty(): return "invalid_target"
			if not h.carrying.is_empty():
				var carried: Dictionary = b.objects[h.carrying]
				carried.completed=true
				carried.delivered=true
				carried.carrier=""
				if carried.has("crew_id"): b.heroes[carried.crew_id].left=true
				if not carried.contributors.has(h.id): carried.contributors.append(h.id)
				h.carrying=""
			if kind=="leave_site": h.left=true
		"wait": pass
		_: return "unknown_command"
	h.ap-=cost
	var active: int = 0
	for hero: Dictionary in b.heroes.values():
		if not hero.left and not hero.downed: active+=1
	if active==0: settle(s,content)
	return ""

static func hurt(b: Dictionary,h: Dictionary,damage: int) -> void:
	if h.left or h.downed: return
	h.hp=maxi(0,int(h.hp)-damage)
	if h.hp==0:
		h.downed=true
		h.ap=0
		h.deadline=b.round+2
		b.objects["casualty_"+h.id]={"id":"casualty_"+h.id,"crew_id":h.id,"label":"救援失能队员 "+h.id,"kind":"rescue","cell":h.cell.duplicate(),"work":0,"hp":1,"prerequisites":[],"sustain_until_exit":false,"progress":0,"completed":false,"delivered":false,"lost":false,"carrier":"","stable":false,"contributors":[],"transport_path":[]}

		if not h.carrying.is_empty():
			b.objects[h.carrying].cell=h.cell.duplicate()
			b.objects[h.carrying].carrier=""
			h.carrying=""

static func resolve_round(s: Dictionary,content: Dictionary) -> void:
	var b: Dictionary = s.battle
	var board: Dictionary = content.boards[b.mission_id]
	b.electrified_hits=[]
	var ids: Array = b.enemies.keys()
	ids.sort()
	for id: String in ids:
		var e: Dictionary = b.enemies[id]
		if e.hp<=0 or e.disabled or not b.intents.has(id): continue
		Hazards.resolve(b,e,load("res://scripts/domain/campaign_rules.gd"))
	var water: Dictionary = b.environment.water_addition
	if b.round==water.round:
		for cell: Array in water.cells: set_terrain(b,cell,"~")
	Hazards.environment(b,board,load("res://scripts/domain/campaign_rules.gd"))
	Field.end_round(s,load("res://scripts/domain/campaign_rules.gd"))
	for h: Dictionary in b.heroes.values():
		if h.downed and not h.left and b.round>=h.deadline:
			h.left=true
			var casualty: Dictionary = b.objects["casualty_"+h.id]
			casualty.lost=true
			if not casualty.carrier.is_empty(): b.heroes[casualty.carrier].carrying=""
			casualty.carrier=""
	if b.round>=b.limit:
		settle(s,content)
		return
	resolve_promise(s,content)
	b.round+=1
	for key: String in b.barriers.keys():
		if b.barriers[key].expires>0 and b.barriers[key].expires<=b.round:b.barriers.erase(key)
	b.marks={}
	b.cover={}
	b.move_bonuses={}
	b.round_markers={}
	for h: Dictionary in b.heroes.values():
		h.ap=0 if h.downed or h.left else 2
	lock_intents(b)

static func settle(s: Dictionary,content: Dictionary) -> void:
	var b: Dictionary = s.battle
	if s.campaign.settled.has(b.mission_id): return
	var board: Dictionary = content.boards[b.mission_id]
	var all_groups: bool = true
	var milestone: bool = false
	for group: Array in Full.groups(s,board):
		var secured: bool = false
		for id: String in group:
			var o: Dictionary = b.objects[id]
			milestone = milestone or o.completed
			secured = secured or (o.completed and (not o.sustain_until_exit or o.hp>0))
		all_groups = all_groups and secured
	var outcome: String = "success" if all_groups else ("partial" if milestone else "failed")
	var reward: Dictionary = content.domains.economy["side_rewards" if board.kind=="side" else "main_rewards"][outcome].duplicate()
	var responders: int = 0
	var injured: Array = []
	var xp_receipts: Dictionary={}
	var reward_rows: Array=[{"reason":"任务基础结算","resources":reward.duplicate()}]
	for id: String in b.heroes:
		var h: Dictionary = b.heroes[id]
		if not s.actors.has(id):
			responders+=1
			continue
		var old_xp: int=s.actors[id].xp
		s.actors[id].xp=mini(100,s.actors[id].xp+int(content.domains.economy.growth["side_xp" if board.kind=="side" else "main_xp"][outcome]))
		xp_receipts[id]={"before":old_xp,"after":s.actors[id].xp,"source":"main" if board.kind=="main" else "side"}
		if h.downed or (not h.left and not contains_cell(Field.exits(b,board),h.cell)):
			s.actors[id].ready_day=s.campaign.day+2
			injured.append(id)
			if b.difficulty=="hard" and h.downed and not b.objects.get("casualty_"+id,{}).get("delivered",false):
				if not s.product.withdrawn.has(id):s.product.withdrawn.append(id)
				s.product.loadout[id]={"tool":"","support":""}
	if board.kind=="main":
		var fee: int=int(reward.credits)-maxi(6,int(reward.credits)-4*responders)
		reward.credits-=fee
		if responders>0:reward_rows.append({"reason":"临时响应员费用（最低保留6资金）","resources":{"credits":-fee}})
	for entry: Dictionary in content.domains.economy.objective_rewards:
		if entry.mission==b.mission_id and b.objects.has(entry.objective) and b.objects[entry.objective].completed and not b.objects[entry.objective].lost and (not b.objects[entry.objective].sustain_until_exit or b.objects[entry.objective].hp>0):
			reward_rows.append({"reason":b.objects[entry.objective].label,"resources":entry.reward.duplicate()})
			for key: String in entry.reward: reward[key]+=entry.reward[key]
	for key: String in reward: s.inventory[key]+=reward[key]
	var facts: Dictionary = {}
	for o: Dictionary in b.objects.values():
		facts[o.id]="saved" if o.delivered else ("lost" if o.lost else ("completed" if o.completed else "unresolved"))
	for mission: Dictionary in content.domains.world.missions:
		if mission.id==b.mission_id:
			s.campaign.districts[mission.district]=clampi(int(s.campaign.districts[mission.district])+int(mission.infrastructure_delta[outcome]),0,3)
	for object: Dictionary in b.objects.values():
		if object.delivered:
			for step: Dictionary in object.transport_path:
				if not step.actor.is_empty() and not object.contributors.has(step.actor):object.contributors.append(step.actor)
	resolve_promise(s,content,true)
	Appraisal.positives(s,content)
	Appraisal.personal(s,content,outcome,injured)
	s.campaign.last_result={"mission":b.mission_id,"outcome":outcome,"reward":reward,"injured":injured,"withdrawn":s.product.withdrawn.filter(func(id):return b.heroes.has(id)),"difficulty":b.difficulty,"variant":b.variant,"facts":facts,"xp_receipts":xp_receipts,"reward_rows":reward_rows}
	s.campaign.settled[b.mission_id]=s.campaign.last_result.duplicate(true)
	if board.kind=="main":s.campaign.failure_modifier=outcome=="failed"
	s.campaign.last_result.recruits=Crew.recruit(s,b.mission_id)
	Chapter.settled(s,board)
	Field.settled(s,content)
	Full.settlement(s,content)
	s.campaign.phase="settlement"

static func camp(s: Dictionary,c: Dictionary,content: Dictionary) -> String:
	var id: String = c.actor_id
	if c.kind in ["repair_event","schedule_repair"]:return Appraisal.repair_command(s,c)
	if c.kind in ["repair_field_facility","field_assistance"]:return Field.camp(s,c,content)
	if c.kind=="history_repair":return preload("res://scripts/domain/history_repair.gd").apply(s,c,content)
	if c.kind in ["buy_supplies","buy_tool","refund_tool","equip_tool","upgrade_facility"]:return Product.camp(s,c,content)
	if c.kind in ["select_route","review_record","craft_medicine","publish_record"]:return Full.command(s,c,content)
	if c.kind in ["story_open","story_choice","story_defer"]:return preload("res://scripts/domain/chapter_stories.gd").apply(s,c,content)
	if c.kind=="finish_evening":return Chapter.finish_evening(s,content,load("res://scripts/domain/campaign_rules.gd"))
	if c.kind=="next_mission":return Chapter.command(s,c,content,load("res://scripts/domain/campaign_rules.gd"))
	if c.kind=="mentor":return Chapter.mentor(s,c)
	if c.kind in ["train","treat","rest"]:return Chapter.group_project(s,c)
	if not s.actors.has(id) or not Crew.joined(s,id): return "unavailable_actor"
	var a: Dictionary = s.actors[id]
	if c.kind=="tendency":
		if not c.payload.get("choice") in ["work","move"]:return "invalid_target"
		a.tendency=c.payload.choice
		return ""
	if c.kind=="acknowledge":
		var pair: String=id+">"+str(c.payload.get("target","leader"))
		if s.campaign.talked.size()>=2 or s.campaign.talked.has("ack:"+id):return "project_used"
		if not s.social.has(pair):return "invalid_target"
		var r: Dictionary=s.social[pair]
		var acknowledged: Dictionary=Social.Legacy.acknowledge(r,str(c.payload.get("event","")))
		if acknowledged==r:return "invalid_target"
		for memory: Dictionary in acknowledged.memories:
			if memory.id==str(c.payload.get("event","")):memory.ack_revision=s.revision+1;memory.ack_day=s.campaign.day
		s.social[pair]=Social.refresh(acknowledged,s.campaign.day,a.stress)
		for conflict: Dictionary in s.appraisal.conflicts:
			if conflict.pair==pair and conflict.event==str(c.payload.get("event","")):conflict.status="acknowledged"
		s.campaign.talked.append("ack:"+id)
		return ""
	if c.kind=="agreement":
		var target: String=str(c.payload.get("target",""))
		var choice: String=str(c.payload.get("choice",""))
		if target==id or not s.actors.has(target) or not Crew.joined(s,target) or not choice in ["professional","cooperate"]:return "invalid_target"
		var r: Dictionary=s.social[id+">"+target]
		if r.agreement==choice:return "already_used"
		if r.renegotiated_day==s.campaign.day or s.campaign.talked.size()>=2:return "project_used"
		for pair: String in [id+">"+target,target+">"+id]:
			s.social[pair].agreement=choice
			s.social[pair].renegotiated_day=s.campaign.day
			if choice=="professional":
				for conflict: Dictionary in s.appraisal.conflicts:
					if conflict.pair==pair:conflict.status="professional"
		s.campaign.talked.append("agreement:"+id+":"+target)
		return ""
	if c.kind=="short_talk":
		var target: String = str(c.payload.get("target",""))
		var pair: String = id+">"+target
		if not s.social.has(pair) or not s.actors.has(target) or not Crew.joined(s,target) or s.campaign.talked.size()>=2 or s.campaign.talked.has(pair): return "invalid_target"
		s.social[pair].closeness=mini(100,int(s.social[pair].closeness)+3)
		s.campaign.talked.append(pair)
		Appraisal.support(s,id);Appraisal.support(s,target)
		return ""
	return "unknown_command"

static func resolve_promise(s: Dictionary,content: Dictionary,settling: bool=false) -> void:
	var b: Dictionary=s.battle
	if not b.has("retreat_promise") or b.retreat_promise.resolved:return
	var promise: Dictionary=b.retreat_promise
	if not settling and b.round<int(promise.deadline):return
	promise.resolved=true
	var kept: bool=settling and b.round<=int(promise.deadline)
	promise.kept=kept
	for id: String in b.heroes:
		if not s.actors.has(id):continue
		var pair: String=id+">leader"
		if kept:
			for m: Dictionary in s.social[pair].memories:
				if m.stage==1 and m.remedy=="keep_agreement":
					s.social[pair]=Social.Legacy.repair(s.social[pair],m.id,b.mission_id+":kept-promise","keep_agreement")
		else:
			Appraisal.record(s,content,{"root":b.mission_id+":retreat-promise","observers":[id],"known":true,"shares":{"leader":1.0},"family":"breach","deliberate":true,"warned":true,"reason":"已接受第%d轮前撤离，实际未按约撤离"%promise.deadline})


static func record_transport(object: Dictionary,actor: String,origin: Array,destination: Array) -> void:
	var path: Array=object.transport_path
	if path.is_empty():path.append({"cell":origin.duplicate(),"actor":""})
	for i: int in range(path.size()):
		if same(path[i].cell,destination):
			object.transport_path=path.slice(0,i+1)
			return
	path.append({"cell":destination.duplicate(),"actor":actor})

static func shutdown(b: Dictionary,id: String) -> void:
	var enemy: Dictionary=b.enemies[id]
	for required: String in enemy.disable_requires:
		if not b.objects[required].completed:return
	enemy.disabled=true

static func movement_passive(s: Dictionary,id: String) -> bool:
	var h: Dictionary=s.battle.heroes[id]
	var actor: Dictionary=s.actors.get(id,{})
	return not actor.is_empty() and Specialties.level(int(actor.xp))>=2 and (actor.tendency=="move" or Specialties.level(int(actor.xp))>=6) and h.carrying.is_empty() and not s.battle.used_markers.has("move:"+id)
static func movement_budget(s: Dictionary,id: String) -> int:
	var h: Dictionary=s.battle.heroes[id]
	var improved_carry: bool=(id=="he" and Specialties.level(int(s.actors.he.xp))>=3) or s.battle.equipment.get(id,{}).get("support","")=="stretcher"
	var budget: int=3 if h.carrying.is_empty() or improved_carry else 2
	return budget+(1 if h.carrying.is_empty() and (movement_passive(s,id) or s.battle.move_bonuses.has(id)) else 0)
static func reachable_cells(s: Dictionary,id: String) -> Array:
	if not s.battle.heroes.has(id):return []
	var h: Dictionary=s.battle.heroes[id]
	if h.left or h.downed or h.ap<1:return []
	var b: Dictionary=s.battle
	var budget: int=movement_budget(s,id)
	var start: Array=[int(h.cell[0]),int(h.cell[1])]
	var best: Dictionary={str(start):0}
	var queue: Array=[[start,0]]
	while not queue.is_empty():
		var entry: Array=queue.pop_front()
		for offset: Array in [[0,-1],[-1,0],[1,0],[0,1]]:
			var cell: Array=[int(entry[0][0])+offset[0],int(entry[0][1])+offset[1]]
			if blocked(b,cell):continue
			var cost: int=int(entry[1])+(2 if terrain(b,cell) in ["~",":"] else 1)
			if cost>budget or cost>=int(best.get(str(cell),999)):continue
			best[str(cell)]=cost;queue.append([cell,cost])
	var cells: Array=[]
	for y: int in range(8):
		for x: int in range(8):
			var cell: Array=[x,y]
			if not same(cell,start) and best.has(str(cell)) and not occupied(b,cell) and not b.barriers.has(str(cell)):cells.append(cell)
	return cells
