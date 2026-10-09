extends SceneTree
var route
var output := ""
var rows: Array = []
var errors: Array[String] = []
var subjects: Dictionary = {}
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 root.show()
 create_timer(120).timeout.connect(func():push_error("TUBI_OPTIONS_TIMEOUT");quit(1))
 call_deferred("run")
func settle() -> void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
 RenderingServer.force_draw()
 await RenderingServer.frame_post_draw
func vertices(pattern: String) -> Array[Vector3]:
 var mesh=route.find_child(pattern,true,false) as MeshInstance3D
 assert(mesh!=null,pattern)
 var points: Array[Vector3]=[]
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
func capture(mode: String,variant: String,parameters: Dictionary) -> void:
 var image:=root.get_texture().get_image()
 var path:=output+"/%s-%s-%dx%d.png"%[mode,variant,image.get_width(),image.get_height()]
 assert(image.save_png(path)==OK)
 var measurements:Dictionary={}
 for name in subjects:measurements[name]=measure(subjects[name])
 rows.append({"mode":mode,"variant":variant,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"measurements":measurements,"parameters":parameters,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"action_scroll_height":route.action_scroll.custom_minimum_size.y,"site_bakes_enabled":route.site_bakes_enabled,"camera_transition_running":false})
func run() -> void:
 assert(output!="" and DisplayServer.get_name()!="headless")
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 subjects.hall=box(vertices("SITE_tubi-tang_MAT_rooftile"))+box(vertices("HERO_tubi_title*"))+box(vertices("SITE_tubi-tang_MAT_whitewash"))
 subjects.moon=vertices("SITE_stage_MAT_painted_moon")
 subjects.pavilion=box(vertices("SITE_qinfang-ting_MAT_pavilion_atlas"))
 subjects.stair=[]
 var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/source-contract.json"))
 for p in contract.colliders.COL_tubi_stair_ramp.faces:subjects.stair.append(Vector3(p[0],p[1],p[2]))
 route.player.position=Vector3(7,4.03,-31)
 for mode in ["normal","touch","density"]:
  var sizes=[Vector2i(1080,2340),Vector2i(945,2100)] if mode=="density" else [Vector2i(390,844),Vector2i(360,800)]
  for size in sizes:
   root.size=size;route._configure_ui_scale(mode!="normal",420 if mode=="density" else 160);await settle()
   route._arrive("tubi_tang",true);await settle()
   capture(mode,"arrival-baseline",{})
   # Explicit comparison policy: bound the portrait action list without shrinking touch targets.
   route.action_scroll.custom_minimum_size.y=minf(route.action_scroll.custom_minimum_size.y,128.0);await settle()
   var best:Dictionary={}
   var score:float=-INF
   for height in [6.0,8.0]:
    for depth in [-12.0,-8.0,-4.0]:
     for fov in [45.0,50.0,55.0,60.0,65.0,70.0]:
      for x in [3.0,5.0,7.0]:
       for y in [-11.1,-9.1,-7.1,-5.1,-3.1]:
        route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=fov
        route._camera_to(Vector3(16,height,depth),Vector3(x,y,-32),true)
        var h:=measure(subjects.hall);var m:=measure(subjects.moon);var stairs:=measure(subjects.stair)
        if not h.fits or not m.fits or not stairs.fits:continue
        if h.width_fraction>score:score=h.width_fraction;best={"fov":fov,"target":[x,y,-32],"position":[16,height,depth],"action_scroll_policy":128}
   if best.is_empty():errors.append("No arrival fit "+mode+str(size))
   else:
    route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=best.fov
    route._camera_to(Vector3(best.position[0],best.position[1],best.position[2]),Vector3(best.target[0],best.target[1],best.target[2]),true);await settle()
    capture(mode,"arrival-measured",best)
   route._arrive("tubi_tang",true);await settle()
   route.execute_command("overlook");await settle()
   capture(mode,"overlook-baseline",{})
   route.action_scroll.custom_minimum_size.y=minf(route.action_scroll.custom_minimum_size.y,128.0);await settle()
   for height in [8.0,10.0,12.0]:
    route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=45.0
    route._camera_to(Vector3(7,height,-30.5),Vector3(0,-1,0),true);await settle()
    capture(mode,"overlook-height-"+str(int(height)),{"position":[7,height,-30.5],"target":[0,-1,0],"fov":45,"action_scroll_policy":128})
 root.size=Vector2i(1410,600);route._configure_ui_scale(false,160);await settle()
 route._arrive("tubi_tang",true);await settle();route.execute_command("overlook");await settle();capture("desktop","overlook-baseline",{})
 for height in [8.0,10.0,12.0]:
  route.camera.keep_aspect=Camera3D.KEEP_HEIGHT;route.camera.fov=55.0
  route._camera_to(Vector3(7,height,-30.5),Vector3(0,1.2,0),true);await settle()
  capture("desktop","overlook-height-"+str(int(height)),{"position":[7,height,-30.5],"target":[0,1.2,0],"fov":55})
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"options_complete_visual_review_pending" if errors.is_empty() else "options_rejected","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("res://tests/tubi_framing_options.gd"),"errors":errors,"rows":rows,"scope":"Isolated manual camera and 128-unit action-scroll comparison. Normal/touch/host-clamped desktop-density originals. Full hall/moon/stair fit candidates and three higher overlooks; projection does not prove visibility. No product changes or phone/final-art acceptance."}," ")+"\n");file.close()
 print("TUBI_OPTIONS_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
