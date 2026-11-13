extends SceneTree
## Lossless template registration and mask construction only; creative edits use imagegen.
func _initialize() -> void:
	DirAccess.make_dir_recursive_absolute("res://../tmp/imagegen")
	var records: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/characters018/manifest.json"))
	for actor: String in records:
		var original:=Image.load_from_file("res://assets/characters018/"+actor+"-bodies.png");original.convert(Image.FORMAT_RGBA8)
		var info: Dictionary=records[actor];var h: Array=info.head[0];var f: Array=info.face[0]
		var crop:=Rect2i(int(h[0]),int(h[1]),int(h[2]),int(h[3]));var face:=Rect2i(int(f[0]),int(f[1]),int(f[2]),int(f[3]))
		var inset:=Vector2i((384-crop.size.x)/2,(512-crop.size.y)/2)
		var sheet:=Image.create(1536,1024,false,Image.FORMAT_RGBA8);sheet.fill(Color.TRANSPARENT)
		var mask:=Image.create(1536,1024,false,Image.FORMAT_RGBA8);mask.fill(Color.WHITE)
		for index: int in range(8):
			var cell:=Vector2i((index%4)*384,(index/4)*512);sheet.blit_rect(original,crop,cell+inset)
			if index>0:mask.fill_rect(Rect2i(cell+inset+face.position-crop.position,face.size),Color(1,1,1,0))
		sheet.save_png("res://../tmp/imagegen/"+actor+"-p4art-template.png");mask.save_png("res://../tmp/imagegen/"+actor+"-p4art-mask.png")
	quit()
