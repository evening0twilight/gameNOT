extends "res://tests/full_playthrough.gd"
const Guide=preload("res://scripts/presentation/guidance.gd")
func run() -> void:
	content=Catalog.load_catalog();use_specialties=false
	var failures: int=0
	for variant: String in ["A","B"]:
		s=Rules.fresh(content,"hard-safe-route",{"difficulty":"hard","variant":variant});log=[]
		var board: Dictionary=content.boards.M05
		s.campaign.day=int(board.day);Rules.deploy(s,content,"M05")
		for turn: int in range(int(s.battle.limit)):
			if s.campaign.phase!="battle":break
			for cycle: int in range(3):
				for actor: String in s.battle.heroes.keys():
					if s.campaign.phase!="battle":break
					var control: Dictionary=s.battle.objects.M05_enemy1_cut
					if not control.completed and Rules.distance(s.battle.heroes[actor].cell,control.cell)<=1:
						if attempt("interact",actor,{"target":control.id}):continue
					var goal: String={"lin":"isolate","xu":"pump","su":"M05_enemy1_cut"}[actor]
					if s.battle.objects[goal].completed:goal="pump"
					tick(actor,goal,board)
			if s.campaign.phase=="battle":attempt("end_round",s.battle.heroes.keys()[0])
		var outcome: String=s.campaign.get("last_result",{}).get("outcome","unfinished")
		if outcome!="success":failures+=1
		records.append({"mission":"M05","difficulty":"hard","variant":variant,"outcome":outcome,"actions":log,"last_result":s.campaign.get("last_result",{}),"specialties_used":false,"equipment_used":false,"method":"prioritize machine shutdown before energizing the sustained pump; production reducer actions only"})
		print("HARD_ROUTE: ",variant," ",outcome)
	var file:=FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../outputs/p4-tuning-hard-route.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(records,"  "));file.close()
	print("P4_HARD_ROUTE_RESULTS: paths=2 failures=",failures)
	quit(1 if failures else 0)
