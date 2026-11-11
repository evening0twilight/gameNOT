extends "res://tests/baseline018_ui.gd"
func run() -> void:
	scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene);scene.title_screen=false
	var evidence: Array=[]
	for day: int in [4,6,18,19,24]:
		var source: String="res://../outputs/baseline018-linked-day%02d.json"%day
		var loaded: Dictionary=scene.session.store.load_slot(source,scene.session.content)
		if not loaded.ok:failures.append("real journey snapshot day%d"%day);continue
		scene.session.state=loaded.state;scene.message="实际连续周目 · 第%d日"%day;scene.render();await process_frame
		if day==4:scene.Screens.introduction(scene,"chen")
		elif day==6:scene.Screens.profile(scene,"chen")
		elif day==18:scene.Screens.relationships(scene,"su","jiang")
		await screenshot("journey-day%02d"%day)
		evidence.append({"day":day,"phase":loaded.state.campaign.phase,"revision":loaded.state.revision,"source":source,"state_mutated_for_presentation":false})
		close_modals();await process_frame
	for id: String in scene.session.content.actors:
		for expression: String in ["neutral","smile","worried","firm","tired","surprised","grief","relieved"]:
			var texture: AtlasTexture=scene.Art.portrait(id,expression)
			if not Rect2(Vector2.ZERO,texture.atlas.get_size()).encloses(texture.region):failures.append("portrait "+id+expression)
		for outfit: String in ["work","camp"]:
			if scene.Art.outfit(id,outfit)==null:failures.append("outfit "+id+outfit)
	for context: String in ["title","briefing","battle","camp","story","ending"]:
		var music: AudioStreamWAV=load("res://assets/audio018/"+context+".wav")
		if music==null or music.get_length()<20:failures.append("music "+context)
	var f:=FileAccess.open("res://../outputs/baseline018-journey-review.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"failures":failures,"captures":evidence,"rendered":DisplayServer.get_name()!="headless","screen":DisplayServer.window_get_current_screen(),"primary":DisplayServer.get_primary_screen(),"portraits":64,"outfits":16,"music_contexts":6},"\t"));f.close()
	print("BASELINE018_JOURNEY_REVIEW: captures=%d failures=%d"%[evidence.size(),failures.size()]);scene.sound.stop_audio();scene.queue_free();await process_frame;quit(0 if failures.is_empty() else 1)
