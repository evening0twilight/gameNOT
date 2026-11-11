extends RefCounted
## Loads the frozen authority, never the separately exported projections.
## Returned dictionaries are owned by the caller; failures contain no partial catalog.
static func load_catalog() -> Dictionary:
	var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/final_design/design_manifest.json"))
	if not manifest is Dictionary or manifest.get("authority") != "release_baseline.json":
		return failure("invalid_manifest")
	var raw := FileAccess.get_file_as_string("res://data/final_design/release_baseline.json")
	var baseline: Variant = JSON.parse_string(raw)
	var result := validate(baseline)
	if result.ok:
		if baseline.version != manifest.get("version"):
			return failure("content_mismatch")
		result.content_sha256 = raw.sha256_text()
	return result

static func failure(code: String) -> Dictionary:
	return {"ok": false, "error_code": code}

static func cell_valid(cell: Variant) -> bool:
	if not cell is Array or cell.size() != 2:
		return false
	for coordinate: Variant in cell:
		if not (coordinate is int or coordinate is float):
			return false
		if not is_finite(float(coordinate)) or coordinate != int(coordinate) or coordinate < 0 or coordinate > 7:
			return false
	return true

static func validate(baseline: Variant) -> Dictionary:
	if not baseline is Dictionary or not baseline.get("version") is String or not baseline.get("domains") is Dictionary:
		return failure("invalid_content")
	var domains: Dictionary = baseline.domains
	if not domains.get("characters") is Array or not domains.get("boards") is Dictionary or not domains.boards.get("boards") is Array:
		return failure("invalid_content")
	var actors: Dictionary = {}
	for actor: Variant in domains.characters:
		if not actor is Dictionary or not actor.get("id") is String or actor.id.is_empty() or actors.has(actor.id):
			return failure("invalid_actor_id")
		actors[actor.id] = actor.duplicate(true)
	var boards: Dictionary = {}
	for board: Variant in domains.boards.boards:
		if not board is Dictionary or not board.get("id") is String or board.id.is_empty() or boards.has(board.id):
			return failure("invalid_board_id")
		if not board.get("rows") is Array or board.rows.size() != 8:
			return failure("invalid_board_rows")
		for row: Variant in board.rows:
			if not row is String or row.length() != 8:
				return failure("invalid_board_rows")
		for field: String in ["spawns", "exits"]:
			if not board.get(field) is Array or board[field].is_empty():
				return failure("invalid_board_cells")
			for cell: Variant in board[field]:
				if not cell_valid(cell):
					return failure("invalid_board_cells")
		if board.spawns.size() != 3:
			return failure("invalid_spawn_count")
		var objects: Dictionary = {}
		for field: String in ["objectives", "controls", "enemies"]:
			if not board.get(field) is Array:
				return failure("invalid_board_objects")
			for object: Variant in board[field]:
				if not object is Dictionary or not object.get("id") is String or objects.has(object.id) or not cell_valid(object.get("cell")):
					return failure("invalid_board_object")
				objects[object.id] = object
		for object: Dictionary in board.objectives + board.controls:
			if not object.get("prerequisites") is Array:
				return failure("invalid_prerequisites")
			for prerequisite: Variant in object.prerequisites:
				if not prerequisite is String or not objects.has(prerequisite) or prerequisite == object.id:
					return failure("invalid_prerequisites")
		boards[board.id] = board.duplicate(true)
	if not boards.has("M01") or not boards.has("M02"):
		return failure("missing_p1_missions")
	var alignment_error: String=preload("res://scripts/infrastructure/baseline_catalog_validation.gd").validate(domains,actors,boards)
	if not alignment_error.is_empty():return failure(alignment_error)
	return {"ok": true, "error_code": "", "version": baseline.version, "boards": boards, "actors": actors, "domains": domains.duplicate(true)}
