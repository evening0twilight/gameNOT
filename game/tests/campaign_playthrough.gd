extends "res://tests/full_playthrough.gd"
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
var failures: int=0
func require(value: bool,message: String) -> bool:
	if not value:failures+=1;printerr("CAMPAIGN_PATH_FAIL: "+message)
	return value
func run() -> void:
	content=Catalog.load_catalog()
	var campaigns: Array=[]
	var modes: Array=["shared_control","distributed_rebuild","evacuation","failure"]
	var suffix: String=""
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--campaign-mode="):
			var requested: String=argument.trim_prefix("--campaign-mode=")
			if not modes.has(requested):quit(2);return
			modes=[requested];suffix="-"+requested
	for mode: String in modes:
		s=Rules.fresh(content,"continuous-"+mode);log=[]
		if mode=="failure":s.inventory={"credits":0,"supplies":0,"parts":0}
		var days: Array=[]
		var store=Store.new()
		var slot: String="user://tests/p3-continuous-%s-%d/autosave.json" % [mode,Time.get_ticks_usec()]
		for day: int in range(1,25):
			if not require(s.campaign.day==day and s.battle.mission_id=="M%02d"%day,"ordered day "+str(day)):break
			if mode=="failure":require(attempt("emergency_retreat","lin",{"confirmed":true}),"failure retreat")
			else:solve(content.boards[s.battle.mission_id])
			var outcome: String=s.campaign.get("last_result",{}).get("outcome","unfinished")
			require(outcome==("failed" if mode=="failure" else "success"),mode+" day "+str(day)+" "+outcome)
			days.append({"day":day,"outcome":outcome,"mission":s.battle.mission_id,"roster":s.battle.heroes.keys(),"inventory":s.inventory.duplicate(),"districts":s.campaign.districts.duplicate(),"actors":s.actors.duplicate(true)})
			if day==24:break
			require(attempt("community_report","lin",{"choice":"archive"}),"community record")
			if not require(attempt("enter_camp","lin"),"night entry"):break
			if mode!="failure":
				if day==20:require(attempt("review_record","lin",{"evidence":"E_ORDER"}),"order review")
				if day==22:require(attempt("review_record","lin",{"evidence":"E_WARNING"}),"warning review")
			if day==23:require(attempt("select_route","lin",{"route":"evacuation" if mode=="failure" else mode}),"route eligibility "+mode)
			if not require(store.save_slot(slot,s,content).ok,"save day "+str(day)):break
			var loaded: Dictionary=store.load_slot(slot,content)
			if not require(loaded.ok,"load day "+str(day)):break
			require(Store.canonical(s)==Store.canonical(loaded.state),"exact saved state")
			s=loaded.state
			if not require(attempt("next_mission","lin"),"next day"):break
		require(s.chapter_one.finished and s.campaign.day==24,"24-day completion "+mode)
		require(s.full_campaign.ending==("evacuation" if mode=="failure" else mode),"world ending "+mode)
		require(not attempt("enter_camp","lin"),"no post-final camp")
		require(store.save_slot(slot,s,content).ok,"final save")
		campaigns.append({"mode":mode,"days":days,"ending":s.full_campaign.ending,"finished":s.chapter_one.finished,"actions":log,"evidence":s.full_campaign.evidence,"final_inventory":s.inventory})
		print("P3_CAMPAIGN: mode=%s days=%d ending=%s" % [mode,days.size(),s.full_campaign.ending])
	var file:=FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-campaign-paths"+suffix+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(campaigns,"  "));file.close()
	print("P3_CAMPAIGN_RESULTS: campaigns=%d failures=%d" % [campaigns.size(),failures])
	quit(1 if failures else 0)
