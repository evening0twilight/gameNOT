extends SceneTree
## Developer GUI runner: always selects a non-primary display before loading the real scene.
func _initialize() -> void:
	var count: int=DisplayServer.get_screen_count()
	var primary: int=DisplayServer.get_primary_screen()
	if count<2:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_MINIMIZED)
		push_error("External display required; GUI validation not started")
		quit(1)
		return
	var external: int=0 if primary!=0 else 1
	DisplayServer.window_set_current_screen(external)
	DisplayServer.window_set_position(DisplayServer.screen_get_position(external)+Vector2i(40,60))
	print("GUI_EXTERNAL_DISPLAY: screen=%d primary=%d total=%d" % [external,primary,count])
	call_deferred("launch")
func launch() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	if "--isolated-ui-review" in OS.get_cmdline_user_args():
		await scene_changed
		var scene=current_scene
		scene.session.path="user://tests/ui-review-%d/autosave.json" % Time.get_ticks_usec()
		scene.session.state=scene.Rules.fresh(scene.session.content,"isolated-ui-review")
		if "--camp" in OS.get_cmdline_user_args():
			for kind: String in ["emergency_retreat","enter_camp"]:
				var preview: Dictionary=scene.session.preview({"command_id":"review-"+kind,"root_decision_id":"review-"+kind,"expected_revision":scene.session.state.revision,"kind":kind,"actor_id":"lin","payload":{"confirmed":true}})
				if preview.ok:scene.session.state=preview.next_state
		if "--p2-review" in OS.get_cmdline_user_args():
			scene.session.state.campaign.day=4
			scene.Rules.deploy(scene.session.state,scene.session.content,"M04")
			scene.session.state.chapter_one.roster=["lin","su","chen"]
			scene.Rules.deploy(scene.session.state,scene.session.content,"M04")
		scene.render()
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--resume-review="):
			if current_scene==null:await scene_changed
			current_scene.session.path="user://tests/"+argument.trim_prefix("--resume-review=")+"/autosave.json"
			var result: Dictionary=current_scene.session.load_game()
			if result.ok:current_scene.render()
