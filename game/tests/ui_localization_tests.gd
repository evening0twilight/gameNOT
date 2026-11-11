extends SceneTree
const I18n=preload("res://scripts/presentation/localization.gd")
var failures: int=0
var checks: int=0
func check(value: bool,context: String) -> void:
	checks+=1
	if not value:failures+=1;printerr("UI_CHECK_FAILED: "+context)
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var scene=load("res://scenes/main.tscn").instantiate()
	root.add_child(scene)
	scene.title_screen=false
	scene.session.state=scene.Rules.fresh(scene.session.content,"isolated-layout-fixture")
	var original: Dictionary=scene.session.state.duplicate(true)
	var disk: String=FileAccess.get_file_as_string(scene.session.path)
	var source: String=FileAccess.get_file_as_string("res://scripts/app/main.gd")
	var regex:=RegEx.new();regex.compile('I18n.t\\("([^"\\n]+)"\\)')
	for match_result: RegExMatch in regex.search_all(source):check(I18n.messages.has(match_result.get_string(1)),"catalog key "+match_result.get_string(1))
	for locale: String in ["zh_CN","en_XA"]:
		I18n.locale=locale
		check((I18n.t("preview.actor") % ["NAME",1,2,3,4]).contains("NAME"),"format placeholders "+locale)
		for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
			root.size=dimensions;root.content_scale_size=dimensions
			for font: int in [16,20,24]:
				scene.font_size=font
				for tab: String in ["actions","objectives","cooperation"]:
					scene.panel_tab=tab;scene.render()
					for frame in range(4):await process_frame
					if scene.root.size.y>dimensions.y:
						for child in scene.root.get_children():printerr(str(child.get_class())+" "+str(child.size)+" min="+str(child.get_combined_minimum_size()))
					check(scene.root.size.x<=dimensions.x and scene.root.size.y<=dimensions.y,"battle layout %s %s %d %s size=%s" % [locale,dimensions,font,tab,scene.root.size])
					check(scene.session.state==original,"presentation does not mutate campaign")
	var preview: Dictionary=scene.session.preview({"command_id":"ui-test","expected_revision":original.revision,"root_decision_id":"ui-test","actor_id":"lin","kind":"emergency_retreat","payload":{"confirmed":true}})
	check(preview.ok,"settlement preview")
	if preview.ok:
		scene.session.state=preview.next_state
		for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
			root.size=dimensions;root.content_scale_size=dimensions
			for locale: String in ["zh_CN","en_XA"]:
				I18n.locale=locale
				for font: int in [16,20,24]:
					scene.font_size=font
					for phase: String in ["settlement","camp"]:
						scene.session.state.campaign.phase=phase
						scene.render()
						for frame in range(4):await process_frame
						check(scene.root.size.x<=root.size.x and scene.root.size.y<=root.size.y,"camp layout %s %s %d %s" % [phase,locale,font,dimensions])
	check(FileAccess.get_file_as_string(scene.session.path)==disk,"test and language changes leave save bytes intact")
	scene.session.state=original
	I18n.initialize()
	scene.queue_free();await process_frame
	print("UI_LOCALIZATION_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
