extends SceneTree
## External reader. The wrapper mounts the extracted Windows PCK over an
## empty project directory. Only the supplied retained saves are read from disk.
var problems: Array[String]=[]
var results: Dictionary={}
var ui: Control
var store
var rules
var content: Dictionary

func expect(ok: bool,description: String) -> bool:
	if not ok:
		problems.append(description)
		printerr("PACK PROBE: "+description)
	return ok

func labels(parent: Node) -> Array[String]:
	var text: Array[String]=[]
	for label: Label in parent.find_children("*","Label",true,false):text.append(label.text)
	return text

func saved(path: String) -> Dictionary:
	var envelope: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
	if not expect(envelope is Dictionary,"read save "+path.get_file()):return {}
	var loaded: Dictionary=store.validate(envelope,content)
	if not expect(loaded.ok,"validate "+path.get_file()):return {}
	return loaded.state

func replay_six(state: Dictionary) -> Dictionary:
	var campaign: Dictionary=rules.begin_campaign(content,state.campaign.id)
	var commands: Array=[]
	for value: String in state.commands.values():commands.append(JSON.parse_string(value))
	commands.sort_custom(func(a: Dictionary,b: Dictionary)->bool:return a.expected_revision<b.expected_revision)
	var report: Dictionary={}
	for cmd: Dictionary in commands:
		var day: int=int(campaign.campaign.day)
		if cmd.kind=="finish_evening":
			# The recorded run saved and reopened its slot each night. Serialized
			# dictionaries recover their persisted ordering at this boundary.
			var nightly_slot: String="user://tests/package-probe-%s/night.json"%Time.get_ticks_usec()
			if not expect(store.new().save_slot(nightly_slot,campaign,content).ok,"replay overnight save"):return report
			campaign=store.new().load_slot(nightly_slot,content).state
		if day==6 and cmd.kind=="camp_lesson":
			# The input file is from *after* the lesson. Replay its real accepted
			# commands, then cross an actual save/load boundary before querying.
			var slot: String="user://tests/package-probe-%s/day06-before.json"%Time.get_ticks_usec()
			if not expect(store.new().save_slot(slot,campaign,content).ok,"save earned day-six pre-lesson state"):return report
			var restored: Dictionary=store.new().load_slot(slot,content)
			if not expect(restored.ok,"reload pre-lesson state"):return report
			var offered: String=rules.CampLearning.offer(restored.state,content)
			report={"offered_after_load":offered,"recorded_command_topic":cmd.payload.topic,"revision":campaign.revision,"current_projects_used":campaign.campaign.projects,"restored_equal":store.canonical(campaign)==store.canonical(restored.state)}
			expect(offered=="mentors" and offered==cmd.payload.topic and report.restored_equal,"earned mentor lesson survives save/load before spending a project")
		var preview: Dictionary=rules.reduce(campaign,cmd,content)
		if not expect(preview.ok,"replay stored command "+str(cmd.command_id)+" "+str(preview.get("error_code",""))):return report
		campaign=preview.next_state
	if not expect(not report.is_empty(),"found a day-six lesson in the command history"):return report
	report.accepted_commands=commands.size()
	report.trained_student=campaign.full_campaign.mentored.has("chen") or campaign.commands.values().any(func(value: String)->bool:
		var cmd: Dictionary=JSON.parse_string(value)
		return cmd.kind=="mentor" and cmd.payload.student=="chen")
	report.known_after_load=rules.CampLearning.known(state).has("mentors")
	report.repeat_offer_after_read=rules.CampLearning.offer(state,content)
	expect(report.trained_student and report.known_after_load and report.repeat_offer_after_read=="","real lesson acquired and not repeated in saved night")
	for key: String in ["day","phase","projects","used","settled"]:
		expect(store.canonical(campaign.campaign[key])==store.canonical(state.campaign[key]),"replay reproduces saved campaign "+key)
	expect(store.canonical(campaign.full_campaign.mentored)==store.canonical(state.full_campaign.mentored),"replay reproduces day-six mentoring state")
	return report

func review_ending(state: Dictionary,profile: String) -> Dictionary:
	var result: Dictionary={"day":state.campaign.day,"route":state.full_campaign.route,"ending":state.full_campaign.ending,"main_missions":0,"side_missions":0,"locales":{}}
	for id: String in state.campaign.settled:
		if id.begins_with("M"):result.main_missions+=1
		if id.begins_with("S"):result.side_missions+=1
	expect(state.chapter_one.finished and state.campaign.day==24 and result.main_missions==24 and state.journey.recruited.size()==8,"completed 24 days and acquired eight crew "+profile)
	if profile=="sides":expect(result.side_missions==12,"all side missions "+profile)
	ui.title_screen=false
	ui.session.state=state
	for locale: String in ui.I18n.LOCALES:
		ui.I18n.locale=locale
		ui.render()
		var title: String=ui.I18n.t("p3.final_title")%ui.I18n.t("p3.route_"+result.ending)
		var coda: Dictionary=ui.StoryFacts.community(state,content,content.domains.scripts.community.back())
		var visible: Array[String]=labels(ui.root)
		expect(visible.has(title) and visible.has(ui.I18n.s(coda.text)) and coda.outcome==state.campaign.settled.M24.outcome,"actual ending title and M24 result "+profile+locale)
		var people: Array=[]
		for button: Button in ui.root.find_children("*","Button",true,false):
			for id: String in state.journey.recruited:
				if button.text==ui.actor_name(id):people.append(id)
		expect(people.size()==8,"eight individual coda entries "+profile+locale)
		ui.show_person_ending("lin")
		var dialog: Window=null
		for child: Node in ui.get_children():
			if child is Window and child.visible:dialog=child
		if expect(dialog!=null,"open individual ending"):
			expect(labels(dialog).has(ui.I18n.t("story.unread_ending")),"unresolved final conversation uses reader-facing coda")
			dialog.hide();dialog.queue_free()
		var source: Dictionary=ui.StoryFacts.chapter(state,content,content.domains.scripts.chapter[11])
		if state.campaign.settled.M17.facts.get("isolate")=="completed":
			expect(source.text==ui.I18n.t("p4close.isolated_coda"),"isolation retained in chapter coda")
		result.locales[locale]={"title":title,"M24_outcome":coda.outcome,"R05_isolation_text":ui.I18n.s(source.text),"crew_buttons":people.size()}
		if profile=="sides":
			var scene: Dictionary=ui.Screens.Journey.scene(state,content,"P_lin_1")
			expect(scene.record.choice=="share" and scene.pages.size()>scene.opening_count,"retained story response "+locale)
			result.locales[locale].saved_choice=scene.record.choice
	return result

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var args:=OS.get_cmdline_user_args()
	if args.size()!=2:quit(2);return
	var root_dir: String=args[0]
	store=load("res://scripts/infrastructure/campaign_store.gd")
	rules=load("res://scripts/domain/campaign_rules.gd")
	content=load("res://scripts/infrastructure/content_catalog.gd").load_catalog()
	if not expect(content.ok,"open frozen catalog from project pack"):quit(1);return
	results.authority=content.content_sha256
	ui=load("res://scenes/main.tscn").instantiate()
	root.add_child(ui)
	results.saves={}
	for file: String in ["camp-day06","camp-day23","ending-main","ending-sides","ending-recovery"]:
		var path: String=root_dir.path_join(file+".json")
		var state: Dictionary=saved(path)
		if state.is_empty():continue
		var report: Dictionary={}
		if file=="camp-day06":report=replay_six(state)
		elif file=="camp-day23":
			report={"day":state.campaign.day,"route":state.full_campaign.route,"available_routes":rules.Full.routes(state),"known":rules.CampLearning.known(state).has("route")}
			expect(report.day==23 and report.route=="shared_control" and report.available_routes.has(report.route) and report.known,"earned day-23 route remains selected")
		else:report=review_ending(state,file.trim_prefix("ending-"))
		report.sha256=FileAccess.get_sha256(path)
		results.saves[file]=report
	results.problems=problems
	var f:=FileAccess.open(args[1],FileAccess.WRITE)
	f.store_string(JSON.stringify(results,"  ")+"\n");f.close()
	ui.sound.stop_audio()
	ui.queue_free()
	await process_frame
	print("RELEASE_CONTENT_PROBE ",problems.is_empty())
	quit(0 if problems.is_empty() else 1)
