extends "res://tests/firstshift_review.gd"
## Local rendering and command preview time. The OS monitor and physical inputs are outside this probe.
func run() -> void:
	if DisplayServer.get_name()=="headless":quit(2);return
	canvas=SubViewport.new();canvas.size=Vector2i(1920,1080);canvas.gui_embed_subwindows=true
	canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui)
	ui.session.path="user://tests/p4release-perf-%d/save.json"%Time.get_ticks_usec()
	var source: String="res://../outputs/p4release-20261119/camp-day23.json"
	var saved: Dictionary=ui.session.store.load_slot(source,ui.session.content)
	if not saved.ok:quit(1);return
	ui.session.state=saved.state;ui.enter_loaded_campaign();ui.reduced_motion=false
	if not act("finish_evening") or not act("depart",ui.session.state.journey.draft.duplicate(true)):quit(1);return
	ui.render()
	for tick: int in range(45):
		await process_frame;RenderingServer.force_draw(false)
	var durations: Array[float]=[]
	var before: int=Time.get_ticks_usec()
	var last: int=before
	var within: int=0
	while last-before<30000000:
		await process_frame
		RenderingServer.force_draw(false)
		var now: int=Time.get_ticks_usec()
		var ms: float=(now-last)/1000.0
		durations.append(ms)
		if ms<=16.7:within+=1
		last=now
	durations.sort()
	var previews: Array[float]=[]
	for sample: int in range(12):
		var start: int=Time.get_ticks_usec()
		ui.propose("end_round",{})
		await process_frame
		RenderingServer.force_draw(false)
		previews.append((Time.get_ticks_usec()-start)/1000.0)
		ui.confirmation.hide()
		await process_frame
	var ordered: Array=previews.duplicate();ordered.sort()
	var result: Dictionary={"host":OS.get_name(),"cpu":OS.get_processor_name(),"gpu":RenderingServer.get_video_adapter_name(),"viewport":[1920,1080],"mission":ui.session.state.battle.mission_id,"guide":ui.FieldGuide.active(ui),"continuous_input_sha256":FileAccess.get_sha256(source),"stable_seconds":(last-before)/1000000.0,"stable_frames":durations.size(),"stable_p95_ms":durations[ceili(durations.size()*.95)-1],"fraction_under_16_7_ms":within/float(durations.size()),"preview_to_rendered_ms":previews,"preview_to_rendered_p95_ms":ordered[ceili(ordered.size()*.95)-1],"measurement":"Hidden macOS root and forced GPU draw of 1080p SubViewport, synthetic calls to actual final-mission preview. Window/screen latency, cold first launch and Windows memory trend not measured."}
	var f:=FileAccess.open("res://../outputs/p4release-20261119-local-frame.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(result,"  ")+"\n");f.close()
	print("LOCAL_FRAMES: ",JSON.stringify(result))
	ui.queue_free();await process_frame;quit()
