extends SceneTree

const SOURCE := "26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38"
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
 create_timer(100).timeout.connect(func():push_error("TUBI_FRAMING_REJECTED: Native test deadline exceeded");quit(1))
 call_deferred("run")

func check(ok: bool,message: String) -> void:
 if not ok:errors.append(message);push_error("TUBI_FRAMING_REJECTED: "+message)

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

func inspect(phase: String,arrival: bool,portrait: bool) -> void:
 var measurements:Dictionary={}
 for name in subjects:measurements[name]=measure(subjects[name])
 if portrait:
  check(route.camera.keep_aspect==Camera3D.KEEP_WIDTH,"Portrait projection: "+phase)
  if arrival:
   for name in ["hall","moon","stair"]:check(measurements[name].fits,name+" clipped or covered: "+phase)
   check(measurements.hall.width_fraction>=.45,"Hilltop hall too small: "+phase)
  else:
   check(measurements.pavilion.fits,"Central pavilion roof clipped or covered: "+phase)
   check(measurements.pavilion.width_fraction>=.18,"Overlook pavilion too small: "+phase)
 if not arrival:check(route.camera.position.y>=10,"Overlook remains behind the near roof: "+phase)
 var image:=root.get_texture().get_image()
 var path:=output+"/"+phase+".png"
 check(image.save_png(path)==OK,"Cannot save original "+phase)
 rows.append({"phase":phase,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"measurements":measurements,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"action_scroll_height":route.action_scroll.custom_minimum_size.y,"action_minimum_height":route.actions.get_combined_minimum_size().y,"output_height":route.output_label.size.y,"panel_height":route.command_panel.size.y,"camera_transition_running":false,"text":route.output_label.text})

func run() -> void:
 if DisplayServer.get_name()=="headless" or output=="":push_error("Native renderer and output folder required");quit(1);return
 DirAccess.make_dir_recursive_absolute(output)
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE,"Subject source mismatch")
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 check(route.site_bakes_enabled,"Matching lighting disabled")
 subjects.hall=box(vertices("SITE_tubi-tang_MAT_rooftile"))+box(vertices("HERO_tubi_title*"))+box(vertices("SITE_tubi-tang_MAT_whitewash"))
 subjects.moon=vertices("SITE_stage_MAT_painted_moon")
 # The atlas also contains distant corridor roofs. Select the central pavilion's
 # complete roof region, whose source radius is below four metres.
 var pavilion: Array[Vector3]=[]
 for p in vertices("SITE_qinfang-ting_MAT_pavilion_atlas"):
  if absf(p.x)<4 and absf(p.z)<4 and p.y>2.5:pavilion.append(p)
 check(pavilion.size()>64,"Central pavilion roof selection empty")
 subjects.pavilion=box(pavilion)
 subjects.stair=[]
 var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/source-contract.json"))
 check(contract.source_glb_sha256==SOURCE,"Stair contract source mismatch")
 for p in contract.colliders.COL_tubi_stair_ramp.faces:subjects.stair.append(Vector3(p[0],p[1],p[2]))
 var portrait_size:=Vector2i(1080,2340) if density else Vector2i(390,844)
 var narrow_size:=Vector2i(945,2100) if density else Vector2i(360,800)
 var desktop_size:=Vector2i(2340,1080) if density else Vector2i(1410,600)
 root.size=portrait_size;route._configure_ui_scale(touch,420 if density else 160);await settle()
 route.player.position=Vector3(7,4.03,-31);route._arrive("tubi_tang",true);await settle()
 var visitor:Vector3=route.player.position
 inspect("arrival-portrait",true,true)
 root.size=narrow_size;await settle();inspect("arrival-narrow",true,true)
 root.size=desktop_size;await settle()
 var desktop:=Transform3D(Basis.IDENTITY,Vector3(16,10,-20)).looking_at(Vector3(7,4.9,-32),Vector3.UP)
 check(route.camera.transform.is_equal_approx(desktop) and is_equal_approx(route.camera.fov,55.0) and route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Original desktop arrival not restored")
 inspect("arrival-desktop",true,false)
 root.size=portrait_size;await settle();inspect("arrival-return",true,true)
 press("Look over the garden");await settle()
 var detail_text:String=route.output_label.text
 inspect("overlook-portrait",false,true)
 root.size=narrow_size;await settle();inspect("overlook-narrow",false,true)
 check(route.output_label.text==detail_text,"Resize replaced overlook text")
 root.size=desktop_size;await settle();inspect("overlook-desktop",false,false)
 check(route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Desktop overlook projection not restored")
 check(route.output_label.text==detail_text,"Rotation replaced overlook text")
 root.size=portrait_size;await settle();inspect("overlook-return",false,true)
 var overlook:Transform3D=route.camera.transform
 press("Look");await settle();inspect("look-portrait",true,true)
 check(not route.camera.transform.is_equal_approx(overlook),"Look did not leave the overlook")
 check(route.output_label.text==route.ROOMS.tubi_tang.text,"Look did not restore arrival text")
 root.size=narrow_size;await settle();inspect("look-narrow",true,true)
 check(route.player.position.distance_to(visitor)<.005 and route.room_id=="tubi_tang","Camera actions moved visitor or changed room")
 if touch:
  check(route.input.size.y>=48,"Touch input smaller than 48 logical units")
  for button in route.actions.get_children():check(button.size.y>=48,"Touch action smaller than 48 logical units")
  route.action_scroll.scroll_vertical=10000;await settle()
  var last=route.actions.get_child(route.actions.get_child_count()-1) as Button
  check(route.action_scroll.get_global_rect().encloses(last.get_global_rect()),"Last hilltop action unreachable by scrolling")
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"tubi_framing_passed" if errors.is_empty() else "rejected","source_glb_sha256":SOURCE,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256(get_script().resource_path),"touch":touch,"density":density,"pavilion_selected_vertices":pavilion.size(),"errors":errors,"rows":rows,"scope":"Actual public arrival/overlook/Look, completed tweens, imported hall/moon/central-roof bounds and entire stair-ramp contract above measured UI, resize/rotation/state/text and visitor invariants. Touch targets and final-action scroll reachability. Native density windows can be host-clamped; actual dimensions retained. Projection does not prove occlusion: original pixels need direct review. Not phone or final scene-art acceptance."}," ")+"\n");file.close()
 print("TUBI_FRAMING_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
