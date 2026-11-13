extends SceneTree
const Art=preload("res://scripts/presentation/visual_assets.gd")
var failures: Array=[]
func _initialize() -> void:root.hide();call_deferred("run")
func grab(canvas: SubViewport) -> Image:
	for i: int in range(3):await process_frame
	await RenderingServer.frame_post_draw
	return canvas.get_texture().get_image()
func run() -> void:
	var canvas:=SubViewport.new();canvas.size=Vector2i(768,1024);canvas.transparent_bg=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	var results: Array=[]
	for id: String in Art.CharacterArt.specs():
		for kind: String in ["work","camp"]:
			var original=Art.character(id,kind,"neutral",Vector2(768,1024));canvas.add_child(original)
			var before: Image=await grab(canvas);original.queue_free();await process_frame
			var panel: int=1 if kind=="camp" else 0
			var face: Array=Art.CharacterArt.specs()[id].face[panel]
			var lower: int=int(face[1])+int(face[3])+1
			for emotion: String in Art.CharacterArt.EXPRESSIONS:
				var view=Art.character(id,kind,emotion,Vector2(768,1024));canvas.add_child(view)
				var after: Image=await grab(canvas)
				var neck_same: bool=before.get_region(Rect2i(0,lower,768,1024-lower)).get_data()==after.get_region(Rect2i(0,lower,768,1024-lower)).get_data()
				var changed: bool=before.get_data()!=after.get_data()
				if not neck_same:failures.append(id+kind+emotion+" altered neck/shoulder")
				if emotion!="neutral" and not changed:failures.append(id+kind+emotion+" expression missing")
				results.append({"actor":id,"costume":kind,"expression":emotion,"neck_shoulders_body_identical":neck_same,"face_changed":changed})
				if emotion=="light":after.save_png("res://../outputs/p4art-"+id+"-"+kind+"-expression.png")
				view.queue_free();await process_frame
	var file:=FileAccess.open("res://../outputs/p4art-character-review.json",FileAccess.WRITE);file.store_string(JSON.stringify({"failures":failures,"results":results,"scope":"Actual production CharacterArt shader, two costumes and all eight expressions; anatomy invariance is not final human acceptance"},"\t"));file.close()
	print("P4ART_CHARACTER_REVIEW: ",results.size()," combinations, failures=",failures)
	quit(1 if failures else 0)
