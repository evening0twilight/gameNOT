extends "res://tests/product018_story_tests.gd"
const Preview=preload("res://scripts/presentation/action_preview.gd")
const Camp=preload("res://scripts/presentation/camp_workspace.gd")
func text_in(node: Node) -> String:
	var rows: Array[String]=[]
	for label: Node in node.find_children("*","Label",true,false):rows.append(label.text)
	return "\n".join(rows)
func close_windows(ui: Control) -> void:
	for node: Node in ui.get_children():
		if node is Window:node.hide();if node!=ui.confirmation:node.queue_free()
func run() -> void:
	c=Catalog.load_catalog();I18n.initialize()
	# Editorial fixtures explicitly cover absence and later recovery, not playthroughs.
	for id: String in Journey.catalog().scene_beats:
		var node: Dictionary=Stories.nodes(c)[id]
		for mode: String in ["present","recovery","letter"]:
			prepare(node,mode);check(act("story_open",{"node":id}).ok,"open staging fixture "+id+mode)
			var view: Dictionary=Journey.scene(s,c,id)
			check(view.pages.any(func(p: Dictionary):return p.has("beat_before"))==(mode=="present"),"physical staging respects delivery "+id+mode)
			var saved: String=Store.canonical(view)
			for actor: Dictionary in s.actors.values():actor.ready_day=1
			s.product.withdrawn=[]
			check(Store.canonical(Journey.scene(s,c,id))==saved,"staging archive not rewritten "+id+mode)
	var ui=load("res://scenes/main.tscn").instantiate();root.add_child(ui)
	for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080)]:
		root.size=dimensions;root.content_scale_size=dimensions
		for font: int in [16,20,24]:
			ui.font_size=font;ui.render()
			for frame: int in range(4):await process_frame
			check(ui.root.size.x<=dimensions.x and ui.root.size.y<=dimensions.y,"title fits screen and font "+str(dimensions)+str(font))
	root.size=Vector2i(1280,720);root.content_scale_size=root.size;ui.font_size=20
	ui.title_screen=false
	ui.session.start(c,"user://tests/quality-%d/autosave.json"%Time.get_ticks_usec(),"quality-flow")
	ui.propose("depart",{});ui.confirmation.hide();ui.commit_pending();ui.finish_feedback();close_windows(ui);await process_frame
	var before: String=Store.canonical(ui.session.state)
	ui.propose("move",{"cell":[3,6]})
	check(ui.inline_pending and ui.message.contains("2 → 1") and ui.message.contains("第 4 列"),"movement preview shows actual AP and one-based destination")
	check(Store.canonical(ui.session.state)==before,"visible action preview is read only")
	ui.cancel_selection();check(Store.canonical(ui.session.state)==before,"cancel still leaves all state unchanged")
	ui.propose("emergency_retreat",{"confirmed":true});ui.confirmation.hide();ui.commit_pending();ui.finish_feedback();close_windows(ui);await process_frame
	ui.propose("enter_camp",{});ui.confirmation.hide();ui.commit_pending();ui.finish_feedback();close_windows(ui);await process_frame
	check(ui.session.state.campaign.phase=="camp","real M01 retreat reaches new camp screen")
	before=Store.canonical(ui.session.state)
	Camp.short_talk(ui,"lin")
	var parent: Window
	for child: Node in ui.get_children():
		if child is Window and child!=ui.confirmation and child.visible:parent=child
	var nested: Dictionary=ui.modal("nested navigation")
	check(is_instance_valid(parent) and not parent.visible and nested.window.visible,"only the top exclusive dialog is visible")
	nested.window.queue_free();await process_frame;await process_frame
	check(parent.visible,"closing a drill-down restores its parent")
	check(Store.canonical(ui.session.state)==before,"camp drawer navigation does not spend projects or talks")
	close_windows(ui);await process_frame
	prepare(Stories.nodes(c).L01,"present");check(act("story_open",{"node":"L01"}).ok,"open isolated story for response regression")
	ui.session.state=s
	ui.propose("story_choice",{"node":"L01","choice":"a"});ui.confirmation.hide();ui.commit_pending();await process_frame
	var visible: String=""
	for child: Node in ui.get_children():
		if child is Window and child!=ui.confirmation and child.visible:visible+=text_in(child)
	check(visible.contains("保温杯") and not visible.contains("林岚尝了尝汤"),"choice opens the new reply instead of replaying the opening")
	close_windows(ui);await process_frame
	var audio=ui.sound;audio.stop_audio();audio.output_enabled=true;audio.muted=false;audio.effects_volume=.6;audio.music_volume=.35;audio.apply_levels()
	audio.ambience("camp");await create_timer(1.3).timeout
	audio.ambience("battle");await create_timer(.6).timeout
	var power: float=pow(audio.music.volume_linear,2)+pow(audio.fading_music.volume_linear,2)
	check(absf(power-1.0)<.02,"crossfade retains power at midpoint")
	audio.play("injury",true);await create_timer(.15).timeout
	check(audio.music_duck<.7,"injury cue gets short music space")
	await create_timer(.85).timeout
	check(is_equal_approx(audio.music_duck,1.0),"music recovers after priority cue")
	var limiters: int=0
	for index: int in range(AudioServer.get_bus_effect_count(0)):
		if AudioServer.get_bus_effect(0,index).resource_name=="NightTideHeadroom":limiters+=1
	check(limiters==1,"one shared master limiter prevents summed cue clipping")
	audio.stop_audio();ui.queue_free();await create_timer(.2).timeout
	print("P4QUALITY_RESULTS: checks=%d failures=%d"%[checks,failures]);quit(1 if failures else 0)
