extends Node

const AUDIO_ROOT := "res://assets/product018/audio/nov13/"
const MUSIC := {
	"camp": "res://assets/audio018/camp.wav",
	"battle": AUDIO_ROOT + "battle.wav",
	"battle_high": AUDIO_ROOT + "battle_high.wav",
	"daily": AUDIO_ROOT + "daily.wav",
	"grave": AUDIO_ROOT + "grave.wav",
	"ending": "res://assets/audio018/ending.wav",
}
const UI_CUES := ["ui_focus", "ui_confirm", "ui_cancel", "ui_error", "ui_page", "ui_save"]
const FIELD_FOLEY := ["move", "work", "stabilize", "extract"]
const NEW_CUES := [
	"attack", "push", "pickup", "drop", "injury", "objective",
	"machine_scout", "machine_welder", "machine_hauler",
	"machine_skimmer", "machine_relay", "machine_sentinel",
]
const OTHER_CUES := ["end_round", "ending"]
const ACTION_CUES := {
	"move": "move", "cross_anchor": "move", "attack": "attack", "push": "push",
	"stabilize": "stabilize", "pickup": "pickup", "interact": "work", "drop": "drop",
	"service_watch": "work", "restore_power": "work", "use_tool": "work",
	"specialty": "work", "protocol": "work", "extract": "extract", "leave_site": "extract",
	"end_round": "end_round",
}

var music_volume: float = .35
var effects_volume: float = .6
var muted: bool = false
var preferences_path: String = "user://p4_audio.cfg"
# Tests may enable players on the headless dummy driver.
var output_enabled: bool = DisplayServer.get_name() != "headless"
var music: AudioStreamPlayer
var fading_music: AudioStreamPlayer
var music_tween: Tween
var phase: String = ""
var base_phase: String = "camp"
var scene_phases: Dictionary = {}
var voices: Array[AudioStreamPlayer] = []
var action_voices: Array[AudioStreamPlayer] = []
var cue_cache: Dictionary = {}
var timeline: Array = []
var timeline_started: int = 0
var played_events: Array = []
var playback_seconds: Callable
var playback_paused: Callable

func _ready() -> void:
	for bus: String in ["Music", "Effects"]:
		if AudioServer.get_bus_index(bus) < 0:
			AudioServer.add_bus()
			AudioServer.set_bus_name(AudioServer.bus_count - 1, bus)
	music = _player("Music")
	fading_music = _player("Music")
	for _index: int in range(6):
		voices.append(_player("Effects"))
		action_voices.append(_player("Effects"))
	var config := ConfigFile.new()
	if config.load(preferences_path) == OK:
		music_volume = clampf(float(config.get_value("audio", "music", .35)), 0, 1)
		effects_volume = clampf(float(config.get_value("audio", "effects", .6)), 0, 1)
		muted = bool(config.get_value("audio", "mute", false))
	apply_levels()

func _player(bus: String) -> AudioStreamPlayer:
	var player := AudioStreamPlayer.new()
	player.bus = bus
	add_child(player)
	return player

func apply_levels() -> void:
	for setting: Array in [["Music", music_volume], ["Effects", effects_volume]]:
		var bus: int = AudioServer.get_bus_index(setting[0])
		var volume: float = setting[1]
		AudioServer.set_bus_volume_db(bus, linear_to_db(maxf(.0001, volume)))
		AudioServer.set_bus_mute(bus, muted or volume == 0.0)

func save_preferences() -> void:
	apply_levels()
	var config := ConfigFile.new()
	config.set_value("audio", "music", music_volume)
	config.set_value("audio", "effects", effects_volume)
	config.set_value("audio", "mute", muted)
	config.save(preferences_path)

func ambience(current: String) -> void:
	base_phase = {"title": "camp", "briefing": "camp", "story": "daily"}.get(current, current)
	if not MUSIC.has(base_phase):
		base_phase = "camp"
	_update_music()

## Only the window that owns a scene can dismiss its music. Replacing a page
## with another window for the same cue does not restart the track.
func scene_music(owner: Node, current: String) -> void:
	if not MUSIC.has(current):
		return
	var id: int = owner.get_instance_id()
	if not scene_phases.has(id):
		owner.tree_exiting.connect(_clear_scene_music.bind(id), CONNECT_ONE_SHOT)
	scene_phases[id] = current
	_update_music()

func _clear_scene_music(id: int) -> void:
	if not scene_phases.erase(id):
		return
	if is_inside_tree() and not is_queued_for_deletion():
		_update_music()

func _update_music() -> void:
	var next: String = base_phase if scene_phases.is_empty() else scene_phases.values().back()
	if phase == next:
		return
	if not output_enabled:
		phase = next
		return
	var path: String = MUSIC[next]
	var stream := load(path) as AudioStreamWAV
	if stream == null:
		return
	if music_tween and music_tween.is_valid():
		music_tween.kill()
	if fading_music.playing and fading_music.stream.resource_name == next:
		_swap_music_players()
	else:
		# A third request during a fade keeps the louder player as the outgoing
		# source. Reversing the fade above preserves both tracks' positions.
		if not fading_music.playing or music.volume_linear >= fading_music.volume_linear:
			_swap_music_players()
		music.stop()
		var loop := stream.duplicate() as AudioStreamWAV
		loop.resource_name = next
		if loop.loop_mode == AudioStreamWAV.LOOP_DISABLED:
			loop.loop_begin = 0
			loop.loop_end = roundi(loop.get_length() * loop.mix_rate)
			loop.loop_mode = AudioStreamWAV.LOOP_FORWARD
		music.stream = loop
		music.volume_linear = 0.0
		music.play()
	phase = next
	music_tween = create_tween().set_parallel(true)
	music_tween.tween_property(music, "volume_linear", 1.0, 1.2)
	music_tween.tween_property(fading_music, "volume_linear", 0.0, 1.2)
	music_tween.chain().tween_callback(_release_music.bind(fading_music))

func _swap_music_players() -> void:
	var old: AudioStreamPlayer = music
	music = fading_music
	fading_music = old

func _release_music(player: AudioStreamPlayer) -> void:
	player.stop()
	player.stream = null

static func cue_path(id: String) -> String:
	if id in NEW_CUES:
		return AUDIO_ROOT + id + ".wav"
	if id in FIELD_FOLEY:
		return "res://assets/audio_feedback/%s.wav" % id
	if id in UI_CUES or id in OTHER_CUES:
		return "res://assets/audio_p4/%s.wav" % id
	return ""

func play(id: String, tactical: bool = false) -> void:
	if not output_enabled or muted or effects_volume == 0:
		return
	if not cue_cache.has(id):
		var path := cue_path(id)
		if path.is_empty():
			return
		cue_cache[id] = load(path)
	var pool: Array[AudioStreamPlayer] = action_voices if tactical else voices
	var voice: AudioStreamPlayer = pool[0]
	for available: AudioStreamPlayer in pool:
		if not available.playing:
			voice = available
			break
	voice.stream = cue_cache[id]
	voice.play()

func schedule(events: Array, started: int, clock: Callable = Callable(), is_paused: Callable = Callable()) -> void:
	cancel_timeline()
	timeline = events.duplicate(true)
	timeline_started = started
	played_events.clear()
	playback_seconds = clock
	playback_paused = is_paused

func _process(_delta: float) -> void:
	if timeline.is_empty() and not playback_seconds.is_valid() and not playback_paused.is_valid():
		return
	var paused: bool = playback_paused.is_valid() and playback_paused.call()
	for voice: AudioStreamPlayer in action_voices:
		if voice.stream_paused != paused:
			voice.stream_paused = paused
	if not paused:
		_dispatch_due()

func _dispatch_due() -> void:
	if timeline.is_empty():
		return
	var seconds: float = playback_seconds.call() if playback_seconds.is_valid() else float(Time.get_ticks_msec() - timeline_started) / 1000.0
	while not timeline.is_empty() and float(timeline[0].at) <= seconds:
		var event: Dictionary = timeline.pop_front()
		played_events.append(event)
		play(event.sound, true)

func finish_timeline() -> void:
	for voice: AudioStreamPlayer in action_voices:
		voice.stream_paused = false
	# The parent may finish before this child processes the final frame.
	_dispatch_due()
	timeline.clear()
	playback_seconds = Callable()
	playback_paused = Callable()

func cancel_timeline() -> void:
	timeline.clear()
	playback_seconds = Callable()
	playback_paused = Callable()
	for voice: AudioStreamPlayer in action_voices:
		voice.stop()
		voice.stream_paused = false

static func _outcome_cue(before: Dictionary, after: Dictionary) -> String:
	if after.chapter_one.finished and not before.chapter_one.finished:
		return "ending"
	if before.campaign.phase != "battle" or before.battle.mission_id != after.battle.mission_id:
		return ""
	if after.campaign.phase == "settlement" and after.campaign.get("last_result", {}).get("outcome") == "success":
		return "objective"
	for id: String in after.battle.objects:
		var object: Dictionary = after.battle.objects[id]
		if object.get("lost", false) or (object.get("sustain_until_exit", false) and object.get("hp", 0) <= 0):
			continue
		var prior: Dictionary = before.battle.objects.get(id, {})
		if object.get("completed", false) and not prior.get("completed", false):
			return "objective"
	return ""

static func _relay_activated(before: Dictionary, after: Dictionary) -> bool:
	if before.battle.mission_id != after.battle.mission_id:
		return false
	if int(after.battle.get("spawn_count", 0)) > int(before.battle.get("spawn_count", 0)):
		return true
	for id: String in after.battle.enemies:
		if id.begins_with("reinforcement_") and not before.battle.enemies.has(id):
			return true
	return false

func contextual_events(plan: Dictionary, before: Dictionary, after: Dictionary) -> Array:
	var events: Array = plan.events.filter(func(event: Dictionary): return event.sound not in ["objective", "ending"])
	if plan.kind == "end_round" and _relay_activated(before, after):
		events.append({"at": plan.impact, "sound": "machine_relay"})
	var outcome := _outcome_cue(before, after)
	if not outcome.is_empty():
		events.append({"at": float(plan.duration) - .15, "sound": outcome})
	events.sort_custom(func(a: Dictionary, b: Dictionary): return a.at < b.at)
	return events

func action(kind: String, before: Dictionary, after: Dictionary) -> void:
	var outcome := _outcome_cue(before, after)
	if outcome == "ending":
		play(outcome)
		return
	play(ACTION_CUES.get(kind, "ui_confirm"), before.campaign.phase == "battle")
	if kind == "end_round" and _relay_activated(before, after):
		play("machine_relay", true)
	if before.campaign.phase == "battle" and before.battle.mission_id == after.battle.mission_id:
		for id: String in after.battle.heroes:
			if before.battle.heroes.has(id) and after.battle.heroes[id].hp < before.battle.heroes[id].hp:
				play("injury", true)
				break
	if not outcome.is_empty():
		play(outcome, true)

func stop_audio() -> void:
	if music_tween and music_tween.is_valid():
		music_tween.kill()
	phase = ""
	scene_phases.clear()
	if is_instance_valid(music):
		_release_music(music)
	if is_instance_valid(fading_music):
		_release_music(fading_music)
	cancel_timeline()
	for voice: AudioStreamPlayer in voices + action_voices:
		voice.stop()
		voice.stream = null
	cue_cache.clear()

func _exit_tree() -> void:
	stop_audio()
