extends RefCounted
const I18n=preload("res://scripts/presentation/localization.gd")
const Journey=preload("res://scripts/presentation/journey_presentation.gd")
## All views refer to the saved source mission, never today's battle or injured roster.
static func community(s: Dictionary,content: Dictionary,entry: Dictionary) -> Dictionary:
	if not s.campaign.settled.has(entry.source):return {}
	var result: Dictionary=s.campaign.settled[entry.source]
	var field: String="variants."+result.outcome
	var overrides: Dictionary=Journey.catalog().get("community_text",{}).get(entry.id,{})
	var text: String=overrides.get(result.outcome,I18n.content("scenes",entry.id,field,entry.variants[result.outcome]))
	var facts: Array[String]=[]
	for id: String in result.facts:
		var name: String=id
		for object: Dictionary in content.boards[entry.source].objectives+content.boards[entry.source].controls:
			if object.id==id:name=object.label;break
		facts.append(name+" · "+I18n.t("p3.fact_"+result.facts[id]))
	var flag: String="community."+entry.source+".public"
	var choice: String=("publish" if s.chapter_one.flags[flag] else "archive") if s.chapter_one.flags.has(flag) else ""
	var reply: Array=entry.choices.get(choice,[])
	return {"text":text,"facts":facts,"source":entry.source,"choice":choice,"reply":reply,"outcome":result.outcome}
static func chapter(s: Dictionary,content: Dictionary,entry: Dictionary) -> Dictionary:
	if not s.campaign.settled.has(entry.source):return {}
	var result: Dictionary=s.campaign.settled[entry.source]
	var secured: bool=result.facts.get(entry.condition.objective,"") in ["saved","completed"]
	var field: String="true_text" if secured else "false_text"
	var text: String=Journey.catalog().get("chapter_text",{}).get(entry.id,{}).get(field,I18n.content("scenes",entry.id,field,entry[field]))
	if entry.id=="K12" and result.facts.get("isolate","")=="completed":text=I18n.t("p4close.isolated_coda")
	return {"text":text,"secured":secured,"source":entry.source,"fact":result.facts.get(entry.condition.objective,"unresolved")}
static func breach(s: Dictionary,actor: String,script: Dictionary) -> Dictionary:
	var contract: Dictionary=s.full_campaign.contracts.get(actor,{})
	if not contract.get("breached",false):return {}
	var event: Dictionary={}
	var root: String=str(contract.get("node",""))+":accepted-plan-breach"
	for candidate: Dictionary in s.appraisal.events.values():
		if candidate.observer==actor and candidate.root==root:event=candidate;break
	var own: float=event.get("shares",{}).get(actor,0.0)
	var other: float=0.0
	for target: String in event.get("shares",{}):
		if target!=actor:other+=float(event.shares[target])
	var kind: String="shared" if own>0 and other>0 else ("self" if own>0 else ("other" if other>0 else "unknown"))
	return {"kind":kind,"line":script.get("later_breach_"+kind,script.get("later_breach","")),"reason":event.get("reason",I18n.t("p4close.unknown_breach"))}
