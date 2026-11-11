extends "res://tests/full_playthrough.gd"
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
func run() -> void:
	content=Catalog.load_catalog()
	use_specialties=false
	var difficulty: String="standard"
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--difficulty="):difficulty=argument.trim_prefix("--difficulty=")
	if difficulty not in ["relaxed","standard","hard"]:quit(2);return
	var failures: int=0
	var counts: Dictionary={"success":0,"partial":0,"failed":0}
	for variant: String in ["A","B"]:
		for mission: String in content.boards:
			s=Rules.fresh(content,"p4-matrix",{"difficulty":difficulty,"variant":variant});log=[]
			var board: Dictionary=content.boards[mission]
			s.campaign.day=int(board.day)
			for actor: Dictionary in s.actors.values():actor.fatigue=0
			if mission=="M24":s.full_campaign.route="evacuation"
			Rules.deploy(s,content,mission)
			solve(board)
			var outcome: String=s.campaign.get("last_result",{}).get("outcome","unfinished")
			var valid: bool=s.campaign.phase=="settlement" and Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,content))),content).ok
			if valid and mission!="M24":valid=attempt("enter_camp",s.battle.heroes.keys()[0])
			if not valid:failures+=1
			counts[outcome]=int(counts.get(outcome,0))+1
			records.append({"mission":mission,"difficulty":difficulty,"variant":variant,"outcome":outcome,"can_continue":valid,"injured":s.campaign.get("last_result",{}).get("injured",[]),"withdrawn":s.product.withdrawn,"actions":log,"specialties_used":false,"equipment_used":false,"setup":"isolated deployment at authored day; all actions use production reducer; no outcome injection"})
			print("P4_MATRIX_PATH: %s %s %s %s continued=%s" % [mission,difficulty,variant,outcome,valid])
	var file:=FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../outputs/baseline018-matrix-"+difficulty+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(records,"  "));file.close()
	print("P4_MATRIX_RESULTS: paths=%d failures=%d outcomes=%s" % [records.size(),failures,counts])
	quit(1 if failures else 0)
