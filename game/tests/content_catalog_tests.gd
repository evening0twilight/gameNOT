extends SceneTree
const Catalog = preload("res://scripts/infrastructure/content_catalog.gd")
var failures: int = 0
func check(condition: bool, label: String) -> void:
	if not condition:
		failures += 1
		push_error(label)
func _initialize() -> void:
	var result := Catalog.load_catalog()
	check(result.ok, "frozen authority loads")
	if result.ok:
		check(result.boards.M01.spawns.size() == 3 and int(result.boards.M01.spawns[0][0]) == 1 and int(result.boards.M01.spawns[2][1]) == 7, "M01 actual deployment")
		check(result.boards.M02.objectives[1].prerequisites == ["cut"], "M02 power dependency")
		check(result.actors.has("lin") and result.actors.has("xu") and result.actors.has("su"), "opening cast")
	var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/final_design/release_baseline.json"))
	var bad := source.duplicate(true)
	bad.domains.boards.boards[0].rows[0] = "short"
	check(not Catalog.validate(bad).ok, "reject malformed grid")
	bad = source.duplicate(true)
	bad.domains.characters.append(bad.domains.characters[0])
	check(not Catalog.validate(bad).ok, "reject duplicate actor")
	bad = source.duplicate(true)
	bad.domains.boards.boards[0].objectives[0].prerequisites = ["missing"]
	check(not Catalog.validate(bad).ok, "reject broken dependency")
	check(not Catalog.cell_valid([1.5, 2]), "reject fractional cell")
	check(not Catalog.cell_valid([8, 2]), "reject outside cell")
	check(not Catalog.validate([]).ok, "reject wrong root type")
	print("CONTENT_TEST_RESULTS: failures=%d" % failures)
	quit(1 if failures else 0)
