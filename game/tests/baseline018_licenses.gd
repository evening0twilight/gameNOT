extends SceneTree
func _initialize() -> void:
	var file:=FileAccess.open("res://../docs/baseline018-engine-license.txt",FileAccess.WRITE)
	file.store_string(Engine.get_license_text()+"\n\nThird-party notices\n"+JSON.stringify({"copyright":Engine.get_copyright_info(),"licenses":Engine.get_license_info()},"\t"));file.close();quit()
