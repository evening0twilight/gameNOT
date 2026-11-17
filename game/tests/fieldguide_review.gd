extends "res://tests/firstshift_review.gd"
const Learning=preload("res://scripts/domain/field_learning.gd")
var lessons: Array=[]
var used_lessons: Array=[]
var screenshots: Array=[]
func shot(id: String) -> void:
	if DisplayServer.get_name()=="headless":return
	await process_frame;await process_frame;await RenderingServer.frame_post_draw
	canvas.get_texture().get_image().save_png("res://../outputs/fieldguide-"+id+".png")
	if not screenshots.has(id):screenshots.append(id)
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui);ui.reduced_motion=true
	check(ui.session.start(ui.session.content,"user://tests/fieldguide-%d/save.json"%Time.get_ticks_usec(),"fieldguide-live").ok,"new production campaign")
	ui.title_screen=false;ui.render()
	check(act("depart",ui.session.state.journey.draft.duplicate(true)),"first departure")
	ui.tutorial_ack("forecast")
	await play_mission(false)
	check(act("enter_camp"),"first camp")
	check(act("finish_evening"),"finish first night")
	var draft: Dictionary=ui.session.state.journey.draft.duplicate(true);draft.loadout.su.tool="crowbar"
	check(act("save_preparation",{"draft":draft}),"equip owned crowbar through production draft")
	await shot("m02-briefing")
	var saved_message: String=ui.message
	ui.propose("depart",{"roster":["jiang"]})
	var visible_error: bool=false
	for label: Node in ui.root.find_children("*","Label",true,false):
		if label.text==ui.message and ui.message!=saved_message:visible_error=true
	check(visible_error,"briefing preserves rejected departure reason")
	ui.message=saved_message;ui.render()
	check(not ui.full_preparation,"second preparation is compact")
	ui.full_preparation=true;ui.render();await shot("m02-full-preparation")
	check(ui.FirstShift.enabled(ui),"detailed preparation does not skip teaching")
	ui.full_preparation=false;ui.render()
	for day: int in [2,3,4]:
		check(act("depart",ui.session.state.journey.draft.duplicate(true)),"departure day%d"%day)
		check(ui.FieldGuide.active(ui),"context learning active day%d"%day)
		if day==3:
			for button: Node in ui.root.find_children("*","Button",true,false):
				if button.text=="林岚":button.pressed.emit();break
			check(ui.session.state.battle.equipment.su.tool=="crowbar","owned tool remains equipped for warehouse obstacle")
		if day==2:
			check(ui.FieldGuide.offer(ui).get("topic","")=="interact","M02 introduces one new interaction")
			var labels: Array=[]
			for button: Node in ui.root.find_children("*","Button",true,false):labels.append(button.text)
			check(not labels.has("攻击") and not labels.has("推撞") and not labels.has("掩护作业"),"second mission hides untaught combat/cooperation")
			await layout_review("m02")
			canvas.size=Vector2i(1920,1080);ui.render();await shot("m02-1080p")
			canvas.size=Vector2i(1280,720);ui.render();await process_frame
			var unchanged: String=ui.session.store.canonical(ui.session.state)
			for button: Node in ui.root.find_children("*","Button",true,false):
				if "点击定位" in button.text:button.pressed.emit();break
			check(not ui.focus_cell.is_empty() and unchanged==ui.session.store.canonical(ui.session.state),"objective locator spends no action or teaching state")
			var map: Control=ui.root.find_child("TacticalMap",true,false)
			check(map.hover_description(ui.session.state.battle.heroes.lin.cell).contains("林岚"),"hover names actual crew")
			await shot("m02-locate");ui.focus_cell=[]
			var state: String=ui.session.store.canonical(ui.session.state)
			ui.render();await process_frame
			check(ui.session.store.canonical(ui.session.state)==state,"render offers no mutations")
			var before: Dictionary=ui.session.state.battle.duplicate(true)
			ui.field_ack("interact")
			check(before==ui.session.state.battle,"reading has no battle/undo costs")
			check(ui.FieldGuide.offer(ui).is_empty(),"no next lesson immediately after reading")
			check(ui.session.load_game().ok and Learning.known(ui.session.state).has("interact"),"learning saved and loaded")
			var no: Dictionary=ui.Rules.reduce(ui.session.state,{"command_id":"bad-lesson","root_decision_id":"bad-lesson","expected_revision":ui.session.state.revision,"actor_id":ui.selected,"kind":"field_lesson","payload":{"topic":"ability:jiang_3","manual":true}},ui.session.content)
			check(not no.ok,"cannot learn unrecruited advanced ability")
		await shot("m0%d-entry"%day)
		await field_mission(day)
		check(act("enter_camp"),"camp day%d"%day)
		if day<4:check(act("finish_evening"),"night day%d"%day)
	check(used_lessons.has("tool:crowbar"),"taught tool actually used in continuous campaign")
	check(ui.session.state.journey.recruited.has("chen"),"real M04 recruitment preserved")
	var actual: Dictionary=ui.session.state.duplicate(true)
	var envelope: Dictionary=ui.session.store.envelope(actual,ui.session.content)
	check(ui.session.store.validate(envelope,ui.session.content).ok,"continuous day04 checkpoint validates")
	var save:=FileAccess.open("res://../outputs/fieldguide-"+("gpu-" if DisplayServer.get_name()!="headless" else "")+"day04.json",FileAccess.WRITE);save.store_string(ui.session.store.canonical(envelope));save.close()
	var malformed: Dictionary=envelope.duplicate(true);malformed.state.tutorial.field_lessons.known.append("ability:fake");malformed.erase("checksum");malformed.checksum=ui.session.store.canonical(malformed).sha256_text()
	check(not ui.session.store.validate(malformed,ui.session.content).ok,"corrupt optional lesson metadata rejected")
	await later_fixtures(actual)
	await metadata_regressions(actual)
	safeguard_fixtures()
	ui.session.state=actual
	var out:=FileAccess.open("res://../outputs/fieldguide-review"+("-gpu" if DisplayServer.get_name()!="headless" else "")+".json",FileAccess.WRITE)
	out.store_string(JSON.stringify({"checks":checks,"failures":failures,"commands":log,"lessons":lessons,"used_lessons":used_lessons,"screenshots":screenshots,"scope":"continuous production new campaign M01 to M04; later mission UI fixtures explicitly isolated; no Windows native evidence","renderer":DisplayServer.get_name()},"\t"));out.close()
	print("FIELDGUIDE_RESULTS: checks=%d failures=%d commands=%d"%[checks,failures.size(),log.size()])
	ui.sound.stop_audio();ui.queue_free();await create_timer(.3).timeout;quit(0 if failures.is_empty() else 1)
func field_mission(day: int) -> void:
	var seen: Array=[]
	for turn: int in range(260):
		if ui.session.state.campaign.phase!="battle":break
		var info: Dictionary=ui.FieldGuide.offer(ui)
		if not info.is_empty():
			check(not Learning.known(ui.session.state).has(info.topic),"only unknown feature offered")
			if info.has("payload"):
				check(Learning.legal(ui.session.state,ui.session.content,ui.selected,info.kind,info.payload),"context example is legal "+info.topic)
				var before: String=ui.session.store.canonical(ui.session.state)
				ui.FieldGuide.preview_example(ui,info);check(not ui.pending.is_empty(),"example opens a real pending command "+info.topic);ui.confirmation.hide();ui.cancel_selection()
				check(ui.session.store.canonical(ui.session.state)==before,"cancel lesson example changes nothing")
			if not seen.has(info.topic):
				seen.append(info.topic);await shot("m0%d-lesson-%s"%[day,info.topic.replace(":","-")])
			lessons.append({"day":day,"round":ui.session.state.battle.round,"actor":ui.selected,"topic":info.topic})
			ui.field_ack(info.topic)
			if info.has("payload") and info.topic in ["tool:crowbar","protocol:protected_work"] and not used_lessons.has(info.topic):
				check(act(info.kind,info.payload.duplicate(true)),"execute taught feature "+info.topic);used_lessons.append(info.topic)
			continue
		var next: Dictionary=ui.current_guidance()
		if next.has("actor"):ui.selected=next.actor;ui.action="move";ui.render();continue
		if next.get("action","").is_empty():failures.append("no legal next "+str(next));break
		if not act(next.action,next.get("payload",{}).duplicate(true)):failures.append("rejected "+str(next));break
		await process_frame
	check(ui.session.state.campaign.phase=="settlement","M0%d actual settlement"%day)
func later_fixtures(actual: Dictionary) -> void:
	# UI-only contexts: no claim that these are continuous progression/playthrough.
	for mission: String in ["M08","M12"]:
		var s: Dictionary=ui.Rules.fresh(ui.session.content,"field-ui-fixture")
		s.campaign.mission_id=mission;s.campaign.day=int(mission.substr(1));s.campaign.phase="battle"
		ui.Rules.deploy(s,ui.session.content,mission)
		s.tutorial.first_shift={"enabled":true,"actions":["move","stabilize","pickup","extract","leave_site"],"forecast":true}
		s.tutorial.field_lessons={"known":["move","stabilize","pickup","extract","leave_site","interact"],"quiet":false}
		ui.session.state=s;ui.selected="lin";ui.action="move";ui.message="独立界面复核场景";ui.render();await shot("fixture-"+mission)
		check(ui.FieldGuide.active(ui),"later context teaching "+mission)
		check(ui.FieldGuide.offer(ui).get("topic","")==("objective:convoy" if mission=="M08" else "objective:channel"),"matching later mechanic "+mission)
	ui.session.state=actual

func metadata_regressions(actual: Dictionary) -> void:
	var s: Dictionary=ui.Rules.begin_campaign(ui.session.content,"metadata-regression")
	s.campaign.day=2;ui.Rules.deploy(s,ui.session.content,"M02")
	ui.session.state=s;ui.selected="lin";ui.action="move";ui.render()
	var info: Dictionary=ui.FieldGuide.offer(ui)
	ui.field_ack(info.topic)
	var next: Dictionary=ui.current_guidance()
	check(act(next.action,next.get("payload",{})),"metadata undo setup move")
	check(act("undo"),"undo real move")
	check(Learning.known(ui.session.state).has(info.topic),"undo preserves read lesson")
	ui.tutorial_ack("skip");check(not ui.FieldGuide.active(ui),"explicit skip returns full controls")
	var legacy: Dictionary=ui.Rules.fresh(ui.session.content,"legacy-no-teaching");legacy.campaign.day=2;ui.Rules.deploy(legacy,ui.session.content,"M02")
	check(not Learning.active(legacy),"legacy without first-shift flag remains unchanged")
	ui.session.state=actual

func safeguard_fixtures() -> void:
	# Isolated relationship contexts; these are not acquired relationship milestones.
	var s: Dictionary=ui.Rules.fresh(ui.session.content,"guard-context-fixture")
	s.campaign.day=18;ui.Rules.deploy(s,ui.session.content,"M03")
	s.tutorial.first_shift={"enabled":true,"actions":[],"forecast":true}
	s.tutorial.field_lessons={"known":Learning.BASIC.filter(func(x):return x!="declare_priority"),"quiet":false}
	var hero: Dictionary=s.battle.heroes.su.duplicate(true);hero.id="jiang";hero.carrying="crate"
	s.battle.heroes.erase("su");s.battle.heroes.jiang=hero;s.battle.objects.crate.carrier="jiang"
	s.social["jiang>leader"].band="conditional"
	check(Learning.offer(s,ui.session.content,"jiang").get("topic","")=="declare_priority","tense cargo handoff teaches actual priority safeguard")
	s.tutorial.field_lessons.known=Learning.BASIC.filter(func(x):return x!="authorize")
	s.social["xu>leader"].band="conditional"
	check(Learning.offer(s,ui.session.content,"xu").get("topic","")=="authorize","Xu context teaches authorization")
	s=ui.Rules.fresh(ui.session.content,"third-person-guard-fixture");s.campaign.day=4;ui.Rules.deploy(s,ui.session.content,"M04")
	s.tutorial.first_shift={"enabled":true,"actions":[],"forecast":true}
	s.tutorial.field_lessons={"known":Learning.BASIC.filter(func(x):return x!="prepare_safety"),"quiet":false}
	s.social["lin>leader"].band="conditional";s.battle.heroes.lin.cell=[3,2];s.battle.heroes.su.cell=[4,2]
	var info: Dictionary=Learning.offer(s,ui.session.content,"su")
	check(info.get("topic","")=="prepare_safety" and info.get("payload",{}).get("target","")=="lin","third partner provides the fall-risk safeguard")
