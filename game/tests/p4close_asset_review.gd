extends SceneTree
const Art=preload("res://scripts/presentation/visual_assets.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
var canvas: SubViewport
var box: VBoxContainer
func _initialize() -> void:root.hide();call_deferred("run")
func label(parent: Node,text: String) -> void:
	var node:=Label.new();node.text=text;node.add_theme_font_override("font",load("res://assets/fonts/noto_sans_cjk_sc_regular.otf"));node.add_theme_font_size_override("font_size",20);parent.add_child(node)
func tile(parent: Node,texture: Texture2D,text: String,dimensions: Vector2) -> void:
	var item:=VBoxContainer.new();parent.add_child(item)
	var picture=Art.picture(texture,dimensions);picture.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;item.add_child(picture);label(item,text)
func reset(title: String,columns: int) -> GridContainer:
	if box!=null:box.queue_free()
	box=VBoxContainer.new();box.position=Vector2(24,24);canvas.add_child(box);label(box,title)
	var grid:=GridContainer.new();grid.columns=columns;grid.add_theme_constant_override("h_separation",22);grid.add_theme_constant_override("v_separation",18);box.add_child(grid);return grid
func capture(name: String) -> void:
	await process_frame;await process_frame;await RenderingServer.frame_post_draw
	canvas.get_texture().get_image().save_png("res://../outputs/p4close-assets-"+name+".png")
func run() -> void:
	canvas=SubViewport.new();canvas.size=Vector2i(1600,900);canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	var content: Dictionary=Catalog.load_catalog()
	var grid=reset("当前生产资源：96×96头像与96×96棋子（不是新设定样张）",8)
	for id: String in content.actors:tile(grid,Art.portrait(id),content.actors[id].name,Vector2(96,96))
	for id: String in content.actors:tile(grid,Art.motion(id,0),content.actors[id].role,Vector2(130,96))
	await capture("crew")
	grid=reset("当前12地点套件在生产地图中的来源",4)
	for place: String in ["bridge","clinic","coldstore","control","factory","ferry","gate","housing","pump","roof","shelter","warehouse"]:tile(grid,Art.environment(place),place,Vector2(340,210))
	await capture("locations")
	grid=reset("当前48图标（实际运行纹理，带文字辅助）",8)
	var icons: Array=JSON.parse_string(FileAccess.get_file_as_string("res://../docs/product018-icons.json")).icons
	for id: String in icons:tile(grid,Art.icon(id),id,Vector2(146,64))
	await capture("icons")
	grid=reset("当前6种机器与通用人物标记；居民类别和两种借调外形尚未完整分开",8)
	for pair: Array in [[3,"scout"],[30,"welder"],[31,"hauler"],[32,"skimmer"],[44,"relay"],[45,"sentinel"],[4,"rescue marker"],[9,"borrowed responder"]]:tile(grid,Art.sprite(pair[0]),pair[1],Vector2(160,160))
	await capture("machines")
	print("P4CLOSE_ASSET_REVIEW: captured actual runtime texture references")
	quit()
