extends RefCounted
const I18n=preload("res://scripts/presentation/localization.gd")
## A presentation lesson follows real commands. No fabricated rewards or free actions.
static func enabled(ui: Control) -> bool:
	return ui.guidance_enabled and ui.session.state.tutorial.get("first_shift",{}).get("enabled",false)
static func active(ui: Control) -> bool:
	return enabled(ui) and ui.session.state.battle.mission_id=="M01" and ui.session.state.campaign.phase=="battle"
static func lesson(ui: Control) -> Dictionary:
	var learned: Dictionary=ui.session.state.tutorial.get("first_shift",{})
	var actions: Array=learned.get("actions",[])
	var next: Dictionary=ui.current_guidance().duplicate(true)
	if not actions.has("move"):
		return {"id":"move","number":1,"title":I18n.s("先走近需要帮助的人"),"why":I18n.s("前舱居民还在船的另一头。先靠近，才能稳定伤势和搬运。"),"how":I18n.s("点右侧「移动」，再点地图上的亮格。先看路线与消耗，点底部「确认行动」才会行动。"),"next":next}
	if not learned.get("forecast",false):
		return {"id":"forecast","number":2,"title":I18n.s("出发前，看清危险"),"why":I18n.s("橙色折线是机器本轮将攻击的区域。救人不要求消灭所有机器，可以先绕开它。"),"how":I18n.s("查看地图上的橙色预告。结束回合时机器才会执行；阅读这张卡不会让时间流逝。"),"next":{}}
	var kind: String=next.get("action","")
	var id: String="approach"
	if next.has("actor"):id="switch"
	elif kind=="end_round":id="round"
	elif kind=="stabilize":id="stabilize"
	elif kind=="pickup":id="pickup"
	elif kind=="extract":id="deliver"
	elif next.get("key","")=="return":id="return"
	elif kind=="leave_site" or next.get("key","")=="leave_move":id="leave"
	elif kind=="emergency_retreat":id="retreat"
	var copy: Dictionary={
		"approach":[3,I18n.s("靠近，再伸出援手"),I18n.s("稳定和搬运需要靠近目标。每人每轮有2行动点，可以交错操作。"),I18n.s("点「移动」，选亮格靠近居民。金框只是一个可行示例，你也可以选别的安全路线。")],
		"switch":[3,I18n.s("换一位伙伴接手"),I18n.s("一人的行动点用完，其他人仍可以行动。三个人可以分头救援。"),I18n.s("点右侧伙伴头像下的名字，查看他的行动点和可走范围。")],
		"round":[3,I18n.s("让下一轮开始"),I18n.s("目前需要等待下一轮行动点恢复。结束回合也会执行机器预告和环境变化。"),I18n.s("先看橙色危险区，再点「结束回合」核对风险，确认后继续。")],
		"stabilize":[4,I18n.s("先稳定伤势"),I18n.s("稳定后才能安全拾起居民。稳定只是救援的第一步，还没有把人送出去。"),I18n.s("新功能：点「稳定」，再点身旁的居民，确认预览。")],
		"pickup":[5,I18n.s("把居民带在身边"),I18n.s("现在可以搬运了。携带者走得更慢，需要把居民送到左下方箭头出口。"),I18n.s("新功能：点「拾起」，再点已稳定的居民，确认后观察身边的携带标记。")],
		"return":[6,I18n.s("带他回到出口"),I18n.s("携带不等于获救。先回到左下方箭头格，再完成交付。"),I18n.s("用「移动」沿安全路线返回。行动点不足时可换人，或确认结束回合。")],
		"deliver":[7,I18n.s("完成交付，才算救回"),I18n.s("你已经站在出口。交付后居民会记为获救，队员还能回到现场继续帮忙。"),I18n.s("新功能：点「交付」，检查预览后确认。接着用同样方法帮助另一位居民。")],
		"leave":[8,I18n.s("最后，让队员也回来"),I18n.s("必须目标已经完成。可以继续处理可选事务，也可以让队员回到出口离场。"),I18n.s("到箭头出口后点「撤出」。若想尝试专长、停机和其他办法，可展开全部操作。")],
		"retreat":[8,I18n.s("先保住还在场的人"),I18n.s("当前建议没有找到可继续完成的目标。撤退前会显示损失与人员后果。"),I18n.s("可展开完整操作自行处理，或查看撤退预览后再决定。")]}
	var row: Array=copy[id]
	return {"id":id,"number":row[0],"title":row[1],"why":row[2],"how":row[3],"next":next}
static func panel(ui: Control,box: VBoxContainer) -> void:
	var step: Dictionary=lesson(ui)
	ui.label(box,I18n.s("第一次救援 · %d / 8")%step.number).add_theme_color_override("font_color",ui.GOLD)
	ui.label(box,step.title).add_theme_font_size_override("font_size",24)
	ui.label(box,step.why)
	ui.label(box,step.how).add_theme_color_override("font_color",ui.TEAL)
	if step.id=="forecast":ui.button(box,I18n.s("我看清预告了"),func():ui.tutorial_ack("forecast"))
	elif step.next.has("actor"):
		ui.button(box,I18n.s("切换到")+ui.actor_name(step.next.actor),ui.preview_guidance)
	else:
		ui.label(box,I18n.s("已完成的动作会自动推进教学；取消预览不会扣行动点。")).add_theme_font_size_override("font_size",14)
	var space:=Control.new();space.size_flags_vertical=Control.SIZE_EXPAND_FILL;box.add_child(space)
	ui.button(box,I18n.s("展开全部操作 · 跳过教学"),func():ui.tutorial_ack("skip")).add_theme_font_size_override("font_size",14)
static func actions(ui: Control,box: VBoxContainer) -> void:
	var step: Dictionary=lesson(ui)
	var learned: Array=ui.session.state.tutorial.first_shift.actions
	var kinds: Array=["move"]
	for kind: String in ["stabilize","pickup","extract","leave_site"]:
		if learned.has(kind) or step.next.get("action","")==kind:kinds.append(kind)
	for kind: String in kinds:
		var button: Button=ui.button(box,ui.action_name(kind),func():
			ui.action=kind;ui.message=I18n.s("选择地图上的目标，再检查底部预览。");ui.render()
			if kind in ["extract","leave_site"]:ui.propose(kind,{}))
		button.icon=ui.Art.icon(kind)
		button.custom_minimum_size.y=52
		if kind==step.next.get("action",""):button.add_theme_stylebox_override("normal",ui.surface(Color("35524c"),8,ui.TEAL))
	if step.number>=3:
		ui.label(box,I18n.s("已学会的操作会留在这里。")).add_theme_font_size_override("font_size",14)
static func briefing(ui: Control,parent: Node) -> void:
	var frame:=HBoxContainer.new();frame.size_flags_horizontal=Control.SIZE_EXPAND_FILL;frame.add_theme_constant_override("separation",28);parent.add_child(frame)
	var picture=ui.Art.site_picture("ferry",Vector2(0,300));picture.size_flags_horizontal=Control.SIZE_EXPAND_FILL;frame.add_child(picture)
	var box:=VBoxContainer.new();box.custom_minimum_size.x=400;box.size_flags_vertical=Control.SIZE_SHRINK_CENTER;box.add_theme_constant_override("separation",18);frame.add_child(box)
	ui.label(box,I18n.s("第一场救援")).add_theme_color_override("font_color",ui.GOLD)
	ui.label(box,I18n.s("最后一班渡轮")).add_theme_font_size_override("font_size",32)
	ui.label(box,I18n.s("船上还有两位居民。\n带三位伙伴出发，把人接回岸边。"))
	ui.label(box,I18n.s("先学会移动，再一步步完成救援。\n不用先研究装备、培养或关系系统。")).add_theme_color_override("font_color",ui.MUTED)
	ui.button(box,I18n.s("开始救援 · 边做边学"),func():ui.propose("depart",ui.session.state.journey.draft.duplicate(true)))
	ui.button(box,I18n.s("我已熟悉玩法 · 完整准备"),func():ui.tutorial_ack("skip"))
static func camp(ui: Control,box: VBoxContainer) -> void:
	var heading:=HBoxContainer.new();box.add_child(heading)
	ui.label(heading,I18n.s("第一晚 · 回到灯下")).add_theme_font_size_override("font_size",28)
	var finish: Button=ui.button(heading,I18n.s("结束夜晚 · 准备明天"),ui.show_night_review);finish.custom_minimum_size.x=260;finish.autowrap_mode=TextServer.AUTOWRAP_OFF
	var columns:=HBoxContainer.new();columns.add_theme_constant_override("separation",24);box.add_child(columns)
	var left:=VBoxContainer.new();left.size_flags_horizontal=Control.SIZE_EXPAND_FILL;left.add_theme_constant_override("separation",14);columns.add_child(left)
	left.add_child(ui.Art.picture(ui.Art.narrative("office"),Vector2(0,195)))
	var saved: int=0
	for object: Dictionary in ui.session.state.battle.objects.values():
		if object.kind=="rescue" and object.delivered:saved+=1
	ui.label(left,I18n.s("渡轮行动结束，%d 位居民已送达。\n桌上留着温水，窗外的雨还没有停。")%saved)
	ui.label(left,I18n.s("今晚还可安排%d个项目、%d次短谈，都可以留空。\n睡眠会自然恢复疲劳，不必给每个人都安排休息。")%[maxi(0,2-int(ui.session.state.campaign.projects)),maxi(0,2-ui.session.state.campaign.talked.size())]).add_theme_color_override("font_color",ui.MUTED)
	ui.button(left,I18n.s("读今晚的行动记录"),func():night_record(ui))
	ui.button(left,I18n.s("其他安排与完整营地"),func():ui.tutorial_ack("skip"))
	var right:=VBoxContainer.new();right.size_flags_horizontal=Control.SIZE_EXPAND_FILL;right.add_theme_constant_override("separation",10);columns.add_child(right)
	ui.label(right,I18n.s("你的新手班组 · 看状态 → 按需安排 → 结束夜晚")).add_theme_color_override("font_color",ui.GOLD)
	for id: String in ui.session.state.journey.recruited:
		var actor: Dictionary=ui.session.state.actors[id]
		var card:=PanelContainer.new();card.add_theme_stylebox_override("panel",ui.surface(ui.SURFACE,12));right.add_child(card)
		var row:=HBoxContainer.new();row.add_theme_constant_override("separation",12);card.add_child(row)
		row.add_child(ui.Art.character(id,"camp","tired" if actor.fatigue>=70 else "neutral",Vector2(68,86),true))
		var info:=VBoxContainer.new();info.size_flags_horizontal=Control.SIZE_EXPAND_FILL;row.add_child(info)
		ui.label(info,ui.actor_name(id)+I18n.s(" · 疲劳 %d → 睡后 %d")%[actor.fatigue,ui.Crew.overnight_fatigue(ui.session.state,id,actor.fatigue)])
		var role: String={"lin":I18n.s("救援 · 先稳伤，再带人回来"),"xu":I18n.s("机动 · 跨越障碍，接应伙伴"),"su":I18n.s("辅助 · 标记机器，配合队友")}.get(id,"")
		ui.label(info,role).add_theme_font_size_override("font_size",16)
		var actions:=HBoxContainer.new();info.add_child(actions)
		var arrange: Button=ui.button(actions,I18n.s("恢复或培养"),func():project(ui,id));arrange.add_theme_font_size_override("font_size",16);arrange.custom_minimum_size.x=145;arrange.autowrap_mode=TextServer.AUTOWRAP_OFF
		ui.button(actions,I18n.s("聊两句"),func():preload("res://scripts/presentation/camp_workspace.gd").short_talk(ui,id)).add_theme_font_size_override("font_size",16)
	ui.label(right,I18n.s("三位伙伴已可持续培养。其他成员会在后续行动中陆续加入。")).add_theme_font_size_override("font_size",16)
static func project(ui: Control,id: String) -> void:
	var dialog: Dictionary=ui.modal(ui.actor_name(id)+I18n.s(" · 今晚怎么安排"))
	ui.label(dialog.box,I18n.s("恢复：为明天留体力。培养：用物资换经验，同时增加疲劳。选中后仍会显示完整预览。"))
	for kind: String in ["rest","train","treat"]:
		var command: Dictionary={"command_id":"lesson-project","root_decision_id":"lesson-project","expected_revision":ui.session.state.revision,"actor_id":id,"kind":kind,"payload":{}}
		var preview: Dictionary=ui.session.preview(command)
		var button: Button=ui.button(dialog.box,ui.action_name(kind),func():dialog.window.queue_free();ui.selected=id;ui.propose(kind,{}))
		button.disabled=not preview.ok
		if preview.ok:
			var before: Dictionary=ui.session.state.actors[id];var after: Dictionary=preview.next_state.actors[id]
			ui.label(dialog.box,I18n.s("经验 %d → %d · 疲劳 %d → %d · %s")%[before.xp,after.xp,before.fatigue,after.fatigue,ui.resource_text(preview.costs.resources)])
		else:ui.label(dialog.box,ui.error_text(preview.error_code))
	ui.button(dialog.box,I18n.s("今晚不安排"),dialog.window.queue_free)
static func night_record(ui: Control) -> void:
	var dialog: Dictionary=ui.modal(I18n.s("渡轮 · 今晚留下的记录"))
	dialog.box.add_child(ui.Art.picture(ui.Art.narrative("office"),Vector2(0,200)))
	ui.label(dialog.box,I18n.s("门关上以后，雨声退到了玻璃另一侧。桌上的记录还没有收好，湿纸的边角慢慢卷起来。"))
	for entry: Dictionary in ui.session.content.domains.scripts.community:
		if entry.source=="M01":
			var facts: Dictionary=ui.StoryFacts.community(ui.session.state,ui.session.content,entry)
			if not facts.is_empty():ui.label(dialog.box,facts.text)
	ui.label(dialog.box,I18n.s("今天发生的事会留下，今晚不必把每件事都谈清楚。先给明天留一点余地。"))
	ui.button(dialog.box,I18n.s("回到大家身边"),dialog.window.queue_free)

static func settlement(ui: Control,box: VBoxContainer) -> void:
	var s: Dictionary=ui.session.state
	var saved: int=0
	for object: Dictionary in s.battle.objects.values():
		if object.kind=="rescue" and object.delivered:saved+=1
	ui.label(box,I18n.s("渡轮 · 救援结束")).add_theme_font_size_override("font_size",30)
	var row:=HBoxContainer.new();row.add_theme_constant_override("separation",28);box.add_child(row)
	var scene=ui.Art.site_picture("ferry",Vector2(0,380));scene.size_flags_horizontal=Control.SIZE_EXPAND_FILL;row.add_child(scene)
	var result:=VBoxContainer.new();result.custom_minimum_size.x=440;result.add_theme_constant_override("separation",12);row.add_child(result)
	ui.label(result,I18n.s("%d / 2 位居民已送达")%saved).add_theme_font_size_override("font_size",30)
	ui.label(result,I18n.s("人已上岸。现在轮到照顾留下来的伙伴。") if saved==2 else I18n.s("没有回来的人也会留在记录里。先看清结果，再安排今晚。"))
	ui.label(result,"\n".join(Array(ui.risk_text(s).split("\n")).slice(0,2)) if s.campaign.last_result.injured.is_empty() else ui.risk_text(s)).add_theme_color_override("font_color",ui.MUTED)
	ui.label(result,I18n.s("本次获得 · ")+ui.resource_text(s.campaign.last_result.reward))
	for id: String in s.campaign.last_result.get("xp_receipts",{}):
		var growth: Dictionary=s.campaign.last_result.xp_receipts[id]
		ui.label(result,ui.actor_name(id)+I18n.s(" · 经验 %d → %d")%[growth.before,growth.after]).add_theme_font_size_override("font_size",16)
	ui.button(result,I18n.s("回到营地 · 安排第一晚"),func():ui.propose("enter_camp",{}))
	ui.button(result,I18n.s("行动记录与公开方式"),func():report(ui))
	ui.button(result,I18n.s("查看完整结算"),func():report(ui,true))
static func report(ui: Control,detailed: bool=false) -> void:
	var dialog: Dictionary=ui.modal(I18n.s("渡轮 · 完整结算") if detailed else I18n.s("渡轮 · 让记录与事实一致"))
	if detailed:
		var result: Dictionary=ui.session.state.campaign.last_result
		ui.label(dialog.box,ui.risk_text(ui.session.state))
		for row: Dictionary in result.get("reward_rows",[]):ui.label(dialog.box,row.reason+"："+ui.resource_text(row.resources))
		for id: String in result.get("xp_receipts",{}):
			var growth: Dictionary=result.xp_receipts[id]
			ui.label(dialog.box,ui.actor_name(id)+I18n.s(" · 经验 %d → %d")%[growth.before,growth.after])
		for id: String in result.facts:
			ui.label(dialog.box,ui.object_name(id)+" · "+{"saved":I18n.s("已救出"),"completed":I18n.s("已完成"),"lost":I18n.s("已失去"),"unresolved":I18n.s("未完成")}.get(result.facts[id],str(result.facts[id])))
	for entry: Dictionary in ui.session.content.domains.scripts.community:
		if entry.source!="M01":continue
		ui.label(dialog.box,ui.StoryFacts.community(ui.session.state,ui.session.content,entry).text)
		var flag: String="community.M01.public"
		if ui.session.state.chapter_one.flags.has(flag):
			var choice: String="publish" if ui.session.state.chapter_one.flags[flag] else "archive"
			ui.label(dialog.box,ui.story_lines(entry.id,"choices."+choice,entry.choices[choice]))
		else:
			for choice: String in ["publish","archive"]:
				ui.button(dialog.box,ui.I18n.t("p2.community_"+choice),func():dialog.window.queue_free();ui.propose("community_report",{"choice":choice}))
	ui.Screens.appraisal_log(ui,dialog.box)
	ui.button(dialog.box,I18n.s("回到救援结果"),dialog.window.queue_free)
