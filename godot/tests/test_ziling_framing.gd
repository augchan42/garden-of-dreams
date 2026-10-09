extends SceneTree

const SOURCE := "c9d4fb308730733af2175c424449f8a63b731674d2527df2168a260cc0f5013e"
var route
var output := ""
var errors: Array[String] = []
var rows: Array = []
var subjects: Dictionary = {}
var touch := false
var density := false

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg=="--touch":touch=true
  if arg=="--density":density=true;touch=true
 if DisplayServer.get_name()!="headless":root.show()
 create_timer(100).timeout.connect(func():push_error("ZILING_FRAMING_REJECTED: Native test deadline exceeded");quit(1))
 call_deferred("run")

func check(ok: bool,message: String) -> void:
 if not ok:errors.append(message);push_error("ZILING_FRAMING_REJECTED: "+message)

func settle() -> void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 check(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(),"Camera tween timeout")
 # Subscribe before forcing a frame so a synchronous completion cannot be missed.
 var completed: Array[bool]=[false]
 RenderingServer.frame_post_draw.connect(func():completed[0]=true,CONNECT_ONE_SHOT)
 RenderingServer.force_draw()
 print("ZILING_DRAW_COMPLETED_SYNCHRONOUSLY ",completed[0])
 if not completed[0]:await RenderingServer.frame_post_draw
 check(completed[0],"Native draw did not complete")

func press(label: String) -> void:
 for button in route.actions.get_children():
  if button is Button and button.text==label:
   check(not button.disabled,"Disabled public action "+label)
   button.pressed.emit()
   return
 check(false,"Missing public action "+label)

func vertices(node: MeshInstance3D,geometry: Mesh=null) -> Array[Vector3]:
 var points: Array[Vector3]=[]
 check(node!=null,"Missing subject node")
 if node==null:return points
 if geometry==null:geometry=node.mesh
 for surface in range(geometry.get_surface_count()):
  for p in geometry.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:points.append(node.global_transform*p)
 return points

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

func inspect(phase: String,portrait: bool) -> void:
 var measurements:Dictionary={}
 for name in subjects:measurements[name]=measure(subjects[name])
 if portrait:
  check(route.camera.keep_aspect==Camera3D.KEEP_WIDTH,"Portrait projection: "+phase)
  for name in subjects:check(measurements[name].fits,name+" clipped or covered: "+phase)
  check(measurements.island.width_fraction>=.45,"Island too small: "+phase)
  check(measurements.bridge.width_fraction>=.18,"Bridge too small: "+phase)
  check(measurements.pavilion_roof.high[1]<measurements.island.low[1]-8,"Roof and island silhouettes not separated: "+phase)
  check(route.camera.position.y<=3.3,"Island view too high: "+phase)
 else:
  check(route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Desktop projection: "+phase)
  for name in subjects:check(measurements[name].fits,name+" clipped or covered: "+phase)
  check(measurements.island.width_fraction>=(150.0/root.get_visible_rect().size.x if root.get_visible_rect().size.y<600 else .23),"Desktop island too small: "+phase)
  check(measurements.bridge.width_fraction>=(110.0/root.get_visible_rect().size.x if root.get_visible_rect().size.y<600 else .12),"Desktop bridge too small: "+phase)
  check(measurements.pavilion_roof.high[1]<measurements.island.low[1]-8,"Desktop roof and island silhouettes not separated: "+phase)
  check(route.camera.position.y<=3.3,"Desktop island view too high: "+phase)
 var image:=root.get_texture().get_image()
 var path:=output+"/"+phase+".png"
 check(image.save_png(path)==OK,"Cannot save original "+phase)
 rows.append({"phase":phase,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"measurements":measurements,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"camera_transition_running":false,"text":route.output_label.text})

func run() -> void:
 if DisplayServer.get_name()=="headless" or output=="":push_error("Native renderer and output folder required");quit(1);return
 DirAccess.make_dir_recursive_absolute(output)
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE,"Subject source mismatch")
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 check(route.site_bakes_enabled,"Matching lighting disabled")
 subjects.island=vertices(route.find_child("SITE_ziling-zhou_MAT_plaster_rock",true,false))
 subjects.bridge=vertices(route.find_child("SITE_ziling-zhou_MAT_pavilion_atlas",true,false))
 subjects.pavilion_roof=vertices(route.find_child("SITE_ouxiang-xie_MAT_rooftile",true,false))
 subjects.reeds=[]
 for plant in route.get_node("FloraLOD").plants:
  if str(plant.node.name).begins_with("HERO_flora_ziling"):
   subjects.reeds.append_array(vertices(plant.node,plant.base));subjects.reeds.append_array(vertices(plant.node,plant.lower))
 check(subjects.island.size()==2112 and subjects.bridge.size()==1296 and subjects.pavilion_roof.size()==8116 and subjects.reeds.size()==48320,"Incomplete imported geometry subject")
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   var active=node.get_active_material(i)
   if active is ShaderMaterial and active.shader.resource_path in ["res://shaders/water.gdshader","res://shaders/floor_fog.gdshader"]:active.set_shader_parameter("timeline_time",10.0)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",10.0)
 var portrait_size:=Vector2i(1080,2340) if density else Vector2i(390,844)
 var narrow_size:=Vector2i(945,2100) if density else Vector2i(360,800)
 var desktop_size:=Vector2i(2340,1080) if density else Vector2i(1410,600)
 root.size=portrait_size;route._configure_ui_scale(touch,420 if density else 160);await settle()
 route.player.position=route.ISLAND_PATH[-1]+Vector3(0,.03,0);route._arrive("ziling_zhou",true);await settle()
 var visitor:Vector3=route.player.position
 inspect("arrival-portrait",true)
 root.size=narrow_size;await settle();inspect("arrival-narrow",true)
 root.size=desktop_size;await settle()
 var short_view:=clampf((600.0-root.get_visible_rect().size.y)/190.0,0.0,1.0)
 var desktop:=Transform3D(Basis.IDENTITY,Vector3(-40,1.4,10).lerp(Vector3(-42,1.4,16),short_view)).looking_at(Vector3(-32,-1.25,0).lerp(Vector3(-32,-3.25,0),short_view),Vector3.UP)
 check(route.camera.transform.is_equal_approx(desktop) and is_equal_approx(route.camera.fov,55.0) and route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Desktop arrival not restored")
 inspect("arrival-desktop",false)
 if not touch:
  root.size=Vector2i(1280,720);await settle();inspect("arrival-desktop-720",false)
 if not density:
  for height in [540,480]:
   root.size=Vector2i(1410,height);await settle();inspect("arrival-desktop-"+str(height),false)
 root.size=portrait_size;await settle();inspect("arrival-return",true)
 var before:Transform3D=route.camera.transform
 press("Watch the reeds");await settle()
 var detail_text:String=route.output_label.text
 check(route.camera.transform.is_equal_approx(before),"Reed description changed the arrival view")
 inspect("reeds-portrait",true)
 root.size=narrow_size;await settle();inspect("reeds-narrow",true)
 check(route.output_label.text==detail_text,"Resize replaced reed description")
 root.size=desktop_size;await settle();inspect("reeds-desktop",false)
 check(route.camera.transform.is_equal_approx(desktop) and route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Reed rotation did not restore desktop camera")
 check(route.output_label.text==detail_text,"Rotation replaced reed description")
 root.size=portrait_size;await settle();inspect("reeds-return",true)
 press("Look");await settle();inspect("look-portrait",true)
 check(route.output_label.text==route.ROOMS.ziling_zhou.text,"Look did not restore arrival text")
 root.size=narrow_size;await settle();inspect("look-narrow",true)
 check(route.player.position.distance_to(visitor)<.005 and route.room_id=="ziling_zhou","Camera actions moved visitor or changed room")
 if touch:
  check(route.input.size.y>=48,"Touch input smaller than 48 logical units")
  for button in route.actions.get_children():check(button.size.y>=48,"Touch action smaller than 48 logical units")
  route.action_scroll.scroll_vertical=10000;await settle()
  var last=route.actions.get_child(route.actions.get_child_count()-1) as Button
  check(route.action_scroll.get_global_rect().encloses(last.get_global_rect()),"Return to pavilion action unreachable by scrolling")
 check(rows.size()==(10 if density else (12 if touch else 13)),"Missing original captures")
 var counts:Dictionary={}
 for name in subjects:counts[name]=subjects[name].size()
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"ziling_framing_passed" if errors.is_empty() else "rejected","source_glb_sha256":SOURCE,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256("res://tests/test_ziling_framing.gd"),"touch":touch,"density":density,"subject_vertex_counts":counts,"errors":errors,"rows":rows,"scope":"Actual public arrival/Watch the reeds/Look with completed tweens, all imported island/bridge/pavilion roof vertices and both reed LODs above measured UI; desktop camera restored, resize/rotation/text/visitor invariants and touch48/last-action scroll. Native density windows can be host-clamped. Projection cannot prove occlusion: original images require direct review. Not final source/site-art, physical phone, moving-tour or sustained acceptance."}," ")+"\n");file.close()
 print("ZILING_FRAMING_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
