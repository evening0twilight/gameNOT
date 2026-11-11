extends RefCounted
const Journey=preload("res://scripts/presentation/journey_presentation.gd")
const Crew=preload("res://scripts/domain/crew_journey.gd")
const Full=preload("res://scripts/domain/full_campaign.gd")
const Product=preload("res://scripts/domain/product_systems.gd")
const Specialties=preload("res://scripts/domain/p1_specialties.gd")
static func column(parent: Node) -> VBoxContainer:
	var scroll:=ScrollContainer.new();scroll.size_flags_horizontal=Control.SIZE_EXPAND_FILL;scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL;scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;parent.add_child(scroll)
	var box:=VBoxContainer.new();box.size_flags_horizontal=Control.SIZE_EXPAND_FILL;box.add_theme_constant_override("separation",12);scroll.add_child(box);return box
static func title(ui: Control,parent: Node) -> void:
	var box:=column(parent)
	box.add_child(ui.Art.picture(ui.Art.narrative("office"),Vector2(0,280)))
	ui.label(box,ui.I18n.t("baseline018.ea0219b09f08")).add_theme_font_size_override("font_size",36)
	ui.label(box,ui.I18n.t("baseline018.fc93cc6a7c50"))
	ui.button(box,ui.I18n.t("baseline018.b5fbc7830ee2")%ui.session.state.campaign.day,func():ui.title_screen=false;ui.render()).disabled=not FileAccess.file_exists(ui.session.path)
	ui.button(box,ui.I18n.t("baseline018.383860206bb4"),ui.new_campaign)
	ui.button(box,ui.I18n.t("baseline018.fbe77b429bd8"),ui.campaign_picker)
	ui.button(box,ui.I18n.t("baseline018.f0c4b4c6f9cd"),ui.show_help)
	ui.button(box,ui.I18n.t("baseline018.db78bb2404bf"),ui.audio_settings)
	ui.button(box,ui.I18n.t("baseline018.dbc0fe120d31"),func():ui.get_tree().quit())
static func recruits(ui: Control,box: VBoxContainer) -> void:
	var s: Dictionary=ui.session.state
	var row:=HFlowContainer.new();box.add_child(row)
	for id: String in s.journey.recruited:
		if s.journey.introduced.has(id):continue
		ui.button(row,(ui.I18n.t("baseline018.f717c56fae7c") if s.actors[id].join==1 else ui.I18n.t("baseline018.48df6e63191b"))+ui.actor_name(id),func():introduction(ui,id))
static func introduction(ui: Control,id: String) -> void:
	var actor: Dictionary=ui.session.content.actors[id]
	var contact: Dictionary=Journey.contact(id)
	var dialog: Dictionary=ui.modal(actor.name+ui.I18n.t("baseline018.f04a519e103e"))
	var stage:=HBoxContainer.new();stage.add_theme_constant_override("separation",18);dialog.box.add_child(stage)
	var picture=ui.Art.picture(ui.Art.outfit(id,"work"),Vector2(200,260));picture.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;stage.add_child(picture)
	var speech:=VBoxContainer.new();speech.size_flags_horizontal=Control.SIZE_EXPAND_FILL;stage.add_child(speech)
	ui.label(speech,contact.entrance).add_theme_color_override("font_color",ui.MUTED)
	ui.label(speech,actor.name+"："+contact.line)
	ui.label(speech,contact.use).add_theme_color_override("font_color",ui.TEAL)
	ui.label(dialog.box,contact.tradeoff)
	ui.label(dialog.box,actor.name+"："+contact.everyday)
	var roster: Array=ui.session.state.journey.draft.get("roster",[]).duplicate()
	if roster.has(id):
		ui.label(dialog.box,ui.I18n.t("journey.already_planned"))
	elif roster.size()<3:
		var chosen: Array=roster.duplicate();chosen.append(id)
		ui.button(dialog.box,ui.I18n.t("journey.plan_member"),func():dialog.window.queue_free();ui.propose("acknowledge_recruit",{"actor":id,"roster":chosen}))
	else:
		ui.label(dialog.box,ui.I18n.t("journey.replace_notice"))
		var choices:=HFlowContainer.new();dialog.box.add_child(choices)
		for previous: String in roster:
			var chosen: Array=roster.duplicate();chosen[chosen.find(previous)]=id
			ui.button(choices,ui.I18n.t("journey.replace_member")%ui.actor_name(previous),func():dialog.window.queue_free();ui.propose("acknowledge_recruit",{"actor":id,"roster":chosen}))
	ui.button(dialog.box,ui.I18n.t("journey.keep_roster"),func():dialog.window.queue_free();ui.propose("acknowledge_recruit",{"actor":id}))
	ui.button(dialog.box,ui.I18n.t("baseline018.29a93d2eb324"),func():profile(ui,id))
static func briefing(ui: Control,parent: Node) -> void:
	var s: Dictionary=ui.session.state
	var frame:=VBoxContainer.new();frame.size_flags_horizontal=Control.SIZE_EXPAND_FILL;parent.add_child(frame)
	var columns:=HBoxContainer.new();columns.size_flags_vertical=Control.SIZE_EXPAND_FILL;columns.add_theme_constant_override("separation",20);frame.add_child(columns)
	var box:=column(columns)
	box.get_parent().size_flags_stretch_ratio=.85
	var mission: String=s.journey.next_mission
	var board: Dictionary=ui.session.content.boards[mission]
	ui.label(box,ui.I18n.t("baseline018.fd006c90fe24")%[s.campaign.day,board.title]).add_theme_color_override("font_color",ui.TEAL)
	box.add_child(ui.Art.picture(ui.Art.environment(board.location),Vector2(0,140)))
	ui.label(box,board.decision)
	var context:=VBoxContainer.new();box.add_child(context)
	for line: String in Journey.situation(s,ui.session.content,mission):ui.label(context,line)
	ui.button(context,ui.I18n.t("journey.city_button"),func():city(ui))
	for group: Array in Full.groups(s,board):
		var names: Array[String]=[]
		for id: String in group:
			for obj: Dictionary in board.objectives:
				if obj.id==id:names.append(obj.label)
		ui.label(box,ui.I18n.t("baseline018.1a78ccb9b0d5")+" / ".join(names))
	ui.label(box,ui.I18n.t("baseline018.c06312b8d2a7"))
	var draft: Dictionary=s.journey.draft.duplicate(true)
	var settings: Dictionary=ui.difficulty_controls(box,board,str(draft.get("difficulty",s.campaign.difficulty)))
	box=column(columns)
	box.get_parent().size_flags_stretch_ratio=1.15
	recruits(ui,box)
	var roster: Array=draft.get("roster",[]).duplicate()
	var refresh_dispatch: Array=[func():pass]
	var equipment_widgets: Dictionary={}
	var row:=HFlowContainer.new();box.add_child(row)
	ui.button(row,ui.I18n.t("baseline018.53249668124e"),func():roster_page(ui))
	ui.button(row,ui.I18n.t("baseline018.00768fb3f70c"),func():relationships(ui))
	ui.label(box,ui.I18n.t("journey.roster_help"))
	ui.label(box,ui.I18n.t("baseline018.5039e6e1cbdb"))
	for id: String in s.actors:
		if not Crew.joined(s,id):continue
		var a: Dictionary=s.actors[id]
		var choice:=CheckButton.new();choice.text=ui.I18n.t("baseline018.64c144e5ce1f")%[a.name,Specialties.level(a.xp),a.fatigue,a.fatigue+18,ui.I18n.t("baseline018.250bfc665c5d") if s.product.withdrawn.has(id) else (ui.I18n.t("baseline018.d36240265d5c")%a.ready_day if a.ready_day>s.campaign.day else ui.I18n.t("baseline018.bdb7394221de"))]
		choice.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
		choice.button_pressed=roster.has(id);choice.disabled=not Crew.ready_ids(s).has(id)
		var actor_row:=HBoxContainer.new();box.add_child(actor_row)
		var face=ui.Art.picture(ui.Art.portrait(id,"tired" if a.fatigue>=70 else "neutral"),Vector2(58,70));face.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;actor_row.add_child(face)
		choice.size_flags_horizontal=Control.SIZE_EXPAND_FILL;actor_row.add_child(choice)
		ui.label(box,Journey.contact(id).use).add_theme_color_override("font_color",ui.MUTED)
		choice.toggled.connect(func(on: bool):
			if on and not roster.has(id):roster.append(id)
			elif not on:roster.erase(id)
			refresh_dispatch[0].call())
		var equipment:=HFlowContainer.new();box.add_child(equipment)
		ui.button(equipment,ui.I18n.t("baseline018.db8db0530432")+a.name,func():profile(ui,id))
		for slot: String in ["tool","support"]:
			var option:=OptionButton.new();option.add_item(ui.I18n.t("baseline018.7d0343ff9364") if slot=="tool" else ui.I18n.t("baseline018.2454c5bf29ea"));option.set_item_metadata(0,"");equipment.add_child(option)
			for item: String in s.product.owned:
				var definition: Dictionary=Product.item(ui.session.content,item)
				if definition.slot!=slot:continue
				option.add_item(ui.I18n.t("p4.tool."+item));option.set_item_metadata(option.item_count-1,item)
				if draft.loadout[id][slot]==item:option.select(option.item_count-1)
			equipment_widgets[id+":"+slot]=option
			option.item_selected.connect(func(i: int):
				var item: String=str(option.get_item_metadata(i))
				for gear: Dictionary in draft.loadout.values():
					if not item.is_empty() and gear[slot]==item:gear[slot]=""
				draft.loadout[id][slot]=item
				for key: String in equipment_widgets:
					var names: PackedStringArray=key.split(":");var widget: OptionButton=equipment_widgets[key]
					for index: int in range(widget.item_count):
						if widget.get_item_metadata(index)==draft.loadout[names[0]][names[1]]:widget.select(index))
		if Specialties.level(a.xp)>=2:
			var tendency:=OptionButton.new();tendency.add_item(ui.I18n.t("baseline018.1add996d31c5"));tendency.add_item(ui.I18n.t("baseline018.84d17d33b58f"));equipment.add_child(tendency)
			tendency.select(0 if draft.tendencies.get(id,a.tendency)=="work" else 1)
			tendency.item_selected.connect(func(i: int):draft.tendencies[id]="work" if i==0 else "move")
	ui.label(box,ui.I18n.t("baseline018.e1c94d385921"))
	var support:=OptionButton.new();support.add_item(ui.I18n.t("baseline018.49922c9d36c2"));support.set_item_metadata(0,"");box.add_child(support)
	for id: String in s.journey.recruited:
		if s.product.withdrawn.has(id) or s.actors[id].ready_day>s.campaign.day or s.actors[id].fatigue+8>100:continue
		support.add_item(s.actors[id].name);support.set_item_metadata(support.item_count-1,id)
		if draft.get("support","")==id:support.select(support.item_count-1)
	support.item_selected.connect(func(i: int):draft.support=str(support.get_item_metadata(i));refresh_dispatch[0].call())
	ui.label(box,ui.I18n.t("baseline018.c535e1b44b3e")%[s.full_campaign.medicine_stock,Product.pack_limit(s)])
	var medicine:=SpinBox.new();medicine.min_value=0;medicine.max_value=mini(s.full_campaign.medicine_stock,Product.pack_limit(s));medicine.value=draft.get("medicine",0);box.add_child(medicine)
	var dispatch:=CheckButton.new();dispatch.text=ui.I18n.t("baseline018.c8fb6bfa320c");dispatch.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;dispatch.button_pressed=draft.get("dispatch",false);box.add_child(dispatch)
	ui.label(box,ui.I18n.t("baseline018.7fbfe38cc7a7")+str(board.exits)+ui.I18n.t("baseline018.cc68a892e198"))
	refresh_dispatch[0]=func():
		dispatch.disabled=not ui.Rules.Field.dispatch_ready(s,roster,str(draft.get("support",""))) or s.inventory.supplies<2
		if dispatch.disabled:dispatch.button_pressed=false;draft.dispatch=false
	refresh_dispatch[0].call()
	var buttons:=HFlowContainer.new();frame.add_child(buttons)
	var value: Callable=func() -> Dictionary:
		draft.roster=roster;draft.difficulty=settings.difficulty;draft.hard_acknowledged=settings.ack;draft.medicine=int(medicine.value);draft.dispatch=dispatch.button_pressed;return draft
	ui.button(buttons,ui.I18n.t("journey.planning_board"),func():planning_board(ui,value.call()))
	ui.button(buttons,ui.I18n.t("baseline018.957bcad5d107"),func():ui.propose("save_preparation",{"draft":value.call()}))
	ui.button(buttons,ui.I18n.t("baseline018.53d841564e3b"),func():ui.propose("depart",value.call()))

static func roster_page(ui: Control) -> void:
	var dialog: Dictionary=ui.modal(ui.I18n.t("baseline018.001ce34fcf94"))
	for id: String in ui.session.state.actors:
		var a: Dictionary=ui.session.content.actors[id]
		if Crew.joined(ui.session.state,id):ui.button(dialog.box,a.name+" · "+a.role,func():profile(ui,id))
		else:ui.label(dialog.box,ui.I18n.t("baseline018.242c55d95a86")%a.join)
static func profile(ui: Control,id: String) -> void:
	var s: Dictionary=ui.session.state
	var actor: Dictionary=s.actors[id]
	var definition: Dictionary=ui.session.content.actors[id]
	var dialog: Dictionary=ui.modal(definition.name+ui.I18n.t("baseline018.a6f33fcf27e9"));var box: VBoxContainer=dialog.box
	var header:=HBoxContainer.new();box.add_child(header)
	var portrait=ui.Art.picture(ui.Art.outfit(id,"camp" if s.campaign.phase=="camp" else "work"),Vector2(105,160));portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;header.add_child(portrait)
	var summary:=VBoxContainer.new();summary.size_flags_horizontal=Control.SIZE_EXPAND_FILL;header.add_child(summary)
	ui.label(summary,definition.role+"\n"+definition.ordinary)
	ui.label(summary,Journey.contact(id).use).add_theme_color_override("font_color",ui.TEAL)
	ui.label(summary,ui.I18n.t("baseline018.068b208c686a")%[Specialties.level(actor.xp),actor.xp,Full.stages(s,id),actor.fatigue,actor.stress,actor.self_load,actor.ready_day])
	var next_level: int=mini(6,Specialties.level(actor.xp)+1)
	if actor.xp<100:ui.label(box,ui.I18n.t("journey.next_level")%[next_level,[0,0,12,28,48,72,100][next_level]-actor.xp])
	var load_band: int=s.appraisal.self_bands.get(id,0)
	if load_band>0:ui.label(box,ui.I18n.t("baseline018.efab689db8a5")+(ui.I18n.t("baseline018.25f65a583717") if load_band==1 else ui.I18n.t("baseline018.6b7908bc340e"))+ui.I18n.t("baseline018.2b82b47ec419"))
	var planned: bool=s.journey.draft.get("roster",[]).has(id)
	ui.label(box,ui.I18n.t("baseline018.4772c273d30f")+(s.journey.next_mission+ui.I18n.t("baseline018.be5dbf469d2d") if planned and s.journey.next_mission!="M%02d"%s.chapter_one.main_completed else ui.I18n.t("baseline018.1bf6c99127c2")))
	if s.campaign.phase=="camp":
		ui.label(box,ui.I18n.t("baseline018.994e29687fb9")%(2-s.campaign.projects))
		for kind: String in ["train","rest","treat"]:
			var command: Dictionary={"command_id":"comparison","expected_revision":s.revision,"kind":kind,"actor_id":id,"payload":{},"root_decision_id":"comparison"}
			var preview: Dictionary=ui.session.preview(command)
			if preview.ok:
				var after: Dictionary=preview.next_state.actors[id]
				ui.label(box,ui.I18n.t("baseline018.64392ceb9129")%[ui.action_name(kind),actor.xp,after.xp,actor.fatigue,after.fatigue,Crew.overnight_fatigue(s,id,after.fatigue),Crew.overnight_fatigue(s,id,after.fatigue)+18,ui.resource_text(preview.costs.resources)])
				if kind=="train" and Specialties.level(after.xp)>Specialties.level(actor.xp):
					for ability: Dictionary in ui.session.content.domains.abilities:
						if ability.actor==id and ability.level>Specialties.level(actor.xp) and ability.level<=Specialties.level(after.xp):ui.label(box,ui.I18n.t("journey.unlock_now")%ability.name).add_theme_color_override("font_color",ui.TEAL)
				ui.button(box,ui.I18n.t("baseline018.13d61fea9f17")+ui.action_name(kind),func():dialog.window.queue_free();ui.selected=id;ui.propose(kind,{}))
			else:
				var reason: String=ui.error_text(preview.error_code)
				if kind=="train" and preview.error_code=="training_unavailable":
					reason=ui.I18n.t("baseline018.0f02323da7b3")%actor.ready_day if actor.ready_day>s.campaign.day else (ui.I18n.t("baseline018.ab7962e71a04") if actor.xp>=100 else (ui.I18n.t("baseline018.68a7c505e506") if actor.fatigue+6>100 else ui.I18n.t("baseline018.952aabe81ebb")))
				ui.label(box,ui.action_name(kind)+"："+reason)
		ui.label(box,ui.I18n.t("baseline018.27fdbc9a6954")%[actor.xp,Crew.overnight_fatigue(s,id,actor.fatigue)])
	ui.button(box,ui.I18n.t("baseline018.c9d3731e56af"),func():relationships(ui,id))
	ui.label(box,Journey.contact(id).tradeoff)
	ui.label(box,ui.I18n.t("journey.growth_path"))
	for a: Dictionary in ui.session.content.domains.abilities:
		if a.actor!=id:continue
		var ability_row:=HBoxContainer.new();box.add_child(ability_row);ability_row.add_child(ui.Art.picture(ui.Art.icon(a.id),Vector2(30,30)))
		ui.label(ability_row,ui.I18n.t("baseline018.2f233147e7e0")%[a.name,ui.I18n.t("baseline018.e4cf2de9b47f") if Specialties.level(actor.xp)>=a.level else ui.I18n.t("baseline018.716470b2918c")%a.level,a.ap,a.charges_per_mission,a.effect,a.get("level5_effect","")])
static func relationships(ui: Control,observer: String="lin",target: String="xu") -> void:
	var s: Dictionary=ui.session.state
	var dialog: Dictionary=ui.modal(ui.I18n.t("baseline018.daf349b31c7f"));var box: VBoxContainer=dialog.box
	var selectors:=HBoxContainer.new();box.add_child(selectors)
	for side: int in [0,1]:
		var option:=OptionButton.new();selectors.add_child(option)
		var ids: Array=s.journey.recruited.keys()
		if side==1:ids.append("leader")
		for id: String in ids:
			option.add_item(ui.I18n.t("baseline018.36caf75886a3") if id=="leader" else ui.actor_name(id));option.set_item_metadata(option.item_count-1,id)
			if id==(observer if side==0 else target):option.select(option.item_count-1)
		option.item_selected.connect(func(i: int):dialog.window.queue_free();relationships(ui,str(option.get_item_metadata(i)) if side==0 else observer,str(option.get_item_metadata(i)) if side==1 else target))
	if observer==target:ui.label(box,ui.I18n.t("baseline018.20b8265aa749"));return
	for pair: String in [observer+">"+target,target+">"+observer]:
		if not s.social.has(pair):continue
		var r: Dictionary=s.social[pair]
		ui.label(box,ui.I18n.t("baseline018.700a0ad4d3e9")%[ui.actor_name(r.observer),ui.I18n.t("baseline018.36caf75886a3") if r.target=="leader" else ui.actor_name(r.target),r.trust,ui.I18n.t("band."+r.band),ui.I18n.t("baseline018.be70db1b5226") if r.agreement=="cooperate" else ui.I18n.t("baseline018.15b701706924")]).add_theme_color_override("font_color",ui.TEAL)
		ui.label(box,ui.I18n.t("journey.closeness")%r.closeness)
		ui.label(box,ui.I18n.t("baseline018.e7d49fe16476")%r.contribution_missions.size())
		if r.observer in ui.session.content.actors:ui.label(box,ui.I18n.t("baseline018.0325bd20d707")+ui.session.content.actors[r.observer].rupture)
		for memory: Dictionary in r.memories:
			ui.label(box,Journey.memory_text(s,memory)+" · "+ui.I18n.t("journey.repair_stage."+str(memory.stage)))
			if s.campaign.phase=="camp" and memory.stage==0:ui.button(box,ui.I18n.t("baseline018.ca9ebade8289"),func():dialog.window.queue_free();ui.selected=r.observer;ui.propose("acknowledge",{"target":r.target,"event":memory.id}))
			if s.campaign.phase=="camp" and memory.stage==1:
				var proof: String=ui.Rules.Appraisal.repair_proof(s,pair,memory)
				ui.label(box,ui.I18n.t("baseline018.d3aa77639656")+(ui.I18n.t("baseline018.3d4fb1f66fcd") if memory.remedy=="keep_agreement" else ui.I18n.t("baseline018.e6e5bbed0d50")))
				if proof!="":ui.button(box,ui.I18n.t("journey.repair_with_proof"),func():dialog.window.queue_free();ui.selected=r.observer;ui.propose("repair_event",{"target":r.target,"event":memory.id}))
				elif not memory.has("scheduled_mission"):ui.button(box,ui.I18n.t("baseline018.a49c71d191dc"),func():dialog.window.queue_free();ui.selected=r.observer;ui.propose("schedule_repair",{"target":r.target,"event":memory.id}))
	if s.campaign.phase=="camp" and target!="leader":
		for choice: String in ["cooperate","professional"]:ui.button(box,ui.I18n.t("baseline018.00890989dbb2") if choice=="cooperate" else ui.I18n.t("baseline018.b7cc66f80cb0"),func():dialog.window.queue_free();ui.selected=observer;ui.propose("agreement",{"target":target,"choice":choice}))
		ui.button(box,ui.I18n.t("baseline018.a2fef510ad7d"),func():dialog.window.queue_free();ui.selected=observer;ui.propose("short_talk",{"target":target}))
		var offer: Dictionary=ui.Rules.Chapter.mentor_offer(s,observer,target)
		ui.label(box,ui.I18n.t("baseline018.72755f1dca67")%[offer.gain,offer.ordinary])
		if offer.reasons.is_empty():ui.button(box,ui.I18n.t("baseline018.b00f349ad290"),func():dialog.window.queue_free();ui.selected=observer;ui.propose("mentor",{"student":target,"consent":true}))
		else:
			for reason: String in offer.reasons:ui.label(box,ui.I18n.t("baseline018.83133484166c")+reason)
static func manual_slots(ui: Control,saving: bool) -> void:
	var dialog: Dictionary=ui.modal(ui.I18n.t("baseline018.f9cec2dd6db1") if saving else ui.I18n.t("baseline018.186908b78346"))
	if not saving:
		for legacy: String in ["manual.json","manual.json.bak"]:
			var path: String=ui.session.path.get_base_dir().path_join(legacy)
			var loaded: Dictionary=ui.session.store.load_slot(path,ui.session.content)
			if loaded.ok:ui.button(dialog.box,ui.I18n.t("baseline018.a8c6d8f5a849")+legacy,func():
				var saved: Dictionary=ui.session.store.save_slot(ui.session.path,loaded.state,ui.session.content)
				if saved.ok:ui.session.state=loaded.state;ui.title_screen=false;dialog.window.queue_free();ui.render())
	for i: int in range(1,11):
		var path: String=ui.session.path.get_base_dir().path_join("manual-%02d.json"%i)
		var existing: Dictionary=ui.session.store.load_slot(path,ui.session.content)
		var caption: String=ui.I18n.t("baseline018.f857ef1eb9e2")%[i,ui.I18n.t("baseline018.fd6cf6476633")%[existing.state.campaign.day,existing.state.campaign.phase] if existing.ok else (ui.I18n.t("baseline018.e14ac69ed248") if FileAccess.file_exists(path) else ui.I18n.t("baseline018.2f8267a89ad5"))]
		ui.button(dialog.box,caption,func():
			if saving and FileAccess.file_exists(path):
				var confirm: Dictionary=ui.modal(ui.I18n.t("baseline018.262faac2210e")%i)
				ui.label(confirm.box,caption+ui.I18n.t("baseline018.bfc9f55ab3d6"))
				ui.button(confirm.box,ui.I18n.t("baseline018.d788c6261163"),func():confirm.window.queue_free();dialog.window.queue_free();write_manual(ui,path))
			elif saving:dialog.window.queue_free();write_manual(ui,path)
			elif existing.ok:
				var saved: Dictionary=ui.session.store.save_slot(ui.session.path,existing.state,ui.session.content)
				if saved.ok:ui.session.state=existing.state;ui.title_screen=false;dialog.window.queue_free();ui.render()
				else:ui.message=ui.error_text(saved.error_code);ui.render()).disabled=not saving and not existing.ok
static func write_manual(ui: Control,path: String) -> void:
	var result: Dictionary=ui.session.store.save_slot(path,ui.session.state,ui.session.content)
	ui.message=ui.I18n.t("baseline018.68942f066e8c") if result.ok else ui.error_text(result.error_code);ui.render()
static func operations(ui: Control,box: VBoxContainer) -> void:
	var s: Dictionary=ui.session.state
	if s.campaign.phase=="battle":
		var f: Dictionary=s.battle.get("service",{})
		if f.is_empty():return
		ui.label(box,ui.I18n.t("baseline018.51a9a7d05791")+f.definition.label).add_theme_color_override("font_color",ui.GOLD)
		ui.label(box,ui.I18n.t("baseline018.243fc10db942")%[f.ticks,f.definition.consecutive_rounds,f.definition.deadline,ui.I18n.t("baseline018.f28461bb49c8") if f.done else (ui.I18n.t("baseline018.ea3bfa41a837") if f.failed else (ui.I18n.t("baseline018.20690a5dbb29") if ui.Rules.Field.power(s.battle) else ui.I18n.t("baseline018.5feb374bb007"))),f.definition.effect])
		ui.label(box,ui.I18n.t("baseline018.5aaac2f8b4ee"))
		for i: int in range(ui.Rules.Field.posts(s.battle).size()):
			var cell: Array=ui.Rules.Field.posts(s.battle)[i]
			ui.button(box,ui.I18n.t("baseline018.44081200bb96")%[i+1,str(cell)],func():ui.propose("service_watch",{"post":i})).disabled=f.done or f.failed
			ui.button(box,ui.I18n.t("baseline018.fe3a1266e41f")%ui.actor_name(ui.partner),func():ui.propose("protocol",{"protocol":"protected_work","partner":ui.partner,"post":i,"consent":true})).disabled=f.done or f.failed
		if ui.selected=="chen":ui.button(box,ui.I18n.t("baseline018.49762365263d"),func():ui.propose("specialty",{"ability":"chen_3","target":"live_service"}))
		for id: String in f.definition.linked_controls:
			if s.battle.objects[id].completed:ui.button(box,ui.I18n.t("baseline018.9ab3efb440ee")+ui.object_name(id),func():ui.propose("restore_power",{"target":id}))
		return
	if s.campaign.phase!="camp":return
	ui.label(box,ui.I18n.t("baseline018.b3fdfeb37a6b"))
	for id: String in s.operations.assets:
		var asset: Dictionary=s.operations.assets[id]
		ui.label(box,id+" · "+(ui.I18n.t("baseline018.a29c8c5bbb65") if asset.intact else ui.I18n.t("baseline018.059d79eda376"))+" · "+(ui.I18n.t("baseline018.fa8d1e620749") if asset.service_done else ui.I18n.t("baseline018.1dbd7edb4f2e")))
	for id: String in s.operations.facilities:
		var f: Dictionary=s.operations.facilities[id]
		var spec: Dictionary=ui.session.content.domains.field_operations.investments[id]
		ui.label(box,spec.label+ui.I18n.t("baseline018.a158c92d099f")%[spec.first_day,spec.last_day])
		var remaining: int=maxi(0,int(spec.last_day)-maxi(s.campaign.day+1,spec.first_day)+1)
		ui.label(box,ui.I18n.t("baseline018.ac9eba24148d")%[remaining,mini(2-f.used,remaining),16 if s.product.facilities.rest_area>=1 else 12])
		if not f.qualified:
			ui.label(box,ui.I18n.t("baseline018.05fe2c4a84d5"))
			ui.button(box,ui.I18n.t("baseline018.605c80e898ce"),func():ui.propose("repair_field_facility",{"facility":id}))
		elif s.campaign.day>=maxi(spec.first_day,f.available_day) and s.campaign.day<=spec.last_day and f.used<2:
			ui.button(box,ui.I18n.t("baseline018.0672009b88fb"),func():
				var dialog: Dictionary=ui.modal(spec.label);var ids: Array=[]
				for actor: String in s.journey.recruited:
					if s.product.withdrawn.has(actor) or s.actors[actor].ready_day>s.campaign.day:continue
					var toggle:=CheckButton.new();toggle.text=ui.actor_name(actor)+ui.I18n.t("baseline018.ee770115c3f6")%[s.actors[actor].fatigue,s.actors[actor].stress];dialog.box.add_child(toggle)
					toggle.toggled.connect(func(on: bool):
						if on:ids.append(actor)
						else:ids.erase(actor))
				ui.button(dialog.box,ui.I18n.t("baseline018.b94f4080cad2"),func():dialog.window.queue_free();ui.propose("field_assistance",{"facility":id,"participants":ids})))
static func appraisal_log(ui: Control,box: VBoxContainer) -> void:
	var rows: Array=Journey.reactions(ui.session.state,ui.session.content)
	if rows.is_empty():return
	ui.label(box,ui.I18n.t("journey.reactions")).add_theme_color_override("font_color",ui.GOLD)
	var shown: Dictionary={}
	for row: Dictionary in rows:
		var key: String=row.actor+row.fact+row.change
		if shown.has(key):continue
		shown[key]=true
		var panel:=PanelContainer.new();panel.add_theme_stylebox_override("panel",ui.surface(ui.SURFACE,8));box.add_child(panel)
		var inner:=VBoxContainer.new();panel.add_child(inner)
		ui.label(inner,ui.actor_name(row.actor)+" · "+row.fact).add_theme_color_override("font_color",ui.TEAL)
		ui.label(inner,row.change)
		var detail: Label=ui.label(inner,row.concern);detail.visible=false
		ui.button(inner,ui.I18n.t("journey.why"),func():detail.visible=not detail.visible)

static func city(ui: Control) -> void:
	var s: Dictionary=ui.session.state
	var dialog: Dictionary=ui.modal(ui.I18n.t("journey.city_button"))
	for id: String in s.campaign.districts:
		ui.label(dialog.box,ui.I18n.t("journey.district_state")%[Journey.district_name(id),s.campaign.districts[id],s.full_campaign.district_caps[id]])
		for mission: Dictionary in ui.session.content.domains.world.missions:
			if mission.district!=id or not s.campaign.settled.has(mission.id):continue
			var result: Dictionary=s.campaign.settled[mission.id]
			ui.label(dialog.box,ui.session.content.boards[mission.id].title+" · "+ui.I18n.t("journey.outcome."+result.outcome))
	ui.label(dialog.box,ui.I18n.t("journey.side_heading")).add_theme_color_override("font_color",ui.GOLD)
	for board: Dictionary in ui.session.content.boards.values():
		if board.kind!="side" or board.day>s.campaign.day:continue
		var status: String=ui.I18n.t("baseline018.374d13aec7f1") if s.campaign.settled.has(board.id) else (ui.I18n.t("baseline018.ced9778174ce") if s.journey.declined_sides.has(board.id) else (ui.I18n.t("baseline018.2fe0e3339ac4") if s.campaign.day>board.day+1 else ui.I18n.t("baseline018.96c28d7f3839")%mini(23,board.day+1)))
		ui.label(dialog.box,board.title+" · "+status)

static func planning_board(ui: Control,draft: Dictionary) -> void:
	var command: Dictionary={"kind":"depart","actor_id":"lin","payload":draft,"command_id":"planning-board","root_decision_id":"planning-board","expected_revision":ui.session.state.revision}
	var preview: Dictionary=ui.session.preview(command)
	var dialog: Dictionary=ui.modal(ui.I18n.t("journey.planning_board"))
	if not preview.ok:ui.label(dialog.box,ui.error_text(preview.error_code));return
	var state: Dictionary=preview.next_state
	ui.label(dialog.box,ui.I18n.t("journey.planning_help"))
	var members:=HFlowContainer.new();dialog.box.add_child(members)
	var map=ui.BoardView.new();map.state=state;map.board=ui.session.content.boards[state.battle.mission_id];map.selected=state.battle.heroes.keys()[0]
	map.custom_minimum_size=Vector2(450,410);map.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	var info: Label=ui.label(dialog.box,"")
	var choose: Callable=func(id: String):map.selected=id;map.reachable=ui.Rules.reachable_cells(state,id);map.queue_redraw()
	for id: String in state.battle.heroes:ui.button(members,ui.actor_name(id),func():choose.call(id))
	choose.call(map.selected)
	map.validate_hover=func(cell: Array):return ui.Rules.contains_cell(map.reachable,cell)
	map.cell_chosen.connect(func(cell: Array):info.text=map.hover_description(cell))
	dialog.box.add_child(map)
