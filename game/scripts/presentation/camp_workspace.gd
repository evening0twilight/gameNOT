extends RefCounted
## Nightly priorities, then people. Optional administration lives in one drawer.
static func show(ui: Control,box: VBoxContainer) -> void:
	var s: Dictionary=ui.session.state
	var top:=HBoxContainer.new();box.add_child(top)
	ui.label(top,ui.I18n.t("quality.camp_heading")).add_theme_color_override("font_color",ui.GOLD)
	var advance: Button=ui.button(top,ui.I18n.t("p2.prepare_next"),ui.show_night_review)
	advance.custom_minimum_size.x=260;advance.add_theme_stylebox_override("normal",ui.surface(Color("35524c"),8,ui.TEAL))
	ui.label(box,ui.I18n.t("ui.10a3c2a27fcc")%[s.campaign.projects,s.campaign.talked.size()]).add_theme_font_size_override("font_size",maxi(14,ui.font_size-4))
	ui.label(box,ui.I18n.t("quality.camp_optional")).add_theme_color_override("font_color",ui.MUTED)
	if s.campaign.day==23:ui.label(box,ui.I18n.t("p3.final_warning")).add_theme_color_override("font_color",ui.GOLD)
	ui.Screens.recruits(ui,box)
	var nav:=HFlowContainer.new();box.add_child(nav)
	ui.button(nav,ui.I18n.t("quality.camp_story"),func():var window: Dictionary=ui.modal(ui.I18n.t("p2.stories"));ui.render_story_list(window.box))
	ui.button(nav,ui.I18n.t("baseline018.e8282617ef13"),ui.plan_next_roster)
	ui.button(nav,ui.I18n.t("p4.equipment_facilities"),ui.show_workshop)
	ui.button(nav,ui.I18n.t("quality.camp_more"),func():administration(ui))
	ui.button(nav,ui.I18n.t("journey.city_button"),func():ui.Screens.city(ui))
	ui.button(nav,ui.I18n.t("baseline018.00768fb3f70c"),func():ui.Screens.relationships(ui))
	for control: Control in nav.get_children():control.add_theme_font_size_override("font_size",maxi(14,ui.font_size-4));control.custom_minimum_size.x=156
	var cards:=GridContainer.new();cards.columns=3 if ui.size.x>=1100 else 2;cards.add_theme_constant_override("h_separation",12);cards.add_theme_constant_override("v_separation",12);box.add_child(cards)
	for id: String in s.journey.recruited:
		var a: Dictionary=s.actors[id]
		var card:=PanelContainer.new();card.size_flags_horizontal=Control.SIZE_EXPAND_FILL;card.add_theme_stylebox_override("panel",ui.surface(ui.SURFACE,10));cards.add_child(card)
		var contents:=VBoxContainer.new();contents.add_theme_constant_override("separation",8);card.add_child(contents)
		var row:=HBoxContainer.new();contents.add_child(row)
		row.add_child(ui.Art.character(id,"camp","tired" if a.fatigue>=70 else "neutral",Vector2(76,96),true))
		var details:=VBoxContainer.new();details.size_flags_horizontal=Control.SIZE_EXPAND_FILL;row.add_child(details)
		ui.label(details,ui.actor_name(id)+" · Lv%d"%ui.Rules.Specialties.level(a.xp)).add_theme_color_override("font_color",ui.TEAL)
		ui.label(details,ui.I18n.t("quality.camp_rest")%[a.fatigue,ui.Crew.overnight_fatigue(s,id,a.fatigue)]).add_theme_font_size_override("font_size",maxi(14,ui.font_size-4))
		var status: String=ui.I18n.t("quality.camp_ready") if s.journey.draft.get("roster",[]).has(id) else ui.I18n.t("quality.camp_reserve")
		if s.product.withdrawn.has(id):status=ui.I18n.t("p4.withdrawn")%ui.actor_name(id)
		elif a.ready_day>s.campaign.day:status=ui.I18n.t("baseline018.d36240265d5c")%a.ready_day
		ui.label(details,status).add_theme_font_size_override("font_size",maxi(14,ui.font_size-4))
		ui.button(contents,ui.I18n.t("quality.camp_person"),func():ui.Screens.profile(ui,id))
		if not s.product.withdrawn.has(id):
			ui.button(contents,ui.I18n.t("quality.camp_talk"),func():short_talk(ui,id))

static func short_talk(ui: Control,id: String) -> void:
	var dialog: Dictionary=ui.modal(ui.I18n.t("quality.camp_talk_title")%ui.actor_name(id))
	for target: String in ui.session.state.journey.recruited:
		if target==id:continue
		var command: Dictionary={"command_id":"talk-preview","expected_revision":ui.session.state.revision,"actor_id":id,"kind":"short_talk","payload":{"target":target},"root_decision_id":"talk-preview"}
		var preview: Dictionary=ui.session.preview(command)
		var row: Button=ui.button(dialog.box,ui.actor_name(target),func():dialog.window.hide();dialog.window.queue_free();ui.selected=id;ui.propose("short_talk",{"target":target}))
		row.disabled=not preview.ok
		if not preview.ok:ui.label(dialog.box,ui.error_text(preview.error_code)).add_theme_color_override("font_color",ui.MUTED)

static func administration(ui: Control) -> void:
	var dialog: Dictionary=ui.modal(ui.I18n.t("quality.camp_more"))
	var projects:=HFlowContainer.new();dialog.box.add_child(projects)
	for kind: String in ["train","treat","rest"]:ui.button(projects,ui.I18n.t("p2.group")%ui.action_name(kind),func():ui.group_project(kind))
	ui.Screens.operations(ui,dialog.box)
	ui.render_campaign_options(dialog.box)
	ui.render_mentors(dialog.box)
	ui.button(dialog.box,ui.I18n.t("journey.reactions"),func():var report: Dictionary=ui.modal(ui.I18n.t("journey.reactions"));ui.Screens.appraisal_log(ui,report.box))
	ui.button(dialog.box,ui.I18n.t("p4.history"),ui.show_history_repair)
