extends SceneTree
const Art=preload("res://scripts/presentation/visual_assets.gd")
const Board=preload("res://scripts/presentation/tactical_board.gd")
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const Catalog=preload("res://scripts/infrastructure/content_catalog.gd")
var checks: int=0
var failures: int=0
func check(condition: bool,description: String) -> void:
	checks+=1
	if not condition:failures+=1;printerr("VISUAL_FAIL: "+description)
func _initialize() -> void:call_deferred("run")
func run() -> void:
	for id: String in ["lin","xu","su"]:
		var portrait: Texture2D=Art.portrait(id)
		check(portrait.get_width()>300 and portrait.get_height()>300,"portrait resolution "+id)
	for index: int in range(9):
		var sprite: AtlasTexture=Art.sprite(index)
		check(sprite.atlas.get_size().x>=1200,"sprite source resolution")
		check(Rect2(Vector2.ZERO,sprite.atlas.get_size()).encloses(sprite.region),"sprite atlas bounds")
	check(Art.sprite(9)!=null and Art.cache.has("support"),"temporary responder texture retained across render frames")
	var pixels: Image=load("res://assets/visual_p1/rescue_sprites.png").get_image()
	check(pixels.get_pixel(0,0).a<.1,"sprite background has real transparency")
	for index: int in range(4):check(Art.terrain(index)!=null,"terrain region")
	check(load("res://assets/visual_p1/harbor_camp.png")!=null,"camp background")
	var content:=Catalog.load_catalog()
	var state:=Rules.fresh(content,"visual-test")
	for mission: String in ["M01","M02"]:
		if mission=="M02":Rules.deploy(state,content,"M02")
		var before: Dictionary=state.duplicate(true)
		for actor: String in state.battle.heroes:
			var start: Array=state.battle.heroes[actor].cell
			for y: int in range(8):
				for x: int in range(8):
					var target: Array=[x,y]
					var cost: int=Rules.move_cost(state.battle,start,target,4)
					if cost<0:continue
					var path:=Board.route(state.battle,start,target)
					check(not path.is_empty(),"legal destination has route")
					var actual: int=0
					for index: int in range(1,path.size()):
						check(Rules.distance(path[index-1],path[index])==1 and not Rules.blocked(state.battle,path[index]),"route follows traversable cardinal cells")
						actual+=2 if Rules.terrain(state.battle,path[index]) in ["~",":"] else 1
					check(actual==cost,"displayed route matches authoritative move cost")
		check(state==before,"visual pathfinding leaves campaign immutable")
	print("VISUAL_P1_RESULTS: checks=%d failures=%d" % [checks,failures])
	quit(1 if failures else 0)
