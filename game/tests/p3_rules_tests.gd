extends SceneTree
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Full=preload("res://scripts/domain/full_campaign.gd")
const Stories=preload("res://scripts/domain/chapter_stories.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
const I18n=preload("res://scripts/presentation/localization.gd")
var c: Dictionary
var s: Dictionary
var checks: int=0
var failures: int=0
var index: int=0
func check(value: bool,description: String) -> void:
	checks+=1
	if not value:failures+=1;printerr("P3_FAIL: "+description)
func act(kind: String,payload: Dictionary={},actor: String="lin") -> Dictionary:
	index+=1
	var command: Dictionary={"kind":kind,"actor_id":actor,"payload":payload,"command_id":"p3-test-%d"%index,"root_decision_id":"p3-test-%d"%index,"expected_revision":s.revision}
	var before: String=Store.canonical(s)
	var result: Dictionary=Rules.reduce(s,command,c)
	check(Store.canonical(s)==before,"preview immutable "+kind)
	check(Store.canonical(result)==Store.canonical(Rules.reduce(s,command,c)),"deterministic preview "+kind)
	if result.ok:s=result.next_state
	return result
func fixture(mission: String,roster: Array=[]) -> void:
	s=Rules.fresh(c,"p3-fixture")
	s.campaign.day=int(c.boards[mission].day)
	s.chapter_one.main_completed=s.campaign.day-1
	preload("res://tests/baseline018_fixture.gd").joined(s)
	s.chapter_one.roster=roster
	if mission=="M24":s.full_campaign.route="evacuation"
	Rules.deploy(s,c,mission)
func camp(day: int) -> void:
	fixture("M%02d" % day)
	act("emergency_retreat",{"confirmed":true});act("enter_camp")
	for actor: Dictionary in s.actors.values():actor.ready_day=1;actor.fatigue=0
func _initialize() -> void:call_deferred("run")
func run() -> void:
	c=Catalog.load_catalog();I18n.initialize()
	check(c.boards.size()==36,"36 authority boards")
	var scene_count: int=0
	for group: String in ["personal","relationships","life","community","chapter"]:
		for scene: Dictionary in c.domains.scripts[group]:
			scene_count+=1
			check(I18n.messages.has("content.scenes."+scene.id+".title"),"localized authored scene "+scene.id)
	check(scene_count==96,"96 distinct authored scenes")
	camp(7)
	check(Full.stages(s,"lin")==2 and Full.stages(s,"ye")==1,"unused stages carry; no prerecruit stages")
	check(s.actors.ye.xp==12 and s.actors.mo.xp==28,"authored recruit XP floors")
	check(act("train",{},"lin").ok,"chapter two training")
	check(Full.stages(s,"lin")==1,"stage decrement")
	check(not act("train",{},"lin").ok,"night participant lock")
	camp(23)
	check(not act("next_mission").ok,"explicit route required")
	check(not act("select_route",{"route":"shared_control"}).ok,"insufficient infrastructure/evidence route blocked")
	check(act("review_record",{"evidence":"E_ORDER"}).ok,"public record window")
	check(not act("review_record",{"evidence":"E_ORDER"}).ok,"no duplicate record")
	check(act("select_route",{"route":"distributed_rebuild"}).ok,"baseline ending available without evidence")
	check(act("next_mission").ok,"D24 deployment")
	check(s.battle.objects.has("west") and s.battle.objects.has("east") and s.battle.objects.has("archive") and not s.battle.objects.has("r1") and not s.battle.objects.has("auth"),"route excludes other goals")
	check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,c))),c).ok,"route-filtered save roundtrip")
	act("emergency_retreat",{"confirmed":true})
	check(s.full_campaign.ending=="evacuation" and s.chapter_one.finished,"failed final route has actual evacuation coda")
	check(not act("enter_camp").ok,"no day24 camp")
	fixture("M17")
	s.battle.heroes.lin.cell=[2,4]
	check(act("interact",{"target":"isolate"}).ok,"first branch action")
	check(not act("undo").ok,"branch commitment boundary")
	s.battle.heroes.lin.cell=[6,2];s.battle.objects.repair1.completed=true
	check(not act("interact",{"target":"repair2"}).ok,"repair cannot follow isolation")
	s.battle.heroes.lin.cell=[2,4];s.battle.heroes.lin.ap=2
	act("interact",{"target":"isolate"});act("emergency_retreat",{"confirmed":true})
	check(s.full_campaign.district_caps.floodgates==2 and s.campaign.districts.floodgates==1,"isolate success has no infrastructure gain")
	fixture("M24")
	var enemy: Dictionary=s.battle.enemies.M24_enemy1
	s.battle.objects.M24_enemy1_cut0.completed=true;Rules.shutdown(s.battle,enemy.id)
	check(not enemy.disabled,"sentinel needs both shutdown switches")
	s.battle.objects.M24_enemy1_cut1.completed=true;Rules.shutdown(s.battle,enemy.id)
	check(enemy.disabled,"both switches disable")
	fixture("S07")
	for round_index: int in range(4):act("end_round")
	check(s.battle.enemies.has("reinforcement_1"),"relay spawns after published delay")
	check(s.battle.spawn_count<=2,"shared reinforcement cap")
	fixture("M08")
	for id: String in ["block1","block2"]:s.battle.objects[id].completed=true
	s.battle.heroes.lin.cell=[3,4]
	check(act("interact",{"target":"truck"}).ok,"dispatch convoy")
	s.battle.heroes.xu.cell=[3,5]
	act("end_round")
	check(s.battle.objects.truck.waypoint==0,"convoy waits for occupied next cell")
	s.battle.heroes.xu.cell=[2,7];act("end_round")
	check(s.battle.objects.truck.waypoint==1,"convoy advances exactly one waypoint")
	fixture("M12")
	s.battle.heroes.lin.cell=[3,2]
	act("interact",{"target":"backup"});act("end_round")
	check(not s.battle.objects.backup.completed,"channel not immediate completion")
	act("end_round");check(s.battle.objects.backup.completed,"two real end rounds complete channel")
	# Every authored choice is executed through reducer in an explicitly isolated story fixture.
	for node: Dictionary in Stories.nodes(c).values():
		for choice: Dictionary in node.choices:
			camp(maxi(1,int(node.earliest_day)))
			for required: String in node.get("requires_resolved",[]):s.chapter_one.scenes[required]={"seen":true,"choice":"fixture","status":"resolved"}
			check(act("story_open",{"node":node.id}).ok,"story opens "+node.id)
			var credits: int=s.inventory.credits
			var result: Dictionary=act("story_choice",{"node":node.id,"choice":choice.id})
			if choice.id=="integrated":check(not result.ok and result.error_code=="proof_required","no fabricated proof "+node.id)
			else:
				check(result.ok,"authored choice "+node.id+"/"+choice.id)
				check(s.inventory.credits==credits-int(choice.get("credits",0)),"atomic story payment")
				check(not act("story_choice",{"node":node.id,"choice":choice.id}).ok,"choice cannot replay")
	camp(20)
	s.chapter_one.scenes.P_jiang_1={"seen":true,"choice":"wages","status":"resolved"}
	act("story_open",{"node":"P_jiang_2"});act("story_choice",{"node":"P_jiang_2","choice":"settle"})
	check(not s.full_campaign.contracts.jiang.fulfilled,"payment alone not final proof")
	s.campaign.day=23;Full.verify(s,c)
	check(s.full_campaign.contracts.jiang.fulfilled,"day23 wage verification")
	check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,c))),c).ok,"contract state roundtrip")
	var legacy: Dictionary=Store.envelope(Rules.fresh(c,"legacy"),c)
	legacy.runtime_revision=3;legacy.state.erase("full_campaign");legacy.erase("checksum");legacy.checksum=Store.canonical(legacy).sha256_text()
	var migrated: Dictionary=Store.validate(legacy,c)
	check(migrated.ok and migrated.state.full_campaign.evidence.is_empty() and migrated.state.full_campaign.contracts.is_empty(),"legacy migration cannot invent history")
	var bad: Dictionary=Store.envelope(s,c);bad.state.full_campaign.evidence={"FAKE":{"source":"review","day":20,"revision":1}};bad.erase("checksum");bad.checksum=Store.canonical(bad).sha256_text()
	check(not Store.validate(bad,c).ok,"unknown evidence rejected")
	print("P3_RULES_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
