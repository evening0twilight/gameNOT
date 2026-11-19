extends RefCounted
const I18n=preload("res://scripts/presentation/localization.gd")
## Stable labels follow authored order, including branch alternatives.
static func cell_text(cell: Array) -> String:
	return "(%d, %d)" % [int(cell[0])+1,int(cell[1])+1]

static func cell_list(cells: Array) -> String:
	var names: Array[String]=[]
	for cell: Array in cells:names.append(cell_text(cell))
	return ", ".join(names)

static func code(board: Dictionary,battle: Dictionary,id: String) -> String:
	var ids: Array=[]
	for object: Dictionary in board.objectives+board.get("controls",[]):
		if not ids.has(object.id):ids.append(object.id)
	for key: String in battle.objects:
		if not ids.has(key):ids.append(key)
	var index: int=ids.find(id)
	return String.chr(65+index) if index>=0 and index<26 else str(index+1)
static func location(battle: Dictionary,object: Dictionary) -> Array:
	var carrier: String=object.carrier
	return battle.heroes[carrier].cell if battle.heroes.has(carrier) else object.cell

static func status(object: Dictionary) -> String:
	if object.lost or object.has("unavailable_reason"):return I18n.s("已失去")
	if object.completed:return I18n.s("已完成")
	if object.get("active",false):return I18n.s("进行中 %d/%d")%[int(object.get("timer",0)) if object.kind=="channel" else int(object.get("waypoint",0)),int(object.get("hold_rounds",1)) if object.kind=="channel" else maxi(1,object.get("waypoints",[]).size()-1)]
	if not object.carrier.is_empty():return I18n.s("携带中")
	if object.kind=="cargo":return I18n.s("待搬运")
	if object.work>0:return "%d / %d"%[object.progress,object.work]
	if object.stable:return I18n.s("已稳定")
	return I18n.s("待救援") if object.kind=="rescue" else I18n.s("待处理")
