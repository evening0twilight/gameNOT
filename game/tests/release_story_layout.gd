extends "res://tests/firstshift_review.gd"
const Screen=preload("res://scripts/presentation/story_screen.gd")
const Journey=preload("res://scripts/presentation/journey_presentation.gd")
var captures: Array=[]
var geometry: Array=[]
var evidence_sources=[
	"outputs/firstshift-day02-story.json",
	"outputs/baseline018-linked-day24.json",
	"outputs/p4art-benefits-growth-mo-day23.json",
]
func load_save(path: String) -> void:
	var envelope: Variant=JSON.parse_string(FileAccess.get_file_as_string("res://../"+path))
	var loaded: Dictionary=ui.session.store.validate(envelope,ui.session.content)
	check(loaded.ok,"retained production save "+path)
	ui.session.state=loaded.state

func window() -> Window:
	for child: Node in ui.get_children():
		if child is Window and child.visible and not child.is_queued_for_deletion():return child
	return null

func settle_ui() -> void:
	for tick: int in range(5):await process_frame
	if DisplayServer.get_name()!="headless":RenderingServer.force_draw(false)

func inspect(id: String,capture: bool) -> void:
	await settle_ui()
	var dialog: Window=window()
	check(is_instance_valid(dialog),"active window "+id)
	if dialog==null:return
	for control: Button in dialog.find_children("*","Button",true,false):
		if not control.is_visible_in_tree():continue
		var rect: Rect2=control.get_global_rect()
		if DisplayServer.get_name()!="headless":
			check(rect.position.x>=0 and rect.end.x<=dialog.size.x and rect.end.y<=dialog.size.y-12,"visible choice "+id+" "+control.text)
			geometry.append({"view":id,"label":control.text,"disabled":control.disabled,"y_end":roundi(rect.end.y),"window_height":dialog.size.y})
	if capture and DisplayServer.get_name()!="headless":
		var path: String="outputs/p4release-20261119-story-"+id+".png"
		canvas.get_texture().get_image().save_png("res://../"+path)
		captures.append(path)

func real_archive(source: String,id: String) -> void:
	load_save(source)
	var before: String=ui.session.store.canonical(ui.session.state)
	ui.render()
	ui.show_journal()
	var journal: Window=window()
	for control: Button in journal.find_children("*","Button",true,false):
		if control.text==ui.I18n.content("scenes",id,"title",id):control.pressed.emit();break
	await settle_ui()
	var original: Window=window()
	check(original!=journal,"archive opens saved scene")
	for label_key: String in ["journey.next","story.transcript","journey.full","journey.previous"]:
		for control: Button in original.find_children("*","Button",true,false):
			if control.text==ui.I18n.t(label_key):
				control.pressed.emit()
				break
		await settle_ui()
		check(window()==original,"page retains journal navigation")
		if label_key=="story.transcript":
			await inspect("archive-"+id+"-"+ui.I18n.locale,true)
	for child: Button in original.find_children("*","Button",true,false):
		if child.text==ui.I18n.t("quality.story_close"):child.pressed.emit();break
	await settle_ui()
	check(window()==journal,"previous journal restored after page turns")
	check(before==ui.session.store.canonical(ui.session.state),"read-only archive preserves campaign")
	close_windows()
	await process_frame

func pending_choice(id: String,font: int) -> void:
	# This is a copied campaign with an injected unanswered scene. No claim
	# that the participant's state/choices were earned in this save.
	load_save(evidence_sources[2])
	var s: Dictionary=ui.session.state
	var node: Dictionary=ui.Stories.nodes(ui.session.content)[id]
	for prereq: String in node.get("requires_resolved",[]):s.chapter_one.scenes[prereq]={"seen":true,"choice":"","status":"resolved","day":s.campaign.day}
	s.chapter_one.scenes[id]={"seen":true,"choice":"","status":"seen","day":s.campaign.day,"delivery":{"mode":"present","day":s.campaign.day,"injured":[],"absent":[]}}
	s.full_campaign.contracts.erase(node.actor)
	ui.font_size=font
	ui.render()
	var view: Dictionary=Journey.scene(s,ui.session.content,id)
	Screen.show(ui,id,view.pages.size()-1)
	var name_tag: String="fixture-"+id+"-"+ui.I18n.locale+"-"+str(font)
	await inspect(name_tag,font==24 and id=="P_lin_3")
	var unavailable: int=0
	for control: Button in window().find_children("*","Button",true,false):
		if control.disabled:unavailable+=1
	check(unavailable>=1,"proof or creation deadline visible before proposing "+name_tag)
	close_windows()
	await process_frame

func alternate_delivery(locale: String) -> void:
	var id: String="R10"
	for mode: String in ["recovery","letter"]:
		load_save(evidence_sources[2])
		var s: Dictionary=ui.session.state
		var injured: Array=["su"] if mode=="recovery" else []
		var absent: Array=["mo"] if mode=="letter" else []
		s.chapter_one.scenes[id]={"seen":true,"choice":"","status":"resolved" if mode=="letter" else "seen","day":23,"delivery":{"mode":mode,"day":23,"injured":injured,"absent":absent}}
		ui.font_size=24
		ui.render()
		var view: Dictionary=Journey.scene(s,ui.session.content,id)
		Screen.show(ui,id,view.pages.size()-1)
		await inspect("fixture-"+mode+"-"+locale,locale=="en")
		if mode=="letter":
			var found: bool=false
			for label: Label in window().find_children("*","Label",true,false):
				if label.text==ui.I18n.t("story.duty_log"):found=true
			check(found,"absent negotiation shown as duty log")
		close_windows()
		await process_frame

func no_pending_response(locale: String) -> void:
	load_save(evidence_sources[0])
	var s: Dictionary=ui.session.state
	# Real recorded opening, isolated unresolved copy outside camp.
	s.chapter_one.scenes.P_lin_1.choice=""
	s.chapter_one.scenes.P_lin_1.status="seen"
	s.campaign.phase="briefing"
	ui.render()
	var view: Dictionary=Journey.scene(s,ui.session.content,"P_lin_1")
	Screen.show(ui,"P_lin_1",view.pages.size()-1,true)
	await settle_ui()
	var found: bool=false
	for label: Label in window().find_children("*","Label",true,false):
		if label.text==ui.I18n.t("story.answer_at_camp"):found=true
	check(found,"read-only response notice outside camp "+locale)
	for button: Button in window().find_children("*","Button",true,false):
		check(button.text!=ui.I18n.t("p2.story_defer"),"no defer command outside camp "+locale)
	close_windows()
	await process_frame

func run() -> void:
	canvas=SubViewport.new()
	canvas.size=Vector2i(1280,720)
	canvas.gui_embed_subwindows=true
	canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	ui=load("res://scenes/main.tscn").instantiate()
	canvas.add_child(ui)
	ui.reduced_motion=true
	ui.title_screen=false
	for locale: String in ["zh_CN","zh_TW","en"]:
		ui.I18n.locale=locale
		ui.font_size=20
		await real_archive(evidence_sources[0],"P_lin_1")
		await real_archive(evidence_sources[1],"R04")
		for font: int in [16,20,24]:
			for id: String in ["P_lin_3","P_chen_2"]:await pending_choice(id,font)
		await alternate_delivery(locale)
		await no_pending_response(locale)
	var f:=FileAccess.open("res://../outputs/p4release-20261119-story-layout"+("-gpu" if DisplayServer.get_name()!="headless" else "")+".json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"checks":checks,"failures":failures,"runtime":DisplayServer.get_name(),"captures":captures,"sources":evidence_sources,"button_geometry":geometry,"scope":"real saved day 2/day 24 journal replay; isolated day 23 decisions; 1280x720 three locales and three font sizes. No human or Windows evidence."},"  ")+"\n")
	f.close()
	ui.sound.stop_audio()
	ui.queue_free()
	await process_frame
	print("RELEASE_STORY_UI: checks=%d failures=%d"%[checks,failures.size()])
	quit(0 if failures.is_empty() else 1)
