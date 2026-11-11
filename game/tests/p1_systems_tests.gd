extends SceneTree
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
const Session=preload("res://scripts/app/session.gd")
var content: Dictionary
var s: Dictionary
var serial: int=0
var passed: int=0
var failed: int=0
func check(ok: bool,label: String) -> void:
	if ok:passed+=1
	else:failed+=1;push_error(label)
func cmd(kind: String,actor: String="lin",payload: Dictionary={}) -> Dictionary:
	serial+=1
	return {"command_id":"systems-%d"%serial,"expected_revision":s.revision,"kind":kind,"actor_id":actor,"payload":payload,"root_decision_id":"decision-%d"%serial}
func run_action(kind: String,actor: String="lin",payload: Dictionary={}) -> Dictionary:
	var c:=cmd(kind,actor,payload)
	var before: String=Store.canonical(s)
	var r:=Rules.reduce(s,c,content)
	check(Store.canonical(s)==before,"pure preview input")
	check(Store.canonical(r)==Store.canonical(Rules.reduce(s,c,content)),"preview/execute consistency")
	if r.ok:s=r.next_state
	return r
func reset() -> void:s=Rules.fresh(content,"systems")
func _initialize() -> void:
	content=Catalog.load_catalog()
	reset()
	var baseline: Dictionary=s.duplicate(true)
	check(run_action("move","lin",{"cell":[1,4]}).ok,"valid action before undo")
	check(run_action("undo").ok,"undo succeeds")
	check(s.battle.heroes==baseline.battle.heroes and s.inventory==baseline.inventory and s.social==baseline.social,"undo restores full gameplay domains")
	check(s.revision==2 and s.receipts.size()==1 and s.receipts[0].kind=="undo","undo monotonic revision, no orphan action receipts")
	check(not run_action("undo").ok,"empty undo rejected")
	run_action("move","lin",{"cell":[1,4]})
	run_action("end_round")
	check(not run_action("undo").ok,"enemy boundary cannot undo")
	reset()
	s.battle.heroes.lin.cell=[2,4]
	check(run_action("specialty","lin",{"ability":"lin_1","target":"r1"}).ok,"Lin stabilization at distance two")
	check(s.battle.objects.r1.stable and s.battle.ability_uses.lin_1==1 and s.battle.heroes.lin.ap==1,"Lin costs exact")
	check(run_action("undo").ok and not s.battle.objects.r1.stable and not s.battle.ability_uses.has("lin_1"),"undo specialty refunds charge and target")
	var before: String=Store.canonical(s)
	check(not run_action("specialty","lin",{"ability":"lin_3","target":"r1","cell":[2,3]}).ok,"locked L3 rejected")
	check(Store.canonical(s)==before,"locked specialty atomic")
	s.actors.lin.xp=28
	check(run_action("specialty","lin",{"ability":"lin_3","target":"r1","cell":[2,3]}).ok,"mobile first aid moves and stabilizes atomically")
	reset()
	s.battle.heroes.xu.cell=[3,3]
	check(not run_action("specialty","xu",{"ability":"xu_1","cell":[6,3]}).ok,"rope cannot cross two deep cells")
	s.battle.heroes.xu.cell=[1,1]
	check(run_action("specialty","xu",{"ability":"xu_1","cell":[2,0]}).error_code=="invalid_target","rope must be straight")
	check(run_action("specialty","xu",{"ability":"xu_1","cell":[1,4]}).ok,"rope legal straight landing")
	reset()
	s.battle.heroes.su.cell=[7,5]
	s.battle.heroes.xu.cell=[6,2]
	check(run_action("specialty","su",{"ability":"su_1","target":"M01_enemy1"}).ok,"mark at range")
	check(run_action("attack","xu",{"target":"M01_enemy1"}).ok and s.battle.enemies.M01_enemy1.hp==0,"marked next attack deals three")
	check(not s.battle.marks.has("M01_enemy1"),"mark consumed exactly once")
	reset()
	s.actors.su.xp=72
	check(run_action("specialty","su",{"ability":"su_3","target":"xu","consent":true,"mode":"ap"}).ok,"L5 AP handoff")
	check(s.battle.heroes.su.ap==1 and s.battle.heroes.xu.ap==3,"AP conserved")
	check(not run_action("specialty","su",{"ability":"su_3","target":"lin","consent":true,"mode":"ap"}).ok,"AP transfer once per mission")
	check(run_action("specialty","su",{"ability":"su_3","target":"lin","consent":true}).ok,"second charge remains movement option")
	reset()
	s.actors.su.xp=28
	s.social["xu>leader"].band="conditional"
	check(run_action("specialty","su",{"ability":"su_3","target":"xu","consent":true}).error_code=="relationship_safeguard_required","directed leader grievance checks cooperation")
	check(run_action("move","xu",{"cell":[2,4]}).ok,"basic movement retained despite grievance")
	check(run_action("authorize","xu").ok,"explicit authority available")
	s.battle.heroes.xu.cell=[2,7]
	check(run_action("specialty","su",{"ability":"su_3","target":"xu","consent":true}).ok,"authority satisfies specific restriction")
	reset()
	check(run_action("promise_retreat").ok,"promise concrete deadline")
	for i: int in range(10):run_action("end_round")
	check(s.social["lin>leader"].memories.size()==1 and s.social["lin>xu"].memories.is_empty(),"breach attributed to leader, not executing teammate")
	check(s.social["lin>leader"].trust==42,"breach actual trust loss")
	check(not run_action("undo").ok,"breach boundary cannot rewind")
	run_action("emergency_retreat","lin",{"confirmed":true});run_action("enter_camp")
	var incident: String=s.social["lin>leader"].memories[0].id
	check(run_action("acknowledge","lin",{"event":incident}).ok,"specific recognition in camp")
	check(not run_action("acknowledge","lin",{"event":incident}).ok,"recognition not farmable")
	check(run_action("treat","lin").ok,"restore named actor for promised next mission")
	run_action("next_mission")
	run_action("promise_retreat");run_action("emergency_retreat","lin",{"confirmed":true})
	check(s.social["lin>leader"].memories[0].stage==2 and s.social["lin>leader"].trust==46,"future actual kept retreat repairs same-scope acknowledged promise")
	var social: Dictionary=Rules.Social.create({"observer":"lin","target":"leader","grudge":90,"trust":90})
	for i: int in range(8):social=Rules.Social.event(social,{"id":str(i),"observer":"lin","blame":{"leader":1},"severity":18,"serious":true,"trust_loss":8},1,10)
	check(Rules.Social.value(social,1)<=100.00001,"actual memory allocation capped, not display-only")
	var amplitudes: Array=[]
	for memory: Dictionary in social.memories:amplitudes.append(memory.amplitude)
	social.grudge=0
	for i: int in range(social.memories.size()):check(social.memories[i].amplitude==amplitudes[i],"old grievance reduction never reinflates memory")
	reset()
	run_action("move","lin",{"cell":[1,4]})
	var store=Store.new()
	var path: String="user://tests/expanded-%d/save.json"%Time.get_ticks_usec()
	check(store.save_slot(path,s,content).ok,"persist full undo stack")
	var loaded: Dictionary=store.load_slot(path,content)
	check(loaded.ok and Store.canonical(loaded.state)==Store.canonical(s),"expanded state roundtrip")
	if loaded.ok:s=loaded.state
	check(run_action("undo").ok and s.battle.heroes.lin.cell==[1.0,7.0],"undo after load")
	reset()
	s.battle.heroes.lin.cell=[6,4]
	s.battle.heroes.xu.cell=[7,4]
	var old_trust: float=s.social["lin>xu"].trust
	check(run_action("protocol","lin",{"protocol":"protected_work","partner":"xu","target":"M01_enemy1_cut","consent":true}).ok,"protected work commits both AP and objective")
	check(s.battle.objects.M01_enemy1_cut.completed and s.battle.enemies.M01_enemy1.disabled and s.battle.heroes.lin.ap==1 and s.battle.heroes.xu.ap==1,"protected work exact joint costs")
	check(run_action("undo").ok and not s.battle.objects.M01_enemy1_cut.completed and s.battle.heroes.xu.ap==2,"joint undo restores both actors and machine")
	check(run_action("protocol","lin",{"protocol":"protected_work","partner":"xu","target":"M01_enemy1_cut","consent":true}).ok,"joint action can be reissued with new command id")
	run_action("emergency_retreat","lin",{"confirmed":true})
	check(s.social["lin>xu"].trust==old_trust+2,"actual shared secured objective gives directional trust once")
	var trust_after: float=s.social["lin>xu"].trust
	Rules.settle(s,content)
	check(s.social["lin>xu"].trust==trust_after,"settlement replay cannot farm trust")
	reset()
	s.battle.objects.r1.stable=true
	s.battle.objects.r1.cell=[1,6]
	check(run_action("pickup","lin",{"target":"r1"}).ok,"pickup possible")
	check(not s.battle.objects.r1.contributors.has("lin"),"touching cargo is not contribution")
	check(run_action("protocol","lin",{"protocol":"relay_carry","partner":"xu","cell":[2,4],"consent":true}).ok,"relay carries with fixed three terrain budget")
	check(s.battle.heroes.lin.carrying=="" and s.battle.heroes.xu.carrying=="r1" and s.battle.heroes.xu.ap==1,"relay AP and custody")
	check(run_action("undo").ok and s.battle.heroes.lin.carrying=="r1" and s.battle.heroes.xu.carrying=="","relay undo restores custody")
	var current:=s.duplicate(true)
	var session=Session.new()
	var session_path: String="user://tests/expanded-atomic-%d/save.json"%Time.get_ticks_usec()
	check(session.start(content,session_path,"expanded-atomic").ok,"expanded session starts")
	session.state=current
	var undo_command:=cmd("undo")
	session.store.fail_writes=true
	check(not session.submit(undo_command).ok and Store.canonical(session.state)==Store.canonical(current),"failed undo write cannot publish rollback")
	reset()
	s.actors.lin.xp=12;s.actors.lin.tendency="move"
	check(run_action("move","lin",{"cell":[1,3]}).ok,"L2 first unladen movement budget four")
	check(s.battle.used_markers.has("move:lin"),"L2 marker persisted")
	check(run_action("undo").ok and not s.battle.used_markers.has("move:lin"),"undo restores first-use passive")
	reset()
	s.actors.su.xp=28
	for i: int in range(2):check(run_action("specialty","su",{"ability":"su_3","target":"lin","consent":true}).ok,"shared charge consumed")
	run_action("end_round")
	check(run_action("specialty","su",{"ability":"su_3","target":"lin","consent":true}).error_code=="ability_exhausted","mission charges do not reset per round")
	print("P1_SYSTEMS_RESULTS: %d passed, %d failed"%[passed,failed])
	quit(1 if failed else 0)
