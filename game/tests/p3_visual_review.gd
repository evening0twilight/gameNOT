extends "res://tests/gui_external.gd"
## Isolated presentation fixtures on the non-primary monitor; no player save mutations.
func capture(name: String) -> void:
	for frame: int in range(5):await process_frame
	await RenderingServer.frame_post_draw
	var directory: String=ProjectSettings.globalize_path("res://").path_join("../outputs/p3-visual-review")
	DirAccess.make_dir_recursive_absolute(directory)
	root.get_texture().get_image().save_png(directory.path_join(name+".png"))
func launch() -> void:
	await super.launch()
	await process_frame
	var scene=current_scene
	scene.session.state=scene.Rules.fresh(scene.session.content,"isolated-p3-visual-review")
	scene.session.state.campaign.day=18;scene.session.state.chapter_one.roster=["ye","he","mo"]
	scene.Rules.deploy(scene.session.state,scene.session.content,"M18")
	scene.selected="ye";scene.render()
	await capture("late-crew-board")
	scene.show_site()
	await capture("site-camera")
	for child: Node in scene.get_children():
		if child is Window and not child is ConfirmationDialog:child.queue_free()
	await process_frame
	scene.session.state.campaign.phase="camp"
	scene.session.state.chapter_one.scenes.P_ye_2={"seen":true,"choice":"","status":"seen"}
	scene.show_story("P_ye_2")
	await capture("personal-scene")
	for child: Node in scene.get_children():
		if child is Window and not child is ConfirmationDialog:child.queue_free()
	await process_frame
	scene.Rules.settle(scene.session.state,scene.session.content)
	scene.session.state.campaign.phase="settlement";scene.session.state.chapter_one.finished=true;scene.session.state.full_campaign.ending="evacuation"
	scene.render()
	await capture("ending-layout-fixture")
	print("P3_VISUAL_REVIEW: four isolated screenshots; screen=",DisplayServer.window_get_current_screen()," primary=",DisplayServer.get_primary_screen())
	quit()
