extends "res://tests/gui_external.gd"
## Captures actual UI and deterministic presentation samples; gameplay fixtures are isolated.
var output: String
var captures: Array=[]
func capture(name: String) -> void:
	for frame: int in range(5):await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output.path_join(name+".png"))
	captures.append(name)
func close_windows(scene: Node) -> void:
	for child: Node in scene.get_children():
		if child is Window and not child is ConfirmationDialog:child.queue_free()
func launch() -> void:
	await super.launch();await process_frame
	var scene=current_scene
	output=ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-review")
	DirAccess.make_dir_recursive_absolute(output)
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	scene.font_size=20;scene.render()
	await capture("01-first-task")
	scene.show_intro(false,2);await capture("02-rescue-introduction");close_windows(scene);await process_frame
	scene.new_campaign();await capture("03-difficulty");close_windows(scene);await process_frame
	scene.propose("move",{"cell":[1,4]});await capture("04-move-preview");scene.commit_pending()
	scene.set_process(false)
	var board=scene.root.find_children("*","Control",true,false).filter(func(node: Node):return node.get_script()==scene.BoardView)[0]
	board.playhead=.18;await capture("05-walk-stride")
	board.playhead=.35;await capture("06-walk-passing")
	scene.finish_feedback();scene.set_process(true)
	scene.session.state.battle.heroes.lin.cell=[1,2];scene.session.state.battle.heroes.lin.ap=2;scene.render()
	var target: String=""
	for object: Dictionary in scene.session.state.battle.objects.values():
		if object.kind=="rescue" and scene.Rules.distance(object.cell,[1,2])<=1:target=object.id;break
	if not target.is_empty():
		scene.action="stabilize";scene.propose("stabilize",{"target":target});scene.commit_pending();scene.set_process(false)
		board=scene.root.find_children("*","Control",true,false).filter(func(node: Node):return node.get_script()==scene.BoardView)[0]
		board.playhead=.42;await capture("07-stabilize");scene.finish_feedback();scene.set_process(true)
		scene.action="pickup";scene.propose("pickup",{"target":target});scene.commit_pending();scene.set_process(false)
		board=scene.root.find_children("*","Control",true,false).filter(func(node: Node):return node.get_script()==scene.BoardView)[0]
		board.playhead=.45;await capture("08-lift");scene.finish_feedback();scene.set_process(true)
	await capture("09-contextual-next-step")
	var file:=FileAccess.open(output.path_join("record.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"kind":"isolated UI and actual runtime animation samples","captures":captures,"screen":DisplayServer.window_get_current_screen(),"primary":DisplayServer.get_primary_screen(),"human_acceptance":false},"  "));file.close()
	scene.sound.stop_audio()
	for frame: int in range(15):await process_frame
	print("FEEDBACK_VISUAL_REVIEW: ",captures.size()," captures")
	quit()
