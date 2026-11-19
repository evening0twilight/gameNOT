extends "res://tests/release_visible_campaign.gd"
## Two fresh processes share a deliberately isolated user://. Never use player files.
const DAMAGED = "damaged test autosave"
const RESTART = "res://slot-review-restart.json"

func popup() -> Window:
	return controls() as Window

func send_key(viewport: Viewport, code: Key) -> void:
	for down: bool in [true,false]:
		var key := InputEventKey.new()
		key.keycode = code
		key.pressed = down
		viewport.push_input(key, true)
	await settle()

func to_title() -> bool:
	await send_key(canvas, KEY_ESCAPE)
	return await press(ui.I18n.t("baseline018.df0379d3d6af"))

func create_campaign() -> bool:
	for key in ["baseline018.383860206bb4", "p4.start"]:
		if not await press(ui.I18n.t(key)):
			return false
	return not ui.title_screen

func prepare() -> bool:
	if not await create_campaign():
		return false
	var first: String = ui.session.path
	var first_id: String = ui.session.state.campaign.id
	var menu: MenuButton = button(ui.I18n.t("ui.6ca5a77d24c4")) as MenuButton
	if menu == null or not await hit(menu, menu.text) or not menu.get_popup().visible:
		errors.append("Could not open the game menu")
		return false
	# Click the first row of the embedded options menu (Manual save).
	var menu_popup := menu.get_popup()
	var point := Vector2(menu_popup.position) + Vector2(menu_popup.size.x / 2.0, 13.0)
	for pressed: bool in [true, false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.global_position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		canvas.push_input(event, true)
	await settle()
	if not await press("位置01 · 空") or not await press("开始救援 · 边做边学"):
		return false
	if not await hit(ui.confirmation.get_ok_button(), "confirm departure") or not await to_title():
		return false
	if not await create_campaign():
		return false
	var second: String = ui.session.path
	var second_id: String = ui.session.state.campaign.id
	var manual: String = first.get_base_dir().path_join("manual-01.json")
	var backup: bool = ui.session.store.load_slot(first, ui.session.content, true).ok
	var manual_valid: bool = ui.session.store.load_slot(manual, ui.session.content).ok
	print("Two new campaigns=", first_id != second_id, " backup=", backup, " manual=", manual_valid)
	if first_id == second_id or not backup or not manual_valid:
		return false
	# Damage only the older campaign of the two created in this temporary project.
	var invalid := FileAccess.open(first, FileAccess.WRITE)
	invalid.store_string(DAMAGED)
	invalid.close()
	if not await to_title() or not await press(ui.I18n.t("baseline018.fbe77b429bd8")):
		return false
	var recover_label: String = first_id + " · " + ui.I18n.t("ui.1ae486278078")
	print("Older campaign recovery offered=", button(recover_label) != null)
	if not await press(recover_label):
		return false
	popup().close_requested.emit()
	await settle()
	var active := ConfigFile.new()
	if active.load("user://p4_active_slot.cfg") != OK:
		return false
	var untouched: bool = ui.session.path == second and active.get_value("campaign", "path", "") == second
	print("Cancel kept B in memory and on disk=", untouched)
	if not untouched or not await press(recover_label):
		return false
	var backup_label := "autosave.json.bak · " + str(ui.I18n.t("p3.slot_label") % [first_id,1])
	if not await press(backup_label):
		return false
	var preserved := false
	for entry in DirAccess.get_files_at(first.get_base_dir()):
		if entry.begins_with("autosave.json.damaged-"):
			preserved = FileAccess.get_file_as_string(first.get_base_dir().path_join(entry)) == DAMAGED
	var restored: bool = ui.session.path == first and ui.session.state.campaign.id == first_id and not ui.title_screen
	print("Restored A=", restored, " preserved damaged bytes=", preserved)
	if not preserved or not restored:
		return false
	for file: String in [first, first + ".bak"]:
		if FileAccess.file_exists(file) and DirAccess.remove_absolute(file) != OK:
			return false
	if DirAccess.rename_absolute(manual, manual + ".bak") != OK:
		return false
	var restart := FileAccess.open(RESTART, FileAccess.WRITE)
	restart.store_string(JSON.stringify({"path": first, "id": first_id}))
	restart.close()
	return true

func recover_after_restart() -> bool:
	var expected: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(RESTART))
	var resume: Button = button(ui.I18n.t("baseline018.b5fbc7830ee2") % 1)
	print("Fresh process: missing primary, no false Continue=", ui.title_screen and resume == null)
	if not ui.title_screen or resume != null:
		return false
	var slot_button: Button
	for language: String in ["zh_CN", "zh_TW", "en"]:
		if ui.I18n.locale != language:
			if not await press(ui.I18n.t("ui.f5bb41e345b5")) or not await press(ui.I18n.NAMES[language]):
				return false
		if not await press(ui.I18n.t("baseline018.186908b78346")):
			return false
		var detail: String = ui.I18n.t("baseline018.fd6cf6476633") % [1, ui.I18n.t("p2.briefing")]
		var caption: String = ui.I18n.t("baseline018.f857ef1eb9e2") % [1, detail] + " · manual-01.json.bak"
		slot_button = button(caption)
		print("Visible localized recovery row [", language, "] ", caption, " verified=", slot_button != null)
		if slot_button == null:
			return false
		if language != "en":
			popup().close_requested.emit()
			await settle()
	if not await hit(slot_button, "restore numbered backup"):
		return false
	var restored: bool = ui.session.path == expected.path and ui.session.state.campaign.id == expected.id and not ui.title_screen and ui.session.store.load_slot(expected.path, ui.session.content).ok
	print("Sole numbered manual backup restored original campaign=", restored)
	return restored

func run() -> void:
	var project := ProjectSettings.globalize_path("res://").trim_suffix("/").get_file()
	var user_dir := OS.get_user_data_dir()
	if not project.begins_with("night-tide-slot-review-") or user_dir.get_file() != project:
		printerr("Use tools/review_release_slots.py to create a disposable project for this check.")
		quit(2)
		return
	var marker := FileAccess.open("res://slot-review-directory.txt", FileAccess.WRITE)
	marker.store_string(user_dir)
	marker.close()
	canvas = SubViewport.new()
	canvas.size = Vector2i(1280,720)
	canvas.gui_embed_subwindows = true
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	ui = load("res://scenes/main.tscn").instantiate()
	canvas.add_child(ui)
	await settle()
	var success: bool
	if OS.get_cmdline_user_args().has("--slot-review-cold"):
		success = await recover_after_restart()
	else:
		success = await prepare()
	if not success:
		printerr("SLOT_RECOVERY_FAILED ", errors)
	ui.sound.stop_audio()
	await create_timer(.6).timeout
	ui.queue_free()
	await settle()
	quit(0 if success else 1)
