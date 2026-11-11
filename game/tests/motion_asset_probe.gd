extends SceneTree
func _initialize() -> void:
	for id: String in ["a","b"]:
		var image:=Image.load_from_file("res://assets/motion_p4/crew_%s.png"%id)
		var clear: int=0
		for y: int in range(0,image.get_height(),8):
			for x: int in range(0,image.get_width(),8):
				if image.get_pixel(x,y).a<.01:clear+=1
		print("MOTION_ALPHA: ",id," size=",image.get_size()," transparent_samples=",clear)
	quit()
