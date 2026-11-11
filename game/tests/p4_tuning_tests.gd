extends SceneTree
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
const Guide=preload("res://scripts/presentation/guidance.gd")
var failures: int=0
var checks: int=0
var sequence: int=0
var content: Dictionary
func check(ok: bool,context: String) -> void:
	checks+=1
	if not ok:failures+=1;printerr("TUNING_FAIL: "+context)
func command(s: Dictionary,kind: String,actor: String,payload: Dictionary) -> Dictionary:
	sequence+=1
	return {"kind":kind,"actor_id":actor,"payload":payload,"command_id":"tune-%d"%sequence,"root_decision_id":"tune-%d"%sequence,"expected_revision":s.revision}
func _initialize() -> void:call_deferred("run")
func run() -> void:
	content=Catalog.load_catalog()
	check_reachability()
	check_storage_cache()
	for difficulty: String in ["relaxed","standard","hard"]:
		var s: Dictionary=Rules.fresh(content,"balance",{"difficulty":difficulty})
		check(s.battle.balance_revision==2,"new deployment uses tuning revision")
		check(Rules.Hazards.enemy_damage(s.battle,2)=={"relaxed":1,"standard":2,"hard":3}[difficulty],"meaningful machine damage "+difficulty)
		s.campaign.day=6;Rules.deploy(s,content,"M06")
		var o: Dictionary=s.battle.objects.r1
		check(Rules.Hazards.rescue_deadline(s.battle,o)==(8 if difficulty=="relaxed" else 6),"resident deadline "+difficulty)
		var legacy: Dictionary=Store.envelope(s,content).duplicate(true)
		legacy.runtime_revision=5;legacy.state.battle.erase("balance_revision");legacy.erase("checksum");legacy.checksum=Store.canonical(legacy).sha256_text()
		var before: String=Store.canonical(legacy)
		var migrated: Dictionary=Store.validate(JSON.parse_string(before),content)
		check(migrated.ok,"old P4 save migrates "+difficulty)
		if migrated.ok:
			check(migrated.state.battle.balance_revision==1 and Rules.Hazards.rescue_deadline(migrated.state.battle,migrated.state.battle.objects.r1)==6,"in-flight old battle keeps deadlines")
			check(Rules.Hazards.enemy_damage(migrated.state.battle,2)==(1 if difficulty=="relaxed" else 2),"in-flight old battle keeps damage")
			check(Store.canonical(legacy)==before,"migration leaves old input untouched")
			Rules.deploy(migrated.state,content,"M06")
			check(migrated.state.battle.balance_revision==2,"next deployment opts into tuned rules")
	var old_state: Dictionary=Rules.fresh(content,"old-undo",{"difficulty":"hard"})
	var moved: Dictionary=Rules.reduce(old_state,command(old_state,"move","lin",{"cell":[1,6]}),content)
	var old_save: Dictionary=Store.envelope(moved.next_state,content).duplicate(true)
	old_save.runtime_revision=5;old_save.state.battle.erase("balance_revision")
	for checkpoint: Dictionary in old_save.state.battle.undo:checkpoint.battle.erase("balance_revision")
	old_save.erase("checksum");old_save.checksum=Store.canonical(old_save).sha256_text()
	var restored: Dictionary=Store.validate(JSON.parse_string(Store.canonical(old_save)),content)
	check(restored.ok,"legacy save with a live undo checkpoint loads")
	if restored.ok:
		check(restored.state.battle.undo[0].battle.balance_revision==1,"legacy undo checkpoint retains old balance")
		var undone: Dictionary=Rules.reduce(restored.state,command(restored.state,"undo","lin",{}),content)
		check(undone.ok and Rules.same(undone.next_state.battle.heroes.lin.cell,[1,7]) and Rules.Hazards.enemy_damage(undone.next_state.battle,2)==2,"legacy undo restores position and old damage")
	var invalid: Dictionary=Store.envelope(old_state,content).duplicate(true)
	invalid.state.battle.balance_revision=2.5;invalid.erase("checksum");invalid.checksum=Store.canonical(invalid).sha256_text()
	check(not Store.validate(JSON.parse_string(Store.canonical(invalid)),content).ok,"reject fractional balance version")
	var records: Array=[]
	for difficulty: String in ["relaxed","standard","hard"]:
		for mission: String in ["M01","M02","M03"]:
			var s: Dictionary=Rules.fresh(content,"guide-follow",{"difficulty":difficulty})
			s.campaign.day=int(content.boards[mission].day);Rules.deploy(s,content,mission)
			var actions: Array=[]
			for turn: int in range(int(s.battle.limit)):
				if s.campaign.phase!="battle":break
				for cycle: int in range(2):
					for actor: String in s.battle.heroes:
						if s.campaign.phase!="battle":break
						var hint: Dictionary=Guide.next_step(s,content,actor)
						if hint.get("action","").is_empty() or hint.action=="end_round":continue
						var result: Dictionary=Rules.reduce(s,command(s,hint.action,actor,hint.get("payload",{})),content)
						check(result.ok,"hint is actionable "+mission+" "+str(hint))
						if result.ok:actions.append({"actor":actor,"kind":hint.action,"payload":hint.get("payload",{}),"round":s.battle.round});s=result.next_state
				if s.campaign.phase=="battle":
					var result: Dictionary=Rules.reduce(s,command(s,"end_round",s.battle.heroes.keys()[0],{}),content)
					check(result.ok,"guided end round");s=result.next_state
			var outcome: String=s.campaign.get("last_result",{}).get("outcome","unfinished")
			check(outcome=="success","following visible suggestions completes "+mission+" "+difficulty+" outcome="+outcome)
			if mission=="M01":
				check(actions.filter(func(a: Dictionary):return a.payload.get("target","")=="map").is_empty(),"mandatory completion does not force the optional map")
			records.append({"mission":mission,"difficulty":difficulty,"outcome":outcome,"round":s.battle.round,"actions":actions})
	var file:=FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-guided-paths.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"kind":"production hint follower; isolated fresh first three missions, no specialty or equipment use; not human evidence","records":records},"  "));file.close()
	var scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene)
	check(scene.session.state.campaign.difficulty=="relaxed","first launch starts relaxed even if introduction is closed")
	var before: String=Store.canonical(scene.session.state)
	scene.preview_guidance()
	check(scene.inline_pending and Store.canonical(scene.session.state)==before,"suggestion button previews only")
	scene.preview_guidance()
	check(Store.canonical(scene.session.state)==before,"repeated preview button does not execute")
	scene.commit_pending();scene.finish_feedback()
	check(scene.session.state.revision==1,"explicit confirm executes once")
	scene.sound.stop_audio();scene.queue_free();await process_frame
	print("P4_TUNING_RESULTS: checks=%d failures=%d" % [checks,failures]);quit(1 if failures else 0)

func check_reachability() -> void:
	for mission: String in content.boards:
		var s: Dictionary=Rules.fresh(content,"reachability")
		s.campaign.day=int(content.boards[mission].day);Rules.deploy(s,content,mission)
		for actor: String in s.battle.heroes:
			for carrying: bool in [false,true]:
				s.battle.heroes[actor].carrying="test-load" if carrying else ""
				var expected: Array=[]
				for y: int in range(8):
					for x: int in range(8):
						var cell: Array=[x,y]
						if not s.battle.barriers.has(str(cell)) and Rules.move_cost(s.battle,s.battle.heroes[actor].cell,cell,Rules.movement_budget(s,actor))>=0:expected.append(cell)
				check(Rules.reachable_cells(s,actor)==expected,"single flood matches individual paths "+mission+" "+actor+" carrying="+str(carrying))
				s.battle.heroes[actor].carrying=""
			s.battle.heroes[actor].ap=0
			check(Rules.reachable_cells(s,actor).is_empty(),"spent actor has no highlighted cells")
			s.battle.heroes[actor].ap=2
func write_fixture(path: String,text: String) -> void:
	var file:=FileAccess.open(path,FileAccess.WRITE)
	file.store_string(text);file.close()
func check_storage_cache() -> void:
	var path: String="user://tests/cache-check-%d/save.json"%Time.get_ticks_usec()
	var store=Store.new()
	var s: Dictionary=Rules.fresh(content,"cached-save")
	check(store.save_slot(path,s,content).ok,"cache initial validated save")
	var moved: Dictionary=Rules.reduce(s,command(s,"move","lin",{"cell":[1,6]}),content)
	check(store.save_slot(path,moved.next_state,content).ok,"cache reuses unchanged primary with exact backup")
	var backup: String=FileAccess.get_file_as_string(path+".bak")
	var good: String=FileAccess.get_file_as_string(path)
	write_fixture(path,"broken{")
	check(not store.save_slot(path,s,content).ok and FileAccess.get_file_as_string(path+".bak")==backup,"cached primary byte corruption refuses replacement and preserves backup")
	var broken: Dictionary=JSON.parse_string(good)
	broken.state.battle.undo[0].battle.heroes.lin.hp=-1
	broken.erase("checksum");broken.checksum=Store.canonical(broken).sha256_text()
	write_fixture(path,Store.canonical(broken))
	check(not store.save_slot(path,s,content).ok and FileAccess.get_file_as_string(path+".bak")==backup,"changed checksum-valid primary with corrupt undo is revalidated and rejected")
	broken=JSON.parse_string(good);broken.state.battle.undo[0].campaign.id="other-campaign"
	broken.erase("checksum");broken.checksum=Store.canonical(broken).sha256_text()
	check(not Store.validate(broken,content).ok,"undo cannot restore a different campaign")
	broken=JSON.parse_string(good);broken.state.battle.heroes.lin.hp=1
	check(not Store.validate(broken,content).ok,"outer checksum still protects changed state")
	write_fixture(path,backup)
	check(store.save_slot(path,moved.next_state,content).ok,"valid external primary replacement is revalidated and accepted")
	check(Store.canonical(store.load_slot(path,content).state)==Store.canonical(moved.next_state),"cached save reload matches committed state")
	for suffix: String in ["",".bak",".tmp",".bak.tmp"]:
		if FileAccess.file_exists(path+suffix):DirAccess.remove_absolute(path+suffix)
