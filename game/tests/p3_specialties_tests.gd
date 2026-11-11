extends "res://tests/p3_rules_tests.gd"
func run() -> void:
	c=Catalog.load_catalog()
	fixture("M17",["ye","he","mo"])
	for id: String in ["ye","he","mo"]:s.actors[id].xp=72
	s.battle.heroes.ye.cell=[6,2]
	check(act("specialty",{"ability":"ye_1","target":"M17_enemy1"},"ye").ok,"Ye isolates hazardous output")
	check(s.battle.enemies.M17_enemy1.isolated and not s.battle.enemies.M17_enemy1.disabled,"isolation preserves machine power and body")
	check(Rules.Hazards.footprint(s.battle,s.battle.enemies.M17_enemy1,Rules).is_empty(),"isolated machine has no danger output")
	check(not act("specialty",{"ability":"ye_1","target":"M17_enemy2"},"ye").ok,"two AP specialty spends exact budget")
	act("end_round")
	s.battle.heroes.ye.cell=[1,7]
	check(act("specialty",{"ability":"ye_3","cell":[4,7]},"ye").ok,"L5 three-cell insulation")
	check(s.battle.insulation.size()==3,"insulation exact cells")
	s.battle.heroes.he.cell=[4,6]
	check(act("specialty",{"ability":"he_1","cell":[4,7]},"he").ok,"He places shield")
	check(s.battle.barriers["[4, 7]"].hp==5 and s.battle.barriers["[4, 7]"].expires==0,"L5 persistent shield HP")
	check(not act("move",{"cell":[4,7]},"he").ok,"cannot land on barrier")
	s.battle.heroes.mo.cell=[6,4]
	check(act("specialty",{"ability":"mo_1","target":"M17_enemy2_cut1"},"mo").ok,"remote switch work")
	check(not s.battle.enemies.M17_enemy2.disabled,"remote switch respects two-switch sentinel")
	check(not act("specialty",{"ability":"mo_1","target":"repair2"},"mo").ok,"remote work cannot operate primary goal")
	fixture("S09",["mo","he","jiang"])
	s.actors.mo.xp=72;s.actors.he.xp=72;s.actors.jiang.xp=72
	s.battle.heroes.mo.cell=[3,7]
	var intent: Dictionary=s.battle.intents.duplicate(true)
	# Replace only machine type in this unit fixture, using an authored scout definition.
	var id: String=s.battle.enemies.keys()[0];s.battle.enemies[id].type="scout"
	check(act("specialty",{"ability":"mo_3","target":id,"cell":[5,7]},"mo").ok,"beacon accepts empty dry target")
	check(s.battle.intents==intent,"beacon does not retarget locked current intent")
	act("end_round");check(s.battle.beacons[id].round==s.battle.round,"beacon used next round")
	fixture("M23",["jiang","lin","xu"])
	s.actors.jiang.xp=72
	s.battle.heroes.jiang.cell=[6,0];s.battle.heroes.lin.cell=[4,0]
	check(act("pickup",{"target":"rebuild"},"jiang").ok,"actual cargo pickup")
	check(act("specialty",{"ability":"jiang_1","target":"lin","consent":true},"jiang").ok,"level3+ real handoff")
	check(s.battle.heroes.lin.carrying=="rebuild" and s.battle.objects.rebuild.carrier=="lin" and not s.battle.objects.rebuild.delivered,"handoff is not delivery")
	act("end_round")
	s.battle.heroes.xu.cell=[5,0];s.battle.heroes.xu.hp=6;s.battle.medicine=1
	check(act("specialty",{"ability":"jiang_3","target":"xu"},"jiang").ok,"actual packed medicine heals")
	check(s.battle.heroes.xu.hp==9 and s.battle.medicine==0,"medicine and healing conserved")
	check(not act("specialty",{"ability":"jiang_3","target":"xu"},"jiang").ok,"no free second dose")
	camp(16)
	var supplies: int=s.inventory.supplies
	check(act("craft_medicine").ok,"craft stock from one supply")
	check(s.inventory.supplies==supplies-1 and s.full_campaign.medicine_stock==1,"craft conservation")
	check(act("next_mission",{"medicine":1}).ok,"medicine packing")
	check(s.full_campaign.medicine_stock==0 and s.battle.medicine==1,"packing is transfer")
	act("emergency_retreat",{"confirmed":true})
	check(s.full_campaign.medicine_stock==1 and s.battle.medicine==0,"unused dose returns on retreat")
	check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,c))),c).ok,"specialty fields saved")
	print("P3_SPECIALTIES_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
