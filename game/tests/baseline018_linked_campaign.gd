extends "res://tests/full_playthrough.gd"
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
var failures: Array=[]
var milestones: Array=[]
func require(value: bool,reason: String) -> void:
	if not value:failures.append(reason);printerr("LINKED_FAIL: "+reason)
func event(name: String) -> void:
	if int(s.campaign.day) in [4,6,16,18,19,24]:
		var snapshot:=FileAccess.open("res://../outputs/baseline018-linked-day%02d.json"%s.campaign.day,FileAccess.WRITE)
		snapshot.store_string(Store.canonical(Store.envelope(s,content)));snapshot.close()
	milestones.append({"name":name,"day":s.campaign.day,"revision":s.revision,"actors":s.actors.duplicate(true),"inventory":s.inventory.duplicate(),"recruited":s.journey.recruited.duplicate(true),"plans":s.full_campaign.contracts.duplicate(true),"su_jiang":s.social["su>jiang"].duplicate(true),"lin_chen":s.social["lin>chen"].duplicate(true)})
func tick(actor: String,goal: String,board: Dictionary) -> bool:
	# Use real paid cooperation when both workers happen to reach the same work site.
	var o: Dictionary=s.battle.objects.get(goal,{})
	if actor=="lin" and o.get("kind","")=="rescue" and not o.get("delivered",false) and s.full_campaign.contracts.has("lin") and not s.full_campaign.contracts.lin.fulfilled and s.battle.heroes.has("xu"):
		if not o.stable and attempt("stabilize","lin",{"target":goal}):return true
		if o.stable and o.carrier.is_empty():
			if attempt("pickup","xu",{"target":goal}):return true
			if navigate_to("xu",near(o.cell)):return true
			return false
	if not o.is_empty() and o.kind=="work" and not o.completed:
		for partner: String in s.battle.heroes:
			if partner!=actor and attempt("protocol",actor,{"protocol":"protected_work","partner":partner,"target":goal,"consent":true}):return true
	return super.tick(actor,goal,board)
func run() -> void:
	content=Catalog.load_catalog();s=Rules.begin_campaign(content,"baseline018-linked");log=[]
	var store=Store.new();var path: String="user://tests/linked-%d/save.json"%Time.get_ticks_usec()
	require(attempt("depart","lin"),"initial departure")
	for day: int in range(1,25):
		solve(content.boards[s.battle.mission_id])
		require(s.campaign.phase=="settlement","day %d settles"%day)
		if s.campaign.phase!="settlement":break
		print("LINKED_DAY: %d %s %s"%[day,s.campaign.last_result.outcome,str(s.battle.heroes.keys())])
		if day in [4,7,10,13,16]:event("actual recruitment settlement")
		if day==24:break
		require(attempt("enter_camp","lin"),"camp %d"%day)
		if day==1:require(attempt("train","lin"),"initial course advances Lin to L2");event("training consumed actual project, supplies and stage")
		if day==2:
			require(attempt("story_open","lin",{"node":"P_lin_1"}),"first personal scene opens")
			require(attempt("story_choice","lin",{"node":"P_lin_1","choice":"share"}),"consented disclosure recorded")
		if day==4:require(attempt("agreement","lin",{"target":"chen","choice":"cooperate"}),"new recruit cooperation agreement")
		if day==6:
			var offer: Dictionary=Rules.Chapter.mentor_offer(s,"lin","chen")
			print("LINKED_MENTOR_OFFER: "+str(offer))
			require(attempt("mentor","lin",{"student":"chen","consent":true}),"two real missions unlock meaningful mentorship")
			event("mentorship after recruitment and two contributed missions")
		if day==17:
			require(attempt("story_open","su",{"node":"R04"}),"actual R04 conversation")
			require(attempt("story_choice","su",{"node":"R04","choice":"agreement"}),"R04 chosen rotation agreement")
		if day==18:
			require(Rules.Field.dispatch_ready(s,["su","lin","xu"],"jiang"),"R04 and two actual cooperative missions qualify dispatch")
			event("relationship unlocks dispatch")
		# Persistent career plan: choose a real authored plan and meet it through later operations.
		if day==9:
			require(attempt("story_open","lin",{"node":"P_lin_2"}),"plan scene opens")
			require(attempt("story_choice","lin",{"node":"P_lin_2","choice":"rotation"}),"real shared rescue plan accepted")
		if day==16:
			require(s.full_campaign.contracts.lin.fulfilled,"later shared rescue fulfills plan")
			require(attempt("story_open","lin",{"node":"P_lin_3"}),"career scene opens")
			require(attempt("story_choice","lin",{"node":"P_lin_3","choice":"new_life"}),"independent career choice retains fulfilled plan")
			event("real plan fulfilled and future career selected")
		if day==23:require(attempt("select_route","lin",{"route":"evacuation"}),"final route")
		# Recovery uses remaining real projects; no fatigue/XP/resource injection.
		var tired: Array=[]
		for id: String in s.journey.recruited:
			if not s.campaign.used.has(id) and s.actors[id].fatigue>=30 and tired.size()<2:tired.append(id)
		if not tired.is_empty():attempt("rest",tired[0],{"participants":tired})
		require(store.save_slot(path,s,content).ok,"camp durable %d"%day)
		var loaded: Dictionary=store.load_slot(path,content)
		require(loaded.ok,"camp reload %d"%day)
		if not loaded.ok:break
		require(Store.canonical(s)==Store.canonical(loaded.state),"exact camp roundtrip %d"%day);s=loaded.state
		require(attempt("finish_evening","lin"),"finish night %d"%day)
		var payload: Dictionary={}
		if day in [4,5]:payload.roster=["lin","chen","xu"]
		if day in [16,17]:payload.roster=["su","jiang","lin"]
		if day==18:payload={"roster":["su","lin","xu"],"support":"jiang","dispatch":true}
		var supplies: int=s.inventory.supplies
		require(attempt("depart","lin",payload),"next departure %d"%(day+1))
		if day==18:
			require(s.operations.dispatch and s.battle.exits==[[7,7]] and s.inventory.supplies==supplies-2,"paid dispatch replaces regular exit at deployment")
			event("dispatch changes actual tactical exit and costs two supplies")
	require(s.chapter_one.finished and s.journey.recruited.size()==8,"all eight acquired through actual settlement; full ending")
	require(s.full_campaign.contracts.lin.fulfilled and s.chapter_one.scenes.P_lin_3.choice=="new_life","ending keeps fulfilled plan independently of career")
	require(not s.full_campaign.mentored.is_empty(),"mentorship retained at ending")
	event("ending retains recruitment training relationships and cooperation")
	var file:=FileAccess.open("res://../outputs/baseline018-linked-campaign.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"failures":failures,"milestones":milestones,"actions":log,"ending":s.full_campaign.ending,"final_state":s,"evidence_scope":"continuous real reducer actions and daily save/load; no state injection or synthetic contributions"},"\t"));file.close()
	print("BASELINE018_LINKED: failures=%d"%failures.size());quit(0 if failures.is_empty() else 1)
