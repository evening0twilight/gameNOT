extends RefCounted
const Learning=preload("res://scripts/domain/camp_learning.gd")
const TEXT={
	"projects":["恢复与训练","先看疲劳和自然休息后的状态，再决定是否安排项目。","选择一位伙伴，查看恢复或训练的费用与收益；确认才执行。今晚不安排项目也能继续。"],
	"talk":["聊两句","让两位伙伴在任务后交流，了解彼此。","选择发起者和交谈对象，先看预览。聊天和夜间项目使用不同的次数限制。"],
	"stories":["第二晚 · 听听伙伴的故事","现场的选择会延续到营地。故事可以帮助你理解伙伴的顾虑。","打开今晚的故事，选择一个人物，逐页阅读后再决定回应。可以暂缓，不必为了教程作出选择。"],
	"equipment":["第三晚 · 带上已有工具","已有的撬棍和医疗包需要配给队员，现场才能使用。","选择一件已有工具和携带者，查看预览再确认。出发前还能调整；本次不需要购买。"],
	"roster":["第四晚 · 安排下一班","陈砚加入后，你可以轮换出勤，让疲劳的伙伴休息。","选择最多三位已入队伙伴，保存下一班阵容。查看疲劳与角色分工，也可以保留原阵容。"],
	"supplies":["补充物资","物资不足时，部分治疗和训练无法安排。","先看当前余额与购买费用，再决定是否补充。无需为了提示购买。"],
	"medicine":["准备药品","拥有医疗包还需要药品，才能在现场治疗。","先制作药品，再在出发准备里装入本次用量，并给队员装备医疗包。制作有资源成本。"],
	"growth":["查看成长与专长","经验和训练阶段决定角色能用哪些专长。","选一位伙伴查看档案，比较普通操作和专长的实际收益。看到未解锁专长不代表现在能用。"],
	"relationships":["理解协作条件","伙伴间的信任和共同经历会影响协作，关系紧张时可能需要保障。","查看具体关系和未满足的条件，再安排共同出勤或沟通。数值变化不等于历史问题已经解决。"],
	"mentors":["一次合适的带教","带教需要满足合作与成长条件，且收益高于普通训练。","选择师生组合，核对经验、物资与双方疲劳。带教占用夜间项目和学员的训练阶段，不必立即使用。"],
	"operations":["限时的现场支援","完成的现场设施可能提供后续支援，但有可用日期和次数限制。","查看设施是否完好、是否需要补修，以及剩余窗口；符合条件时再选择参加者。离开今晚前留意截止日期。"],
	"city":["看看城市的变化","任务结果会改变街区状态，并影响后续机会。","打开城市记录，查看已经发生的事实与街区变化；阅读不消耗夜间项目。"],
	"journal":["回看记录与约定","人物的计划和已发生的故事都可以回看。","打开记录，核对已经答应的事、当前进展和章节结果。阅读不会作出新的承诺。"],
	"evidence":["整理证据","现在处于证据整理的可用时段，遗漏的记录可能影响后续路线。","选择需要复核的记录，查看费用和条件再确认；整理不会自动公开。"],
	"publish":["决定公开范围","已有证据可以公开，是否隐去个人信息会产生不同后果。","比较隐去信息和完整公开的说明，预览后再决定。教程不会替你公开。"],
	"route":["第23晚 · 确定最终路线","下一次出勤将进入终战，需要先确定团队的去向。","查看各条路线的条件和已有约定，再选择路线并确认。结束今晚前仍可调整。"],
	"history":["修复旧事","历史裂痕需要承认问题和后续实际行动，不能只靠聊天消除。","打开旧事，查看当前阶段与已有事实；只有满足条件时才确认修复。"],
	"groups":["一起安排夜间项目","多位伙伴都需要恢复时，可以集中安排，减少重复操作。","先选择项目和参加者，核对总费用、个人状态及项目次数，再确认。"],
	"purchase":["选择一件新工具","新工具提供额外方法，但会占用资金、零件和携带位置。","这里只查看这一件：先比较用途和费用，购买后再分配携带者。现场会另行介绍用法。"],
	"facility":["改善营地设施","设施升级会持续改变后勤条件，适合解决反复出现的需求。","这里只查看这一处：比较下一等级效果和费用，确认后升级。可以先保留资源。"]}
static func active(ui: Control) -> bool:return ui.guidance_enabled and Learning.active(ui.session.state)
static func info(topic: String) -> Array:return TEXT.get(topic.split(":")[0],[])
static func title(ui: Control,topic: String) -> String:
	if topic.begins_with("purchase:"):return ui.I18n.t("p4.item."+topic.get_slice(":",1))
	if topic.begins_with("facility:"):return ui.I18n.t("p4.facility."+topic.get_slice(":",1))
	if topic=="stories":return ui.I18n.t("quality.camp_story")
	if topic=="equipment":return ui.I18n.s("已有装备")
	if topic=="roster":return ui.I18n.s("下一班阵容")
	return ui.I18n.s(info(topic)[0])
static func explanation(ui: Control,box: Node,topic: String) -> void:
	var text: Array=info(topic)
	ui.label(box,ui.I18n.s(text[0])+(" · "+title(ui,topic) if topic.contains(":") else "")).add_theme_color_override("font_color",ui.GOLD)
	ui.label(box,text[1]).add_theme_font_size_override("font_size",maxi(16,ui.font_size-2))
	var how: Label=ui.label(box,text[2]);how.add_theme_color_override("font_color",ui.TEAL);how.add_theme_font_size_override("font_size",maxi(16,ui.font_size-2))
static func navigation(ui: Control,box: VBoxContainer) -> void:
	var s: Dictionary=ui.session.state
	ui.label(box,ui.I18n.s("基础教程已完成 · 自主安排") if Learning.completed(s) else ui.I18n.s("基础引导 · 第%d/4晚")%mini(4,int(s.campaign.day))).add_theme_color_override("font_color",ui.TEAL)
	if not Learning.completed(s):ui.label(box,ui.I18n.s("休息 → 故事 → 装备 → 配队；第四晚结束后进入自主阶段。")).add_theme_font_size_override("font_size",maxi(14,ui.font_size-4))
	var topic: String=Learning.offer(s,ui.session.content)
	if not topic.is_empty():
		var panel:=PanelContainer.new();panel.add_theme_stylebox_override("panel",ui.surface(Color("203a3a"),10,ui.TEAL));box.add_child(panel)
		var body:=VBoxContainer.new();body.add_theme_constant_override("separation",8);panel.add_child(body)
		explanation(ui,body,topic)
		var actions:=HFlowContainer.new();body.add_child(actions)
		ui.button(actions,ui.I18n.s("了解并打开"),func():if ui.camp_ack(topic):open_feature(ui,topic))
		ui.button(actions,ui.I18n.s("明白了 · 稍后再用"),func():ui.camp_ack(topic))
	var due: String=Learning.urgent(s,ui.session.content)
	if not due.is_empty() and Learning.known(s).has(due):
		ui.button(box,ui.I18n.s("离开今晚前留意 · ")+title(ui,due),func():open_feature(ui,due))
	var nav:=HFlowContainer.new();nav.add_theme_constant_override("h_separation",8);box.add_child(nav)
	for learned: String in Learning.known(s):
		if learned in ["projects","talk"]:continue
		ui.button(nav,title(ui,learned),func():details(ui,learned))
	ui.button(nav,ui.I18n.s("按需查阅营地功能"),func():browse(ui))
static func browse(ui: Control) -> void:
	var dialog: Dictionary=ui.modal(ui.I18n.s("按需查阅营地功能"))
	ui.label(dialog.box,ui.I18n.s("选择一项查看用途。尚未到使用时机的功能，会在之后出现；关闭手册不会跳过教学。"))
	for topic: String in Learning.available(ui.session.state,ui.session.content):
		ui.button(dialog.box,title(ui,topic),func():dialog.window.queue_free();details(ui,topic))
static func details(ui: Control,topic: String) -> void:
	var dialog: Dictionary=ui.modal(title(ui,topic));explanation(ui,dialog.box,topic)
	ui.button(dialog.box,ui.I18n.s("了解并打开"),func():dialog.window.queue_free();if ui.camp_ack(topic):open_feature(ui,topic))
	ui.button(dialog.box,ui.I18n.s("明白了 · 稍后再用"),func():dialog.window.queue_free();ui.camp_ack(topic))
static func night_review(ui: Control,box: VBoxContainer,window: Window) -> bool:
	if not active(ui) or ui.session.state.campaign.day<2:return false
	var topic: String=Learning.pending(ui.session.state)
	if not topic.is_empty():
		ui.label(box,ui.I18n.s("结束前认识今晚这一项；无需购买或执行项目。"))
		explanation(ui,box,topic)
		ui.button(box,ui.I18n.s("明白了 · 继续夜间总结"),func():window.queue_free();if ui.camp_ack(topic):ui.show_night_review())
		return true
	if not Learning.completed(ui.session.state) and ui.session.state.campaign.day>=4:
		ui.label(box,ui.I18n.s("基础教程完成：移动与救援、夜间恢复、故事、装备和配队。结束今晚后，自主安排；新功能仍会按场景逐项提示。"))
	return false
static func open_feature(ui: Control,topic: String) -> void:
	if topic.begins_with("purchase:"):ui.show_workshop("purchase",topic.get_slice(":",1));return
	if topic.begins_with("facility:"):ui.show_workshop("facility",topic.get_slice(":",1));return
	match topic:
		"equipment":ui.show_workshop("owned");return
		"supplies":ui.show_workshop("supplies");return
		"roster":ui.plan_next_roster();return
		"city":ui.Screens.city(ui);return
		"relationships":ui.Screens.relationships(ui);return
		"history":ui.show_history_repair();return
	var dialog: Dictionary=ui.modal(title(ui,topic))
	match topic:
		"stories":ui.render_story_list(dialog.box)
		"mentors":
			ui.render_mentors(dialog.box)
			if dialog.box.get_child_count()==0:
				ui.label(dialog.box,ui.I18n.s("今晚暂无可用的带教组合。"))
				ui.label(dialog.box,ui.I18n.t("p2.mentorship_unavailable"))
				ui.label(dialog.box,ui.I18n.s("也请核对今晚剩余项目、双方疲劳和物资；条件满足后，这里会出现可选组合。"))
		"operations":ui.Screens.operations(ui,dialog.box)
		"journal","evidence","publish","route":ui.render_campaign_options(dialog.box,false,topic)
		"medicine":ui.button(dialog.box,ui.I18n.t("p3.craft_medicine"),func():dialog.window.queue_free();ui.propose("craft_medicine",{}))
		"groups":
			for kind: String in ["train","treat","rest"]:ui.button(dialog.box,ui.I18n.t("p2.group")%ui.action_name(kind),func():dialog.window.queue_free();ui.group_project(kind))
		"projects","talk","growth":
			for id: String in ui.session.state.journey.recruited:
				ui.button(dialog.box,ui.actor_name(id),func():
					dialog.window.queue_free()
					if topic=="projects":ui.FirstShift.project(ui,id)
					elif topic=="talk":ui.CampWorkspace.short_talk(ui,id)
					else:ui.Screens.profile(ui,id))
