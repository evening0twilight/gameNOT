extends SceneTree
## Visible Godot controls in a hidden 720p viewport. No commands constructed by this driver.
const OUTPUT="res://../outputs/p4release-20261119"
var ui: Control
var canvas: SubViewport
var rows: Array=[]
var events: Array=[]
var errors: Array=[]
var current_day: int=0
var canceled_route: bool=false
var frames: Array=[]
var last_phase: String=""
var scrolls: int=0

func _initialize() -> void:
	if DisplayServer.get_name()!="headless":root.hide()
	root.gui_embed_subwindows=true
	call_deferred("run")

func controls() -> Node:
	if ui.confirmation.visible:return ui.confirmation
	for child: Node in ui.get_children():
		if child is Window and child.visible and not child.is_queued_for_deletion():return child
	return ui.root

func button(text: String) -> Button:
	for b: Node in controls().find_children("*","Button",true,false):
		if b.is_visible_in_tree() and not b.disabled and b.text==text:return b
	return null

func settle() -> void:
	await process_frame
	await process_frame

func capture(id: String) -> void:
	if DisplayServer.get_name()=="headless" or frames.has(id):return
	RenderingServer.force_draw(false)
	var picture: Image=canvas.get_texture().get_image()
	if picture.get_size()!=canvas.size or picture.save_png(OUTPUT+"/visible-"+id+".png")!=OK:
		errors.append("Could not save offscreen state "+id)
	else:frames.append(id)

func visible_area(node: Control) -> Rect2:
	var area: Rect2=node.get_viewport().get_visible_rect()
	var parent: Node=node.get_parent()
	while parent is Control:
		if parent.clip_contents:area=area.intersection(parent.get_global_rect())
		parent=parent.get_parent()
	return area

func hit(control: Control,label_text: String,at: Vector2=Vector2.INF) -> bool:
	if not is_instance_valid(control) or not control.is_visible_in_tree():return false
	var position: Vector2=control.get_global_rect().get_center() if at==Vector2.INF else at
	var parent: Node=control.get_parent()
	while parent is Control:
		if parent is ScrollContainer and not visible_area(control).has_point(position):
			var previous: int=parent.scroll_vertical
			parent.ensure_control_visible(control)
			await settle()
			if previous!=parent.scroll_vertical:
				scrolls+=1
				events.append({"ui":"scroll","day":current_day,"to":label_text,"delta":parent.scroll_vertical-previous})
			position=control.get_global_rect().get_center() if at==Vector2.INF else at
		parent=parent.get_parent()
	if not visible_area(control).has_point(position):
		errors.append("Unreachable "+label_text+" at "+str(position)+" clip "+str(visible_area(control)))
		return false
	var surface: Viewport=control.get_viewport()
	if surface is Window and surface.is_embedded():
		position+=Vector2(surface.position)
		surface=surface.get_parent().get_viewport()
	var event:=InputEventMouseMotion.new();event.position=position;event.global_position=position;surface.push_input(event,true)
	for pressed: bool in [true,false]:
		var click:=InputEventMouseButton.new()
		click.button_index=MOUSE_BUTTON_LEFT;click.position=position;click.global_position=position;click.pressed=pressed
		surface.push_input(click,true)
	events.append({"day":current_day,"phase":last_phase,"ui":label_text,"x":roundi(position.x),"y":roundi(position.y)})
	await settle()
	return true

func press(text: String) -> bool:
	var b: Button=button(text)
	if not is_instance_valid(b):
		errors.append("Missing "+text+" in "+str(controls().name))
		return false
	return await hit(b,text)

func battle() -> bool:
	if ui.inline_pending:
		if current_day==1:capture("first-move")
		return await press(ui.I18n.t("p4.confirm_action"))
	if current_day==1:
		if button("我看清预告了"):return await press("我看清预告了")
		var step: Dictionary=ui.FirstShift.lesson(ui).next
		if step.has("actor"):return await press(ui.actor_name(step.actor))
		var kind: String=step.get("action","")
		if kind.is_empty():errors.append("First rescue gave no next action");return false
		var label: String=ui.action_name(kind)
		if not await press(label):return false
		if kind in ["move","stabilize","pickup"]:
			var map: Control=ui.root.find_child("TacticalMap",true,false)
			var cell: Array=map.hint_cell
			if cell.is_empty():errors.append("Missing first-rescue board outline");return false
			return await hit(map,"board "+str(cell),map.get_global_transform()*map.center(cell))
		return true
	if button("明白了 · 保留操作"):
		if current_day==2:capture("clinic-circuit")
		return await press("明白了 · 保留操作")
	return await press("看看下一步怎么做")

func act() -> bool:
	if ui.confirmation.visible:
		if ui.pending.get("kind","")=="select_route" and not canceled_route:
			var before: int=ui.session.state.revision
			capture("final-route-preview")
			canceled_route=true
			if not await hit(ui.confirmation.get_cancel_button(),ui.confirmation.cancel_button_text):return false
			if ui.session.state.revision!=before or not button(ui.I18n.t("p3.route_evacuation")):
				errors.append("Cancel must return to the route choices without committing")
				return false
			return true
		return await hit(ui.confirmation.get_ok_button(),ui.confirmation.ok_button_text)
	var view: Node=controls()
	if view is Window:
		for key: String in ["journey.keep_roster","baseline018.eb18d0a2363c","p3.route_evacuation"]:
			if button(ui.I18n.t(key)):
				if key=="p3.route_evacuation" and not ui.session.state.full_campaign.route.is_empty():
					view.close_requested.emit();await settle();return true
				return await press(ui.I18n.t(key))
		for caption: String in ["明白了 · 继续夜间总结","查看最终路线","完成基础引导 · 开始第5天",ui.I18n.t("baseline018.e6f809da1227")]:
			if button(caption):return await press(caption)
		errors.append("Unhandled modal "+view.title)
		return false
	match last_phase:
		"briefing":return await press("开始救援 · 边做边学" if current_day==1 else "出发 · 到现场再学")
		"battle":return await battle()
		"settlement":return await press("回到营地 · 安排第一晚" if current_day==1 else ui.I18n.t("ui.6de354f5f7cd"))
		"camp":
			if current_day!=2 and current_day!=23 and button("明白了 · 稍后再用"):return await press("明白了 · 稍后再用")
			return await press("结束夜晚 · 准备明天" if current_day==1 else "结束今晚")
	return false

func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true
	canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui)
	ui.I18n.locale="zh_CN";ui.font_size=20;ui.reduced_motion=true
	# Only the fresh slot setup is injected; all subsequent state changes go through the UI.
	if not ui.session.start(ui.session.content,"user://tests/visible-%d/save.json"%Time.get_ticks_usec(),"release-visible").ok:
		quit(1);return
	ui.title_screen=false;ui.render();await settle()
	var repeated: int=0
	var previous_key: String=""
	for index: int in range(4400):
		current_day=ui.session.state.campaign.day;last_phase=ui.session.state.campaign.phase
		if ui.session.state.chapter_one.finished:break
		if rows.is_empty() or rows[-1].day!=current_day:
			rows.append({"day":current_day,"first_event":events.size(),"scrolls_before":scrolls})
			print("VISIBLE_DAY ",current_day," event ",events.size())
		if last_phase=="camp":
			rows[-1].camp=true
			if current_day==20 and controls()==ui.root:
				capture("evidence-night")
				var complete: Array=[]
				for id: String in ["west","east"]:
					if ui.Guidance.secured(ui.session.state.battle.objects[id]):complete.append(ui.object_name(id))
				if complete.size()!=1 or ui.objective_summary()!=ui.I18n.t("p3.done")+str(complete[0]):
					errors.append("Shelter summary must name only the secured site")
					break
		var view: Node=controls()
		var key: String=str([ui.session.state.revision,ui.selected,ui.action,ui.pending.get("kind",""),ui.inline_pending,str(view.title) if view is Window else "",ui.confirmation.visible])
		repeated=repeated+1 if previous_key==key else 0;previous_key=key
		if repeated>=3:
			errors.append("Control did not advance: "+key);break
		if not await act():break
	if ui.session.state.chapter_one.finished:
		capture("ending")
		for row: Dictionary in rows:
			var result: Dictionary=ui.session.state.campaign.settled["M%02d"%row.day]
			row.outcome=result.outcome;row.party=result.roster
			row.facts=result.facts
		var path: String=ProjectSettings.globalize_path(OUTPUT+"/visible-ending-"+DisplayServer.get_name()+".json")
		if DirAccess.copy_absolute(ProjectSettings.globalize_path(ui.session.path),path)!=OK:errors.append("Could not retain UI ending autosave")
		else:
			var loaded: Dictionary=ui.session.store.load_slot(path,ui.session.content)
			if not loaded.ok or loaded.state.revision!=ui.session.state.revision:errors.append("UI ending autosave failed reload")
	if not canceled_route:errors.append("Final-route cancel/reopen was never exercised")
	if not ui.session.state.chapter_one.finished or current_day!=24:errors.append("Visible campaign did not reach ending")
	if not errors.is_empty():
		var buttons: Array=[]
		for b: Node in controls().find_children("*","Button",true,false):
			if b.is_visible_in_tree():buttons.append(b.text)
		printerr("VISIBLE_STOP ",errors," buttons=",buttons," tail=",events.slice(-5))
	for i: int in range(rows.size()):
		var end: int=rows[i+1].first_event if i+1<rows.size() else events.size()
		rows[i].ui_events=end-int(rows[i].first_event)
		rows[i].scrolls=int(rows[i+1].scrolls_before if i+1<rows.size() else scrolls)-int(rows[i].scrolls_before)
		rows[i].erase("scrolls_before")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT))
	var file:=FileAccess.open(OUTPUT+"/visible-"+DisplayServer.get_name()+".json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"days":rows,"failures":errors,"frames":frames,"events":events,"ending":ui.session.state.full_campaign.ending,"route":ui.session.state.full_campaign.route,"scope":"Isolated fresh slot; Chinese 1280x720 reduced-motion UI, deterministic pointer input through Godot viewports. ScrollContainer reveal and window close request are UI-level operations. No native Windows input, human perception or timing claim."},"\t"));file.close()
	print("VISIBLE_RESULTS days=%d events=%d scrolls=%d failures=%d"%[rows.size(),events.size(),scrolls,errors.size()])
	ui.sound.stop_audio();ui.queue_free();await settle();quit(int(not errors.is_empty()))
