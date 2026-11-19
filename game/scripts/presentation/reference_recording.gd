extends Node
## Opt-in recorder for the ordinary game. No network or gameplay commands.

class WindowInputTap extends Node:
	var record: Callable
	func _input(event: InputEvent) -> void:
		record.call(event)

var output: String
var ui: Control
var input_file: FileAccess
var first_drawn := false
var last_draw_us := 0
var previous_context := ""
var context_since_us := 0
var stable_frames := 0
var stable_time_us := 0
var on_budget := 0
var frame_histogram := {}
var input_started_us := 0
var input_frame := -1
var event_kind := ""
var pending_inputs: Array[Dictionary] = []
var inputs_seen := 0
var inputs_late := 0
var worst_input_us := 0
var last_flush_us := 0

func _ready() -> void:
	ui = get_parent()
	output = OS.get_environment("NIGHT_TIDE_REVIEW_DIR")
	if output.is_empty() or not DirAccess.dir_exists_absolute(output):
		queue_free()
		return
	input_file = FileAccess.open(output.path_join("input-feedback.csv"), FileAccess.WRITE)
	if input_file == null:
		push_error("Cannot write the reference input record.")
		queue_free()
		return
	input_file.store_csv_line(["engine_seconds", "input", "command", "stage", "event_to_post_draw_ms"])
	# Focused dialogs process their own _input before GUI callbacks. Include
	# the confirmation and story windows as well as the base viewport.
	for window: Node in ui.find_children("*", "Window", true, false):
		watch_window(window)
	get_tree().node_added.connect(watch_window)
	RenderingServer.frame_post_draw.connect(after_draw)

func watch_window(node: Node) -> void:
	if node is Window and ui.is_ancestor_of(node):
		var tap := WindowInputTap.new()
		tap.record = record_input
		node.add_child.call_deferred(tap)

func _input(event: InputEvent) -> void:
	record_input(event)

func record_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
		event_kind = "mouse"
	elif event is InputEventKey and not event.echo:
		event_kind = "keyboard"
	else:
		return
	input_started_us = Time.get_ticks_usec()
	input_frame = Engine.get_process_frames()

func observe_command(kind: String, phase: String) -> void:
	if input_started_us == 0 or input_frame != Engine.get_process_frames():
		return
	# A second click may propose and immediately commit in one callback.
	if not pending_inputs.is_empty() and pending_inputs.back().start == input_started_us:
		pending_inputs.back().stage = phase
	else:
		pending_inputs.append({"start":input_started_us, "input":event_kind, "kind":kind, "stage":phase})

func stable_context() -> String:
	if ui.title_screen or ui.paused or ui.feedback_active() or ui.inline_pending:
		return ""
	if ui.session.state.campaign.phase != "battle" or not get_window().has_focus():
		return ""
	if get_window().size != Vector2i(1920, 1080):
		return ""
	for child: Node in ui.get_children():
		if child is Window and child.visible:
			return ""
	return "%s:%s:%d" % [ui.session.state.campaign.id, ui.session.state.battle.mission_id, ui.session.state.revision]

func after_draw() -> void:
	if not first_drawn:
		if not ui.title_screen:
			return
		first_drawn = true
		var marker := FileAccess.open(output.path_join("title-presented.txt"), FileAccess.WRITE)
		if marker != null:
			marker.store_line(str(Time.get_ticks_usec()))
			marker.close()
	var now := Time.get_ticks_usec()
	for sample in pending_inputs:
		var latency: int = now - sample.start
		worst_input_us = maxi(worst_input_us, latency)
		inputs_seen += 1
		if latency > 100000:
			inputs_late += 1
		input_file.store_csv_line(["%.3f" % (now/1e6), sample.input, sample.kind, sample.stage, "%.3f" % (latency/1000.0)])
	pending_inputs.clear()
	input_started_us = 0

	var context := stable_context()
	if context != previous_context:
		previous_context = context
		context_since_us = now
	if not context.is_empty() and last_draw_us - context_since_us >= 1000000:
		var elapsed := now - last_draw_us
		var bin_index := ceili(elapsed/100.0)
		frame_histogram[bin_index] = int(frame_histogram.get(bin_index, 0)) + 1
		stable_frames += 1
		stable_time_us += elapsed
		if elapsed <= 16700:
			on_budget += 1
	last_draw_us = now
	if now - last_flush_us >= 15000000:
		last_flush_us = now
		flush()

func _exit_tree() -> void:
	if first_drawn:
		flush()
	input_file = null

func flush() -> void:
	var bins := frame_histogram.keys()
	bins.sort()
	var cumulative := 0
	var p95: Variant = null
	for bin_index: int in bins:
		cumulative += int(frame_histogram[bin_index])
		if cumulative >= ceili(stable_frames * .95):
			p95 = bin_index / 10.0
			break
	var report := {
		"platform":OS.get_name(), "render_device":RenderingServer.get_video_adapter_name(),
		"screen_refresh_hz":DisplayServer.screen_get_refresh_rate(get_window().current_screen),
		"client_pixels":[get_window().size.x, get_window().size.y],
		"stable_1080p_frames":stable_frames, "stable_seconds":stable_time_us / 1e6,
		"stable_frame_p95_ms_upper_bound":p95,
		"stable_fraction_le_16_7_ms":on_budget/float(stable_frames) if stable_frames else null,
		"input_samples":inputs_seen, "input_over_100_ms":inputs_late,
		"input_max_ms":worst_input_us / 1000.0 if inputs_seen else null,
		"scope":"Godot post-draw intervals while focused at 1920x1080, battle revision stable for one second, no preview/animation/modal. Timed commands start at game input receipt and end at post-draw. OS input, compositor, display scanout and screen response require external observation."
	}
	input_file.flush()
	var path := output.path_join("game-metrics.json")
	var file := FileAccess.open(path + ".tmp", FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(report, "  ") + "\n")
		file.close()
		var err := DirAccess.rename_absolute(path + ".tmp", path)
		if err != OK:
			push_error("Could not replace the reference metrics file: " + error_string(err))
