extends "res://tests/product018_visual_review.gd"
var canvas: SubViewport
func _initialize() -> void:
	root.hide()
	root.gui_embed_subwindows=true
	call_deferred("run")
func screenshot(id: String) -> void:
	await process_frame;await process_frame
	await RenderingServer.frame_post_draw
	var bitmap: Image=canvas.get_texture().get_image()
	if bitmap==null or bitmap.is_empty():failures.append("offscreen image empty "+id);return
	bitmap.save_png("res://../outputs/p4art-"+id+".png")
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	scene=load("res://scenes/main.tscn").instantiate();canvas.add_child(scene)
	await screenshot("title")
	var slot: String="user://tests/product018-visual-%d/autosave.json"%Time.get_ticks_usec()
	scene.session.start(scene.session.content,slot,"product018-visual");scene.title_screen=false;scene.render();await screenshot("preparation")
	scene.Screens.planning_board(scene,scene.session.state.journey.draft);await screenshot("planning");close_modals();await process_frame
	scene.Screens.introduction(scene,"lin");await screenshot("first-contact");close_modals();await process_frame
	scene.Screens.city(scene);await screenshot("city");close_modals();await process_frame
	var loaded: Dictionary=scene.session.store.load_slot("res://../outputs/p4close-before-mentor.json",scene.session.content)
	if loaded.ok:
		scene.session.state=loaded.state;scene.render();await screenshot("camp")
		scene.Screens.profile(scene,"chen");await screenshot("growth")
		for window: Node in scene.get_children():
			if window is Window and window!=scene.confirmation:
				for scroll: Node in window.find_children("*","ScrollContainer",true,false):scroll.scroll_vertical=760
		await screenshot("mentorship");close_modals();await process_frame
		scene.show_story("P_lin_1");await screenshot("dialogue");close_modals();await process_frame
		preload("res://scripts/presentation/story_screen.gd").show(scene,"P_lin_1",0,true);await screenshot("story-overview");close_modals();await process_frame
	else:failures.append("linked day06")
	loaded=scene.session.store.load_slot("res://../outputs/baseline018-linked-day18.json",scene.session.content)
	if loaded.ok:
		scene.session.state=loaded.state;scene.render();scene.Screens.relationships(scene,"su","jiang");await screenshot("relationships");close_modals();await process_frame
	loaded=scene.session.store.load_slot("res://../outputs/baseline018-linked-day24.json",scene.session.content)
	if loaded.ok:
		scene.session.state=loaded.state;scene.render();await screenshot("ending")
	else:failures.append("linked day24")
	scene.session.start(scene.session.content,slot,"product018-action-review");scene.title_screen=false;scene.selected="lin";scene.render()
	scene.propose("depart",{});scene.confirmation.hide();scene.commit_pending();scene.finish_feedback();close_modals()
	if scene.session.state.campaign.phase!="battle":failures.append("actual departure for battle review")
	else:
		await screenshot("battle")
		scene.propose("move",{"cell":[3,6]});scene.confirmation.hide();scene.commit_pending()
		if not scene.feedback_active():failures.append("actual move feedback")
		else:
			scene.paused=true;scene.feedback_elapsed=float(scene.feedback_plan.duration)*.45
			await screenshot("walking")
			if "--capture-motion" in OS.get_cmdline_user_args():
				DirAccess.make_dir_recursive_absolute("res://../outputs/p4art-motion-frames")
				for step: int in range(60):
					scene.feedback_elapsed=float(scene.feedback_plan.duration)*float(step)/60.0
					await screenshot("motion-frames/frame-%03d"%step)
			scene.paused=false;scene.finish_feedback()
	var file:=FileAccess.open("res://../outputs/p4art-visual-review.json",FileAccess.WRITE);file.store_string(JSON.stringify({"failures":failures,"rendered":"hidden root with actual GPU SubViewport","native_input_acceptance":false,"dimensions":[1280,720]},"\t"));file.close()
	print("P4CLOSE_OFFSCREEN: failures=%d"%failures.size());scene.sound.stop_audio();scene.queue_free();await process_frame;quit(1 if failures else 0)
