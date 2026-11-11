extends SceneTree
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Chapter=preload("res://scripts/domain/chapter_one.gd")
const Stories=preload("res://scripts/domain/chapter_stories.gd")
const Hazards=preload("res://scripts/domain/chapter_hazards.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
var content: Dictionary
var state: Dictionary
var count: int=0
var failures: int=0
var sequence: int=0
func check(condition: bool,description: String) -> void:
	count+=1
	if not condition:failures+=1;printerr("CHAPTER_FAIL: "+description)
func command(kind: String,payload: Dictionary={},actor: String="lin") -> Dictionary:
	sequence+=1
	return {"kind":kind,"payload":payload,"actor_id":actor,"command_id":"chapter-%d"%sequence,"root_decision_id":"chapter-%d"%sequence,"expected_revision":state.revision}
func act(kind: String,payload: Dictionary={},actor: String="lin") -> Dictionary:
	var c:=command(kind,payload,actor)
	var before:=Store.canonical(state)
	var result:=Rules.reduce(state,c,content)
	check(Store.canonical(state)==before,"preview immutable "+kind)
	if result.ok:state=result.next_state
	return result
func _initialize() -> void:call_deferred("run")
func run() -> void:
	content=Catalog.load_catalog()
	state=Rules.fresh(content,"chapter-failures")
	state.inventory={"credits":0,"supplies":0,"parts":0}
	for day: int in range(1,7):
		check(state.battle.mission_id=="M%02d"%day,"six main missions in order")
		check(act("emergency_retreat",{"confirmed":true}).ok,"failure remains playable")
		check(state.chapter_one.main_completed==day,"main completion recorded independently")
		check(act("community_report",{"choice":"archive"}).ok,"community choice follows real settlement")
		check(not act("community_report",{"choice":"publish"}).ok,"community choice once")
		check(act("enter_camp").ok,"camp after failure")
		check(act("next_mission").ok,"free next day or chapter ending")
	check(not state.chapter_one.finished and state.campaign.day==7 and state.battle.mission_id=="M07","P3 continues from first chapter into authored M07")
	check(not act("next_mission").ok,"cannot advance twice from battle")
	check(Store.validate(Store.envelope(state,content),content).ok,"chapter save round trip")
	state=Rules.fresh(content,"side-window")
	act("emergency_retreat",{"confirmed":true});act("enter_camp");act("next_mission")
	for actor: Dictionary in state.actors.values():actor.ready_day=1;actor.fatigue=0
	act("emergency_retreat",{"confirmed":true})
	for actor: Dictionary in state.actors.values():actor.ready_day=1
	check(Chapter.side_available(state,content).has("S01"),"S01 opens on D2")
	check(not act("start_side",{"mission":"S02"}).ok,"future side rejected")
	check(not act("start_side",{"mission":"S01","roster":["lin","lin","su"]}).ok,"duplicate party rejected atomically")
	check(act("start_side",{"mission":"S01","roster":["lin","xu","su"]}).ok,"side deploys same day")
	var credits: int=state.inventory.credits
	act("emergency_retreat",{"confirmed":true})
	check(state.inventory.credits==credits,"failed side has no main allowance")
	check(not act("start_side",{"mission":"S01"}).ok,"side cannot replay rewards")
	check(state.chapter_one.main_completed==2,"side does not advance main cursor")
	act("enter_camp");act("next_mission")
	check(state.battle.mission_id=="M03","side returns to correct next main")
	state=Rules.fresh(content,"projects")
	act("emergency_retreat",{"confirmed":true});act("enter_camp")
	for actor: Dictionary in state.actors.values():actor.ready_day=1
	var supplies: int=state.inventory.supplies
	check(act("train",{"participants":["lin","xu"]}).ok,"two trainees one project")
	check(state.campaign.projects==1 and state.inventory.supplies==supplies-2 and state.actors.lin.training_completed==1 and state.actors.xu.training_completed==1,"group costs and stages")
	check(not act("rest",{"participants":["lin","su"]}).ok,"participant cannot double book")
	state.campaign.day=2
	check(Stories.available(state,content).has("P_lin_1"),"authored personal story unlocked")
	check(act("story_open",{"node":"P_lin_1"}).ok,"opening consumes one reading window")
	var trust: float=state.social["lin>leader"].trust
	check(act("story_defer",{"node":"P_lin_1"}).ok,"deferral persists without resolving")
	check(act("story_choice",{"node":"P_lin_1","choice":"private"}).ok,"explicit choice persisted")
	check(state.chapter_one.flags["lin.disclosure.private"] and state.social["lin>leader"].trust==trust,"privacy choice does not fabricate trust")
	check(not act("story_choice",{"node":"P_lin_1","choice":"share"}).ok,"choice cannot double commit")
	var closeness: float=state.social["xu>leader"].closeness
	act("story_open",{"node":"L02"});act("story_choice",{"node":"L02","choice":"a"})
	check(state.social["xu>leader"].closeness==closeness+3,"life scene one-time closeness")
	check(not act("story_open",{"node":"L01"}).ok,"two scenes per night enforced")
	var old:=Store.envelope(state,content);old.runtime_revision=2;old.state.erase("chapter_one");old.erase("checksum");old.checksum=Store.canonical(old).sha256_text()
	check(Store.validate(old,content).ok,"P1 envelope remains readable without changing source save")
	state=Rules.fresh(content,"mentorship")
	state.campaign.phase="camp";state.actors.lin.xp=40
	check(not act("mentor",{"student":"xu","consent":true}).ok,"mentorship cannot invent contribution history")
	for pair: String in ["lin>xu","xu>lin"]:
		state.social[pair].agreement="cooperate";state.social[pair].contribution_missions=["M01","M02"]
	var mentor_xp: int=state.actors.lin.xp
	check(not act("mentor",{"student":"xu"}).ok,"mentorship explicit consent")
	check(act("mentor",{"student":"xu","consent":true}).ok,"eligible mentorship")
	check(state.actors.xu.xp==24 and state.actors.lin.xp==mentor_xp and state.actors.xu.training_completed==1,"mentorship actual gain and shared stage")
	check(not act("train",{},"xu").ok,"mentorship cannot double use learner stage")
	var bad: Dictionary=state.duplicate(true);bad.chapter_one.scenes={"invented":{"seen":true,"choice":"a","status":"resolved"}}
	check(not Store.validate(Store.envelope(bad,content),content).ok,"corrupt chapter scene rejected")
	state=Rules.fresh(content,"hazards")
	Rules.deploy(state,content,"M03")
	var enemy: Dictionary=state.battle.enemies.values()[0]
	check(enemy.hp==5,"welder authored HP")
	state.battle.round=1;check(Hazards.footprint(state.battle,enemy,Rules).is_empty(),"welder charges odd round")
	state.battle.round=2;check(Hazards.footprint(state.battle,enemy,Rules).size()>0,"welder fan even round")
	Rules.deploy(state,content,"M06");enemy=state.battle.enemies.M06_enemy1
	check(enemy.hp==8 and Hazards.footprint(state.battle,enemy,Rules).size()==2,"hauler follows two rail cells")
	print("CHAPTER_ONE_RESULTS: checks=%d failures=%d" % [count,failures])
	quit(1 if failures else 0)
