extends "res://tests/gui_external.gd"
## Actual rendered macOS run on the non-primary display. Inputs replay recorded legal commands.
## This is automated host GUI evidence, not Windows/native/manual/human acceptance.
func launch() -> void:
	await super.launch()
	await process_frame
	var scene=current_scene
	var records: Array=JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path("res://").path_join("../outputs/p3-path-exploration.json")))
	var result_records: Array=[]
	var output: String=ProjectSettings.globalize_path("res://").path_join("../outputs/p3-gui")
	DirAccess.make_dir_recursive_absolute(output)
	var sequence: int=0
	for record: Dictionary in records:
		scene.session.state=scene.Rules.fresh(scene.session.content,"gui-"+record.mission)
		scene.session.state.campaign.day=int(scene.session.content.boards[record.mission].day)
		for actor: Dictionary in scene.session.state.actors.values():actor.fatigue=0
		if record.mission=="M24":scene.session.state.full_campaign.route="evacuation"
		scene.Rules.deploy(scene.session.state,scene.session.content,record.mission)
		scene.session.path="user://tests/p3-gui-%d/%s.json" % [Time.get_ticks_usec(),record.mission]
		var ok: bool=scene.session.store.save_slot(scene.session.path,scene.session.state,scene.session.content).ok
		scene.render()
		for frame: int in range(3):await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(output.path_join(record.mission+"-start.png"))
		for action: Dictionary in record.actions:
			sequence+=1
			var command: Dictionary={"command_id":"gui-%d"%sequence,"root_decision_id":"gui-%d"%sequence,"expected_revision":scene.session.state.revision,"kind":action.kind,"actor_id":action.actor,"payload":action.payload}
			var result: Dictionary=scene.session.submit(command)
			if not result.ok:ok=false;printerr("GUI_REPLAY_FAIL "+record.mission+" "+str(result));break
			if action.kind=="end_round" or scene.session.state.campaign.phase!="battle":
				scene.render();await process_frame
		var outcome: String=scene.session.state.campaign.get("last_result",{}).get("outcome","unfinished")
		ok=ok and outcome=="success"
		scene.render()
		for frame: int in range(3):await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(output.path_join(record.mission+"-result.png"))
		result_records.append({"mission":record.mission,"ok":ok,"outcome":outcome,"actions":record.actions.size(),"screen":DisplayServer.window_get_current_screen(),"primary":DisplayServer.get_primary_screen()})
		print("P3_GUI_PATH: ",record.mission," ",outcome," ok=",ok)
	var file:=FileAccess.open(output.path_join("replay.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"platform":OS.get_name(),"kind":"automated rendered legal-command replay","windows_acceptance":false,"human_acceptance":false,"records":result_records},"  "));file.close()
	print("P3_GUI_REPLAY_FINISHED: ",result_records.size())
	quit()
