extends RefCounted
const Journey=preload("res://scripts/presentation/journey_presentation.gd")
static func show(ui: Control,id: String,index: int=0,summary: bool=false) -> void:
	var view: Dictionary=Journey.scene(ui.session.state,ui.session.content,id)
	var node: Dictionary=view.node;var record: Dictionary=view.record
	var dialog: Dictionary=ui.modal(node.title);var box: VBoxContainer=dialog.box
	ui.sound.scene_music(dialog.window,"grave" if view.tone=="grave" or view.delivery.mode=="letter" else "daily")
	box.add_child(ui.Art.picture(ui.Art.narrative(view.location),Vector2(0,170)))
	ui.label(box,ui.I18n.t("journey.delivery."+view.delivery.mode)%view.delivery.day).add_theme_color_override("font_color",ui.MUTED)
	var page: Dictionary=view.pages[clampi(index,0,view.pages.size()-1)]
	var stage:=HBoxContainer.new();stage.add_theme_constant_override("separation",18);box.add_child(stage)
	if not page.speaker.is_empty():
		var portrait=ui.Art.character(page.speaker,"camp",page.expressions.get(page.speaker,"neutral"),Vector2(180,240));portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;stage.add_child(portrait)
	var text_box:=VBoxContainer.new();text_box.size_flags_horizontal=Control.SIZE_EXPAND_FILL;stage.add_child(text_box)
	if not page.speaker.is_empty():ui.label(text_box,ui.actor_name(page.speaker)).add_theme_color_override("font_color",ui.TEAL)
	var summary_lines: Array[String]=[]
	for part: Dictionary in view.pages:
		summary_lines.append(part.text)
	var summary_text: String="\n\n".join(summary_lines)
	ui.label(text_box,summary_text if summary else page.text)
	# Other participant keeps an independent listening expression.
	for actor: String in page.expressions:
		if actor==page.speaker:continue
		var listener=ui.Art.character(actor,"camp",page.expressions[actor],Vector2(100,130),true);listener.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;stage.add_child(listener)
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
		for choice: Dictionary in node.choices:
			ui.button(box,choice.label,func():dialog.window.queue_free();ui.propose("story_choice",{"node":id,"choice":choice.id}))
		ui.button(box,ui.I18n.t("p2.story_defer"),func():dialog.window.queue_free();ui.propose("story_defer",{"node":id}))
