extends SceneTree
const Art=preload("res://scripts/presentation/visual_assets.gd")
const Plan=preload("res://scripts/presentation/action_feedback.gd")
var checks: int=0
var failures: int=0
var scene: Node
func check(value: bool,context: String) -> void:
	checks+=1
	if not value:failures+=1;printerr("FEEDBACK_FAIL: "+context)
func _initialize() -> void:call_deferred("run")
func reset() -> void:
	scene.finish_feedback();scene.confirmation.hide()
	scene.session.state=scene.Rules.fresh(scene.session.content,"feedback-fixture")
	scene.title_screen=false;scene.selected="lin";scene.pending={};scene.inline_pending=false
func execute(kind: String,payload: Dictionary) -> void:
	scene.action=kind;scene.propose(kind,payload);scene.confirmation.hide();scene.commit_pending()
func run() -> void:
	scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene)
	for id: String in ["lin","xu","su","chen","ye","he","mo","jiang"]:
		for frame: int in range(6):
			var texture: AtlasTexture=Art.motion(id,frame)
			check(Rect2(Vector2.ZERO,texture.atlas.get_size()).encloses(texture.region),"motion frame bounds "+id+str(frame))
		check(Art.motion(id,0).get_image().get_data()!=Art.motion(id,1).get_image().get_data(),"actual distinct walking poses "+id)
	for id: String in ["a","b"]:
		var pixels: Image=load("res://assets/motion_p4/crew_%s.png"%id).get_image()
		check(pixels.get_pixel(0,0).a<.01,"real transparent background "+id)
	reset()
	var before: String=scene.session.store.canonical(scene.session.state)
	scene.action="move";scene.propose("move",{"cell":[1,4]})
	check(scene.session.store.canonical(scene.session.state)==before,"preview never mutates gameplay")
	scene.commit_pending()
	check(scene.feedback_active(),"successful move starts presentation")
	check(scene.feedback_plan.paths.lin.size()==4,"walk follows each intermediate tile")
	check(scene.feedback_plan.events.size()==3,"one footstep cue per tile")
	var committed: String=scene.session.store.canonical(scene.session.state)
	var saved: String=FileAccess.get_file_as_string(scene.session.path)
	scene.propose("end_round",{});scene.commit_pending()
	check(scene.session.store.canonical(scene.session.state)==committed,"input during playback cannot submit twice")
	scene.finish_feedback()
	check(scene.session.store.canonical(scene.session.state)==committed and FileAccess.get_file_as_string(scene.session.path)==saved,"skip changes neither state nor disk")
	check(scene.sound.timeline.is_empty(),"skipping cancels future audio cues")
	execute("undo",{})
	check(scene.Rules.same(scene.session.state.battle.heroes.lin.cell,[1,7]),"undo still restores committed move")
	var corners: Array=[[2,3],[1,3],[1,2],[2,2]]
	check(Plan.direction(corners,.1)==Vector2.LEFT and Plan.direction(corners,.5)==Vector2.UP and Plan.direction(corners,.9)==Vector2.RIGHT,"body direction follows each corner")
	check(Plan.step_position(corners,0)==Vector2(2,3) and Plan.step_position(corners,1)==Vector2(2,2),"movement starts and ends exactly at cells")
	reset()
	var target: String=""
	for o: Dictionary in scene.session.state.battle.objects.values():
		if o.kind=="rescue":target=o.id;break
	scene.session.state.battle.heroes.lin.cell=[int(scene.session.state.battle.objects[target].cell[0])-1,int(scene.session.state.battle.objects[target].cell[1])]
	check(scene.Guidance.next_step(scene.session.state,scene.session.content,"lin").action=="stabilize","adjacent unstable resident prompts stabilization")
	execute("stabilize",{"target":target})
	check(scene.feedback_active() and scene.feedback_plan.events[0].sound=="stabilize","stabilization timed cue")
	scene.finish_feedback()
	check(scene.Guidance.next_step(scene.session.state,scene.session.content,"lin").action=="pickup","stable resident prompts pickup")
	execute("pickup",{"target":target})
	check(scene.feedback_active() and scene.session.state.battle.heroes.lin.carrying==target,"pickup commits then animates")
	scene.finish_feedback();scene.session.state.battle.heroes.lin.ap=2
	check(scene.Guidance.next_step(scene.session.state,scene.session.content,"lin").key=="return","carrying prompts return")
	scene.session.state.battle.heroes.lin.cell=scene.session.content.boards.M01.exits[0].duplicate()
	check(scene.Guidance.next_step(scene.session.state,scene.session.content,"lin").action=="extract","at exit prompts delivery")
	execute("extract",{})
	check(scene.session.state.battle.objects[target].delivered and scene.feedback_active(),"delivery has visible completion timeline")
	scene.finish_feedback()
	for kind: String in ["attack","push"]:
		reset()
		var id: String=str(scene.session.state.battle.enemies.keys()[0])
		scene.session.state.battle.enemies[id].cell=[2,6]
		scene.session.state.battle.heroes.lin.cell=[1,6]
		var previous: Dictionary=scene.session.state.duplicate(true)
		execute(kind,{"target":id})
		check(scene.feedback_active() and scene.feedback_plan.target==id,kind+" names actual target")
		check(scene.feedback_plan.events[0].at==scene.feedback_plan.impact,kind+" audio aligned with impact")
		check(scene.feedback_plan.before==previous.battle,kind+" retains immutable prior positions")
	reset()
	execute("end_round",{})
	check(scene.feedback_active() and not scene.feedback_plan.machines.is_empty(),"enemy phase resolves machine feedback sequentially")
	var last: float=-1
	for event: Dictionary in scene.feedback_plan.events:
		check(event.at>=last and event.at<scene.feedback_plan.duration,"audio timeline ordered and bounded");last=event.at
	var current: String=scene.session.store.canonical(scene.session.state)
	scene.feedback_elapsed=float(scene.feedback_plan.duration)+.01;scene._process(0)
	check(not scene.feedback_active() and scene.session.store.canonical(scene.session.state)==current,"automatic playback finish never advances another round")
	reset();scene.session.state.battle.heroes.lin.ap=0
	check(scene.Guidance.next_step(scene.session.state,scene.session.content,"lin").key=="no_ap","no-AP guidance does not suggest illegal action")
	# Last exit must keep the battle visible until the departure animation finishes.
	reset()
	for h: Dictionary in scene.session.state.battle.heroes.values():h.left=h.id!="lin"
	scene.session.state.battle.heroes.lin.cell=[0,7]
	execute("leave_site",{})
	check(scene.session.state.campaign.phase=="settlement" and scene.feedback_active(),"last departure retains its animation across settlement")
	check(not scene.root.find_children("*","Control",true,false).filter(func(n: Node):return n.get_script()==scene.BoardView).is_empty(),"board remains visible for final departure")
	scene.finish_feedback()
	check(scene.root.find_children("*","Control",true,false).filter(func(n: Node):return n.get_script()==scene.BoardView).is_empty(),"settlement appears after final departure")
	scene.sound.stop_audio();scene.queue_free();await process_frame
	print("P4_FEEDBACK_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
