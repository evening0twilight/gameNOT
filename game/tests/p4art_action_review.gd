extends "res://tests/product018_visual_review.gd"
## Isolated art/action fixtures use production command submission and feedback.
## Positions/AP below are fixture setup, never claimed as campaign progression.
var canvas: SubViewport
var frame_number: int=0
var clips: Array=[]
func _initialize() -> void:root.hide();root.gui_embed_subwindows=true;call_deferred("run")
func execute(kind: String,payload: Dictionary) -> void:
	scene.action=kind;scene.propose(kind,payload);scene.confirmation.hide();scene.commit_pending()
func reset_fixture() -> void:
	scene.finish_feedback();close_modals();await process_frame
	scene.session.state=scene.Rules.fresh(scene.session.content,"p4art-action-fixture")
	scene.title_screen=false;scene.selected="lin";scene.pending={};scene.inline_pending=false;scene.paused=false;scene.render()
func capture_clip(name: String) -> void:
	if not scene.feedback_active():failures.append("missing animation "+name);return
	var canonical: String=scene.session.store.canonical(scene.session.state)
	var duration: float=float(scene.feedback_plan.duration)
	clips.append({"name":name,"start_frame":frame_number,"frames":48,"game_seconds":duration,"fixture":true})
	scene.paused=true
	for tick: int in range(48):
		scene.feedback_elapsed=duration*float(tick)/47.0
		await process_frame;await process_frame;await RenderingServer.frame_post_draw
		canvas.get_texture().get_image().save_png("res://../outputs/p4art-action-frames/frame-%04d.png"%frame_number);frame_number+=1
	if scene.session.store.canonical(scene.session.state)!=canonical:failures.append("animation changed state "+name)
	scene.paused=false;scene.finish_feedback()
func run() -> void:
	DirAccess.make_dir_recursive_absolute("res://../outputs/p4art-action-frames")
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	scene=load("res://scenes/main.tscn").instantiate();canvas.add_child(scene);scene.sound.set_process(false);scene.sound.stop_audio()
	await reset_fixture();execute("move",{"cell":[3,6]});await capture_clip("walk_and_corner")
	for kind: String in ["attack","push"]:
		await reset_fixture();var target: String=scene.session.state.battle.enemies.keys()[0]
		scene.session.state.battle.enemies[target].cell=[2,6];scene.session.state.battle.heroes.lin.cell=[1,6];scene.render()
		execute(kind,{"target":target});await capture_clip(kind)
	await reset_fixture()
	var target: String=""
	for object: Dictionary in scene.session.state.battle.objects.values():
		if object.kind=="rescue":target=object.id;break
	scene.session.state.battle.heroes.lin.cell=[int(scene.session.state.battle.objects[target].cell[0])-1,int(scene.session.state.battle.objects[target].cell[1])];scene.render()
	execute("stabilize",{"target":target});await capture_clip("stabilize")
	execute("pickup",{"target":target});await capture_clip("pickup")
	await reset_fixture();execute("end_round",{});await capture_clip("machine_response")
	var file:=FileAccess.open("res://../outputs/p4art-action-review.json",FileAccess.WRITE);file.store_string(JSON.stringify({"failures":failures,"clips":clips,"scope":"GPU production rendering of committed commands from isolated fixtures; silent slow-motion art review, not real-time input or audio capture"},"\t"));file.close()
	scene.sound.stop_audio();scene.queue_free();await process_frame
	print("P4ART_ACTION_REVIEW: clips=",clips.size()," failures=",failures);quit(1 if failures else 0)
