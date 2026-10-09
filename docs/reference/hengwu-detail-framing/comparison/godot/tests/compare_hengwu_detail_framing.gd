extends SceneTree
var route
var output := ""
var contract: Dictionary
var rows: Array = []
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 call_deferred("run")
func settle(frames: int = 12) -> void:
 for f in range(frames):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
 RenderingServer.force_draw()
 await RenderingServer.frame_post_draw
func points(bounds: Array) -> Array[Vector3]:
 var result: Array[Vector3]=[]
 for x in [bounds[0][0],bounds[1][0]]:
  for y in [bounds[0][1],bounds[1][1]]:
   for z in [bounds[0][2],bounds[1][2]]:result.append(Vector3(x,y,z))
 return result
func measure(subject: Array[Vector3]) -> Dictionary:
 var low:=Vector2(INF,INF)
 var high:=Vector2(-INF,-INF)
 var behind:=0
 for p in subject:
  if route.camera.is_position_behind(p):behind+=1
  var pixel:Vector2=route.camera.unproject_position(p)
  low=low.min(pixel);high=high.max(pixel)
 var visible:Vector2=root.get_visible_rect().size
 var panel:Rect2=route.command_panel.get_global_rect()
 var header:Rect2=route.status.get_global_rect()
 return {"low":[low.x,low.y],"high":[high.x,high.y],"behind":behind,"panel_top":panel.position.y,"header_bottom":header.end.y,"width_fraction":(high.x-low.x)/visible.x,"fits":behind==0 and low.x>=12 and high.x<=visible.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14}
func visibility(action: String,subject: Array[Vector3]) -> Dictionary:
 var center:=Vector3.ZERO
 for p in subject:center+=p
 center/=subject.size()
 var query:=PhysicsRayQueryParameters3D.create(route.camera.global_position,center)
 query.exclude=[route.player.get_rid()]
 query.hit_from_inside=true
 var hit:Dictionary=route.get_world_3d().direct_space_state.intersect_ray(query)
 var name:String=str(hit.get("collider",{}).name) if not hit.is_empty() else ""
 var expected:String="COL_hengwu_rock" if action=="rocks" else "COL_hengwu_table"
 return {"hit":name,"expected":expected,"visible":name==expected}
func capture(action: String,variant: String,subject: Array[Vector3],extra: Dictionary) -> void:
 var size:Vector2i=root.size
 var image:=root.get_texture().get_image()
 var path:=output+"/%s-%s-%dx%d.png"%[action,variant,size.x,size.y]
 assert(image.save_png(path)==OK)
 rows.append({"action":action,"variant":variant,"file":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[size.x,size.y],"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"measurement":measure(subject),"visibility":visibility(action,subject),"probe_parameters":extra,"camera_transition_running":false,"site_bakes_enabled":route.site_bakes_enabled})
func run() -> void:
 assert(output!="" and DisplayServer.get_name()!="headless")
 contract=JSON.parse_string(FileAccess.get_file_as_string("res://tests/hengwu-framing-probe.json"))
 assert(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==contract.source_glb_sha256)
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 route.player.position=Vector3(-18,.03,-11)
 for size in [Vector2i(390,844),Vector2i(360,800),Vector2i(1410,600)]:
  root.size=size;route._configure_ui_scale(false,160);await settle()
  route._arrive("hengwu_yuan",true);await settle()
  for action in ["rocks","read"]:
   route.execute_command(action);await settle()
   route.camera.fov=55.0
   var original:Vector3=route.camera.position
   var target:=Vector3(-15.4,1.35,-12.5) if action=="rocks" else Vector3(-20,.85,-14.7)
   var subject:=points(contract.rock_bounds if action=="rocks" else contract.tabletop_bounds)
   capture(action,"baseline",subject,{})
   if size.x>size.y:continue
   # Compare a fixed adjusted pose with a measured pose; neither changes product code.
   var fixed_target:=target+Vector3(0,-.85 if action=="rocks" else -.65,0)
   route._camera_to(target+(original-target)*1.35,fixed_target,true);await settle()
   capture(action,"fixed",subject,{"distance_scale":1.35,"target":[fixed_target.x,fixed_target.y,fixed_target.z]})
   var best:Dictionary={}
   var score:float=-INF
   for fov in [55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0]:
    route.camera.fov=fov
    for scale in [1.0,1.1]:
     for shift in [-1.8,-1.5,-1.2,-1.0,-.85,-.7,-.55,-.4,-.25,0.0]:
      var aim:=target+Vector3(0,shift,0)
      route._camera_to(target+(original-target)*scale,aim,true)
      var m:=measure(subject)
      if not m.fits or not visibility(action,subject).visible:continue
      var center:float=(m.low[1]+m.high[1])*.5
      var desired:float=(m.header_bottom+12+m.panel_top-14)*.5
      var candidate_score:float=m.width_fraction-absf(center-desired)/float(size.y)*.5-(fov-55.0)*.002
      if candidate_score>score:score=candidate_score;best={"fov":fov,"scale":scale,"shift":shift,"target":[aim.x,aim.y,aim.z]}
   assert(not best.is_empty(),"No fitting pose for "+action)
   route.camera.fov=best.fov
   var chosen:Vector3=Vector3(best.target[0],best.target[1],best.target[2])
   route._camera_to(target+(original-target)*float(best.scale),chosen,true);await settle()
   best["book_measurement"]=measure(points(contract.book_bounds)) if action=="read" else {}
   capture(action,"measured",subject,best)
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"camera_comparison_completed_visual_review_pending","source_glb_sha256":contract.source_glb_sha256,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"probe_sha256":FileAccess.get_sha256("res://tests/hengwu-framing-probe.json"),"script_sha256":FileAccess.get_sha256("res://tests/compare_hengwu_detail_framing.gd"),"rows":rows,"scope":"Camera-only comparison on source-matched fresh lighting; baseline public actions, conservative subject projection above measured interface, fixed and measured alternatives. Not installed or final scene acceptance."}," ")+"\n");file.close()
 print("HENGWU_DETAIL_COMPARISON_RECORDED ",rows.size());quit(0)
