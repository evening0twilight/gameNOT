extends "res://tests/release_visible_campaign.gd"
## Three languages and three eligible endings from the same acquired night-23 save.
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true
	canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui)
	var source: String=OUTPUT+"/camp-day23.json"
	var loaded: Dictionary=ui.session.store.load_slot(source,ui.session.content)
	if not loaded.ok:quit(1);return
	ui.session.state=loaded.state
	ui.title_screen=false;ui.reduced_motion=true;ui.font_size=20
	current_day=23;last_phase="camp"
	var actual: String=ui.session.store.canonical(ui.session.state)
	var groups: Dictionary=ui.session.content.boards.M24.route_groups
	for locale: String in ["zh_CN","zh_TW","en"]:
		ui.I18n.locale=locale
		ui.message=ui.I18n.t("journey.status_camp")
		ui.render();await settle()
		ui.CampGuide.open_feature(ui,"route");await settle()
		for route: String in ["shared_control","distributed_rebuild","evacuation"]:
			var title: String=ui.I18n.t("p3.route_"+route)
			if not await press(title):break
			if not ui.confirmation.visible:
				errors.append("No confirmation for "+locale+" "+route);break
			var preview: String=ui.confirmation_text.text
			if not preview.contains(ui.I18n.t("p3.selected_route")%title):errors.append("Missing selected route "+locale+" "+route)
			for group: Array in groups[route]:
				for id: String in group:
					if not preview.contains(ui.I18n.t("content.objects.M24."+id+".label")):errors.append("Missing final objective "+locale+" "+id)
			capture("route-"+locale+"-"+route)
			if not await hit(ui.confirmation.get_cancel_button(),ui.confirmation.cancel_button_text):break
			if not button(title) or ui.session.store.canonical(ui.session.state)!=actual:errors.append("Cancel did not restore the same route choices and state")
			rows.append({"locale":locale,"route":route,"preview":preview})
		var previous: Node=controls()
		if previous is Window:previous.close_requested.emit();await settle()
	var file:=FileAccess.open(OUTPUT+"/route-preview-"+DisplayServer.get_name()+".json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"source":source.get_file(),"sha256":FileAccess.get_sha256(source),"previews":rows,"frames":frames,"failures":errors},"\t"));file.close()
	print("ROUTE_PREVIEW_RESULTS previews=%d failures=%d"%[rows.size(),errors.size()])
	if not errors.is_empty():printerr(errors)
	ui.sound.stop_audio();ui.queue_free();await settle();quit(int(not errors.is_empty()))
