extends "res://tests/p4close_offscreen_review.gd"
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1920,1080);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	scene=load("res://scenes/main.tscn").instantiate();canvas.add_child(scene)
	scene.sound.stop_audio()
	var loaded: Dictionary=scene.session.store.load_slot("res://../outputs/p4close-growth-mo-day23.json",scene.session.content)
	if not loaded.ok:printerr("Missing real continuous late-campaign save");quit(1);return
	scene.session.state=loaded.state;scene.title_screen=false
	scene.session.path="user://tests/p4close-performance-%d/save.json"%Time.get_ticks_usec()
	scene.selected="lin";scene.propose("finish_evening",{});scene.confirmation.hide();scene.commit_pending();scene.finish_feedback();close_modals()
	scene.propose("depart",{});scene.confirmation.hide();scene.commit_pending();scene.finish_feedback();close_modals();scene.render();scene.sound.stop_audio()
	for i: int in range(60):await process_frame
	var frames: Array=[];var input_times: Array=[]
	var memory_before: int=OS.get_static_memory_usage()
	var start: int=Time.get_ticks_usec();var previous: int=start
	while Time.get_ticks_usec()-start<30000000:
		await process_frame
		var now: int=Time.get_ticks_usec();frames.append((now-previous)/1000.0);previous=now
	var memory_after: int=OS.get_static_memory_usage()
	frames.sort();var within: int=0
	for ms: float in frames:
		if ms<=16.7:within+=1
	# Actual late-game proposals include production preview/reducer and UI rebuild.
	for i: int in range(12):
		var begin: int=Time.get_ticks_usec()
		scene.propose("end_round",{});scene.confirmation.hide()
		await process_frame
		input_times.append((Time.get_ticks_usec()-begin)/1000.0)
	input_times.sort()
	var report: Dictionary={"host":OS.get_name(),"cpu":OS.get_processor_name(),"gpu":RenderingServer.get_video_adapter_name(),"memory_info":OS.get_memory_info(),"rendered_canvas":[1920,1080],"window":"hidden 1x1 root; GPU SubViewport","mission":scene.session.state.battle.mission_id,"frames":frames.size(),"stable_seconds":30,"stable_p95_frame_ms":frames[int(frames.size()*.95)],"stable_fraction_le_16_7ms":float(within)/frames.size(),"preview_to_next_frame_p95_ms":input_times[int(input_times.size()*.95)],"preview_samples":input_times,"godot_static_memory_before":memory_before,"godot_static_memory_after":memory_after,"windows_native":false,"cold_start_measured":false,"two_hour_memory_measured":false,"scope":"macOS hidden offscreen GPU development measurement; not Windows 8GB, OS resident-memory, native input/display latency, human experience, or release acceptance"}
	var file:=FileAccess.open("res://../outputs/p4close-performance.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("P4CLOSE_PERFORMANCE: ",JSON.stringify(report))
	scene.sound.stop_audio();quit()
