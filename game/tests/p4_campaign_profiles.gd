extends "res://tests/full_playthrough.gd"
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
var failures: int=0
func require(value: bool,context: String) -> void:
	if not value:failures+=1;printerr("P4_PROFILE_FAIL: "+context)
func run() -> void:
	content=Catalog.load_catalog()
	var mode: String="no_training"
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--profile="):mode=argument.trim_prefix("--profile=")
	if mode not in ["no_training","few_sides","fixed_favorites","injury_rotation"]:quit(2);return
	s=Rules.fresh(content,"p4-profile-"+mode);log=[]
	var days: Array=[]
	var store=Store.new()
	var slot: String="user://tests/p4-profile-%s-%d/save.json" % [mode,Time.get_ticks_usec()]
	for day: int in range(1,25):
		require(s.campaign.day==day,"ordered day")
		if mode=="injury_rotation" and day in [1,8,15]:
			require(attempt("emergency_retreat",s.battle.heroes.keys()[0],{"confirmed":true}),"actual emergency causes recovery/rotation")
		else:solve(content.boards[s.battle.mission_id])
		require(s.campaign.phase=="settlement","mission ends "+str(day))
		days.append({"day":day,"outcome":s.campaign.last_result.outcome,"roster":s.battle.heroes.keys(),"injured":s.campaign.last_result.injured,"inventory":s.inventory.duplicate(),"actors":s.actors.duplicate(true)})
		if day==24:break
		if mode=="few_sides" and day==2:
			var side: String="S01"
			require(attempt("start_side","lin",{"mission":side}),"one optional side only")
			solve(content.boards[side]);require(s.campaign.phase=="settlement","side completed")
		require(attempt("enter_camp","lin"),"camp")
		if day==23:require(attempt("select_route","lin",{"route":"evacuation"}),"route")
		require(store.save_slot(slot,s,content).ok,"daily actual save")
		var loaded: Dictionary=store.load_slot(slot,content)
		require(loaded.ok,"daily actual load")
		if not loaded.ok:break
		require(Store.canonical(s)==Store.canonical(loaded.state),"exact resource/fatigue/XP roundtrip")
		s=loaded.state
		var payload: Dictionary={}
		if mode=="fixed_favorites":
			var ready: bool=true
			for id: String in ["lin","xu","su"]:
				ready=ready and s.actors[id].ready_day<=day+1 and s.actors[id].fatigue+6<=100
			if ready:payload.roster=["lin","xu","su"]
		require(attempt("next_mission","lin",payload),"no economic softlock on departure")
	require(s.chapter_one.finished and days.size()==24,"24-day completion")
	require(s.full_campaign.ending=="evacuation","failure has real ending")
	require(store.save_slot(slot,s,content).ok,"final persisted")
	for actor: Dictionary in s.actors.values():require(actor.training_completed==0,"zero paid training")
	var result: Dictionary={"profile":mode,"finished":s.chapter_one.finished,"days":days,"ending":s.full_campaign.ending,"actions":log,"source":"continuous production reducer with real daily save/load; no inventory/XP/fatigue resets"}
	var file:=FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-profile-"+mode+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"  "));file.close()
	print("P4_PROFILE_RESULTS: profile=%s days=%d failures=%d" % [mode,days.size(),failures])
	quit(1 if failures else 0)
