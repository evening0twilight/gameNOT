extends SceneTree
## Run from an empty directory with --main-pack; reads a retained save, never writes it.
func _initialize() -> void:
	var args: PackedStringArray=OS.get_cmdline_user_args()
	if args.size()!=1:printerr("Expected path to continuous campguide day05 save");quit(1);return
	var catalog=load("res://scripts/infrastructure/content_catalog.gd")
	var rules=load("res://scripts/domain/campaign_rules.gd")
	var store=load("res://scripts/infrastructure/campaign_store.gd")
	var learning=load("res://scripts/domain/camp_learning.gd")
	var guide=load("res://scripts/presentation/camp_guide.gd")
	var content: Dictionary=catalog.load_catalog()
	if not content.ok:quit(1);return
	var raw: String=FileAccess.get_file_as_string(args[0])
	var loaded: Dictionary=store.validate(JSON.parse_string(raw),content)
	if not loaded.ok:printerr("Export rejected retained campaign");quit(1);return
	var state: Dictionary=loaded.state
	if not learning.completed(state) or state.tutorial.camp_lessons.completed_day!=4 or state.campaign.day!=5:quit(1);return
	var fresh: Dictionary=rules.begin_campaign(content,"export-probe")
	if not learning.active(fresh) or learning.completed(fresh) or guide.info("roster").is_empty():quit(1);return
	var result: Dictionary=rules.reduce(state,{"command_id":"export-camp-lesson","root_decision_id":"export-camp-lesson","expected_revision":state.revision,"actor_id":"lin","kind":"camp_lesson","payload":{"topic":"medicine"}},content)
	if not result.ok or result.next_state.inventory!=state.inventory or result.next_state.actors!=state.actors or result.next_state.campaign!=state.campaign:quit(1);return
	print("PACKAGED_CAMPGUIDE: "+JSON.stringify({"save_sha256":raw.sha256_text(),"saved_completion_day":state.tutorial.camp_lessons.completed_day,"loaded_day":state.campaign.day,"new_campaign_active":true,"new_campaign_completed":false,"reading_changes_resources":false,"foundation":learning.FOUNDATION,"scenario":"actual continuous day05 save loaded from exported pack; read-only lesson probe"}))
	quit(0)
