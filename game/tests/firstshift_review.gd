extends SceneTree
var ui: Control
var canvas: SubViewport
var failures: Array=[]
var log: Array=[]
var checks: int=0
func _initialize() -> void:
	if DisplayServer.get_name()!="headless":root.hide()
	root.gui_embed_subwindows=true;call_deferred("run")
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failures.append(message);printerr("FIRSTSHIFT_FAIL: "+message)
func close_windows() -> void:
	for child: Node in ui.get_children():
		if child is Window:child.hide();if child!=ui.confirmation:child.queue_free()
func shot(id: String) -> void:
	if DisplayServer.get_name()=="headless":return
	await process_frame;await process_frame;await RenderingServer.frame_post_draw
	canvas.get_texture().get_image().save_png("res://../outputs/firstshift-"+id+".png")
func act(kind: String,payload: Dictionary={}) -> bool:
	var before: int=ui.session.state.revision
	if kind!="undo":ui.action=kind
	ui.propose(kind,payload);ui.confirmation.hide()
	if ui.session.state.revision==before:ui.commit_pending()
	ui.finish_feedback();close_windows()
	log.append({"kind":kind,"actor":ui.selected,"payload":payload,"day":ui.session.state.campaign.day,"round":ui.session.state.battle.round,"revision":ui.session.state.revision,"message":ui.message})
	return ui.session.state.revision>before
func play_mission(captures: bool) -> void:
	var captured: Array=[]
	for turn: int in range(240):
		if ui.session.state.campaign.phase!="battle":break
		if captures and ui.FirstShift.active(ui):
			var lesson: Dictionary=ui.FirstShift.lesson(ui)
			if not captured.has(lesson.id):captured.append(lesson.id);await shot(lesson.id)
			if lesson.id=="forecast":
				var before: Dictionary=ui.session.state.battle.duplicate(true)
				ui.tutorial_ack("forecast");check(before==ui.session.state.battle,"reading forecast does not spend AP, advance time or clear undo")
				continue
		var next: Dictionary=ui.Guidance.next_step(ui.session.state,ui.session.content,ui.selected)
		if next.has("actor"):ui.selected=next.actor;ui.action="move";ui.render();continue
		if next.get("action","").is_empty():failures.append("No legal suggestion "+str(next));break
		if not act(next.action,next.get("payload",{}).duplicate(true)):failures.append("Rejected "+str(next));break
		await process_frame
	check(ui.session.state.campaign.phase=="settlement","mission reaches actual settlement")
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui);ui.reduced_motion=true
	check(ui.session.start(ui.session.content,"user://tests/firstshift-%d/save.json"%Time.get_ticks_usec(),"firstshift-live").ok,"new real campaign")
	await compatibility_and_preferences()
	ui.title_screen=false;ui.render();await shot("briefing")
	check(act("depart",ui.session.state.journey.draft.duplicate(true)),"departure")
	check(ui.FirstShift.lesson(ui).id=="move","only movement lesson first")
	check(ui.action=="move" and not ui.reach_cache.is_empty(),"deployment opens movement with reachable cells")
	await layout_review("move")
	var texts: Array=[]
	for button: Node in ui.find_children("*","Button",true,false):texts.append(button.text)
	check(not texts.has(ui.action_name("attack")) and not texts.has(ui.action_name("pickup")),"untaught action buttons hidden")
	var initial: String=ui.session.store.canonical(ui.session.state)
	for button: Node in ui.root.find_children("*","Button",true,false):
		if button.text==ui.action_name("move"):button.pressed.emit();break
	ui.click_cell([3,6]);check(ui.inline_pending,"move button then map click produces visible preview");check(ui.FirstShift.lesson(ui).id=="move","preview is not lesson completion");ui.cancel_selection()
	check(ui.session.store.canonical(ui.session.state)==initial,"preview cancellation no mutation")
	check(act("move",{"cell":[3,6]}),"first move")
	check(ui.FirstShift.lesson(ui).id=="forecast","movement opens danger lesson")
	check(act("undo"),"can undo first move")
	check(ui.FirstShift.lesson(ui).id=="move","undo restores corresponding lesson")
	await play_mission(true)
	if ui.session.state.campaign.phase!="settlement":
		print(JSON.stringify({"failures":failures,"last":log.slice(-4),"heroes":ui.session.state.battle.heroes,"next":ui.current_guidance()}));quit(1);return
	check(ui.session.state.battle.objects.r1.delivered and ui.session.state.battle.objects.r2.delivered,"two actual rescues")
	await shot("settlement")
	var result_state: String=ui.session.store.canonical(ui.session.state)
	ui.FirstShift.report(ui,true);await process_frame
	check(ui.session.store.canonical(ui.session.state)==result_state and ui.FirstShift.enabled(ui),"reading full settlement leaves first-night teaching enabled")
	close_windows();await process_frame
	check(act("enter_camp"),"first camp")
	checkpoint("day01-camp")
	await shot("camp")
	await layout_review("camp")
	ui.FirstShift.night_record(ui);await shot("night-record");close_windows();await process_frame
	ui.FirstShift.project(ui,"lin");await shot("project");close_windows();await process_frame
	var before: String=ui.session.store.canonical(ui.session.state)
	ui.propose("train",{});ui.confirmation.hide();ui.cancel_selection();check(ui.session.store.canonical(ui.session.state)==before,"training remains a preview")
	ui.selected="lin";check(act("train"),"actual first-night training")
	check(ui.session.load_game().ok and ui.session.state.tutorial.first_shift.actions.has("extract"),"lesson progress round trips")
	check(act("finish_evening"),"first night ends")
	check(ui.session.state.campaign.day==2,"next day")
	check(act("depart",ui.session.state.journey.draft.duplicate(true)),"second departure")
	check(not ui.FirstShift.active(ui),"M02 normal workspace restored")
	await play_mission(false)
	if ui.session.state.campaign.phase!="settlement":
		print(JSON.stringify({"failures":failures,"last":log.slice(-4),"heroes":ui.session.state.battle.heroes,"next":ui.current_guidance()}));quit(1);return
	check(act("enter_camp"),"second camp for key story")
	check(act("story_open",{"node":"P_lin_1"}),"key story opens by production conditions")
	ui.show_story("P_lin_1");await shot("key-story");close_windows();await process_frame
	preload("res://scripts/presentation/story_screen.gd").show(ui,"P_lin_1",2)
	await shot("key-choice")
	var choose_private: Button
	for window: Node in ui.get_children():
		if window is Window and window.visible and window!=ui.confirmation:
			for button: Node in window.find_children("*","Button",true,false):
				if button.text in ["先让她决定交班单向谁公开","征得同意后安排双方核对"]:check(button.get_global_rect().end.y<=window.size.y-20,"key choice visible without scrolling "+button.text)
				if button.text=="先让她决定交班单向谁公开":choose_private=button
	check(is_instance_valid(choose_private),"authored choice has an actual button")
	if not is_instance_valid(choose_private):quit(1);return
	var before_choice: String=ui.session.store.canonical(ui.session.state)
	choose_private.pressed.emit();ui.confirmation.hide()
	check(ui.session.store.canonical(ui.session.state)==before_choice,"story button opens preview before committing choice")
	ui.commit_pending();await shot("key-reply");close_windows()
	check(ui.session.state.chapter_one.scenes.P_lin_1.choice=="private","visible choice button commits correct branch")
	log.append({"kind":"story_choice","actor":ui.selected,"payload":{"node":"P_lin_1","choice":"private"},"day":ui.session.state.campaign.day,"round":ui.session.state.battle.round,"revision":ui.session.state.revision,"message":ui.message})
	checkpoint("day02-story")
	var out:=FileAccess.open("res://../outputs/firstshift-review"+("-gpu" if DisplayServer.get_name()!="headless" else "")+".json",FileAccess.WRITE);out.store_string(JSON.stringify({"checks":checks,"failures":failures,"commands":log,"scope":"actual new campaign M01/night1/M02/key-story with production UI/session commands; hidden GPU captures when available; no injected XP/roster","windows_native":false,"renderer":DisplayServer.get_name()},"\t"));out.close()
	print("FIRSTSHIFT_RESULTS: checks=%d failures=%d commands=%d"%[checks,failures.size(),log.size()])
	ui.sound.stop_audio();ui.queue_free();await create_timer(.5).timeout;quit(0 if failures.is_empty() else 1)

func layout_review(phase: String) -> void:
	for font: int in [16,20,24]:
		ui.font_size=font;ui.render()
		for frame: int in range(4):await process_frame
		check(ui.root.size.x<=canvas.size.x and ui.root.size.y<=canvas.size.y,"root fits 720p "+phase+str(font))
		for node: Node in ui.root.find_children("*","Control",true,false):
			if node is Button and node.is_visible_in_tree():check(node.get_global_rect().end.x<=canvas.size.x+1,"button not horizontally clipped "+phase+str(font)+node.text)
		await shot(phase+"-font"+str(font))
	ui.font_size=20;ui.render();await process_frame
func compatibility_and_preferences() -> void:
	var store=ui.session.store;var content: Dictionary=ui.session.content
	for path: String in ["res://../docs/p4-firstshift-20261117/before-save-day06.json","res://../docs/p4-firstshift-20261117/before-save-day18.json"]:
		var old: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
		var loaded: Dictionary=store.validate(old,content)
		check(loaded.ok,"retained pre-tutorial save loads "+path)
		if loaded.ok:check(not loaded.state.tutorial.has("first_shift"),"old progress does not replay new tutorial")
	var current: Dictionary=store.envelope(ui.session.state,content)
	var invalid: Dictionary=current.duplicate(true);invalid.content_sha256="unknown";invalid.erase("checksum");invalid.checksum=store.canonical(invalid).sha256_text()
	check(store.validate(invalid,content).get("error_code")=="content_mismatch","unknown content still rejected")
	invalid=current.duplicate(true);invalid.content_sha256=content.compatible_content_hashes[0]
	check(store.validate(invalid,content).get("error_code")=="corrupt_save","accepted predecessor still requires matching checksum")
	invalid=current.duplicate(true);invalid.state.tutorial.first_shift.forecast="bad";invalid.erase("checksum");invalid.checksum=store.canonical(invalid).sha256_text()
	check(store.validate(invalid,content).get("error_code")=="corrupt_save","malformed teaching state rejected")
	check(ui.session.state.journey.recruited.keys()==["lin","xu","su"],"initial roster only three balanced utility roles")
	for id: String in content.actors:
		var actor: Dictionary=ui.session.state.actors[id]
		var expected: int={"lin":0,"xu":0,"su":0,"chen":0,"ye":12,"he":12,"mo":28,"jiang":28}[id]
		check(int(actor.xp)==expected and ui.Rules.Specialties.level(int(actor.xp))<5,"recruit XP floor never grants top tier "+id)
		if id in ["lin","xu","su"]:continue
		var draft: Dictionary=ui.session.state.journey.draft.duplicate(true);draft.roster=["lin","xu",id]
		check(not ui.Crew.valid_draft(ui.session.state,draft),"cannot field future recruit "+id)
		var camp: Dictionary=ui.session.state.duplicate(true);camp.campaign.phase="camp"
		var denied: Dictionary=ui.Rules.reduce(camp,{"kind":"train","actor_id":id,"payload":{},"expected_revision":camp.revision,"command_id":"early-"+id,"root_decision_id":"early-"+id},content)
		check(not denied.ok,"cannot train a future recruit before joining "+id)
	var trial: Dictionary=ui.session.state.duplicate(true)
	for kind: String in ["depart","move","tutorial_ack","undo"]:
		var payload: Dictionary={"move":{"cell":[3,6]},"tutorial_ack":{"lesson":"skip"}}.get(kind,{})
		var result: Dictionary=ui.Rules.reduce(trial,{"kind":kind,"actor_id":"lin","payload":payload,"expected_revision":trial.revision,"command_id":"skip-"+kind,"root_decision_id":"skip-"+kind},content)
		check(result.ok,"skip/undo isolated preference regression "+kind)
		if not result.ok:return
		trial=result.next_state
	check(not trial.tutorial.first_shift.enabled and trial.tutorial.first_shift.actions.is_empty(),"undo cannot re-enable skipped tutorial")

func checkpoint(id: String) -> void:
	var envelope: Dictionary=ui.session.store.envelope(ui.session.state,ui.session.content)
	check(ui.session.store.validate(envelope,ui.session.content).ok,"actual checkpoint validates "+id)
	var path: String="res://../outputs/firstshift-"+("gpu-" if DisplayServer.get_name()!="headless" else "")+id+".json"
	var file:=FileAccess.open(path,FileAccess.WRITE);file.store_string(ui.session.store.canonical(envelope));file.close()
