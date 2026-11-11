extends SceneTree
const I18n=preload("res://scripts/presentation/localization.gd")
var checks: int=0
var failures: int=0
func check(value: bool,context: String) -> void:
	checks+=1
	if not value:failures+=1;printerr("P4_UI_FAIL: "+context)
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var names: Array=["ui_focus","ui_confirm","ui_cancel","ui_error","ui_page","ui_save","move","attack","push","stabilize","pickup","work","drop","extract","machine_scout","machine_welder","machine_hauler","machine_skimmer","machine_relay","machine_sentinel","objective","injury","end_round","ending","ambient_camp","ambient_field"]
	for id: String in names:
		var stream: AudioStreamWAV=load("res://assets/audio_p4/%s.wav"%id)
		check(stream!=null and stream.get_length()>0,"actual PCM audio "+id)
	var scene=load("res://scenes/main.tscn").instantiate();root.add_child(scene)
	var original: String=FileAccess.get_file_as_string(scene.session.path)
	scene.sound.music_volume=.2;scene.sound.effects_volume=.8;scene.sound.muted=false;scene.sound.apply_levels()
	check(not is_equal_approx(AudioServer.get_bus_volume_db(AudioServer.get_bus_index("Music")),AudioServer.get_bus_volume_db(AudioServer.get_bus_index("Effects"))),"independent audio bus levels")
	scene.sound.muted=true;scene.sound.apply_levels()
	check(AudioServer.is_bus_mute(AudioServer.get_bus_index("Music")) and AudioServer.is_bus_mute(AudioServer.get_bus_index("Effects")),"mute both buses")
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var fixture: Dictionary=scene.Rules.fresh(scene.session.content,"p4-ui-fixture")
	fixture.campaign.day=20;fixture.chapter_one.main_completed=19
	scene.Rules.settle(fixture,scene.session.content);fixture.campaign.phase="camp"
	fixture.product.facilities.communications=2
	for locale: String in ["zh_CN","en_XA"]:
		I18n.locale=locale
		for font: int in [16,20,24]:
			scene.font_size=font;scene.session.state=fixture.duplicate(true);scene.render()
			for method: String in ["show_workshop","show_help","show_history_repair","audio_settings","new_campaign"]:
				scene.call(method)
				for frame: int in range(3):await process_frame
				for child: Node in scene.get_children():
					if child is Window and not child is ConfirmationDialog:
						check(child.size.x<=root.size.x and child.size.y<=root.size.y,"modal bounds "+method+locale+str(font))
						child.queue_free()
				await process_frame
	check(FileAccess.get_file_as_string(scene.session.path)==original,"presentation review never writes campaign fixtures")
	# Ordinary reversible actions commit once, with undo, without a modal confirmation.
	scene.session.state=scene.Rules.fresh(scene.session.content,"p4-input-fixture");scene.selected="lin";scene.guidance_enabled=true
	scene.propose("move",{"cell":[1,6]})
	check(scene.Rules.same(scene.session.state.battle.heroes.lin.cell,[1,7]) and scene.inline_pending and not scene.confirmation.visible,"inline preview without mutation or modal")
	scene.propose("move",{"cell":[1,6]})
	check(scene.Rules.same(scene.session.state.battle.heroes.lin.cell,[1,6]),"second click confirms exact ordinary action")
	scene.finish_feedback()
	scene.propose("undo",{})
	check(scene.Rules.same(scene.session.state.battle.heroes.lin.cell,[1,7]),"undo restores ordinary move")
	scene.propose("move",{"cell":[1,6]})
	scene.selected="xu";scene.render()
	check(not scene.inline_pending and scene.pending.is_empty(),"changing actor removes obsolete inline preview")
	scene.selected="lin"
	var state: String=scene.session.store.canonical(scene.session.state)
	scene.propose("emergency_retreat",{"confirmed":true})
	check(scene.confirmation.visible and scene.session.store.canonical(scene.session.state)==state,"irreversible action still previews without mutation")
	scene.confirmation.hide()
	scene.session.state.product.withdrawn.append("lin")
	scene.session.state.chapter_one.scenes.P_lin_1={"seen":true,"choice":"","status":"seen"}
	scene.show_story("P_lin_1")
	for frame: int in range(2):await process_frame
	var choice_buttons: int=0
	for child: Node in scene.get_children():
		if child is Window and not child is ConfirmationDialog:
			choice_buttons+=child.find_children("*","Button",true,false).size();child.queue_free()
	check(choice_buttons==0,"withdrawn scene summary has no live dialogue choices")
	scene.queue_free();await process_frame;I18n.initialize()
	print("P4_PRESENTATION_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
