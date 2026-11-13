extends SceneTree
const INFO={"he":{"face":Rect2(318,82,166,172),"source":Vector2(120,168)},"lin":{"face":Rect2(326,103,140,155),"source":Vector2(108,169)}}
const EMOTIONS=["平静","专注","轻松","疑虑","克制愤怒","疲惫","动容","坚定"]
class Portrait extends Control:
	func build(bodies: Texture2D,expressions: Texture2D,actor: String,outfit: int,emotion: int) -> void:
		var original:=AtlasTexture.new();original.atlas=bodies;original.region=Rect2(outfit*768,0,768,1024)
		var body:=TextureRect.new();body.texture=original;body.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;body.size=Vector2(768,1024);add_child(body)
		if emotion==0:return
		var face: Rect2=INFO[actor].face
		if outfit==1:face.position.x+=-52 if actor=="lin" else -1
		var source: Vector2=INFO[actor].source+Vector2((emotion%4)*384,(emotion/4)*512)
		var patch:=AtlasTexture.new();patch.atlas=expressions;patch.region=Rect2(source,face.size)
		var overlay:=TextureRect.new();overlay.texture=patch;overlay.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;overlay.position=face.position;overlay.size=face.size
		var shader:=Shader.new()
		shader.code="shader_type canvas_item; uniform sampler2D base_image; uniform vec2 source_origin; uniform vec2 face_size; uniform vec2 target_origin; void fragment(){ vec4 part=texture(TEXTURE,UV); vec2 p=(UV-source_origin)/face_size; float edge=min(min(p.x,1.0-p.x),min(p.y,1.0-p.y)); float mask=texture(base_image,target_origin+p*face_size).a*smoothstep(0.0,0.09,edge); COLOR=vec4(part.rgb,part.a*mask); }"
		var material:=ShaderMaterial.new();material.shader=shader
		material.set_shader_parameter("base_image",bodies);material.set_shader_parameter("source_origin",source/Vector2(1536,1024));material.set_shader_parameter("face_size",face.size/Vector2(1536,1024));material.set_shader_parameter("target_origin",(face.position+Vector2(outfit*768,0))/Vector2(1536,1024));overlay.material=material;add_child(overlay)
func _initialize() -> void:root.hide();call_deferred("run")
func viewport(dimensions: Vector2i) -> SubViewport:
	var canvas:=SubViewport.new();canvas.size=dimensions;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	var background:=ColorRect.new();background.size=dimensions;background.color=Color("17252c");canvas.add_child(background)
	return canvas
func label_at(canvas: SubViewport,words: String,at: Vector2,font_size: int=24) -> void:
	var label:=Label.new();label.text=words;label.position=at;label.add_theme_font_override("font",load("res://assets/fonts/noto_sans_cjk_sc_regular.otf"));label.add_theme_font_size_override("font_size",font_size);canvas.add_child(label)
func rendered(canvas: SubViewport) -> Image:
	for i: int in range(3):await process_frame
	await RenderingServer.frame_post_draw
	return canvas.get_texture().get_image()
func run() -> void:
	var reports: Array=[]
	var overview:=viewport(Vector2i(1600,860))
	for actor: String in ["lin","he"]:
		var bodies:=ImageTexture.create_from_image(Image.load_from_file("res://../output/imagegen/p4close/%s-bodies-v2.png"%actor))
		var expressions:=ImageTexture.create_from_image(Image.load_from_file("res://../output/imagegen/p4close/%s-expressions-v3.png"%actor))
		var canvas:=viewport(Vector2i(1600,2240))
		for outfit: int in range(2):
			var probe:=viewport(Vector2i(768,1024))
			var original:=Portrait.new();original.build(bodies,expressions,actor,outfit,0);probe.add_child(original)
			var before: Image=await rendered(probe);original.queue_free();await process_frame
			for emotion: int in range(8):
				var portrait:=Portrait.new();portrait.build(bodies,expressions,actor,outfit,emotion);portrait.position=Vector2(10+(emotion%4)*400,50+(outfit*2+emotion/4)*550);portrait.scale=Vector2.ONE*.5;canvas.add_child(portrait)
				label_at(canvas,("现场服" if outfit==0 else "日常服")+" · "+EMOTIONS[emotion],portrait.position-Vector2(0,38))
				var test:=Portrait.new();test.build(bodies,expressions,actor,outfit,emotion);probe.add_child(test)
				var after: Image=await rendered(probe)
				var below: int=int(INFO[actor].face.end.y)
				var same: bool=before.get_region(Rect2i(0,below,768,1024-below)).get_data()==after.get_region(Rect2i(0,below,768,1024-below)).get_data()
				reports.append({"actor":actor,"outfit":outfit,"emotion":emotion,"neck_shoulders_body_identical":same})
				test.queue_free();await process_frame
			probe.queue_free()
			var sample:=Portrait.new();sample.build(bodies,expressions,actor,outfit,2 if outfit==1 else 0);sample.position=Vector2((0 if actor=="lin" else 800)+outfit*400,76);sample.scale=Vector2.ONE*.5;overview.add_child(sample)
			label_at(overview,("林岚" if actor=="lin" else "贺鸣")+(" · 现场服" if outfit==0 else " · 日常服"),sample.position-Vector2(0,42))
		var contact: Image=await rendered(canvas);contact.save_png("res://../outputs/p4close-%s-registered-expressions-v3.png"%actor);canvas.queue_free()
	label_at(overview,"返工样张 · 完整颈肩底图 + 同位脸部表情 · 尚未获美术认可",Vector2(30,700),28)
	var shot: Image=await rendered(overview);shot.save_png("res://../outputs/p4close-corrected-art-v3.png")
	var all_same: bool=reports.all(func(r: Dictionary)->bool:return r.neck_shoulders_body_identical)
	var file:=FileAccess.open("res://../outputs/p4close-registered-art-v3.json",FileAccess.WRITE);file.store_string(JSON.stringify({"checks":reports,"all_neck_shoulders_body_identical":all_same,"human_art_approval":false},"\t"));file.close()
	print("P4CLOSE_REGISTERED_ART: ",reports.size()," neck/shoulder comparisons; identical=",all_same)
	quit(0 if all_same else 1)
