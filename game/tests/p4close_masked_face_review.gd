extends SceneTree
class Portrait extends Control:
	func build(bodies: Texture2D,edited: Texture2D,outfit: int,smile: bool) -> void:
		var original:=AtlasTexture.new();original.atlas=bodies;original.region=Rect2(outfit*768,0,768,1024)
		var body:=TextureRect.new();body.texture=original;body.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;body.size=Vector2(768,1024);add_child(body)
		if not smile:return
		var patch:=AtlasTexture.new();patch.atlas=edited;patch.region=Rect2(318,82,166,172)
		var overlay:=TextureRect.new();overlay.texture=patch;overlay.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;overlay.position=Vector2(318,82);overlay.size=Vector2(166,172)
		var shader:=Shader.new()
		shader.code="shader_type canvas_item; uniform sampler2D base_image; uniform float panel_offset=0.0; void fragment(){ vec4 part=texture(TEXTURE,UV); vec2 p=(UV-vec2(318.0/1536.0,82.0/1024.0))/vec2(166.0/1536.0,172.0/1024.0); float edge=min(min(p.x,1.0-p.x),min(p.y,1.0-p.y)); float mask=texture(base_image,UV+vec2(panel_offset,0.0)).a*smoothstep(0.0,0.09,edge); COLOR=vec4(part.rgb,part.a*mask); }"
		var material:=ShaderMaterial.new();material.shader=shader;material.set_shader_parameter("base_image",bodies);material.set_shader_parameter("panel_offset",.5 if outfit==1 else 0.0);overlay.material=material;add_child(overlay)
var canvas: SubViewport
func _initialize() -> void:root.hide();call_deferred("run")
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1600,1060);canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	var background:=ColorRect.new();background.size=Vector2(1600,1060);background.color=Color("17252c");canvas.add_child(background)
	var bodies:=ImageTexture.create_from_image(Image.load_from_file("res://../output/imagegen/p4close/he-bodies-v2.png"))
	var edited:=ImageTexture.create_from_image(Image.load_from_file("res://../output/imagegen/p4close/he-smile-masked-v3.png"))
	for index: int in range(3):
		var portrait:=Portrait.new();portrait.build(bodies,edited,1 if index==2 else 0,index>0);portrait.position=Vector2(15+index*520,80);portrait.scale=Vector2.ONE*.65;canvas.add_child(portrait)
		var label:=Label.new();label.text=["完整底图 · 平静","现场服 · 同位脸部编辑","日常服 · 复用同一脸部层"][index];label.position=Vector2(25+index*520,35);label.add_theme_font_override("font",load("res://assets/fonts/noto_sans_cjk_sc_regular.otf"));label.add_theme_font_size_override("font_size",24);canvas.add_child(label)
	for i: int in range(4):await process_frame
	await RenderingServer.frame_post_draw
	canvas.get_texture().get_image().save_png("res://../outputs/p4close-he-masked-face-v3.png")
	# Isolated same-position renders compare original neck/shoulder/body pixels.
	var probe:=SubViewport.new();probe.size=Vector2i(768,1024);probe.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(probe)
	var base:=Portrait.new();base.build(bodies,edited,1,false);probe.add_child(base)
	for i: int in range(3):await process_frame
	await RenderingServer.frame_post_draw
	var before: Image=probe.get_texture().get_image();base.queue_free();await process_frame
	var changed:=Portrait.new();changed.build(bodies,edited,1,true);probe.add_child(changed)
	for i: int in range(3):await process_frame
	await RenderingServer.frame_post_draw
	var after: Image=probe.get_texture().get_image()
	var neck_unchanged: bool=before.get_region(Rect2i(0,254,768,770)).get_data()==after.get_region(Rect2i(0,254,768,770)).get_data()
	var face_changed: bool=before.get_region(Rect2i(318,82,166,172)).get_data()!=after.get_region(Rect2i(318,82,166,172)).get_data()
	var report: Dictionary={"face_changed":face_changed,"face_region":[318,82,166,172],"original_neck_shoulders_body_pixel_identical":neck_unchanged,"method":"same-position masked edit, only original face pixels reused across two whole-anatomy costumes","human_art_approval":false}
	var file:=FileAccess.open("res://../outputs/p4close-masked-face-v3.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("P4CLOSE_MASKED_FACE: neck/shoulders/body identical=",neck_unchanged)
	quit(0 if neck_unchanged and face_changed else 1)
