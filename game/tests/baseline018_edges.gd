extends "res://tests/baseline018_tests.gd"
func _initialize() -> void:
	content=Catalog.load_catalog()
	knowledge()
	facilities()
	persistence()
	cooperation()
	hazards()
	var f:=FileAccess.open("res://../outputs/baseline018-edges.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":count,"failures":failures,"scope":"isolated boundary fixtures, not campaign completion evidence"},"\t"));f.close()
	print("BASELINE018_EDGES: checks=%d failures=%d"%[count,failures.size()]);quit(0 if failures.is_empty() else 1)
func knowledge() -> void:
	var s: Dictionary=Rules.fresh(content,"late-facts")
	s.campaign.day=20
	var fact: Dictionary={"root":"old-1","mission":"M01","occurrence_day":1,"observers":["lin"],"known":true,"shares":{"leader":1.0},"family":"breach","deliberate":true,"warned":true,"reason":"verified old event"}
	var initial: float=s.social["lin>leader"].trust
	Rules.Appraisal.record(s,content,fact)
	check("old event decays from first knowledge",s.social["lin>leader"].memories[0].day==20 and s.appraisal.events["old-1:lin"].occurrence_day==1)
	fact.shares={"leader":.5};Rules.Appraisal.record(s,content,fact)
	check("partial evidence correction refunds only difference",s.social["lin>leader"].trust==initial-4)
	var stable: String=Store.canonical(s.social)
	Rules.Appraisal.record(s,content,fact)
	check("repeated correction is idempotent",Store.canonical(s.social)==stable)
	for i: int in [2,3]:
		fact.root="old-"+str(i);fact.occurrence_day=i;fact.shares={"leader":1.0};Rules.Appraisal.record(s,content,fact)
	check("three old files learned today are not three recent deliberate breaches",not s.social["lin>leader"].memories[-1].serious)
	fact.known=false;fact.visible_doubt=true;fact.root="uncertain";Rules.Appraisal.record(s,content,fact)
	check("personality bounds uncertainty without blame",s.appraisal.provisional["uncertain:lin"].strength>0 and s.appraisal.provisional["uncertain:lin"].strength<4)
	check("revised appraisal persists",Store.validate(Store.envelope(s,content),content).ok)
	for id: String in ["lin","xu"]:s.social[id+">"+("xu" if id=="lin" else "lin")].grudge=100
	fact={"root":"new-related","observers":["lin"],"known":true,"shares":{"xu":1.0},"family":"breach","warned":true,"deliberate":true,"reason":"explicit new breach"}
	Rules.Appraisal.record(s,content,fact)
	check("long conflict cooldown shared across both directions",s.social["lin>xu"].cooldown_until_day==s.social["xu>lin"].cooldown_until_day and s.social["xu>lin"].cooldown_until_day==22)
func facilities() -> void:
	var s: Dictionary=fixture("M05")
	s.campaign.last_result={"outcome":"success"}
	Rules.Field.settled(s,content)
	check("preserved facility earned through success",s.operations.facilities.M05.qualified)
	s.campaign.phase="camp"
	check("facility not available same night",not command(s,"field_assistance",{"facility":"M05","participants":["lin"]}).ok)
	s.campaign.day=6;s.actors.lin.fatigue=30;s.actors.lin.stress=25
	var credits: Dictionary=s.inventory.duplicate();var xp: int=s.actors.lin.xp
	var r: Dictionary=command(s,"field_assistance",{"facility":"M05","participants":["lin"]})
	check("facility restores actual fatigue and stress without project or XP",r.ok and r.next_state.actors.lin.fatigue==18 and r.next_state.actors.lin.stress==9 and r.next_state.actors.lin.xp==xp and r.next_state.inventory==credits and r.next_state.campaign.projects==0)
	if r.ok:s=r.next_state
	check("one facility use per evening",not command(s,"field_assistance",{"facility":"M05","participants":["xu"]}).ok)
	s.campaign.day=7;r=command(s,"field_assistance",{"facility":"M05","participants":["lin"]});check("second use next evening",r.ok)
	if r.ok:s=r.next_state
	s.campaign.day=8;check("facility has exactly two uses",not command(s,"field_assistance",{"facility":"M05","participants":["lin"]}).ok)
	s=fixture("M05");s.campaign.last_result={"outcome":"failed"};Rules.Field.settled(s,content);s.campaign.phase="camp"
	r=command(s,"repair_field_facility",{"facility":"M05"});check("failed mission permits paid next-day repair",r.ok and r.next_state.inventory.supplies==s.inventory.supplies-2 and r.next_state.campaign.projects==s.campaign.projects+1)
	if r.ok:s=r.next_state
	s.campaign.day=10;check("repair never extends authored support window",not command(s,"field_assistance",{"facility":"M05","participants":["lin"]}).ok)
func persistence() -> void:
	var s: Dictionary=Rules.fresh(content,"legacy-neutral")
	var e: Dictionary=Store.envelope(s,content);e.runtime_revision=6;e.state=s.duplicate(true)
	for key: String in ["journey","operations","appraisal"]:e.state.erase(key)
	for key: String in ["exits","service"]:e.state.battle.erase(key)
	e.erase("checksum");e.checksum=Store.canonical(e).sha256_text()
	var r: Dictionary=Store.validate(e,content)
	check("revision6 migration preserves resources XP and mission",r.ok and r.state.inventory==s.inventory and r.state.actors==s.actors and r.state.battle.mission_id==s.battle.mission_id)
	check("migration invents no service progress or appraisal",r.ok and r.state.appraisal.events.is_empty() and r.state.battle.service.is_empty() and r.state.operations.assets.is_empty())
	for key: String in ["support_days","self_bands","positive","provisional"]:
		var broken: Dictionary=s.duplicate(true);broken.appraisal[key]["lin"]="bad"
		check("reject malformed "+key,not Store.validate(Store.envelope(broken,content),content).ok)
	var broken: Dictionary=s.duplicate(true);broken.social["lin>xu"].memories=[{"id":"malformed"}]
	check("reject malformed memory without crashing",not Store.validate(Store.envelope(broken,content),content).ok)
	var domains: Dictionary=content.domains.duplicate(true)
	domains.stories.personal_nodes[0].requires_resolved=[domains.stories.personal_nodes[0].id]
	check("content gate rejects story cycle",preload("res://scripts/infrastructure/baseline_catalog_validation.gd").validate(domains,content.actors,content.boards)=="story_dependency_cycle")
func cooperation() -> void:
	var s: Dictionary=fixture("M17")
	s.chapter_one.roster=["lin","xu","su"];Rules.deploy(s,content,"M17")
	var heavy: Dictionary={}
	for enemy: Dictionary in s.battle.enemies.values():
		if enemy.type in ["hauler","sentinel"]:heavy=enemy;break
	if heavy.is_empty():
		s=fixture("M06")
		for enemy: Dictionary in s.battle.enemies.values():
			if enemy.type in ["hauler","sentinel"]:heavy=enemy;break
	check("heavy authored fixture exists",not heavy.is_empty())
	if not heavy.is_empty():
		heavy.cell=[4,4];s.battle.heroes.lin.cell=[4,3];s.battle.heroes.xu.cell=[3,4];s.battle.heroes.su.cell=[0,7]
		for cell: Array in [[4,3],[3,4],[4,4],[4,5]]:Rules.set_terrain(s.battle,cell,".")
		var p: Dictionary={"protocol":"coordinated_pull","target":heavy.id,"partner":"xu","cell":[4,5],"consent":true}
		s.social["xu>lin"].band="conditional"
		check("restricted Xu needs explicit motion authority",not command(s,"protocol",p).ok)
		s.battle.authorizations.append("xu")
		var r: Dictionary=command(s,"protocol",p)
		check("coordinated pull moves heavy with both actual AP",r.ok and r.next_state.battle.enemies[heavy.id].cell==[4,5] and r.next_state.battle.heroes.lin.ap==s.battle.heroes.lin.ap-1 and r.next_state.battle.heroes.xu.ap==s.battle.heroes.xu.ap-1)
	s=fixture("M01");s.battle.heroes.lin.cell=[2,6];s.battle.heroes.xu.cell=[3,6];s.battle.heroes.su.cell=[1,6]
	for cell: Array in [[2,6],[3,6],[1,6]]:Rules.set_terrain(s.battle,cell,".")
	s.battle.objects.r1.cell=[2,5];s.battle.objects.r1.risk_context=["fall"]
	s.social["lin>xu"].band="conditional"
	var p: Dictionary={"protocol":"mutual_cover","partner":"xu","consent":true}
	check("fall cooperation requires real safeguard",not command(s,"protocol",p).ok)
	var r: Dictionary=command(s,"prepare_safety",{"target":"lin","protocol":"mutual_cover"},"su")
	check("third party can prepare mutual-cover protection",r.ok)
	if r.ok:s=r.next_state
	r=command(s,"protocol",p)
	check("prepared safeguard consumed by actual joint action",r.ok and r.next_state.battle.safety.is_empty() and r.next_state.battle.protection.has("su"))

func hazards() -> void:
	var s: Dictionary=Rules.fresh(content,"single-source-damage")
	var b: Dictionary=s.battle
	var enemy: Dictionary=b.enemies.values()[0]
	enemy.type="sentinel";enemy.cell=[2,5];b.intents[enemy.id]=[0,-1];b.round=2
	b.heroes.lin.cell=[2,4];b.heroes.lin.hp=1;b.heroes.lin.carrying="r1"
	b.objects.r1.cell=[2,4];b.objects.r1.carrier="lin";b.objects.r1.stable=true
	for cell: Array in [[2,5],[2,4],[2,3],[2,2]]:Rules.set_terrain(b,cell,".")
	var object_hp: int=b.objects.r1.hp
	Rules.Hazards.resolve(b,enemy,Rules)
	check("one attack drops cargo once without a second hit",b.heroes.lin.downed and b.heroes.lin.carrying.is_empty() and b.objects.r1.carrier.is_empty() and b.objects.r1.hp==object_hp)
	s=Rules.fresh(content,"environment-maximum");b=s.battle;enemy=b.enemies.values()[0]
	enemy.type="skimmer";enemy.cell=[2,7];b.intents[enemy.id]=[0,-1];b.round=2
	b.heroes.lin.cell=[1,7];b.heroes.lin.hp=4;b.heroes.xu.cell=[5,7];b.heroes.su.cell=[6,7]
	Rules.set_terrain(b,[1,7],"~");Rules.set_terrain(b,[2,7],"~")
	b.electrified_hits=[];b.cover.lin=2;b.environment.fire_pulse={"round":2,"duration_rounds":1,"cells":[[1,7]],"damage":1}
	Rules.Hazards.resolve(b,enemy,Rules);Rules.Hazards.environment(b,content.boards.M01,Rules)
	check("water ignores machine cover and fire does not stack",b.heroes.lin.hp==2 and b.cover.lin==2)
	b.heroes.lin.hp=4;b.electrified_hits=[];b.insulation=[[1,7]]
	Rules.Hazards.resolve(b,enemy,Rules);Rules.Hazards.environment(b,content.boards.M01,Rules)
	check("insulation removes electricity but leaves fire",b.heroes.lin.hp==3)
