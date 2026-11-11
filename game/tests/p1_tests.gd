extends SceneTree
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Session=preload("res://scripts/app/session.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
var content: Dictionary
var s: Dictionary
var n: int=0
var failed: int=0
var passed: int=0
func check(ok: bool,text: String) -> void:
	if ok: passed+=1
	else: failed+=1;push_error(text)
func command(kind: String,actor: String="lin",payload: Dictionary={}) -> Dictionary:
	n+=1
	return {"command_id":"test-%d"%n,"expected_revision":s.revision,"kind":kind,"actor_id":actor,"payload":payload,"root_decision_id":"root-%d"%n}
func act(kind: String,actor: String="lin",payload: Dictionary={}) -> bool:
	var c:=command(kind,actor,payload)
	var before:=Store.canonical(s)
	var preview:=Rules.reduce(s,c,content)
	check(Store.canonical(s)==before,"preview must not mutate")
	var result:=Rules.reduce(s,c,content)
	check(Store.canonical(result)==Store.canonical(preview),"preview equals execution")
	if not result.ok:
		push_error("action %s %s %s failed: %s"%[kind,actor,str(payload),result.error_code])
		failed+=1
		return false
	s=result.next_state
	return true
func move(actor: String,cell: Array) -> void:
	act("move",actor,{"cell":cell})
func _initialize() -> void:
	content=Catalog.load_catalog()
	s=Rules.fresh(content,"integration")
	var original:=Store.canonical(s)
	var invalid:=command("move","lin",{"cell":[4,3]})
	check(not Rules.reduce(s,invalid,content).ok and Store.canonical(s)==original,"wall/deep rejection atomic")
	invalid.expected_revision=-1
	check(Rules.reduce(s,invalid,content).error_code=="stale_revision","stale revision")
	# Real M01 deployment, parallel rescue with exact legal movement costs.
	move("lin",[1,4]);move("lin",[2,3])
	move("xu",[3,5]);move("xu",[6,5])
	move("su",[6,7]);move("su",[7,5])
	act("end_round")
	act("stabilize","lin",{"target":"r1"});act("pickup","lin",{"target":"r1"})
	move("xu",[6,3]);act("stabilize","xu",{"target":"r2"})
	act("attack","su",{"target":"M01_enemy1"})
	act("end_round")
	act("attack","su",{"target":"M01_enemy1"})
	move("lin",[1,4]);move("lin",[1,6])
	act("pickup","xu",{"target":"r2"});move("xu",[6,5])
	act("end_round")
	move("lin",[0,6]);act("extract","lin")
	move("xu",[4,5]);move("xu",[2,5])
	act("end_round")
	act("leave_site","lin")
	move("xu",[1,6]);move("xu",[0,6])
	act("end_round")
	act("extract","xu")
	act("emergency_retreat","lin",{"confirmed":true})
	check(s.campaign.last_result.outcome=="success","real M01 success")
	check(s.inventory.credits==40,"success reward exactly once")
	var prior:=Store.canonical(s)
	Rules.settle(s,content)
	check(Store.canonical(s)==prior,"settlement idempotent")
	act("enter_camp")
	act("train","lin")
	act("short_talk","lin",{"target":"xu"})
	check(s.actors.lin.xp==17 and s.social["lin>xu"].closeness==28 and s.social["lin>xu"].grudge==42,"growth and relation separate")
	var store=Store.new()
	var path: String="user://tests/p1-%d/save.json"%Time.get_ticks_usec()
	check(store.save_slot(path,s,content).ok,"save stable camp")
	var loaded: Dictionary=store.load_slot(path,content)
	check(loaded.ok and Store.canonical(loaded.state)==Store.canonical(s),"complete roundtrip")
	if loaded.ok:s=loaded.state
	act("next_mission")
	check(s.battle.mission_id=="M02" and s.campaign.day==2,"M02 entered after load")
	check(s.battle.objects.power.prerequisites==["cut"],"real M02 prerequisite retained")
	var support: String = ""
	for id: String in s.battle.heroes:
		if id not in ["lin","xu"]: support=id
	move("lin",[0,5]);move("lin",[0,2])
	move("xu",[4,6]);move("xu",[6,5])
	move(support,[6,7]);move(support,[7,5])
	act("end_round")
	move("lin",[1,2])
	move("xu",[6,3])
	var rejected := Rules.reduce(s,command("interact","xu",{"target":"power"}),content)
	check(not rejected.ok and rejected.error_code=="prerequisite_required","M02 power rejects before cut completes")
	act("attack",support,{"target":"M02_enemy1"})
	act("end_round")
	act("interact","lin",{"target":"cut"})
	check(s.battle.objects.cut.completed,"trained L2 first work supplies two work")
	act("attack",support,{"target":"M02_enemy1"})
	act("interact","xu",{"target":"power"});act("interact","xu",{"target":"power"})
	act("emergency_retreat","lin",{"confirmed":true})
	check(s.campaign.last_result.outcome=="success" and s.campaign.districts.medical==2,"M02 playable to success with world consequence")
	check(store.save_slot(path,s,content).ok,"backup rotation")
	var f:=FileAccess.open(path,FileAccess.WRITE);f.store_string("broken");f.close()
	check(not store.load_slot(path,content).ok and store.load_slot(path,content,true).ok,"bad primary recoverable backup")
	var e:=Store.envelope(s,content);e.schema_version=999
	check(Store.validate(e,content).error_code=="unsupported_schema","unknown schema refused")
	var session=Session.new()
	var session_path: String="user://tests/session-%d/save.json"%Time.get_ticks_usec()
	check(session.start(content,session_path,"atomic").ok,"session starts")
	s=session.state
	check(session.submit(command("depart")).ok,"session departs from preparation")
	s=session.state
	var c:=command("end_round")
	prior=Store.canonical(session.state)
	session.store.fail_writes=true
	check(not session.submit(c).ok and Store.canonical(session.state)==prior,"write failure rollback")
	session.store.fail_writes=false
	check(session.submit(c).ok,"retry after failed write")
	prior=Store.canonical(session.state)
	check(session.submit(c).ok and Store.canonical(session.state)==prior,"duplicate command idempotent")
	s=Rules.fresh(content,"failure")
	act("emergency_retreat","lin",{"confirmed":true})
	check(s.campaign.last_result.outcome=="failed" and s.inventory.credits==36,"failure preserves allowance")
	act("enter_camp");act("next_mission")
	check(s.battle.heroes.size()==3 and s.battle.heroes.keys()[0].begins_with("responder"),"injured roster continues with responders")
	check(s.battle.rows[5].substr(1,1)==":","one failure rubble cell")
	var forged:=Store.envelope(s,content)
	forged.state.battle.heroes[forged.state.battle.heroes.keys()[0]].erase("carrying")
	forged.erase("checksum");forged.checksum=Store.canonical(forged).sha256_text()
	check(not Store.validate(forged,content).ok,"valid checksum cannot bypass state shape validation")
	check(s.rng.seed=="9223372036854775806","64-bit RNG stays exact decimal string")
	s=Rules.fresh(content,"timeout")
	move("lin",[1,4]);move("lin",[2,3])
	var no_ap:=Rules.reduce(s,command("stabilize","lin",{"target":"r1"}),content)
	check(not no_ap.ok and no_ap.error_code=="insufficient_ap","no AP rejected")
	for i: int in range(12): act("end_round")
	check(s.campaign.phase=="settlement" and s.campaign.last_result.outcome=="failed","timeout resolves after last player round")
	act("enter_camp");act("next_mission")
	check(s.campaign.mission_id=="M02","timeout continues")
	print("P1_TEST_RESULTS: %d passed, %d failed"%[passed,failed])
	quit(1 if failed else 0)
