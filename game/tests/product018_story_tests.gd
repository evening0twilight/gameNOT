extends "res://tests/p3_rules_tests.gd"
const Journey=preload("res://scripts/presentation/journey_presentation.gd")
const Delivery=preload("res://scripts/domain/story_delivery.gd")
func prepare(node: Dictionary,mode: String) -> void:
	camp(23)
	for required: String in node.get("requires_resolved",[]):s.chapter_one.scenes[required]={"seen":true,"choice":"","status":"resolved"}
	if mode=="recovery":
		for id: String in node.get("actors",[node.get("actor","")]):s.actors[id].ready_day=25
	elif mode=="letter":s.product.withdrawn.append(node.get("actor",node.get("actors",[""])[0]))
func run() -> void:
	c=Catalog.load_catalog();I18n.initialize()
	var examined: Array=[]
	for node: Dictionary in Stories.nodes(c).values():
		for mode: String in ["present","recovery","letter"]:
			prepare(node,mode)
			var social: String=Store.canonical(s.social)
			check(act("story_open",{"node":node.id}).ok,"open "+node.id+mode)
			var record: Dictionary=s.chapter_one.scenes[node.id]
			check(record.delivery.mode==mode,"delivery captured "+node.id+mode)
			var view: Dictionary=Journey.scene(s,c,node.id)
			check(not view.pages.is_empty() and not view.pages[0].text.is_empty(),"actual rendered text "+node.id+mode)
			check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,c))),c).ok,"delivery save "+node.id+mode)
			var before: String=Store.canonical(view)
			# A later state change must not rewrite the archive.
			for actor: Dictionary in s.actors.values():actor.ready_day=1
			s.product.withdrawn=[]
			check(Store.canonical(Journey.scene(s,c,node.id))==before,"archive stable after recovery "+node.id+mode)
			if mode=="letter":
				check(not act("story_choice",{"node":node.id,"choice":node.choices[0].id}).ok,"letter cannot make agreement "+node.id)
				check(Store.canonical(s.social)==social,"letter no relation reward "+node.id)
			elif node.category=="recovery_nodes":
				var stress: float=s.actors[node.actor].stress;var load_value: float=s.actors[node.actor].self_load
				var closeness: float=s.social[node.actor+">leader"].closeness
				check(act("story_choice",{"node":node.id,"choice":node.choices[0].id}).ok,"life choice "+node.id)
				check(s.actors[node.actor].stress==stress and s.actors[node.actor].self_load==load_value,"life is not treatment "+node.id)
				check(s.social[node.actor+">leader"].closeness==minf(100,closeness+3),"life closeness once "+node.id)
				check(not act("story_choice",{"node":node.id,"choice":node.choices[0].id}).ok,"life cannot farm reward "+node.id)
			if mode!="letter":
				for option: Dictionary in node.choices:
					var snapshot: Dictionary=s.duplicate(true)
					s.chapter_one.scenes[node.id].choice=option.id
					var choice_view: Dictionary=Journey.scene(s,c,node.id)
					check(choice_view.pages.size()>view.pages.size(),"choice text delivered "+node.id+option.id+mode)
					for page: Dictionary in choice_view.pages:
						check(not page.text.is_empty(),"nonempty page "+node.id)
						check(not page.text.contains("不播放") and not page.text.contains("本次只记录意愿") and not page.text.contains("不产生本场"),"no production instructions in dialogue "+node.id)
					s=snapshot
			examined.append({"scene":node.id,"mode":mode,"text":view.pages[0].text})
	# A recruitment choice changes only the next plan, not the actual sortie.
	camp(4)
	var supplies: int=s.inventory.supplies
	check(act("acknowledge_recruit",{"actor":"chen","roster":["lin","chen","su"]}).ok,"recruit assignment")
	check(s.journey.draft.roster==["lin","chen","su"] and s.inventory.supplies==supplies and s.campaign.phase=="camp","choice saved without deployment or charges")
	check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,c))),c).ok,"recruit choice save")
	var file:=FileAccess.open("res://../outputs/product018-story-coverage.json",FileAccess.WRITE);file.store_string(JSON.stringify({"checks":checks,"failures":failures,"scope":"isolated editorial fixtures, no claim of complete human playthrough","views":examined},"\t"));file.close()
	print("PRODUCT018_STORY: checks=%d failures=%d"%[checks,failures]);quit(1 if failures else 0)
