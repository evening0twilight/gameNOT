extends "res://tests/firstshift_review.gd"
var locale_captures: Array=[]
var leaks: Array=[]
var captured_locale: String="zh_CN"
func shot(id: String) -> void:
	for frame: int in range(4):await process_frame
	var chinese:=RegEx.new();chinese.compile("[\\x{4e00}-\\x{9fff}]")
	for node: Node in ui.find_children("*","Control",true,false):
		if not node.is_visible_in_tree():continue
		if node is Label or node is Button:
			var text: String=node.text
			if captured_locale=="en" and chinese.search(text)!=null and not text in ui.I18n.NAMES.values():
				var row: Dictionary={"screen":id,"text":text}
				if not leaks.has(row):leaks.append(row)
	check(ui.root.size.x<=canvas.size.x and ui.root.size.y<=canvas.size.y,"localized root fits "+captured_locale+id)
	if DisplayServer.get_name()=="headless":return
	await RenderingServer.frame_post_draw
	var path: String="outputs/languages-"+captured_locale+"-"+id+".png"
	canvas.get_texture().get_image().save_png("res://../"+path);locale_captures.append(path)
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui);ui.reduced_motion=true
	var preference_path: String="user://ui_preferences.cfg"
	var preference_exists: bool=FileAccess.file_exists(preference_path)
	var preference_bytes: PackedByteArray=FileAccess.get_file_as_bytes(preference_path) if preference_exists else PackedByteArray()
	for locale: String in ["zh_CN","zh_TW","en"]:
		captured_locale=locale;ui.I18n.locale=locale;ui.I18n.missing.clear();ui.message=""
		check(ui.session.start(ui.session.content,"user://tests/languages-%d-%s/save.json"%[Time.get_ticks_usec(),locale],"languages-live").ok,"new localized campaign")
		ui.title_screen=true;ui.render();await shot("title")
		var language_entry: bool=false
		for control: Node in ui.root.find_children("*","Button",true,false):
			if control.text==ui.I18n.t("ui.f5bb41e345b5"):language_entry=true
		check(language_entry,"language accessible before starting a campaign")
		ui.title_screen=false;ui.render();await shot("briefing")
		check(act("depart",ui.session.state.journey.draft.duplicate(true)),"localized departure")
		for font: int in [16,20,24]:ui.font_size=font;ui.render();await shot("move-font%d"%font)
		ui.font_size=20;ui.render();ui.tutorial_ack("forecast")
		await play_mission(false)
		await shot("settlement")
		check(act("enter_camp"),"localized camp")
		await shot("camp")
		for screen: String in ["profile","roster","relationships","workshop","journal","city","help","intro","recruit"]:
			match screen:
				"profile":ui.Screens.profile(ui,"lin")
				"roster":ui.Screens.roster_page(ui)
				"relationships":ui.Screens.relationships(ui)
				"workshop":ui.show_workshop()
				"journal":ui.show_journal()
				"city":ui.Screens.city(ui)
				"help":ui.show_help()
				"intro":ui.show_intro()
				"recruit":ui.Screens.introduction(ui,"lin")
			await shot(screen);close_windows();await process_frame
		check(act("finish_evening"),"localized evening")
		await shot("m02-briefing")
		ui.full_preparation=true;ui.render();await shot("full-preparation");ui.full_preparation=false;ui.render()
		check(act("depart",ui.session.state.journey.draft.duplicate(true)),"localized second departure")
		await shot("m02-entry")
		var before: String=ui.session.store.canonical(ui.session.state)
		var disk_before: PackedByteArray=FileAccess.get_file_as_bytes(ui.session.path)
		for language: String in ui.I18n.LOCALES:
			ui.show_languages();await process_frame
			for window: Node in ui.get_children():
				if not window is Window or not window.visible:continue
				for control: Node in window.find_children("*","Button",true,false):
					if control.text==ui.I18n.NAMES[language] and not control.disabled:control.pressed.emit();break
			close_windows();await process_frame
			check(ui.I18n.locale==language,"native language picker switches to "+language)
			ui.I18n.initialize();check(ui.I18n.locale==language,"language persists independently of campaign")
		check(disk_before==FileAccess.get_file_as_bytes(ui.session.path),"language picker preserves disk save bytes")
		check(before==ui.session.store.canonical(ui.session.state),"language toggles preserve all campaign bytes")
		ui.I18n.locale=locale;ui.field_offer_key=0;ui.render()
		await play_mission(false)
		check(act("enter_camp"),"second camp")
		check(act("story_open",{"node":"P_lin_1"}),"actual story opens")
		ui.show_story("P_lin_1");await shot("story");close_windows();await process_frame
		for font: int in [16,20,24]:
			ui.font_size=font;preload("res://scripts/presentation/story_screen.gd").show(ui,"P_lin_1",2);await shot("choice-font%d"%font)
			for window: Node in ui.get_children():
				if not window is Window or not window.visible:continue
				for control: Node in window.find_children("*","Button",true,false):
					if DisplayServer.get_name()!="headless":check(control.get_global_rect().end.y<=window.size.y-16,"story controls visible "+locale+str(font)+control.text)
			close_windows();await process_frame
		ui.font_size=20
		check(act("story_choice",{"node":"P_lin_1","choice":"private"}),"localized story retains choice ID")
		check(ui.session.state.chapter_one.scenes.P_lin_1.choice=="private","story branch unchanged by localization")
	var report: Dictionary={"checks":checks,"failures":failures,"leaks":leaks,"captures":locale_captures,"commands":log,"renderer":DisplayServer.get_name(),"story_geometry_gpu_only":true,"scope":"production M01/M02/first-camp/story for each language; UI-only language toggle no save mutation"}
	var file:=FileAccess.open("res://../outputs/languages-review"+("-gpu" if DisplayServer.get_name()!="headless" else "")+".json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	if preference_exists:
		var preference_file:=FileAccess.open(preference_path,FileAccess.WRITE);preference_file.store_buffer(preference_bytes);preference_file.close()
	else:DirAccess.remove_absolute(preference_path)
	ui.I18n.initialize();ui.sound.stop_audio();ui.queue_free();await process_frame
	print("LANGUAGE_RESULTS: checks=%d failures=%d untranslated=%d"%[checks,failures.size(),leaks.size()]);quit(0 if failures.is_empty() and leaks.is_empty() else 1)
