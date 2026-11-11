extends Node
## Local measurements, never a replacement for reference-device or human acceptance.
var started: int=0
var first_frame_ms: int=0
var frames: int=0
var within_167ms: int=0
var sum_ms: float=0
var max_ms: float=0
var last_memory: int=0
var memory: Array=[]
var inputs: Array=[]
func _ready() -> void:
	started=Time.get_ticks_msec();last_memory=started
func _process(delta: float) -> void:
	if DisplayServer.get_name()=="headless":return
	if first_frame_ms==0:first_frame_ms=Time.get_ticks_msec()
	frames+=1;sum_ms+=delta*1000;max_ms=maxf(max_ms,delta*1000)
	if delta<=.0167:within_167ms+=1
	if Time.get_ticks_msec()-last_memory>=60000:
		last_memory=Time.get_ticks_msec()
		memory.append({"elapsed_seconds":(last_memory-started)/1000.0,"godot_static_bytes":OS.get_static_memory_usage()})
func input_finished(start_us: int) -> void:
	if inputs.size()<10000:inputs.append((Time.get_ticks_usec()-start_us)/1000.0)
func report() -> Dictionary:
	var times: Array=inputs.duplicate();times.sort()
	return {"platform":OS.get_name(),"cpu":OS.get_processor_name(),"gpu":RenderingServer.get_video_adapter_name(),"memory_info":OS.get_memory_info(),"renderer":RenderingServer.get_current_rendering_method(),"display_backend":DisplayServer.get_name(),"window_size":str(get_window().size),"engine_to_first_frame_ms":first_frame_ms,"cold_launch_stopwatch":"not_measured","elapsed_seconds":(Time.get_ticks_msec()-started)/1000.0,"frames":frames,"fraction_frames_le_16_7ms":float(within_167ms)/maxi(1,frames),"mean_frame_ms":sum_ms/maxi(1,frames),"max_frame_ms":max_ms,"input_samples":times.size(),"input_submit_to_next_frame_p95_ms":times[mini(times.size()-1,int(times.size()*.95))] if not times.is_empty() else null,"memory_samples":memory,"scope":"This session includes menus and user interactions. Not automatically a stable-board benchmark, cold launch, 2-hour memory test, 8GB reference-machine acceptance or human-playtest result."}
func export_report() -> String:
	var path: String="user://diagnostics/p4-%d.json" % Time.get_unix_time_from_system()
	if DirAccess.make_dir_recursive_absolute(path.get_base_dir())!=OK:return ""
	var file:=FileAccess.open(path,FileAccess.WRITE)
	if file==null:return ""
	file.store_string(JSON.stringify(report(),"  "));file.close()
	return ProjectSettings.globalize_path(path)
