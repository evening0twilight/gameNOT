extends "res://tests/multilanguage_review.gd"
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui);ui.reduced_motion=true;ui.title_screen=false
	var scene_count: int=0
	var inputs: Array=["outputs/baseline018-linked-day24.json","outputs/p4art-benefits-growth-mo-day23.json"]
	for source: String in inputs:
		var retained: Variant=JSON.parse_string(FileAccess.get_file_as_string("res://../"+source))
		var loaded: Dictionary=ui.session.store.validate(retained,ui.session.content)
		check(loaded.ok,"retained late campaign validates "+source)
		if not loaded.ok:continue
		for locale: String in ["zh_CN","zh_TW","en"]:
			captured_locale=locale;ui.I18n.locale=locale;ui.session.state=loaded.state.duplicate(true);ui.message="";ui.selected="lin"
			var before: String=ui.session.store.canonical(ui.session.state)
			ui.render();await shot("late-day%d"%ui.session.state.campaign.day)
			ui.show_journal();await shot("late-journal-day%d"%ui.session.state.campaign.day);close_windows();await process_frame
			for id: String in ui.session.state.actors:
				ui.Screens.profile(ui,id);await shot("late-profile-"+id+str(ui.session.state.campaign.day));close_windows();await process_frame
			if ui.session.state.campaign.day==24:
				for id: String in ui.Stories.nodes(ui.session.content):
					var actual: Dictionary=ui.session.state
					ui.session.state=actual.duplicate(true)
					if not ui.session.state.chapter_one.scenes.has(id):ui.session.state.chapter_one.scenes[id]={"seen":true,"choice":"","status":"seen","day":24}
					ui.show_story(id);await shot("isolated-late-story-"+id);close_windows();await process_frame
					ui.session.state=actual;scene_count+=1
			check(before==ui.session.store.canonical(ui.session.state),"render-only late campaign remains unchanged "+locale+source)
	var file:=FileAccess.open("res://../outputs/languages-lategame.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"checks":checks,"failures":failures,"leaks":leaks,"sources":inputs,"scene_openings_rendered":scene_count,"scope":"retained day23/day24 saves for ending/journal/eight profiles; isolated copies inject seen records for all 54 staged story openings per language, without rewards; not a multilingual 24-day playthrough or proof all scenes unlocked","renderer":DisplayServer.get_name()},"\t"));file.close()
	ui.I18n.initialize();ui.sound.stop_audio();ui.queue_free();await process_frame
	print("LANGUAGE_LATE_RESULTS: checks=%d failures=%d untranslated=%d"%[checks,failures.size(),leaks.size()]);quit(0 if failures.is_empty() and leaks.is_empty() else 1)
