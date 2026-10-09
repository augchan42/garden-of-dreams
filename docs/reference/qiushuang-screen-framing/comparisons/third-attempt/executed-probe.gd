extends SceneTree
var route
var output := ""
var rows: Array = []
var errors: Array[String] = []
var hall: Array[Vector3]=[]
var banks:Dictionary={}
var hall_native:Array[Vector3]=[]
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 root.show()
 create_timer(150).timeout.connect(func():push_error("QIUSHUANG_PROBE_TIMEOUT");quit(1))
 call_deferred("run")
func settle() -> void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
 RenderingServer.force_draw();await RenderingServer.frame_post_draw
func vertices(name:String) -> Array[Vector3]:
 var mesh=route.find_child(name,true,false) as MeshInstance3D
 assert(mesh!=null,name)
 var points:Array[Vector3]=[]
 for surface in range(mesh.mesh.get_surface_count()):
  for p in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:points.append(mesh.global_transform*p)
 return points
func box(points:Array[Vector3]) -> Array[Vector3]:
 var low:=Vector3(INF,INF,INF);var high:=Vector3(-INF,-INF,-INF)
 for p in points:low=low.min(p);high=high.max(p)
 var result:Array[Vector3]=[]
 for x in [low.x,high.x]:
  for y in [low.y,high.y]:
   for z in [low.z,high.z]:result.append(Vector3(x,y,z))
 return result
func measure(points:Array) -> Dictionary:
 var low:=Vector2(INF,INF);var high:=Vector2(-INF,-INF);var behind:=0
 for p in points:
  if route.camera.is_position_behind(p):behind+=1
  var pixel:Vector2=route.camera.unproject_position(p);low=low.min(pixel);high=high.max(pixel)
 var size:Vector2=root.get_visible_rect().size;var header:Rect2=route.status.get_global_rect();var panel:Rect2=route.command_panel.get_global_rect()
 return {"low":[low.x,low.y],"high":[high.x,high.y],"width_fraction":(high.x-low.x)/size.x,"fits":behind==0 and low.x>=12 and high.x<=size.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14,"behind":behind,"header_bottom":header.end.y,"panel_top":panel.position.y}
func capture(mode:String,action:String,variant:String,points:Array,parameters:Dictionary) -> void:
 var image:=root.get_texture().get_image();var path:=output+"/%s-%s-%s-%dx%d.png"%[mode,action,variant,image.get_width(),image.get_height()]
 assert(image.save_png(path)==OK)
 rows.append({"mode":mode,"action":action,"variant":variant,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"measurement":measure(points),"actual_vertex_measurement":measure(hall_native) if action=="arrival" else {},"parameters":parameters,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"action_scroll_height":route.action_scroll.custom_minimum_size.y,"site_bakes_enabled":route.site_bakes_enabled,"camera_transition_running":false})
func reserve() -> void:
 route.action_scroll.custom_minimum_size.y=128
 route.command_panel.offset_top=-195
 await settle()
func run() -> void:
 assert(output!="" and DisplayServer.get_name()!="headless")
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route);await settle()
 hall_native=vertices("SITE_qiushuang-zhai_MAT_rooftile")+vertices("SITE_qiushuang-zhai_MAT_whitewash")+vertices("SITE_qiushuang-zhai_MAT_tech_atlas")
 var hull:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/qiushuang-hull.json"))
 assert(hull.source_glb_sha256==FileAccess.get_sha256("res://assets/garden-of-dreams.glb"))
 for p in hull.hall_hull:hall.append(Vector3(p[0],p[1],p[2]))
 var tech:=vertices("SITE_qiushuang-zhai_MAT_tech_atlas")
 for action in ["left","centre","right"]:
  var x:float={"left":18.85,"centre":22.0,"right":25.15}[action]
  var points:Array[Vector3]=[]
  for p in tech:
   if absf(p.x-x)<.85 and p.y>.65 and p.z<-15.33:points.append(p)
  assert(points.size()>64,action)
  banks[action]=box(points)
 route.player.position=Vector3(22,.03,-13.5)
 for mode in ["normal","touch","density"]:
  var sizes=[Vector2i(1080,2340),Vector2i(945,2100)] if mode=="density" else [Vector2i(390,844),Vector2i(360,800)]
  for size in sizes:
   root.size=size;route._configure_ui_scale(mode!="normal",420 if mode=="density" else 160);await settle()
   route._arrive("qiushuang_zhai",true);await settle();capture(mode,"arrival","baseline",hall,{})
   await reserve()
   var best:Dictionary={};var score:float=-INF
   for depth in [-6.8,-4.8,-2.8]:
    for fov in [55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0]:
     for y in [-6.0,-5.0,-4.0,-3.0,-2.0,-1.0,0.0]:
      route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=fov;route._camera_to(Vector3(22,3.2,depth),Vector3(22,y,-15.5),true)
      var m:=measure(hall)
      var candidate_score:float=m.width_fraction-(m.low[1]-m.header_bottom-12)/root.get_visible_rect().size.y*.4
      if m.fits and candidate_score>score:score=candidate_score;best={"fov":fov,"target":[22,y,-15.5],"position":[22,3.2,depth],"action_scroll_policy":128}
   if best.is_empty():errors.append("No arrival fit "+mode+str(size))
   else:
    route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=best.fov;route._camera_to(Vector3(best.position[0],best.position[1],best.position[2]),Vector3(best.target[0],best.target[1],best.target[2]),true);await settle();capture(mode,"arrival","measured",hall,best)
   for action in ["left","centre","right"]:
    route._arrive("qiushuang_zhai",true);await settle();route.execute_command(action);await settle();capture(mode,action,"baseline",banks[action],{})
    await reserve()
    best={};score=-INF
    var x:float={"left":18.85,"centre":22.0,"right":25.15}[action]
    for fov in [40.0,45.0,50.0,55.0,60.0]:
     for y in [.25,.5,.75,1.0,1.25]:
      route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=fov;route._camera_to(Vector3(x,1.7,-12.7),Vector3(x,y,-15.6),true)
      var m:=measure(banks[action])
      if m.fits and m.width_fraction>score:score=m.width_fraction;best={"fov":fov,"target":[x,y,-15.6],"position":[x,1.7,-12.7],"action_scroll_policy":128}
    if best.is_empty():errors.append("No bank fit "+action+mode+str(size))
    else:
     route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=best.fov;route._camera_to(Vector3(x,1.7,-12.7),Vector3(best.target[0],best.target[1],best.target[2]),true);await settle();capture(mode,action,"measured",banks[action],best)
 root.size=Vector2i(1410,600);route._configure_ui_scale(false,160);await settle()
 route._arrive("qiushuang_zhai",true);await settle();capture("desktop","arrival","baseline",hall,{})
 for action in ["left","centre","right"]:
  route.execute_command(action);await settle();capture("desktop",action,"baseline",banks[action],{})
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"comparison_complete_visual_review_pending" if errors.is_empty() else "comparison_rejected","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("res://tests/compare_qiushuang.gd"),"errors":errors,"rows":rows,"scope":"Isolated arrival and all three bank comparisons using imported roof/wall/tech bounds and bank-region points, above actual UI. Manual 128-unit scroll reserve and panel reset for candidates. No product changes; projection alone cannot establish visible individual monitors. Desktop-density windows may be clamped; no phone/final-art acceptance."}," ")+"\n");file.close()
 print("QIUSHUANG_COMPARISON_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
