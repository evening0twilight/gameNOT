extends RefCounted
## Show the reducer's actual differences before committing a common action.
static func summary(ui: Control,preview: Dictionary,payload: Dictionary) -> String:
	var before: Dictionary=ui.session.state.battle
	var after: Dictionary=preview.next_state.battle
	var parts: Array[String]=[]
	for id: String in before.heroes:
		var old: Dictionary=before.heroes[id];var next: Dictionary=after.heroes.get(id,old)
		var changes: Array[String]=[]
		if old.ap!=next.ap:changes.append(ui.I18n.t("quality.preview_ap")%[old.ap,next.ap])
		if old.hp!=next.hp:changes.append(ui.I18n.t("quality.preview_hp")%[old.hp,next.hp])
		if not changes.is_empty():parts.append(ui.actor_name(id)+"："+"，".join(changes))
	for id: String in before.enemies:
		var old: Dictionary=before.enemies[id];var next: Dictionary=after.enemies.get(id,old)
		if old.hp!=next.hp:parts.append(ui.I18n.t("quality.enemy."+old.type)+"："+ui.I18n.t("quality.preview_hp")%[old.hp,next.hp])
		if not old.disabled and next.disabled:parts.append(ui.I18n.t("quality.preview_disabled"))
	for id: String in before.objects:
		var old: Dictionary=before.objects[id];var next: Dictionary=after.objects.get(id,old)
		var changes: Array[String]=[]
		if old.hp!=next.hp:changes.append(ui.I18n.t("quality.preview_hp")%[old.hp,next.hp])
		if old.progress!=next.progress:changes.append(ui.I18n.t("quality.preview_work")%[old.progress,next.progress,next.work])
		if not old.stable and next.stable:changes.append(ui.I18n.t("quality.preview_stable"))
		if old.carrier!=next.carrier:changes.append(ui.I18n.t("quality.preview_carry")%ui.actor_name(next.carrier) if not next.carrier.is_empty() else ui.I18n.t("quality.preview_drop"))
		if not old.delivered and next.delivered:changes.append(ui.I18n.t("quality.preview_delivered"))
		if not changes.is_empty():parts.append(ui.object_name(id)+"："+"，".join(changes))
	if payload.has("cell"):parts.append(ui.I18n.t("quality.preview_cell")%[int(payload.cell[0])+1,int(payload.cell[1])+1])
	return "；".join(parts)
