extends SceneTree
const Art=preload("res://scripts/presentation/visual_assets.gd")
const I18n=preload("res://scripts/presentation/localization.gd")
var checks: int=0
var failures: int=0
func check(value: bool,context: String) -> void:
	checks+=1
	if not value:failures+=1;printerr("P3_PRESENTATION_FAIL: "+context)
func _initialize() -> void:call_deferred("run")
func run() -> void:
	for location: String in ["factory","roof","control","coldstore","housing","shelter"]:
		var texture: AtlasTexture=Art.environment(location)
		check(Rect2(Vector2.ZERO,texture.atlas.get_size()).encloses(texture.region),"new environment atlas "+location)
	for index: int in range(40,48):
		var texture: AtlasTexture=Art.sprite(index)
		check(Rect2(Vector2.ZERO,texture.atlas.get_size()).encloses(texture.region),"new sprite atlas bounds")
	var pixels: Image=load("res://assets/visual_p3/crew_sprites.png").get_image()
	check(pixels.get_pixel(0,0).a<.1,"actual transparent sprite background")
	var scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene)
	var disk: String=FileAccess.get_file_as_string(scene.session.path)
	var base: Dictionary=scene.Rules.fresh(scene.session.content,"p3-layout")
	base.campaign.day=23;base.chapter_one.main_completed=22;base.chapter_one.roster=["ye","he","mo"]
	scene.Rules.deploy(base,scene.session.content,"M23")
	for locale: String in ["zh_CN","en_XA"]:
		I18n.locale=locale
		for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
			root.size=dimensions;root.content_scale_size=dimensions
			for font: int in [16,20,24]:
				scene.font_size=font;scene.session.state=base.duplicate(true)
				for phase: String in ["battle","camp","ending"]:
					if phase!="battle":
						scene.Rules.settle(scene.session.state,scene.session.content)
						scene.session.state.campaign.phase="camp" if phase=="camp" else "settlement"
						if phase=="ending":scene.session.state.chapter_one.finished=true;scene.session.state.full_campaign.ending="evacuation"
					scene.render()
					for frame: int in range(4):await process_frame
					check(scene.root.size.x<=dimensions.x and scene.root.size.y<=dimensions.y,"late campaign layout %s %s %d %s" % [locale,dimensions,font,phase])
		# Explicit authored scene fixtures; this is presentation coverage, not a natural playthrough.
		scene.session.state=base.duplicate(true);scene.session.state.campaign.phase="camp"
		for node: Dictionary in scene.Stories.nodes(scene.session.content).values():
			scene.session.state.chapter_one.scenes[node.id]={"seen":true,"choice":"","status":"seen"}
			scene.show_story(node.id)
			for frame: int in range(2):await process_frame
			for child: Node in scene.get_children():
				if child is Window and not child is ConfirmationDialog:
					check(child.size.x<=root.size.x and child.size.y<=root.size.y,"story modal "+node.id+locale);child.queue_free()
			await process_frame
	check(FileAccess.get_file_as_string(scene.session.path)==disk,"layout fixture does not write player state")
	scene.queue_free();await process_frame;I18n.initialize()
	print("P3_PRESENTATION_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
