extends SceneTree

const SOURCE := "c9d4fb308730733af2175c424449f8a63b731674d2527df2168a260cc0f5013e"
var route
var output := ""
var errors: Array[String] = []
var rows: Array = []
var hall: Array[Vector3] = []
var subjects: Dictionary = {}
var touch := false
var density := false

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg=="--touch":touch=true
  if arg=="--density":density=true;touch=true
 if DisplayServer.get_name()!="headless":root.show()
 create_timer(120).timeout.connect(func():push_error("YIHONG_FRAMING_REJECTED: Native deadline exceeded");quit(1))
 call_deferred("run")

func check(ok: bool,message: String) -> void:
 if not ok:errors.append(message);push_error("YIHONG_FRAMING_REJECTED: "+message)

func settle() -> void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 check(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(),"Camera tween timeout")
 var drawn := [false]
 RenderingServer.frame_post_draw.connect(func():drawn[0]=true,CONNECT_ONE_SHOT)
 RenderingServer.force_draw()
 var draw_deadline:=Time.get_ticks_msec()+10000
 while not drawn[0] and Time.get_ticks_msec()<draw_deadline:await process_frame
 check(drawn[0],"Native draw deadline")

func press(label: String) -> void:
 for button in route.actions.get_children():
  if button is Button and button.text==label:
   check(not button.disabled,"Disabled public action "+label)
   button.pressed.emit()
   return
 check(false,"Missing public action "+label)

func vertices(pattern: String) -> Array[Vector3]:
 var mesh=route.find_child(pattern,true,false) as MeshInstance3D
 check(mesh!=null,"Missing subject "+pattern)
 var points: Array[Vector3]=[]
 if mesh==null:return points
 for surface in range(mesh.mesh.get_surface_count()):
  for p in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:points.append(mesh.global_transform*p)
 return points

func box(points: Array[Vector3]) -> Array[Vector3]:
 var low:=Vector3(INF,INF,INF)
 var high:=Vector3(-INF,-INF,-INF)
 for p in points:low=low.min(p);high=high.max(p)
 var result: Array[Vector3]=[]
 for x in [low.x,high.x]:
  for y in [low.y,high.y]:
   for z in [low.z,high.z]:result.append(Vector3(x,y,z))
 return result

func measure(points: Array) -> Dictionary:
 var low:=Vector2(INF,INF)
 var high:=Vector2(-INF,-INF)
 var behind:=0
 for p in points:
  if route.camera.is_position_behind(p):behind+=1
  var pixel:Vector2=route.camera.unproject_position(p)
  low=low.min(pixel);high=high.max(pixel)
 var size:Vector2=root.get_visible_rect().size
 var header:Rect2=route.status.get_global_rect()
 var panel:Rect2=route.command_panel.get_global_rect()
 return {"low":[low.x,low.y],"high":[high.x,high.y],"width_fraction":(high.x-low.x)/size.x,"fits":behind==0 and low.x>=12 and high.x<=size.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14,"behind":behind,"header_bottom":header.end.y,"panel_top":panel.position.y}

func inspect(phase: String,subject: String,portrait: bool) -> void:
 var measurement:=measure(hall if subject=="arrival" else subjects[subject])
 if portrait:
  check(route.camera.keep_aspect==Camera3D.KEEP_WIDTH,"Portrait projection: "+phase)
  check(measurement.fits,"Subject clipped or covered: "+phase)
  check(measurement.width_fraction>=(.65 if subject=="arrival" else .5),"Subject too small: "+phase)
 var image:=root.get_texture().get_image()
 var path:=output+"/"+phase+".png"
 check(image.save_png(path)==OK,"Cannot save original "+phase)
 rows.append({"phase":phase,"subject":subject,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"measurement":measurement,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"action_scroll_height":route.action_scroll.custom_minimum_size.y,"camera_transition_running":false,"text":route.output_label.text})

func desktop_pose(action: String) -> void:
 var position:Vector3={"arrival":Vector3(18,3.1,5),"doors":Vector3(22.2,1.65,1),"leaves":Vector3(21.5,2.3,.5)}[action]
 var target:Vector3={"arrival":Vector3(24.3,1.25,1),"doors":Vector3(25,1.4,1),"leaves":Vector3(23.65,1.7,-1.45)}[action]
 var expected:=Transform3D(Basis.IDENTITY,position).looking_at(target,Vector3.UP)
 check(route.camera.transform.is_equal_approx(expected) and is_equal_approx(route.camera.fov,55.0) and route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Original desktop pose not restored: "+action)

func run() -> void:
 if DisplayServer.get_name()=="headless" or output=="":push_error("Native renderer and output folder required");quit(1);return
 DirAccess.make_dir_recursive_absolute(output)
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE,"Subject source mismatch")
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 check(route.site_bakes_enabled,"Matching lighting disabled")
 for material in ["rooftile","yihong_lacquer","lattice_wood","crt_amber"]:hall.append_array(vertices("SITE_yihong-yuan_MAT_"+material))
 check(hall.size()==2744,"Imported courtyard facade inventory changed")
 var mesh=route.find_child("SITE_yihong-yuan_MAT_yihong_lacquer",true,false) as MeshInstance3D
 var doors:Array[Vector3]=[]
 for surface in range(mesh.mesh.get_surface_count()):
  for p in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
   # Two original closed-door cubes: local x ±.945, height .1..2.1, front z .09..23.
   if absf(p.x)<=.946 and p.y>=.099 and p.y<=2.101 and p.z>=.089 and p.z<=.231:doors.append(mesh.global_transform*p)
 check(doors.size()==48,"Both complete closed-door inventories required")
 subjects.doors=doors
 var portrait_size:=Vector2i(1080,2340) if density else Vector2i(390,844)
 var narrow_size:=Vector2i(945,2100) if density else Vector2i(360,800)
 var desktop_size:=Vector2i(2340,1080) if density else Vector2i(1410,600)
 root.size=portrait_size;route._configure_ui_scale(touch,420 if density else 160);await settle()
 route.player.position=route.RED_COURT_PATH[-1]+Vector3(0,.03,0)
 route._arrive("yihong_yuan",true);await settle()
 var visitor:Vector3=route.player.position
 # The selected banana is actual runtime geometry, including its active LOD.
 subjects.leaves=vertices("HERO_flora_yihong_yuan_4_001")
 check(subjects.leaves.size()>100,"Missing complete selected banana")
 inspect("arrival-portrait","arrival",true)
 var arrival:Transform3D=route.camera.transform
 root.size=narrow_size;await settle();inspect("arrival-narrow","arrival",true)
 root.size=desktop_size;await settle();desktop_pose("arrival");inspect("arrival-desktop","arrival",false)
 root.size=portrait_size;await settle();inspect("arrival-return","arrival",true)
 for action in ["doors","leaves"]:
  press("Inspect the doors" if action=="doors" else "Banana leaves");await settle()
  if action=="leaves":subjects.leaves=vertices("HERO_flora_yihong_yuan_4_001")
  var text:String=route.output_label.text
  inspect(action+"-portrait",action,true)
  root.size=narrow_size;await settle();inspect(action+"-narrow",action,true)
  check(route.output_label.text==text,"Resize replaced selected text: "+action)
  root.size=desktop_size;await settle();desktop_pose(action);inspect(action+"-desktop",action,false)
  root.size=portrait_size;await settle();inspect(action+"-return",action,true)
  check(route.output_label.text==text,"Rotation replaced selected text: "+action)
  var selected:Transform3D=route.camera.transform
  press("Look");await settle();inspect(action+"-look","arrival",true)
  check(not route.camera.transform.is_equal_approx(selected),"Look did not leave selected "+action)
  check(route.camera.transform.is_equal_approx(arrival),"Look did not restore original portrait overview after "+action)
  check(route.output_label.text==route.ROOMS.yihong_yuan.text,"Look did not restore arrival text")
 root.size=narrow_size;await settle();inspect("look-narrow","arrival",true)
 check(route.player.position.distance_to(visitor)<.005 and route.room_id=="yihong_yuan","Camera actions moved visitor or changed room")
 check(route.action_scroll.custom_minimum_size.y<=152,"Portrait actions consume too much scene space")
 if touch:
  check(route.input.size.y>=48,"Touch input smaller than 48 logical units")
  for button in route.actions.get_children():check(button.size.y>=48,"Touch action smaller than 48 logical units")
  route.action_scroll.scroll_vertical=10000;await settle()
  var last=route.actions.get_child(route.actions.get_child_count()-1) as Button
  check(route.action_scroll.get_global_rect().encloses(last.get_global_rect()),"Last courtyard action unreachable by scrolling")
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"yihong_framing_passed" if errors.is_empty() else "rejected","source_glb_sha256":SOURCE,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256("res://tests/test_yihong_framing.gd"),"touch":touch,"density":density,"facade_vertex_count":hall.size(),"closed_door_vertex_count":doors.size(),"errors":errors,"rows":rows,"scope":"Actual arrival and public Inspect the doors/Banana leaves/Look with completed tweens; actual imported facade and closed-door vertices above measured UI; selected primary banana silhouette at its actual runtime LOD. Resize/rotation/text/visitor invariants, original desktop poses, touch targets and last-action scrolling. Projection does not prove visible pixels or foliage surface quality. Density windows may be host-clamped. Not physical-phone or final-art acceptance."}," ")+"\n");file.close()
 print("YIHONG_FRAMING_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
