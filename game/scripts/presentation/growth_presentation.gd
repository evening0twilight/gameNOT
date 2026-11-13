extends RefCounted
const Specialties=preload("res://scripts/domain/p1_specialties.gd")
## Describe actual crossed thresholds from the authority, without forecasting earned XP.
static func gains(content: Dictionary,id: String,before: int,after: int) -> Array[String]:
	var rows: Array[String]=[]
	for level: int in range(Specialties.level(before)+1,Specialties.level(after)+1):
		var details: Array[String]=[]
		if level in [2,4,6]:details.append(content.domains.progression_relationship.levels["L%d"%level])
		for ability: Dictionary in content.domains.abilities:
			if ability.actor!=id:continue
			if level==int(ability.level):details.append(ability.name+"："+ability.effect)
			if level==3 and ability.has("level3_effect"):details.append(ability.level3_effect)
			if level==5 and ability.has("level5_effect"):details.append(ability.level5_effect)
		rows.append("Lv%d · "%level+"\n".join(details))
	return rows
