extends RefCounted
## A readable workspace around the actual board; all commands still use Session.
static func small(ui: Control,parent: Node,text: String,color: Color) -> Label:
	var label: Label=ui.label(parent,text)
	label.add_theme_font_size_override("font_size",maxi(14,ui.font_size-4))
	label.add_theme_color_override("font_color",color)
	return label

static func render(ui: Control,body: HBoxContainer) -> void:
	var s: Dictionary=ui.session.state
	if ui.feedback_active() and s.campaign.phase!="battle":s=s.duplicate(true);s.campaign.phase="battle"
	var b: Dictionary=s.battle
	var board: Dictionary=ui.session.content.boards[b.mission_id]
	if not b.heroes.has(ui.selected):ui.selected=str(b.heroes.keys()[0])
	body.add_theme_constant_override("separation",12)
	var objectives:=VBoxContainer.new();objectives.custom_minimum_size.x=210;body.add_child(objectives)
	small(ui,objectives,ui.I18n.t("quality.mission"),ui.GOLD)
	var objective_scroll:=ScrollContainer.new();objective_scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL;objective_scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;objectives.add_child(objective_scroll)
	var goals:=VBoxContainer.new();goals.size_flags_horizontal=Control.SIZE_EXPAND_FILL;goals.add_theme_constant_override("separation",12);objective_scroll.add_child(goals)
	for group: Array in ui.Full.groups(s,board):
		var names: Array[String]=[];var done: bool=false
		for id: String in group:
			if not b.objects.has(id):continue
			var target: Dictionary=b.objects[id]
			done=done or (target.completed and (not target.sustain_until_exit or target.hp>0))
			names.append(ui.object_name(id))
		var card:=PanelContainer.new();card.add_theme_stylebox_override("panel",ui.surface(ui.SURFACE,8));goals.add_child(card)
		var detail:=VBoxContainer.new();card.add_child(detail)
		small(ui,detail,ui.I18n.t("p3.done") if done else ui.I18n.t("p3.todo"),ui.TEAL if done else ui.GOLD)
		ui.label(detail," / ".join(names))
		for id: String in group:
			if not b.objects.has(id):continue
			var o: Dictionary=b.objects[id]
			if not o.completed and not o.lost:
				small(ui,detail,ui.I18n.t("quality.at_cell")%[int(o.cell[0])+1,int(o.cell[1])+1],ui.MUTED)
				var deadline: int=ui.Rules.Hazards.rescue_deadline(b,o)
				if deadline>0 and not o.stable:small(ui,detail,ui.I18n.t("difficulty.rescue_deadline")%deadline,ui.GOLD)
	var next: Dictionary=ui.current_guidance() if ui.guidance_enabled else {}
	if not next.is_empty():
		small(ui,goals,ui.I18n.t("quality.next_step"),ui.TEAL)
		small(ui,goals,ui.I18n.t("guide."+next.key),ui.INK)
		if not next.get("action","").is_empty() or next.has("actor"):
			var caption: String=ui.I18n.t("guide.switch")%ui.actor_name(next.actor) if next.has("actor") else ui.I18n.t("guide.preview")%ui.action_name(next.action)
			var suggestion: Button=ui.button(goals,caption,ui.preview_guidance);suggestion.add_theme_font_size_override("font_size",maxi(14,ui.font_size-4))
	ui.button(objectives,ui.I18n.t("p3.site_view"),ui.show_site).add_theme_font_size_override("font_size",16)
	ui.button(objectives,ui.I18n.t("intro.button"),func():ui.show_intro(false)).add_theme_font_size_override("font_size",16)

	var center:=VBoxContainer.new();center.size_flags_horizontal=Control.SIZE_EXPAND_FILL;body.add_child(center)
	var top:=HBoxContainer.new();center.add_child(top)
	small(ui,top,ui.I18n.t("ui.23cdebc8c9bf")%[b.round,b.limit],ui.GOLD)
	small(ui,top,ui.actor_name(ui.selected)+" · "+ui.action_name(ui.action),ui.TEAL).horizontal_alignment=HORIZONTAL_ALIGNMENT_RIGHT
	var map=ui.BoardView.new();map.name="TacticalMap";map.state=s;map.board=board;map.selected=ui.selected
	map.previous=ui.visual_previous;map.animation_started=ui.visual_started;map.feedback=ui.feedback_plan;map.actor_facings=ui.actor_facings;map.playback_seconds=ui.feedback_seconds
	map.hint_cell=next.get("cell",[]);map.size_flags_vertical=Control.SIZE_EXPAND_FILL;map.custom_minimum_size=Vector2(320,320)
	var cache_key: String="%s:%s:%s"%[hash(b),ui.selected,ui.action]
	if ui.reach_key!=cache_key:
		ui.reach_cache.clear();ui.reach_key=cache_key
		if ui.action=="move":
			for cell: Array in ui.Rules.reachable_cells(s,ui.selected):ui.reach_cache[str(cell)]=cell
	map.reachable=[] if ui.feedback_active() else ui.reach_cache.values()
	map.validate_hover=func(cell: Array):return ui.reach_cache.has(str(cell))
	map.cell_chosen.connect(ui.click_cell);center.add_child(map)
	small(ui,center,ui.I18n.t("quality.map_legend"),ui.MUTED)

	var panel:=PanelContainer.new();panel.custom_minimum_size.x=320 if ui.font_size<24 else 350;panel.add_theme_stylebox_override("panel",ui.surface(ui.SURFACE,10));body.add_child(panel)
	var right:=VBoxContainer.new();right.add_theme_constant_override("separation",8);panel.add_child(right)
	var crew_row:=HBoxContainer.new();right.add_child(crew_row)
	for hero: Dictionary in b.heroes.values():
		var card:=VBoxContainer.new();card.size_flags_horizontal=Control.SIZE_EXPAND_FILL;crew_row.add_child(card)
		if ui.Art.CharacterArt.has_actor(hero.id):
			var portrait=ui.Art.character(hero.id,"work","neutral",Vector2(48,52),true);card.add_child(portrait)
		var select: Button=ui.button(card,ui.actor_name(hero.id),func():ui.selected=hero.id;ui.action="move";ui.render())
		select.custom_minimum_size=Vector2(0,34);select.add_theme_font_size_override("font_size",maxi(14,ui.font_size-4))
		if ui.selected==hero.id:select.add_theme_stylebox_override("normal",ui.surface(Color("23493f"),6,ui.TEAL))
		small(ui,card,ui.I18n.t("quality.crew_numbers")%[hero.hp,hero.ap],ui.MUTED).horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER
	var selected: Dictionary=b.heroes[ui.selected]
	if selected.downed:small(ui,right,ui.I18n.t("ui.fb2c9b47365c"),ui.GOLD)
	elif selected.left:small(ui,right,ui.I18n.t("ui.4c0584645189"),ui.MUTED)
	elif selected.ap==0:small(ui,right,ui.I18n.t("quality.no_ap"),ui.GOLD)
	var tabs:=HBoxContainer.new();right.add_child(tabs)
	for item: Array in [["actions","ui.253fb75906c6"],["objectives","ui.5253040db864"],["cooperation","ui.19bf536853e2"]]:
		var tab: Button=ui.button(tabs,ui.I18n.t(item[1]),func():ui.panel_tab=item[0];ui.render());tab.custom_minimum_size.x=0;tab.size_flags_horizontal=Control.SIZE_EXPAND_FILL
		if ui.panel_tab==item[0]:tab.add_theme_stylebox_override("normal",ui.surface(Color("23493f"),6,ui.TEAL))
	var scroll:=ScrollContainer.new();scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL;scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;right.add_child(scroll)
	var contents:=VBoxContainer.new();contents.size_flags_horizontal=Control.SIZE_EXPAND_FILL;contents.add_theme_constant_override("separation",8);scroll.add_child(contents)
	match ui.panel_tab:
		"actions":ui.action_panel(contents)
		"cooperation":ui.cooperation_panel(contents)
		"objectives":
			for o: Dictionary in b.objects.values():
				var state_text: String=ui.I18n.t("ui.f28461bb49c8") if o.completed else (ui.I18n.t("p2.lost") if o.lost or o.has("unavailable_reason") else (ui.I18n.t("ui.44068ff6b2ee") if o.stable else ui.I18n.t("ui.999a459c3f3f")))
				if o.work>0 and not o.completed and not o.lost and not o.has("unavailable_reason"):state_text=ui.I18n.t("p2.work_progress")%[o.progress,o.work]
				if o.get("active",false) and not o.completed:state_text=ui.I18n.t("p3.timed_progress")%[int(o.get("timer",o.get("waypoint",0))),int(o.get("hold_rounds",o.get("waypoints",[]).size()-1))]
				ui.button(contents,ui.object_name(o.id)+" · "+state_text,func():ui.object_click(o.id))
				var deadline: int=ui.Rules.Hazards.rescue_deadline(b,o)
				if deadline>0 and not o.stable and not o.lost:small(ui,contents,ui.I18n.t("difficulty.rescue_deadline")%deadline,ui.GOLD)
			ui.label(contents,ui.I18n.t("ui.3ef5bf27c047")%b.environment.water_addition.round)
	for control: Node in contents.find_children("*","Button",true,false):
		control.add_theme_font_size_override("font_size",maxi(16,ui.font_size-2));control.custom_minimum_size.y=38
	var end: Button=ui.button(right,ui.I18n.t("ui.975778d99095"),func():ui.propose("end_round",{}));end.add_theme_stylebox_override("normal",ui.surface(Color("35524c"),8,ui.TEAL))
	var footer:=HBoxContainer.new();right.add_child(footer)
	ui.button(footer,ui.I18n.t("ui.926a50b98ece"),func():ui.propose("undo",{})).size_flags_horizontal=Control.SIZE_EXPAND_FILL
	ui.button(footer,ui.I18n.t("ui.f2adfafb5b50"),func():ui.propose("emergency_retreat",{"confirmed":true})).size_flags_horizontal=Control.SIZE_EXPAND_FILL
