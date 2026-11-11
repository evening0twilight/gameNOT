extends "res://tests/full_playthrough.gd"
var failures: int=0
func all_goals(board: Dictionary) -> bool:
	return super.all_goals(board) and (s.battle.get("service",{}).is_empty() or s.battle.service.done)
func goals(board: Dictionary) -> Array:
	var result: Array=[]
	for group: Array in Rules.Full.groups(s,board):
		var id: String=group[0]
		for required: String in s.battle.objects[id].prerequisites:
			if not result.has(required):result.append(required)
		if not result.has(id):result.append(id)
	return result
func task(actor: String,board: Dictionary) -> bool:
	for id: String in goals(board):
		if not secured(s.battle.objects[id]):return tick(actor,id,board)
	if s.battle.service.done:return tick(actor,goals(board)[0],board)
	var source: String=s.battle.service.definition.source_enemy
	return attempt("attack",actor,{"target":source})
func run() -> void:
	content=Catalog.load_catalog()
	for mission: String in ["M05","M10","M21","S11"]:
		var board: Dictionary=content.boards[mission]
		var found: bool=false
		for order: Array in [["lin","xu","su"],["xu","su","lin"],["su","lin","xu"]]:
			if found:break
			s=Rules.fresh(content,"field-legal-"+mission);log=[];s.campaign.day=board.day;s.chapter_one.roster=order
			# Isolated mission fixture, initial trio at L2; no state changes after deploy.
			for a: Dictionary in s.actors.values():a.fatigue=0;a.xp=12
			Rules.deploy(s,content,mission)
			for turn: int in range(s.battle.limit):
				if s.campaign.phase!="battle":break
				for cycle: int in range(3):
					for actor: String in order:
						if s.campaign.phase!="battle":break
						var f: Dictionary=s.battle.service
						var posts: Array=Rules.Field.posts(s.battle)
						var position: int=order.find(actor)
						var ready: bool=true
						for id: String in f.definition.get("prerequisites",[]):ready=ready and s.battle.objects[id].completed
						var watched: bool=false
						for watch: Dictionary in f.watches.values():watched=watched or watch.actor==actor
						if watched:continue
						if not f.done and not f.failed and ready and position<posts.size():
							if attempt("service_watch",actor,{"post":position}):continue
							if not Rules.same(s.battle.heroes[actor].cell,posts[position]) and navigate_to(actor,[posts[position]]):continue
						task(actor,board)
				if s.campaign.phase=="battle":
					if mission=="M21" and not s.battle.service.done:attempt("protocol",order[0],{"protocol":"mutual_cover","partner":order[1],"consent":true})
					attempt("end_round",order[0])
			found=s.campaign.get("last_result",{}).get("outcome")=="success" and s.battle.service.done
			if found:records.append({"mission":mission,"party":order,"setup":"isolated initial trio L2, only reducer actions after deployment; no completions or teleport injection","actions":log,"result":s.campaign.last_result,"round":s.battle.round})
		if not found:failures+=1;printerr("FIELD_PATH_FAIL "+mission+" "+str(s.battle.service.history))
		else:print("FIELD_PATH_OK "+mission)
	var file:=FileAccess.open("res://../outputs/baseline018-field-paths.json",FileAccess.WRITE);file.store_string(JSON.stringify(records,"\t"));file.close()
	print("BASELINE018_FIELD_PATHS: paths=%d failures=%d"%[records.size(),failures]);quit(1 if failures else 0)
