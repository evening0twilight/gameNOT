extends Node
## Opt-in, local-only packaged test runner. Does not use the player's campaign slot.
var scene: Node
var checks: Array=[]
var started: int=0
var output: String
func check(ok: bool,description: String) -> void:
	checks.append({"ok":ok,"description":description})
	if not ok:printerr("NATIVE_CHECK_FAIL: ",description)
func wait_frames(count: int=3) -> void:
	for frame: int in range(count):await get_tree().process_frame
func run(owner_scene: Node) -> void:
	scene=owner_scene;started=Time.get_ticks_msec()
	output="user://diagnostics/baseline018-native-%d" % Time.get_unix_time_from_system()
	DirAccess.make_dir_recursive_absolute(output)
	check(scene.session.path.begins_with("user://tests/"),"isolated campaign path")
	if not checks[-1].ok:finish();return
	check(scene.session.state.campaign.phase=="briefing","production new-game preparation")
	scene.propose("depart",{});scene.confirmation.hide();scene.commit_pending();scene.finish_feedback()
	for child: Node in scene.get_children():
		if child is Window and child!=scene.confirmation:child.queue_free()
	await wait_frames()
	check(scene.session.state.campaign.phase=="battle" and scene.session.state.actors.lin.fatigue==18,"preparation deploys and charges fatigue once")
	var font: int=scene.font_size
	var dimensions: Vector2i=get_window().size
	for resolution: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
		# Logical viewport checks work on smaller monitors without moving onto the primary display.
		get_window().content_scale_size=resolution
		for size: int in [16,20,24]:
			scene.font_size=size;scene.render();await wait_frames(5)
			check(scene.root.get_combined_minimum_size().x<=resolution.x and scene.root.get_combined_minimum_size().y<=resolution.y,"UI minimum fits %s font %d" % [resolution,size])
	get_window().content_scale_size=Vector2i(1280,720);get_window().size=dimensions
	scene.font_size=font
	for mission: String in ["M01","M02","M03"]:
		scene.finish_feedback();scene.confirmation.hide()
		scene.session.state=scene.Rules.fresh(scene.session.content,"native-"+mission,{"difficulty":"relaxed"})
		scene.session.state.campaign.day=int(scene.session.content.boards[mission].day)
		scene.Rules.deploy(scene.session.state,scene.session.content,mission)
		scene.session.path="user://tests/native-%d/%s.json" % [started,mission]
		check(scene.session.store.save_slot(scene.session.path,scene.session.state,scene.session.content).ok,"initial save "+mission)
		var steps: int=0
		for turn: int in range(int(scene.session.state.battle.limit)):
			if scene.session.state.campaign.phase!="battle":break
			for cycle: int in range(2):
				var actors: Array=scene.session.state.battle.heroes.keys()
				for actor: String in actors:
					if scene.session.state.campaign.phase!="battle":break
					var hint: Dictionary=scene.Guidance.next_step(scene.session.state,scene.session.content,actor)
					if hint.get("action","").is_empty() or hint.action=="end_round":continue
					scene.selected=actor;scene.action=hint.action
					var revision: int=scene.session.state.revision
					scene.propose(hint.action,hint.get("payload",{}).duplicate(true))
					check(scene.session.state.revision==revision,"preview unchanged "+mission)
					scene.confirmation.hide();scene.commit_pending()
					check(scene.session.state.revision==revision+1,"commit once "+mission)
					steps+=1
					# First mission plays all real feedback; later missions use the supported skip control.
					if mission!="M01":scene.finish_feedback()
					while scene.feedback_active():await get_tree().process_frame
					await wait_frames(1)
			if scene.session.state.campaign.phase=="battle":
				scene.action="end_round";scene.propose("end_round",{});scene.confirmation.hide();scene.commit_pending()
				while scene.feedback_active():await get_tree().process_frame
		check(scene.session.state.campaign.get("last_result",{}).get("outcome","")=="success","guided completion "+mission)
		var stable: String=scene.session.store.canonical(scene.session.state)
		var loaded: Dictionary=scene.session.load_game()
		check(loaded.ok and scene.session.store.canonical(scene.session.state)==stable,"save/load exact roundtrip "+mission)
		if DisplayServer.get_name()!="headless":
			scene.render();await wait_frames(3);await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(output.path_join(mission+"-result.png"))
		print("NATIVE_MISSION: ",mission," actions=",steps)
	finish()
func finish() -> void:
	var passed: bool=true
	for result: Dictionary in checks:passed=passed and result.ok
	var report: Dictionary={"kind":"packaged local automated acceptance; not human usability evidence","platform":OS.get_name(),"native_windows":OS.get_name()=="Windows","rendered":DisplayServer.get_name()!="headless","checks":checks,"passed":passed,"human_audio_motion_review":false,"human_difficulty_review":false,"seconds":(Time.get_ticks_msec()-started)/1000.0,"runtime":scene.metrics.report(),"screen":DisplayServer.window_get_current_screen() if DisplayServer.get_name()!="headless" else -1,"primary":DisplayServer.get_primary_screen() if DisplayServer.get_name()!="headless" else -1}
	var file:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	print("NATIVE_ACCEPTANCE: passed=",passed," windows=",report.native_windows," report=",ProjectSettings.globalize_path(output.path_join("report.json")))
	scene.sound.stop_audio()
	await wait_frames(15)
	get_tree().quit(0 if passed else 1)
