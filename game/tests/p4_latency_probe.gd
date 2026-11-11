extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene)
	var samples: Array=[]
	for cycle: int in range(2):
		for actor: String in scene.session.state.battle.heroes:
			var hint: Dictionary=scene.Guidance.next_step(scene.session.state,scene.session.content,actor)
			var c: Dictionary={"command_id":"latency-"+str(samples.size()),"root_decision_id":"latency","expected_revision":scene.session.state.revision,"kind":hint.action,"actor_id":actor,"payload":hint.payload}
			var start: int=Time.get_ticks_usec()
			var preview: Dictionary=scene.session.preview(c)
			var pre: int=Time.get_ticks_usec()
			var result: Dictionary=scene.session.submit(c)
			var saved: int=Time.get_ticks_usec()
			scene.selected=actor;scene.render()
			var rendered: int=Time.get_ticks_usec()
			samples.append({"preview_ms":(pre-start)/1000.0,"submit_ms":(saved-pre)/1000.0,"render_ms":(rendered-saved)/1000.0,"ok":result.ok,"undo":scene.session.state.battle.undo.size()})
			await process_frame
	print("LATENCY_PROBE: ",JSON.stringify(samples))
	scene.sound.stop_audio();scene.queue_free();await process_frame;quit()
