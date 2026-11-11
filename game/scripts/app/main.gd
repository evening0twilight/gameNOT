extends Control
const Screens=preload("res://scripts/presentation/campaign_screens.gd")
const Crew=preload("res://scripts/domain/crew_journey.gd")
var title_screen: bool=true
var animation_rate: float=1.0
var reduced_motion: bool=false
var paused: bool=false
var conflict_notices: Array=[]
const Audio=preload("res://scripts/presentation/audio_controller.gd")
var sound: Node
var metrics: Node
const Product=preload("res://scripts/domain/product_systems.gd")
const Guidance=preload("res://scripts/presentation/guidance.gd")
var guidance_enabled: bool=true
var tool: String=""
var anchor_start: Array=[]
const Catalog = preload("res://scripts/infrastructure/content_catalog.gd")
const Session = preload("res://scripts/app/session.gd")
const I18n=preload("res://scripts/presentation/localization.gd")
const Full=preload("res://scripts/domain/full_campaign.gd")
const Chapter=preload("res://scripts/domain/chapter_one.gd")
const Stories=preload("res://scripts/domain/chapter_stories.gd")
var reading_scene: String=""
const Art=preload("res://scripts/presentation/visual_assets.gd")
const BoardView=preload("res://scripts/presentation/tactical_board.gd")
var panel_tab: String="actions"
var visual_previous: Dictionary={}
var visual_started: int=0
const Feedback=preload("res://scripts/presentation/action_feedback.gd")
var feedback_plan: Dictionary={}
var actor_facings: Dictionary={}
var feedback_elapsed: float=0.0
func feedback_seconds() -> float:return feedback_elapsed
func feedback_active() -> bool:return not feedback_plan.is_empty()
func _process(_delta: float) -> void:
	if feedback_active() and not paused:
		feedback_elapsed+=_delta*animation_rate
		if feedback_elapsed>=float(feedback_plan.duration):finish_feedback()
func finish_feedback() -> void:
	feedback_plan={};visual_previous={};sound.cancel_timeline();render()
	show_conflict_notice()
	show_next_welcome()

var welcome_queue: Array=[]
func show_next_welcome() -> void:
	if welcome_queue.is_empty() or feedback_active():return
	var id: String=welcome_queue.pop_front()
	Screens.introduction(self,id)

var reach_cache: Dictionary={}
var reach_key: String=""
var guide_key: int=0
var guide_cache: Dictionary={}
func current_guidance() -> Dictionary:
	var key: int=hash([session.state.battle,session.state.campaign.phase,session.state.full_campaign.route,selected])
	if guide_key!=key or guide_cache.is_empty():
		guide_cache=Guidance.next_step(session.state,session.content,selected);guide_key=key
	return guide_cache
const INK=Color("dce8e2")
const TEAL=Color("70d9c1")
const MUTED=Color("8ea9a8")
const SURFACE=Color("152b33")
const GOLD=Color("e8ca8a")
const Rules = preload("res://scripts/domain/campaign_rules.gd")
var session = Session.new()
var selected: String = "lin"
var action: String = "move"
var ability: String=""
var partner: String="xu"
var protocol: String="protected_work"
var specialty_mode: String="move"
var specialty_target: String=""
var message: String = I18n.t("ui.28efa9cc44f6")
var pending: Dictionary = {}
var inline_pending: bool=false
var detailed_preview: bool=false
var font_size: int = 20
var sequence: int = 0
var root: VBoxContainer
var confirmation_text: Label
var confirmation: ConfirmationDialog
func _ready() -> void:
	var acceptance: bool="--acceptance-test" in OS.get_cmdline_user_args()
	if acceptance and DisplayServer.get_name()!="headless":
		if DisplayServer.get_screen_count()<2 and OS.get_name()=="macOS":
			printerr("NATIVE_ACCEPTANCE: external display required on development host");get_tree().quit(2);return
		var external: int=(0 if DisplayServer.get_primary_screen()!=0 else 1) if DisplayServer.get_screen_count()>1 else DisplayServer.get_primary_screen()
		DisplayServer.window_set_current_screen(external)
		DisplayServer.window_set_position(DisplayServer.screen_get_position(external)+Vector2i(40,60))
	I18n.initialize()
	sound=Audio.new();add_child(sound)
	metrics=preload("res://scripts/presentation/runtime_metrics.gd").new();add_child(metrics)
	var presentation:=ConfigFile.new()
	if presentation.load("user://presentation018.cfg")==OK:
		animation_rate=clampf(float(presentation.get_value("feedback","rate",1.0)),.5,2.0);reduced_motion=bool(presentation.get_value("feedback","reduced",false))
	font_size=I18n.font_size
	var ui_theme := Theme.new()
	ui_theme.default_font=load("res://assets/fonts/noto_sans_cjk_sc_regular.otf")
	theme=ui_theme
	ui_theme.default_font_size=font_size
	ui_theme.set_color("font_color","Label",INK)
	ui_theme.set_color("font_color","Button",INK)
	ui_theme.set_stylebox("normal","Button",surface(Color("203c43"),8))
	ui_theme.set_stylebox("hover","Button",surface(Color("2d555a"),8))
	ui_theme.set_stylebox("pressed","Button",surface(Color("35685f"),8))
	ui_theme.set_stylebox("focus","Button",surface(Color(0,0,0,0),8,TEAL))
	ui_theme.set_stylebox("panel","PopupMenu",surface(SURFACE,8))
	ui_theme.set_stylebox("panel","AcceptDialog",surface(SURFACE,12,Color("4b6768")))
	ui_theme.set_color("title_color","Window",TEAL)
	ui_theme.set_font("title_font","Window",ui_theme.default_font)
	ui_theme.set_font_size("title_font_size","Window",18)
	var content := Catalog.load_catalog()
	if not content.ok:
		message=I18n.t("ui.9d5bf0059d71")+error_text(content.error_code)
		return
	session.content=content
	session.path="user://saves/p4/autosave.json"
	var active_slot:=ConfigFile.new()
	if active_slot.load("user://p4_active_slot.cfg")==OK:
		var active: String=str(active_slot.get_value("campaign","path",session.path))
		if active.begins_with("user://saves/p4/") and active.ends_with("/autosave.json") and not active.contains(".."):session.path=active
	if DisplayServer.get_name()=="headless" or acceptance or "--isolated-ui-review" in OS.get_cmdline_user_args():session.path="user://tests/p4-ui-%d/autosave.json" % Time.get_ticks_usec()
	var loaded: Dictionary=session.load_game()
	if not loaded.ok:
		session.state=Rules.begin_campaign(content,"title-preview")
		if loaded.error_code!="missing_save":message=I18n.t("baseline018.213b98e39610")+error_text(loaded.error_code)
	if acceptance:title_screen=false
	confirmation=ConfirmationDialog.new()
	confirmation.title=I18n.t("ui.fa9622b77529")
	confirmation.min_size=Vector2i(580,260)
	confirmation.ok_button_text=I18n.t("ui.68a35e224268")
	confirmation.cancel_button_text=I18n.t("ui.2cd0f3be8738")
	confirmation.confirmed.connect(commit_pending)
	add_child(confirmation)
	confirmation.get_label().hide()
	var preview_scroll:=ScrollContainer.new();preview_scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	preview_scroll.offset_left=16;preview_scroll.offset_top=16;preview_scroll.offset_right=-16;preview_scroll.offset_bottom=-66
	preview_scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;confirmation.add_child(preview_scroll)
	confirmation_text=Label.new();confirmation_text.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;confirmation_text.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	preview_scroll.add_child(confirmation_text)
	render()
	print("PROJECT_BOOT_OK: baseline 0.18 campaign UI")
	if acceptance:
		var runner=preload("res://scripts/app/native_acceptance.gd").new();add_child(runner);runner.call_deferred("run",self)

func button(parent: Node,label: String,callback: Callable) -> Button:
	var b := Button.new()
	b.text=label
	for mapping: Array in [["ui.975778d99095","end_round"],["ui.926a50b98ece","undo"],["baseline018.00768fb3f70c","relations"],["p3.journal","journal"],["baseline018.d04bb3ddf1b7","coordinated_pull"],["ui.029b72a67ea6","protected_work"],["ui.a4b81cbe097b","relay_carry"],["ui.81bac7b6b054","mutual_cover"]]:
		if label==I18n.t(mapping[0]):b.icon=Art.icon(mapping[1]);break
	b.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	b.custom_minimum_size=Vector2(170 if parent is FlowContainer else 100,42)
	b.add_theme_font_size_override("font_size",font_size)
	b.pressed.connect(func():sound.play("ui_focus"))
	b.pressed.connect(callback)
	parent.add_child(b)
	return b
func label(parent: Node,text: String) -> Label:
	var l := Label.new()
	l.text=text
	l.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	l.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	l.custom_minimum_size.x=0
	l.add_theme_font_size_override("font_size",font_size)
	parent.add_child(l)
	return l
func surface(color: Color,radius: int,border: Color=Color(0,0,0,0)) -> StyleBoxFlat:
	var style:=StyleBoxFlat.new()
	style.bg_color=color
	style.set_corner_radius_all(radius)
	style.content_margin_left=12;style.content_margin_right=12
	style.content_margin_top=8;style.content_margin_bottom=8
	style.border_color=border;style.set_border_width_all(1)
	return style
func render() -> void:
	if inline_pending and (session.state.campaign.phase!="battle" or pending.get("actor_id")!=selected or pending.get("kind")!=action or (action=="use_tool" and pending.payload.get("item")!=tool)):
		inline_pending=false;pending={}
	if root!=null:
		remove_child(root);root.queue_free()
	root=VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.offset_left=24;root.offset_top=12;root.offset_right=-24;root.offset_bottom=-12
	root.add_theme_constant_override("separation",8)
	add_child(root)
	var s: Dictionary=session.state
	if s.campaign.phase=="battle" and not s.battle.heroes.has(selected):selected=s.battle.heroes.keys()[0]
	sound.ambience(music_context())
	var header:=HBoxContainer.new();root.add_child(header)
	var title:=VBoxContainer.new();title.size_flags_horizontal=Control.SIZE_EXPAND_FILL;header.add_child(title)
	var heading:=label(title,I18n.t("ui.ea0219b09f08"));heading.add_theme_font_size_override("font_size",28);heading.add_theme_color_override("font_color",TEAL)
	var subtitle:=label(title,I18n.t("ui.6b73f6729147") % [s.campaign.day,I18n.content("boards",s.battle.mission_id,"title",session.content.boards[s.battle.mission_id].title)])
	subtitle.add_theme_color_override("font_color",MUTED);subtitle.add_theme_font_size_override("font_size",16)
	for currency: String in ["credits","supplies","parts"]:
		var balance:=HBoxContainer.new();header.add_child(balance)
		var glyph:=TextureRect.new();glyph.texture=Art.icon(currency);glyph.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;glyph.custom_minimum_size=Vector2(24,24);glyph.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;balance.add_child(glyph)
		var value_label:=label(balance,I18n.t("journey.currency."+currency)%int(s.inventory[currency]));value_label.autowrap_mode=TextServer.AUTOWRAP_OFF
	var menu:=MenuButton.new();menu.text=I18n.t("ui.6ca5a77d24c4");menu.add_theme_font_size_override("font_size",font_size);header.add_child(menu)
	for item: String in [I18n.t("ui.5ea11db9fc7f"),I18n.t("ui.a04cc6756dec"),I18n.t("ui.1ae486278078"),I18n.t("ui.106ffa675ea5"),I18n.t("ui.f5bb41e345b5"),I18n.t("ui.dbc0fe120d31")]:menu.get_popup().add_item(item)
	menu.get_popup().add_item(I18n.t("p3.new_campaign"))
	menu.get_popup().add_item(I18n.t("p3.switch_campaign"))
	menu.get_popup().add_item(I18n.t("p4.help"))
	menu.get_popup().add_item(I18n.t("p4.toggle_guidance"))
	menu.get_popup().add_item(I18n.t("p4.audio"))
	menu.get_popup().add_item(I18n.t("p4.diagnostics"))
	menu.get_popup().add_item(I18n.t("baseline018.df0379d3d6af"))
	menu.get_popup().add_item(I18n.t("baseline018.40327e5a6e68"))
	menu.get_popup().id_pressed.connect(settings_action)
	var separator:=HSeparator.new();root.add_child(separator)
	var body:=HBoxContainer.new();body.size_flags_vertical=Control.SIZE_EXPAND_FILL;body.add_theme_constant_override("separation",20);root.add_child(body)
	if title_screen:Screens.title(self,body)
	elif s.campaign.phase=="briefing":Screens.briefing(self,body)
	elif s.campaign.phase=="battle" or feedback_active():render_battle(body)
	else:
		var scroll:=ScrollContainer.new();scroll.size_flags_horizontal=Control.SIZE_EXPAND_FILL;scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;body.add_child(scroll)
		var contents:=HBoxContainer.new();contents.size_flags_horizontal=Control.SIZE_EXPAND_FILL;scroll.add_child(contents);render_camp(contents)
	if feedback_active():
		menu.disabled=true
		for control: Node in body.find_children("*","Button",true,false):control.disabled=true
	var notice:=PanelContainer.new();notice.custom_minimum_size.y=56;notice.add_theme_stylebox_override("panel",surface(SURFACE,8));root.add_child(notice)
	var status_row:=HBoxContainer.new();notice.add_child(status_row)
	var status_message: String=message
	if message==I18n.t("ui.28efa9cc44f6") and s.campaign.phase!="battle":status_message=I18n.t("journey.status_briefing" if s.campaign.phase=="briefing" else "journey.status_camp")
	if s.chapter_one.finished:status_message=I18n.t("journey.status_ending")
	if title_screen:status_message=I18n.t("journey.status_title")
	var status:=label(status_row,status_message);status.add_theme_font_size_override("font_size",16);status.max_lines_visible=3
	if feedback_active():
		button(status_row,I18n.t("baseline018.8d12fc0d4eb2"),pause_menu)
		button(status_row,I18n.t("feedback.skip"),finish_feedback).add_theme_font_size_override("font_size",16)
	if inline_pending:
		button(status_row,I18n.t("baseline018.b6c837a36a6e"),func():detailed_preview=true;propose(pending.kind,pending.payload);detailed_preview=false)
		button(status_row,I18n.t("p4.confirm_action"),commit_pending).add_theme_font_size_override("font_size",16)
		button(status_row,I18n.t("p4.cancel_action"),cancel_selection).add_theme_font_size_override("font_size",16)
	confirmation.title=I18n.t("ui.db51313720b4");confirmation.ok_button_text=I18n.t("ui.68a35e224268");confirmation.cancel_button_text=I18n.t("ui.2cd0f3be8738")
func settings_action(index: int) -> void:
	if index==12:title_screen=true;render();return
	if index==13:pause_menu();return
	match index:
		0:save_manual()
		1:load_manual()
		2:recover()
		3:
			font_size=16 if font_size==24 else font_size+4
			I18n.font_size=font_size;I18n.save_preferences();render()
		4:
			I18n.locale="en_XA" if I18n.locale=="zh_CN" else "zh_CN"
			I18n.save_preferences();message=I18n.t("ui.da10edbf29b7");render()
		5:get_tree().quit()
		6:new_campaign()
		7:campaign_picker()
		8:show_help()
		9:guidance_enabled=not guidance_enabled;render()
		10:audio_settings()
		11:
			var path: String=metrics.export_report()
			message=I18n.t("p4.diagnostics_saved") % path if not path.is_empty() else I18n.t("error.save") % error_text("save_io_failed")
			render()
func render_battle(body: HBoxContainer) -> void:
	var s: Dictionary=session.state
	if feedback_active() and s.campaign.phase!="battle":s=s.duplicate(true);s.campaign.phase="battle"
	var b: Dictionary=s.battle
	var board: Dictionary=session.content.boards[b.mission_id]
	if not b.heroes.has(selected):selected=str(b.heroes.keys()[0])
	var left:=VBoxContainer.new();left.size_flags_horizontal=Control.SIZE_EXPAND_FILL;body.add_child(left)
	label(left,objective_summary()).add_theme_color_override("font_color",TEAL)
	var title:=HBoxContainer.new();left.add_child(title)
	button(title,I18n.t("p3.site_view"),show_site).custom_minimum_size.x=140
	button(title,I18n.t("intro.button"),func():show_intro(false)).custom_minimum_size.x=100
	label(title,I18n.t("ui.b3033f3709e4")).add_theme_color_override("font_color",GOLD)
	label(title,I18n.t("ui.23cdebc8c9bf") % [b.round,b.limit])
	for control: Control in title.get_children():control.add_theme_font_size_override("font_size",16)
	var map=BoardView.new();map.state=s;map.board=board;map.selected=selected
	map.previous=visual_previous;map.animation_started=visual_started;map.feedback=feedback_plan;map.actor_facings=actor_facings;map.playback_seconds=feedback_seconds
	var next: Dictionary=current_guidance() if guidance_enabled else {}
	map.hint_cell=next.get("cell",[])
	map.size_flags_vertical=Control.SIZE_EXPAND_FILL;map.custom_minimum_size=Vector2(300,280)
	var cache_key: String="%s:%s:%s" % [hash(s.battle),selected,action]
	if reach_key!=cache_key:
		reach_cache.clear();reach_key=cache_key
		if action=="move":
			for cell: Array in Rules.reachable_cells(s,selected):reach_cache[str(cell)]=cell
	map.reachable=[] if feedback_active() else reach_cache.values()
	map.validate_hover=func(cell: Array):return reach_cache.has(str(cell))
	map.cell_chosen.connect(click_cell);left.add_child(map)
	if not next.is_empty():
		var panel:=PanelContainer.new();panel.add_theme_stylebox_override("panel",surface(SURFACE,8));left.add_child(panel)
		var guidance_row:=HBoxContainer.new();panel.add_child(guidance_row)
		var hint_text:=label(guidance_row,I18n.t("guide."+next.key));hint_text.add_theme_font_size_override("font_size",16)
		if not next.get("action","").is_empty() or next.has("actor"):
			var caption: String=I18n.t("guide.switch") % actor_name(next.actor) if next.has("actor") else I18n.t("guide.preview") % action_name(next.action)
			var suggestion:=button(guidance_row,caption,preview_guidance);suggestion.custom_minimum_size.x=132;suggestion.add_theme_font_size_override("font_size",16)

	label(left,I18n.t("ui.4697785e420d")).add_theme_font_size_override("font_size",14)
	var right_panel:=PanelContainer.new();right_panel.custom_minimum_size.x=390;right_panel.add_theme_stylebox_override("panel",surface(SURFACE,12));body.add_child(right_panel)
	var right:=VBoxContainer.new();right.add_theme_constant_override("separation",8);right_panel.add_child(right)
	for h: Dictionary in b.heroes.values():
		var text: String=I18n.t("ui.de04e409bc3a") % [actor_name(h.id),h.hp,h.ap]
		if h.downed:text+=I18n.t("ui.fb2c9b47365c")
		elif h.left:text+=I18n.t("ui.4c0584645189")
		var row:=HBoxContainer.new();row.add_theme_constant_override("separation",10);right.add_child(row)
		if h.id in ["lin","xu","su","chen","ye","he","mo","jiang"]:
			var portrait=Art.picture(Art.portrait(h.id),Vector2(48,60));row.add_child(portrait)
		var crew:=button(row,text,func():selected=h.id;action="move";render());crew.size_flags_horizontal=Control.SIZE_EXPAND_FILL
		crew.add_theme_font_size_override("font_size",16)
		if selected==h.id:crew.add_theme_stylebox_override("normal",surface(Color("23493f"),8,TEAL))
	var tabs:=HBoxContainer.new();right.add_child(tabs)
	for item: Array in [["actions",I18n.t("ui.253fb75906c6")],["objectives",I18n.t("ui.5253040db864")],["cooperation",I18n.t("ui.19bf536853e2")]]:
		var tab:=button(tabs,item[1],func():panel_tab=item[0];render());tab.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	var scroll:=ScrollContainer.new();scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL;scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;right.add_child(scroll)
	var contents:=VBoxContainer.new();contents.size_flags_horizontal=Control.SIZE_EXPAND_FILL;contents.add_theme_constant_override("separation",8);scroll.add_child(contents)
	match panel_tab:
		"actions":action_panel(contents)
		"objectives":
			for o: Dictionary in b.objects.values():
				var state_text: String=I18n.t("ui.f28461bb49c8") if o.completed else (I18n.t("p2.lost") if o.lost or o.has("unavailable_reason") else (I18n.t("ui.44068ff6b2ee") if o.stable else I18n.t("ui.999a459c3f3f")))
				if o.work>0 and not o.completed and not o.lost and not o.has("unavailable_reason"):state_text=I18n.t("p2.work_progress") % [o.progress,o.work]
				if o.get("active",false) and not o.completed:state_text=I18n.t("p3.timed_progress") % [int(o.get("timer",o.get("waypoint",0))),int(o.get("hold_rounds",o.get("waypoints",[]).size()-1))]
				var item:=button(contents,"%s · %s" % [object_name(o.id),state_text],func():object_click(o.id));item.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
				var deadline: int=Rules.Hazards.rescue_deadline(b,o)
				if deadline>0 and not o.stable and not o.lost:label(contents,I18n.t("difficulty.rescue_deadline") % deadline).add_theme_font_size_override("font_size",16)
			label(contents,I18n.t("ui.3ef5bf27c047") % b.environment.water_addition.round)
		"cooperation":cooperation_panel(contents)
	button(right,I18n.t("ui.975778d99095"),func():propose("end_round",{}))
	var footer:=HBoxContainer.new();right.add_child(footer)
	button(footer,I18n.t("ui.926a50b98ece"),func():propose("undo",{})).size_flags_horizontal=Control.SIZE_EXPAND_FILL
	button(footer,I18n.t("ui.f2adfafb5b50"),func():propose("emergency_retreat",{"confirmed":true})).size_flags_horizontal=Control.SIZE_EXPAND_FILL
func action_panel(box: VBoxContainer) -> void:
	Screens.operations(self,box)
	var s: Dictionary=session.state
	var grid:=GridContainer.new();grid.columns=2;box.add_child(grid)
	for kind: String in ["move","attack","push","stabilize","pickup","interact","drop","extract","leave_site"]:
		var b:=button(grid,action_name(kind),func():action=kind;message=I18n.t("ui.5f8e4339d044") % action_name(kind);render();if kind in ["drop","extract","leave_site"]:propose(kind,{}))
		b.size_flags_horizontal=Control.SIZE_EXPAND_FILL;b.icon=Art.icon(kind)
		if action==kind:b.add_theme_stylebox_override("normal",surface(Color("34594f"),8,TEAL))
	render_tools(box)
	if s.actors.has(selected):
		var lv: int=Rules.Specialties.level(int(s.actors[selected].xp))
		label(box,I18n.t("ui.d18936001d7a")).add_theme_color_override("font_color",GOLD)
		for spec: Dictionary in session.content.domains.abilities:
			if spec.actor==selected and spec.level<=lv and spec.production_status=="active":
				if spec.id=="he_3":label(box,I18n.content("abilities",spec.id,"effect",spec.effect));continue
				var title: String=I18n.content("abilities",spec.id,"name",spec.name)
				var b:=button(box,I18n.t("ui.f4012a3898f3") % [title,int(spec.charges_per_mission)-int(s.battle.ability_uses.get(spec.id,0))],func():action="specialty";ability=spec.id;specialty_mode="move";specialty_target="";message=I18n.content("abilities",spec.id,"effect",spec.effect);render())
				b.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;b.icon=Art.icon(spec.id)
		if selected=="su" and lv>=5:button(box,I18n.t("ui.bf8acf052f64"),func():action="specialty";ability="su_3";specialty_mode="ap";message=I18n.t("ui.7e050b01a60e");render())
func cooperation_panel(box: VBoxContainer) -> void:
	button(box,I18n.t("baseline018.d04bb3ddf1b7"),func():action="protocol";protocol="coordinated_pull";specialty_target="";message=I18n.t("baseline018.07d244dd0218");render())
	button(box,I18n.t("baseline018.12bb628f0efc"),func():propose("declare_priority",{"priority":"people"}))
	button(box,I18n.t("baseline018.a178bcfbaf13"),func():propose("declare_priority",{"priority":"cargo"}))
	var partners:=OptionButton.new();box.add_child(partners)
	for id: String in session.state.battle.heroes:
		if id!=selected:partners.add_item(actor_name(id));partners.set_item_metadata(partners.item_count-1,id)
	var found: int=-1
	for i: int in range(partners.item_count):
		if str(partners.get_item_metadata(i))==partner:found=i
	if found<0:found=0;partner=str(partners.get_item_metadata(0))
	partners.select(found);partners.item_selected.connect(func(i: int):partner=str(partners.get_item_metadata(i)))
	button(box,I18n.t("ui.029b72a67ea6"),func():action="protocol";protocol="protected_work";message=I18n.t("ui.f54c30a42f40");render())
	button(box,I18n.t("ui.a4b81cbe097b"),func():action="protocol";protocol="relay_carry";message=I18n.t("ui.1fea80ddf5c0");render())
	button(box,I18n.t("ui.81bac7b6b054"),func():propose("protocol",{"protocol":"mutual_cover","partner":partner,"consent":true}))
	button(box,I18n.t("p4.action.prepare_safety"),func():
		var choice:=modal(I18n.t("baseline018.ccba6eef4a11"))
		for kind: String in ["protected_work","mutual_cover"]:button(choice.box,I18n.t("baseline018.029b72a67ea6") if kind=="protected_work" else I18n.t("baseline018.81bac7b6b054"),func():choice.window.queue_free();propose("prepare_safety",{"target":partner,"protocol":kind})))
	button(box,I18n.t("ui.75bc5d3f648d"),func():propose("authorize",{}))
	button(box,I18n.t("ui.582cdf55a501") % (session.state.battle.limit-2),func():propose("promise_retreat",{}))
func object_name(id: String) -> String:
	var o: Dictionary=session.state.battle.objects.get(id,{})
	if o.has("crew_id"):return I18n.t("object.crew") % actor_name(o.crew_id)
	return I18n.content("objects",session.state.battle.mission_id+"."+id,"label",str(o.get("label","")))
func actor_name(id: String) -> String:
	return I18n.content("characters",id,"name",session.state.actors[id].name) if session.state.actors.has(id) else I18n.t("ui.5c6114712d44") % id.right(1)
func click_cell(cell: Array) -> void:
	if feedback_active():return
	if action=="drop":propose("drop",{"cell":cell});return
	if action=="protocol" and protocol=="coordinated_pull":
		if specialty_target.is_empty():
			for enemy: Dictionary in session.state.battle.enemies.values():
				if Rules.same(enemy.cell,cell):specialty_target=enemy.id;message=I18n.t("baseline018.01156b373c3b");render();return
		else:propose("protocol",{"protocol":protocol,"target":specialty_target,"partner":partner,"cell":cell,"consent":true});return
		return
	var candidates: Array=[]
	if action in ["stabilize","pickup","interact"] or (action=="protocol" and protocol=="protected_work") or (action=="use_tool" and tool in ["crowbar","scanner"]):
		for object: Dictionary in session.state.battle.objects.values():
			if Rules.same(object.cell,cell) and not object.lost and not object.delivered:candidates.append(object.id)
		if candidates.size()>1:
			var chooser:=modal(I18n.t("baseline018.56ce9faa674f"))
			for id: String in candidates:button(chooser.box,object_name(id)+" · "+id,func():chooser.window.queue_free();choose_object(id))
			return
	if action=="cross_anchor":propose(action,{"cell":cell});return
	if action=="use_tool":
		if tool in ["shield","insulation"]:propose(action,{"item":tool,"cell":cell});return
		if tool=="winch":
			if anchor_start.is_empty():anchor_start=cell;message=I18n.t("p4.anchor_other");render();return
			propose(action,{"item":tool,"cell":anchor_start,"other":cell});anchor_start=[];return
		var collection: Dictionary=session.state.battle.heroes if tool=="medkit" else session.state.battle.objects
		for target: Dictionary in collection.values():
			if Rules.same(target.cell,cell):propose(action,{"item":tool,"target":target.id});return
		message=I18n.t("p4.tool_target");render();return
	if action=="move":
		for hero: Dictionary in session.state.battle.heroes.values():
			if not hero.left and Rules.same(hero.cell,cell):selected=hero.id;render();return
	if action=="protocol":
		var payload: Dictionary={"protocol":protocol,"partner":partner,"cell":cell,"consent":true}
		if protocol=="protected_work":
			for object: Dictionary in session.state.battle.objects.values():
				if Rules.same(object.cell,cell):payload.target=object.id;break
		propose("protocol",payload)
		return
	if action=="specialty":
		if ability in ["xu_1","ye_3","he_1"] or (ability in ["lin_3","mo_3"] and not specialty_target.is_empty()):
			propose("specialty",{"ability":ability,"cell":cell,"target":specialty_target,"consent":true})
			return
		var targets: Array=[]
		for collection: Dictionary in [session.state.battle.objects,session.state.battle.enemies,session.state.battle.heroes]:
			for target: Dictionary in collection.values():
				if Rules.same(target.cell,cell):targets.append(target.id)
		if targets.size()>1:
			var chooser:=modal(I18n.t("baseline018.0a5b6bee9e4b"))
			for id: String in targets:button(chooser.box,object_name(id) if session.state.battle.objects.has(id) else (actor_name(id) if session.state.battle.heroes.has(id) else id),func():chooser.window.queue_free();specialty_click(id))
		elif targets.size()==1:specialty_click(targets[0])
		return
	if action=="move": propose(action,{"cell":cell}); return
	var b: Dictionary = session.state.battle
	for e: Dictionary in b.enemies.values():
		if action in ["attack","push"] and Rules.same(e.cell,cell): propose(action,{"target":e.id});return
	for o: Dictionary in b.objects.values():
		if Rules.same(o.cell,cell): propose(action,{"target":o.id});return
	message=I18n.t("ui.7277f58fcf6d")
	render()
func render_camp(body: HBoxContainer) -> void:
	var s: Dictionary=session.state
	var box:=VBoxContainer.new();box.size_flags_horizontal=Control.SIZE_EXPAND_FILL;box.add_theme_constant_override("separation",16);body.add_child(box)
	if s.chapter_one.finished:
		render_ending(box)
		return
	Screens.recruits(self,box)
	var nav:=HFlowContainer.new();box.add_child(nav)
	button(nav,I18n.t("baseline018.b2bc2ee20311"),func():Screens.roster_page(self))
	button(nav,I18n.t("journey.city_button"),func():Screens.city(self))
	button(nav,I18n.t("baseline018.00768fb3f70c"),func():Screens.relationships(self))
	var banner:=HBoxContainer.new();banner.add_theme_constant_override("separation",16);box.add_child(banner)
	var atmosphere=Art.picture(Art.narrative("office"),Vector2(380,120 if s.campaign.phase=="camp" else 200));atmosphere.size_flags_horizontal=Control.SIZE_EXPAND_FILL;banner.add_child(atmosphere)
	var summary:=PanelContainer.new();summary.add_theme_stylebox_override("panel",surface(SURFACE,12));summary.size_flags_horizontal=Control.SIZE_EXPAND_FILL;banner.add_child(summary)
	var overview:=VBoxContainer.new();summary.add_child(overview)
	label(overview,I18n.t("camp.title")).add_theme_color_override("font_color",TEAL)
	label(overview,risk_text(s) if s.campaign.phase=="settlement" else risk_text(s).split("\n")[0])
	var result: Dictionary=s.campaign.last_result
	label(overview,I18n.t("camp.summary") % resource_text(result.reward))
	for entry: Dictionary in (result.get("reward_rows",[]) if s.campaign.phase=="settlement" else []):label(overview,entry.reason+"："+resource_text(entry.resources))
	for id: String in (result.get("xp_receipts",{}).keys() if s.campaign.phase=="settlement" else []):
		var growth: Dictionary=result.xp_receipts[id]
		label(overview,actor_name(id)+I18n.t("baseline018.aa68ce525b6c")%[growth.before,growth.after,{"main":I18n.t("baseline018.11ac606f3fa7"),"side":I18n.t("baseline018.d9df006540bb"),"support":I18n.t("baseline018.9588f74237f4")}.get(growth.source,growth.source)])
	var facts:=HFlowContainer.new();overview.add_child(facts)
	for id: String in (result.facts.keys() if s.campaign.phase=="settlement" else []):
		var fact:=Label.new();fact.text="%s · %s   " % [object_name(id),{"saved":I18n.t("ui.1fb12e48bde3"),"completed":I18n.t("ui.f28461bb49c8"),"lost":I18n.t("ui.c9cc5aa759c6"),"unresolved":I18n.t("ui.6707de42c29d")}.get(result.facts[id],I18n.t("event.unknown"))];facts.add_child(fact)
	if s.campaign.phase=="settlement":
		if s.chapter_one.finished:
			render_ending(box)
			return
		for entry: Dictionary in session.content.domains.scripts.community:
			if entry.source!=s.battle.mission_id:continue
			label(overview,I18n.content("scenes",entry.id,"variants."+result.outcome,entry.variants[result.outcome]))
			var flag: String="community."+entry.source+".public"
			if s.chapter_one.flags.has(flag):
				var choice: String="publish" if s.chapter_one.flags[flag] else "archive"
				label(overview,story_lines(entry.id,"choices."+choice,entry.choices[choice]))
			else:
				for choice: String in ["publish","archive"]:
					button(overview,I18n.t("p2.community_"+choice),func():propose("community_report",{"choice":choice}))
		Screens.appraisal_log(self,overview)
		for side: String in Chapter.side_available(s,session.content):
			button(overview,I18n.t("p2.side") % I18n.content("boards",side,"title",session.content.boards[side].title),func():prepare_mission(side,true))
		for side: String in Chapter.side_available(s,session.content):button(overview,I18n.t("baseline018.bc5141d3c6cc")+session.content.boards[side].title,func():propose("decline_side",{"mission":side}))
		button(overview,I18n.t("ui.6de354f5f7cd"),func():propose("enter_camp",{}))
		return
	label(box,I18n.t("ui.10a3c2a27fcc") % [s.campaign.projects,s.campaign.talked.size()]).add_theme_color_override("font_color",GOLD)
	var projects:=HFlowContainer.new();box.add_child(projects)
	for kind: String in ["train","treat","rest"]:button(projects,I18n.t("p2.group") % action_name(kind),func():group_project(kind))
	button(projects,I18n.t("p2.stories"),func():var choices: Dictionary=modal(I18n.t("p2.stories"));render_story_list(choices.box))
	if s.chapter_one.main_completed<24:
		button(box,I18n.t("p2.prepare_next"),show_night_review)
	else:
		button(box,I18n.t("p2.complete"),func():propose("next_mission",{})).disabled=s.chapter_one.finished
		chapter_report(box)
	button(box,I18n.t("baseline018.e8282617ef13"),plan_next_roster)
	button(box,I18n.t("p4.equipment_facilities"),show_workshop)
	Screens.operations(self,box)
	button(box,I18n.t("journey.reactions"),func():var report: Dictionary=modal(I18n.t("journey.reactions"));Screens.appraisal_log(self,report.box))
	render_campaign_options(box)
	render_mentors(box)
	button(box,I18n.t("p4.history"),show_history_repair)

	var cards:=GridContainer.new();cards.columns=3 if size.x>=1100 else 1;cards.add_theme_constant_override("h_separation",16);cards.add_theme_constant_override("v_separation",16);box.add_child(cards)
	for a: Dictionary in s.actors.values():
		if not Crew.joined(s,a.id):continue
		if s.product.withdrawn.has(a.id):label(box,I18n.t("p4.withdrawn") % actor_name(a.id));continue
		var card:=PanelContainer.new();card.size_flags_horizontal=Control.SIZE_EXPAND_FILL;card.add_theme_stylebox_override("panel",surface(SURFACE,12));cards.add_child(card)
		var details:=VBoxContainer.new();details.add_theme_constant_override("separation",10);card.add_child(details)
		if a.id in ["lin","xu","su","chen","ye","he","mo","jiang"]:
			var portrait=Art.picture(Art.outfit(a.id,"camp"),Vector2(0,175));portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;details.add_child(portrait)
		label(details,actor_name(a.id)).add_theme_color_override("font_color",TEAL)
		label(details,I18n.t("role."+a.id)).add_theme_color_override("font_color",MUTED)
		label(details,I18n.t("camp.stats") % [Rules.Specialties.level(int(a.xp)),a.fatigue,a.ready_day])
		var row:=HFlowContainer.new();details.add_child(row)
		button(row,action_name("train"),func():selected=a.id;propose("train",{})).tooltip_text=I18n.t("ui.47bab1cfd683")
		button(row,action_name("treat"),func():selected=a.id;propose("treat",{})).tooltip_text=I18n.t("ui.a4209ed05035")
		button(row,I18n.t("ui.57173daf8f5a"),func():selected=a.id;propose("rest",{}))
		if not s.social.has(a.id+">leader"):continue
		var relation: Dictionary=s.social[a.id+">leader"]
		label(details,I18n.t("camp.relationship") % [relation.trust,I18n.t("band."+relation.band)])
		var trust:=ProgressBar.new();trust.min_value=0;trust.max_value=100;trust.value=relation.trust;trust.show_percentage=false;trust.custom_minimum_size.y=6
		trust.add_theme_stylebox_override("background",surface(Color("0d1c24"),3));trust.add_theme_stylebox_override("fill",surface(TEAL,3));details.add_child(trust)
		var social:=HFlowContainer.new();details.add_child(social)
		for target: String in ["lin","xu","su","chen","ye","he","mo","jiang"]:
			if target!=a.id and Crew.joined(s,target):button(social,I18n.t("ui.281ebdc87350") % actor_name(target),func():selected=a.id;propose("short_talk",{"target":target}))
		var choices:=HFlowContainer.new();details.add_child(choices)
		button(choices,I18n.t("camp.work"),func():selected=a.id;propose("tendency",{"choice":"work"}))
		button(choices,I18n.t("camp.move"),func():selected=a.id;propose("tendency",{"choice":"move"}))
		for memory: Dictionary in relation.memories:
			label(details,I18n.t("camp.memory") % [Rules.Social.Legacy.memory_value(memory,s.campaign.day),memory.stage])
			if memory.stage==0:button(details,I18n.t("camp.ack"),func():selected=a.id;propose("acknowledge",{"event":memory.id}))
		button(details,I18n.t("baseline018.7bb112c825a0"),func():Screens.relationships(self,a.id,"xu" if a.id=="lin" else "lin"))
	label(box,I18n.t("camp.log")).add_theme_color_override("font_color",GOLD)
	for e: Dictionary in s.receipts.slice(maxi(0,s.receipts.size()-6)):label(box,action_name(e.kind))
func propose(kind: String,payload: Dictionary) -> void:
	if feedback_active():return
	sequence+=1
	if guidance_enabled:
		var hint: Dictionary=Guidance.card(session.state,session.content)
		if not hint.is_empty():payload=payload.duplicate(true);payload.tutorial_card=hint
	var repeated: bool=inline_pending and pending.get("kind")==kind and pending.get("expected_revision")==session.state.revision and session.store.canonical(pending.get("payload",{}))==session.store.canonical(payload)
	inline_pending=false
	pending={"command_id":"ui-%d-%d-%d" % [Time.get_ticks_usec(),session.state.revision,sequence],"expected_revision":session.state.revision,"kind":kind,"actor_id":selected,"payload":payload,"root_decision_id":"decision-%d" % sequence}
	var preview: Dictionary = session.preview(pending)
	if not preview.ok:
		message=I18n.t("error.action") % error_text(preview.error_code)
		sound.play("ui_error");render()
		if preview.error_code=="relationship_safeguard_required":
			var explanation:=modal(I18n.t("baseline018.aa27861f73ea"))
			for row: String in cooperation_details(payload):label(explanation.box,row)
			button(explanation.box,I18n.t("baseline018.03622be88c1d"),explanation.window.queue_free)
		return
	if kind=="undo":commit_pending();return
	if not detailed_preview and kind in ["move","attack","push","stabilize","pickup","drop","extract","wait","use_tool","cross_anchor"] and preview.next_state.campaign.phase==session.state.campaign.phase and preview.next_state.full_campaign.contracts==session.state.full_campaign.contracts:
		if repeated:commit_pending();return
		inline_pending=true;message=I18n.t("p4.inline_preview") % [action_name(kind),preview.costs.ap]+" · "+(object_name(str(payload.target)) if payload.has("target") and session.state.battle.objects.has(str(payload.target)) else str(payload.get("cell",payload.get("target",""))))+I18n.t("baseline018.c0eaab529348")+actor_name(selected);render();return
	confirmation_text.text=I18n.t("ui.32942064f5c9") % [action_name(kind),preview.costs.ap,resource_text(preview.costs.resources),risk_text(preview.next_state) if kind in ["emergency_retreat","end_round","leave_site"] else I18n.t("ui.dcb6036882a9")]
	var changes: Array[String]=[]
	changes.append(I18n.t("baseline018.0c7188e33d47")+actor_name(selected)+(I18n.t("baseline018.659950576da9")+actor_name(str(payload.partner)) if payload.has("partner") else ""))
	if payload.has("target"):changes.append(I18n.t("baseline018.4d2d25a2888d")+(object_name(str(payload.target)) if session.state.battle.objects.has(str(payload.target)) else str(payload.target))+" ["+str(payload.target)+"]")
	if payload.has("cell"):changes.append(I18n.t("baseline018.1d5ca789d6b9")+str(payload.cell))
	changes.append(I18n.t("baseline018.75787a40d819")+risk_text(preview.next_state))
	if kind=="protocol":changes.append_array(cooperation_details(payload))
	if kind in ["end_round","leave_site","emergency_retreat"]:
		for id: String in session.state.battle.heroes:
			var hero: Dictionary=session.state.battle.heroes[id]
			if hero.downed and not session.state.battle.objects.get("casualty_"+id,{}).get("delivered",false):
				changes.append(I18n.t("baseline018.376f20ccca34")+actor_name(id)+I18n.t("baseline018.5f6e713a6afb")%[hero.deadline,I18n.t("baseline018.25e25bdd81f1") if preview.next_state.product.withdrawn.has(id) else (I18n.t("baseline018.6dba8baadb19") if preview.next_state.campaign.phase=="settlement" else I18n.t("baseline018.1b7593e912ac"))])
	if kind=="end_round":
		var unused: Array[String]=[]
		for h: Dictionary in session.state.battle.heroes.values():
			if not h.left and not h.downed and h.ap>0:unused.append(actor_name(h.id)+" "+str(h.ap)+" AP")
		if not unused.is_empty():changes.append(I18n.t("guide.unused_ap") % "、".join(unused))
		for id: String in session.state.battle.objects:
			var old: Dictionary=session.state.battle.objects[id]
			var future: Dictionary=preview.next_state.battle.objects.get(id,old)
			if not old.lost and future.lost:changes.append(I18n.t("guide.object_lost") % object_name(id))
	for id: String in session.state.battle.heroes:
		if not preview.next_state.battle.heroes.has(id):continue
		var before: Dictionary=session.state.battle.heroes[id]
		var after: Dictionary=preview.next_state.battle.heroes[id]
		if before.ap!=after.ap or before.hp!=after.hp:changes.append(I18n.t("preview.actor") % [actor_name(id),before.ap,after.ap,before.hp,after.hp])
	for id: String in session.state.battle.objects:
		if not preview.next_state.battle.objects.has(id):continue
		var old: Dictionary=session.state.battle.objects[id]
		var next: Dictionary=preview.next_state.battle.objects[id]
		var details: Array[String]=[]
		if old.hp!=next.hp:details.append(I18n.t("baseline018.a7c4ceca2811")%[old.hp,next.hp])
		if old.progress!=next.progress:details.append(I18n.t("baseline018.5d3df41f34dc")%[old.progress,next.progress,next.work])
		if old.get("timer",0)!=next.get("timer",0):details.append(I18n.t("baseline018.38b6eba18a86")%[old.get("timer",0),next.get("timer",0)])
		if not old.stable and next.stable:details.append(I18n.t("baseline018.09a47dd92e8e"))
		if old.carrier!=next.carrier:details.append(I18n.t("baseline018.8a34e5fadef7")+(actor_name(next.carrier) if next.carrier!="" else I18n.t("baseline018.484d55613910")))
		if not old.completed and next.completed:details.append(I18n.t("baseline018.7106e2605494"))
		if not old.delivered and next.delivered:details.append(I18n.t("baseline018.fe1ae51ba964"))
		if not old.lost and next.lost:details.append(I18n.t("baseline018.2e6947485d64"))
		if not details.is_empty():changes.append(object_name(id)+"："+"；".join(details))
	var service: Dictionary=preview.next_state.battle.get("service",{})
	if not service.is_empty() and service!=session.state.battle.get("service",{}):
		changes.append(I18n.t("baseline018.1102fd4f05eb")%[service.ticks,service.definition.consecutive_rounds,I18n.t("baseline018.c0b3fbff51cc") if service.done else (I18n.t("baseline018.9aeb9b8ba679") if service.failed else I18n.t("baseline018.dc9591e56d50"))])
	if preview.next_state.battle.get("exits",[])!=session.state.battle.get("exits",[]):changes.append(I18n.t("baseline018.048630905cca")+str(preview.next_state.battle.exits))
	for id: String in session.state.actors:
		var before: Dictionary=session.state.actors[id]
		var after: Dictionary=preview.next_state.actors[id]
		if kind in ["train","mentor","rest","treat"] and (before.xp!=after.xp or before.fatigue!=after.fatigue or before.training_completed!=after.training_completed):
			changes.append(I18n.t("p2.growth_preview") % [actor_name(id),before.xp,after.xp,Rules.Specialties.level(int(before.xp)),Rules.Specialties.level(int(after.xp)),before.fatigue,after.fatigue,Crew.overnight_fatigue(preview.next_state,id,int(after.fatigue)),Full.stages(preview.next_state,id)])
	if kind in ["train","mentor"]:changes.append(I18n.t("p2.training_opportunity"))
	if kind=="field_assistance":
		for id: String in payload.get("participants",[]):
			var old: Dictionary=session.state.actors[id];var next: Dictionary=preview.next_state.actors[id]
			changes.append(I18n.t("baseline018.9df80a6ecfdd")%[actor_name(id),old.fatigue,next.fatigue,old.stress,next.stress,2-session.state.operations.facilities[payload.facility].used,2-preview.next_state.operations.facilities[payload.facility].used])
	for id: String in preview.next_state.appraisal.events:
		if not session.state.appraisal.events.has(id):
			var fact: Dictionary=preview.next_state.appraisal.events[id]
			changes.append(actor_name(fact.observer)+I18n.t("baseline018.805fafd46f9e")+fact.reason)
	for id: String in session.state.social:
		var old: Dictionary=session.state.social[id]
		var next: Dictionary=preview.next_state.social[id]
		if not is_equal_approx(float(old.trust),float(next.trust)):changes.append(I18n.t("ui.dae03c7abc06") % [actor_name(str(id).split(">")[0])+" → "+(I18n.t("leader") if str(id).ends_with(">leader") else actor_name(str(id).split(">")[1])),old.trust,next.trust])
	for id: String in preview.next_state.full_campaign.contracts:
		if preview.next_state.full_campaign.contracts[id].get("breached",false) and not session.state.full_campaign.contracts.get(id,{}).get("breached",false):changes.append(I18n.t("p3.breach_warning") % actor_name(id))
	for id: String in preview.next_state.product.withdrawn:
		if not session.state.product.withdrawn.has(id):changes.append(I18n.t("p4.withdrawal_warning") % actor_name(id))
	if not changes.is_empty():confirmation_text.text+=I18n.t("ui.d7b6fc9ef523")+"\n".join(changes)
	confirmation.popup_centered_clamped(Vector2i(820,560),.95)
func commit_pending() -> void:
	if feedback_active() or pending.is_empty():return
	inline_pending=false
	var input_start: int=Time.get_ticks_usec()
	var previous_state: Dictionary=session.state
	var before: Dictionary=session.state.battle.duplicate(true)
	var result: Dictionary = session.submit(pending)
	var saved_at: int=Time.get_ticks_usec()
	if result.ok:
		for id: String in session.state.journey.recruited:
			if not previous_state.journey.recruited.has(id):welcome_queue.append(id)
		for entry: Dictionary in session.state.appraisal.conflicts.slice(previous_state.appraisal.conflicts.size()):
			if entry.long_scene:conflict_notices.append(entry.duplicate(true))
		feedback_plan={} if reduced_motion else Feedback.build(previous_state,session.state,pending,BoardView.route)
		visual_previous=before;visual_started=Time.get_ticks_msec();feedback_elapsed=0
		if feedback_active():
			for id: String in feedback_plan.paths:actor_facings[id]=Feedback.direction(feedback_plan.paths[id],1.0)
			sound.schedule(feedback_plan.events,visual_started,feedback_seconds)
		else:visual_previous={};sound.action(pending.kind,previous_state,session.state)
	else:sound.play("ui_error")
	message=(I18n.t("p3.action_done") % action_name(pending.kind))+" · "+objective_summary() if result.ok else I18n.t("error.commit") % error_text(result.error_code)
	render()
	get_tree().process_frame.connect(func():metrics.input_finished(input_start),CONNECT_ONE_SHOT)
	if "--profile-input" in OS.get_cmdline_user_args():print("INPUT_TIMING: ",JSON.stringify({"kind":pending.kind,"submit_ms":(saved_at-input_start)/1000.0,"feedback_render_ms":(Time.get_ticks_usec()-saved_at)/1000.0,"undo":session.state.battle.undo.size(),"receipts":session.state.receipts.size()}))
	if not feedback_active():
		show_conflict_notice();show_next_welcome()
	if result.ok and pending.kind in ["story_open","story_choice"]:show_story(str(pending.payload.node))
	if result.ok and pending.kind in ["depart","next_mission","start_side"] and session.state.campaign.phase=="battle":show_site()
func save_manual() -> void:Screens.manual_slots(self,true)
func load_manual() -> void:Screens.manual_slots(self,false)
func recover() -> void:
	var result: Dictionary = session.load_game(true)
	message=I18n.t("ui.cb88d2cdf9c2") if result.ok else I18n.t("error.recover") % error_text(result.error_code)
	render()

func action_name(kind: String) -> String:
	var names: Dictionary={"finish_evening":I18n.t("baseline018.ec4e6b69c86a"),"depart":I18n.t("baseline018.fb1dac351325"),"save_preparation":I18n.t("baseline018.957bcad5d107"),"acknowledge_recruit":I18n.t("baseline018.79c98c2fb64b"),"service_watch":I18n.t("baseline018.b9ecb75695f1"),"restore_power":I18n.t("baseline018.b4389481a817"),"declare_priority":I18n.t("baseline018.61b03a4f643b"),"repair_field_facility":I18n.t("baseline018.1bfcaed648d8"),"field_assistance":I18n.t("baseline018.44630ad7ef4a"),"decline_side":I18n.t("baseline018.8266e0d647d9"),"plan_next_roster":I18n.t("baseline018.8b834bbafbb5"),"repair_event":I18n.t("baseline018.dc84255708ed"),"schedule_repair":I18n.t("baseline018.414799f5bd36")}
	if names.has(kind):return names[kind]
	if I18n.messages.has("p4.action."+kind):return I18n.t("p4.action."+kind)
	return {"craft_medicine":I18n.t("p3.craft_medicine"),"publish_record":I18n.t("p3.publish"),"select_route":I18n.t("p3.select_route"),"review_record":I18n.t("p3.review"),"community_report":I18n.t("p2.community_report"),"mentor":I18n.t("p2.mentor"),"start_side":I18n.t("p2.start_side"),"story_open":I18n.t("p2.story_open"),"story_choice":I18n.t("p2.story_choice"),"story_defer":I18n.t("p2.story_defer"),"mission_settled":I18n.t("event.settled"),"objective_result":I18n.t("event.objective"),"relationship_changed":I18n.t("event.relationship"),"move":I18n.t("ui.fc6bb436b8ca"),"attack":I18n.t("ui.8226ca02ff36"),"push":I18n.t("ui.40c328e118ed"),"stabilize":I18n.t("ui.8d972cf00664"),"pickup":I18n.t("ui.192a1a780a22"),"interact":I18n.t("ui.d94aec50ca73"),"drop":I18n.t("ui.e0f2d3ead59c"),"extract":I18n.t("ui.1b29df5aa1ec"),"leave_site":I18n.t("ui.856703dd5046"),"end_round":I18n.t("ui.975778d99095"),"emergency_retreat":I18n.t("ui.ef504de2b0bb"),"enter_camp":I18n.t("ui.6de354f5f7cd"),"train":I18n.t("ui.a29c0de14076"),"treat":I18n.t("ui.c81995fafdc2"),"rest":I18n.t("ui.fff33732fc97"),"short_talk":I18n.t("ui.53d395cebf30"),"next_mission":I18n.t("ui.e50994d51a48"),"specialty":I18n.t("ui.9f5e8b5c9b8e"),"undo":I18n.t("ui.394fe10e9d4b"),"authorize":I18n.t("ui.ff95c5959fcb"),"promise_retreat":I18n.t("ui.10de563f4537"),"tendency":I18n.t("ui.d940a75ac88f"),"acknowledge":I18n.t("ui.207d18836ec0"),"agreement":I18n.t("ui.789c7aa4b70d"),"protocol":I18n.t("ui.9f660330d5ec")}.get(kind,I18n.t("event.unknown"))
func error_text(code: String) -> String:
	var explanations: Dictionary={"service_unavailable":I18n.t("baseline018.11d787453e2d"),"power_required":I18n.t("baseline018.98743f759221"),"facility_unavailable":I18n.t("baseline018.f761de2f07ba"),"dispatch_unavailable":I18n.t("baseline018.05c6f3b1b563")}
	if explanations.has(code):return explanations[code]
	if I18n.messages.has("p4.error."+code):return I18n.t("p4.error."+code)
	return {"route_required":I18n.t("p3.route_required"),"route_unavailable":I18n.t("p3.route_unavailable"),"proof_required":I18n.t("p3.proof_required"),"branch_locked":I18n.t("p3.branch_locked"),"invalid_support":I18n.t("p3.invalid_support"),"record_unavailable":I18n.t("p3.record_unavailable"),"mentorship_unavailable":I18n.t("p2.mentorship_unavailable"),"invalid_roster":I18n.t("p2.invalid_roster"),"side_requires_three":I18n.t("p2.side_requires_three"),"side_unavailable":I18n.t("p2.side_unavailable"),"story_unavailable":I18n.t("p2.story_unavailable"),"already_used":I18n.t("p2.already_used"),"missing_save":I18n.t("error.missing"),"invalid_target":I18n.t("ui.384b773722fa"),"insufficient_ap":I18n.t("ui.cbcc876fb615"),"prerequisite_required":I18n.t("ui.807249005c6d"),"unavailable_actor":I18n.t("ui.866d6a9f37d7"),"carrying_restriction":I18n.t("ui.d18f45d91634"),"training_unavailable":I18n.t("ui.4d99ce3d1c58"),"project_used":I18n.t("ui.2eace33acd47"),"insufficient_resources":I18n.t("ui.a6975134338c"),"save_io_failed":I18n.t("ui.0ae83e9475f1"),"stale_revision":I18n.t("ui.95e1eb1ea5ce")}.get(code,I18n.t("error.fallback"))
func risk_text(candidate: Dictionary) -> String:
	if candidate.campaign.phase=="briefing":return I18n.t("baseline018.d3f4ef681de7")
	if candidate.campaign.phase=="battle":
		var b: Dictionary=candidate.battle
		var risks: Array[String]=[]
		for enemy: Dictionary in b.enemies.values():
			if enemy.get("paused_round",0)==b.round:continue
			var cells: Array=Rules.Hazards.footprint(b,enemy,Rules)
			for h: Dictionary in b.heroes.values():
				if h.left or h.downed or not Rules.contains_cell(cells,h.cell):continue
				var water: bool=enemy.type=="skimmer" and int(b.round)%2==0
				if water and Rules.contains_cell(b.insulation,h.cell):continue
				risks.append(actor_name(h.id)+I18n.t("baseline018.a850d56fa243")+enemy.id+I18n.t("baseline018.8af2350cfd65")+(I18n.t("baseline018.9d3c4d578acc") if water else I18n.t("baseline018.85bafee7886e")%int(b.cover.get(h.id,0))))
		var fire: Dictionary=b.environment.fire_pulse
		if b.round>=fire.round and b.round<fire.round+fire.duration_rounds:
			for h: Dictionary in b.heroes.values():
				if not h.left and not h.downed and Rules.contains_cell(fire.cells,h.cell):risks.append(actor_name(h.id)+I18n.t("baseline018.4533f7cca7b6"))
		return "；".join(risks) if not risks.is_empty() else I18n.t("baseline018.bf1b0109c11e")
	var result: Dictionary = candidate.campaign.last_result
	var names: Array[String] = []
	for id: String in result.injured: names.append(actor_name(id))
	return I18n.t("ui.fd6383d67ac6") % [{"success":I18n.t("ui.053461ce86d2"),"partial":I18n.t("ui.1bd16b45b478"),"failed":I18n.t("ui.28384d7afd2e")}[result.outcome],"、".join(names) if not names.is_empty() else I18n.t("ui.484d55613910")]

func resource_text(resources: Dictionary) -> String:
	return I18n.t("ui.5316db6ad41c") % [resources.get("credits",0),resources.get("supplies",0),resources.get("parts",0)]

func specialty_click(target: String) -> void:
	if ability in ["lin_3","mo_3"]:
		specialty_target=target
		message=I18n.t("ui.e633f4c21475")
		render()
	else:propose("specialty",{"ability":ability,"target":target,"consent":true,"mode":specialty_mode})

func object_click(target: String) -> void:
	if action=="use_tool":propose(action,{"item":tool,"target":target});return
	if action=="specialty":specialty_click(target)
	elif action=="protocol":propose("protocol",{"protocol":protocol,"partner":partner,"target":target,"consent":true})
	else:propose(action,{"target":target})

func modal(title_text: String) -> Dictionary:
	var window:=Window.new();window.title=title_text;window.size=Vector2i(850,600);window.min_size=Vector2i(580,400)
	window.transient=true;window.exclusive=true;add_child(window)
	window.close_requested.connect(window.queue_free)
	var margin:=MarginContainer.new();margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side: String in ["left","right","top","bottom"]:margin.add_theme_constant_override("margin_"+side,20)
	window.add_child(margin)
	var scroll:=ScrollContainer.new();scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;margin.add_child(scroll)
	var box:=VBoxContainer.new();box.size_flags_horizontal=Control.SIZE_EXPAND_FILL;box.add_theme_constant_override("separation",12);scroll.add_child(box)
	window.popup_centered()
	return {"window":window,"box":box}
func prepare_mission(mission: String,side: bool) -> void:
	var board: Dictionary=session.content.boards[mission]
	var dialog:=modal(I18n.t("p2.briefing"));var box: VBoxContainer=dialog.box
	label(box,I18n.content("boards",mission,"title",board.title)).add_theme_color_override("font_color",TEAL)
	box.add_child(Art.picture(Art.environment(board.location),Vector2(0,240)))
	var settings: Dictionary=difficulty_controls(box,board)
	label(box,I18n.t("p4.weather") % [session.state.product.variant,Product.weather(board,session.state.product.variant).water_addition.round])
	for group: Array in Full.groups(session.state,board):
		var names: Array[String]=[]
		for id: String in group:
			for object: Dictionary in board.objectives:
				if object.id==id:names.append(I18n.content("objects",mission+"."+id,"label",object.label))
		label(box,I18n.t("p2.required") % " / ".join(names))
	label(box,I18n.t("p2.basic_method"))
	label(box,I18n.content("boards",mission,"decision",board.decision))
	label(box,I18n.t("p2.choose_roster"))
	var roster: Array=[]
	var support_choice: Array=[""]
	label(box,I18n.t("p3.pack_medicine") % session.state.full_campaign.medicine_stock)
	var medicine:=SpinBox.new();medicine.min_value=0;medicine.max_value=mini(Product.pack_limit(session.state),session.state.full_campaign.medicine_stock);medicine.step=1;box.add_child(medicine)
	if not side:
		label(box,I18n.t("p3.support"))
		var support:=OptionButton.new();support.add_item(I18n.t("p3.none"));box.add_child(support)
		for id: String in session.state.actors:
			if Crew.joined(session.state,id):support.add_item(actor_name(id));support.set_item_metadata(support.item_count-1,id)
		support.item_selected.connect(func(i: int):support_choice[0]="" if i==0 else str(support.get_item_metadata(i)))
	for actor: Dictionary in session.state.actors.values():
		if not Crew.joined(session.state,actor.id) or session.state.product.withdrawn.has(actor.id):continue
		var toggle:=CheckButton.new();toggle.text=I18n.t("p2.roster_actor") % [actor_name(actor.id),actor.fatigue,actor.ready_day];box.add_child(toggle)
		toggle.toggled.connect(func(on: bool):
			if on:roster.append(actor.id)
			else:roster.erase(actor.id))
	label(box,I18n.t("p2.roster_hint"))
	button(box,I18n.t("p2.preview_departure"),func():dialog.window.queue_free();propose("start_side" if side else "next_mission",{"mission":mission,"roster":roster,"support":support_choice[0],"medicine":int(medicine.value),"difficulty":settings.difficulty,"hard_acknowledged":settings.ack}))
func group_project(kind: String) -> void:
	var dialog:=modal(I18n.t("p2.group") % action_name(kind));var participants: Array=[]
	label(dialog.box,I18n.t("p2.group_hint"))
	for actor: Dictionary in session.state.actors.values():
		if not Crew.joined(session.state,actor.id):continue
		var toggle:=CheckButton.new();toggle.text=actor_name(actor.id);dialog.box.add_child(toggle)
		toggle.toggled.connect(func(on: bool):
			if on:participants.append(actor.id)
			else:participants.erase(actor.id))
	button(dialog.box,I18n.t("p2.preview_project"),func():dialog.window.queue_free();propose(kind,{"participants":participants}))
func render_story_list(box: VBoxContainer) -> void:
	label(box,I18n.t("p2.stories")).add_theme_color_override("font_color",GOLD)
	var row:=HFlowContainer.new();box.add_child(row)
	var nodes:=Stories.nodes(session.content)
	for id: String in Stories.available(session.state,session.content):
		var node: Dictionary=nodes[id]
		var seen: bool=session.state.chapter_one.scenes.get(id,{}).get("seen",false)
		button(row,I18n.content("scenes",id,"title",node.title),func():
			if seen:show_story(id)
			else:propose("story_open",{"node":id}))
func story_lines(id: String,field: String,lines: Array) -> String:
	var result: Array[String]=[]
	for index: int in range(lines.size()):result.append(I18n.content("scenes",id,field+".%d" % index,str(lines[index])))
	return "\n\n".join(result)
func show_story(id: String) -> void:
	preload("res://scripts/presentation/story_screen.gd").show(self,id)
func chapter_report(box: VBoxContainer) -> void:
	label(box,I18n.t("p2.chapter_summary")).add_theme_color_override("font_color",GOLD)
	for entry: Dictionary in session.content.domains.scripts.chapter:
		if not session.state.campaign.settled.has(entry.source):continue
		var result: Dictionary=session.state.campaign.settled[entry.source]
		var secured: bool=result.facts.get(entry.condition.objective,"") in ["saved","completed"]
		label(box,I18n.content("scenes",entry.id,"true_text" if secured else "false_text",entry.true_text if secured else entry.false_text))

func render_mentors(box: VBoxContainer) -> void:
	for teacher: String in session.state.actors:
		for student: String in session.state.actors:
			var trial: Dictionary=session.state.duplicate(true)
			if Chapter.mentor(trial,{"actor_id":teacher,"payload":{"student":student,"consent":true}})!="":continue
			var gain: int=int(trial.actors[student].xp)-int(session.state.actors[student].xp)
			button(box,I18n.t("p2.mentor_option") % [actor_name(teacher),actor_name(student),gain],func():selected=teacher;propose("mentor",{"student":student,"consent":true}))

func objective_summary() -> String:
	var s: Dictionary=session.state
	var board: Dictionary=session.content.boards[s.battle.mission_id]
	var lines: Array[String]=[]
	for group: Array in Full.groups(s,board):
		var names: Array[String]=[];var done: bool=false
		for id: String in group:
			if not s.battle.objects.has(id):continue
			var o: Dictionary=s.battle.objects[id]
			done=done or (o.completed and (not o.sustain_until_exit or o.hp>0))
			names.append(object_name(id))
		lines.append((I18n.t("p3.done") if done else I18n.t("p3.todo"))+" / ".join(names))
	return " · ".join(lines)
func render_campaign_options(box: VBoxContainer) -> void:
	var s: Dictionary=session.state
	button(box,I18n.t("p3.journal"),show_journal)
	button(box,I18n.t("p3.craft_medicine"),func():propose("craft_medicine",{})).icon=Art.icon("medicine")
	if s.campaign.day>=18 and not s.full_campaign.evidence.is_empty():
		for privacy: String in ["redacted","unredacted"]:button(box,I18n.t("p3.publish_"+privacy),func():propose("publish_record",{"privacy":privacy}))
	label(box,I18n.t("p3.chapter") % [Full.chapter(s.campaign.day),s.campaign.day])
	if int(s.campaign.day) in [20,22,23] or (s.campaign.day==18 and Product.tier(s,"communications")>=1):
		for id: String in session.content.domains.world.evidence:
			if not s.full_campaign.evidence.has(id):button(box,I18n.t("p3.review_named") % I18n.t("p3."+id),func():propose("review_record",{"evidence":id}))
	if Product.tier(s,"communications")>=2 and int(s.campaign.day) in [20,22,23]:
		var remaining: Array=[]
		for id: String in session.content.domains.world.evidence:
			if not s.full_campaign.evidence.has(id):remaining.append(id)
		if remaining.size()>=2:button(box,I18n.t("p4.review_two"),func():propose("review_record",{"records":remaining.slice(0,2)}))
	for id: String in s.full_campaign.contracts:
		var contract: Dictionary=s.full_campaign.contracts[id]
		label(box,I18n.t("p3.plan_status") % [actor_name(id),I18n.t("p3.fulfilled") if contract.fulfilled else (I18n.t("baseline018.2a50f442d19a") if contract.get("interrupted_by_injury",false) else (I18n.t("baseline018.3b98164d604b") if contract.get("breached",false) else I18n.t("p3.pending"))),contract.proof])
	if s.campaign.day==23:
		label(box,I18n.t("p3.final_warning"))
		var total: int=0
		for value: int in s.campaign.districts.values():total+=value
		label(box,I18n.t("p3.route_conditions") % [total,s.full_campaign.evidence.size()])
		for route: String in Full.routes(s):button(box,I18n.t("p3.route_"+route),func():propose("select_route",{"route":route}))
		if not s.full_campaign.route.is_empty():label(box,I18n.t("p3.selected_route") % I18n.t("p3.route_"+s.full_campaign.route))
	if int(s.campaign.day)%6==0:chapter_report(box)
func render_ending(box: VBoxContainer) -> void:
	var s: Dictionary=session.state
	label(box,I18n.t("p3.final_title") % I18n.t("p3.route_"+s.full_campaign.ending)).add_theme_color_override("font_color",GOLD)
	button(box,I18n.t("p3.journal"),show_journal)
	button(box,I18n.t("p3.new_campaign"),new_campaign)
	box.add_child(Art.picture(Art.environment("shelter"),Vector2(0,260)))
	label(box,I18n.t("p3.ending_"+s.full_campaign.ending))
	for district: String in s.campaign.districts:label(box,I18n.t("journey.district_state")%[Screens.Journey.district_name(district),s.campaign.districts[district],s.full_campaign.district_caps[district]])
	label(box,risk_text(s))
	for entry: Dictionary in session.content.domains.scripts.community:
		if entry.source=="M24":label(box,I18n.content("scenes",entry.id,"variants."+s.campaign.last_result.outcome,entry.variants[s.campaign.last_result.outcome]))
	chapter_report(box)
	for id: String in s.actors:
		var node_id: String="P_"+id+"_3"
		var node: Dictionary=Stories.nodes(session.content)[node_id]
		var script: Dictionary=Stories.script(session.content,node)
		var record: Dictionary=s.chapter_one.scenes.get(node_id,{})
		label(box,actor_name(id)).add_theme_color_override("font_color",TEAL)
		var portrait=Art.picture(Art.portrait(id,"grief" if s.product.withdrawn.has(id) else ("relieved" if record.get("choice","")=="integrated" else "neutral")),Vector2(0,150));portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;box.add_child(portrait)
		label(box,I18n.t("baseline018.139478be0703")+(I18n.t("baseline018.a973c1399893") if s.product.withdrawn.has(id) else I18n.t("baseline018.68e5b398962f")))
		if s.product.withdrawn.has(id):
			label(box,I18n.content("scenes",node_id,"withdrawn",script.withdrawn))
		if s.full_campaign.contracts.get(id,{}).get("breached",false):label(box,I18n.content("scenes",node_id,"later_breach_other",script.later_breach_other))
		label(box,I18n.t("baseline018.7b9c7799cdb3"))
		if record.get("choice","").is_empty():label(box,I18n.content("scenes",node_id,"unread",script.unread))
		elif record.choice=="integrated" and s.full_campaign.contracts.get(id,{}).get("breached",false):label(box,I18n.t("p3.past_fulfilled"))
		else:label(box,story_lines(node_id,"choices."+record.choice,script.choices[record.choice]))
		if s.full_campaign.contracts.has(id):
			var contract: Dictionary=s.full_campaign.contracts[id]
			label(box,I18n.t("p3.plan_status") % [actor_name(id),I18n.t("p3.fulfilled") if contract.fulfilled else (I18n.t("baseline018.2a50f442d19a") if contract.get("interrupted_by_injury",false) else (I18n.t("baseline018.3b98164d604b") if contract.get("breached",false) else I18n.t("p3.pending"))),contract.proof])
		for relation: Dictionary in s.social.values():
			if relation.observer!=id:continue
			label(box,I18n.t("baseline018.ed421a5cf3c8")+(I18n.t("baseline018.36caf75886a3") if relation.target=="leader" else actor_name(relation.target))+"："+I18n.t("band."+relation.band)+"；"+(I18n.t("baseline018.be70db1b5226") if relation.agreement=="cooperate" else I18n.t("baseline018.fc4055ae6171")))
			for memory: Dictionary in relation.memories:
				if memory.stage<2:label(box,I18n.t("p3.unresolved_memory") % [actor_name(relation.target) if relation.target!="leader" else I18n.t("leader"),Screens.Journey.memory_text(session.state,memory)])

func show_site() -> void:
	var board: Dictionary=session.content.boards[session.state.battle.mission_id]
	var dialog:=modal(I18n.content("boards",board.id,"title",board.title))
	dialog.box.add_child(Art.picture(Art.environment(board.location),Vector2(0,380)))
	label(dialog.box,objective_summary()).add_theme_color_override("font_color",TEAL)
	label(dialog.box,I18n.content("boards",board.id,"decision",board.decision))
	label(dialog.box,I18n.t("p2.basic_method"))
	button(dialog.box,I18n.t("p3.return_site"),dialog.window.queue_free)

func show_journal() -> void:
	var dialog:=modal(I18n.t("p3.journal"));var box: VBoxContainer=dialog.box
	for id: String in Stories.available(session.state,session.content):
		if not session.state.chapter_one.scenes.get(id,{}).get("seen",false):label(box,Stories.nodes(session.content)[id].title+I18n.t("baseline018.9280bc81998c"))
	for board: Dictionary in session.content.boards.values():
		if board.kind!="side" or board.day>session.state.campaign.day:continue
		var status: String=I18n.t("baseline018.374d13aec7f1") if session.state.campaign.settled.has(board.id) else (I18n.t("baseline018.ced9778174ce") if session.state.journey.declined_sides.has(board.id) else (I18n.t("baseline018.2fe0e3339ac4") if session.state.campaign.day>board.day+1 else I18n.t("baseline018.96c28d7f3839")%(board.day+1)))
		label(box,board.title+" · "+status)
	for id: String in session.state.chapter_one.scenes:
		if session.state.chapter_one.scenes[id].get("seen",false):button(box,I18n.content("scenes",id,"title",id),func():show_story(id))
	for entry: Dictionary in session.content.domains.scripts.community:
		if not session.state.campaign.settled.has(entry.source):continue
		var result: Dictionary=session.state.campaign.settled[entry.source]
		label(box,I18n.content("scenes",entry.id,"title",entry.title)).add_theme_color_override("font_color",TEAL)
		label(box,I18n.content("scenes",entry.id,"variants."+result.outcome,entry.variants[result.outcome]))
		for id: String in result.facts:
			label(box,I18n.content("objects",entry.source+"."+id,"label",id)+" · "+I18n.t("p3.fact_"+result.facts[id]))

func new_campaign() -> void:
	var dialog:=modal(I18n.t("p3.new_campaign"))
	var settings: Dictionary=difficulty_controls(dialog.box,session.content.boards.M01,"standard")
	var variant: Array=["A"]
	var choice:=OptionButton.new();choice.add_item(I18n.t("p4.variant_a"));dialog.box.add_child(choice)
	if can_variant_b():choice.add_item(I18n.t("p4.variant_b"))
	else:label(dialog.box,I18n.t("p4.variant_locked"))
	choice.item_selected.connect(func(i: int):variant[0]="A" if i==0 else "B")
	button(dialog.box,I18n.t("p4.start"),func():
		if settings.difficulty=="hard" and not settings.ack:label(dialog.box,I18n.t("p4.error.hard_confirmation_required")).add_theme_color_override("font_color",GOLD);sound.play("ui_error");return
		dialog.window.queue_free();create_campaign({"difficulty":settings.difficulty,"variant":variant[0]}))
func can_variant_b() -> bool:
	if session.state.chapter_one.finished:return true
	for version: String in ["p3","p4"]:
		var base: String="user://saves/"+version
		if not DirAccess.dir_exists_absolute(base):continue
		var slots: Array[String]=[base+"/autosave.json"]
		for directory: String in DirAccess.get_directories_at(base):
			if directory.begins_with("campaign-"):slots.append(base+"/"+directory+"/autosave.json")
		for slot: String in slots:
			var saved: Dictionary=session.store.load_slot(slot,session.content)
			if saved.ok and saved.state.chapter_one.finished:return true
	return false
func create_campaign(options: Dictionary) -> void:
	var id: String="campaign-%d-%d" % [Time.get_unix_time_from_system(),Time.get_ticks_usec()]
	var slot: String="user://saves/p4/"+id+"/autosave.json"
	var candidate=Session.new()
	var result: Dictionary=candidate.start(session.content,slot,id,options)
	if result.ok:
		var config:=ConfigFile.new();config.set_value("campaign","path",slot)
		if config.save("user://p4_active_slot.cfg")==OK:session=candidate;title_screen=false;selected="lin";message=I18n.t("p3.new_campaign_ready")
		else:message=I18n.t("error.save") % error_text("save_io_failed")
	else:message=I18n.t("error.save") % error_text(result.error_code)
	render()
	if result.ok:
		welcome_queue=["lin","xu","su"];show_next_welcome()
func campaign_picker() -> void:
	var dialog:=modal(I18n.t("p3.switch_campaign"))
	var slots: Array[String]=["user://saves/p4/autosave.json"]
	for directory: String in (DirAccess.get_directories_at("user://saves/p4") if DirAccess.dir_exists_absolute("user://saves/p4") else PackedStringArray()):
		if directory.begins_with("campaign-"):slots.append("user://saves/p4/"+directory+"/autosave.json")
	for slot: String in slots:
		var result: Dictionary=session.store.load_slot(slot,session.content)
		if not result.ok:continue
		button(dialog.box,I18n.t("p3.slot_label") % [result.state.campaign.id,result.state.campaign.day],func():
			var config:=ConfigFile.new();config.set_value("campaign","path",slot)
			if config.save("user://p4_active_slot.cfg")!=OK:message=I18n.t("error.save") % error_text("save_io_failed");return
			session.path=slot;session.state=result.state;title_screen=false;dialog.window.queue_free();render())

func difficulty_controls(box: VBoxContainer,board: Dictionary,initial: String="") -> Dictionary:
	var settings: Dictionary={"difficulty":session.state.campaign.difficulty if initial.is_empty() else initial,"ack":session.state.campaign.difficulty=="hard" and initial.is_empty()}
	label(box,I18n.t("difficulty.title")).add_theme_color_override("font_color",TEAL)
	var group:=ButtonGroup.new()
	var ack:=CheckButton.new();ack.text=I18n.t("p4.hard_ack");ack.button_pressed=settings.ack
	ack.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	for id: String in ["relaxed","standard","hard"]:
		var panel:=PanelContainer.new();panel.add_theme_stylebox_override("panel",surface(SURFACE,8));box.add_child(panel)
		var row:=VBoxContainer.new();panel.add_child(row)
		var choice:=CheckBox.new();choice.button_group=group;choice.text=I18n.t("difficulty."+id)+" · "+I18n.t("p4.rounds") % Product.limit(board,id)
		choice.button_pressed=id==settings.difficulty;row.add_child(choice)
		label(row,I18n.t("difficulty."+id+"_body")).add_theme_font_size_override("font_size",16)
		choice.toggled.connect(func(on: bool):
			if on:settings.difficulty=id;ack.visible=id=="hard")
	box.add_child(ack);ack.visible=settings.difficulty=="hard"
	ack.toggled.connect(func(on: bool):settings.ack=on)
	label(box,I18n.t("difficulty.lock")).add_theme_font_size_override("font_size",16)
	return settings
func render_tools(box: VBoxContainer) -> void:
	var b: Dictionary=session.state.battle
	var gear: Dictionary=b.equipment.get(selected,{})
	for id: String in gear.values():
		if id.is_empty():continue
		if id=="stretcher":label(box,I18n.t("p4.stretcher_passive"));continue
		var definition: Dictionary=Product.item(session.content,id)
		var remaining: String="∞" if definition.uses_per_mission==null else str((b.medicine_limit if id=="medkit" else int(definition.uses_per_mission))-int(b.tool_uses.get(id,0)))
		button(box,I18n.t("p4.tool_button") % [I18n.t("p4.item."+id),remaining],func():tool=id;anchor_start=[];action="use_tool";message=I18n.content("equipment",id,"effect",definition.effect);render()).icon=Art.icon(id)
	if not b.deployed_tools.is_empty():button(box,I18n.t("p4.action.cross_anchor"),func():action="cross_anchor";message=I18n.t("p4.anchor_cross");render())
	if gear.values().has("medkit"):label(box,I18n.t("p4.medical_status") % [b.medicine,b.medicine_limit,int(b.tool_uses.get("medkit",0))])
func show_workshop() -> void:
	var dialog:=modal(I18n.t("p4.equipment_facilities"));var box: VBoxContainer=dialog.box
	var s: Dictionary=session.state
	label(box,I18n.t("p4.workshop_intro"))
	button(box,I18n.t("p4.buy_supplies") % session.content.domains.economy.supply_buy_cost,func():dialog.window.queue_free();propose("buy_supplies",{}))
	for definition: Dictionary in session.content.domains.equipment.items:
		var id: String=definition.id
		var item_row:=HBoxContainer.new();box.add_child(item_row);item_row.add_child(Art.picture(Art.icon(id),Vector2(30,30)))
		label(item_row,I18n.t("p4.item."+id)).add_theme_color_override("font_color",GOLD)
		label(box,I18n.content("equipment",id,"effect",definition.effect))
		if s.product.owned.has(id):
			var row:=HFlowContainer.new();box.add_child(row)
			for actor: String in s.actors:
				if s.actors[actor].join>s.campaign.day or s.product.withdrawn.has(actor):continue
				var equipped: bool=s.product.loadout[actor][definition.slot]==id
				button(row,I18n.t("p4.equip") % [actor_name(actor),I18n.t("p4.unequip") if equipped else I18n.t("p4.equip_word")],func():selected=actor;dialog.window.queue_free();propose("equip_tool",{"item":"" if equipped else id,"slot":definition.slot}))
			if s.product.purchases.has(id) and not s.product.purchases[id].deployed:button(row,I18n.t("p4.action.refund_tool"),func():dialog.window.queue_free();propose("refund_tool",{"item":id}))
		else:
			var discount: int=1 if Product.tier(s,"workshop")>=1 and s.product.discount_main!=s.chapter_one.main_completed else 0
			var purchase:=button(box,I18n.t("p4.purchase") % [definition.price_credits,maxi(0,int(definition.price_parts)-discount),definition.unlocked_after_main],func():dialog.window.queue_free();propose("buy_tool",{"item":id}))
			purchase.disabled=s.chapter_one.main_completed<int(definition.unlocked_after_main)
	for definition: Dictionary in session.content.domains.facilities:
		var tier: int=Product.tier(s,definition.id)
		var facility_row:=HBoxContainer.new();box.add_child(facility_row);facility_row.add_child(Art.picture(Art.icon(definition.id),Vector2(30,30)))
		label(facility_row,I18n.t("p4.facility."+definition.id)+" · "+str(tier)+" / 2").add_theme_color_override("font_color",GOLD)
		if tier>=2:continue
		label(box,I18n.content("facilities",definition.id,"tier"+str(tier+1),definition["tier"+str(tier+1)]))
		button(box,I18n.t("p4.upgrade") % [definition.costs[tier][0],definition.costs[tier][1]],func():dialog.window.queue_free();propose("upgrade_facility",{"facility":definition.id}))
func show_help() -> void:
	var dialog:=modal(I18n.t("p4.help"))
	button(dialog.box,I18n.t("intro.button"),func():dialog.window.queue_free();show_intro(false))
	label(dialog.box,I18n.t("p4.help_body"))
	label(dialog.box,I18n.t("p4.hint_history"))
	for entry: Dictionary in session.state.tutorial.get("history",[]):label(dialog.box,I18n.t("p4.hint."+entry.id))

func audio_settings() -> void:
	var dialog:=modal(I18n.t("p4.audio"))
	for entry: Array in [["music_volume","p4.music"],["effects_volume","p4.effects"]]:
		label(dialog.box,I18n.t(entry[1]))
		var slider:=HSlider.new();slider.min_value=0;slider.max_value=1;slider.step=.05;slider.value=sound.get(entry[0]);slider.custom_minimum_size=Vector2(280,42);dialog.box.add_child(slider)
		slider.value_changed.connect(func(value: float):sound.set(entry[0],value);sound.save_preferences())
	var mute:=CheckButton.new();mute.text=I18n.t("p4.mute");mute.button_pressed=sound.muted;dialog.box.add_child(mute)
	mute.toggled.connect(func(on: bool):sound.muted=on;sound.save_preferences())
	button(dialog.box,I18n.t("p4.test_sound"),func():sound.play("extract"))

func show_history_repair() -> void:
	var dialog:=modal(I18n.t("p4.history"))
	label(dialog.box,I18n.t("p4.history_intro"))
	for route: Dictionary in session.content.domains.integration.history_repair_routes:
		var pair: String=route.pair
		var stage: int=int(session.state.social[pair].history_stage)+1
		var actors: PackedStringArray=pair.split(">")
		if session.state.actors[actors[0]].join>session.state.campaign.day or session.state.actors[actors[1]].join>session.state.campaign.day:continue
		label(dialog.box,actor_name(actors[0])+" → "+actor_name(actors[1])+" · "+str(stage-1)+" / 3").add_theme_color_override("font_color",GOLD)
		if stage>3:continue
		label(dialog.box,I18n.content("history",pair,"stage"+str(stage),route["stage"+str(stage)]))
		var receipt: Dictionary=preload("res://scripts/domain/history_repair.gd").proof(session.state,pair)
		if receipt.is_empty():label(dialog.box,I18n.t("p4.error.history_proof_required"))
		else:button(dialog.box,I18n.t("p4.history_confirm"),func():dialog.window.queue_free();propose("history_repair",{"pair":pair,"consent":true}))

func cancel_selection() -> void:
	if feedback_active():finish_feedback();return
	sound.play("ui_cancel")
	inline_pending=false;pending={};anchor_start=[];action="move";message=I18n.t("p4.selection_cancelled");render()
func _unhandled_input(event: InputEvent) -> void:
	if feedback_active():
		if event is InputEventKey and event.pressed and not event.echo:
			if event.keycode==KEY_ESCAPE and not paused:pause_menu();get_viewport().set_input_as_handled()
			elif event.keycode==KEY_SPACE and not paused:finish_feedback();get_viewport().set_input_as_handled()
		return
	for child: Node in get_children():
		if child is Window and child.visible:return
	if event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_RIGHT:
		cancel_selection();get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode==KEY_ESCAPE:
			if inline_pending or action!="move":cancel_selection()
			else:pause_menu()
			get_viewport().set_input_as_handled()
		elif event.keycode==KEY_SPACE and session.state.campaign.phase=="battle":propose("end_round",{});get_viewport().set_input_as_handled()
		elif event.keycode==KEY_F1:show_help();get_viewport().set_input_as_handled()

func show_intro(start_campaign: bool=false,page: int=0) -> void:
	var dialog:=modal(I18n.t("intro.title"))
	label(dialog.box,I18n.t("intro.page") % [page+1,4]).add_theme_color_override("font_color",MUTED)
	label(dialog.box,I18n.t("intro.title."+str(page))).add_theme_color_override("font_color",TEAL)
	var strip:=HBoxContainer.new();strip.alignment=BoxContainer.ALIGNMENT_CENTER;dialog.box.add_child(strip)
	var frames: Array=[1,4,5,1]
	for index: int in range(3):
		var picture=Art.picture(Art.motion(["lin","xu","su"][index],frames[page]),Vector2(100,100))
		picture.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;strip.add_child(picture)
	label(dialog.box,I18n.t("intro.body."+str(page)))
	var controls:=HFlowContainer.new();dialog.box.add_child(controls)
	if page>0:button(controls,I18n.t("intro.back"),func():dialog.window.queue_free();show_intro(start_campaign,page-1))
	if page<3:button(controls,I18n.t("intro.next"),func():dialog.window.queue_free();show_intro(start_campaign,page+1))
	else:button(controls,I18n.t("intro.choose") if start_campaign else I18n.t("intro.return"),func():dialog.window.queue_free();new_campaign() if start_campaign else render())
	if page<3:button(controls,I18n.t("intro.skip"),func():dialog.window.queue_free();new_campaign() if start_campaign else render())

func preview_guidance() -> void:
	if feedback_active():return
	var next: Dictionary=current_guidance()
	inline_pending=false;pending={}
	if next.has("actor"):
		selected=next.actor;action="move";render();return
	if next.get("action","").is_empty():return
	action=next.action;panel_tab="actions"
	propose(action,next.get("payload",{}).duplicate(true))

func choose_object(id: String) -> void:
	if action=="protocol":propose(action,{"protocol":protocol,"partner":partner,"target":id,"consent":true})
	elif action=="use_tool":propose(action,{"item":tool,"target":id})
	else:propose(action,{"target":id})

func pause_menu() -> void:
	if paused:return
	paused=true
	var dialog:=modal(I18n.t("baseline018.cbfd5e57246b"))
	dialog.window.close_requested.connect(func():paused=false)
	label(dialog.box,I18n.t("baseline018.c9facb8e6ba4"))
	var rate:=OptionButton.new()
	for value: float in [.5,1.0,1.5,2.0]:
		rate.add_item(I18n.t("baseline018.a10e3b235685")%value);rate.set_item_metadata(rate.item_count-1,value)
		if is_equal_approx(value,animation_rate):rate.select(rate.item_count-1)
	dialog.box.add_child(rate)
	rate.item_selected.connect(func(i: int):animation_rate=rate.get_item_metadata(i);save_presentation())
	var reduced:=CheckButton.new();reduced.text=I18n.t("baseline018.870fa3a471d5");reduced.button_pressed=reduced_motion;dialog.box.add_child(reduced)
	reduced.toggled.connect(func(value: bool):reduced_motion=value;save_presentation())
	button(dialog.box,I18n.t("baseline018.a897aeb6cf42"),func():paused=false;dialog.window.queue_free())
	button(dialog.box,I18n.t("baseline018.8e12463580ce"),func():paused=false;dialog.window.queue_free();show_help())
	button(dialog.box,I18n.t("baseline018.df0379d3d6af"),func():finish_feedback();paused=false;dialog.window.queue_free();title_screen=true;render())
func save_presentation() -> void:
	var config:=ConfigFile.new();config.set_value("feedback","rate",animation_rate);config.set_value("feedback","reduced",reduced_motion);config.save("user://presentation018.cfg")

func plan_next_roster() -> void:
	var dialog:=modal(I18n.t("baseline018.b470eecf764a"))
	var roster: Array=session.state.journey.draft.get("roster",[]).duplicate()
	label(dialog.box,I18n.t("baseline018.716816ae3d4e"))
	for id: String in session.state.journey.recruited:
		var a: Dictionary=session.state.actors[id]
		if session.state.product.withdrawn.has(id):continue
		var toggle:=CheckButton.new();toggle.text=actor_name(id)+I18n.t("baseline018.14c4d4c22d9e")%[maxi(0,a.fatigue-12),maxi(0,a.fatigue-12)+18];toggle.button_pressed=roster.has(id);dialog.box.add_child(toggle)
		toggle.toggled.connect(func(on: bool):
			if on and not roster.has(id):roster.append(id)
			elif not on:roster.erase(id))
	button(dialog.box,I18n.t("baseline018.86b4a0ac6616"),func():dialog.window.queue_free();propose("plan_next_roster",{"roster":roster}))
func show_night_review() -> void:
	var dialog:=modal(I18n.t("baseline018.07f04b8b6e99"))
	label(dialog.box,I18n.t("baseline018.d6866791de57")%[session.state.campaign.day,session.state.campaign.projects,session.state.campaign.talked.size()])
	if session.state.campaign.day==23:
		label(dialog.box,I18n.t("baseline018.fb149873289e"))
		for id: String in session.state.full_campaign.contracts:
			var contract: Dictionary=session.state.full_campaign.contracts[id]
			if not contract.fulfilled:label(dialog.box,actor_name(id)+" · "+(I18n.t("baseline018.2a50f442d19a") if contract.get("interrupted_by_injury",false) else (I18n.t("baseline018.3b98164d604b") if contract.get("breached",false) else I18n.t("baseline018.bf513a1c326e"))))
		label(dialog.box,I18n.t("baseline018.5ab7b400e6b1")+session.state.full_campaign.route)
	button(dialog.box,I18n.t("baseline018.e6f809da1227"),func():dialog.window.queue_free();propose("finish_evening",{}))

func show_conflict_notice() -> void:
	if conflict_notices.is_empty() or feedback_active():return
	var entry: Dictionary=conflict_notices.pop_front()
	var actor: String=entry.pair.split(">")[0]
	var target: String=entry.pair.split(">")[1]
	var dialog:=modal(actor_name(actor)+I18n.t("baseline018.fa93d44a3ff7"))
	sound.ambience("grave")
	dialog.window.tree_exited.connect(func():sound.ambience(music_context()))
	var portrait=Art.picture(Art.portrait(actor,"firm"),Vector2(0,200));portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;dialog.box.add_child(portrait)
	label(dialog.box,I18n.t("baseline018.72dcac11836b")+(I18n.t("baseline018.36caf75886a3") if target=="leader" else actor_name(target))+" · "+entry.reason)
	label(dialog.box,session.content.actors[actor].rupture)
	label(dialog.box,I18n.t("baseline018.00d41827a37a"))
	button(dialog.box,I18n.t("baseline018.eb18d0a2363c"),dialog.window.queue_free)

func cooperation_details(payload: Dictionary) -> Array[String]:
	var rows: Array[String]=[]
	for spec: Dictionary in session.content.domains.progression_relationship.protocols:
		if spec.id==payload.get("protocol",""):
			if payload.has("post"):rows.append(I18n.t("baseline018.6f9a270bb73c"))
			else:rows.append(spec.name+"："+spec.cost+"。"+spec.effect)
			rows.append(I18n.t("baseline018.559e3a554511")+spec.baseline)
	for id: String in [selected,str(payload.get("partner",""))]:
		if not session.content.actors.has(id):continue
		var other: String=str(payload.get("partner","")) if id==selected else selected
		for target: String in [other,"leader"]:
			var r: Dictionary=session.state.social.get(id+">"+target,{})
			if r.get("band","") in ["conditional","rupture"]:rows.append(actor_name(id)+I18n.t("baseline018.74570c72706a")+(I18n.t("baseline018.36caf75886a3") if target=="leader" else actor_name(target))+I18n.t("baseline018.1582d6de505a")+session.content.actors[id].rupture)
	return rows

func music_context() -> String:
	if title_screen:return "title"
	var s: Dictionary=session.state
	if s.chapter_one.finished:return "ending"
	if s.campaign.phase=="battle" or feedback_active():
		var urgent: bool=s.battle.round>=s.battle.limit-3
		for h: Dictionary in s.battle.heroes.values():
			if h.downed or (not h.left and h.hp<=3):urgent=true
		return "battle_high" if urgent else "battle"
	return "camp"
