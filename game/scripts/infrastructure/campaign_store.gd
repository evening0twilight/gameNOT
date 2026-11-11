extends RefCounted
## One envelope per slot, validated before replacement. No reward replay on load.
var fail_writes: bool = false
var validated_files: Dictionary={}
func known_valid_file(path: String,content: Dictionary) -> bool:
	if not FileAccess.file_exists(path):return false
	var digest: String=FileAccess.get_file_as_string(path).sha256_text()
	var known: Dictionary=validated_files.get(path,{})
	if known.get("digest")==digest and known.get("content")==content.content_sha256:return true
	return read_file(path,content).ok
static var templates: Dictionary={}
static func validation_template(content: Dictionary) -> Dictionary:
	var key: String=str(content.get("content_sha256",""))
	if key.is_empty():return preload("res://scripts/domain/campaign_rules.gd").fresh(content,"validation")
	if not templates.has(key):templates[key]=preload("res://scripts/domain/campaign_rules.gd").fresh(content,"validation")
	return templates[key]
static func canonical(value: Variant) -> String:
	return JSON.stringify(normalize(value),"",true,true)
static func normalize(value: Variant) -> Variant:
	if value is float and is_finite(value) and value == floor(value): return int(value)
	if value is Array:
		var array: Array = []
		for entry: Variant in value: array.append(normalize(entry))
		return array
	if value is Dictionary:
		var object: Dictionary = {}
		for key: Variant in value: object[key] = normalize(value[key])
		return object
	return value
static func envelope(state: Dictionary,content: Dictionary) -> Dictionary:
	var e := {"format":"night_tide_save","schema_version":2,"content_version":content.version,"content_sha256":content.content_sha256,"engine_version":"4.7.2","runtime_revision":8,"campaign_id":state.campaign.id,"revision":state.revision,"state":state}
	e.checksum=canonical(e).sha256_text()
	return e
static func validate(e: Variant,content: Dictionary) -> Dictionary:
	if not e is Dictionary: return {"ok":false,"error_code":"corrupt_save"}
	if not int(e.get("runtime_revision",-1)) in [2,3,4,5,6,7,8]: return {"ok":false,"error_code":"unsupported_runtime_revision"}
	if e.get("schema_version")!=2: return {"ok":false,"error_code":"unsupported_schema"}
	if e.get("content_sha256")!=content.content_sha256 or e.get("content_version")!=content.version: return {"ok":false,"error_code":"content_mismatch"}
	var copy: Dictionary = e.duplicate(true)
	copy.erase("checksum")
	if e.get("checksum")!=canonical(copy).sha256_text(): return {"ok":false,"error_code":"corrupt_save"}
	if e.get("format")!="night_tide_save" or not e.get("state") is Dictionary: return {"ok":false,"error_code":"corrupt_save"}
	var s: Dictionary = e.state.duplicate(true)
	if e.runtime_revision==4 and s.get("full_campaign") is Dictionary and s.get("battle") is Dictionary:
		# Neutral optional fields from in-session P3 candidates; checksum was checked above.
		for key: String in ["medicine_stock","packed","publications"]:
			if not s.full_campaign.has(key):s.full_campaign[key]=[] if key=="publications" else 0
		if not s.battle.has("protection"):s.battle.protection=[]
		if not s.battle.has("reinforcement") and content.boards.has(s.battle.get("mission_id")):s.battle.reinforcement=content.boards[s.battle.mission_id].reinforcement.duplicate(true)
	if e.runtime_revision<4:
		var migration_error: String=migrate_legacy(s,content)
		if not migration_error.is_empty():return {"ok":false,"error_code":migration_error}
	if int(e.runtime_revision)<5:
		if not migrate_product(s,content):return {"ok":false,"error_code":"corrupt_save"}
	if int(e.runtime_revision)<6:migrate_balance(s)
	if int(e.runtime_revision)<7:
		if not s.get("actors") is Dictionary or not s.get("chapter_one") is Dictionary or not s.get("battle") is Dictionary:return {"ok":false,"error_code":"corrupt_save"}
		migrate_alignment(s,content)
	return validate_state(s,content,e.get("revision"),e.get("campaign_id"))

static func validate_state(s: Dictionary,content: Dictionary,expected_revision: Variant,expected_campaign: Variant,include_state: bool=true) -> Dictionary:
	for field: String in ["campaign","battle","actors","inventory","social","story","tutorial","rng","commands"]:
		if not s.get(field) is Dictionary: return {"ok":false,"error_code":"corrupt_save"}
	if not s.get("receipts") is Array or not s.get("revision") is float and not s.get("revision") is int: return {"ok":false,"error_code":"corrupt_save"}
	if s.revision!=expected_revision or s.campaign.get("id")!=expected_campaign or not content.boards.has(s.battle.get("mission_id")): return {"ok":false,"error_code":"corrupt_save"}
	if not s.campaign.get("phase") in ["battle","settlement","camp","briefing"]: return {"ok":false,"error_code":"corrupt_save"}
	if not s.rng.get("seed") is String or not s.rng.get("state") is String: return {"ok":false,"error_code":"corrupt_save"}
	for field: String in ["heroes","objects","enemies","intents"]:
		if not s.battle.get(field) is Dictionary: return {"ok":false,"error_code":"corrupt_save"}
	for h: Variant in s.battle.heroes.values():
		if not h is Dictionary or not h.get("cell") is Array or h.cell.size()!=2 or not h.has("ap") or h.ap<0 or h.ap>3 or not h.has("hp") or h.hp<0 or h.hp>12: return {"ok":false,"error_code":"corrupt_save"}
	for value: Variant in s.inventory.values():
		if not (value is int or value is float) or not is_finite(float(value)) or value<0: return {"ok":false,"error_code":"corrupt_save"}
	var template: Dictionary = validation_template(content)
	for field: String in ["campaign","actors","inventory","social","rng"]:
		if not shape_matches(template[field],s[field]): return {"ok":false,"error_code":"corrupt_save"}
	if not shape_matches(template.battle,s.battle): return {"ok":false,"error_code":"corrupt_save"}
	if s.campaign.mission_id!=s.battle.mission_id or s.campaign.day<1 or s.battle.round<1 or s.battle.round>s.battle.limit: return {"ok":false,"error_code":"corrupt_save"}
	var board: Dictionary = content.boards[s.battle.mission_id]
	if s.battle.rows.size()!=8 or s.battle.heroes.size()!=3: return {"ok":false,"error_code":"corrupt_save"}
	for row: Variant in s.battle.rows:
		if not row is String or row.length()!=8: return {"ok":false,"error_code":"corrupt_save"}
	var object_ids: Array = []
	for object: Dictionary in board.objectives+board.controls:
		if preload("res://scripts/domain/full_campaign.gd").objective_active(s,board,object):object_ids.append(object.id)
	if s.battle.objects.size()<object_ids.size() or s.battle.objects.size()>object_ids.size()+3: return {"ok":false,"error_code":"corrupt_save"}
	for id: String in s.battle.objects:
		if not object_ids.has(id) and not (id.begins_with("casualty_") and s.battle.heroes.has(id.trim_prefix("casualty_"))): return {"ok":false,"error_code":"corrupt_save"}
		var object: Variant = s.battle.objects[id]
		if not object is Dictionary or not shape_matches({"id":"","cell":[],"progress":0,"completed":false,"delivered":false,"lost":false,"carrier":"","stable":false,"contributors":[],"hp":0,"prerequisites":[],"kind":"","work":0,"sustain_until_exit":false},object): return {"ok":false,"error_code":"corrupt_save"}
	for id: String in s.battle.heroes:
		var hero: Dictionary = s.battle.heroes[id]
		if not shape_matches(template.battle.heroes.lin,hero): return {"ok":false,"error_code":"corrupt_save"}
		if not content.actors.has(id) and not id.begins_with("responder_"+s.battle.mission_id+"_"): return {"ok":false,"error_code":"corrupt_save"}
		if not preload("res://scripts/infrastructure/content_catalog.gd").cell_valid(hero.cell): return {"ok":false,"error_code":"corrupt_save"}
		if not hero.carrying.is_empty() and (not s.battle.objects.has(hero.carrying) or s.battle.objects[hero.carrying].carrier!=id): return {"ok":false,"error_code":"corrupt_save"}
	for i: int in range(s.receipts.size()):
		if not s.receipts[i] is Dictionary or s.receipts[i].get("seq")!=i+1: return {"ok":false,"error_code":"corrupt_save"}
	if not s.has("chapter_one") or not shape_matches(template.chapter_one,s.chapter_one):return {"ok":false,"error_code":"corrupt_save"}
	if not s.has("full_campaign") or not shape_matches(template.full_campaign,s.full_campaign):return {"ok":false,"error_code":"corrupt_save"}
	if not preload("res://scripts/infrastructure/alignment_validation.gd").valid(s,content):return {"ok":false,"error_code":"corrupt_save"}
	if not preload("res://scripts/domain/crew_journey.gd").valid(s,content):return {"ok":false,"error_code":"corrupt_save"}
	if not validate_product(s,content):return {"ok":false,"error_code":"corrupt_save"}
	if not validate_full(s,content):return {"ok":false,"error_code":"corrupt_save"}
	if s.has("chapter_one"):
		var chapter: Variant=s.chapter_one
		if not shape_matches(template.chapter_one,chapter):return {"ok":false,"error_code":"corrupt_save"}
		if chapter.main_completed<0 or chapter.main_completed>24 or chapter.side_day<0 or chapter.side_day>s.campaign.day:return {"ok":false,"error_code":"corrupt_save"}
		for list_name: String in ["attempted","worked","roster"]:
			var unique: Array=[]
			for id: Variant in chapter[list_name]:
				if not id is String or unique.has(id):return {"ok":false,"error_code":"corrupt_save"}
				if list_name=="attempted":
					if not content.boards.has(id) or content.boards[id].kind!="side":return {"ok":false,"error_code":"corrupt_save"}
				elif not s.actors.has(id):return {"ok":false,"error_code":"corrupt_save"}
				unique.append(id)
		var nodes: Dictionary=preload("res://scripts/domain/chapter_stories.gd").nodes(content)
		for id: String in chapter.scenes:
			var scene: Variant=chapter.scenes[id]
			if not nodes.has(id) or not shape_matches({"seen":false,"choice":"","status":""},scene):return {"ok":false,"error_code":"corrupt_save"}
			if scene.has("delivery") and not preload("res://scripts/domain/story_delivery.gd").valid(scene.delivery,s):return {"ok":false,"error_code":"corrupt_save"}
			if not scene.status in ["unread","seen","deferred","resolved"]:return {"ok":false,"error_code":"corrupt_save"}
			if not scene.choice.is_empty():
				var valid_choice: bool=false
				for choice: Dictionary in nodes[id].choices:
					if choice.id==scene.choice:valid_choice=true
				if not valid_choice or not scene.seen:return {"ok":false,"error_code":"corrupt_save"}
		for value: Variant in chapter.flags.values():
			if not value is bool:return {"ok":false,"error_code":"corrupt_save"}
	if s.battle.undo.size()>256:return {"ok":false,"error_code":"corrupt_save"}
	for checkpoint: Variant in s.battle.undo:
		if not checkpoint is Dictionary or not checkpoint.get("battle") is Dictionary or not checkpoint.battle.get("undo") is Array or not checkpoint.battle.undo.is_empty():return {"ok":false,"error_code":"corrupt_save"}
		# The outer checksum already covers these bytes. Validate their structure directly.
		if not validate_state(checkpoint,content,checkpoint.get("revision"),s.campaign.id,false).ok:return {"ok":false,"error_code":"corrupt_save"}
	if not include_state:return {"ok":true,"error_code":""}
	var migrated: Dictionary=s.duplicate(true)
	preload("res://scripts/domain/chapter_one.gd").ensure(migrated)
	return {"ok":true,"state":migrated,"error_code":""}
static func shape_matches(template: Variant,value: Variant) -> bool:
	if template is Dictionary:
		if not value is Dictionary: return false
		for key: Variant in template:
			# These collections have mission-scoped keys; validated separately.
			if key in ["heroes","objects","enemies","intents","equipment"]: continue
			if not value.has(key) or not shape_matches(template[key],value[key]): return false
		return true
	if template is Array: return value is Array
	if template is int or template is float: return (value is int or value is float) and is_finite(float(value)) 
	return typeof(template)==typeof(value)

func read_file(path: String,content: Dictionary) -> Dictionary:
	if not FileAccess.file_exists(path): return {"ok":false,"error_code":"missing_save"}
	var f := FileAccess.open(path,FileAccess.READ)
	if f==null or f.get_length()>67108864: return {"ok":false,"error_code":"corrupt_save"}
	var raw: String=f.get_as_text()
	var parser := JSON.new()
	if parser.parse(raw) != OK: return {"ok":false,"error_code":"corrupt_save"}
	var result: Dictionary=validate(parser.data,content)
	if result.ok:validated_files[path]={"digest":raw.sha256_text(),"content":content.content_sha256}
	return result
func load_slot(path: String,content: Dictionary,backup: bool=false) -> Dictionary:
	return read_file(path+".bak" if backup else path,content)
func save_slot(path: String,state: Dictionary,content: Dictionary) -> Dictionary:
	if fail_writes: return {"ok":false,"error_code":"save_io_failed"}
	# Validate the supplied current-runtime state once. The temporary file is verified
	# byte-for-byte below; parsing/cloning the entire undo history again adds no coverage.
	if not validate_state(state,content,state.get("revision"),state.get("campaign",{}).get("id"),false).ok:return {"ok":false,"error_code":"save_io_failed"}
	var raw: String=canonical(envelope(state,content))
	var digest: String=raw.sha256_text()
	var directory: String = path.get_base_dir()
	if DirAccess.make_dir_recursive_absolute(directory)!=OK: return {"ok":false,"error_code":"save_io_failed"}
	var f := FileAccess.open(path+".tmp",FileAccess.WRITE)
	if f==null: return {"ok":false,"error_code":"save_io_failed"}
	f.store_string(raw)
	f.flush()
	f.close()
	if FileAccess.get_file_as_string(path+".tmp").sha256_text()!=digest:return {"ok":false,"error_code":"save_io_failed"}
	validated_files[path+".tmp"]={"digest":digest,"content":content.content_sha256}
	if FileAccess.file_exists(path):
		if not known_valid_file(path,content): return {"ok":false,"error_code":"existing_save_invalid"}
		if DirAccess.copy_absolute(path,path+".bak.tmp")!=OK: return {"ok":false,"error_code":"save_io_failed"}
		if FileAccess.get_file_as_string(path+".bak.tmp").sha256_text()!=validated_files[path].digest or DirAccess.rename_absolute(path+".bak.tmp",path+".bak")!=OK: return {"ok":false,"error_code":"save_io_failed"}
	if DirAccess.rename_absolute(path+".tmp",path)!=OK: return {"ok":false,"error_code":"save_io_failed"}
	validated_files[path]=validated_files[path+".tmp"];validated_files.erase(path+".tmp")
	return {"ok":true,"error_code":""}

static func migrate_legacy(s: Dictionary,content: Dictionary) -> String:
	if not s.get("campaign") is Dictionary or not s.get("battle") is Dictionary or not s.campaign.get("settled") is Dictionary:return "corrupt_save"
	preload("res://scripts/domain/chapter_one.gd").ensure(s)
	s.full_campaign.migrated=true
	if not s.battle.has("reinforcement") and content.boards.has(s.battle.get("mission_id")):s.battle.reinforcement=content.boards[s.battle.mission_id].reinforcement.duplicate(true)
	for actor: Dictionary in s.get("actors",{}).values():
		if actor.get("join",0)>s.campaign.day:actor.xp=[0,12,28,48][preload("res://scripts/domain/full_campaign.gd").chapter(actor.join)-1]
	if s.chapter_one.main_completed<24:s.chapter_one.finished=false
	for key: String in {"barriers":{},"insulation":[],"beacons":{},"medicine":0,"branch":"","spawn_count":0,"protection":[]}:
		if not s.battle.has(key):s.battle[key]={"barriers":{},"insulation":[],"beacons":{},"medicine":0,"branch":"","spawn_count":0,"protection":[]}[key]
	for checkpoint: Variant in s.battle.get("undo",[]):
		if not checkpoint is Dictionary or not migrate_legacy(checkpoint,content).is_empty():return "corrupt_save"
	return ""
static func validate_full(s: Dictionary,content: Dictionary) -> bool:
	var f: Dictionary=s.full_campaign
	if s.campaign.day>24 or s.campaign.day<1:return false
	if not f.route in ["","shared_control","distributed_rebuild","evacuation"] or not f.ending in ["","shared_control","distributed_rebuild","evacuation"]:return false
	if not f.ending.is_empty() and (s.campaign.day!=24 or not s.campaign.settled.has("M24") or not s.chapter_one.finished):return false
	for id: String in f.evidence:
		if not content.domains.world.evidence.has(id) or not shape_matches({"source":"","day":0,"revision":0},f.evidence[id]):return false
	for id: String in f.contracts:
		if not s.actors.has(id) or not shape_matches({"node":"","choice":"","created_revision":0,"created_day":0,"paid":0,"fulfilled":false,"proof":"","fulfilled_day":0},f.contracts[id]):return false
		if f.contracts[id].created_revision>s.revision or f.contracts[id].paid<0:return false
	for id: String in s.actors:
		var actor: Dictionary=s.actors[id]
		if actor.xp<0 or actor.xp>100 or actor.training_completed<0 or actor.training_completed>4 or actor.fatigue<0 or actor.fatigue>100:return false
	for id: String in s.campaign.districts:
		if not f.district_caps.has(id) or not int(f.district_caps[id]) in [2,3] or s.campaign.districts[id]>f.district_caps[id]:return false
	return true

static func migrate_product(s: Dictionary,content: Dictionary) -> bool:
	if not s.get("actors") is Dictionary or not s.get("battle") is Dictionary:return false
	var product=preload("res://scripts/domain/product_systems.gd")
	product.ensure(s)
	if not s.battle.has("environment"):
		if not content.boards.has(s.battle.get("mission_id")):return false
		s.battle.environment=product.weather(content.boards[s.battle.mission_id],s.battle.get("variant","A"))
	for checkpoint: Variant in s.battle.get("undo",[]):
		if not checkpoint is Dictionary or not migrate_product(checkpoint,content):return false
	return true
static func validate_product(s: Dictionary,content: Dictionary) -> bool:
	var product=preload("res://scripts/domain/product_systems.gd")
	var sample: Dictionary=validation_template(content)
	if not s.get("product") is Dictionary or not shape_matches(sample.product,s.product):return false
	if s.product.variant not in ["A","B"] or s.battle.variant not in ["A","B"] or s.battle.difficulty not in ["relaxed","standard","hard"] or s.campaign.difficulty not in ["relaxed","standard","hard"]:return false
	if s.battle.get("balance_revision",0)!=int(s.battle.get("balance_revision",0)) or not int(s.battle.get("balance_revision",0)) in [1,2,3]:return false
	if s.battle.limit!=product.limit(content.boards[s.battle.mission_id],s.battle.difficulty):return false
	if not s.battle.get("environment") is Dictionary or s.battle.environment!=product.weather(content.boards[s.battle.mission_id],s.battle.variant):return false
	var unique: Array=[]
	for id: Variant in s.product.owned:
		if not id is String or product.item(content,id).is_empty() or unique.has(id):return false
		unique.append(id)
	unique=[]
	for gear: Variant in s.product.loadout.values():
		if not gear is Dictionary or not shape_matches({"tool":"","support":""},gear):return false
		for slot: String in ["tool","support"]:
			var id: String=gear[slot]
			if id.is_empty():continue
			if not s.product.owned.has(id) or unique.has(id) or product.item(content,id).slot!=slot:return false
			unique.append(id)
	for value: Variant in s.product.facilities.values():
		if not (value is int or value is float) or value!=int(value) or value<0 or value>2:return false
	unique=[]
	for id: Variant in s.product.withdrawn:
		if not id is String or not s.actors.has(id) or unique.has(id):return false
		unique.append(id)
	if not s.battle.equipment is Dictionary:return false
	for id: String in s.battle.equipment:
		if not s.battle.heroes.has(id) or not shape_matches({"tool":"","support":""},s.battle.equipment[id]):return false
		for slot: String in ["tool","support"]:
			var tool: String=s.battle.equipment[id][slot]
			if not tool.is_empty() and (not s.product.owned.has(tool) or product.item(content,tool).slot!=slot):return false
	if s.battle.medicine<0 or s.battle.medicine>s.battle.medicine_limit or int(s.battle.medicine_limit) not in [2,3]:return false
	for id: String in s.product.purchases:
		if not s.product.owned.has(id) or id in ["crowbar","medkit"]:return false
		var purchase: Variant=s.product.purchases[id]
		if not shape_matches({"credits":0,"parts":0,"discounted":false,"main":0,"deployed":false},purchase):return false
		if purchase.credits!=product.item(content,id).price_credits or purchase.parts!=maxi(0,int(product.item(content,id).price_parts)-(1 if purchase.discounted else 0)):return false
	return true

static func migrate_balance(s: Dictionary) -> void:
	# A loaded battle (including undo checkpoints) retains the original damage and deadlines.
	if not s.get("battle") is Dictionary:return
	s.battle.balance_revision=1
	for checkpoint: Variant in s.battle.get("undo",[]):
		if checkpoint is Dictionary:migrate_balance(checkpoint)

static func migrate_alignment(s: Dictionary,content: Dictionary) -> void:
	preload("res://scripts/domain/crew_journey.gd").migrate(s)
	if not s.battle.has("exits"):s.battle.exits=content.boards.get(s.battle.get("mission_id"),{}).get("exits",[]).duplicate(true)
	# Mid-mission legacy saves retain their previously available routes and do not invent service progress.
	if not s.battle.has("service"):s.battle.service={}
	for checkpoint: Dictionary in s.battle.get("undo",[]):migrate_alignment(checkpoint,content)
