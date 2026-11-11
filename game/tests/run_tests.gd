extends SceneTree

const Rules = preload("res://scripts/domain/relationship_rules.gd")
const Store = preload("res://scripts/domain/save_store.gd")
var passed: Array[String] = []
var failures: Array[String] = []

func check(label: String, condition: bool) -> void:
	if condition:
		passed.append(label)
	else:
		failures.append(label)
		push_error(label)

func base(grudge: float = 0.0, trust: float = 50.0) -> Dictionary:
	return Rules.create({"observer":"lin", "target":"xu", "grudge":grudge, "trust":trust, "grudge_categories":["promise"]})

func incident(id: String, serious: bool = false) -> Dictionary:
	return {"id":id, "observer":"lin", "blame":{"xu":1.0}, "category":"promise", "severity":12.0,
		"sensitivity":1.0, "trust_loss":8.0, "serious":serious, "remedy":"keep_agreement"}

func _initialize() -> void:
	var neutral: Dictionary = base()
	var old: Dictionary = base(55.0)
	check("historical resentment exists at new game", is_equal_approx(Rules.resentment(old, 1), 55.0))
	check("new game already displays the historical grievance band", old["band"] == "guarded")
	var n1: Dictionary = Rules.apply_event(neutral, incident("a"), 1, 50.0)
	var o1: Dictionary = Rules.apply_event(old, incident("a"), 1, 50.0)
	check("same provocation grows faster with relevant old grievance", float(o1["memories"][0]["amplitude"]) > float(n1["memories"][0]["amplitude"]))
	check("pure transition preserves original input", neutral["memories"].is_empty() and old["memories"].is_empty())
	check("duplicate event is idempotent", Rules.apply_event(o1, incident("a"), 1, 50.0) == o1)
	var hidden: Dictionary = incident("hidden")
	hidden["known"] = false
	check("unknown actions do not cause telepathy", Rules.apply_event(old, hidden, 1, 50.0) == old)
	var order: Dictionary = incident("leader_order")
	order["blame"] = {"leader":1.0}
	check("leader order does not blame innocent teammate", Rules.apply_event(old, order, 1, 50.0) == old)
	var other_observer: Dictionary = incident("other")
	other_observer["observer"] = "xu"
	check("directional relationship is respected", Rules.apply_event(old, other_observer, 1, 50.0) == old)
	var invalid: Dictionary = incident("bad")
	invalid["blame"] = {"xu":0.8,"leader":0.8}
	check("invalid responsibility split rejected", Rules.apply_event(old, invalid, 1, 50.0) == old)
	check("stress alone does not create interpersonal grievance", Rules.update_band(base(), 1, 100.0)["band"] == "calm")
	var hysteresis: Dictionary = base(44.0)
	hysteresis["band"] = "guarded"
	check("hysteresis keeps warning state below entry threshold", Rules.update_band(hysteresis, 1, 40.0)["band"] == "guarded")
	check("same pressure does not prematurely enter state", Rules.update_band(base(44.0), 1, 40.0)["band"] == "calm")
	var high: Dictionary = Rules.update_band(base(85.0), 1, 40.0)
	check("threshold alone cannot cause unannounced outburst", not Rules.can_rupture(high, 1, "M01", true, false))
	check("unrelated action cannot trigger outburst", not Rules.can_rupture(high, 1, "M01", false, true))
	check("qualified redline can trigger outburst", Rules.can_rupture(high, 1, "M01", true, true))
	var marked: Dictionary = Rules.mark_rupture(high, 1, "M01")
	check("same mission does not repeatedly trigger outburst", not Rules.can_rupture(marked, 4, "M01", true, true))
	check("next day respects cooldown", not Rules.can_rupture(marked, 2, "M02", true, true))
	check("later relevant mission can trigger unresolved conflict", Rules.can_rupture(marked, 3, "M03", true, true))
	var ack: Dictionary = Rules.acknowledge(o1, "a")
	check("acknowledgement cannot be spammed", Rules.acknowledge(ack, "a") == ack)
	check("wrong repair cannot erase specific memory", Rules.repair(ack, "a", "gift", "buy_gift") == ack)
	var fixed: Dictionary = Rules.repair(ack, "a", "mission-proof", "keep_agreement")
	check("repair token cannot be replayed", Rules.repair(fixed, "a", "mission-proof", "keep_agreement") == fixed)
	var safe_floor: bool = true
	for start: int in range(101):
		var state: Dictionary = Rules.apply_event(base(0.0, start), incident("harm"), 1, 30.0)
		state = Rules.repair(Rules.acknowledge(state,"harm"),"harm","proof","keep_agreement")
		safe_floor = safe_floor and float(state["trust"]) <= start
	check("hurt-repair cannot farm trust at any initial value 0..100", safe_floor)
	check("time alone does not erase historical grievance", is_equal_approx(Rules.resentment(old, 1000), 55.0))
	var h1: Dictionary = Rules.repair_history(old, 1, "verified-history")
	check("history repair is staged and irreversible by repeat", Rules.repair_history(h1, 1, "another-token") == h1)
	check("cannot skip directly to forgiveness", Rules.repair_history(old, 3, "shortcut") == old)
	check("history repair does not delete later incident memories", Rules.repair_history(o1, 1, "history")["memories"] == o1["memories"])
	var bounded: bool = true
	for seed_value: int in range(50):
		var rng := RandomNumberGenerator.new()
		rng.seed = seed_value
		var state: Dictionary = base(rng.randf_range(0.0, 70.0))
		for day: int in range(60):
			var e: Dictionary = incident(str(day), day % 7 == 0)
			e["severity"] = rng.randf_range(0.0, 50.0)
			state = Rules.apply_event(state, e, day, rng.randf_range(0.0,100.0))
			var value: float = Rules.resentment(state, day)
			bounded = bounded and value >= 0.0 and value <= 100.0 and float(state["trust"]) >= 0.0
	check("50 seeded histories x 60 days remain bounded", bounded)
	var sample: Array = []
	for g: float in [0.0, 42.0, 55.0]:
		var state: Dictionary = base(g)
		var points: Array = [{"step":0,"resentment":Rules.resentment(state,1),"pressure":Rules.pressure(state,1,60.0)}]
		for step: int in range(1,5):
			# Four separate explicit breaches, not four observations of one incident.
			state = Rules.apply_event(state, incident("breach_%d" % step, true), 1, 60.0)
			state = Rules.update_band(state,1,60.0)
			points.append({"step":step,"resentment":Rules.resentment(state,1),"pressure":Rules.pressure(state,1,60.0),"band":state["band"]})
		sample.append({"initial_grudge":g,"points":points})

	var path: String = "user://preparation_test_save.json"
	for suffix: String in ["", ".bak", ".tmp"]:
		if FileAccess.file_exists(path + suffix):
			DirAccess.remove_absolute(path + suffix)
	var rng := RandomNumberGenerator.new()
	rng.seed = 20261031
	rng.randf()
	var saved_rng_state: String = str(rng.state)
	var expected_next: int = rng.randi()
	var payload: Dictionary = {"relationship":o1,"rng_seed":"20261031","rng_state":saved_rng_state,"content_version":"0.2"}
	check("save write succeeds", Store.save_file(path,payload) == OK)
	var loaded: Dictionary = Store.load_file(path)
	check("save preserves relationship totals", loaded.get("ok",false) and is_equal_approx(Rules.resentment(loaded["state"]["relationship"],1),Rules.resentment(o1,1)))
	var restored := RandomNumberGenerator.new()
	restored.seed = int(loaded["state"]["rng_seed"])
	restored.state = int(loaded["state"]["rng_state"])
	check("saved RNG state restores next random value", restored.randi() == expected_next)
	check("second save creates backup", Store.save_file(path,{"new":true}) == OK and Store.load_file(path+".bak").get("ok",false))
	var bad := FileAccess.open(path,FileAccess.WRITE)
	bad.store_string("broken{")
	bad.close()
	check("corrupt save is rejected", not Store.load_file(path).get("ok",false))
	check("saving over corruption preserves valid backup", Store.save_file(path,{"new":true}) == ERR_FILE_CORRUPT and Store.load_file(path+".bak").get("ok",false))
	for suffix: String in ["", ".bak", ".tmp"]:
		if FileAccess.file_exists(path + suffix):
			DirAccess.remove_absolute(path + suffix)
	var output: Dictionary = {"engine":Engine.get_version_info(),"passed_count":passed.size(),"passed":passed,"failures":failures,"curve_samples":sample,
		"scope":"relationship rules and preparation save container only; no complete combat or campaign"}
	var report := FileAccess.open("res://docs/engine-checks.json",FileAccess.WRITE)
	report.store_string(JSON.stringify(output,"  "))
	report.close()
	print("TEST_RESULTS: %d passed, %d failed" % [passed.size(), failures.size()])
	quit(0 if failures.is_empty() else 1)
