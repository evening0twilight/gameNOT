extends RefCounted
const Journey=preload("res://scripts/presentation/journey_presentation.gd")
static func show(ui: Control,id: String,index: int=0,summary: bool=false) -> void:
	var view: Dictionary=Journey.scene(ui.session.state,ui.session.content,id)
	var node: Dictionary=view.node;var record: Dictionary=view.record
	var dialog: Dictionary=ui.modal(node.title);var box: VBoxContainer=dialog.box
	ui.sound.scene_music(dialog.window,"grave" if view.tone=="grave" or view.delivery.mode=="letter" else "daily")
	dialog.window.borderless=true
	dialog.window.popup_centered_clamped(Vector2i(1160,700),.92)
	var heading:=HBoxContainer.new();box.add_child(heading)
	ui.label(heading,node.title).add_theme_font_size_override("font_size",28)
	ui.button(heading,ui.I18n.t("quality.story_close"),dialog.window.queue_free).add_theme_font_size_override("font_size",16)
	ui.label(box,ui.I18n.t("journey.delivery."+view.delivery.mode)%view.delivery.day).add_theme_color_override("font_color",ui.MUTED)
	var page: Dictionary=view.pages[clampi(index,0,view.pages.size()-1)]
	var stage:=PanelContainer.new();stage.custom_minimum_size.y=300;box.add_child(stage)
	var background=ui.Art.picture(ui.Art.narrative(view.location),Vector2.ZERO);stage.add_child(background)
	var shade:=ColorRect.new();shade.color=Color(.025,.06,.08,.45);shade.mouse_filter=Control.MOUSE_FILTER_IGNORE;stage.add_child(shade)
	var stage_margin:=MarginContainer.new();stage.add_child(stage_margin)
	for side: String in ["left","right","top","bottom"]:stage_margin.add_theme_constant_override("margin_"+side,20)
	var actors:=HBoxContainer.new();actors.add_theme_constant_override("separation",22);stage_margin.add_child(actors)
	if not page.speaker.is_empty():
		var portrait=ui.Art.character(page.speaker,"camp",page.expressions.get(page.speaker,"neutral"),Vector2(230,280),view.delivery.mode=="recovery");actors.add_child(portrait)
	var text_panel:=PanelContainer.new();text_panel.size_flags_horizontal=Control.SIZE_EXPAND_FILL;text_panel.add_theme_stylebox_override("panel",ui.surface(Color(.04,.09,.11,.94),8));actors.add_child(text_panel)
	var text_box:=VBoxContainer.new();text_box.add_theme_constant_override("separation",18);text_panel.add_child(text_box)
	var speaking: bool=not page.speaker.is_empty() and page.text.begins_with(ui.actor_name(page.speaker)+"：")
	ui.label(text_box,ui.actor_name(page.speaker) if speaking else ui.I18n.t("quality.story_letter" if view.delivery.mode=="letter" else "quality.story_narration")).add_theme_color_override("font_color",ui.TEAL)
	var summary_lines: Array[String]=[]
	for part: Dictionary in view.pages:
		if part.has("beat_before"):summary_lines.append(part.beat_before)
		summary_lines.append(part.text)
		if part.has("beat_after"):summary_lines.append(part.beat_after)
	var summary_text: String="\n\n".join(summary_lines)
	var text: String=page.text.trim_prefix(ui.actor_name(page.speaker)+"：") if speaking else page.text
	if not summary and page.has("beat_before"):ui.label(text_box,page.beat_before).add_theme_color_override("font_color",ui.MUTED)
	ui.label(text_box,summary_text if summary else text)
	if not summary and page.has("beat_after"):ui.label(text_box,page.beat_after).add_theme_color_override("font_color",ui.MUTED)
	for actor: String in page.expressions:
		if actor==page.speaker:continue
		var listener=ui.Art.character(actor,"camp",page.expressions[actor],Vector2(90,120),true);listener.size_flags_vertical=Control.SIZE_SHRINK_END;actors.add_child(listener)
	var nav:=HFlowContainer.new();box.add_child(nav)
	if index>0 and not summary:ui.button(nav,ui.I18n.t("journey.previous"),func():dialog.window.hide();dialog.window.queue_free();show(ui,id,index-1),"ui_page")
	if index<view.pages.size()-1 and not summary:ui.button(nav,ui.I18n.t("journey.next"),func():dialog.window.hide();dialog.window.queue_free();show(ui,id,index+1),"ui_page")
	ui.button(nav,ui.I18n.t("journey.full") if summary else ui.I18n.t("journey.summary"),func():dialog.window.hide();dialog.window.queue_free();show(ui,id,index,not summary),"ui_page")
	if not summary:ui.label(nav,"%d / %d"%[index+1,view.pages.size()])
	if view.delivery.mode=="letter":
		ui.label(box,ui.I18n.t("journey.letter_no_reward"));return
	if node.has("actor") and node.category=="personal_nodes":
		var later: Dictionary=ui.StoryFacts.breach(ui.session.state,node.actor,view.script)
		if not later.is_empty():ui.label(box,ui.I18n.t("p4close.later_record")+"\n"+later.line+"\n"+later.reason)
	if node.get("stage",0)==2:ui.label(box,ui.I18n.t("p3.project_notice"))
	if node.get("stage",0)==3 and not ui.session.state.full_campaign.contracts.get(node.actor,{}).get("fulfilled",false):ui.label(box,view.script.get("unmet",""))
	if record.choice.is_empty() and not ui.session.state.chapter_one.finished and (summary or index==view.pages.size()-1):
		var absent_now: bool=false
		for actor: String in node.get("actors",[node.get("actor","")]):
			if ui.session.state.product.withdrawn.has(actor):absent_now=true
		if absent_now:ui.label(box,ui.I18n.t("journey.now_absent"));return
		ui.label(box,ui.I18n.t("quality.story_choices")).add_theme_color_override("font_color",ui.GOLD)
		for choice: Dictionary in node.choices:
			ui.button(box,choice.label,func():dialog.window.hide();dialog.window.queue_free();ui.propose("story_choice",{"node":id,"choice":choice.id}))
		ui.button(box,ui.I18n.t("p2.story_defer"),func():dialog.window.hide();dialog.window.queue_free();ui.propose("story_defer",{"node":id}))
