extends SceneTree
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
const Product=preload("res://scripts/domain/product_systems.gd")
const Session=preload("res://scripts/app/session.gd")
const Guidance=preload("res://scripts/presentation/guidance.gd")
var checks: int=0
var failures: int=0
var sequence: int=0
var content: Dictionary
var s: Dictionary
func check(value: bool,context: String) -> void:
	checks+=1
	if not value:failures+=1;printerr("P4_FAIL: "+context)
func command(kind: String,actor: String="lin",payload: Dictionary={}) -> Dictionary:
	sequence+=1
	return {"kind":kind,"actor_id":actor,"payload":payload,"command_id":"p4-%d"%sequence,"root_decision_id":"p4-%d"%sequence,"expected_revision":s.revision}
func act(kind: String,actor: String="lin",payload: Dictionary={},expected: bool=true) -> Dictionary:
	var c:=command(kind,actor,payload)
	var before: String=Store.canonical(s)
	var preview:=Rules.reduce(s,c,content)
	check(Store.canonical(s)==before,"pure preview "+kind)
	check(preview.ok==expected,"command "+kind+" "+str(preview.get("error_code")))
	if preview.ok:
		check(Store.canonical(preview)==Store.canonical(Rules.reduce(s,c,content)),"deterministic preview "+kind)
		s=preview.next_state
		check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,content))),content).ok,"roundtrip "+kind)
	return preview
func fresh_camp(day: int=18) -> void:
	s=Rules.fresh(content,"p4-fixture")
	s.campaign.day=day;s.campaign.phase="camp";s.chapter_one.main_completed=day
	preload("res://tests/baseline018_fixture.gd").joined(s)
	s.inventory={"credits":1000,"supplies":30,"parts":100}
func setup_tool(id: String,mission: String) -> void:
	s=Rules.fresh(content,"p4-tool")
	if not s.product.owned.has(id):s.product.owned.append(id)
	s.product.loadout.lin[Product.item(content,id).slot]=id
	for actor: Dictionary in s.actors.values():actor.fatigue=0
	s.chapter_one.roster=["lin","xu","su"]
	Rules.deploy(s,content,mission)
func _initialize() -> void:
	content=Catalog.load_catalog()
	fresh_camp()
	act("buy_tool","lin",{"item":"winch"})
	var paid: Dictionary=s.inventory.duplicate()
	act("buy_tool","lin",{"item":"winch"},false)
	act("equip_tool","lin",{"item":"winch"})
	act("equip_tool","xu",{"item":"winch"})
	check(s.product.loadout.lin.support=="" and s.product.loadout.xu.support=="winch","unique shared tool")
	act("refund_tool","lin",{"item":"winch"})
	check(s.inventory.credits==paid.credits+20 and s.inventory.parts==paid.parts+2 and s.product.loadout.xu.support=="","actual refund and unequip")
	act("refund_tool","lin",{"item":"winch"},false)
	act("upgrade_facility","lin",{"facility":"workshop"})
	act("upgrade_facility","lin",{"facility":"rest_area"},false)
	act("buy_tool","lin",{"item":"shield"})
	check(s.product.purchases.shield.parts==0,"workshop discounts actual price")
	act("refund_tool","lin",{"item":"shield"})
	act("buy_tool","lin",{"item":"scanner"})
	check(s.product.purchases.scanner.parts==0,"refund restores unused discount")
	act("next_mission")
	Rules.settle(s,content);s.campaign.phase="camp"
	act("refund_tool","lin",{"item":"scanner"},false)
	fresh_camp(2);act("buy_tool","lin",{"item":"winch"},false)
	s.inventory.credits=0;act("buy_supplies","lin",{},false)
	s.inventory.credits=100;var supplies: int=s.inventory.supplies
	act("buy_supplies");check(s.inventory.supplies==supplies+1,"one supply purchase")
	setup_tool("crowbar","M03");s.battle.heroes.lin.cell=[3,3]
	act("use_tool","lin",{"item":"crowbar","target":"door"})
	check(s.battle.objects.door.completed and s.battle.heroes.lin.ap==1,"crowbar 2 work 1AP")
	act("use_tool","lin",{"item":"crowbar","target":"door"},false)
	setup_tool("scanner","M01");s.battle.heroes.lin.cell=[3,3]
	act("use_tool","lin",{"item":"scanner","target":"M01_enemy1_cut"})
	check(s.battle.objects.M01_enemy1_cut.progress==1,"scanner ranged work no L2")
	act("use_tool","lin",{"item":"scanner","target":"M01_enemy1_cut"},false)
	setup_tool("medkit","M01");s.battle.medicine=2;s.battle.heroes.xu.hp=8
	act("use_tool","lin",{"item":"medkit","target":"xu"})
	check(s.battle.heroes.xu.hp==10 and s.battle.medicine==1,"heal clipped actual dose")
	act("use_tool","lin",{"item":"medkit","target":"xu"},false)
	setup_tool("winch","M04");s.battle.heroes.lin.cell=[1,1]
	act("use_tool","lin",{"item":"winch","cell":[1,1],"other":[3,1]})
	check(s.battle.heroes.lin.ap==0,"anchor 2AP")
	act("cross_anchor","lin",{"cell":[3,1]},false)
	act("end_round")
	act("cross_anchor","lin",{"cell":[3,1]})
	check(s.battle.heroes.lin.cell==[3,1],"anchor actual gap crossing")
	setup_tool("shield","M01");s.battle.heroes.lin.cell=[3,6]
	act("use_tool","lin",{"item":"shield","cell":[4,6]})
	act("move","lin",{"cell":[4,6]},false)
	act("use_tool","lin",{"item":"shield","cell":[3,5]},false)
	setup_tool("insulation","M01");act("use_tool","lin",{"item":"insulation","cell":[1,6]})
	check(Rules.contains_cell(s.battle.insulation,[1,6]),"insulation on dry ground")
	setup_tool("stretcher","M01");s.battle.heroes.lin.carrying="r1";s.battle.objects.r1.carrier="lin";s.battle.objects.r1.stable=true
	check(Rules.movement_budget(s,"lin")==3,"stretcher passive carry 3")
	fresh_camp();s.product.facilities.infirmary=2;s.product.facilities.rest_area=2
	for id: String in ["lin","xu","su"]:s.actors[id].ready_day=20;s.actors[id].fatigue=40
	act("treat","lin",{"participants":["lin","xu","su"]})
	check(s.inventory.supplies==25 and s.actors.lin.ready_day==19,"infirmary three patients discount first")
	act("rest","lin",{"participants":["lin"]},false)
	fresh_camp();s.product.facilities.rest_area=2
	for id: String in ["lin","xu","su"]:s.actors[id].fatigue=40
	act("rest","lin",{"participants":["lin","xu","su"]})
	check(s.actors.lin.fatigue==24 and s.actors.su.fatigue==24,"rest tier2 capacity and16 recovery")
	fresh_camp();act("review_record","lin",{"evidence":"E_ORDER"},false)
	s.product.facilities.communications=1
	act("review_record","lin",{"evidence":"E_ORDER"})
	fresh_camp(20);s.product.facilities.communications=2
	act("review_record","lin",{"records":["E_ORDER","E_WARNING"]})
	check(s.campaign.projects==1 and s.full_campaign.evidence.size()==2,"two independent records one project")
	fresh_camp();s.product.facilities.workshop=2;s.full_campaign.medicine_stock=3
	act("next_mission","lin",{"medicine":3})
	check(s.battle.medicine==3 and s.battle.medicine_limit==3,"workshopII snapshot not free refill")
	for mission: String in content.boards:
		for difficulty: String in ["relaxed","standard","hard"]:
			for variant: String in ["A","B"]:
				s=Rules.fresh(content,"matrix",{"difficulty":difficulty,"variant":variant});s.campaign.day=int(content.boards[mission].day)
				Rules.deploy(s,content,mission)
				check(s.battle.limit==Product.limit(content.boards[mission],difficulty),"authored limit "+mission+difficulty+variant)
				check(s.battle.environment==Product.weather(content.boards[mission],variant),"weather snapshot "+mission+variant)
				check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,content))),content).ok,"matrix save "+mission+difficulty+variant)
	for difficulty: String in ["relaxed","standard","hard"]:
		s=Rules.fresh(content,"withdrawal",{"difficulty":difficulty})
		Rules.hurt(s.battle,s.battle.heroes.lin,99)
		act("emergency_retreat","xu",{"confirmed":true})
		check(s.product.withdrawn.has("lin")== (difficulty=="hard"),"explicit permanent boundary "+difficulty)
		s.campaign.phase="camp";s.campaign.day=3
		check(Rules.Chapter.eligible(s).has("lin")==(difficulty!="hard"),"permanent roster exclusion "+difficulty)
	for difficulty: String in ["relaxed","standard","hard"]:
		for saved: bool in [true,false]:
			s=Rules.fresh(content,"deadline",{"difficulty":difficulty})
			Rules.hurt(s.battle,s.battle.heroes.lin,99)
			s.battle.heroes.xu.cell=[0,7]
			act("stabilize","xu",{"target":"casualty_lin"})
			act("stabilize","xu",{"target":"casualty_lin"},false)
			act("pickup","xu",{"target":"casualty_lin"})
			while s.battle.round<s.battle.heroes.lin.deadline:act("end_round","xu")
			if saved:act("extract","xu")
			else:act("end_round","xu")
			act("emergency_retreat","xu",{"confirmed":true})
			check(s.battle.objects.casualty_lin.delivered==saved,"last round full action "+difficulty)
			check(s.product.withdrawn.has("lin")== (difficulty=="hard" and not saved),"deadline actual severity "+difficulty)
		s=Rules.fresh(content,"standing-retreat",{"difficulty":difficulty})
		act("emergency_retreat","xu",{"confirmed":true})
		check(s.product.withdrawn.is_empty(),"standing retreat never permanent "+difficulty)
	check(Rules.Hazards.enemy_damage({"difficulty":"relaxed"},2)==1 and Rules.Hazards.enemy_damage({"difficulty":"hard"},2)==2,"difficulty enemy damage")
	s=Rules.fresh(content,"guidance")
	var hint: Dictionary=Guidance.card(s,content)
	act("move","lin",{"cell":[1,6],"tutorial_card":hint})
	check(s.tutorial.history.size()==1 and Guidance.card(s,content).is_empty(),"one card per round stored")
	act("end_round")
	check(Guidance.card(s,content).id=="forecast","second card separate round")
	var migration: Dictionary=Store.envelope(s,content)
	migration.runtime_revision=4;migration.state=migration.state.duplicate(true);migration.state.erase("product")
	for key: String in ["equipment","tool_uses","medicine_limit","environment"]:migration.state.battle.erase(key)
	migration.erase("checksum");migration.checksum=Store.canonical(migration).sha256_text()
	var migrated: Dictionary=Store.validate(migration,content)
	check(migrated.ok and migrated.state.product.withdrawn.is_empty() and migrated.state.product.purchases.is_empty(),"P3 neutral migration no invented acts")
	var session=Session.new();var path: String="user://tests/p4-restore-%d/save.json"%Time.get_ticks_usec()
	check(session.start(content,path,"restore").ok,"fresh session")
	s=session.state
	check(session.submit(command("depart")).ok,"session departs before recovery test")
	s=session.state
	check(session.submit(command("move","lin",{"cell":[1,6]})).ok,"persist first action")
	var prior: String=FileAccess.get_file_as_string(path)
	s=session.state;session.store.fail_writes=true
	check(not session.submit(command("move","lin",{"cell":[1,5]})).ok and FileAccess.get_file_as_string(path)==prior,"write failure preserves primary and memory")
	check(not session.load_game(true).ok and FileAccess.get_file_as_string(path)==prior,"recovery failure preserves original")
	session.store.fail_writes=false
	var f:=FileAccess.open(path,FileAccess.WRITE);f.store_string("corrupt");f.close()
	check(session.load_game(true).ok,"recover backup")
	var reopened=Session.new();reopened.content=content;reopened.path=path
	check(reopened.load_game().ok and Store.canonical(reopened.state)==Store.canonical(session.state),"backup recovery durable before next action")
	print("P4_PRODUCT_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
