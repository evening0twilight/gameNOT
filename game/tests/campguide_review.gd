extends "res://tests/firstshift_review.gd"
const Learning=preload("res://scripts/domain/camp_learning.gd")
var screenshots: Array=[]
var nights: Dictionary={}
func shot(id: String) -> void:
	if DisplayServer.get_name()=="headless":return
	await process_frame;await process_frame
	RenderingServer.force_draw(false)
	canvas.get_texture().get_image().save_png("res://../outputs/campguide-"+id+".png");screenshots.append(id)
func press(text: String) -> bool:
	for button: Node in ui.find_children("*","Button",true,false):
		if button.is_visible_in_tree() and button.text==text and not button.disabled:button.pressed.emit();return true
	return false
func has_button(text: String) -> bool:
	for button: Node in ui.root.find_children("*","Button",true,false):
		if button.text==text and button.is_visible_in_tree():return true
	return false
func read_topic(topic: String) -> void:
	var before: Dictionary=ui.session.state.duplicate(true)
	check(ui.camp_ack(topic),"read camp lesson "+topic)
	var after: Dictionary=ui.session.state
	for key: String in ["actors","inventory","social","journey","campaign","battle","product","full_campaign"]:
		check(before[key]==after[key],"reading preserves "+key)
	check(ui.session.load_game().ok and Learning.known(ui.session.state).has(topic),"lesson survives save/load "+topic)
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui);ui.reduced_motion=true;ui.I18n.locale="zh_CN";ui.guidance_enabled=true
	check(ui.session.start(ui.session.content,"user://tests/campguide-%d/save.json"%Time.get_ticks_usec(),"campguide-live").ok,"new campaign")
	ui.title_screen=false;ui.render();ui.tutorial_ack("forecast")
	for day: int in [1,2,3,4,5]:
		print("CAMP_DAY: ",day)
		check(act("depart",ui.session.state.journey.draft.duplicate(true)),"real departure %d"%day)
		if day==5:check(ui.FieldGuide.active(ui),"completion retains contextual battlefield teaching")
		await play_mission(false)
		check(act("enter_camp"),"real camp %d"%day)
		if day==1:
			check(act("finish_evening"),"first night");continue
		nights[day]=ui.session.state.duplicate(true)
		var topic: String=Learning.offer(ui.session.state,ui.session.content)
		if day<5:
			check(topic==Learning.FOUNDATION[day-2],"one scheduled lesson night%d"%day)
			check(not has_button(ui.I18n.t("p4.equipment_facilities")) and not has_button(ui.I18n.t("quality.camp_more")),"no full workshop/admin pile night%d"%day)
			if day==2:
				ui.show_night_review();await process_frame
				check(press(ui.I18n.s("明白了 · 继续夜间总结")),"night review catches unread lesson")
				check(Learning.known(ui.session.state).has("stories"),"night review records reading without story choice")
				close_windows()
			else:await read_topic(topic)
			check(Learning.offer(ui.session.state,ui.session.content).is_empty(),"no immediate next feature")
			if day==3:
				ui.CampGuide.open_feature(ui,"equipment");await shot("owned-equipment");close_windows()
				ui.selected="su";check(act("equip_tool",{"item":"crowbar","slot":"tool"}),"equip owned tool through real command")
			if day==4:
				check(ui.session.state.journey.recruited.has("chen") and ui.session.state.journey.recruited.size()==4,"real Chen recruitment; no high-tier gifts")
				check(act("plan_next_roster",{"roster":["lin","su","chen"]}),"real next roster")
				ui.show_night_review();await shot("completion-review");close_windows()
				check(not Learning.completed(ui.session.state),"reading/preview does not complete foundation")
			check(act("finish_evening"),"finish night %d"%day)
			if day==4:
				check(Learning.completed(ui.session.state) and ui.session.state.tutorial.camp_lessons.completed_day==4,"completion exactly on fourth night commit")
				check(ui.session.load_game().ok and Learning.completed(ui.session.state),"completion persists")
				await shot("day05-autonomous")
		else:
			check(not topic.is_empty(),"day5 has one contextual camp topic")
			await read_topic(topic)
			check(Learning.offer(ui.session.state,ui.session.content).is_empty(),"day5 reading does not start feature cascade")
	var actual: Dictionary=ui.session.state.duplicate(true)
	var file:=FileAccess.open("res://../outputs/campguide-day05"+("-gpu" if DisplayServer.get_name()!="headless" else "")+".json",FileAccess.WRITE);file.store_string(ui.session.store.canonical(ui.session.store.envelope(actual,ui.session.content)));file.close()
	await layout_nights()
	await later_fixtures(actual)
	metadata_checks(actual)
	ui.session.state=actual;ui.I18n.locale="zh_CN"
	var report:=FileAccess.open("res://../outputs/campguide-review"+("-gpu" if DisplayServer.get_name()!="headless" else "")+".json",FileAccess.WRITE)
	report.store_string(JSON.stringify({"checks":checks,"failures":failures,"commands":log,"screenshots":screenshots,"scope":"continuous new campaign M01-M05; advanced contexts isolated and labelled; no Windows native or human acceptance","renderer":DisplayServer.get_name()},"\t"));report.close()
	print("CAMPGUIDE_RESULTS: checks=%d failures=%d commands=%d"%[checks,failures.size(),log.size()])
	ui.sound.stop_audio();ui.queue_free();await create_timer(.3).timeout;quit(0 if failures.is_empty() else 1)
func layout_nights() -> void:
	for locale: String in ["zh_CN","zh_TW","en"]:
		ui.I18n.locale=locale
		for day: int in [2,3,4,5]:
			for font: int in [16,20,24]:
				ui.session.state=nights[day].duplicate(true);ui.font_size=font;ui.message="";ui.render();await process_frame;await process_frame
				for control: Node in ui.root.find_children("*","Button",true,false):
					if control.is_visible_in_tree():
						check(control.size.x<=1280,"button fits camp width %s/%d/%d"%[locale,day,font])
						if control.text in [ui.I18n.s("了解并打开"),ui.I18n.s("明白了 · 稍后再用")]:check(control.global_position.y+control.size.y<=660,"lesson action above fold %s/%d/%d"%[locale,day,font])
				if locale=="en":
					var regex:=RegEx.new();regex.compile("[一-鿿]")
					for control: Node in ui.root.find_children("*","Label",true,false):
						if control.is_visible_in_tree():check(regex.search(control.text)==null,"English camp no Chinese: "+control.text.left(60))
				await shot("%s-night%02d-font%d"%[locale,day,font])
	ui.I18n.locale="zh_CN";ui.font_size=20
func later_fixtures(actual: Dictionary) -> void:
	# These fixtures test presentation conditions, not a claim of actual late-game growth.
	ui.session.state=actual.duplicate(true)
	var s: Dictionary=ui.session.state
	s.tutorial.camp_lessons.introduced_day=0
	s.campaign.day=23;s.tutorial.camp_lessons.known.erase("route")
	check(Learning.offer(s,ui.session.content)=="route","final route deadline takes priority")
	ui.render();await shot("fixture-final-night");ui.CampGuide.open_feature(ui,"route");await shot("fixture-records");close_windows()
	s.campaign.day=5;s.inventory.supplies=0;s.tutorial.camp_lessons.known.erase("supplies")
	if Learning.urgent(s,ui.session.content).is_empty():check(Learning.offer(s,ui.session.content)=="supplies","low supplies context")
	ui.render();ui.CampGuide.open_feature(ui,"facility:infirmary");await shot("fixture-single-facility");close_windows()
	check(not Learning.available(s,ui.session.content).has("mentors"),"no mentorship lesson without real eligibility")
	s.tutorial.camp_lessons.known.append("mentors")
	ui.CampGuide.open_feature(ui,"mentors");await process_frame
	var explained: bool=false
	for label: Node in ui.find_children("*","Label",true,false):
		if label.is_visible_in_tree() and label.text==ui.I18n.s("今晚暂无可用的带教组合。"):explained=true
	check(explained,"learned mentorship explains later unavailability instead of blank page")
	await shot("fixture-mentor-unavailable");close_windows()
	for id: String in s.operations.facilities:
		var spec: Dictionary=ui.session.content.domains.field_operations.investments[id]
		s.campaign.day=spec.last_day;s.operations.facilities[id].used=0;s.tutorial.camp_lessons.known.erase("operations");s.tutorial.camp_lessons.introduced_day=s.campaign.day
		check(Learning.offer(s,ui.session.content)=="operations","expiring assistance overrides quiet day")
		break
	var mentorship: Dictionary=actual.duplicate(true)
	mentorship.campaign.day=6;mentorship.campaign.projects=0;mentorship.campaign.used=[];mentorship.full_campaign.mentored={}
	mentorship.actors.lin.xp=60;mentorship.actors.chen.xp=12;mentorship.actors.chen.training_completed=0
	for id: String in ["lin","chen"]:mentorship.actors[id].fatigue=0;mentorship.actors[id].ready_day=1
	for pair: String in ["lin>chen","chen>lin"]:
		mentorship.social[pair].agreement="cooperate";mentorship.social[pair].band="open";mentorship.social[pair].contribution_missions=["M02","M04"]
	check(Learning.available(mentorship,ui.session.content).has("mentors"),"isolated eligible mentor is offered; real prerequisites queried")
	ui.session.state=mentorship;ui.render();ui.CampGuide.open_feature(ui,"mentors");await shot("fixture-mentorship");close_windows()
	ui.session.state=actual.duplicate(true);ui.tutorial_ack("skip")
	check(not ui.CampGuide.active(ui),"explicit tutorial skip restores full camp")
func metadata_checks(actual: Dictionary) -> void:
	var envelope: Dictionary=ui.session.store.envelope(actual,ui.session.content)
	check(ui.session.store.validate(envelope,ui.session.content).ok,"continuous save validates")
	for bad: Variant in [{"known":["fake"],"introduced_day":0,"completed_day":0},{"known":[],"introduced_day":0,"completed_day":4},{"known":["stories","stories"],"introduced_day":0,"completed_day":0},{"known":[],"introduced_day":-1,"completed_day":0}]:
		var broken: Dictionary=envelope.duplicate(true);broken.state.tutorial.camp_lessons=bad;broken.erase("checksum");broken.checksum=ui.session.store.canonical(broken).sha256_text()
		check(not ui.session.store.validate(broken,ui.session.content).ok,"malformed optional metadata rejected")
	var legacy: Dictionary=envelope.duplicate(true);legacy.state.tutorial.erase("camp_lessons");legacy.erase("checksum");legacy.checksum=ui.session.store.canonical(legacy).sha256_text()
	check(ui.session.store.validate(legacy,ui.session.content).ok and not Learning.active(legacy.state),"prior tutorial saves retain familiar camp; no forced replay")
