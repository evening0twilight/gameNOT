extends RefCounted
## Atlas regions are runtime views; original generated assets remain unmodified.
static var cache: Dictionary={}
static func atlas(file: String,column: int,row: int,columns: int,rows: int) -> AtlasTexture:
	var key: String="%s:%d:%d:%d:%d" % [file,column,row,columns,rows]
	if cache.has(key):return cache[key]
	var texture: Texture2D=load("res://assets/%s.png" % (file if file.begins_with("visual_p2/") or file.begins_with("visual_p3/") or file.begins_with("motion_p4/") or file.begins_with("portraits018/") or file.begins_with("product018/") else "visual_p1/"+file))
	var region:=AtlasTexture.new();region.atlas=texture
	var cell: Vector2=texture.get_size()/Vector2(columns,rows)
	region.region=Rect2(Vector2(column,row)*cell+Vector2.ONE,cell-Vector2.ONE*2)
	region.filter_clip=true;cache[key]=region
	return region
static func portrait(id: String,expression: String="neutral") -> Texture2D:
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
	var ids: Array=["lin","xu","su","chen","ye","he","mo","jiang"]
	var index: int=ids.find(id)
	if index<0:return sprite(9)
	return atlas("motion_p4/crew_a" if index<4 else "motion_p4/crew_b",clampi(frame,0,5),index%4,6,4)

static func outfit(id: String,kind: String="work") -> Texture2D:
	if ResourceLoader.exists("res://assets/product018/"+id+".png"):return atlas("product018/"+id,1 if kind=="camp" else 0,0,4,3)
	if ResourceLoader.exists("res://assets/portraits018/"+id+".png"):return atlas("portraits018/"+id,1 if kind=="camp" else 0,0,5,2)
	return portrait(id)

static func narrative(location: String) -> Texture2D:
	var index: int=maxi(0,["office","clinic","dock","old_town","factory","gate","roof","shelter"].find(location))
	return atlas("product018/narrative",index%2,index/2,2,4)

static func icon(id: String) -> Texture2D:
	var path: String="res://assets/product018/icons/"+id+".svg"
	return load(path) if ResourceLoader.exists(path) else null
