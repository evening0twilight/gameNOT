extends "res://tests/p3_rules_tests.gd"
const Journey=preload("res://scripts/presentation/journey_presentation.gd")
const Facts=preload("res://scripts/presentation/story_facts.gd")
var entries: Dictionary={}
var translated_pages: int=0
var untranslated:=RegEx.new()
var day_templates: Dictionary={}

func review_pages(node: Dictionary,view: Dictionary,mode: String) -> void:
	for page: Dictionary in view.pages:
		translated_pages+=1
		check(not page.text.is_empty(),"text "+node.id)
		if I18n.locale=="en":check(untranslated.search(page.text)==null,"English page "+node.id)
		if mode=="letter":
			check(page.speaker=="" and page.expressions.is_empty(),"absent people are not staged "+node.id)
		if page.speaking:
			var speaker: String=I18n.s(c.actors[page.speaker].name)
			check(page.text.begins_with(speaker+"：") or page.text.begins_with(speaker+": "),"speaker matches delivered line "+node.id)
		for actor: String in view.delivery.injured:
			check(page.expressions.get(actor)=="injured","injured expression "+node.id)

func dialogues() -> void:
	for node: Dictionary in Stories.nodes(c).values():
		var people: Array=node.get("actors",[node.get("actor","")])
		var variants: Array=[["present",""]]
		for person: String in people:
			variants.append(["recovery",person])
			variants.append(["letter",person])
		var day: int=int(node.earliest_day)
		# Put all participants in the roster pool as an explicit fixture even
		# when a nominal earliest day precedes the actual final recruit.
		day=maxi(day,16)
		if not day_templates.has(day):
			camp(day)
			day_templates[day]=s.duplicate(true)
		var cases: Array=[]
		for variant: Array in variants:
			var mode: String=variant[0]
			var affected: String=variant[1]
			s=day_templates[day].duplicate(true)
			for prerequisite: String in node.get("requires_resolved",[]):s.chapter_one.scenes[prerequisite]={"seen":true,"choice":"","status":"resolved"}
			if mode=="recovery":s.actors[affected].ready_day=day+2
			if mode=="letter":s.product.withdrawn.append(affected)
			check(act("story_open",{"node":node.id}).ok,"open "+node.id+mode)
			var original: Dictionary=s.duplicate(true)
			var branches: Array=[]
			for option: Dictionary in node.choices:
				s=original.duplicate(true)
				if option.id=="integrated" and mode!="letter":
					check(Stories.choice_error(s,node,option)=="proof_required","unearned trust not selectable "+node.id)
					check(not act("story_choice",{"node":node.id,"choice":option.id}).ok,"commit rejects unearned trust")
					s.full_campaign.contracts[node.actor]={"fulfilled":true,"breached":false,"node":"P_"+node.actor+"_2"}
				var verdict: Dictionary=act("story_choice",{"node":node.id,"choice":option.id})
				if mode=="letter":
					check(not verdict.ok and s.social==original.social,"letter cannot reply or gain "+node.id)
				else:
					check(verdict.ok,"eligible reply "+node.id+" "+option.id)
				for language: String in I18n.LOCALES:
					I18n.locale=language
					var view: Dictionary=Journey.scene(s,c,node.id)
					check(view.delivery.mode==mode,"recorded circumstances "+node.id)
					review_pages(node,view,mode)
					if mode=="letter":check(view.pages.size()==1,"absent scene has one record")
				branches.append({"choice":option.id,"accepted":verdict.ok})
			cases.append({"mode":mode,"affected":affected,"choices":branches})
		entries[node.id]={"actors":people,"variants":cases}

func consequences() -> void:
	I18n.locale="zh_CN"
	for community: Dictionary in c.domains.scripts.community:
		var cases: int=0
		for outcome: String in ["success","partial","failed"]:
			for decision: String in ["publish","archive",""]:
				s=day_templates.values()[0].duplicate(true)
				var saved_facts: Dictionary={}
				for objective: Dictionary in c.boards[community.source].objectives:
					saved_facts[objective.id]="unresolved" if saved_facts.size()%2 else ("saved" if objective.kind in ["rescue","cargo"] else "completed")
				s.campaign.settled[community.source]={"outcome":outcome,"facts":saved_facts}
				var flag: String="community."+community.source+".public"
				s.chapter_one.flags.erase(flag)
				if not decision.is_empty():s.chapter_one.flags[flag]=decision=="publish"
				for language: String in I18n.LOCALES:
					I18n.locale=language
					var report: Dictionary=Facts.community(s,c,community)
					check(report.outcome==outcome and report.choice==decision and report.facts.size()==saved_facts.size(),"source and publication "+community.id)
					check(report.reply.size()==int(not decision.is_empty()),"no fabricated answer "+community.id)
					if language=="en":check(untranslated.search(I18n.s(report.text))==null,"translated follow-up "+community.id)
				cases+=1
		entries[community.id]={"mission":community.source,"publication_outcome_pairs":cases}
	for chapter: Dictionary in c.domains.scripts.chapter:
		var cases: Array=[]
		for status: String in ["saved","completed","lost","unresolved"]:
			s=day_templates.values()[0].duplicate(true)
			s.campaign.settled[chapter.source]={"outcome":"failed","facts":{chapter.condition.objective:status}}
			for language: String in I18n.LOCALES:
				I18n.locale=language
				var report: Dictionary=Facts.chapter(s,c,chapter)
				check(report.secured==(status in ["saved","completed"]),"objective before overall outcome "+chapter.id)
				if language=="en":check(untranslated.search(I18n.s(report.text))==null,"translated chapter "+chapter.id)
			cases.append(status)
		entries[chapter.id]={"mission":chapter.source,"objective":chapter.condition.objective,"statuses":cases}

func responsibility() -> void:
	for person: String in c.actors:
		var id: String="P_"+person+"_3"
		var script: Dictionary=Stories.script(c,Stories.nodes(c)[id])
		var kinds: Array=[]
		for kind: String in ["self","other","shared","unknown"]:
			s=day_templates.values()[0].duplicate(true)
			var plan: String="P_"+person+"_2"
			s.full_campaign.contracts[person]={"node":plan,"breached":true}
			var shares: Dictionary={}
			if kind in ["self","shared"]:shares[person]=0.5 if kind=="shared" else 1.0
			if kind in ["other","shared"]:shares.leader=0.5 if kind=="shared" else 1.0
			Rules.Appraisal.record(s,c,{"root":plan+":accepted-plan-breach","observers":[person],"known":kind!="unknown","visible_doubt":true,"shares":shares,"family":"breach","reason":"review source"})
			var report: Dictionary=Facts.breach(s,person,script)
			check(report.kind==kind and report.line==script["later_breach_"+kind],"blame follows known evidence "+id+kind)
			for language: String in I18n.LOCALES:
				I18n.locale=language
				if language=="en":check(untranslated.search(I18n.s(report.line))==null,"blame localized")
			kinds.append(kind)
		entries[id].attribution=kinds

func run() -> void:
	c=Catalog.load_catalog()
	I18n.initialize()
	untranslated.compile("[\\x{4e00}-\\x{9fff}]")
	dialogues()
	consequences()
	responsibility()
	check(entries.size()==96,"all nodes")
	var f:=FileAccess.open("res://../outputs/p4release-20261119-story-branches.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"checks":checks,"failures":failures,"translated_pages":translated_pages,"nodes":entries,"scope":"Isolated production command and rendering-data checks. Injury or withdrawal affects each participant in turn. Fulfilled proofs are fixtures. Mixed public records probe source selection, not reachability. No player or Windows observations."},"  ")+"\n")
	f.close()
	print("RELEASE_STORY: nodes=%d pages=%d checks=%d failures=%d"%[entries.size(),translated_pages,checks,failures])
	quit(1 if failures else 0)
