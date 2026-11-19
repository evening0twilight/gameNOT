extends SceneTree
## Records only Godot's master mix via the dummy driver, with scripted inputs.
## Arguments: output JSON path, optional WAV path, optionally --packaged.
const Audio := preload("res://scripts/presentation/audio_controller.gd")
const RETIRED_BY_DIRECTORY := {
	"res://assets/audio018/": ["title", "briefing", "camp", "battle", "story", "ending"],
	"res://assets/product018/audio/": ["daily", "grave", "battle_high"],
	Audio.AUDIO_ROOT: ["battle", "battle_high", "daily", "grave"],
}
const CUES := {
	"camp": "ui_confirm", "battle": "move", "battle_high": "injury",
	"daily": "ui_page", "grave": "ui_cancel", "ending": "ending",
}

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var args := Array(OS.get_cmdline_user_args())
	var packaged := args.has("--packaged")
	args.erase("--packaged")
	if args.is_empty():
		quit(2)
		return
	var sound := Audio.new()
	sound.preferences_path = "user://tests/score-review-%s.cfg" % Time.get_ticks_usec()
	root.add_child(sound)
	sound.output_enabled = true
	var capture := AudioEffectCapture.new()
	capture.buffer_length = 8.0
	AudioServer.add_bus_effect(0, capture)
	var result := {"source": "Godot dummy driver master bus; scripted isolated scene transitions",
		"engine": Engine.get_version_info().string, "tracks": [], "mix_rate": AudioServer.get_mix_rate(),
		"human_listening": false, "windows_native": false}
	var recording := PackedByteArray()
	var ok := true
	result.packaged = packaged
	result.retired_music_present = []
	for directory: String in RETIRED_BY_DIRECTORY:
		for name: String in RETIRED_BY_DIRECTORY[directory]:
			var path: String = directory + name + ".wav"
			if ResourceLoader.exists(path):
				result.retired_music_present.append(path)
	ok = result.retired_music_present.size() == (0 if packaged else 13)
	result.short_cues_present = []
	for cue: String in Audio.UI_CUES + Audio.FIELD_FOLEY + Audio.NEW_CUES + Audio.OTHER_CUES:
		var path := Audio.cue_path(cue)
		var effect := load(path) as AudioStreamWAV
		if effect != null and effect.loop_mode == AudioStreamWAV.LOOP_DISABLED:
			result.short_cues_present.append(cue)
	ok = ok and result.short_cues_present.size() == 24
	for id: String in CUES:
		sound.ambience(id)
		var stream := sound.music.stream as AudioStreamWAV
		var start: float = float(stream.loop_begin) / stream.mix_rate
		var finish: float = float(stream.loop_end) / stream.mix_rate
		await create_timer(1.4).timeout
		sound.music.seek(finish - 1.1)
		await create_timer(.8).timeout
		sound.play(CUES[id], id.begins_with("battle"))
		await create_timer(1.7).timeout
		var at := sound.music.get_playback_position()
		var buffer := capture.get_buffer(capture.get_frames_available())
		var peak := 0.0
		var energy := 0.0
		for frame: Vector2 in buffer:
			peak = maxf(peak, maxf(absf(frame.x), absf(frame.y)))
			energy += frame.length_squared()
		var wrapped := at >= start and at < start + 3 and sound.music.playing
		ok = ok and wrapped and peak > .002 and peak < 1 and capture.get_discarded_frames() == 0
		result.tracks.append({"id":id,"path": Audio.MUSIC[id], "source_frames":roundi(stream.get_length()*stream.mix_rate),
			"loop_begin":stream.loop_begin,"loop_end":stream.loop_end,"sample_rate":stream.mix_rate,
			"position_after_wrap":at,"wrap_ok":wrapped,"cue":CUES[id],"capture_frames":buffer.size(),
			"rms":sqrt(energy/maxf(1,buffer.size()*2)), "peak":peak})
		if args.size() > 1:
			var pcm := PackedByteArray()
			pcm.resize(buffer.size() * 4)
			for i: int in buffer.size():
				pcm.encode_s16(4*i, roundi(clampf(buffer[i].x,-1,1)*32767))
				pcm.encode_s16(4*i+2, roundi(clampf(buffer[i].y,-1,1)*32767))
			recording.append_array(pcm)
	result.discarded_frames = capture.get_discarded_frames()
	if args.size() > 1:
		var wav := AudioStreamWAV.new()
		wav.mix_rate = roundi(AudioServer.get_mix_rate())
		wav.format = AudioStreamWAV.FORMAT_16_BITS
		wav.stereo = true
		wav.data = recording
		ok = (wav.save_to_wav(args[1]) == OK) and ok
	result.passed = ok
	var file := FileAccess.open(args[0], FileAccess.WRITE)
	if file == null:
		quit(1)
		return
	file.store_string(JSON.stringify(result, "  ") + "\n")
	file.close()
	AudioServer.remove_bus_effect(0, AudioServer.get_bus_effect_count(0)-1)
	sound.stop_audio()
	# The dummy mixer retires its final stream on its own audio clock.
	await create_timer(.6).timeout
	sound.queue_free()
	await create_timer(.2).timeout
	print("RELEASE_SCORE_REVIEW ", ok)
	quit(0 if ok else 1)
