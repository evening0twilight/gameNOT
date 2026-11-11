extends "res://tests/gui_external.gd"
## Runtime capture with isolated legal-action fixtures, not a natural playthrough.
var scene: Node
var records: Array=[]
func pause(seconds: float) -> void:await create_timer(seconds).timeout
func reset(title: String) -> void:
	scene.finish_feedback();scene.confirmation.hide()
	scene.session.state=scene.Rules.fresh(scene.session.content,"feedback-movie-fixture")
	scene.selected="lin";scene.action="move";scene.pending={};scene.inline_pending=false
	scene.message=title;scene.render()
func act(kind: String,payload: Dictionary,caption: String) -> void:
	scene.action=kind;scene.propose(kind,payload)
	scene.confirmation.hide();scene.commit_pending()
	if not scene.feedback_active():push_error("Movie action did not animate: "+kind);quit(1);return
	scene.message=caption;scene.render()
	records.append({"kind":kind,"payload":payload,"duration":scene.feedback_plan.duration,"revision":scene.session.state.revision})
	while scene.feedback_active():await process_frame
	await pause(.7)
func launch() -> void:
	await super.launch();await process_frame
	scene=current_scene
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	scene.sound.muted=false;scene.sound.music_volume=.1;scene.sound.effects_volume=.8;scene.sound.apply_levels()
	scene.font_size=20;reset("操作反馈演示 · 隔离场景；玩法仍由同一套规则执行")
	scene.show_intro(false,2);await pause(3)
	for child: Node in scene.get_children():
		if child is Window and not child is ConfirmationDialog:child.queue_free()
	await process_frame
	scene.new_campaign();await pause(3)
	for child: Node in scene.get_children():
		if child is Window and not child is ConfirmationDialog:child.queue_free()
	await process_frame
	await act("move",{"cell":[1,4]},"移动：按格换步，脚步声跟随落脚")
	await act("move",{"cell":[3,3]},"拐角：沿路径改变朝向；动作期间不会重复提交")
	reset("近身攻击示例")
	var enemy: String=str(scene.session.state.battle.enemies.keys()[0])
	scene.session.state.battle.enemies[enemy].cell=[2,6]
	scene.session.state.battle.heroes.lin.cell=[1,6];scene.render();await pause(.8)
	await act("attack",{"target":enemy},"攻击：准备 → 出手 → 命中；显示实际生命变化")
	await act("push",{"target":enemy},"推移：目标沿格位移，碰撞结果由规则决定")
	reset("救援示例")
	var target: String=""
	for object: Dictionary in scene.session.state.battle.objects.values():
		if object.kind=="rescue":target=object.id;break
	var cell: Array=scene.session.state.battle.objects[target].cell
	scene.session.state.battle.heroes.lin.cell=[int(cell[0])-1,int(cell[1])];scene.render();await pause(.8)
	await act("stabilize",{"target":target},"急救：俯身处理，稳定后有标记和完成声")
	await act("pickup",{"target":target},"拾起：伸手与抬起，携带的伤员随队员移动")
	scene.session.state.battle.heroes.lin.ap=2
	await act("move",{"cell":[1,4]},"搬运：伤员保持可见；下一步引导指向出口")
	# Jump to a separate delivery fixture, clearly labelled, instead of implying a skipped move was legal.
	scene.session.state.battle.heroes.lin.cell=[0,6];scene.session.state.battle.heroes.lin.ap=2
	scene.message="出口交付示例 · 独立测试位置";scene.render();await pause(1)
	await act("extract",{},"交付：送达提示与声音；稳定、拾起和送达是不同阶段")
	reset("施工示例 · 独立测试位置")
	for object: Dictionary in scene.session.state.battle.objects.values():
		if object.kind=="work" and object.prerequisites.is_empty():
			scene.session.state.battle.heroes.lin.cell=object.cell.duplicate();scene.render();await pause(.8)
			await act("interact",{"target":object.id},"施工：手部动作、工具敲击和实际进度反馈")
			break
	reset("机器行动与受击示例 · 独立测试位置")
	for e: Dictionary in scene.session.state.battle.enemies.values():
		var cells: Array=scene.Rules.Hazards.footprint(scene.session.state.battle,e,scene.Rules)
		if not cells.is_empty():scene.session.state.battle.heroes.lin.cell=cells[0].duplicate();break
	scene.render();await pause(1)
	await act("end_round",{},"机器按顺序行动；受击闪烁、后仰与伤害数字对应实际结算")
	await pause(1)
	var output: String=ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-movie.json")
	var file:=FileAccess.open(output,FileAccess.WRITE)
	file.store_string(JSON.stringify({"kind":"engine runtime capture of isolated legal-action fixtures","actions":records,"screen":DisplayServer.window_get_current_screen(),"primary":DisplayServer.get_primary_screen(),"human_acceptance":false},"  "));file.close()
	scene.sound.stop_audio();await pause(.5)
	print("FEEDBACK_MOVIE_OK: ",records.size()," legal actions")
	quit()
