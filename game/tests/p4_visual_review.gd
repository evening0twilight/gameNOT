extends "res://tests/gui_external.gd"
## Isolated UI fixtures, not human or natural-campaign acceptance.
var captures: Array=[]
func capture(name: String) -> void:
	for frame: int in range(5):await process_frame
	await RenderingServer.frame_post_draw
	var directory: String=ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-visual-review")
	DirAccess.make_dir_recursive_absolute(directory)
	root.get_texture().get_image().save_png(directory.path_join(name+".png"))
	captures.append({"name":name,"screen":DisplayServer.window_get_current_screen(),"primary":DisplayServer.get_primary_screen(),"size":str(root.size)})
func close_windows(scene: Node) -> void:
	for child: Node in scene.get_children():
		if child is Window and not child is ConfirmationDialog:child.queue_free()
func launch() -> void:
	await super.launch();await process_frame
	var scene=current_scene
	scene.sound.muted=true;scene.sound.apply_levels()
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	scene.session.state=scene.Rules.fresh(scene.session.content,"isolated-p4-visual-review")
	scene.font_size=24;scene.render()
	await capture("m01-guidance-large-font")
	scene.propose("move",{"cell":[1,6]});await capture("inline-action-preview");scene.cancel_selection()
	scene.show_help();await capture("help");close_windows(scene);await process_frame
	scene.new_campaign();await capture("difficulty-and-weather");close_windows(scene);await process_frame
	scene.session.state.campaign.day=18;scene.session.state.chapter_one.main_completed=18
	scene.Rules.settle(scene.session.state,scene.session.content);scene.session.state.campaign.phase="camp"
	scene.session.state.product.facilities.workshop=2;scene.render()
	scene.show_workshop();await capture("equipment-and-facilities");close_windows(scene);await process_frame
	scene.show_history_repair();await capture("historical-repair");close_windows(scene);await process_frame
	scene.audio_settings();await capture("audio-controls");close_windows(scene);await process_frame
	var path: String=ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-visual-review/record.json")
	var file:=FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify({"kind":"isolated visual fixtures","captures":captures,"human_acceptance":false},"  "));file.close()
	await process_frame
	print("P4_VISUAL_REVIEW: ",captures.size()," screenshots on non-primary screen")
	scene.sound.stop_audio()
	for frame: int in range(15):await process_frame
	quit()
