extends SceneTree
const Art=preload("res://scripts/presentation/visual_assets.gd")
const I18n=preload("res://scripts/presentation/localization.gd")
var checks: int=0
var failures: int=0
func check(value: bool,description: String) -> void:
	checks+=1
	if not value:failures+=1;printerr("P2_PRESENTATION_FAIL: "+description)
func _initialize() -> void:call_deferred("run")
func run() -> void:
	for location: String in ["ferry","clinic","warehouse","bridge","pump","gate"]:
		var texture: AtlasTexture=Art.environment(location)
		check(Rect2(Vector2.ZERO,texture.atlas.get_size()).encloses(texture.region),"environment atlas "+location)
	for index: int in [10,20,21,22,23,24,25,30,31,32]:
		var texture: Texture2D=Art.sprite(index)
		check(texture.get_width()>100,"production sprite resolution")
	for name: String in ["chen_sprite","objectives","machines"]:
		var pixels: Image=load("res://assets/visual_p2/%s.png"%name).get_image()
		check(pixels.get_pixel(0,0).a<.1,"actual transparency "+name)
	var scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene)
	var disk: String=FileAccess.get_file_as_string(scene.session.path)
	scene.session.state=scene.Rules.fresh(scene.session.content,"p2-layout")
	scene.session.state=scene.Rules.reduce(scene.session.state,{"kind":"emergency_retreat","actor_id":"lin","payload":{"confirmed":true},"command_id":"layout-retreat","root_decision_id":"layout-retreat","expected_revision":scene.session.state.revision},scene.session.content).next_state
	scene.session.state.campaign.day=6;scene.session.state.campaign.phase="camp"
	for locale: String in ["zh_CN","en_XA"]:
		I18n.locale=locale
		for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080)]:
			root.size=dimensions;root.content_scale_size=dimensions;scene.font_size=24
			scene.render()
			for frame: int in range(4):await process_frame
			check(scene.root.size.x<=dimensions.x and scene.root.size.y<=dimensions.y,"four-person camp layout "+locale)
			scene.prepare_mission("M06",false)
			for frame: int in range(4):await process_frame
			for child: Node in scene.get_children():
				if child is Window and not child is ConfirmationDialog:
					check(child.size.x<=dimensions.x and child.size.y<=dimensions.y,"briefing window fits "+locale)
					child.queue_free()
			await process_frame
			for id: String in scene.Stories.available(scene.session.state,scene.session.content):
				scene.session.state.chapter_one.scenes[id]={"seen":true,"choice":"","status":"seen"}
				scene.show_story(id)
				await process_frame
				for child: Node in scene.get_children():
					if child is Window and not child is ConfirmationDialog:
						check(child.size.x<=dimensions.x,"story width "+id+locale);child.queue_free()
				await process_frame
	check(FileAccess.get_file_as_string(scene.session.path)==disk,"visual fixtures never overwrite player save")
	scene.queue_free();await process_frame
	I18n.initialize()
	print("P2_PRESENTATION_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
