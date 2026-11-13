extends "res://tests/product018_crew_campaign.gd"
var focus: String="lin"
var output_prefix: String="p4close"
var advanced: Dictionary={}
var campaigns: Array=[]
var focused: String=""
func battle_view(battle: Dictionary) -> Dictionary:
	var result: Dictionary={}
	for key: String in battle:
		if key!="undo":result[key]=battle[key]
	return result.duplicate(true)
func observe(actor: String,payload: Dictionary,reason: String) -> bool:
	var key: String=focus+":"+payload.ability+":"+str(Rules.Specialties.level(s.actors[actor].xp))
	if advanced.has(key):return false
	var before: Dictionary=battle_view(s.battle)
	if not attempt("specialty",actor,payload):return false
	advanced[key]={"focus":focus,"day":s.campaign.day,"ability":payload.ability,"xp":s.actors[actor].xp,"mission":s.battle.mission_id,"round":s.battle.round,"reason":reason,"payload":payload,"before":before,"after":battle_view(s.battle)}
	return true
func tick(actor: String,goal: String,board: Dictionary) -> bool:
	var h: Dictionary=s.battle.heroes[actor]
	if h.ap<=0 or h.downed or h.left:return false
	var lv: int=Rules.Specialties.level(s.actors[actor].xp)
	if focused=="jiang" and actor!="jiang" and s.battle.heroes.has("jiang") and Rules.Specialties.level(s.actors.jiang.xp)>=5:
		var carrier: Dictionary=s.battle.heroes.jiang
		if not carrier.carrying.is_empty() and h.carrying.is_empty():
			for destination: Array in [[carrier.cell[0]+3,carrier.cell[1]],[carrier.cell[0]-3,carrier.cell[1]],[carrier.cell[0],carrier.cell[1]+3],[carrier.cell[0],carrier.cell[1]-3]]:
				if Rules.distance(destination,board.exits[0])<Rules.distance(carrier.cell,board.exits[0]) and h.cell!=destination and attempt("move",actor,{"cell":destination}):return true

	if actor==focus and lv>=5:
		if actor=="lin":
			for target: Dictionary in s.battle.objects.values():
				if Rules.distance(h.cell,target.cell)==3 and observe(actor,{"ability":"lin_1","target":target.id},"level 5 reaches a real unstable casualty at distance 3, outside old range 2"):return true
		if actor=="xu" and not h.carrying.is_empty():
			for destination: Array in [[h.cell[0]+3,h.cell[1]],[h.cell[0]-3,h.cell[1]],[h.cell[0],h.cell[1]+3],[h.cell[0],h.cell[1]-3]]:
				if Rules.move_cost(s.battle,h.cell,destination,Rules.movement_budget(s,actor))<0 and observe(actor,{"ability":"xu_1","cell":destination},"level 5 carried cargo across a route unavailable to ordinary loaded movement without a winch"):return true
		if actor=="ye" and (focused!="ye" or advanced.has("ye:ye_3:"+str(lv))):
			for enemy: Dictionary in s.battle.enemies.values():
				if Rules.distance(h.cell,enemy.cell)==2 and observe(actor,{"ability":"ye_1","target":enemy.id},"level 5 isolated output from distance 2 while retaining power"):return true
		if actor=="he":
			for enemy: Dictionary in s.battle.enemies.values():
				for cell: Array in Rules.Hazards.footprint(s.battle,enemy,Rules):
					if observe(actor,{"ability":"he_1","cell":cell},"level 5 placed persistent 5HP shield on an announced attack path"):return true
		if actor=="mo":
			for target: Dictionary in s.battle.objects.values():
				if target.work-target.progress>=2 and observe(actor,{"ability":"mo_1","target":target.id},"level 5 advanced real shutdown switch by two work units in one AP"):return true
		if actor=="jiang" and not h.carrying.is_empty():
			for partner: Dictionary in s.battle.heroes.values():
				if Rules.distance(h.cell,partner.cell)==3 and observe(actor,{"ability":"jiang_1","target":partner.id,"consent":true},"level 5 handed off real cargo across three clear cells"):return true
	if actor==focus and lv>=3:
		var object: Dictionary=s.battle.objects.get(goal,{})
		if actor=="lin" and object.get("kind","")=="rescue" and not object.stable and Rules.distance(h.cell,object.cell)>1:
			for cell: Array in near(object.cell):
				if observe(actor,{"ability":"lin_3","target":goal,"cell":cell},"actual move plus stabilization in one AP"):return true
		if actor=="xu":
			for partner: Dictionary in s.battle.heroes.values():
				if partner.id!=actor and Rules.distance(h.cell,partner.cell)==2 and observe(actor,{"ability":"xu_3","target":partner.id,"consent":true},"recipient moved one cell without spending own AP; usefulness depends on subsequent route"):return true
		if actor=="su":
			for partner: Dictionary in s.battle.heroes.values():
				if partner.id==actor:continue
				if observe(actor,{"ability":"su_3","target":partner.id,"consent":true,"mode":"ap" if lv>=5 else "move"},"AP transferred at level 5; otherwise next movement budget raised, not free AP"):return true
		if actor=="chen":
			for target: Dictionary in s.battle.objects.values():
				if target.kind=="work" and target.get("sustain_until_exit",false) and observe(actor,{"ability":"chen_3","target":target.id},"shield applied to a real sustained objective; absorbed damage must be assessed separately"):return true
		if actor=="ye":
			for enemy: Dictionary in s.battle.enemies.values():
				if enemy.type!="skimmer" or enemy.disabled or enemy.hp<=0:continue
				var footprint: Array=Rules.Hazards.footprint(s.battle,enemy,Rules)
				if focused=="ye" and lv>=5:
					for endpoint: Array in [[h.cell[0]+3,h.cell[1]],[h.cell[0]-3,h.cell[1]],[h.cell[0],h.cell[1]+3],[h.cell[0],h.cell[1]-3]]:
						var touches: bool=false
						for at: Array in footprint:
							if Rules.distance(h.cell,at)+Rules.distance(at,endpoint)==3:touches=true
						if touches and observe(actor,{"ability":"ye_3","cell":endpoint},"level 5 lays three actual insulating cells crossing the skimmer footprint"):return true
				else:
					for cell: Array in footprint:
						if observe(actor,{"ability":"ye_3","cell":cell},"insulated cells on actual skimmer threat footprint; no fire or deep-water immunity"):return true
				if focused=="ye" and lv>=5 and not advanced.has("ye:ye_3:"+str(lv)):
					var choices: Array=[]
					for at: Array in footprint:choices.append_array(near(at))
					if navigate_to(actor,choices):return true
		if actor=="mo":
			for enemy: Dictionary in s.battle.enemies.values():
				if enemy.type!="scout":continue
				for cell: Array in near(h.cell):
					if observe(actor,{"ability":"mo_3","target":enemy.id,"cell":cell},"beacon placed for next round; current intent intentionally unchanged"):return true
		if actor=="jiang":
			for partner: Dictionary in s.battle.heroes.values():
				if partner.id!=actor and observe(actor,{"ability":"jiang_3","target":partner.id},"healed genuinely damaged teammate using packed medicine"):return true
	var before: Dictionary=battle_view(s.battle)
	var acted: bool=super.tick(actor,goal,board)
	if acted and actor=="he" and lv>=3 and not h.carrying.is_empty() and s.battle.heroes.has(actor):
		var after: Dictionary=s.battle.heroes[actor]
		if Rules.move_cost(before,h.cell,after.cell,2)<0 and h.cell!=after.cell:
			advanced[focus+":he_3:"+str(lv)]={"focus":focus,"day":s.campaign.day,"ability":"he_3","xp":s.actors[actor].xp,"mission":before.mission_id,"before":before,"after":battle_view(s.battle),"reason":"actual loaded move unavailable with ordinary budget 2"}
	return acted
func run() -> void:
	content=Catalog.load_catalog()
	var store=Store.new()
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--focus="):focused=argument.trim_prefix("--focus=")
	for id: String in content.actors:
		if not focused.is_empty() and id!=focused:continue
		focus=id;used={};s=Rules.begin_campaign(content,"p4close-growth-"+id);log=[]
		var slot: String="user://tests/p4close-growth-%s-%d/save.json"%[id,Time.get_ticks_usec()]
		var days: Array=[]
		attempt("depart","lin")
		for day: int in range(1,25):
			solve(content.boards[s.battle.mission_id])
			if s.campaign.phase!="settlement":failures.append(id+" settlement "+str(day));break
			days.append({"day":day,"outcome":s.campaign.last_result.outcome,"party":s.battle.heroes.keys(),"xp":s.actors[id].xp,"joined":Rules.Crew.joined(s,id),"fatigue":s.actors[id].fatigue})
			if day==24:break
			if focused=="jiang" and day in [22,23]:
				var side: String="S11" if day==22 else "S12"
				if attempt("start_side","lin",{"mission":side,"roster":s.battle.heroes.keys()}):solve(content.boards[side])
			attempt("enter_camp","lin")
			if Rules.Crew.joined(s,id):attempt("train",id)
			var tired: Array=[]
			for member: String in Rules.Crew.ready_ids(s):
				if not s.campaign.used.has(member) and s.actors[member].fatigue>=30 and tired.size()<2:tired.append(member)
			if not tired.is_empty():attempt("rest",tired[0],{"participants":tired})
			if id=="jiang" and s.full_campaign.medicine_stock<1:attempt("craft_medicine","lin")
			if day==23:attempt("select_route","lin",{"route":"evacuation"})
			if id=="mo" and day==23:store.save_slot("res://../outputs/%s-growth-%s-day%02d.json"%[output_prefix,id,day],s,content)
			if not store.save_slot(slot,s,content).ok:failures.append(id+" save");break
			var loaded: Dictionary=store.load_slot(slot,content)
			if not loaded.ok:failures.append(id+" load");break
			s=loaded.state
			if not attempt("finish_evening","lin"):failures.append(id+" night");break
			var ready: Array=Rules.Crew.ready_ids(s)
			ready.sort_custom(func(a: String,b: String):return s.actors[a].fatigue<s.actors[b].fatigue)
			if ready.has(id):ready.erase(id);ready.push_front(id)
			if not attempt("depart","lin",{"roster":ready.slice(0,3),"medicine":mini(1,s.full_campaign.medicine_stock)}):failures.append(id+" departure");break
		campaigns.append({"focus":id,"days":days,"finished":s.chapter_one.finished,"commands":log,"final_xp":s.actors[id].xp})
		if not s.chapter_one.finished:failures.append(id+" did not finish")
		print("P4CLOSE_GROWTH ",id," xp=",s.actors[id].xp," observed actions=",advanced.size())
	var missing: Array=[]
	for id: String in content.actors:
		if not focused.is_empty() and id!=focused:continue
		var found: bool=false
		for record: Dictionary in advanced.values():
			if record.ability==id+"_3":found=true
		if not found:missing.append(id+"_3")
	if not missing.is_empty():failures.append("Second specialties not observed: "+str(missing))
	var file:=FileAccess.open("res://../outputs/"+output_prefix+"-growth-campaign"+("-"+focused if not focused.is_empty() else "")+".json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"failures":failures,"unobserved_second_specialties":missing,"campaigns":campaigns,"actions":advanced,"scope":"eight continuous production-command focus routes, real costs, daily save/load; no state injection. Observed activation is distinct from tactical benefit and human balance acceptance."},"\t"));file.close()
	print("P4CLOSE_GROWTH_RESULTS: failures=%d unobserved=%s"%[failures.size(),str(missing)])
	quit(1 if failures else 0)
