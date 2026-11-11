extends "res://tests/baseline018_ui.gd"
func screenshot(id: String) -> void:
	await process_frame;await process_frame
	if DisplayServer.get_name()!="headless":
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://../outputs/product018-"+id+".png")
func run() -> void:
	scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene)
	await screenshot("title")
	var slot: String="user://tests/product018-visual-%d/autosave.json"%Time.get_ticks_usec()
	scene.session.start(scene.session.content,slot,"product018-visual");scene.title_screen=false;scene.render()
	await screenshot("preparation")
	scene.Screens.introduction(scene,"lin");await screenshot("first-contact");close_modals();await process_frame
	scene.Screens.city(scene);await screenshot("city");close_modals();await process_frame
	# Actual linked playthrough saves are used for the UI, without inventing recruitment or XP.
	var loaded: Dictionary=scene.session.store.load_slot("res://../outputs/baseline018-linked-day06.json",scene.session.content)
	if loaded.ok:
		scene.session.state=loaded.state;scene.render();await screenshot("camp")
		scene.Screens.profile(scene,"chen");await screenshot("growth");close_modals();await process_frame
		scene.show_story("P_lin_1");await screenshot("dialogue");close_modals();await process_frame
	else:failures.append("linked day06")
	loaded=scene.session.store.load_slot("res://../outputs/baseline018-linked-day18.json",scene.session.content)
	if loaded.ok:
		scene.session.state=loaded.state;scene.render();scene.Screens.relationships(scene,"su","jiang");await screenshot("relationships");close_modals();await process_frame
	var file:=FileAccess.open("res://../outputs/product018-visual-review.json",FileAccess.WRITE);file.store_string(JSON.stringify({"failures":failures,"rendered":DisplayServer.get_name()!="headless","screen":DisplayServer.window_get_current_screen(),"primary":DisplayServer.get_primary_screen()},"\t"));file.close()
	print("PRODUCT018_VISUAL: failures=%d"%failures.size());scene.sound.stop_audio();scene.queue_free();await process_frame;quit(1 if failures else 0)
