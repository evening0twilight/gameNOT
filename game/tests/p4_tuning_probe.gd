extends "res://tests/full_playthrough.gd"
func run() -> void:
	content=Catalog.load_catalog();use_specialties=false
	var suffix: String="before"
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--stage="):suffix=arg.trim_prefix("--stage=")
	for difficulty: String in ["relaxed","standard","hard"]:
		for delay: int in [0,2,4,6]:
			for mission: String in ["M01","M02","M04","M06","M09","M15","M19","M23"]:
				s=Rules.fresh(content,"tuning",{"difficulty":difficulty});log=[]
				var board: Dictionary=content.boards[mission]
				s.campaign.day=int(board.day);Rules.deploy(s,content,mission)
				for turn: int in range(delay):attempt("end_round",s.battle.heroes.keys()[0])
				solve(board)
				var lost: Array=[]
				for o: Dictionary in s.battle.objects.values():
					if o.kind=="rescue" and o.lost:lost.append(o.id)
				records.append({"mission":mission,"difficulty":difficulty,"idle_rounds":delay,"outcome":s.campaign.get("last_result",{}).get("outcome","unfinished"),"final_round":s.battle.round,"limit":s.battle.limit,"lost_residents":lost,"injured":s.campaign.get("last_result",{}).get("injured",[])})
	var file:=FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-probe-"+suffix+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"scope":"Deterministic isolated recovery after deliberately idle rounds; not a human win-rate estimate","records":records},"  "));file.close()
	print("TUNING_PROBE: cases=",records.size());quit()
