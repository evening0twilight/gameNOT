extends "res://tests/full_playthrough.gd"
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
var used: Dictionary={}
var failures: Array=[]
var growth: Array=[]
func specialty(actor: String,payload: Dictionary,benefit: String) -> bool:
	if used.has(payload.ability):return false
	var before: Dictionary=s.battle.duplicate(true)
	if not attempt("specialty",actor,payload):return false
	used[payload.ability]={"day":s.campaign.day,"mission":s.battle.mission_id,"round":before.round,"actor":actor,"xp":s.actors[actor].xp,"cell":before.heroes[actor].cell,"payload":payload,"benefit":benefit,"before":before,"after":s.battle.duplicate(true)}
	return true
func tick(actor: String,goal: String,board: Dictionary) -> bool:
	var h: Dictionary=s.battle.heroes[actor]
	if h.ap<=0 or h.downed or h.left:return false
	var o: Dictionary=s.battle.objects.get(goal,{})
	if actor=="lin" and o.get("kind","")=="rescue" and not o.stable:
		if specialty(actor,{"ability":"lin_1","target":goal},"stabilized at actual distance %d"%Rules.distance(h.cell,o.cell)):return true
	if actor=="xu" and not o.is_empty() and h.carrying.is_empty():
		for y: int in range(8):
			for x: int in range(8):
				var cell: Array=[x,y]
				if Rules.distance(cell,o.cell)>=Rules.distance(h.cell,o.cell):continue
				if Rules.move_cost(s.battle,h.cell,cell,Rules.movement_budget(s,actor))>=0:continue
				if specialty(actor,{"ability":"xu_1","cell":cell},"crossed to a cell unavailable to one ordinary move"):return true
	if actor=="su":
		for enemy: Dictionary in s.battle.enemies.values():
			if enemy.hp>0 and not enemy.disabled:
				if specialty(actor,{"ability":"su_1","target":enemy.id},"mark makes next allied attack stronger, does not claim more total AP damage"):return true
	if actor=="chen":
		for enemy: Dictionary in s.battle.enemies.values():
			if not enemy.disabled and enemy.hp>0 and not Rules.Hazards.footprint(s.battle,enemy,Rules).is_empty():
				if specialty(actor,{"ability":"chen_1","target":enemy.id},"cancelled a real currently announced machine action for this round"):return true
	if actor=="ye":
		for enemy: Dictionary in s.battle.enemies.values():
			if specialty(actor,{"ability":"ye_1","target":enemy.id},"isolated hazard while leaving machine body and power intact"):return true
	if actor=="he":
		for enemy: Dictionary in s.battle.enemies.values():
			for cell: Array in Rules.Hazards.footprint(s.battle,enemy,Rules):
				if specialty(actor,{"ability":"he_1","cell":cell},"placed a shield on an announced machine attack cell"):return true
	if actor=="mo":
		for object: Dictionary in s.battle.objects.values():
			if Rules.distance(h.cell,object.cell)>1 and specialty(actor,{"ability":"mo_1","target":object.id},"advanced a shutdown switch from beyond ordinary interaction range"):return true
	if actor=="jiang" and not h.carrying.is_empty():
		for partner: Dictionary in s.battle.heroes.values():
			if partner.id!=actor and specialty(actor,{"ability":"jiang_1","target":partner.id,"consent":true},"handed off actual cargo, receiving hero spent zero AP; not marked delivered"):return true
	return super.tick(actor,goal,board)
func run() -> void:
	content=Catalog.load_catalog();s=Rules.begin_campaign(content,"product018-crew-campaign");log=[]
	var store=Store.new();var slot: String="user://tests/crew-%d/save.json"%Time.get_ticks_usec()
	attempt("depart","lin")
	for day: int in range(1,25):
		solve(content.boards[s.battle.mission_id])
		if s.campaign.phase!="settlement":failures.append("no settlement "+str(day));break
		growth.append({"day":day,"roster":s.battle.heroes.keys(),"outcome":s.campaign.last_result.outcome,"actors":s.actors.duplicate(true),"recruited":s.journey.recruited.duplicate(true)})
		print("CREW_DAY ",day," ",s.campaign.last_result.outcome," used=",used.keys())
		if day==24:break
		attempt("enter_camp","lin")
		# Actual courses and recovery, no XP / position / AP / contribution injection.
		var candidates: Array=s.journey.recruited.keys();candidates.reverse()
		for id: String in candidates:
			if s.actors[id].xp<28 and attempt("train",id):break
		var tired: Array=[]
		for id: String in candidates:
			if s.actors[id].fatigue>=30 and not s.campaign.used.has(id) and tired.size()<2:tired.append(id)
		if not tired.is_empty():attempt("rest",tired[0],{"participants":tired})
		if day==23:attempt("select_route","lin",{"route":"evacuation"})
		if not store.save_slot(slot,s,content).ok:failures.append("save "+str(day));break
		var loaded: Dictionary=store.load_slot(slot,content)
		if not loaded.ok:failures.append("load "+str(day));break
		s=loaded.state
		if not attempt("finish_evening","lin"):failures.append("night "+str(day));break
		var ready: Array=Rules.Crew.ready_ids(s);ready.sort_custom(func(a: String,b: String):return s.actors[a].join>s.actors[b].join)
		var party: Array=ready.slice(0,3)
		if not attempt("depart","lin",{"roster":party}):failures.append("depart "+str(day));break
	var absent: Array=[]
	for id: String in content.actors:
		if not used.has(id+"_1"):absent.append(id)
	if not s.chapter_one.finished:failures.append("campaign did not finish")
	var file:=FileAccess.open("res://../outputs/product018-crew-campaign.json",FileAccess.WRITE);file.store_string(JSON.stringify({"failures":failures,"unobserved":absent,"growth":growth,"specialty_actions":used,"scope":"continuous production reducer commands with daily save/load; no state injection; some specialty contexts may not occur in this route"},"\t"));file.close()
	print("PRODUCT018_CREW: failures=%d observed=%d missing=%s"%[failures.size(),used.size(),str(absent)]);quit(1 if failures else 0)
