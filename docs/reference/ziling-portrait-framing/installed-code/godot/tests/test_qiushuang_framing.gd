extends SceneTree

const SOURCE := "26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38"
var route
var output := ""
var errors: Array[String] = []
var rows: Array = []
var hall: Array[Vector3] = []
var banks: Dictionary = {}
var touch := false
var density := false

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg=="--touch":touch=true
  if arg=="--density":density=true;touch=true
 if DisplayServer.get_name()!="headless":root.show()
 create_timer(120).timeout.connect(func():push_error("QIUSHUANG_FRAMING_REJECTED: Native deadline exceeded");quit(1))
 call_deferred("run")

func check(ok: bool,message: String) -> void:
 if not ok:errors.append(message);push_error("QIUSHUANG_FRAMING_REJECTED: "+message)

func settle() -> void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 check(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(),"Camera tween timeout")
 RenderingServer.force_draw()
 await RenderingServer.frame_post_draw

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
 var measurement:=measure(hall if subject=="arrival" else banks[subject])
 if portrait:
  check(route.camera.keep_aspect==Camera3D.KEEP_WIDTH,"Portrait projection: "+phase)
  check(measurement.fits,"Subject clipped or covered: "+phase)
  check(measurement.width_fraction>=.7,"Subject too small: "+phase)
 var image:=root.get_texture().get_image()
 var path:=output+"/"+phase+".png"
 check(image.save_png(path)==OK,"Cannot save original "+phase)
 rows.append({"phase":phase,"subject":subject,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"measurement":measurement,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"action_scroll_height":route.action_scroll.custom_minimum_size.y,"camera_transition_running":false,"text":route.output_label.text})

func desktop_pose(action: String) -> void:
 var x:float={"left":18.85,"centre":22.0,"right":25.15}.get(action,22.0)
 var position:=Vector3(22,3.2,-6.8) if action=="arrival" else Vector3(x,1.7,-12.7)
 var target:=Vector3(22,1.45,-15.5) if action=="arrival" else Vector3(x,1.35,-15.6)
 var expected:=Transform3D(Basis.IDENTITY,position).looking_at(target,Vector3.UP)
 check(route.camera.transform.is_equal_approx(expected) and is_equal_approx(route.camera.fov,55.0) and route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Original desktop pose not restored: "+action)

func run() -> void:
 if DisplayServer.get_name()=="headless" or output=="":push_error("Native renderer and output folder required");quit(1);return
 DirAccess.make_dir_recursive_absolute(output)
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE,"Subject source mismatch")
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 check(route.site_bakes_enabled,"Matching lighting disabled")
 # Project actual vertices: a whole-batch AABB invents roof corners that do not exist.
 for material in ["rooftile","whitewash","tech_atlas"]:hall.append_array(vertices("SITE_qiushuang-zhai_MAT_"+material))
 check(hall.size()==30987,"Imported facade vertex inventory changed")
 var tech:=vertices("SITE_qiushuang-zhai_MAT_tech_atlas")
 for action in ["left","centre","right"]:
  var x:float={"left":18.85,"centre":22.0,"right":25.15}[action]
  var selected: Array[Vector3]=[]
  # Source racks span x ±.85, start above .65 and lie behind the desk at z -15.33.
  # Each selected region encloses the complete 2×2 monitor rack and lattice front.
  for p in tech:
   if absf(p.x-x)<.85 and p.y>.65 and p.z<-15.33:selected.append(p)
  check(selected.size()>64,"Empty monitor rack: "+action)
  banks[action]=box(selected)
 var portrait_size:=Vector2i(1080,2340) if density else Vector2i(390,844)
 var narrow_size:=Vector2i(945,2100) if density else Vector2i(360,800)
 var desktop_size:=Vector2i(2340,1080) if density else Vector2i(1410,600)
 root.size=portrait_size;route._configure_ui_scale(touch,420 if density else 160);await settle()
 route.player.position=Vector3(22,.03,-13.5);route._arrive("qiushuang_zhai",true);await settle()
 var visitor:Vector3=route.player.position
 inspect("arrival-portrait","arrival",true)
 root.size=narrow_size;await settle();inspect("arrival-narrow","arrival",true)
 root.size=desktop_size;await settle();desktop_pose("arrival");inspect("arrival-desktop","arrival",false)
 root.size=portrait_size;await settle();inspect("arrival-return","arrival",true)
 for action in ["left","centre","right"]:
  press({"left":"Left screens","centre":"Centre screens","right":"Right screens"}[action]);await settle()
  var text:String=route.output_label.text
  inspect(action+"-portrait",action,true)
  root.size=narrow_size;await settle();inspect(action+"-narrow",action,true)
  check(route.output_label.text==text,"Resize replaced bank text: "+action)
  root.size=desktop_size;await settle();desktop_pose(action);inspect(action+"-desktop",action,false)
  root.size=portrait_size;await settle();inspect(action+"-return",action,true)
  check(route.output_label.text==text,"Rotation replaced bank text: "+action)
 var selected_pose:Transform3D=route.camera.transform
 press("Look");await settle();inspect("look-portrait","arrival",true)
 check(not route.camera.transform.is_equal_approx(selected_pose),"Look did not leave the selected bank")
 check(route.output_label.text==route.ROOMS.qiushuang_zhai.text,"Look did not restore arrival text")
 root.size=narrow_size;await settle();inspect("look-narrow","arrival",true)
 check(route.player.position.distance_to(visitor)<.005 and route.room_id=="qiushuang_zhai","Camera actions moved visitor or changed room")
 if touch:
  check(route.input.size.y>=48,"Touch input smaller than 48 logical units")
  for button in route.actions.get_children():check(button.size.y>=48,"Touch action smaller than 48 logical units")
  route.action_scroll.scroll_vertical=10000;await settle()
  var last=route.actions.get_child(route.actions.get_child_count()-1) as Button
  check(route.action_scroll.get_global_rect().encloses(last.get_global_rect()),"Last bulletin action unreachable by scrolling")
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"qiushuang_framing_passed" if errors.is_empty() else "rejected","source_glb_sha256":SOURCE,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256("res://tests/test_qiushuang_framing.gd"),"touch":touch,"density":density,"facade_vertex_count":hall.size(),"errors":errors,"rows":rows,"scope":"Actual arrival and public Left/Centre/Right screens/Look with completed tweens; actual imported facade vertices and complete four-monitor rack bounds above measured UI; resize/rotation/text/visitor invariants, original desktop poses, touch targets and last-action scroll reachability. Projection does not prove visibility or text readability. Desktop density windows may be host-clamped. Not physical-phone or final-art acceptance."}," ")+"\n");file.close()
 print("QIUSHUANG_FRAMING_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
