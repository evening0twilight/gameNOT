extends SceneTree
## Actual production material at UI sizes; this is an art fixture, not campaign evidence.
const Art=preload("res://scripts/presentation/visual_assets.gd")
const IDS=["lin","xu","su","chen","ye","he","mo","jiang"]
const NAMES=["林岚","许舟","苏棠","陈砚","叶禾","贺鸣","莫遥","江朔"]
func _initialize() -> void:root.hide();call_deferred("run")
func label_at(parent: Node,text: String,at: Vector2,font_size: int=16) -> void:
	var label:=Label.new();label.text=text;label.position=at;label.add_theme_font_size_override("font_size",font_size);parent.add_child(label)
func run() -> void:
	var canvas:=SubViewport.new();canvas.size=Vector2i(1400,1880);canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	var bg:=ColorRect.new();bg.color=Color("18252c");bg.size=Vector2(1400,1880);canvas.add_child(bg)
	label_at(canvas,"0.18 · 正式人物材质 / 两套服装 / 96px表情 / 96px棋子（美术夹具）",Vector2(20,10),24)
	for i: int in range(8):
		var y: float=60+i*226;var id: String=IDS[i]
		label_at(canvas,NAMES[i],Vector2(15,y),20)
		for outfit: int in range(2):
			var view:=Art.character(id,"work" if outfit==0 else "camp","light",Vector2(144,192));view.position=Vector2(75+outfit*146,y);canvas.add_child(view)
		for e: int in range(8):
			var head:=Art.character(id,"work",Art.CharacterArt.EXPRESSIONS[e],Vector2(96,96),true);head.position=Vector2(382+e*112,y+42);canvas.add_child(head)
			label_at(canvas,["平静","专注","轻松","疑虑","生气","疲惫","触动","决意"][e],Vector2(403+e*112,y+146),15)
		var token:=Art.picture(Art.motion(id,1),Vector2(96,96));token.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;token.position=Vector2(1288,y+42);canvas.add_child(token)
	for tick: int in range(5):await process_frame
	await RenderingServer.frame_post_draw
	canvas.get_texture().get_image().save_png("res://../outputs/p4art-ensemble.png")
	print("P4ART_ENSEMBLE: actual material gallery rendered")
	quit()
