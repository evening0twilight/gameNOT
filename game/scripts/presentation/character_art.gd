extends RefCounted
## Complete anatomy stays in the costume base. Expressions alter only a registered face rectangle.
const ROOT="res://assets/characters018/"
const EXPRESSIONS=["neutral","focused","light","doubtful","anger","tired","touched","determined"]
static var manifest: Dictionary={}
static var textures: Dictionary={}
static var face_shader: Shader
static func specs() -> Dictionary:
	if manifest.is_empty() and FileAccess.file_exists(ROOT+"manifest.json"):
		manifest=JSON.parse_string(FileAccess.get_file_as_string(ROOT+"manifest.json"))
	return manifest
static func has_actor(id: String) -> bool:return specs().has(id)
static func texture(path: String) -> Texture2D:
	if not textures.has(path):textures[path]=load(ROOT+path)
	return textures[path]
static func semantic(expression: String) -> String:
	return {"smile":"light","worried":"doubtful","firm":"determined","surprised":"focused","grief":"doubtful","relieved":"touched","injured":"neutral"}.get(expression,expression)
static func region(id: String,kind: String,head_only: bool=false) -> AtlasTexture:
	var info: Dictionary=specs()[id]
	var panel: int=1 if kind=="camp" else 0
	var rect:=Rect2(panel*768,0,768,1024)
	if head_only:
		var head: Array=info.head[panel]
		rect=Rect2(float(head[0])+panel*768,float(head[1]),float(head[2]),float(head[3]))
	var result:=AtlasTexture.new();result.atlas=texture(id+"-bodies.png");result.region=rect;result.filter_clip=true
	return result
static func view(id: String,kind: String,expression: String,minimum: Vector2,head_only: bool=false) -> TextureRect:
	var view:=TextureRect.new();view.texture=region(id,kind,head_only)
	view.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;view.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	view.custom_minimum_size=minimum;view.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var expression_index: int=EXPRESSIONS.find(semantic(expression))
	if expression_index<=0:return view
	var info: Dictionary=specs()[id]
	var panel: int=1 if kind=="camp" else 0
	var face: Array=info.face[panel]
	var source: Array=info.source
	if face_shader==null:
		face_shader=Shader.new()
		face_shader.code="""shader_type canvas_item;
		uniform sampler2D expressions;
		uniform vec2 source_origin;
		uniform vec2 target_origin;
		uniform vec2 face_size;
		void fragment(){
			vec4 base=texture(TEXTURE,UV);
			vec2 p=(UV-target_origin)/face_size;
			float edge=min(min(p.x,1.0-p.x),min(p.y,1.0-p.y));
			float blend=smoothstep(0.0,0.09,edge);
			vec4 part=texture(expressions,source_origin+clamp(p,vec2(0.0),vec2(1.0))*face_size);
			COLOR=vec4(mix(base.rgb,part.rgb,blend*part.a),base.a);
		}"""
	var mat:=ShaderMaterial.new();mat.shader=face_shader
	mat.set_shader_parameter("expressions",texture(id+"-expressions.png"))
	mat.set_shader_parameter("source_origin",Vector2(float(source[0])+float(expression_index%4)*384,float(source[1])+float(expression_index/4)*512)/Vector2(1536,1024))
	mat.set_shader_parameter("target_origin",Vector2(float(face[0])+panel*768,float(face[1]))/Vector2(1536,1024))
	mat.set_shader_parameter("face_size",Vector2(float(face[2]),float(face[3]))/Vector2(1536,1024))
	view.material=mat
	return view
