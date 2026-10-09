extends SceneTree

const SOURCE := "7a9fc523bc1517941cc248c040877b86f9cd00a11654c6c31e40f3acc089632f"
var route
var output := ""
var errors: Array[String] = []
var rows: Array = []
var source_contract: Dictionary
var touch_enabled := false
var density_enabled := false

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg=="--touch":touch_enabled=true
  if arg=="--density":density_enabled=true;touch_enabled=true
 if DisplayServer.get_name()!="headless":root.show()
 create_timer(90).timeout.connect(func():push_error("HENGWU_DETAIL_FRAMING_REJECTED: Native test deadline exceeded");quit(1))
 call_deferred("run")

func check(ok: bool,message: String) -> void:
 if not ok:
  errors.append(message)
  push_error("HENGWU_DETAIL_FRAMING_REJECTED: "+message)

func settle() -> void:
 for frame in range(16):await process_frame
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

func box_points(low: Vector3,high: Vector3) -> Array[Vector3]:
 var points: Array[Vector3]=[]
 for x in [low.x,high.x]:
  for y in [low.y,high.y]:
   for z in [low.z,high.z]:points.append(Vector3(x,y,z))
 return points

func subject(action: String) -> Array[Vector3]:
 if action=="read":return box_points(Vector3(-20.9,.71,-15.275),Vector3(-19.1,.925,-14.125))
 var low:=Vector3(INF,INF,INF)
 var high:=Vector3(-INF,-INF,-INF)
 for p in source_contract.colliders.COL_hengwu_rock.faces:
  var world:=Vector3(p[0],p[1],p[2])
  low=low.min(world);high=high.max(world)
 return box_points(low,high)

func inspect(action: String,phase: String,fitted: bool) -> void:
 var low:=Vector2(INF,INF)
 var high:=Vector2(-INF,-INF)
 var behind:=0
 for world in subject(action):
  if route.camera.is_position_behind(world):behind+=1
  var pixel:Vector2=route.camera.unproject_position(world)
  low=low.min(pixel);high=high.max(pixel)
 var size:Vector2=root.get_visible_rect().size
 var header:Rect2=route.status.get_global_rect()
 var panel:Rect2=route.command_panel.get_global_rect()
 var fit:=behind==0 and low.x>=12 and high.x<=size.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14
 if fitted:
  check(route.camera.keep_aspect==Camera3D.KEEP_WIDTH,"Portrait detail projection changed")
  check(fit,action+" subject clipped or covered by interface: "+phase)
  check((high.x-low.x)/size.x>=.5,action+" subject too small: "+phase)
  if action=="rocks":check(route.camera.position.z<=-10.4,"Stone camera left the reviewed court interior")
 var path:=output+"/"+action+"-"+phase+".png"
 var image:=root.get_texture().get_image()
 check(image.save_png(path)==OK,"Cannot save original "+phase)
 rows.append({"action":action,"phase":phase,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[size.x,size.y],"bounds":[[low.x,low.y],[high.x,high.y]],"header_bottom":header.end.y,"panel_top":panel.position.y,"fits":fit,"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"camera_transition_running":false})

func run() -> void:
 if DisplayServer.get_name()=="headless" or output=="":
  push_error("Native graphics and an explicit output folder are required")
  quit(1)
  return
 DirAccess.make_dir_recursive_absolute(output)
 source_contract=JSON.parse_string(FileAccess.get_file_as_string("res://tests/source-contract.json"))
 check(source_contract.source_glb_sha256==SOURCE and FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE,"Subject contract source mismatch")
 route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await settle()
 check(route.site_bakes_enabled,"Matching scene bakes disabled")
 route.player.position=Vector3(-18,.03,-11)
 var portrait_size:=Vector2i(1080,2340) if density_enabled else Vector2i(390,844)
 var narrow_size:=Vector2i(945,2100) if density_enabled else Vector2i(360,800)
 var desktop_size:=Vector2i(2340,1080) if density_enabled else Vector2i(1410,600)
 for action in ["rocks","read"]:
  root.size=portrait_size
  route._configure_ui_scale(touch_enabled,420 if density_enabled else 160)
  route._arrive("hengwu_yuan",true)
  await settle()
  var visitor:Vector3=route.player.position
  press("Inspect the rocks" if action=="rocks" else "Examine the book")
  await settle()
  var text:String=route.output_label.text
  inspect(action,"button-portrait",true)
  root.size=narrow_size
  await settle()
  inspect(action,"resize-narrow",true)
  check(route.output_label.text==text,"Resize replaced selected detail text")
  root.size=desktop_size
  await settle()
  var expected_position:=Vector3(-15.6,1.6,-10.6) if action=="rocks" else Vector3(-18,1.8,-13.4)
  var expected_target:=Vector3(-15.4,1.35,-12.5) if action=="rocks" else Vector3(-20,.85,-14.7)
  var expected_transform:=Transform3D(Basis.IDENTITY,expected_position).looking_at(expected_target,Vector3.UP)
  check(route.camera.transform.is_equal_approx(expected_transform) and is_equal_approx(route.camera.fov,55.0),"Rotation did not restore original desktop "+action+" pose")
  check(route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Rotation did not restore original desktop projection")
  check(route.output_label.text==text,"Rotation replaced selected detail text")
  inspect(action,"rotate-desktop",false)
  root.size=portrait_size
  await settle()
  inspect(action,"return-portrait",true)
  if touch_enabled:
   check(route.input.size.y>=48,"Touch input smaller than 48 logical units")
   for button in route.actions.get_children():check(button.size.y>=48,"Touch action smaller than 48 logical units")
   route.action_scroll.scroll_vertical=10000
   await settle()
   var last=route.actions.get_child(route.actions.get_child_count()-1) as Button
   check(route.action_scroll.get_global_rect().encloses(last.get_global_rect()),"Last Hengwu action unreachable by scrolling")
   route.action_scroll.scroll_vertical=0
  check(route.player.position.distance_to(visitor)<.005 and route.room_id=="hengwu_yuan","Detail action or resize moved visitor/changed room")
  press("Look")
  await settle()
  check(route.camera.position.is_equal_approx(Vector3(-17.5,2.6,-10.5)) and is_equal_approx(route.camera.fov,55.0),"Look did not restore Hengwu overview")
  check(route.output_label.text==route.ROOMS.hengwu_yuan.text,"Look did not restore overview text")
  var overview:Transform3D=route.camera.transform
  root.size=narrow_size
  await settle()
  check(route.camera.transform.is_equal_approx(overview),"Resize resurrected a cleared detail action")
  inspect(action,"look-narrow",false)
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"hengwu_detail_framing_passed" if errors.is_empty() else "rejected","touch_enabled":touch_enabled,"density_enabled":density_enabled,"requested_portrait_size":[portrait_size.x,portrait_size.y],"requested_narrow_size":[narrow_size.x,narrow_size.y],"requested_desktop_size":[desktop_size.x,desktop_size.y],"source_glb_sha256":SOURCE,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256("res://tests/test_hengwu_detail_framing.gd"),"source_contract_sha256":FileAccess.get_sha256("res://tests/source-contract.json"),"errors":errors,"rows":rows,"scope":"Actual public buttons, completed camera tweens, conservative subject bounds above real interface at both portrait sizes, original desktop detail restoration, detail text/visitor preservation and Look clearing; optional touch targets and final-action scroll reachability. Density requests may be clamped by the native desktop window; actual PNG dimensions and logical viewports are recorded. Original rendered pixels still require visual review; not physical-phone or final all-site art acceptance."}," ")+"\n")
 file.close()
 print("HENGWU_DETAIL_FRAMING_RESULT ",rows.size()," captures; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
