extends "res://tests/firstshift_review.gd"
## Production screens. External saves used below are deserialized continuous campaigns.
var frames: Array[String]=[]
var inputs: Dictionary={}

func shot(id: String) -> void:
	for pass_index: int in range(4):await process_frame
	if DisplayServer.get_name()=="headless":return
	RenderingServer.force_draw(false)
	var bitmap: Image=canvas.get_texture().get_image()
	var dest: String="res://../outputs/p4release-20261119-"+id+".png"
	check(not bitmap.is_empty() and bitmap.get_size()==canvas.size and bitmap.save_png(dest)==OK,"GPU capture "+id)
	frames.append(id)

func load_campaign(file: String) -> bool:
	var path: String="res://../"+file if file.begins_with("tmp/") else "res://../outputs/"+file
	var data: Dictionary=ui.session.store.load_slot(path,ui.session.content)
	check(data.ok,"continuous campaign loaded "+file)
	if data.ok:
		inputs[file]=FileAccess.get_sha256(path)
		ui.session.state=data.state;ui.enter_loaded_campaign()
	return data.ok

func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true
	canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui)
	ui.I18n.locale="zh_CN";ui.font_size=20;ui.message="";ui.reduced_motion=true
	ui.render();await shot("title")
	var slot: String="user://tests/release-view-%d/autosave.json"%Time.get_ticks_usec()
	check(ui.session.start(ui.session.content,slot,"release-view").ok,"start isolated slot")
	ui.title_screen=false;ui.render();await shot("briefing")
	check(act("depart",ui.session.state.journey.draft.duplicate(true)),"depart normally")
	ui.action="move";ui.render();await shot("first-board")
	var map: Control=ui.root.find_child("TacticalMap",true,false)
	check(map.geometry().size.x>=450,"720p board size")
	check(map.hover_description([2,1]).contains("无法通行"),"wall inspection")
	check(map.hover_description(ui.session.state.battle.exits[0]).contains("可交付"),"exit inspection")
	ui.click_cell([3,6]);await shot("first-preview")
	map=ui.root.find_child("TacticalMap",true,false)
	check(ui.inline_pending and ui.Rules.same(map.preview_cell,[3,6]) and map.preview_path.size()>1,"clicked route persists until confirmation")
	ui.detailed_preview=true;ui.propose("move",{"cell":[3,6]});ui.detailed_preview=false
	check(ui.confirmation_text.text.contains("(4, 7)"),"expanded destination matches board coordinates")
	ui.confirmation.hide();ui.cancel_selection()
	ui.click_cell([3,6]);ui.return_to_title()
	var key:=InputEventKey.new();key.keycode=KEY_SPACE;key.pressed=true;ui._unhandled_input(key)
	check(ui.pending.is_empty() and not ui.confirmation.visible,"title cannot advance a battle")
	ui.continue_campaign()
	check(not ui.title_screen and not ui.inline_pending and ui.action=="move","continue clears previous input")
	ui.return_to_title()
	var broken:=FileAccess.open(slot,FileAccess.WRITE);broken.store_string("broken-test-slot");broken.close()
	ui.continue_campaign()
	check(ui.title_screen and ui.title_load_error=="corrupt_save","invalid save receives recovery menu")
	check(FileAccess.get_file_as_string(slot)=="broken-test-slot","invalid save preserved")
	ui.recover()
	check(not ui.title_screen and ui.session.store.load_slot(slot,ui.session.content).ok,"backup restored through title screen")
	for day: int in [6,12,18,23]:
		ui.font_size=24 if day==12 else 20
		ui.I18n.locale="en" if day==12 else ("zh_TW" if day==18 else "zh_CN")
		if load_campaign("p4release-20261119/camp-day%02d.json"%day):
			ui.render();await shot("camp-%02d"%day)
			var labels: Array=ui.root.find_children("*","Label",true,false)
			check(labels.any(func(item: Label):return item.text==ui.I18n.t("journey.status_camp")),"camp context on resume "+ui.I18n.locale)
	if load_campaign("campguide-day05.json"):
		check(act("finish_evening"),"advance continuous save to day six briefing")
		for locale: String in ["en","zh_CN","zh_TW"]:
			ui.I18n.locale=locale;ui.font_size=24;ui.message=ui.I18n.t("ui.28efa9cc44f6");ui.render();await shot("dispatch-"+locale)
			for b: Node in ui.root.find_children("*","Button",true,false):
				if b.text==ui.I18n.s("出发 · 到现场再学"):
					check(b.get_global_rect().end.y<=canvas.size.y,"dispatch in view "+locale)
	ui.I18n.locale="zh_CN";ui.font_size=20
	for location: String in ui.Art.LOCATIONS:
		if load_campaign("tmp/quality-review/p4release-boards/"+location+".json"):
			var s: Dictionary=ui.session.state
			ui.I18n.locale="zh_CN";ui.font_size=20;ui.render()
			check(ui.session.content.boards[s.battle.mission_id].location==location,"continuous arrival "+location)
			await shot("board-"+location)
	if load_campaign("p4release-20261119/ending-sides.json"):
		for locale: String in ["zh_CN","zh_TW","en"]:
			ui.I18n.locale=locale;ui.font_size=24;ui.render();await shot("ending-"+locale)
			for id: String in ui.session.state.journey.recruited:
				ui.show_person_ending(id)
				for w: Node in ui.get_children():
					if w is Window and w!=ui.confirmation and w.visible:
						check(w.title==ui.actor_name(id),"selected ending matches "+id)
						if DisplayServer.get_name()!="headless" and id=="lin":await shot("ending-lin-"+locale)
				close_windows();await process_frame
	ui.I18n.initialize();ui.sound.stop_audio()
	var recorder:=FileAccess.open("res://../outputs/p4release-20261119-view-"+DisplayServer.get_name()+".json",FileAccess.WRITE)
	recorder.store_string(JSON.stringify({"checks":checks,"failures":failures,"inputs":inputs,"frames":frames,"host":OS.get_name(),"native_windows":false}, "  "));recorder.close()
	ui.queue_free();await process_frame
	print("WORKSPACE_RESULTS: checks=%d failures=%d"%[checks,failures.size()])
	quit(0 if failures.is_empty() else 1)
