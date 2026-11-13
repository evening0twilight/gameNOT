extends SceneTree
var canvas: SubViewport
func _initialize() -> void:root.hide();call_deferred("run")
func run() -> void:
	var actor: String="he"
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--actor="):actor=arg.trim_prefix("--actor=")
	canvas=SubViewport.new();canvas.size=Vector2i(1440,1024);canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	var background:=ColorRect.new();background.size=Vector2(1440,1024);background.color=Color("17252c");canvas.add_child(background)
	var texture:=ImageTexture.create_from_image(Image.load_from_file("res://../output/imagegen/p4close/"+actor+"-bodies-v2.png"))
	for outfit: int in range(2):
		var region:=AtlasTexture.new();region.atlas=texture;region.region=Rect2(outfit*768,0,768,1024)
		var body:=TextureRect.new();body.texture=region;body.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;body.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;body.size=Vector2(680,960);body.position=Vector2(20+outfit*720,32);canvas.add_child(body)
	for i: int in range(4):await process_frame
	await RenderingServer.frame_post_draw
	canvas.get_texture().get_image().save_png("res://../outputs/p4close-"+actor+"-anatomy-v2.png")
	print("P4CLOSE_ANATOMY: whole painted head, neck, shoulders; no detached anatomy overlay")
	quit()
