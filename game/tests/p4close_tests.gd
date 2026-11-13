extends "res://tests/product018_story_tests.gd"
const Growth=preload("res://scripts/presentation/growth_presentation.gd")
const Facts=preload("res://scripts/presentation/story_facts.gd")
func run() -> void:
	c=Catalog.load_catalog();I18n.initialize()
	var pages: Array=[]
	for actor: String in ["lin","xu","su"]:
		for slot: int in range(3):
			s=Rules.begin_campaign(c,"starting-choice")
			var roster: Array=["lin","xu","su"];roster.erase(actor);roster.insert(slot,actor)
			var inventory: String=Store.canonical(s.inventory)
			check(act("acknowledge_recruit",{"actor":actor,"roster":roster}).ok,"first-contact choice "+actor)
			check(s.campaign.phase=="briefing" and Store.canonical(s.inventory)==inventory and s.actors[actor].fatigue==0,"choice costs nothing before deployment")
			check(Store.validate(JSON.parse_string(Store.canonical(Store.envelope(s,c))),c).ok,"choice saved")
			check(act("depart").ok and s.battle.heroes[actor].cell==c.boards.M01.spawns[slot],"real spawn follows chosen position")
	for actor: String in c.actors:
		var levels: Array=[0,12,28,48,72,100]
		for tier: int in range(1,6):
			var result: Array[String]=Growth.gains(c,actor,levels[tier-1],levels[tier])
			check(result.size()==1,"one crossed threshold "+actor)
			if tier in [1,3,5]:check(result[0].contains(c.domains.progression_relationship.levels["L%d"%(tier+1)]),"actual passive description")
			pages.append({"type":"growth","actor":actor,"level":tier+1,"text":result})
	# Editorial fixtures; never reported as a real acquired level or player playthrough.
	for node: Dictionary in Stories.nodes(c).values():
		for mode: String in ["present","recovery","letter"]:
			prepare(node,mode);check(act("story_open",{"node":node.id}).ok,"open "+node.id+mode)
			var options: Array=[""]
			if mode!="letter":
				for choice: Dictionary in node.choices:options.append(choice.id)
			for choice: String in options:
				s.chapter_one.scenes[node.id].choice=choice
				var view: Dictionary=Journey.scene(s,c,node.id)
				var lines: Array=[]
				for page: Dictionary in view.pages:
					check(not page.text.is_empty(),"nonempty rendered story")
					check(not page.text.contains("不播放") and not page.text.contains("本次只记录意愿"),"no production instructions")
					lines.append(page.text)
				pages.append({"type":"scene","id":node.id,"mode":mode,"choice":choice,"text":lines})
	for entry: Dictionary in c.domains.scripts.community:
		for outcome: String in ["success","partial","failed"]:
			for choice: String in ["publish","archive"]:
				s=Rules.begin_campaign(c,"community-editorial")
				check(Facts.community(s,c,entry).is_empty(),"unplayed community stays unknown")
				var facts: Dictionary={}
				for object: Dictionary in c.boards[entry.source].objectives:facts[object.id]="saved" if object.kind in ["rescue","cargo"] else "completed"
				s.campaign.settled[entry.source]={"outcome":outcome,"facts":facts}
				s.chapter_one.flags["community."+entry.source+".public"]=choice=="publish"
				var view: Dictionary=Facts.community(s,c,entry)
				check(view.choice==choice and view.facts.size()==facts.size(),"source facts and saved choice")
				var archived: String=Store.canonical(view)
				s.product.withdrawn=c.actors.keys();s.battle.mission_id="M24"
				check(Store.canonical(Facts.community(s,c,entry))==archived,"community independent of current scene/roster")
				if entry.id=="C14" and outcome=="failed":check(not view.text.contains("不再把这批药品计入"),"failed mandatory task preserves optional recovered medicine")
				pages.append({"type":"community","id":entry.id,"variant":outcome,"view":view})
	for entry: Dictionary in c.domains.scripts.chapter:
		for fact: String in ["saved","completed","lost","unresolved"]:
			s=Rules.begin_campaign(c,"chapter-editorial")
			check(Facts.chapter(s,c,entry).is_empty(),"unplayed chapter is not fabricated")
			s.campaign.settled[entry.source]={"outcome":"failed","facts":{entry.condition.objective:fact}}
			var view: Dictionary=Facts.chapter(s,c,entry)
			check(view.secured==(fact in ["saved","completed"]),"chapter uses object fact rather than overall success")
			pages.append({"type":"chapter","id":entry.id,"fact":fact,"view":view})
	var k12: Dictionary=c.domains.scripts.chapter[11]
	s.campaign.settled.M17={"outcome":"success","facts":{"repair2":"unresolved","isolate":"completed"}}
	check(Facts.chapter(s,c,k12).text==I18n.t("p4close.isolated_coda"),"successful isolation is not failed repair")
	for kind: String in ["self","other","shared","unknown"]:
		camp(23);s.full_campaign.contracts.mo={"node":"P_mo_2","breached":true}
		var shares: Dictionary={"mo":1.0} if kind=="self" else ({"leader":1.0} if kind=="other" else ({"mo":0.5,"leader":0.5} if kind=="shared" else {}))
		Rules.Appraisal.record(s,c,{"root":"P_mo_2:accepted-plan-breach","observers":["mo"],"known":kind!="unknown","visible_doubt":true,"shares":shares,"family":"breach","reason":"test source fact"})
		var script: Dictionary=Stories.script(c,Stories.nodes(c).P_mo_3)
		var view: Dictionary=Facts.breach(s,"mo",script)
		check(view.kind==kind and view.line==script["later_breach_"+kind],"responsibility controls voice "+kind)
		pages.append({"type":"breach","kind":kind,"view":view})
	var file:=FileAccess.open("res://../outputs/p4close-editorial.json",FileAccess.WRITE);file.store_string(JSON.stringify({"checks":checks,"failures":failures,"scope":"production presentation functions over explicit isolated editorial fixtures; not human acceptance","pages":pages},"\t"));file.close()
	print("P4CLOSE_RESULTS: checks=%d failures=%d"%[checks,failures]);quit(1 if failures else 0)
