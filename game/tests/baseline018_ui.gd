extends SceneTree
var scene: Control
var failures: Array=[]
func _initialize() -> void:
	if DisplayServer.get_name()!="headless":
		if DisplayServer.get_screen_count()<2:quit(2);return
		var external: int=0 if DisplayServer.get_primary_screen()!=0 else 1
		DisplayServer.window_set_current_screen(external);DisplayServer.window_set_position(DisplayServer.screen_get_position(external)+Vector2i(40,60))
	call_deferred("run")
func screenshot(id: String) -> void:
	await process_frame;await process_frame
	if DisplayServer.get_name()!="headless":
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://../outputs/baseline018-"+id+".png")
func close_modals() -> void:
	for child: Node in scene.get_children():
		if child is Window and child!=scene.confirmation:child.queue_free()
func run() -> void:
	scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene)
	await screenshot("title")
	var path: String="user://tests/baseline018-ui-%d/autosave.json"%Time.get_ticks_usec()
	var started: Dictionary=scene.session.start(scene.session.content,path,"ui-baseline018")
	if not started.ok:failures.append("start persistence")
	scene.title_screen=false;scene.render();await screenshot("preparation")
	scene.Screens.profile(scene,"lin");await screenshot("profile");close_modals();await process_frame
	scene.Screens.relationships(scene);await screenshot("relationships");close_modals();await process_frame
	scene.Screens.manual_slots(scene,true);await screenshot("manual-slots");close_modals();await process_frame
	scene.propose("depart",{});await screenshot("departure-preview")
	if scene.pending.get("kind")!="depart":failures.append("departure preview")
	scene.confirmation.hide();scene.commit_pending();scene.finish_feedback();await screenshot("mission-one");close_modals();await process_frame
	if scene.session.state.campaign.phase!="battle":failures.append("actual UI departure")
	scene.propose("emergency_retreat",{"confirmed":true});scene.confirmation.hide();scene.commit_pending();scene.finish_feedback();await screenshot("settlement")
	scene.propose("enter_camp",{});scene.confirmation.hide();scene.commit_pending();scene.finish_feedback();await screenshot("camp")
	scene.Screens.profile(scene,"lin");await screenshot("growth-comparison");close_modals();await process_frame
	var file:=FileAccess.open("res://../outputs/baseline018-ui.json",FileAccess.WRITE);file.store_string(JSON.stringify({"failures":failures,"rendered":DisplayServer.get_name()!="headless","flow":"title > persisted preparation > profiles > relations > slots > departure preview > battle > retreat settlement > camp > growth comparison"},"\t"));file.close()
	print("BASELINE018_UI: failures=%d"%failures.size());scene.sound.stop_audio();scene.queue_free();await process_frame;quit(0 if failures.is_empty() else 1)
