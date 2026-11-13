extends Control
## Render-only board. All action legality and mutations stay in Session/Rules.
signal cell_chosen(cell: Array)
const Rules=preload("res://scripts/domain/campaign_rules.gd")
const I18n=preload("res://scripts/presentation/localization.gd")
const Art=preload("res://scripts/presentation/visual_assets.gd")
var state: Dictionary
var board: Dictionary
var selected: String
var validate_hover: Callable
var reachable: Array=[]
var previous: Dictionary={}
var animation_started: int=0
const Feedback=preload("res://scripts/presentation/action_feedback.gd")
var feedback: Dictionary={}
var playhead: float=-1.0
var playback_seconds: Callable
var hint_cell: Array=[]
var actor_facings: Dictionary={}
func seconds() -> float:
	if playhead>=0:return playhead
	if playback_seconds.is_valid():return playback_seconds.call()
	return float(Time.get_ticks_msec()-animation_started)/1000.0
func animating() -> bool:
	return not feedback.is_empty() and seconds()<float(feedback.duration)
func impact() -> float:return float(feedback.get("impact",.34))
func changed_enemy_at(id: String) -> float:
	for event: Dictionary in feedback.get("machines",[]):
		if event.id==id:return float(event.at)+.18
	return impact()

var hover: Vector2i=Vector2i(-1,-1)
var legal_hover: bool=false
var path: Array=[]
var elapsed: float=0
var redraw_clock: float=0
var colors: Dictionary={"lin":Color("70d9c1"),"xu":Color("f1bd72"),"su":Color("d296b3")}
func _ready() -> void:
	mouse_filter=Control.MOUSE_FILTER_STOP
	resized.connect(queue_redraw)
	mouse_exited.connect(func():hover=Vector2i(-1,-1);path=[];queue_redraw())
func _process(delta: float) -> void:
	elapsed+=delta;redraw_clock+=delta
	if redraw_clock>=0.033:
		redraw_clock=0;queue_redraw()
func geometry() -> Rect2:
	var side: float=minf(size.x,size.y)-32
	return Rect2((size-Vector2.ONE*side)/2,Vector2.ONE*side)
func _gui_input(event: InputEvent) -> void:
	var area:=geometry()
	if event is InputEventMouse:
		var local: Vector2=event.position-area.position
		var next:=Vector2i(floori(local.x/(area.size.x/8)),floori(local.y/(area.size.y/8)))
		if next.x<0 or next.x>7 or next.y<0 or next.y>7:next=Vector2i(-1,-1)
		if next!=hover:
			hover=next
			legal_hover=hover.x>=0 and validate_hover.is_valid() and validate_hover.call([hover.x,hover.y])
			tooltip_text=hover_description([hover.x,hover.y])
			path=route(state.battle,state.battle.heroes[selected].cell,[hover.x,hover.y]) if legal_hover else []
			queue_redraw()
		if event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_LEFT and hover.x>=0:
			cell_chosen.emit([hover.x,hover.y])
func center(cell: Array) -> Vector2:
	var area:=geometry()
	return area.position+(Vector2(float(cell[0]),float(cell[1]))+Vector2.ONE*.5)*(area.size.x/8)
static func route(battle: Dictionary,start: Array,target: Array) -> Array:
	start=[int(start[0]),int(start[1])];target=[int(target[0]),int(target[1])]
	if Rules.blocked(battle,target):return []
	var queue: Array=[[start,0]]
	var best: Dictionary={str(start):0}
	var routes: Dictionary={str(start):[start]}
	while not queue.is_empty():
		var entry: Array=queue.pop_front()
		for direction: Array in [[0,-1],[-1,0],[1,0],[0,1]]:
			var cell: Array=[int(entry[0][0])+direction[0],int(entry[0][1])+direction[1]]
			if Rules.blocked(battle,cell):continue
			var cost: int=int(entry[1])+(2 if Rules.terrain(battle,cell) in ["~",":"] else 1)
			if cost>=best.get(str(cell),999):continue
			best[str(cell)]=cost
			var steps: Array=routes[str(entry[0])].duplicate();steps.append(cell);routes[str(cell)]=steps
			queue.append([cell,cost])
	return routes.get(str(target),[])
func paint_sprite(index: int,at: Vector2,tile: float,tint: Color=Color.WHITE) -> void:
	paint_texture(Art.sprite(index),at,tile,tint)
func paint_texture(texture: Texture2D,at: Vector2,tile: float,tint: Color=Color.WHITE) -> void:
	draw_set_transform(at+Vector2(0,tile*.27),0,Vector2(1,.36))
	draw_circle(Vector2.ZERO,tile*.3,Color(0.02,.06,.08,.55))
	draw_set_transform(Vector2.ZERO)
	draw_texture_rect(texture,Rect2(at-Vector2.ONE*tile*.46,Vector2.ONE*tile*.92),false,tint)
func hero_position(hero: Dictionary) -> Vector2:
	if not animating() or not feedback.get("paths",{}).has(hero.id):return center(hero.cell)
	var point: Vector2=Feedback.step_position(feedback.paths[hero.id],Feedback.progress(feedback,seconds()))
	return geometry().position+(point+Vector2.ONE*.5)*(geometry().size.x/8)
func target_position() -> Vector2:
	var target: String=str(feedback.get("target",""))
	for group: Dictionary in [previous.get("enemies",{}),previous.get("objects",{}),previous.get("heroes",{})]:
		if group.has(target):return center(group[target].cell)
	var actor: String=str(feedback.get("actor",selected))
	return center(state.battle.heroes.get(actor,state.battle.heroes[selected]).cell)
func paint_actor(hero: Dictionary,at: Vector2,tile: float) -> void:
	var old: Dictionary=previous.get("heroes",{}).get(hero.id,hero)
	var moving: bool=animating() and feedback.get("paths",{}).has(hero.id) and Feedback.progress(feedback,seconds())<1
	var active: bool=animating() and feedback.actor==hero.id and feedback.kind!="end_round"
	var direction: Vector2=actor_facings.get(hero.id,Vector2.RIGHT)
	var frame: int=1
	var bob: float=sin(elapsed*2.3+float(hero.id.hash()%10))*.008
	var offset:=Vector2.ZERO
	if moving:
		direction=Feedback.direction(feedback.paths[hero.id],Feedback.progress(feedback,seconds()))
		frame=int(seconds()/.11)%4;bob=-absf(sin(seconds()*PI/.22))*.045
	elif active and feedback.kind not in ["wait","move","cross_anchor"]:
		direction=(target_position()-at).normalized()
		frame=4 if seconds()<impact() else 5
		var effort: float=sin(clampf(seconds()/maxf(.01,impact()),0,1)*PI*.5)
		if seconds()>impact():effort=maxf(0,1-(seconds()-impact())/.32)
		offset=direction*tile*.14*effort
	var tint:=Color.WHITE
	if animating() and hero.hp<old.hp and seconds()>=impact():
		var hit: float=seconds()-impact()
		offset.x+=sin(hit*70)*tile*.065*maxf(0,1-hit/.4)
		if int(hit*16)%2==0:tint=Color(1,.48,.4)
	var fade: float=1.0
	if hero.left and animating():fade=1-clampf((seconds()-impact())/.35,0,1)
	if hero.left and not animating():return
	tint.a=fade
	draw_set_transform(at+Vector2(0,tile*.3),0,Vector2(1,.32))
	draw_circle(Vector2.ZERO,tile*.27,Color(.02,.06,.08,.55*fade));draw_set_transform(Vector2.ZERO)
	var collapsed: bool=hero.downed and (not animating() or seconds()>=impact())
	if collapsed:
		paint_sprite(4,at+offset,tile,tint)
	else:
		var facing: float=-1 if direction.x<-.1 else 1
		# Vertical travel has a subtle body lean; horizontal corners change facing.
		draw_set_transform(at+offset+Vector2(0,bob*tile),direction.y*.04 if moving else 0,Vector2(facing,1))
		draw_texture_rect(Art.motion(hero.id,frame),Rect2(Vector2(-tile*.53,-tile*.62),Vector2.ONE*tile*1.06),false,tint)
		draw_set_transform(Vector2.ZERO)
	var held: String=hero.carrying
	if animating() and seconds()<impact():held=old.carrying
	if not held.is_empty():
		var object: Dictionary=state.battle.objects.get(held,previous.get("objects",{}).get(held,{}))
		var cargo: int=4 if object.get("kind","")=="rescue" else 22
		var carried_at:=at+offset+Vector2(-tile*.12,-tile*.02+bob*tile)
		if active and feedback.kind=="pickup" and seconds()>=impact():carried_at=(target_position()-Vector2.ONE*tile*.28).lerp(carried_at,clampf((seconds()-impact())/.25,0,1))
		draw_texture_rect(Art.rescue_marker(state.battle.mission_id,object) if object.get("kind","")=="rescue" else Art.sprite(cargo),Rect2(carried_at,Vector2.ONE*tile*.56),false,tint)
func floating_text(at: Vector2,text: String,color: Color,age: float,tile: float) -> void:
	if age<0 or age>.8:return
	color.a=1-clampf(age/.8,0,1)
	var font: Font=get_theme_default_font()
	var font_size: int=maxi(18,int(tile*.32))
	var pos:=at+Vector2(-font.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size).x/2,-tile*(.45+age*.5))
	draw_string_outline(font,pos,text,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size,5,Color(0,.06,.08,color.a))
	draw_string(font,pos,text,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size,color)
func draw_feedback(tile: float) -> void:
	if not animating():return
	var time: float=seconds()
	var age: float=time-impact()
	if feedback.kind=="end_round":
		for event: Dictionary in feedback.machines:
			var local: float=time-float(event.at)
			if local<0 or local>.5:continue
			var origin:=center(previous.enemies[event.id].cell)
			for cell: Array in event.cells:
				var point:=center(cell)
				var alpha: float=1-clampf(local/.5,0,1)
				draw_rect(Rect2(point-Vector2.ONE*tile*.43,Vector2.ONE*tile*.86),Color(1,.36,.18,alpha*.3))
				if local>=.18:draw_line(origin,point,Color(1,.64,.27,alpha),maxf(2,tile*.08*alpha),true)
				draw_arc(point,tile*(.12+local*.5),0,TAU,24,Color(1,.55,.27,alpha),2,true)
	elif age>=0 and age<.45:
		var at:=target_position()
		var tint:=Color("70d9c1") if feedback.kind in ["stabilize","extract","pickup","use_tool"] else Color("f1bd72")
		tint.a=1-age/.45
		if feedback.kind in ["attack","push","interact","protocol","specialty","service_watch","restore_power"]:
			for index: int in range(7):
				var ray:=Vector2.RIGHT.rotated(index*TAU/7)
				draw_line(at+ray*tile*(.08+age*.3),at+ray*tile*(.22+age*.55),tint,3,true)
		else:
			draw_arc(at,tile*(.15+age*.55),0,TAU,40,tint,3,true)
			if feedback.kind=="stabilize":
				draw_line(at-Vector2(tile*.12,0),at+Vector2(tile*.12,0),tint,4,true)
				draw_line(at-Vector2(0,tile*.12),at+Vector2(0,tile*.12),tint,4,true)
	for group_name: String in ["heroes","enemies"]:
		for id: String in state.battle[group_name]:
			if not previous.get(group_name,{}).has(id):continue
			var now: Dictionary=state.battle[group_name][id]
			var old: Dictionary=previous[group_name][id]
			var difference: int=int(now.hp)-int(old.hp)
			if difference!=0:floating_text(center(now.cell),("+" if difference>0 else "")+str(difference),Color("ef957d") if difference<0 else Color("70d9c1"),age,tile)
	for id: String in state.battle.objects:
		var now: Dictionary=state.battle.objects[id]
		var old: Dictionary=previous.get("objects",{}).get(id,now)
		var text: String=""
		if now.delivered and not old.delivered:text=I18n.t("feedback.delivered")
		elif now.stable and not old.stable:text=I18n.t("feedback.stable")
		elif now.completed and not old.completed:text=I18n.t("feedback.complete")
		elif now.progress>old.progress:text="+%d" % (now.progress-old.progress)
		if not text.is_empty():floating_text(target_position(),text,Color("70d9c1"),age,tile)
func _draw() -> void:
	if state.is_empty():return
	var b: Dictionary=state.battle
	var area:=geometry()
	var tile: float=area.size.x/8
	# Water surrounds the ferry; clinic gets an architectural surround.
	draw_texture_rect(Art.environment(board.location),Rect2(Vector2.ZERO,size),false,Color(.8,.86,.88))
	draw_rect(Rect2(Vector2.ZERO,size),Color(.015,.045,.065,.32))
	var landmark: Texture2D=Art.landmark(board.location)
	var landmark_size: float=minf(64,area.position.x-12)
	if landmark!=null and landmark_size>=28:draw_texture_rect(landmark,Rect2(Vector2(6,6),Vector2.ONE*landmark_size),false)
	draw_rect(area.grow(10),Color("0b2026"))
	draw_rect(area.grow(8),Color("827865"),false,3)
	# Decorative railings stay outside the interactive board footprint.
	if board.location=="ferry":
		for side: int in [-1,1]:
			var rail_x: float=area.get_center().x+side*(area.size.x*.5+17)
			draw_line(Vector2(rail_x,area.position.y),Vector2(rail_x,area.end.y),Color("839392"),2,true)
			for rung: int in range(9):
				var at:=Vector2(rail_x,area.position.y+rung*tile)
				draw_line(at-Vector2(4,0),at+Vector2(4,0),Color("b3b4a4"),3,true)
			var ring_at:=Vector2(rail_x+side*18,area.get_center().y)
			draw_arc(ring_at,11,0,TAU,32,Color("d68f58"),5,true)
	draw_texture_rect(Art.terrain(2 if board.location=="clinic" else 0),area,false,Color(.70,.79,.80))
	for y: int in range(8):
		for x: int in range(8):
			var cell: Array=[x,y]
			var at:=center(cell)
			var rect:=Rect2(at-Vector2.ONE*tile*.5,Vector2.ONE*tile)
			var terrain: String=b.rows[y].substr(x,1)
			var texture: int=2 if board.location=="clinic" else 0
			if terrain in ["X","~"]:texture=1
			elif terrain=="#":texture=3
			var tint:=Color(.85,.92,.94)
			if terrain=="X":tint=Color(.38,.53,.59)
			if terrain in ["X","~","#"]:draw_texture_rect(Art.terrain(texture),rect,false,tint)
			draw_rect(rect,Color(.55,.69,.68,.18),false,1)
			if terrain in ["X","~"]:
				for wave: int in range(2):
					var points:=PackedVector2Array()
					for step: int in range(9):points.append(at+Vector2((float(step)/8-.5)*tile*.8,(wave-.5)*tile*.32+sin(step*.65+elapsed+y)*tile*.035))
					draw_polyline(points,Color(.5,.77,.78,.25),1.2,true)
			if terrain==":":
				for rock: Vector2 in [Vector2(-.2,.1),Vector2(.1,-.2),Vector2(.25,.2)]:draw_circle(at+rock*tile,tile*.1,Color("7f7466"))
			if Rules.contains_cell(reachable,cell):
				draw_rect(rect.grow(-2),Color(.35,.87,.75,.13))
				draw_circle(at,tile*.035,Color(.55,.95,.82,.65))
			if Rules.contains_cell(b.get("exits",board.exits),cell):
				draw_rect(rect.grow(-3),Color("70d9c1"),false,2)
				draw_line(at+Vector2(tile*.2,0),at-Vector2(tile*.2,0),Color("70d9c1"),3)
				draw_polyline(PackedVector2Array([at+Vector2(-tile*.04,-tile*.13),at-Vector2(tile*.2,0),at+Vector2(-tile*.04,tile*.13)]),Color("70d9c1"),3,true)
	for cell: Array in Rules.Field.posts(b):
		var at: Vector2=center(cell)
		draw_arc(at,tile*.35,0,TAU,24,Color("e8ca8a"),2,true)
		draw_string(ThemeDB.fallback_font,at+Vector2(-tile*.13,tile*.07),"站",HORIZONTAL_ALIGNMENT_LEFT,-1,int(tile*.22),Color("e8ca8a"))
	var fire: Dictionary=b.get("environment",board.environment).fire_pulse
	if b.round>=int(fire.round)-1 and b.round<int(fire.round)+int(fire.duration_rounds):
		for cell: Array in fire.cells:
			var at:=center(cell)
			draw_rect(Rect2(at-Vector2.ONE*tile*.48,Vector2.ONE*tile*.96),Color(1,.35,.08,.2))
			for flame: int in range(4):
				var base:=at+Vector2((flame-1.5)*tile*.16,tile*.22)
				var height: float=tile*(.2+.09*sin(elapsed*7+flame))
				draw_colored_polygon(PackedVector2Array([base-Vector2(tile*.1,0),base-Vector2(0,height),base+Vector2(tile*.1,0)]),Color(1,.53,.13,.7))
	var forecast: Dictionary=previous if animating() and feedback.kind=="end_round" else b
	for id: String in forecast.intents:
		var enemy: Dictionary=forecast.enemies[id]
		if enemy.hp<=0 or enemy.disabled:continue
		if enemy.get("paused_round",0)==forecast.round:continue
		if enemy.type in ["welder","sentinel"] and int(forecast.round)%2==1:
			draw_arc(center(enemy.cell),tile*.4,0,TAU,32,Color("edc785"),2,true)
		for cell: Array in Rules.Hazards.footprint(forecast,enemy,Rules):
			var at:=center(cell)
			draw_rect(Rect2(at-Vector2.ONE*tile*.46,Vector2.ONE*tile*.92),Color(1,.28,.15,.17+.04*sin(elapsed*3)))
			draw_polyline(PackedVector2Array([at+Vector2(-tile*.16,-tile*.1),at+Vector2(0,tile*.06),at+Vector2(tile*.16,-tile*.1)]),Color("ed957a"),2,true)
	for barrier: Dictionary in b.get("barriers",{}).values():
		draw_rect(Rect2(center(barrier.cell)-Vector2.ONE*tile*.3,Vector2.ONE*tile*.6),Color("ceaa65"),false,4)
	for cell: Array in b.get("insulation",[]):
		draw_rect(Rect2(center(cell)-Vector2.ONE*tile*.4,Vector2.ONE*tile*.8),Color("89dbb7"),false,2)
	for pending: Dictionary in b.queued_reinforcements:
		draw_arc(center(pending.cell),tile*.42,0,TAU,32,Color("f08e69"),3,true)
	if path.size()>1:
		var points:=PackedVector2Array()
		for cell: Array in path:points.append(center(cell))
		draw_polyline(points,Color("a1f2d5"),3,true)
	for current_object: Dictionary in b.objects.values():
		var object: Dictionary=previous.get("objects",{}).get(current_object.id,current_object) if animating() and seconds()<impact() else current_object
		if object.delivered or not object.carrier.is_empty():continue
		var at:=center(object.cell)
		if animating() and object.kind=="convoy":
			var old: Dictionary=previous.get("objects",{}).get(object.id,object)
			at=center(old.cell).lerp(at,clampf((seconds()-impact())/.4,0,1))
		var tint:=Color(.5,.5,.5,.7) if object.lost else Color.WHITE
		var index: int=4 if object.kind=="rescue" else (7 if object.has("disables") else (6 if object.kind=="cargo" else 8))
		if board.location=="clinic":
			if object.id=="power" or object.id=="spare":index=5
			elif object.id=="cut":index=7
		if object.kind=="convoy":index=46
		elif object.kind=="channel":index=47
		elif object.kind=="cargo":index=22
		elif object.kind=="work":
			index=23 if object.has("disables") else 25
			if object.id.begins_with("brace") or object.id=="rail":index=20
			elif object.id in ["pump","engine"]:index=21
			elif object.id=="door":index=24
		if object.kind=="rescue":paint_texture(Art.rescue_marker(b.mission_id,object),at,tile,tint)
		else:paint_sprite(index,at,tile,tint)
		if object.completed or object.stable:draw_circle(at+Vector2(tile*.32,-tile*.31),tile*.055,Color("70d9c1"))
	for enemy: Dictionary in b.enemies.values():
		var old: Dictionary=previous.get("enemies",{}).get(enemy.id,enemy)
		var age: float=seconds()-changed_enemy_at(enemy.id)
		if enemy.hp<=0 and (not animating() or age>.42):continue
		var at:=center(enemy.cell)
		var tint:=Color(.5,.6,.6) if enemy.disabled else Color.WHITE
		if animating():
			at=center(old.cell).lerp(at,clampf(age/.3,0,1))
			if enemy.hp<old.hp and age>=0:
				at.x+=sin(age*65)*tile*.06*maxf(0,1-age/.4)
				tint=Color(1,.53,.4) if int(age*18)%2==0 else Color.WHITE
			if enemy.hp<=0:tint.a=1-clampf(age/.42,0,1)
		paint_sprite({"welder":30,"hauler":31,"skimmer":32,"relay":44,"sentinel":45}.get(enemy.type,3),at,tile,tint)
	for hero: Dictionary in b.heroes.values():
		if hero.left and not animating():continue
		var at:=hero_position(hero)
		var ink: Color=colors.get(hero.id,Color("ccd5d2"))
		if not hero.left:draw_arc(at+Vector2(0,tile*.28),tile*.33,0,TAU,36,ink,3 if hero.id==selected else 1,true)
		paint_actor(hero,at,tile)
		for ap: int in range(int(hero.ap)):draw_circle(at+Vector2((ap-(float(hero.ap)-1)/2)*tile*.14,tile*.47),tile*.035,ink)
	draw_feedback(tile)
	if not hint_cell.is_empty() and not animating():
		var at:=center(hint_cell)
		draw_rect(Rect2(at-Vector2.ONE*tile*.45,Vector2.ONE*tile*.9),Color(.9,.8,.5,.65+.25*sin(elapsed*4)),false,3)
	if hover.x>=0:
		var at:=center([hover.x,hover.y])
		draw_rect(Rect2(at-Vector2.ONE*tile*.47,Vector2.ONE*tile*.94),Color("a5edcf") if legal_hover else Color("cdbd99"),false,2)

func hover_description(cell: Array) -> String:
	var lines: Array[String]=[]
	for hero: Dictionary in state.battle.heroes.values():
		if not hero.left and Rules.same(hero.cell,cell):
			lines.append(I18n.content("characters",hero.id,"name",I18n.t("visual.support")))
	for object: Dictionary in state.battle.objects.values():
		if not object.delivered and object.carrier.is_empty() and Rules.same(object.cell,cell):
			lines.append(I18n.content("objects",state.battle.mission_id+"."+object.id,"label",I18n.t("visual.casualty")))
	for enemy: Dictionary in state.battle.enemies.values():
		if enemy.hp>0 and Rules.same(enemy.cell,cell):lines.append(I18n.t("visual.machine"))
	return "\n".join(lines)
