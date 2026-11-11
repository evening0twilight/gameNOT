extends SceneTree
## Deterministic legal-action explorer. Never marks objectives complete or disables enemies directly.
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
const Board=preload("res://scripts/presentation/tactical_board.gd")
var content: Dictionary
var s: Dictionary
var sequence: int=0
var records: Array=[]
var log: Array=[]
func _initialize() -> void:call_deferred("run")
func attempt(kind: String,actor: String,payload: Dictionary={}) -> bool:
	sequence+=1
	var command: Dictionary={"kind":kind,"actor_id":actor,"payload":payload,"expected_revision":s.revision,"command_id":"path-%d"%sequence,"root_decision_id":"path-%d"%sequence}
	var result:=Rules.reduce(s,command,content)
	if not result.ok:return false
	log.append({"round":s.battle.round,"kind":kind,"actor":actor,"payload":payload})
	s=result.next_state
	return true
func navigate_to(actor: String,targets: Array) -> bool:
	var hero: Dictionary=s.battle.heroes[actor]
	var best: Array=[];var best_cost: int=999
	for target: Array in targets:
		if Rules.blocked(s.battle,target) or Rules.occupied(s.battle,target):continue
		var cost: int=Rules.move_cost(s.battle,hero.cell,target,40)
		if cost>=0 and cost<best_cost:best=Board.route(s.battle,hero.cell,target);best_cost=cost
	for index: int in range(best.size()-1,0,-1):
		if attempt("move",actor,{"cell":best[index]}):return true
	return false
func near(cell: Array) -> Array:
	return [cell,[int(cell[0])-1,int(cell[1])],[int(cell[0])+1,int(cell[1])],[int(cell[0]),int(cell[1])-1],[int(cell[0]),int(cell[1])+1]]
func secured(o: Dictionary) -> bool:return o.completed and (not o.sustain_until_exit or o.hp>0)
func all_goals(board: Dictionary) -> bool:
	for group: Array in board.mandatory_groups:
		var done: bool=false
		for id: String in group:done=done or secured(s.battle.objects[id])
		if not done:return false
	return true
func tick(actor: String,goal: String,board: Dictionary) -> bool:
	var hero: Dictionary=s.battle.heroes[actor]
	if hero.ap<1 or hero.left or hero.downed:return false
	if not hero.carrying.is_empty():
		if attempt("extract",actor):return true
		return navigate_to(actor,board.exits)
	if all_goals(board):
		if attempt("leave_site",actor):return true
		return navigate_to(actor,board.exits)
	var object: Dictionary=s.battle.objects.get(goal,{})
	if not object.is_empty() and not object.lost and not secured(object):
		if object.kind=="rescue" and not object.stable:
			if actor=="lin" and attempt("specialty",actor,{"ability":"lin_1","target":goal}):return true
			if attempt("stabilize",actor,{"target":goal}):return true
		elif object.kind in ["rescue","cargo"]:
			if object.carrier.is_empty() and attempt("pickup",actor,{"target":goal}):return true
		elif attempt("interact",actor,{"target":goal}):return true
		if Rules.distance(hero.cell,object.cell)>1 and navigate_to(actor,near(object.cell)):return true
	for enemy: Dictionary in s.battle.enemies.values():
		if enemy.hp>0 and not enemy.disabled and attempt("attack",actor,{"target":enemy.id}):return true
	return false
func solve(board: Dictionary) -> void:
	var goals: Array=[]
	for group: Array in board.mandatory_groups:
		var id: String=group[0]
		for required: String in s.battle.objects[id].prerequisites:
			if not goals.has(required):goals.append(required)
		if not goals.has(id):goals.append(id)
	var actors: Array=s.battle.heroes.keys()
	var assignments: Dictionary={}
	for i: int in range(3):assignments[actors[i]]=goals[i] if i<goals.size() else board.controls[0].id
	for turn: int in range(int(board.round_limit)):
		if s.campaign.phase!="battle":break
		for cycle: int in range(3):
			for actor: String in actors:
				var goal: String=assignments[actor]
				if secured(s.battle.objects[goal]):
					for candidate: String in goals:
						if not secured(s.battle.objects[candidate]):goal=candidate;break
				tick(actor,goal,board)
		if s.campaign.phase=="battle":attempt("end_round",actors[0])
func run() -> void:
	content=Catalog.load_catalog()
	var failures: int=0
	for mission: String in ["M01","M02","M03","M04","M05","M06","S01","S02","S03"]:
		s=Rules.fresh(content,"path-"+mission);log=[]
		var board: Dictionary=content.boards[mission]
		s.campaign.day=int(board.day)
		for a: Dictionary in s.actors.values():a.fatigue=0
		Rules.deploy(s,content,mission)
		solve(board)
		var outcome: String=s.campaign.get("last_result",{}).get("outcome","unfinished")
		if outcome!="success":failures+=1
		records.append({"mission":mission,"outcome":outcome,"actions":log,"final_round":s.battle.round})
		print("CHAPTER_PATH: %s %s actions=%d" % [mission,outcome,log.size()])
	# A second run keeps campaign fatigue, XP, rewards and story state across all six days.
	s=Rules.fresh(content,"continuous-chapter");log=[]
	var continuous: Array=[]
	for day: int in range(1,7):
		var mission: String="M%02d"%day
		if s.battle.mission_id!=mission:failures+=1;break
		solve(content.boards[mission])
		var result: String=s.campaign.get("last_result",{}).get("outcome","unfinished")
		if result!="success":failures+=1
		continuous.append({"mission":mission,"outcome":result,"revision":s.revision})
		if not attempt("enter_camp","lin"):failures+=1;break
		var store=preload("res://scripts/infrastructure/campaign_store.gd").new()
		var slot: String="user://tests/p2-continuous/autosave.json"
		if not store.save_slot(slot,s,content).ok:failures+=1;break
		var loaded: Dictionary=store.load_slot(slot,content)
		if not loaded.ok:failures+=1;break
		s=loaded.state
		if not attempt("next_mission","lin"):failures+=1;break
	if not s.chapter_one.finished:failures+=1
	records.append({"continuous_main":continuous,"finished":s.chapter_one.finished,"actions":log})
	print("CHAPTER_CONTINUOUS_RESULTS: days=%d finished=%s" % [continuous.size(),s.chapter_one.finished])
	var file:=FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../outputs/p2-path-exploration.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(records,"  "));file.close()
	print("CHAPTER_PATH_RESULTS: missions=9 failures=%d" % failures)
	quit(1 if failures else 0)
