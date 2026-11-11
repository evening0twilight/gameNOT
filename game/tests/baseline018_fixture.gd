extends RefCounted
static func joined(s: Dictionary) -> void:
	# Isolated historical/ability fixture only; campaign tests acquire recruits by settlement.
	for id: String in s.actors:
		if s.actors[id].join<=s.campaign.day:s.journey.recruited[id]={"day":s.actors[id].join,"revision":0,"mission":"fixture"}
