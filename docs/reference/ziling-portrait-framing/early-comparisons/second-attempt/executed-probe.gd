extends SceneTree
var route
var output:=""
var rows:Array=[]
var errors:Array[String]=[]
var subjects:Dictionary={}
var bounds:Dictionary={}
func _initialize()->void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 root.show()
 create_timer(150).timeout.connect(func():push_error("ZILING_PROBE_TIMEOUT");quit(1))
 call_deferred("run")
func settle()->void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
 RenderingServer.force_draw();await RenderingServer.frame_post_draw
func vertices(mesh:MeshInstance3D)->Array[Vector3]:
 var points:Array[Vector3]=[]
 for surface in range(mesh.mesh.get_surface_count()):
  for p in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:points.append(mesh.global_transform*p)
 return points
func box(points:Array)->Array[Vector3]:
 var low:=Vector3(INF,INF,INF);var high:=Vector3(-INF,-INF,-INF)
 for p in points:low=low.min(p);high=high.max(p)
 var result:Array[Vector3]=[]
 for x in [low.x,high.x]:
  for y in [low.y,high.y]:
   for z in [low.z,high.z]:result.append(Vector3(x,y,z))
 return result
func measure(points:Array)->Dictionary:
 var low:=Vector2(INF,INF);var high:=Vector2(-INF,-INF);var behind:=0
 for p in points:
  if route.camera.is_position_behind(p):behind+=1
  var pixel:Vector2=route.camera.unproject_position(p);low=low.min(pixel);high=high.max(pixel)
 var size:Vector2=root.get_visible_rect().size;var header:Rect2=route.status.get_global_rect();var panel:Rect2=route.command_panel.get_global_rect()
 return {"low":[low.x,low.y],"high":[high.x,high.y],"width_fraction":(high.x-low.x)/size.x,"fits":behind==0 and low.x>=12 and high.x<=size.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14,"behind":behind,"header_bottom":header.end.y,"panel_top":panel.position.y}
func capture(mode:String,variant:String,parameters:Dictionary)->void:
 var image:=root.get_texture().get_image();var path:=output+"/%s-%s-%dx%d.png"%[mode,variant,image.get_width(),image.get_height()];assert(image.save_png(path)==OK)
 var measurements:Dictionary={}
 for name in subjects:measurements[name]=measure(subjects[name])
 rows.append({"mode":mode,"variant":variant,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"measurements":measurements,"parameters":parameters,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"camera_transition_running":false})
func run()->void:
 assert(output!="" and DisplayServer.get_name()!="headless")
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route);await settle()
 subjects.island=vertices(route.find_child("SITE_ziling-zhou_MAT_plaster_rock",true,false))
 subjects.bridge=vertices(route.find_child("SITE_ziling-zhou_MAT_pavilion_atlas",true,false))
 subjects.reeds=[]
 for mesh in route.find_children("HERO_flora_ziling*","MeshInstance3D",true,false):subjects.reeds.append_array(vertices(mesh))
 assert(subjects.reeds.size()>64)
 for name in subjects:bounds[name]=box(subjects[name])
 route.player.position=Vector3(-35.4,.03,0)
 for mode in ["normal","touch","density"]:
  var sizes=[Vector2i(1080,2340),Vector2i(945,2100)] if mode=="density" else [Vector2i(390,844),Vector2i(360,800)]
  for size in sizes:
   root.size=size;route._configure_ui_scale(mode!="normal",420 if mode=="density" else 160);await settle()
   route._arrive("ziling_zhou",true);await settle();capture(mode,"baseline",{})
   var best:Dictionary={};var score:float=-INF
   for position in [Vector3(-43,1.8,4),Vector3(-43,2.2,6),Vector3(-42,2.2,6),Vector3(-41,2.0,6),Vector3(-40,1.8,6),Vector3(-41,2.4,8),Vector3(-42,2.4,8),Vector3(-43,2.4,8),Vector3(-40,2.4,8),Vector3(-39,2.4,8)]:
    for x in [-33.0,-32.0,-31.0,-30.0,-29.0]:
     for y in [-4.0,-3.0,-2.0,-1.0,0.0]:
      for fov in [45.0,50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0]:
       var target:=Vector3(x,y,0)
       route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=fov;route._camera_to(position,target,true)
       var island:=measure(bounds.island);var bridge:=measure(bounds.bridge);var reeds:=measure(bounds.reeds)
       if island.fits and bridge.fits and reeds.fits:
        var value:float=island.width_fraction+.2*island.high[1]/root.get_visible_rect().size.y
        if value>score:score=value;best={"position":[position.x,position.y,position.z],"target":[target.x,target.y,target.z],"fov":fov}
   if best.is_empty():errors.append("No complete island/bridge/reeds fit: "+mode+str(size))
   else:
    route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=best.fov;route._camera_to(Vector3(best.position[0],best.position[1],best.position[2]),Vector3(best.target[0],best.target[1],best.target[2]),true);await settle();capture(mode,"measured",best)
 root.size=Vector2i(1410,600);route._configure_ui_scale(false,160);await settle();route._arrive("ziling_zhou",true);await settle();capture("desktop","baseline",{})
 var counts:Dictionary={}
 for name in subjects:counts[name]=subjects[name].size()
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"comparison_complete_visual_review_pending" if errors.is_empty() else "comparison_rejected","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("res://tests/compare_ziling.gd"),"subject_vertex_counts":counts,"errors":errors,"rows":rows,"scope":"Isolated camera-only reed island and complete bridge/reeds proposals; conservative boxes constrain search then actual imported vertices are measured. No manual UI reserve changes. Candidate projection does not prove occlusion or final art; density windows can be host-clamped. No product edits or phone acceptance."}," ")+"\n");file.close()
 print("ZILING_COMPARISON_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
