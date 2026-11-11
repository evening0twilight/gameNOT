extends "res://tests/p3_story_proofs.gd"
const History=preload("res://scripts/domain/history_repair.gd")
const Store=preload("res://scripts/infrastructure/campaign_store.gd")
func camp() -> void:
	s.campaign.phase="camp";s.campaign.talked=[];s.campaign.projects=0;s.campaign.used=[]
func joined_fixture(pair: String) -> void:
	# Explicit known-history fixture; subsequent repair proof must still be created by reducer actions.
	s=Rules.fresh(content,"history-"+pair);s.campaign.day=20;s.chapter_one.main_completed=19;camp()
	preload("res://tests/baseline018_fixture.gd").joined(s)
	for id: String in ["E_ORDER","E_MAINTENANCE"]:s.full_campaign.evidence[id]={"source":"fixture","day":19,"revision":0}
	s.full_campaign.known.chen_signed_responsibility=true
	for entry: Array in [["P_lin_1","share"],["P_su_1","list"],["R03","agreement"],["P_mo_1","classify"]]:
		s.chapter_one.scenes[entry[0]]={"seen":true,"choice":entry[1],"status":"resolved"}
func joint_work(mission: String,first: String,second: String,target: String) -> void:
	deploy_fixture(mission,[first,second,"lin" if first!="lin" and second!="lin" else "su"])
	var cell: Array=s.battle.objects[target].cell
	s.battle.heroes[first].cell=cell.duplicate();s.battle.heroes[second].cell=[int(cell[0])-1,int(cell[1])]
	check(attempt("interact",first,{"target":target}),"first actual joint work "+mission)
	if not s.battle.objects[target].completed:check(attempt("interact",second,{"target":target}),"second actual joint work "+mission)
	check(attempt("emergency_retreat",first,{"confirmed":true}),"actual joint settlement")
	camp()
func run() -> void:
	content=Catalog.load_catalog()
	for route: Dictionary in content.domains.integration.history_repair_routes:
		joined_fixture(route.pair)
		var before: float=s.social[route.pair].grudge
		check(attempt("history_repair","lin",{"pair":route.pair,"consent":true}),"explicit directed acknowledgement "+route.pair)
		check(s.social[route.pair].grudge==maxf(0,before-6),"stage1 only6 "+route.pair)
		check(not attempt("history_repair","lin",{"pair":route.pair,"consent":true}),"no fabricated next-stage proof "+route.pair)
		check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,content))),content).ok,"history persisted "+route.pair)
	joined_fixture("chen>ye")
	attempt("history_repair","lin",{"pair":"chen>ye","consent":true})
	# Both operate a 4-work goal using ordinary actions; no outcome or contribution injection.
	joint_work("M17","chen","ye","repair1")
	# repair1 finishes with first increment; it cannot fabricate a joint contribution.
	check(History.proof(s,"chen>ye").is_empty(),"same scene with only one contributor does not repair")
	deploy_fixture("M20",["chen","ye","lin"])
	s.battle.heroes.chen.cell=[3,2];s.battle.heroes.ye.cell=[2,2]
	check(attempt("protocol","chen",{"protocol":"protected_work","partner":"ye","target":"west","consent":true}),"real two-person target")
	attempt("emergency_retreat","chen",{"confirmed":true});camp()
	check(attempt("history_repair","chen",{"pair":"chen>ye","consent":true}),"stage2 accepts later shared target")
	check(not attempt("history_repair","chen",{"pair":"chen>ye","consent":true}),"same mission cannot pay stage3")
	deploy_fixture("M21",["chen","ye","lin"])
	s.battle.heroes.chen.cell=[3,2];s.battle.heroes.ye.cell=[2,2]
	check(attempt("protocol","chen",{"protocol":"protected_work","partner":"ye","target":"route","consent":true}),"different later shared target")
	if not s.battle.objects.route.completed:attempt("interact","chen",{"target":"route"})
	attempt("emergency_retreat","chen",{"confirmed":true});camp()
	check(attempt("history_repair","chen",{"pair":"chen>ye","consent":true}),"third historical stage actual second mission")
	check(s.social["chen>ye"].history_stage==3,"all stages sequential")
	joined_fixture("chen>mo");attempt("history_repair","chen",{"pair":"chen>mo","consent":true})
	check(attempt("publish_record","mo",{"privacy":"redacted"}),"new redacted public fact")
	check(attempt("history_repair","chen",{"pair":"chen>mo","consent":true}),"public fact repairs only correct direction")
	joined_fixture("xu>lin");attempt("history_repair","lin",{"pair":"xu>lin","consent":true})
	s.campaign.phase="settlement";check(attempt("community_report","lin",{"choice":"publish"}),"actual community publication")
	camp();check(attempt("history_repair","lin",{"pair":"xu>lin","consent":true}),"community publication verified")
	plan("chen",12,"copy","fund");camp()
	s.full_campaign.evidence.E_MAINTENANCE={"source":"fixture","day":12,"revision":s.revision}
	check(attempt("history_repair","chen",{"pair":"ye>chen","consent":true}),"Chen accountability before repair work")
	# A previously fulfilled contract must not prevent a new later job from proving this stage.
	s.full_campaign.contracts.chen.fulfilled=true;s.full_campaign.contracts.chen.proof="M10:test1"
	deploy_fixture("M13",["chen","lin","xu"]);solve(content.boards.M13);camp()
	check(attempt("history_repair","chen",{"pair":"ye>chen","consent":true}),"new engineering receipt usable after old contract fulfillment")
	joined_fixture("ye>chen");s.product.withdrawn.append("ye")
	check(not attempt("history_repair","chen",{"pair":"ye>chen","consent":true}),"withdrawn observer not telepathically repaired")
	print("P4_HISTORY_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
