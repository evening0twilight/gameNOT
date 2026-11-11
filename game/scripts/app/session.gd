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
	var result: Dictionary = store.load_slot(path,content,backup)
	if result.ok:
		if backup:
			# Archive first, then durably restore; failure leaves the original slot intact.
			if store.fail_writes:return {"ok":false,"error_code":"save_io_failed"}
			var archived: String=path+".damaged-%d-%d" % [Time.get_unix_time_from_system(),Time.get_ticks_usec()]
			var existed: bool=FileAccess.file_exists(path)
			if existed and DirAccess.rename_absolute(path,archived)!=OK:return {"ok":false,"error_code":"save_io_failed"}
			var restored: Dictionary=store.save_slot(path,result.state,content)
			if not restored.ok:
				if existed:DirAccess.rename_absolute(archived,path)
				return restored
		state=result.state
	return result
