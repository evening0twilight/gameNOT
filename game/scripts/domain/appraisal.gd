extends RefCounted
const Social=preload("res://scripts/domain/campaign_social.gd")
static func ensure(s: Dictionary) -> void:
	if not s.has("appraisal"):s.appraisal={"events":{},"personal_missions":[],"support_days":{},"self_bands":{},"provisional":{},"conflicts":[],"scene_missions":[],"positive":{},"relief":{}}
static func traits(content: Dictionary,id: String) -> Dictionary:
	for a: Dictionary in content.domains.experience.actors:
		if a.id==id:return a.traits
	return {"self_demand":0.5,"evidence_need":1.0,"face_concern":0.0}
static func self_band(s: Dictionary,id: String) -> void:
	var level: int=int(s.appraisal.self_bands.get(id,0))
	var value: float=s.actors[id].self_load
	while level>0 and value<([0,30,55][level]):level-=1
	while level<2 and value>=([40,70][level]):level+=1
	s.appraisal.self_bands[id]=level
static func record(s: Dictionary,content: Dictionary,fact: Dictionary) -> void:
	ensure(s)
	var root: String=str(fact.get("root",""))
	if root.is_empty():return
	var observers: Array=fact.get("observers",[])
	var shares: Dictionary=fact.get("shares",{})
	var total: float=0
	for share: Variant in shares.values():
		if not (share is int or share is float) or share<0:return
		total+=share
	if total>1.000001:return
	for id: String in observers:
		if not s.actors.has(id):continue
		var key: String=root+":"+id
		if not fact.get("known",false):
			if fact.get("visible_doubt",false) and not s.appraisal.provisional.has(key):
				var target: String=str(fact.get("suspected_target",shares.keys()[0] if shares.size()==1 else "unknown"))
				var budget: float=0
				for p: Dictionary in s.appraisal.provisional.values():
					if p.observer==id and p.target==target and p.mission==s.battle.mission_id:budget+=p.strength
				s.appraisal.provisional[key]={"observer":id,"target":target,"mission":s.battle.mission_id,"root":root,"status":"unverified","strength":minf(maxf(0,4-budget),provisional_strength(s,content,id,target)),"reason":fact.get("reason","责任尚未核实"),"day":s.campaign.day}
			continue
		if s.appraisal.provisional.has(key):s.appraisal.provisional[key].status="verified" if not shares.is_empty() else "disproved"
		var previous: Dictionary=s.appraisal.events.get(key,{})
		var family: String=str(fact.get("family","cost_overrun"))
		if not content.domains.experience.appraisal.numeric_families.has(family):continue
		var spec: Dictionary=content.domains.experience.appraisal.numeric_families[family]
		var severity: float=spec.severity;var trust_loss: float=spec.trust_loss;var serious: bool=spec.severe
		var occurrence: int=int(fact.get("occurrence_day",previous.get("occurrence_day",s.campaign.day)))
		var repeats: int=0
		if family=="breach" and fact.get("deliberate",false) and fact.get("warned",false):
			for e: Dictionary in s.appraisal.events.values():
				if e.observer==id and e.root!=root and e.family=="breach" and e.get("deliberate",false) and e.get("warned",false) and e.get("occurrence_day",e.day)>=occurrence-2 and e.get("occurrence_day",e.day)<=occurrence and not e.shares.is_empty():repeats+=1
			if repeats>=2 and occurrence>=s.campaign.day-2:severity=18;trust_loss=12;serious=true
		var first_day: int=previous.get("day",s.campaign.day)
		var entry: Dictionary={"root":root,"observer":id,"family":family,"day":first_day,"first_known_day":first_day,"occurrence_day":occurrence,"mission":fact.get("mission",previous.get("mission",s.battle.mission_id)),"shares":shares.duplicate(),"deliberate":fact.get("deliberate",false),"warned":fact.get("warned",false),"reason":fact.get("reason",""),"directions":previous.get("directions",{}).duplicate(true),"consequences":fact.get("consequences",[]).duplicate(true)}
		for target: String in (shares.keys()+previous.get("shares",{}).keys()):
			var pair: String=id+">"+target
			if not s.social.has(pair):continue
			var share: float=shares.get(target,0.0)
			var r: Dictionary=s.social[pair]
			var event_id: String=root+":"+id+":"+target
			if not entry.directions.has(target):entry.directions[target]={"base":r.duplicate(true),"stress":s.actors[id].stress,"amplitude":0.0,"loss":0.0}
			var base: Dictionary=entry.directions[target]
			if share<=0:
				for m: Dictionary in r.memories:
					if m.id==event_id:
						r.trust=minf(100,r.trust+maxf(0,m.actual_trust_loss-float(m.get("refunded",0))));m.refunded=m.actual_trust_loss;m.amplitude=0.0;m.corrected=true
				base.loss=0.0;base.amplitude=0.0
				continue
			var event: Dictionary={"id":event_id,"observer":id,"known":true,"blame":{target:share},"category":spec.category,"severity":severity,"trust_loss":trust_loss,"serious":serious,"remedy":"keep_agreement" if family=="breach" else "related_contribution","sensitivity":content.actors[id].sensitivity.get(spec.category,1.0)}
			var ideal: Dictionary=Social.Legacy.apply_event(base.base,event,first_day,base.stress)
			if ideal.memories.size()<=base.base.memories.size():continue
			var desired: Dictionary=ideal.memories[-1]
			var exists: bool=false
			for m: Dictionary in r.memories:
				if m.id!=event_id:continue
				exists=true
				if is_equal_approx(desired.amplitude,base.amplitude) and is_equal_approx(desired.actual_trust_loss,base.loss) and m.serious==serious:continue
				var old: float=base.amplitude
				# A compressed memory keeps its compression ratio; revision cannot restore archived weight.
				var ratio: float=0 if m.get("archived",false) else (minf(1,float(m.amplitude)/old) if old>0 else 1.0)
				m.amplitude=desired.amplitude*ratio;m.corrected=false
				var loss: float=minf(r.trust,maxf(0,desired.actual_trust_loss-base.loss))
				var refund: float=minf(maxf(0,base.loss-desired.actual_trust_loss),maxf(0,m.actual_trust_loss-float(m.get("refunded",0))))
				r.trust=minf(100,r.trust-loss+refund);m.actual_trust_loss+=loss;m.refunded=float(m.get("refunded",0))+refund;m.serious=serious
				if serious:m.half_life=8.0;m.floor=.35
			if not exists:r=Social.event(r,event,first_day,s.actors[id].stress)
			base.amplitude=desired.amplitude;base.loss=desired.actual_trust_loss
			s.social[pair]=Social.refresh(r,s.campaign.day,s.actors[id].stress)
			if s.social[pair].band=="rupture" and Social.Legacy.can_rupture(s.social[pair],s.campaign.day,s.battle.mission_id,true,bool(fact.get("warned",false))):
				var long_scene: bool=not s.appraisal.scene_missions.has(s.battle.mission_id)
				s.appraisal.conflicts.append({"pair":pair,"event":event_id,"day":s.campaign.day,"mission":s.battle.mission_id,"status":"pending","long_scene":long_scene,"reason":entry.reason})
				if long_scene:s.appraisal.scene_missions.append(s.battle.mission_id)
				s.social[pair]=Social.Legacy.mark_rupture(s.social[pair],s.campaign.day,s.battle.mission_id)
				var reverse: String=target+">"+id
				if s.social.has(reverse):s.social[reverse]=Social.Legacy.mark_rupture(s.social[reverse],s.campaign.day,s.battle.mission_id)
		s.appraisal.events[key]=entry
static func breached_pair(s: Dictionary,a: String,b: String,mission: String) -> bool:
	ensure(s)
	for e: Dictionary in s.appraisal.events.values():
		if e.mission==mission and e.family=="breach" and not e.shares.is_empty() and (e.observer in [a,b] or e.shares.has(a) or e.shares.has(b)):return true
	# Legacy records without actor attribution cannot establish clean cooperation.
	for receipt: Dictionary in s.receipts:
		if receipt.kind=="relationship_changed" and receipt.get("object_id","") in [a+">leader",b+">leader",a+">"+b,b+">"+a] and receipt.get("next_state",{}).get("seen_events",[]).size()>receipt.get("previous_state",{}).get("seen_events",[]).size() and receipt.get("campaign_day",-1)==s.campaign.day and s.appraisal.events.is_empty():return true
	return false
static func positives(s: Dictionary,content: Dictionary) -> void:
	ensure(s)
	var objects: Array=s.battle.objects.values().duplicate()
	if not s.battle.get("service",{}).is_empty() and s.battle.service.done:objects.append({"id":"live-service","completed":true,"sustain_until_exit":false,"hp":1,"lost":false,"contributors":s.battle.service.contributors})
	for pair: String in s.social:
		var r: Dictionary=s.social[pair]
		if not s.battle.heroes.has(r.observer) or not s.battle.heroes.has(r.target):continue
		if breached_pair(s,r.observer,r.target,s.battle.mission_id):continue
		var one: bool=false;var two: bool=false
		var budget_key: String=s.battle.mission_id+":"+pair
		var used: float=s.appraisal.positive.get(budget_key,0)
		for o: Dictionary in objects:
			if not o.completed or o.lost or (o.sustain_until_exit and o.hp<=0):continue
			one=one or o.contributors.has(r.observer);two=two or o.contributors.has(r.target)
			if not o.contributors.has(r.observer) or not o.contributors.has(r.target):continue
			var key: String=budget_key+":"+o.id
			if s.appraisal.positive.has(key):continue
			var witness: String=""
			var regard: float=0
			for other: String in s.battle.heroes:
				if other in [r.observer,r.target]:continue
				var closeness: float=s.social.get(r.observer+">"+other,{}).get("closeness",0)
				if closeness>=60 and closeness>regard:witness=other;regard=closeness
			var profile: Dictionary=traits(content,r.observer)
			var salience: float=float(profile.face_concern)*regard/100.0
			var gain: float=minf(100-r.trust,minf(3-used,2+(1 if salience>=.5 else 0)))
			r.trust=minf(100,r.trust+gain);used+=gain;s.appraisal.positive[key]={"gain":gain,"object":o.id,"witness":witness,"pair":pair}
			var relief_budget: float=minf(minf(3,1+2*float(profile.get("repair_openness",.5))+salience),6-float(s.appraisal.relief.get(budget_key,0)))
			for memory: Dictionary in r.memories:
				if relief_budget<=0 or memory.serious or memory.get("archived",false) or memory.get("corrected",false) or memory.category not in ["promise","fairness"]:continue
				if memory.category=="promise" and not s.battle.get("retreat_promise",{}).get("kept",false):continue
				var weight: float=Social.Legacy.memory_value(memory,s.campaign.day)
				if weight<=0:continue
				var decrease: float=minf(weight,relief_budget)
				memory.amplitude*=1-decrease/weight;relief_budget-=decrease
				s.appraisal.relief[budget_key]=float(s.appraisal.relief.get(budget_key,0))+decrease
			s.appraisal.positive[budget_key]=used
		if one and two and not r.contribution_missions.has(s.battle.mission_id):r.contribution_missions.append(s.battle.mission_id)
		s.social[pair]=Social.refresh(r,s.campaign.day,s.actors[r.observer].stress)
static func personal(s: Dictionary,content: Dictionary,outcome: String,injured: Array) -> void:
	ensure(s)
	var mission: String=s.battle.mission_id
	if s.appraisal.personal_missions.has(mission):return
	s.appraisal.personal_missions.append(mission)
	for id: String in s.battle.heroes:
		if not s.actors.has(id):continue
		var a: Dictionary=s.actors[id]
		var costs: int=1 if injured.has(id) else 0
		var promise: bool=s.battle.get("retreat_promise",{}).get("resolved",false) and not s.battle.retreat_promise.kept
		var weather: bool=s.battle.get("weather_exposed",[]).has(id)
		var pressure: int=mini(12,(4 if outcome=="failed" else 0)+2*costs+(1 if promise else 0)+(1 if weather else 0))
		if outcome=="success":pressure-=4
		var control: float=0.0
		for object: Dictionary in s.battle.objects.values():
			if object.contributors.has(id):control=1.0
		var load_gain: float=minf(6,(4 if outcome=="failed" else 0)+costs)*float(traits(content,id).self_demand)*(.25+.75*control)
		var before_stress: float=a.stress;var before_load: float=a.self_load
		a.stress=clampi(a.stress+pressure,0,100);a.self_load=clampf(a.self_load+minf(8,load_gain),0,100)
		self_band(s,id)
		s.appraisal.events[mission+":personal:"+id]={"root":mission+":result","observer":id,"family":"personal","day":s.campaign.day,"mission":mission,"shares":{},"reason":"任务%s%s%s%s"%[{"success":"完成","partial":"部分完成","failed":"未完成"}[outcome],"；自己负伤" if costs else "","；未守住约定时限" if promise else "","；受到环境影响" if weather else ""],"stress":a.stress-before_stress,"self_load":a.self_load-before_load,"directions":{}}
static func support(s: Dictionary,id: String) -> void:
	ensure(s)
	if s.appraisal.support_days.get(id,-1)==s.campaign.day:return
	s.actors[id].self_load=maxf(0,s.actors[id].self_load-2);s.appraisal.support_days[id]=s.campaign.day;self_band(s,id)

static func repair_proof(s: Dictionary,pair: String,memory: Dictionary) -> String:
	if memory.stage!=1:return ""
	var target: String=pair.split(">")[1]
	for result: Dictionary in s.campaign.settled.values():
		if result.get("revision",0)<=memory.get("ack_revision",s.revision):continue
		if memory.remedy=="keep_agreement":
			if result.get("promise",{}).get("kept",false) and (target=="leader" or result.get("standing",[]).has(target)):return result.mission+":kept-promise"
		elif memory.remedy=="related_contribution":
			for ids: Array in result.get("contributions",{}).values():
				if ids.has(target) and result.outcome=="success":return result.mission+":contribution"
	return ""
static func repair_command(s: Dictionary,c: Dictionary) -> String:
	var pair: String=c.actor_id+">"+str(c.payload.get("target","leader"))
	if not s.social.has(pair) or s.campaign.talked.size()>=2:return "invalid_target"
	var event: String=str(c.payload.get("event",""))
	for m: Dictionary in s.social[pair].memories:
		if m.id!=event:continue
		if c.kind=="schedule_repair":
			if m.stage!=1 or m.has("scheduled_mission"):return "invalid_target"
			m.scheduled_mission="M%02d"%(s.chapter_one.main_completed+1)
		else:
			var proof: String=repair_proof(s,pair,m)
			if proof.is_empty():return "proof_required"
			s.social[pair]=Social.Legacy.repair(s.social[pair],event,proof,m.remedy)
		for conflict: Dictionary in s.appraisal.conflicts:
			if conflict.pair==pair and conflict.event==event:conflict.status="scheduled" if c.kind=="schedule_repair" else "repaired"
		s.campaign.talked.append(c.kind+":"+event);return ""
	return "invalid_target"

static func provisional_strength(s: Dictionary,content: Dictionary,id: String,target: String) -> float:
	var profile: Dictionary=traits(content,id)
	var prior: float=float(s.social.get(id+">"+target,{}).get("grudge",0))
	return clampf(4*(.25+.5*float(profile.get("externalize",.5))+.25*prior/100)*(1-.5*float(profile.get("evidence_need",1))),0,4)
