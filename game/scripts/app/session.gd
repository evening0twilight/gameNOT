extends RefCounted
const Rules = preload("res://scripts/domain/campaign_rules.gd")
const Store = preload("res://scripts/infrastructure/campaign_store.gd")
var content: Dictionary
var state: Dictionary
var store = Store.new()
var path: String
func start(catalog: Dictionary,slot: String,campaign_id: String,options: Dictionary={}) -> Dictionary:
	content=catalog
	path=slot
	var candidate := Rules.begin_campaign(content,campaign_id,options)
	var result: Dictionary = store.save_slot(path,candidate,content)
	if result.ok: state=candidate
	return result
func preview(command: Dictionary) -> Dictionary:
	return Rules.reduce(state,command,content)
func submit(command: Dictionary) -> Dictionary:
	var result := preview(command)
	if not result.ok or result.get("duplicate",false): return result
	var saved: Dictionary = store.save_slot(path,result.next_state,content)
	if not saved.ok: return saved
	state=result.next_state
	return result
func load_game(backup: bool=false) -> Dictionary:
	var result: Dictionary=store.load_slot(path,content,backup)
	if not result.ok:return result
	if backup:return restore_state(result.state,true)
	state=result.state
	return result

func restore_state(candidate: Dictionary,archive_primary: bool=false) -> Dictionary:
	# A damaged primary is retained for recovery. A valid primary follows the
	# usual atomic save path, which preserves its bytes as the preceding backup.
	if store.fail_writes:return {"ok":false,"error_code":"save_io_failed"}
	var archived: String=""
	if FileAccess.file_exists(path) and (archive_primary or not store.known_valid_file(path,content)):
		archived=path+".damaged-%d-%d" % [Time.get_unix_time_from_system(),Time.get_ticks_usec()]
		if DirAccess.rename_absolute(path,archived)!=OK:return {"ok":false,"error_code":"save_io_failed"}
	var result: Dictionary=store.save_slot(path,candidate,content)
	if not result.ok:
		if not archived.is_empty():DirAccess.rename_absolute(archived,path)
		return result
	state=candidate
	return {"ok":true,"state":state,"error_code":""}

## Ordered recovery candidates for an autosave, including manual-slot backups.
static func recovery_files(slot: String) -> Array[String]:
	var paths: Array[String] = [slot + ".bak"]
	var directory := slot.get_base_dir()
	var manuals: Array[String] = ["manual.json"]
	for i in range(1,11):
		manuals.append("manual-%02d.json" % i)
	for name in manuals:
		var manual := directory.path_join(name)
		paths.append(manual)
		paths.append(manual + ".bak")
	var present: Array[String] = []
	for candidate in paths:
		if FileAccess.file_exists(candidate):
			present.append(candidate)
	return present
