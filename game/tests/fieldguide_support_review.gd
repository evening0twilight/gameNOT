extends SceneTree
func _initialize() -> void:
	root.hide();root.gui_embed_subwindows=true;call_deferred("run")
func run() -> void:
	var canvas:=SubViewport.new();canvas.size=Vector2i(1280,720);canvas.gui_embed_subwindows=true;canvas.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(canvas)
	var ui: Control=load("res://scenes/main.tscn").instantiate();canvas.add_child(ui);ui.reduced_motion=true
	ui.session.state=ui.Rules.begin_campaign(ui.session.content,"support-label-fixture");ui.session.state.campaign.day=5;ui.Rules.deploy(ui.session.state,ui.session.content,"M05")
	var id: String="responder_M05_2";var hero: Dictionary=ui.session.state.battle.heroes.su.duplicate(true);hero.id=id
	ui.session.state.battle.heroes.erase("su");ui.session.state.battle.heroes[id]=hero
	ui.title_screen=false;ui.selected=id;ui.action="move";ui.message="独立界面复核：临时支援员与同格装置";ui.render()
	await process_frame;await process_frame;await RenderingServer.frame_post_draw
	canvas.get_texture().get_image().save_png("res://../outputs/fieldguide-fixture-support.png")
	ui.sound.stop_audio();ui.queue_free();await create_timer(.2).timeout
	print("FIELDGUIDE_SUPPORT_GPU: isolated fixture rendered");quit()
