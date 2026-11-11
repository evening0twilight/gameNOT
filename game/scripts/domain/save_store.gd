class_name SaveStore
extends RefCounted
## Preparation-stage save container; complete campaign migrations come later.
const SCHEMA_VERSION: int = 1

static func load_file(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {"ok": false, "error": "missing"}
	var parser := JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path)) != OK:
		return {"ok": false, "error": "invalid_json"}
	if not parser.data is Dictionary:
		return {"ok": false, "error": "invalid_root"}
	var envelope: Dictionary = parser.data
	if int(envelope.get("schema_version", -1)) != SCHEMA_VERSION:
		return {"ok": false, "error": "unsupported_schema"}
	if not envelope.get("state") is Dictionary:
		return {"ok": false, "error": "invalid_state"}
	return {"ok": true, "state": envelope["state"]}

static func save_file(path: String, state: Dictionary) -> Error:
	var temp: String = path + ".tmp"
	var backup: String = path + ".bak"
	var file := FileAccess.open(temp, FileAccess.WRITE)
	if file == null:
		return FileAccess.get_open_error()
	file.store_string(JSON.stringify({"schema_version": SCHEMA_VERSION, "state": state}))
	file.flush()
	var write_error: Error = file.get_error()
	file.close()
	if write_error != OK or not load_file(temp).get("ok", false):
		return ERR_CANT_CREATE
	var had_valid: bool = FileAccess.file_exists(path) and load_file(path).get("ok", false)
	if had_valid:
		if FileAccess.file_exists(backup):
			var remove_error: Error = DirAccess.remove_absolute(backup)
			if remove_error != OK:
				return remove_error
		var backup_error: Error = DirAccess.rename_absolute(path, backup)
		if backup_error != OK:
			return backup_error
	elif FileAccess.file_exists(path):
		# Preserve a corrupt original rather than overwriting the valid backup.
		return ERR_FILE_CORRUPT
	var result: Error = DirAccess.rename_absolute(temp, path)
	if result != OK and had_valid:
		DirAccess.rename_absolute(backup, path)
	return result

