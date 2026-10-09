extends SceneTree
var route
var output := ""
var rows: Array = []
var errors: Array[String] = []
var hall: Array[Vector3] = []
var moon: Array[Vector3] = []
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 root.show()
 create_timer(100).timeout.connect(func():push_error("TUBI_PROBE_TIMEOUT");quit(1))
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
func measure(points: Array[Vector3]) -> Dictionary:
 var low:=Vector2(INF,INF)
 var high:=Vector2(-INF,-INF)
 var behind:=0
 for p in points:
  if route.camera.is_position_behind(p):behind+=1
  var pixel:Vector2=route.camera.unproject_position(p)
  low=low.min(pixel);high=high.max(pixel)
 var visible:Vector2=root.get_visible_rect().size
 var header:Rect2=route.status.get_global_rect()
 var panel:Rect2=route.command_panel.get_global_rect()
 return {"low":[low.x,low.y],"high":[high.x,high.y],"width_fraction":(high.x-low.x)/visible.x,"fits":behind==0 and low.x>=12 and high.x<=visible.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14,"header_bottom":header.end.y,"panel_top":panel.position.y,"behind":behind}
func capture(variant: String,parameters: Dictionary) -> void:
 var size:Vector2i=root.size
 var image:=root.get_texture().get_image()
 var path:=output+"/%s-%dx%d.png"%[variant,size.x,size.y]
 assert(image.save_png(path)==OK)
 rows.append({"variant":variant,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"hall":measure(hall),"moon":measure(moon),"parameters":parameters,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"text":route.output_label.text,"site_bakes_enabled":route.site_bakes_enabled,"camera_transition_running":false})
func run() -> void:
 assert(output!="" and DisplayServer.get_name()!="headless")
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 hall=box(vertices("SITE_tubi-tang_MAT_rooftile"))+box(vertices("HERO_tubi_title*"))+box(vertices("SITE_tubi-tang_MAT_whitewash"))
 moon=vertices("SITE_stage_MAT_painted_moon")
 route.player.position=Vector3(7,4.03,-31)
 for size in [Vector2i(390,844),Vector2i(360,800),Vector2i(1410,600)]:
  root.size=size;route._configure_ui_scale(false,160);await settle()
  route._arrive("tubi_tang",true);await settle()
  capture("arrival-baseline",{})
  if size.x<size.y:
   var best:Dictionary={}
   var score:float=-INF
   for fov in [45.0,50.0,55.0,60.0,65.0]:
    for x_shift in [-6.0,-4.0,-2.0,0.0,2.0]:
     for y_shift in [-2.0,-1.0,0.0,1.0,2.0]:
      var target:=Vector3(7+x_shift,4.9+y_shift,-32)
      route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=fov
      route._camera_to(Vector3(16,10,-20),target,true)
      var h:=measure(hall);var m:=measure(moon)
      if not h.fits or not m.fits:continue
      var center:float=(h.low[0]+h.high[0])*.5
      var candidate_score:float=h.width_fraction-absf(center-size.x*.55)/size.x*.3
      if candidate_score>score:score=candidate_score;best={"fov":fov,"target":[target.x,target.y,target.z]}
   if best.is_empty():errors.append("No fitting arrival at "+str(size))
   else:
    route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=best.fov
    route._camera_to(Vector3(16,10,-20),Vector3(best.target[0],best.target[1],best.target[2]),true);await settle()
    capture("arrival-measured",best)
  route.execute_command("overlook");await settle()
  capture("overlook-baseline",{})
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"comparison_complete_visual_review_pending" if errors.is_empty() else "comparison_rejected","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("res://tests/compare_tubi_framing.gd"),"errors":errors,"rows":rows,"scope":"Camera-only probe: completed public arrival/overlook and measured portrait alternative using actual imported roof/title/wall bounds and moon vertices. Not installed, phone-tested or final scene art acceptance."}," ")+"\n");file.close()
 print("TUBI_CAMERA_COMPARISON_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
