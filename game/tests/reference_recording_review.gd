extends "res://tests/release_visible_campaign.gd"
## Synthetic input to real controls on a hidden GPU viewport, solely to test the recorder.
func run() -> void:
	canvas = SubViewport.new()
	canvas.size = Vector2i(1280,720)
	canvas.gui_embed_subwindows = true
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	ui = load("res://scenes/main.tscn").instantiate()
	canvas.add_child(ui)
	await settle()
	RenderingServer.force_draw(false)
	var recorder: Node = ui.reference_recording
	if not is_instance_valid(recorder) or not recorder.first_drawn:
		printerr("REFERENCE_FAIL: title marker")
		quit(1)
		return
	ui.I18n.locale = "zh_CN"
	ui.session.start(ui.session.content, "user://tests/recorder-%d/save.json" % Time.get_ticks_usec(),"recorder")
	ui.enter_loaded_campaign(true)
	await settle()
	var launch: bool = await press("开始救援 · 边做边学")
	RenderingServer.force_draw(false)
	var confirmed: bool = await hit(ui.confirmation.get_ok_button(),"confirm")
	RenderingServer.force_draw(false)
	recorder.flush()
	var csv := FileAccess.get_file_as_string(recorder.output.path_join("input-feedback.csv"))
	var valid: bool = (launch and confirmed and ui.session.state.campaign.phase == "battle"
		and csv.contains("depart,preview") and csv.contains("depart,commit")
		and recorder.stable_frames == 0)
	print("REFERENCE_RECORDER_PIPELINE passed=",valid," simulated_mouse_events=",recorder.inputs_seen,
		" hidden_720p_stable_samples=",recorder.stable_frames)
	ui.sound.stop_audio()
	await create_timer(.6).timeout
	ui.queue_free()
	await settle()
	quit(0 if valid else 1)
