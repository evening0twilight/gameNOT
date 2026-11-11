class_name RelationshipRules
extends RefCounted
## Pure rules. No UI, no random calls, no direct global state mutation.
## Coefficients are design hypotheses. Gameplay must validate repair tokens.

const BANDS: Array[String] = ["calm", "guarded", "conditional", "rupture"]
const ENTER: Array[float] = [0.0, 45.0, 65.0, 80.0]
const EXIT: Array[float] = [0.0, 35.0, 50.0, 60.0]

static func create(initial: Dictionary) -> Dictionary:
	var state: Dictionary = initial.duplicate(true)
	state["grudge"] = clampf(float(state.get("grudge", 0.0)), 0.0, 100.0)
	state["trust"] = clampf(float(state.get("trust", 50.0)), 0.0, 100.0)
	state["closeness"] = clampf(float(state.get("closeness", 20.0)), 0.0, 100.0)
	state["memories"] = []
	state["seen_events"] = []
	state["repair_tokens"] = []
	state["history_stage"] = 0
	state["band"] = "calm"
	state["last_rupture_mission"] = ""
	state["cooldown_until_day"] = -1
	return update_band(state, 1, 0.0)

static func memory_value(memory: Dictionary, day: int) -> float:
	var stage: int = int(memory.get("stage", 0))
	var floor_ratio: float = float(memory.get("floor", 0.0)) if stage < 2 else 0.0
	var factors: Array[float] = [1.0, 0.85, 0.45]
	var age: float = maxf(0.0, day - int(memory["day"]))
	return float(memory["amplitude"]) * factors[stage] * (
		floor_ratio + (1.0 - floor_ratio) * pow(2.0, -age / float(memory["half_life"])))

static func resentment(state: Dictionary, day: int) -> float:
	var result: float = float(state["grudge"])
	var categories: Dictionary = {}
	for memory: Dictionary in state["memories"]:
		var value: float = memory_value(memory, day)
		if bool(memory.get("serious", false)):
			result += value
		else:
			var category: String = str(memory["category"])
			if not categories.has(category):
				categories[category] = []
			categories[category].append(value)
	for values: Array in categories.values():
		values.sort()
		values.reverse()
		var subtotal: float = 0.0
		for i: int in range(mini(3, values.size())):
			subtotal += float(values[i])
		result += minf(24.0, subtotal)
	return clampf(result, 0.0, 100.0)

static func apply_event(input: Dictionary, event: Dictionary, day: int, stress: float) -> Dictionary:
	var state: Dictionary = input.duplicate(true)
	var incident: String = str(event.get("id", ""))
	if incident.is_empty() or not bool(event.get("known", true)):
		return state
	if str(event.get("observer", "")) != str(state.get("observer", "")):
		return state
	if incident in state["seen_events"]:
		return state
	var blame: Dictionary = event.get("blame", {})
	var total: float = 0.0
	for value: Variant in blame.values():
		if float(value) < 0.0:
			return state
		total += float(value)
	if total > 1.000001:
		return state
	var share: float = float(blame.get(str(state.get("target", "")), 0.0))
	if share <= 0.0:
		return state
	var category: String = str(event.get("category", "promise"))
	var relevant_history: float = float(state["grudge"]) if category in state.get("grudge_categories", []) else 0.0
	var old_r: float = resentment(state, day)
	var repetitions: int = 0
	for memory: Dictionary in state["memories"]:
		if str(memory["category"]) == category and 0 <= day - int(memory["day"]) and day - int(memory["day"]) <= 2:
			repetitions += 1
	var multiplier: float = (1.0 + 0.7 * pow(relevant_history / 100.0, 2.0))
	multiplier *= (1.0 + 0.8 * pow(old_r / 100.0, 2.0))
	multiplier *= (1.0 + 0.25 * clampf(stress, 0.0, 100.0) / 100.0)
	multiplier *= (1.0 + minf(0.4, 0.1 * repetitions))
	var amplitude: float = minf(40.0, maxf(0.0, float(event.get("severity", 0.0)))
		* clampf(float(event.get("sensitivity", 1.0)), 0.8, 1.3) * share * multiplier)
	var old_trust: float = float(state["trust"])
	state["trust"] = maxf(0.0, old_trust - maxf(0.0, float(event.get("trust_loss", 8.0))) * share)
	var serious: bool = bool(event.get("serious", false))
	state["memories"].append({"id": incident, "category": category, "amplitude": amplitude,
		"day": day, "half_life": 8.0 if serious else 3.0, "floor": 0.35 if serious else 0.0,
		"serious": serious, "stage": 0, "actual_trust_loss": old_trust - float(state["trust"]),
		"remedy": str(event.get("remedy", "keep_agreement"))})
	state["seen_events"].append(incident)
	return state

static func pressure(state: Dictionary, day: int, stress: float) -> float:
	return clampf(resentment(state, day) + 0.25 * maxf(0.0, stress - 40.0), 0.0, 100.0)

static func update_band(input: Dictionary, day: int, stress: float) -> Dictionary:
	var state: Dictionary = input.duplicate(true)
	var index: int = maxi(0, BANDS.find(str(state.get("band", "calm"))))
	var q: float = pressure(state, day, stress)
	if resentment(state, day) < 25.0:
		index = 0
	else:
		while index > 0 and q < EXIT[index]:
			index -= 1
		while index < 3 and q >= ENTER[index + 1]:
			index += 1
	state["band"] = BANDS[index]
	return state

static func can_rupture(state: Dictionary, day: int, mission_id: String, relevant: bool, warned_or_redline: bool) -> bool:
	return str(state["band"]) == "rupture" and relevant and warned_or_redline \
		and day >= int(state["cooldown_until_day"]) and mission_id != str(state["last_rupture_mission"])

static func mark_rupture(input: Dictionary, day: int, mission_id: String) -> Dictionary:
	var state: Dictionary = input.duplicate(true)
	state["last_rupture_mission"] = mission_id
	state["cooldown_until_day"] = day + 2
	return state

static func acknowledge(input: Dictionary, incident: String) -> Dictionary:
	var state: Dictionary = input.duplicate(true)
	for memory: Dictionary in state["memories"]:
		if str(memory["id"]) == incident and int(memory["stage"]) == 0:
			memory["stage"] = 1
	return state

static func repair(input: Dictionary, incident: String, token: String, remedy: String) -> Dictionary:
	var state: Dictionary = input.duplicate(true)
	if token.is_empty() or token in state["repair_tokens"]:
		return state
	for memory: Dictionary in state["memories"]:
		if str(memory["id"]) == incident and int(memory["stage"]) == 1 and str(memory["remedy"]) == remedy:
			memory["stage"] = 2
			var restored: float=minf(4.0,float(memory["actual_trust_loss"])/2.0)
			memory["refunded"]=float(memory.get("refunded",0))+minf(100.0-float(state["trust"]),restored)
			state["trust"] = minf(100.0, float(state["trust"]) + restored)
			state["repair_tokens"].append(token)
			return state
	return state

static func repair_history(input: Dictionary, stage: int, validated_token: String) -> Dictionary:
	var state: Dictionary = input.duplicate(true)
	if stage != int(state["history_stage"]) + 1 or stage > 3 or validated_token.is_empty() or validated_token in state["repair_tokens"]:
		return state
	var reductions: Array[float] = [0.0, 6.0, 12.0, 12.0]
	state["grudge"] = maxf(0.0, float(state["grudge"]) - reductions[stage])
	state["history_stage"] = stage
	state["repair_tokens"].append(validated_token)
	return state

