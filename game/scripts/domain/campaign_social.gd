extends RefCounted
## Runtime social authority: irreversible memory budgets and factual contribution rewards.
const Legacy=preload("res://scripts/domain/relationship_rules.gd")
static func create(initial: Dictionary) -> Dictionary:
	var r:=Legacy.create(initial)
	r.contribution_missions=[]
	r.agreement="professional"
	r.renegotiated_day=0
	return r
static func value(r: Dictionary,day: int) -> float:
	var result: float=r.grudge
	for m: Dictionary in r.memories:
		if not m.get("archived",false): result+=Legacy.memory_value(m,day)
	return result
static func refresh(r: Dictionary,day: int,stress: float) -> Dictionary:
	return Legacy.update_band(r,day,stress)
static func event(r: Dictionary,e: Dictionary,day: int,stress: float) -> Dictionary:
	var next:=Legacy.apply_event(r,e,day,stress)
	if next.memories.size()==r.memories.size():return next
	var categories: Dictionary={}
	for m: Dictionary in next.memories:
		if m.get("archived",false) or m.serious:continue
		if not categories.has(m.category):categories[m.category]=[]
		categories[m.category].append(m)
	for entries: Array in categories.values():
		entries.sort_custom(func(a: Dictionary,b: Dictionary):return str(a.id)<str(b.id) if is_equal_approx(Legacy.memory_value(a,day),Legacy.memory_value(b,day)) else Legacy.memory_value(a,day)>Legacy.memory_value(b,day))
		for i: int in range(3,entries.size()): entries[i].archived=true;entries[i].amplitude=0.0
		var total: float=0
		for m: Dictionary in entries:total+=Legacy.memory_value(m,day)
		if total>24:
			for m: Dictionary in entries:m.amplitude*=24/total
	var active: float=value(next,day)-float(next.grudge)
	if active>100-float(next.grudge):
		for m: Dictionary in next.memories:m.amplitude*=(100-float(next.grudge))/active
	return refresh(next,day,stress)
