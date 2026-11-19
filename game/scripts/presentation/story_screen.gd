extends RefCounted
const Journey=preload("res://scripts/presentation/journey_presentation.gd")
static func show(ui: Control,id: String,index: int=0,summary: bool=false) -> void:
	var view: Dictionary=Journey.scene(ui.session.state,ui.session.content,id)
	var dialog: Dictionary=ui.modal(view.node.title)
	var dim:=ColorRect.new();dim.color=Color(.005,.014,.02,.82);dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT);dim.mouse_filter=Control.MOUSE_FILTER_IGNORE;ui.add_child(dim);dialog.window.tree_exiting.connect(dim.queue_free)
	ui.sound.scene_music(dialog.window,"grave" if view.tone=="grave" or view.delivery.mode=="letter" else "daily")
	dialog.window.borderless=true
	dialog.window.popup_centered_clamped(Vector2i(1160,700),.92)
	draw_page(ui,id,view,dialog,index,summary)

static func draw_page(ui: Control,id: String,view: Dictionary,dialog: Dictionary,index: int,summary: bool) -> void:
	var box: VBoxContainer=dialog.box
	for child: Node in box.get_children():
		box.remove_child(child)
		child.queue_free()
	var scroll: ScrollContainer=box.get_parent()
	scroll.scroll_vertical=0
	box.add_theme_constant_override("separation",8)
	var node: Dictionary=view.node
	var record: Dictionary=view.record
	var heading:=HBoxContainer.new();box.add_child(heading)
	ui.label(heading,node.title).add_theme_font_size_override("font_size",28)
	var close: Button=ui.button(heading,ui.I18n.t("quality.story_close"),dialog.window.queue_free);close.add_theme_font_size_override("font_size",16);close.custom_minimum_size.x=160;close.autowrap_mode=TextServer.AUTOWRAP_OFF
	var delivery_label: Label=ui.label(box,ui.I18n.t("journey.delivery."+view.delivery.mode)%view.delivery.day);delivery_label.add_theme_color_override("font_color",ui.MUTED);delivery_label.add_theme_font_size_override("font_size",16)
	var page: Dictionary=view.pages[clampi(index,0,view.pages.size()-1)]
	var decision: bool=record.choice.is_empty() and (summary or index==view.pages.size()-1) and view.delivery.mode!="letter"
	var stage:=PanelContainer.new();stage.custom_minimum_size.y=176 if decision else (360 if summary or view.delivery.mode=="letter" else 460);box.add_child(stage)
	var background=ui.Art.picture(ui.Art.narrative(view.location),Vector2.ZERO);stage.add_child(background)
	var shade:=ColorRect.new();shade.color=Color(.025,.06,.08,.18);shade.mouse_filter=Control.MOUSE_FILTER_IGNORE;stage.add_child(shade)
	var stage_margin:=MarginContainer.new();stage.add_child(stage_margin)
	for side: String in ["left","right","top","bottom"]:stage_margin.add_theme_constant_override("margin_"+side,12 if decision else 20)
	var actors:=HBoxContainer.new();actors.add_theme_constant_override("separation",22);stage_margin.add_child(actors)
	if not summary and not page.speaker.is_empty():
		var portrait=ui.Art.character(page.speaker,"camp",page.expressions.get(page.speaker,"neutral"),Vector2(140,146) if decision else Vector2(285,380),view.delivery.mode=="recovery");actors.add_child(portrait)
	var text_panel:=PanelContainer.new();text_panel.size_flags_horizontal=Control.SIZE_EXPAND_FILL;text_panel.size_flags_vertical=Control.SIZE_EXPAND_FILL if summary else Control.SIZE_SHRINK_END;text_panel.add_theme_stylebox_override("panel",ui.surface(Color(.025,.06,.08,.94),8));actors.add_child(text_panel)
	var text_box:=VBoxContainer.new();text_box.add_theme_constant_override("separation",10 if decision else 18);text_panel.add_child(text_box)
	var speaking: bool=not page.speaker.is_empty() and page.get("speaking",false)
	if not summary:
		var caption: String=ui.actor_name(page.speaker) if speaking else ui.I18n.t("quality.story_letter" if view.delivery.mode=="letter" else "quality.story_narration")
		if view.delivery.mode=="letter" and node.category=="relationship_nodes":
			caption=ui.I18n.t("story.duty_log")
		ui.label(text_box,caption).add_theme_color_override("font_color",ui.TEAL)
	var summary_lines: Array[String]=[]
	for part: Dictionary in view.pages:
		if part.has("beat_before"):summary_lines.append(part.beat_before)
		summary_lines.append(part.text)
		if part.has("beat_after"):summary_lines.append(part.beat_after)
	var summary_text: String="\n\n".join(summary_lines)
	var text: String=page.text.trim_prefix(ui.actor_name(page.speaker)+"：").trim_prefix(ui.actor_name(page.speaker)+":").strip_edges() if speaking else page.text
	if summary:
		var transcript:=ScrollContainer.new()
		transcript.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
		transcript.size_flags_vertical=Control.SIZE_EXPAND_FILL
		text_box.add_child(transcript)
		var reading:=VBoxContainer.new()
		reading.size_flags_horizontal=Control.SIZE_EXPAND_FILL
		transcript.add_child(reading)
		text_box=reading
	if not summary and page.has("beat_before"):ui.label(text_box,page.beat_before).add_theme_color_override("font_color",ui.MUTED)
	var spoken: Label=ui.label(text_box,summary_text if summary else text);spoken.add_theme_font_size_override("font_size",maxi(24,ui.font_size));spoken.add_theme_constant_override("line_spacing",4 if decision else 10)
	if not summary and page.has("beat_after"):
		var beat: Label=ui.label(text_box,page.beat_after);beat.add_theme_color_override("font_color",ui.MUTED)
		if decision:beat.add_theme_font_size_override("font_size",18)
	for actor: String in page.expressions:
		if summary or actor==page.speaker:continue
		var listener=ui.Art.character(actor,"camp",page.expressions[actor],Vector2(110,150),true);listener.size_flags_vertical=Control.SIZE_SHRINK_END;actors.add_child(listener)
	var nav:=HFlowContainer.new();nav.add_theme_constant_override("h_separation",12);box.add_child(nav)
	if index>0 and not summary:ui.button(nav,ui.I18n.t("journey.previous"),func():draw_page(ui,id,view,dialog,index-1,false),"ui_page")
	if index<view.pages.size()-1 and not summary:ui.button(nav,ui.I18n.t("journey.next"),func():draw_page(ui,id,view,dialog,index+1,false),"ui_page")
	var can_answer: bool=record.choice.is_empty() and view.delivery.mode!="letter" and ui.session.state.campaign.phase=="camp" and not ui.session.state.chapter_one.finished
	if can_answer:
		can_answer=ui.Stories.available(ui.session.state,ui.session.content).has(id)
		for actor: String in node.get("actors",[node.get("actor","")]):
			if ui.session.state.product.withdrawn.has(actor):can_answer=false
	var overview_key: String="journey.summary" if can_answer else "story.transcript"
	ui.button(nav,ui.I18n.t("journey.full") if summary else ui.I18n.t(overview_key),func():draw_page(ui,id,view,dialog,index,not summary),"ui_page")
	if not summary:ui.label(nav,"%d / %d"%[index+1,view.pages.size()]).add_theme_font_size_override("font_size",16)
	for control: Node in nav.get_children():
		if control is Button:
			control.add_theme_font_size_override("font_size",16);control.autowrap_mode=TextServer.AUTOWRAP_OFF;control.custom_minimum_size=Vector2(120,36)
	if not summary and index!=view.pages.size()-1:return
	if view.delivery.mode=="letter":
		ui.label(box,ui.I18n.t("story.absent_meeting" if node.category=="relationship_nodes" else "journey.letter_no_reward"))
		return
	if node.category=="personal_nodes":
		var later: Dictionary=ui.StoryFacts.breach(ui.session.state,node.actor,view.script)
		if not later.is_empty():ui.label(box,ui.I18n.t("p4close.later_record")+"\n"+ui.I18n.s(later.line)+"\n"+ui.I18n.s(later.reason))
	if not record.choice.is_empty():
		for choice: Dictionary in node.choices:
			if choice.id==record.choice:
				ui.label(box,ui.I18n.t("quality.story_recap")+" · "+ui.I18n.s(choice.label))
				break
		return
	var state: Dictionary=ui.session.state
	for actor: String in node.get("actors",[node.get("actor","")]):
		if state.product.withdrawn.has(actor):
			ui.label(box,ui.I18n.t("journey.now_absent"))
			return
	if state.chapter_one.finished or not ui.Stories.available(state,ui.session.content).has(id):
		ui.label(box,ui.I18n.t("story.archived_unanswered"))
		return
	if state.campaign.phase!="camp":
		ui.label(box,ui.I18n.t("story.answer_at_camp"))
		return
	if node.get("stage",0)==2:ui.label(box,ui.I18n.t("p3.project_notice"))
	if node.get("stage",0)==3:
		var plan: Dictionary=state.full_campaign.contracts.get(node.actor,{})
		if plan.is_empty():
			ui.label(box,ui.I18n.t("story.no_plan"))
		elif not plan.get("fulfilled",false) and not plan.get("breached",false):
			ui.label(box,view.script.get("unmet",""))
	ui.label(box,ui.I18n.t("quality.story_choices")).add_theme_color_override("font_color",ui.GOLD)
	var options:=GridContainer.new()
	options.columns=2 if dialog.window.size.x>=900 else 1
	options.add_theme_constant_override("h_separation",8)
	options.add_theme_constant_override("v_separation",6)
	box.add_child(options)
	for choice: Dictionary in node.choices:
		var reason: String=ui.Stories.choice_error(state,node,choice)
		var title: String=ui.I18n.s(choice.label)
		if int(choice.get("credits",0))>0:
			title+=" · "+ui.I18n.t("story.credits")%int(choice.credits)
		if reason=="story_unavailable":
			title+=" · "+ui.I18n.t("story.plan_expired")%int(choice.latest_creation_day)
		elif reason=="proof_required":
			title+=" · "+ui.I18n.t("story.requires_proof")
		elif reason=="insufficient_resources":
			title+=" · "+ui.I18n.t("story.short_on_credits")
		elif not reason.is_empty():
			title+=" · "+ui.error_text(reason)
		var response: Button=ui.button(options,title,func():
			dialog.window.hide()
			dialog.window.queue_free()
			ui.propose("story_choice",{"node":id,"choice":choice.id}))
		response.size_flags_horizontal=Control.SIZE_EXPAND_FILL
		response.disabled=not reason.is_empty()
	ui.button(options,ui.I18n.t("p2.story_defer"),func():dialog.window.hide();dialog.window.queue_free();ui.propose("story_defer",{"node":id}))
