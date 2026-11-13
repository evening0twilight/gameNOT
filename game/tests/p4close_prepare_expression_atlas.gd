extends SceneTree
func _initialize() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://../tmp/imagegen"))
	for actor: String in ["he","lin"]:
		var original:=Image.load_from_file("res://../output/imagegen/p4close/"+actor+"-bodies-v2.png")
		original.convert(Image.FORMAT_RGBA8)
		var crop:=Rect2i(270,20,240,300) if actor=="he" else Rect2i(270,20,280,340)
		var inset:=Vector2i(72,106) if actor=="he" else Vector2i(52,86)
		var face:=Rect2i(318,82,166,172) if actor=="he" else Rect2i(326,103,140,155)
		var sheet:=Image.create(1536,1024,false,Image.FORMAT_RGBA8);sheet.fill(Color.TRANSPARENT)
		var mask:=Image.create(1536,1024,false,Image.FORMAT_RGBA8);mask.fill(Color.WHITE)
		for index: int in range(8):
			var cell:=Vector2i((index%4)*384,(index/4)*512)
			sheet.blit_rect(original,crop,cell+inset)
			if index>0:mask.fill_rect(Rect2i(cell+inset+face.position-crop.position,face.size),Color(1,1,1,0))
		sheet.save_png("res://../tmp/imagegen/"+actor+"-registered-template.png")
		mask.save_png("res://../tmp/imagegen/"+actor+"-registered-mask.png")
	quit()
