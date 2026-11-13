extends SceneTree
## Production controller on the dummy driver. No screen or speakers.
const Audio := preload("res://scripts/presentation/audio_controller.gd")
const Session := preload("res://scripts/app/session.gd")
const Catalog := preload("res://scripts/infrastructure/content_catalog.gd")
const Plan := preload("res://scripts/presentation/action_feedback.gd")
const Screens := preload("res://scripts/presentation/campaign_screens.gd")
var failures: int = 0
var checks: int = 0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		printerr("AUDIO_FAIL: " + label)

func active(players: Array[AudioStreamPlayer]) -> Array[AudioStreamPlayer]:
	return players.filter(func(player: AudioStreamPlayer): return player.playing)

func press(window: Window, caption: String) -> bool:
	for control: Node in window.find_children("*", "Button", true, false):
		if control.text == caption and not control.disabled:
			control.pressed.emit()
			return true
	return false

func scene_window(ui: Control) -> Window:
	for child: Node in ui.get_children():
		if child is Window and not child is ConfirmationDialog and not child.is_queued_for_deletion():
			return child
	return null

func run() -> void:
	var ui := load("res://scenes/main.tscn").instantiate() as Control
	root.add_child(ui)
	var sound := ui.sound as Audio
	sound.preferences_path = "user://audio-nov13-%d.cfg" % Time.get_ticks_usec()
	sound.stop_audio()
	sound.output_enabled = true
	sound.music_volume = .35
	sound.effects_volume = .60
	sound.muted = false
	sound.apply_levels()
	for phase: String in Audio.MUSIC:
		sound.ambience(phase)
		await create_timer(.04).timeout
		var stream := sound.music.stream as AudioStreamWAV
		check(sound.phase == phase and sound.music.playing, "music route starts " + phase)
		check(stream != null and stream.loop_mode == AudioStreamWAV.LOOP_FORWARD and stream.loop_end > stream.loop_begin and stream.get_length() >= 16, "full imported loop " + phase)
	sound.stop_audio()
	sound.ambience("battle")
	await create_timer(1.25).timeout
	var standard := sound.music
	var loop_length: float = standard.stream.get_length()
	standard.seek(loop_length - .12)
	await create_timer(.30).timeout
	check(standard.playing and standard.get_playback_position() < .7, "actual imported battle player wraps through loop boundary")
	sound.ambience("battle_high")
	await create_timer(.5).timeout
	check(standard.playing and sound.music.playing and standard.volume_linear > .1 and sound.music.volume_linear > .1,
		"both tracks are present through the crossfade")
	sound.ambience("battle")
	check(sound.music == standard and sound.music.get_playback_position() > .3, "reverse transition keeps the old track position")
	await create_timer(1.30).timeout
	check(not sound.fading_music.playing and is_equal_approx(sound.music.volume_linear, 1.0), "crossfade releases outgoing stream")
	var cue_ids: Array = Audio.UI_CUES + Audio.FIELD_FOLEY + Audio.NEW_CUES + Audio.OTHER_CUES
	check(cue_ids.size() == 24, "cue budget")
	for id: String in cue_ids:
		var stream := load(Audio.cue_path(id)) as AudioStreamWAV
		check(stream != null and stream.get_length() > .04 and stream.get_length() <= .8 and stream.loop_mode == AudioStreamWAV.LOOP_DISABLED, "valid short import " + id)
	var m: int = AudioServer.get_bus_index("Music")
	var e: int = AudioServer.get_bus_index("Effects")
	sound.music_volume = 0.0
	sound.effects_volume = .55
	sound.save_preferences()
	check(AudioServer.is_bus_mute(m) and not AudioServer.is_bus_mute(e), "zero music does not silence cues")
	sound.muted = true
	sound.save_preferences()
	check(AudioServer.is_bus_mute(m) and AudioServer.is_bus_mute(e), "master mute")
	var restored := Audio.new()
	restored.preferences_path = sound.preferences_path
	root.add_child(restored)
	check(restored.muted and restored.music_volume == 0 and is_equal_approx(restored.effects_volume, .55), "settings round trip through an isolated config")
	restored.queue_free()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(sound.preferences_path))
	sound.muted = false
	sound.music_volume = .35
	sound.effects_volume = 0.0
	sound.apply_levels()
	check(not AudioServer.is_bus_mute(m) and AudioServer.is_bus_mute(e), "zero effects does not silence music")
	sound.effects_volume = .60
	sound.apply_levels()

	# Launch a real campaign and submit its first moves through the production UI.
	var content: Dictionary = Catalog.load_catalog()
	var slot: String = "user://tests/audio-nov13-%d/autosave.json" % Time.get_ticks_usec()
	ui.session = Session.new()
	check(ui.session.start(content, slot, "audio-nov13").ok, "new production save")
	ui.title_screen = false
	ui.reduced_motion = false
	ui.render()
	check(sound.phase == "camp", "new campaign planning starts in camp")
	ui.propose("depart", {})
	ui.confirmation.hide()
	ui.commit_pending()
	var window := scene_window(ui)
	if window != null:
		window.queue_free()
	ui.confirmation.hide()
	await process_frame
	await process_frame
	check(ui.session.state.campaign.phase == "battle" and sound.phase == "battle", "normal field music on departure")

	ui.propose("move", {"cell": [1, 4]})
	ui.commit_pending()
	check(ui.feedback_active(), "committed move creates tactical audio plan")
	ui.feedback_elapsed = .12
	sound._process(0)
	check(sound.played_events.size() == 1 and sound.played_events[0].sound == "move" and sound.timeline.size() == 2, "one audible step with two still queued")
	await process_frame
	var field: Array[AudioStreamPlayer] = active(sound.action_voices)
	ui.pause_menu()
	sound._process(0)
	check(not field.is_empty() and field[0].has_stream_playback() and field[0].stream_paused, "pause freezes current tactical voice")
	var paused_at: float = field[0].get_playback_position() if not field.is_empty() else -1.0
	await create_timer(.10).timeout
	check(not field.is_empty() and absf(field[0].get_playback_position() - paused_at) < .02 and sound.timeline.size() == 2, "paused waveform and cue timeline both hold")
	sound.play("ui_confirm")
	check(not active(sound.voices).is_empty() and not active(sound.voices)[0].stream_paused and sound.music.playing, "pause menu and score can still play")
	ui.paused = false
	window = scene_window(ui)
	if window != null:
		window.queue_free()
	sound._process(0)
	check(not field.is_empty() and not field[0].stream_paused, "resume continues current tactical voice")
	var before_skip: String = ui.session.store.canonical(ui.session.state)
	ui.finish_feedback()
	check(sound.timeline.is_empty() and not sound.action_voices.any(func(voice: AudioStreamPlayer): return voice.has_stream_playback()), "skip cancels both future and active tactical cues")
	check(ui.session.store.canonical(ui.session.state) == before_skip, "skip does not apply a command")
	await process_frame
	await process_frame

	ui.propose("end_round", {})
	ui.confirmation.hide()
	ui.commit_pending()
	check(ui.feedback_active() and sound.timeline.any(func(event: Dictionary): return event.sound == "machine_scout"), "visible M01 scout action schedules the matching servo")
	ui.feedback_elapsed = float(ui.feedback_plan.duration)
	ui._process(0)
	check(sound.timeline.is_empty() and sound.played_events.any(func(event: Dictionary): return event.sound == "machine_scout"), "natural end dispatches final due cues")

	ui.session.state.battle.round = ui.session.state.battle.limit - 3
	ui.render()
	check(sound.phase == "battle_high", "actual urgent threshold chooses high intensity")
	# Isolated fixture for the modal routing and delayed closing order.
	ui.Rules.settle(ui.session.state, ui.session.content)
	ui.session.state.campaign.phase = "camp"
	ui.session.state.chapter_one.scenes.L01 = {"seen": true, "choice": "", "status": "seen"}
	ui.render()
	ui.show_story("L01")
	window = scene_window(ui)
	check(window != null and sound.phase == "daily", "personal story opens daily music")
	var playing_stream := sound.music.stream
	await create_timer(.06).timeout
	check(window != null and press(window, ui.I18n.t("journey.summary")), "full-text summary button exists")
	await process_frame
	await process_frame
	check(sound.phase == "daily" and sound.music.stream == playing_stream and sound.cue_cache.has("ui_page"), "real summary change keeps the score and plays page cue")
	window = scene_window(ui)
	if window != null:
		window.queue_free()
	await process_frame
	await process_frame
	check(sound.phase == "camp", "leaving the final page restores base music")
	ui.conflict_notices.append({"pair": "lin>xu", "reason": "音频隔离检查"})
	ui.show_conflict_notice()
	window = scene_window(ui)
	check(window != null and sound.phase == "grave", "conflict opens grave music")
	if window != null:
		window.queue_free()
	await process_frame
	await process_frame
	check(sound.phase == "camp", "closing conflict restores camp")
	# Canonical maps in isolated rule runs; use actual reducer outputs, no injected reinforcements.
	var relay: Dictionary = ui.Rules.fresh(content, "audio-relay")
	ui.Rules.deploy(relay, content, "M11")
	var heard_relay: int = 0
	for turn: int in range(1, 5):
		var command := {"kind": "end_round", "actor_id": "lin", "payload": {}, "expected_revision": relay.revision,
			"command_id": "audio-relay-%d" % turn, "root_decision_id": "audio-relay-%d" % turn}
		var result: Dictionary = ui.Rules.reduce(relay, command, content)
		check(result.ok, "M11 round resolves %d" % turn)
		if not result.ok:
			break
		var plan := Plan.build(relay, result.next_state, command, ui.BoardView.route)
		var events: Array = sound.contextual_events(plan, relay, result.next_state)
		var cues: int = events.filter(func(event: Dictionary): return event.sound == "machine_relay").size()
		heard_relay += cues
		if turn <= 1:
			check(cues == 0, "inactive relay is silent")
		relay = result.next_state
	check(heard_relay == 2, "actual relay preview and spawned unit each trigger a cue")
	# The other four machine identities share the production turn timeline.
	for map_and_cue: Array in [["M03", "machine_welder"], ["M05", "machine_skimmer"],
		["M06", "machine_hauler"], ["M10", "machine_sentinel"]]:
		var battle: Dictionary = ui.Rules.fresh(content, "audio-" + map_and_cue[0])
		ui.Rules.deploy(battle, content, map_and_cue[0])
		var heard: bool = false
		for turn: int in range(1, 4):
			var id: String = "audio-%s-%d" % [map_and_cue[0], turn]
			var command := {"kind": "end_round", "actor_id": "lin", "payload": {}, "expected_revision": battle.revision,
				"command_id": id, "root_decision_id": id}
			var result: Dictionary = ui.Rules.reduce(battle, command, content)
			if not result.ok:
				break
			var plan := Plan.build(battle, result.next_state, command, ui.BoardView.route)
			heard = heard or plan.events.any(func(event: Dictionary): return event.sound == map_and_cue[1])
			battle = result.next_state
		check(heard, map_and_cue[0] + " real turn uses " + map_and_cue[1])
	var failed_before: Dictionary = ui.Rules.fresh(content, "audio-failed")
	var failed_after: Dictionary = failed_before.duplicate(true)
	ui.Rules.settle(failed_after, content)
	check(failed_after.campaign.last_result.outcome == "failed", "failed mission comes from the real settlement rules")
	var failed_plan: Dictionary = {"kind": "leave_site", "duration": .85, "events": [{"at": .70, "sound": "objective"}]}
	check(sound.contextual_events(failed_plan, failed_before, failed_after).is_empty(), "failed settlement does not play the success chime")
	var manual: String = slot.get_base_dir().path_join("manual-01.json")
	Screens.write_manual(ui, manual)
	check(FileAccess.file_exists(manual) and sound.cue_cache.has("ui_save"), "successful manual save plays save cue")

	var options := OS.get_cmdline_user_args()
	if not options.is_empty():
		var final_slot: String = options[0]
		var ending: Dictionary = ui.session.store.load_slot(final_slot, content)
		check(ending.ok, "load the retained full campaign ending")
		if ending.ok:
			ui.session.state = ending.state
			ui.render()
			check(sound.phase == "ending", "real day 24 save renders ending music")
	await create_timer(.09).timeout
	sound.stop_audio()
	ui.queue_free()
	# Allow the dummy mixer to release stopped WAV playback before teardown.
	await create_timer(.15).timeout
	print("P4_AUDIO_NOV13: checks=%d failures=%d" % [checks, failures])
	quit(1 if failures else 0)
