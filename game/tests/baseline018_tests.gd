extends SceneTree
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
var content: Dictionary
var failures: Array=[]
var count: int=0
func check(name: String,value: bool) -> void:
	count+=1
	if not value:failures.append(name);printerr("FAIL: "+name)
func command(s: Dictionary,kind: String,payload: Dictionary={},actor: String="lin") -> Dictionary:
	return Rules.reduce(s,{"command_id":"test-%d-%d"%[s.revision,count],"expected_revision":s.revision,"kind":kind,"actor_id":actor,"payload":payload,"root_decision_id":"root-%d-%d"%[s.revision,count]},content)
func _initialize() -> void:
	content=Catalog.load_catalog();check("authority loads",content.ok)
	if not content.ok:printerr(content);quit(1);return
	var s: Dictionary=Rules.begin_campaign(content,"baseline018-test")
	check("new game begins before deployment",s.campaign.phase=="briefing" and s.actors.lin.fatigue==0 and s.journey.recruited.size()==3)
	check("new difficulty is baseline standard",s.campaign.difficulty=="standard" and s.battle.balance_revision==3)
	var valid: Dictionary=Store.validate(Store.envelope(s,content),content)
	check("preparation persists",valid.ok)
	var result: Dictionary=command(s,"depart",{})
	check("depart uses saved draft",result.ok)
	if result.ok:s=result.next_state
	check("depart charges fatigue only once",s.actors.lin.fatigue==18 and s.campaign.phase=="battle")
	check("deployed state persists",Store.validate(Store.envelope(s,content),content).ok)
	# Continuous real phase transitions, deliberately retreating, prove no success-only recruitment.
	for day: int in range(1,5):
		check("Chen not available before M04 settlement day%d"%day,not Rules.Crew.joined(s,"chen"))
		result=command(s,"emergency_retreat",{"confirmed":true})
		check("main settlement day%d"%day,result.ok)
		if not result.ok:break
		s=result.next_state
		check("settlement save day%d"%day,Store.validate(Store.envelope(s,content),content).ok)
		if day==4:break
		result=command(s,"enter_camp");check("enter camp%d"%day,result.ok);s=result.next_state
		result=command(s,"finish_evening");check("next morning%d"%day,result.ok);s=result.next_state
		check("preparation save day%d"%(day+1),Store.validate(Store.envelope(s,content),content).ok)
		result=command(s,"depart");check("depart day%d"%(day+1),result.ok)
		if not result.ok:break
		s=result.next_state
	check("M04 settlement recruits Chen even after failure",Rules.Crew.joined(s,"chen") and s.campaign.last_result.recruits==["chen"])
	check("hard baseline damage unchanged",Rules.Hazards.enemy_damage({"difficulty":"hard","balance_revision":3},2)==2)
	check("legacy tuning combat preserved",Rules.Hazards.enemy_damage({"difficulty":"hard","balance_revision":2},2)==3)
	check("relaxed baseline no extra object deadlines",Rules.Hazards.deadline_grace({"difficulty":"relaxed","balance_revision":3})==0)
	field_tests()
	appraisal_tests()
	var output: Dictionary={"checks":count,"failures":failures,"scope":"normal new-game/preparation/recruitment persistence; deliberate retreat campaign"}
	var file:=FileAccess.open("res://../outputs/baseline018-rules.json",FileAccess.WRITE);file.store_string(JSON.stringify(output,"\t"));file.close()
	print("BASELINE018_RESULTS: checks=%d failures=%d"%[count,failures.size()]);quit(0 if failures.is_empty() else 1)

func fixture(mission: String) -> Dictionary:
	var state: Dictionary=Rules.fresh(content,"isolated-rules")
	state.campaign.day=content.boards[mission].day
	# Explicit isolated fixture, not proof of campaign recruitment or economy.
	for id: String in state.actors:
		if state.actors[id].join<int(mission.substr(1)):state.journey.recruited[id]={"day":1,"revision":0,"mission":"fixture"}
	Rules.deploy(state,content,mission)
	return state
func field_tests() -> void:
	for mission: String in ["M05","M10","M21","S11"]:
		var state: Dictionary=fixture(mission)
		var f: Dictionary=state.battle.service
		for id: String in f.definition.get("prerequisites",[]):state.battle.objects[id].completed=true
		for id: String in f.definition.get("exit_requires",[]):state.battle.objects[id].completed=true
		var ids: Array=state.battle.heroes.keys()
		for stage: int in range(f.definition.consecutive_rounds):
			var posts: Array=Rules.Field.posts(state.battle)
			for i: int in range(posts.size()):
				state.battle.heroes[ids[i]].cell=posts[i].duplicate();state.battle.heroes[ids[i]].ap=2
				var result: Dictionary=command(state,"service_watch",{"post":i},ids[i]);check(mission+" legal operation",result.ok)
				if result.ok:state=result.next_state
			Rules.Field.end_round(state,Rules);state.battle.round+=1;f=state.battle.service
		check(mission+" authored cadence completes",f.done)
		if f.definition.has("extra_exit"):check(mission+" earns optional exit",Rules.contains_cell(state.battle.exits,f.definition.extra_exit))
		if mission=="M05":check("M05 drains only authored stages",Rules.terrain(state.battle,[6,3])=="." and Rules.terrain(state.battle,[6,4])==".")
		check(mission+" service save",Store.validate(Store.envelope(state,content),content).ok)
	var state: Dictionary=fixture("M21")
	state.battle.service.ticks=1
	Rules.Field.end_round(state,Rules)
	check("M21 interruption resets consecutive count",state.battle.service.ticks==0)
	state=fixture("M05");state.battle.service.ticks=1
	Rules.Field.end_round(state,Rules)
	check("M05 interruption preserves completed stage",state.battle.service.ticks==1)
	for id: String in state.battle.service.definition.linked_controls:state.battle.objects[id].completed=true
	check("permanent shutdown removes field power",not Rules.Field.power(state.battle))
	state.battle.objects[state.battle.service.definition.linked_controls[0]].completed=false
	state.battle.enemies[state.battle.service.definition.source_enemy].isolated=true
	check("danger isolation preserves field power",Rules.Field.power(state.battle))
func appraisal_tests() -> void:
	var state: Dictionary=Rules.fresh(content,"appraisal-fixture")
	var fact: Dictionary={"root":"M01:authored-choice","observers":["lin"],"known":false,"visible_doubt":true,"shares":{"leader":1.0},"family":"breach","deliberate":true,"warned":true,"reason":"fixture explicit promise"}
	var trust: float=state.social["lin>leader"].trust
	Rules.Appraisal.record(state,content,fact)
	check("provisional interpretation does not penalize trust",state.social["lin>leader"].trust==trust and state.appraisal.provisional.size()==1)
	fact.known=true;Rules.Appraisal.record(state,content,fact)
	var after: String=Store.canonical(state.social)
	Rules.Appraisal.record(state,content,fact)
	check("same fact cannot double charge",after==Store.canonical(state.social))
	check("first known fact owns one memory",state.social["lin>leader"].memories.size()==1 and state.social["lin>leader"].trust==trust-8)
	fact.shares={};Rules.Appraisal.record(state,content,fact)
	check("evidence correction refunds actual loss only",state.social["lin>leader"].trust==trust and state.social["lin>leader"].memories[0].amplitude==0)
	state=Rules.fresh(content,"repeat-fixture")
	for i: int in range(3):
		state.campaign.day=i+1;fact.root="M%02d:accepted-promise"%(i+1);fact.shares={"leader":1.0}
		Rules.Appraisal.record(state,content,fact)
	check("third independent breach is severe once",state.social["lin>leader"].memories.size()==3 and state.social["lin>leader"].memories[-1].serious and state.social["lin>leader"].memories[-1].actual_trust_loss==12)
	Rules.Appraisal.personal(state,content,"failed",["lin"])
	var load_value: float=state.actors.lin.self_load
	Rules.Appraisal.personal(state,content,"failed",["lin"])
	check("self load is distinct and mission capped",load_value>0 and load_value<=8 and state.actors.lin.self_load==load_value)
