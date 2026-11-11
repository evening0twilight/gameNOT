extends Node
var music_volume: float=.35
var effects_volume: float=.6
var muted: bool=false
var fading_music: AudioStreamPlayer
var music_tween: Tween
var music: AudioStreamPlayer
var cue: AudioStreamPlayer
var phase: String=""
var voices: Array[AudioStreamPlayer]=[]
var timeline: Array=[]
var timeline_started: int=0
var played_events: Array=[]
var playback_seconds: Callable
func schedule(events: Array,started: int,clock: Callable=Callable()) -> void:
	timeline=events.duplicate(true);timeline_started=started;played_events=[];playback_seconds=clock
func _process(_delta: float) -> void:
	var seconds: float=playback_seconds.call() if playback_seconds.is_valid() else float(Time.get_ticks_msec()-timeline_started)/1000.0
	while not timeline.is_empty() and float(timeline[0].at)<=seconds:
		var event: Dictionary=timeline.pop_front();played_events.append(event);play(event.sound)
func cancel_timeline() -> void:timeline=[];playback_seconds=Callable()

func _ready() -> void:
	for bus: String in ["Music","Effects"]:
		if AudioServer.get_bus_index(bus)<0:
			AudioServer.add_bus();AudioServer.set_bus_name(AudioServer.bus_count-1,bus)
	music=AudioStreamPlayer.new();music.bus="Music";add_child(music)
	fading_music=AudioStreamPlayer.new();fading_music.bus="Music";add_child(fading_music)
	for index: int in range(8):
		var voice:=AudioStreamPlayer.new();voice.bus="Effects";add_child(voice);voices.append(voice)
	cue=voices[0]
	var config:=ConfigFile.new()
	if config.load("user://p4_audio.cfg")==OK:
		music_volume=clampf(float(config.get_value("audio","music",.35)),0,1)
		effects_volume=clampf(float(config.get_value("audio","effects",.6)),0,1)
		muted=bool(config.get_value("audio","mute",false))
	apply_levels()
func apply_levels() -> void:
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"),linear_to_db(maxf(.0001,music_volume)))
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Effects"),linear_to_db(maxf(.0001,effects_volume)))
	AudioServer.set_bus_mute(AudioServer.get_bus_index("Music"),muted or music_volume==0)
	AudioServer.set_bus_mute(AudioServer.get_bus_index("Effects"),muted or effects_volume==0)
func save_preferences() -> void:
	apply_levels()
	var config:=ConfigFile.new();config.set_value("audio","music",music_volume);config.set_value("audio","effects",effects_volume);config.set_value("audio","mute",muted);config.save("user://p4_audio.cfg")
func ambience(current: String) -> void:
	var next: String={"title":"camp","briefing":"camp","story":"daily"}.get(current,current) if current in ["title","briefing","story","ending","daily","grave","battle_high","battle","camp"] else "camp"
	if phase==next:return
	phase=next
	if DisplayServer.get_name()=="headless":return
	var path: String=("res://assets/product018/audio/%s.wav" if next in ["daily","grave","battle_high"] else "res://assets/audio018/%s.wav")%next
	if not ResourceLoader.exists(path):return
	if music_tween and music_tween.is_valid():music_tween.kill()
	fading_music.stop()
	var old: AudioStreamPlayer=music;music=fading_music;fading_music=old
	var stream: AudioStreamWAV=load(path).duplicate()
	stream.loop_mode=AudioStreamWAV.LOOP_FORWARD;stream.loop_begin=0;stream.loop_end=int(stream.get_length()*stream.mix_rate)
	music.stream=stream;music.volume_db=-48;music.play()
	music_tween=create_tween().set_parallel(true)
	music_tween.tween_property(music,"volume_db",0.0,1.2)
	music_tween.tween_property(fading_music,"volume_db",-48.0,1.2)
	music_tween.chain().tween_callback(fading_music.stop)
func play(id: String) -> void:
	if DisplayServer.get_name()=="headless":return
	var path: String="res://assets/audio_p4/%s.wav" % id
	if ResourceLoader.exists("res://assets/audio_feedback/%s.wav" % id):path="res://assets/audio_feedback/%s.wav" % id
	if not ResourceLoader.exists(path):return
	var voice: AudioStreamPlayer=voices[0]
	for available: AudioStreamPlayer in voices:
		if not available.playing:voice=available;break
	voice.stream=load(path);voice.play()
func action(kind: String,before: Dictionary,after: Dictionary) -> void:
	if after.chapter_one.finished and not before.chapter_one.finished:play("ending");return
	if after.campaign.phase=="settlement" and before.campaign.phase=="battle":play("objective");return
	for id: String in after.battle.heroes:
		if after.battle.heroes[id].downed and not before.battle.heroes.get(id,{}).get("downed",false):play("injury");return
	play({"move":"move","attack":"attack","push":"push","stabilize":"stabilize","pickup":"pickup","interact":"work","drop":"drop","extract":"extract","leave_site":"extract","end_round":"end_round"}.get(kind,"ui_confirm"))

func stop_audio() -> void:
	if is_instance_valid(fading_music):fading_music.stop();fading_music.stream=null
	if is_instance_valid(music):music.stop();music.stream=null
	cancel_timeline()
	for voice: AudioStreamPlayer in voices:
		if is_instance_valid(voice):voice.stop();voice.stream=null
func _exit_tree() -> void:stop_audio()
