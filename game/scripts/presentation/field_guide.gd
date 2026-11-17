extends RefCounted
const Learning=preload("res://scripts/domain/field_learning.gd")
static func active(ui: Control) -> bool:return ui.guidance_enabled and Learning.active(ui.session.state)
static func offer(ui: Control) -> Dictionary:
	var key: int=hash([ui.session.state.revision,ui.session.state.battle,ui.session.state.tutorial,ui.selected])
	if key!=ui.field_offer_key:
		ui.field_offer_key=key;ui.field_offer=Learning.offer(ui.session.state,ui.session.content,ui.selected)
	return ui.field_offer
static func title(ui: Control,info: Dictionary) -> String:
	return ui.I18n.t("p4.item."+info.item) if info.has("item") else info.title
static func copy(ui: Control,box: Node,text: String,color: Color) -> void:
	var label: Label=ui.label(box,text);label.add_theme_font_size_override("font_size",maxi(16,ui.font_size-2));label.add_theme_color_override("font_color",color)
static func panel(ui: Control,box: VBoxContainer) -> void:
	var lesson: Dictionary=offer(ui)
	if not lesson.is_empty():
		copy(ui,box,"本次只学一个 · "+title(ui,lesson),ui.GOLD)
		copy(ui,box,lesson.why,ui.INK);copy(ui,box,lesson.how,ui.TEAL)
		ui.button(box,"明白了 · 保留操作",func():ui.field_ack(lesson.topic))
		if lesson.has("payload"):
			ui.button(box,"查看一个可行示例",func():preview_example(ui,lesson))
	else:
		copy(ui,box,"按自己的节奏继续",ui.TEAL)
		copy(ui,box,"已学操作留在右侧。遇到适合的现场，再介绍下一项。",ui.MUTED)
	var next: Dictionary=ui.current_guidance()
	if not next.is_empty():
		ui.button(box,"看看下一步怎么做",ui.preview_guidance)
static func preview_example(ui: Control,info: Dictionary) -> void:
	ui.action=info.kind
	if info.has("item"):ui.tool=info.item
	if info.has("ability"):ui.ability=info.ability;ui.specialty_mode="ap" if info.topic.ends_with(":ap") else "move"
	if info.kind=="protocol":ui.protocol=info.payload.protocol;ui.partner=info.payload.partner
	ui.propose(info.kind,info.payload.duplicate(true))
static func select(ui: Control,info: Dictionary) -> void:
	if info.get("passive",false):details(ui,info.topic,true);return
	ui.action=info.kind;ui.specialty_target="";ui.anchor_start=[]
	if info.has("ability"):ui.ability=info.ability;ui.specialty_mode="ap" if info.topic.ends_with(":ap") else "move"
	if info.has("item"):ui.tool=info.item
	ui.message=info.how;ui.render()
	if info.get("ability","")=="chen_3" and not ui.session.state.battle.service.is_empty():choices(ui,info.topic)
	elif info.kind in ["extract","leave_site","drop"]:ui.propose(info.kind,{})
	elif info.topic.begins_with("protocol:") or info.kind in ["service_watch","restore_power","prepare_safety","authorize","promise_retreat","declare_priority"]:choices(ui,info.topic)
static func actions(ui: Control,box: VBoxContainer) -> void:
	var known: Array=Learning.known(ui.session.state)
	var lesson: Dictionary=offer(ui)
	var topics: Array=Learning.available(ui.session.state,ui.session.content,ui.selected)
	var grid:=GridContainer.new();grid.columns=2;box.add_child(grid)
	for topic: String in topics:
		if topic.begins_with("objective:") or (not known.has(topic) and lesson.get("topic","")!=topic):continue
		var info: Dictionary=Learning.describe(topic,ui.session.content)
		if info.is_empty():continue
		if topic.begins_with("protocol:"):info.kind="protocol"
		var button: Button=ui.button(grid,("新 · " if not known.has(topic) else "")+title(ui,info),func():select(ui,info))
		button.size_flags_horizontal=Control.SIZE_EXPAND_FILL;button.custom_minimum_size.x=0
		button.tooltip_text=info.why+"\n"+info.how
		if not known.has(topic):button.add_theme_stylebox_override("normal",ui.surface(Color("35524c"),8,ui.TEAL))
	copy(ui,box,"选操作 → 点目标 → 看预览",ui.MUTED)
	if known.has("service_watch") and not ui.session.state.battle.service.is_empty():
		var service: Dictionary=ui.session.state.battle.service
		copy(ui,box,service.definition.label+" · %d/%d轮"%[service.ticks,service.definition.consecutive_rounds]+(" · 已完成" if service.done else (" · 已失效" if service.failed else " · 需持续值守")),ui.GOLD)
static func browse(ui: Control) -> void:
	var dialog: Dictionary=ui.modal("按需学习 · 选择一项")
	ui.label(dialog.box,"可查阅当前队员能用的操作；关闭后仍按场景逐个教学。")
	ui.button(dialog.box,"查看现场与全部目标",func():dialog.window.queue_free();ui.show_site())
	ui.button(dialog.box,"展开全部操作 · 跳过教学",func():dialog.window.queue_free();ui.tutorial_ack("skip"))
	for topic: String in Learning.available(ui.session.state,ui.session.content,ui.selected):
		var info: Dictionary=Learning.describe(topic,ui.session.content)
		ui.button(dialog.box,title(ui,info),func():dialog.window.queue_free();details(ui,topic,true))
static func details(ui: Control,topic: String,manual: bool) -> void:
	var info: Dictionary=Learning.describe(topic,ui.session.content)
	var dialog: Dictionary=ui.modal(title(ui,info));ui.label(dialog.box,info.why);ui.label(dialog.box,info.how)
	ui.button(dialog.box,"已了解 · 保留这个操作",func():dialog.window.queue_free();ui.field_ack(topic,manual))
static func choices(ui: Control,topic: String) -> void:
	var info: Dictionary=Learning.describe(topic,ui.session.content)
	if topic.begins_with("protocol:"):info.kind="protocol"
	var dialog: Dictionary=ui.modal(title(ui,info));ui.label(dialog.box,info.how)
	var count: int=0
	for payload: Dictionary in Learning.payloads(ui.session.state,ui.session.content,ui.selected,topic):
		if not Learning.legal(ui.session.state,ui.session.content,ui.selected,info.kind,payload):continue
		count+=1
		var caption: String=title(ui,info)
		if payload.has("partner"):caption+=" · "+ui.actor_name(payload.partner)
		if payload.has("target"):
			caption+=" · "+(ui.actor_name(payload.target) if ui.session.state.battle.heroes.has(payload.target) else ("现场设施" if payload.target=="live_service" else (ui.object_name(payload.target) if ui.session.state.battle.objects.has(payload.target) else "机器")))
		if payload.has("post"):caption+=" · 岗位%d"%(payload.post+1)
		if payload.has("priority"):caption+=" · "+("人员优先" if payload.priority=="people" else "物资优先")
		if info.kind=="prepare_safety":caption+=" · "+("施工保障" if payload.protocol=="protected_work" else "掩护保障")
		if payload.has("cell"):caption+=" → %d,%d"%[payload.cell[0]+1,payload.cell[1]+1]
		ui.button(dialog.box,caption,func():dialog.window.queue_free();ui.action=info.kind;ui.propose(info.kind,payload.duplicate(true)))
	if count==0:ui.label(dialog.box,"当前没有满足条件的方案。请先检查距离、双方行动点和现场状态。")
static func briefing(ui: Control,parent: Node) -> void:
	var s: Dictionary=ui.session.state
	var board: Dictionary=ui.session.content.boards[s.journey.next_mission]
	var frame:=HBoxContainer.new();frame.size_flags_horizontal=Control.SIZE_EXPAND_FILL;frame.add_theme_constant_override("separation",24);parent.add_child(frame)
	var left:=VBoxContainer.new();left.size_flags_horizontal=Control.SIZE_EXPAND_FILL;frame.add_child(left)
	left.add_child(ui.Art.site_picture(board.location,Vector2(0,240)))
	ui.label(left,"第 %d 天 · %s"%[s.campaign.day,board.title]).add_theme_font_size_override("font_size",28)
	ui.label(left,board.decision)
	var right:=VBoxContainer.new();right.custom_minimum_size.x=440;right.size_flags_horizontal=Control.SIZE_EXPAND_FILL;frame.add_child(right)
	ui.label(right,"本次要完成").add_theme_color_override("font_color",ui.GOLD)
	for group: Array in ui.Full.groups(s,board):
		var names: Array[String]=[]
		for id: String in group:
			for object: Dictionary in board.objectives:
				if object.id==id:names.append(object.label)
		ui.label(right," / ".join(names))
	ui.label(right,"仍使用已学的操作。新装置和新方法，会在现场一次介绍一个。").add_theme_color_override("font_color",ui.MUTED)
	var roster: Array[String]=[]
	for id: String in s.journey.draft.roster:roster.append(ui.actor_name(id))
	ui.label(right,"出勤："+"、".join(roster))
	ui.button(right,"出发 · 到现场再学",func():ui.full_preparation=false;ui.propose("depart",s.journey.draft.duplicate(true)))
	ui.button(right,"调整阵容与装备",func():ui.full_preparation=true;ui.render())
