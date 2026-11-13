extends RefCounted
## Atlas regions are runtime views; original generated assets remain unmodified.
const CharacterArt=preload("res://scripts/presentation/character_art.gd")
static var cache: Dictionary={}
static func character(id: String,kind: String="work",expression: String="neutral",minimum: Vector2=Vector2(155,200),head_only: bool=false) -> TextureRect:
	if CharacterArt.has_actor(id):return CharacterArt.view(id,kind,expression,minimum,head_only)
	return picture(portrait(id,expression) if head_only else outfit(id,kind),minimum)
static func atlas(file: String,column: int,row: int,columns: int,rows: int) -> AtlasTexture:
	var key: String="%s:%d:%d:%d:%d" % [file,column,row,columns,rows]
	if cache.has(key):return cache[key]
	var texture: Texture2D=load("res://assets/%s.png" % (file if file.begins_with("visual_p2/") or file.begins_with("visual_p3/") or file.begins_with("motion_p4/") or file.begins_with("portraits018/") or file.begins_with("product018/") or file.begins_with("characters018/") else "visual_p1/"+file))
	var region:=AtlasTexture.new();region.atlas=texture
	var cell: Vector2=texture.get_size()/Vector2(columns,rows)
	region.region=Rect2(Vector2(column,row)*cell+Vector2.ONE,cell-Vector2.ONE*2)
	region.filter_clip=true;cache[key]=region
	return region
static func portrait(id: String,expression: String="neutral") -> Texture2D:
	if CharacterArt.has_actor(id) and expression=="neutral":return CharacterArt.region(id,"work",true)
	if ResourceLoader.exists("res://assets/product018/"+id+".png"):
		var semantic: String={"smile":"light","worried":"doubtful","firm":"determined","surprised":"focused","grief":"doubtful","relieved":"touched"}.get(expression,expression)
		var index: int=2+maxi(0,["neutral","focused","light","doubtful","anger","tired","touched","determined","injured"].find(semantic))
		return atlas("product018/"+id,index%4,index/4,4,3)
	if ResourceLoader.exists("res://assets/portraits018/"+id+".png"):
		var index: int=2+maxi(0,["neutral","smile","worried","firm","tired","surprised","grief","relieved"].find(expression))
		return atlas("portraits018/"+id,index%5,index/5,5,2)
	if id in ["ye","he","mo","jiang"]:
		var key: String="portrait:"+id
		if cache.has(key):return cache[key]
		var full:=atlas("visual_p3/crew_portraits",["ye","he","mo","jiang"].find(id),0,4,1)
		var face:=AtlasTexture.new();face.atlas=full.atlas
		face.region=Rect2(full.region.position,Vector2(full.region.size.x,full.region.size.y*.54));face.filter_clip=true
		cache[key]=face
		return face
	if id=="chen":return atlas("visual_p2/chen_portrait",0,0,2,1)
	var full:=atlas("crew_portraits",{"lin":0,"xu":1,"su":2}.get(id,0),0,3,1)
	var face:=AtlasTexture.new();face.atlas=full.atlas
	face.region=Rect2(full.region.position,Vector2(full.region.size.x,full.region.size.y*.6));face.filter_clip=true
	return face
static func sprite(index: int) -> Texture2D:
	if index==4 and ResourceLoader.exists("res://assets/characters018/markers.png"):return atlas("characters018/markers",2,0,3,2)
	if index>=40:
		var region:=atlas("visual_p3/crew_sprites",(index-40)%4,(index-40)/4,4,2)
		var texture: Texture2D=region.atlas
		var lower: bool=index>=44
		region.region=Rect2(Vector2((index-40)%4*texture.get_width()/4.0,texture.get_height()*.56 if lower else 0),Vector2(texture.get_width()/4.0,texture.get_height()*(.44 if lower else .56)))
		return region
	if index>=30:return atlas("visual_p2/machines",index-30,0,3,1)
	if index>=20:return atlas("visual_p2/objectives",(index-20)%3,(index-20)/3,3,2)
	if index==10:
		if not cache.has("chen"):cache["chen"]=load("res://assets/visual_p2/chen_sprite.png")
		return cache["chen"]
	if index==9:
		if not cache.has("support"):cache["support"]=load("res://assets/visual_p1/support_responder.png")
		return cache["support"]
	return atlas("rescue_sprites",index%3,index/3,3,3)
static func terrain(index: int) -> Texture2D:
	return atlas("terrain_atlas",index%2,index/2,2,2)
static func ground(location: String,code: String=".") -> Texture2D:
	var index: int={"ferry":0,"clinic":1,"coldstore":1,"control":1,"factory":0,"pump":0,"warehouse":3,"shelter":3}.get(location,2)
	index={"~":4,"X":5,"#":6,":":7}.get(code,index)
	return atlas("product018/terrain-quality",index%4,index/4,4,2)
static func picture(texture: Texture2D,minimum: Vector2) -> TextureRect:
	var view:=TextureRect.new();view.texture=texture
	view.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	view.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_COVERED
	view.custom_minimum_size=minimum;view.mouse_filter=Control.MOUSE_FILTER_IGNORE
	return view

static func environment(location: String) -> Texture2D:
	if location in ["factory","roof","control","coldstore","housing","shelter"]:
		var extra: int=["factory","roof","control","coldstore","housing","shelter"].find(location)
		return atlas("visual_p3/environments",extra%3,extra/3,3,2)
	var index: int={"ferry":0,"clinic":1,"warehouse":2,"bridge":3,"pump":4,"gate":5}.get(location,0)
	return atlas("visual_p2/environments",index%3,index/3,3,2)

static func motion(id: String,frame: int) -> Texture2D:
	if ResourceLoader.exists("res://assets/characters018/"+id+"-motion.png"):return atlas("characters018/"+id+"-motion",clampi(frame,0,5)%3,clampi(frame,0,5)/3,3,2)
	if id.begins_with("responder_") and ResourceLoader.exists("res://assets/characters018/markers.png"):
		var variant: int=4+int(id.get_slice("_",2))%2
		return atlas("characters018/markers",variant%3,variant/3,3,2)
	var ids: Array=["lin","xu","su","chen","ye","he","mo","jiang"]
	var index: int=ids.find(id)
	if index<0:return sprite(9)
	return atlas("motion_p4/crew_a" if index<4 else "motion_p4/crew_b",clampi(frame,0,5),index%4,6,4)

static func outfit(id: String,kind: String="work") -> Texture2D:
	if CharacterArt.has_actor(id):return CharacterArt.region(id,kind)
	if ResourceLoader.exists("res://assets/product018/"+id+".png"):return atlas("product018/"+id,1 if kind=="camp" else 0,0,4,3)
	if ResourceLoader.exists("res://assets/portraits018/"+id+".png"):return atlas("portraits018/"+id,1 if kind=="camp" else 0,0,5,2)
	return portrait(id)

static func narrative(location: String) -> Texture2D:
	var index: int=maxi(0,["office","clinic","dock","old_town","factory","gate","roof","shelter"].find(location))
	return atlas("product018/narrative",index%2,index/2,2,4)

static func icon(id: String) -> Texture2D:
	var path: String="res://assets/product018/icons/"+id+".svg"
	return load(path) if ResourceLoader.exists(path) else null

static var rescue_roles: Dictionary={}
static func rescue_marker(mission: String,object: Dictionary) -> Texture2D:
	if not ResourceLoader.exists("res://assets/characters018/markers.png"):return sprite(4)
	if rescue_roles.is_empty():rescue_roles=JSON.parse_string(FileAccess.get_file_as_string("res://data/presentation/asset_roles.json")).rescue
	var role: String="injured" if object.get("id","").begins_with("casualty_") else rescue_roles.get(mission+":"+object.get("id",""),"adult")
	return atlas("characters018/markers",["adult","child","injured","staff"].find(role)%3,["adult","child","injured","staff"].find(role)/3,3,2)

const LOCATIONS=["bridge","clinic","coldstore","control","factory","ferry","gate","housing","pump","roof","shelter","warehouse"]
static func landmark(location: String) -> Texture2D:
	if not ResourceLoader.exists("res://assets/characters018/landmarks.png"):return null
	var index: int=LOCATIONS.find(location)
	return atlas("characters018/landmarks",index%4,index/4,4,3) if index>=0 else null
static func site_picture(location: String,minimum: Vector2) -> Control:
	var frame:=Control.new();frame.custom_minimum_size=minimum;frame.size_flags_horizontal=Control.SIZE_EXPAND_FILL;frame.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var backdrop:=picture(environment(location),Vector2.ZERO);frame.add_child(backdrop);backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var prop: Texture2D=landmark(location)
	if prop!=null:
		var mark:=picture(prop,Vector2.ZERO);mark.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;frame.add_child(mark)
		var fit: Callable=func():
			var side: float=minf(120,frame.size.y*.7)
			mark.size=Vector2.ONE*side;mark.position=Vector2(maxf(0,frame.size.x-side-10),maxf(0,frame.size.y-side-8))
		frame.resized.connect(fit)
	return frame
