extends "res://tests/full_playthrough.gd"
## Fresh, guided campaigns through production commands and durable nightly saves.
const Guidance=preload("res://scripts/presentation/guidance.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
const OUTPUT="res://../outputs/p4release-20261119"
var profile: String="main"
var failures: Array=[]
var missions: Array=[]
var nights: Array=[]
var comparisons: Dictionary={}
var checkpoints: Array=[]
var locations: Array=[]
var checks: int=0

func require(value: bool,reason: String) -> bool:
	checks+=1
	if not value:
		failures.append(reason)
		printerr("LEARNING_FAIL ",reason)
	return value

func guided_battle(retreat: bool) -> bool:
	var row: Dictionary={"mission":s.battle.mission_id,"day":s.campaign.day,"party":s.battle.heroes.keys(),"lessons":[],"commands":{}}
	missions.append(row)
	var location: String=content.boards[s.battle.mission_id].location
	if profile=="sides" and not locations.has(location):
		var board_path: String=ProjectSettings.globalize_path("res://../tmp/quality-review/p4release-boards/"+location+".json")
		if not require(Store.new().save_slot(board_path,s,content).ok,"save playable location "+location):return false
		locations.append(location)
	var actor: String=s.battle.heroes.keys()[0]
	var switches: int=0
	for turn: int in range(320):
		if s.campaign.phase!="battle":break
		if retreat:
			if not require(attempt("emergency_retreat",actor,{"confirmed":true}),"voluntary emergency retreat"):return false
			break
		if s.battle.mission_id=="M01" and not s.tutorial.first_shift.forecast and s.tutorial.first_shift.actions.has("move"):
			if not require(attempt("tutorial_ack",actor,{"lesson":"forecast"}),"read forecast after moving"):return false
		if profile=="sides":
			for member: String in s.battle.heroes:
				preload("res://tests/release_tactical_value.gd").inspect(s,content,member,comparisons)
		var lesson: Dictionary=Rules.FieldLearning.offer(s,content,actor)
		if not lesson.is_empty():
			var read: Dictionary={"actor":actor,"round":s.battle.round,"topic":lesson.topic}
			if not require(attempt("field_lesson",actor,{"topic":lesson.topic}),"read current field lesson "+lesson.topic):return false
			row.lessons.append(read)
		var hint: Dictionary=Guidance.next_step(s,content,actor)
		if hint.has("actor"):
			actor=hint.actor
			switches+=1
			if not require(switches<=s.battle.heroes.size(),"repeated crew switch "+str(hint)):return false
			continue
		switches=0
		if not require(not hint.get("action","").is_empty(),"%s round %s %s empty hint %s"%[row.mission,s.battle.round,actor,hint]):return false
		if not require(attempt(hint.action,actor,hint.get("payload",{})),"%s round %s %s rejected %s"%[row.mission,s.battle.round,actor,hint]):return false
		row.commands[hint.action]=row.commands.get(hint.action,0)+1
	row.round=s.battle.round
	if not require(s.campaign.phase=="settlement","guided mission settled "+row.mission):return false
	if row.mission=="M02":
		for lesson: Dictionary in row.lessons:
			if not require(lesson.topic in ["interact","move","stabilize","pickup","extract","leave_site"],"clinic teaches basic rescue or circuit only"):return false
		if profile!="recovery" and not require(row.lessons.size()==1 and row.lessons[0].topic=="interact","M02 teaches the clinic circuit only"):return false
	row.outcome=s.campaign.last_result.outcome
	row.inventory=s.inventory.duplicate()
	print("LEARNING_MISSION ",profile," ",row.mission," ",row.outcome)
	return true

func prepare_night(day: int) -> bool:
	if not require(attempt("enter_camp","lin"),"enter camp"):return false
	var topic: String=Rules.CampLearning.offer(s,content)
	var row: Dictionary={"day":day,"topic":topic,"urgent":Rules.CampLearning.urgent(s,content),"available":Rules.CampLearning.available(s,content),"recruited":s.journey.recruited.keys(),"projects":[],"inventory":s.inventory.duplicate()}
	nights.append(row)
	if day==6 and not require(not topic.is_empty(),"day-six load retains contextual offer"):return false
	if profile=="sides" and day==6 and not require(topic=="mentors","real mentor opportunity explained before spending either project"):return false
	if day in [2,3,4] and not require(topic==Rules.CampLearning.FOUNDATION[day-2],"foundation in order"):return false
	if day==23 and not require(topic=="route","route lesson on last camp"):return false
	if not topic.is_empty():
		if not require(attempt("camp_lesson","lin",{"topic":topic}),"read current camp lesson "+topic):return false
		if not require(Rules.CampLearning.offer(s,content).is_empty(),"no second unsolicited lesson on "+str(day)):return false
	if profile=="sides" and day==23 and not require(Rules.CampLearning.urgent(s,content)=="route","unselected route is still actionable before final review"):return false
	if day==3:
		if not require(attempt("equip_tool","su",{"item":"crowbar","slot":"tool"}),"equip owned tool"):return false
	if profile=="recovery":
		var wounded: Array=[]
		for id: String in s.journey.recruited:
			if s.actors[id].ready_day>day+1 and wounded.size()<2:wounded.append(id)
		if not wounded.is_empty() and attempt("treat",wounded[0],{"participants":wounded}):row.projects.append("treat:"+str(wounded))
		if day<8 and s.inventory.supplies>0 and attempt("craft_medicine","lin"):row.projects.append("craft_medicine")
		if day==3 and not require(attempt("equip_tool","lin",{"item":"medkit","slot":"support"}),"prepare field medicine"):return false
		if topic=="supplies" and attempt("buy_supplies","lin"):row.projects.append("buy_supplies")
		if topic=="operations":
			for id: String in s.operations.facilities:
				if attempt("repair_field_facility","lin",{"facility":id}):row.projects.append("repair:"+id)
	if profile=="sides":
		# Spend real stock early, then restore teamwork using ordinary rest and assistance.
		if day==1 and not require(attempt("train","lin"),"first training"):return false
		if day==2 and not require(attempt("story_open","lin",{"node":"P_lin_1"}) and attempt("story_choice","lin",{"node":"P_lin_1","choice":"share"}),"first story choice"):return false
		if day==4 and not require(attempt("agreement","lin",{"target":"chen","choice":"cooperate"}),"recruit agrees to cooperate"):return false
		for id: String in s.operations.facilities:
			if attempt("field_assistance","lin",{"facility":id,"participants":Rules.Crew.ready_ids(s).slice(0,2)}):row.projects.append("field_assistance")
		for learner: String in s.journey.recruited:
			if attempt("mentor","lin",{"student":learner,"consent":true}):row.projects.append("mentor:"+learner)
		var tired: Array=[]
		for id: String in s.journey.recruited:
			if s.actors[id].fatigue>=24 and not s.campaign.used.has(id) and tired.size()<2:tired.append(id)
		if not tired.is_empty() and attempt("rest",tired[0],{"participants":tired}):row.projects.append("rest:"+str(tired))
		for evidence_id: String in content.domains.world.evidence:
			if not s.full_campaign.evidence.has(evidence_id) and attempt("review_record","lin",{"evidence":evidence_id}):row.projects.append("review:"+evidence_id)
		if topic=="publish" and attempt("publish_record","lin",{"privacy":"redacted"}):row.projects.append("publish:redacted")
	if day==23:
		var route: String=Rules.Full.routes(s)[0] if profile=="sides" else "evacuation"
		if not require(attempt("select_route","lin",{"route":route}),"choose legal route"):return false
	var store=Store.new()
	var slot: String="user://tests/p4release-learning-"+profile+"/save.json"
	if not require(store.save_slot(slot,s,content).ok,"durable night "+str(day)):return false
	var loaded: Dictionary=store.load_slot(slot,content)
	if not require(loaded.ok and Store.canonical(s)==Store.canonical(loaded.state),"nightly save/load preserves campaign"):return false
	s=loaded.state
	if day in [6,12,18,23] and profile=="sides":
		var path: String=OUTPUT+"/camp-day%02d.json"%day
		var file:=FileAccess.open(path,FileAccess.WRITE)
		file.store_string(Store.canonical(Store.envelope(s,content)));file.close()
		checkpoints.append({"day":day,"file":path.get_file(),"sha256":FileAccess.get_sha256(path)})
	if not require(attempt("finish_evening","lin"),"leave camp"):return false
	if day>=4 and not require(Rules.CampLearning.completed(s),"foundation completion retained"):return false
	return true

func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT))
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--profile="):profile=arg.trim_prefix("--profile=")
	if profile not in ["main","sides","recovery"]:quit(2);return
	content=Catalog.load_catalog()
	s=Rules.begin_campaign(content,"release-learning-"+profile)
	for day: int in range(1,25):
		var ready: Array=Rules.Crew.ready_ids(s)
		if profile=="sides":
			ready.sort_custom(func(a: String,b: String) -> bool:return s.actors[a].fatigue<s.actors[b].fatigue)
		var party: Array=ready.slice(0,3) if profile=="sides" else s.journey.draft.roster
		if not require(attempt("depart","lin",{"roster":party,"medicine":mini(1,s.full_campaign.medicine_stock) if profile=="recovery" else 0}),"M%02d departure"%day):break
		if not guided_battle((profile=="sides" and day==10) or (profile=="recovery" and day in [1,4,5])):break
		if day==24:break
		if profile=="sides" and day==10:
			require(s.campaign.last_result.outcome=="failed","failed M10 still grants He Ming")
		if profile=="sides":
			var sides: Array=Rules.Chapter.side_available(s,content)
			if not sides.is_empty() and Rules.Chapter.eligible(s).size()>=3:
				if not require(attempt("start_side","lin",{"mission":sides[0]}),"optional departure "+str(sides)):break
				if not guided_battle(false):break
		if not prepare_night(day):break
	require(s.chapter_one.finished and s.campaign.day==24,"continuous 24-day ending")
	require(s.journey.recruited.size()==8,"eight real recruits")
	if s.chapter_one.finished:
		var slot: String="user://tests/p4release-learning-"+profile+"/ending.json"
		var saved: Dictionary=Store.new().save_slot(slot,s,content)
		var dest: String=ProjectSettings.globalize_path(OUTPUT+"/ending-"+profile+".json")
		require(saved.ok and DirAccess.copy_absolute(ProjectSettings.globalize_path(slot),dest)==OK,"durable ending "+profile)
		checkpoints.append({"day":24,"file":dest.get_file(),"sha256":FileAccess.get_sha256(dest)})
	if profile=="sides":
		require(locations.size()==12,"twelve live locations")
		require(s.chapter_one.attempted.size()==12,"all twelve optional missions")
		require(comparisons.size()==8,"an earned tactical comparison for every recruit")
	if not failures.is_empty() and s.campaign.phase=="battle":
		print("STATE ",s.battle.heroes," OBJECTS ",s.battle.objects," LAST ",log.slice(-4))
	if profile=="recovery":
		require(nights.any(func(n: Dictionary):return n.inventory.supplies<4),"recovery route reaches low stocks through treatment and preparation")
	var file:=FileAccess.open(OUTPUT+"/learning-"+profile+".json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"profile":profile,"checks":checks,"failures":failures,"missions":missions,"nights":nights,"value_comparisons":comparisons,"checkpoints":checkpoints,"ending":s.full_campaign.ending,"actions":log.size(),"scope":"Fresh production commands driven by displayed guidance rules; no injected stats or rewards. Nightly durable save/load. No human, Windows, elapsed reading time or difficulty acceptance."},"\t"));file.close()
	print("RELEASE_LEARNING_RESULTS profile=%s missions=%d nights=%d failures=%s"%[profile,missions.size(),nights.size(),failures]);quit(int(not failures.is_empty()))
