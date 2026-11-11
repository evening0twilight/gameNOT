extends "res://tests/full_playthrough.gd"
var checks: int=0
var failures: int=0
func check(value: bool,message: String) -> void:
	checks+=1
	if not value:failures+=1;printerr("P3_PROOF_FAIL: "+message)
func plan(actor: String,day: int,first: String,choice: String) -> void:
	s=Rules.fresh(content,"proof-"+actor);log=[]
	s.campaign.day=day;s.chapter_one.main_completed=day
	preload("res://tests/baseline018_fixture.gd").joined(s)
	s.campaign.phase="camp"
	check(attempt("story_open",actor,{"node":"P_"+actor+"_1"}),"open first "+actor)
	check(attempt("story_choice",actor,{"node":"P_"+actor+"_1","choice":first}),"first choice "+actor)
	check(attempt("story_open",actor,{"node":"P_"+actor+"_2"}),"open plan "+actor)
	check(attempt("story_choice",actor,{"node":"P_"+actor+"_2","choice":choice}),"plan choice "+actor)
func deploy_fixture(mission: String,roster: Array) -> void:
	# Isolated pre-action deployment fixture; after this point only reducer commands produce proof.
	s.campaign.day=int(content.boards[mission].day);s.chapter_one.roster=roster
	Rules.deploy(s,content,mission)
func run() -> void:
	content=Catalog.load_catalog()
	plan("xu",10,"record","bounded")
	check(attempt("next_mission","lin"),"deploy after Xu plan")
	check(attempt("promise_retreat","xu"),"explicit stop condition")
	check(navigate_to("xu",content.boards.M11.exits),"walk Xu to exit")
	check(attempt("leave_site","xu"),"Xu standing extraction")
	attempt("emergency_retreat","lin",{"confirmed":true})
	check(s.full_campaign.contracts.xu.fulfilled and s.campaign.last_result.outcome=="failed","failed objective can still prove kept promise")
	plan("su",11,"list","rota")
	check(attempt("next_mission","lin",{"roster":["lin","xu","su"],"support":"he"}),"real other support assignment")
	attempt("emergency_retreat","lin",{"confirmed":true});attempt("enter_camp","lin");attempt("next_mission","lin")
	attempt("emergency_retreat","lin",{"confirmed":true})
	check(s.full_campaign.contracts.su.fulfilled,"two actual main duties and actual alternative support")
	plan("chen",12,"copy","fund")
	deploy_fixture("M13",["chen","lin","xu"]);solve(content.boards.M13)
	check(s.full_campaign.contracts.chen.fulfilled,"paid compensation plus actual later engineering contribution")
	plan("ye",14,"retain","audit")
	s.campaign.day=20
	check(attempt("review_record","ye",{"evidence":"E_MAINTENANCE"}),"review known source")
	check(s.full_campaign.contracts.ye.fulfilled,"Ye project and verified maintenance proof")
	plan("he",16,"name","delegate")
	deploy_fixture("M19",["he","lin","xu"]);solve(content.boards.M19)
	check(s.full_campaign.contracts.he.fulfilled,"He rescues while peers contribute and all actually extract")
	plan("mo",18,"classify","redact")
	s.campaign.day=20
	attempt("review_record","mo",{"evidence":"E_ORDER"})
	check(attempt("publish_record","mo",{"privacy":"redacted"}),"actual redacted release")
	check(s.full_campaign.contracts.mo.fulfilled,"Mo new public receipt")
	check(attempt("publish_record","mo",{"privacy":"unredacted"}),"explicit later breach")
	check(s.full_campaign.contracts.mo.fulfilled and s.full_campaign.contracts.mo.breached,"prior fulfillment preserved independently of later breach")
	s.campaign.day=23;s.campaign.talked=[]
	check(attempt("story_open","mo",{"node":"P_mo_3"}),"late Mo closing")
	check(not attempt("story_choice","mo",{"node":"P_mo_3","choice":"integrated"}),"new warm closing cannot erase breach")
	check(attempt("story_choice","mo",{"node":"P_mo_3","choice":"new_life"}),"career remains independent of conflict")
	plan("lin",9,"private","rotation")
	deploy_fixture("M15",["lin","xu","su"])
	# Initial placement is a unit fixture; stabilization and transport remain actual distinct acts.
	s.battle.heroes.lin.cell=s.battle.objects.east.cell.duplicate()
	check(attempt("stabilize","lin",{"target":"east"}),"Lin stabilizes Xu's later rescue")
	for round_index: int in range(12):
		for action_index: int in range(2):tick("xu","east",content.boards.M15)
		if s.battle.objects.east.delivered:break
		if s.campaign.phase!="battle":break
		attempt("end_round","xu")
	if s.campaign.phase=="battle":attempt("emergency_retreat","xu",{"confirmed":true})
	check(s.full_campaign.contracts.lin.fulfilled,"distinct stable and transport contributors")
	plan("jiang",20,"wages","settle")
	check(not s.full_campaign.contracts.jiang.fulfilled,"wages cannot preempt final day check")
	s.campaign.day=23;Rules.Full.verify(s,content)
	check(s.full_campaign.contracts.jiang.fulfilled,"wages verified at D23")
	deploy_fixture("M23",["jiang","lin","xu"])
	s.battle.heroes.jiang.cell=s.battle.objects.rebuild.cell.duplicate()
	check(attempt("pickup","jiang",{"target":"rebuild"}),"confirmed cargo before unresolved people")
	check(s.full_campaign.contracts.jiang.breached and s.full_campaign.contracts.jiang.fulfilled,"personnel priority breach records separately")
	print("P3_STORY_PROOFS_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
