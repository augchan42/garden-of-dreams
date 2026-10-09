extends SceneTree

# Catches cropped furniture/stone after arrival, Look, resize, or travel;
# a stale detail selection must never restore a close-up after Look.
const SOURCE := "ba40866e18f9ab3dcb0263855020099b7eedce70243c6a37e4d50c5f74c0e4f2"
var route
var output := ""
var errors: Array[String] = []
var rows: Array = []
var subjects: Dictionary
var touch := false
var density := false

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg=="--touch":touch=true
  if arg=="--density":touch=true;density=true
 if DisplayServer.get_name()=="headless" or output=="":
  push_error("HENGWU_OVERVIEW_REJECTED: Native display and output required");quit(1);return
 root.show()
 create_timer(220).timeout.connect(func():push_error("HENGWU_OVERVIEW_REJECTED: Deadline exceeded");quit(1))
 call_deferred("run")

func check(ok: bool,message: String) -> void:
 if not ok:errors.append(message);push_error("HENGWU_OVERVIEW_REJECTED: "+message)

func settle() -> void:
 for frame in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 check(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(),"Camera tween incomplete")
 var started:=Time.get_ticks_msec()
 await create_timer(.25).timeout
 while Time.get_ticks_msec()-started<250:await process_frame
 var drawn:=[false]
 RenderingServer.frame_post_draw.connect(func():drawn[0]=true,CONNECT_ONE_SHOT)
 RenderingServer.force_draw()
 deadline=Time.get_ticks_msec()+10000
 while not drawn[0] and Time.get_ticks_msec()<deadline:await process_frame
 check(drawn[0],"Native draw incomplete")

func press(label: String) -> void:
 for button in route.actions.get_children():
  if button is Button and button.text==label:
   check(not button.disabled,"Disabled public action "+label);button.pressed.emit();return
 check(false,"Missing public action "+label)

func inspect(label: String) -> void:
 var size:Vector2=root.get_visible_rect().size
 var header:Rect2=route.status.get_global_rect()
 var panel:Rect2=route.command_panel.get_global_rect()
 var measured:Dictionary={}
 for name in subjects:
  var low:=Vector2(INF,INF);var high:=Vector2(-INF,-INF);var behind:=0
  for p in subjects[name].points:
   var world:=Vector3(p[0],p[1],p[2])
   if route.camera.is_position_behind(world):behind+=1
   var pixel:Vector2=route.camera.unproject_position(world);low=low.min(pixel);high=high.max(pixel)
  var fits:=behind==0 and low.x>=12 and high.x<=size.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14
  check(fits,name+" is clipped or covered by interface: "+label)
  if name.begins_with("stone_table") or name=="primary-pierced-stone":
   var minimum:=.15 if size.x<size.y else .045
   check((high.x-low.x)/size.x>=minimum,name+" too small: "+label)
  measured[name]={"bounds":[[low.x,low.y],[high.x,high.y]],"behind":behind,"fits_above_ui":fits,"vertices":subjects[name].points.size()}
 check(route.room_id=="hengwu_yuan" and not route.travelling,"Overview in wrong room: "+label)
 check(route.hengwu_detail_action=="","Cleared detail selection returned: "+label)
 check(route.output_label.text==route.ROOMS.hengwu_yuan.text,"Overview description missing: "+label)
 check(route.camera.position.y<=2.2 and route.camera.position.y>=1.4,"Overview left low observer height: "+label)
 check(route.camera.position.x>-22.25 and route.camera.position.x<-13.75 and route.camera.position.z<-10.3 and route.camera.position.z>-17.8,"Overview camera outside court: "+label)
 var image:Image=root.get_texture().get_image();var path:=output+"/"+label+".png"
 check(image.save_png(path)==OK,"Cannot save original "+label)
 rows.append({"label":label,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],
  "logical_viewport":[size.x,size.y],"header_bottom":header.end.y,"panel_top":panel.position.y,"subjects":measured,
  "camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_transform":str(route.camera.transform),
  "camera_fov":route.camera.fov,"projection":route.camera.projection,"keep_aspect":route.camera.keep_aspect,
  "visitor":[route.player.position.x,route.player.position.y,route.player.position.z],"detail_action":route.hengwu_detail_action,"camera_transition_running":false})

func wait_travel(room: String) -> void:
 check(route.travelling,"Public action did not start travel to "+room)
 var deadline:=Time.get_ticks_msec()+90000
 while route.travelling and Time.get_ticks_msec()<deadline:await physics_frame
 check(not route.travelling and route.room_id==room,"Public travel did not finish at "+room)
 await create_timer(1.8).timeout
 await settle()

func run() -> void:
 DirAccess.make_dir_recursive_absolute(output)
 var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/hengwu-arrival-contract.json"))
 subjects=contract.subjects
 var vertices:=0
 for subject in subjects.values():vertices+=subject.points.size()
 check(subjects.size()==7 and vertices==2482,"Independent saved subject record incomplete")
 check(contract.source_glb_sha256==SOURCE and FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE,"Source/subject identity mismatch")
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 check(route.site_bakes_enabled,"Matching lighting disabled")
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",3.)
 route._configure_ui_scale(touch,160)
 route.player.position=Vector3(-18,.04,-14.7);route._arrive("hengwu_yuan",true)
 await create_timer(1.8).timeout;await settle()
 for size in [Vector2i(640,360),Vector2i(720,360),Vector2i(819,360),Vector2i(820,360),Vector2i(844,360),Vector2i(1410,360),Vector2i(640,579),Vector2i(640,580),Vector2i(819,580),Vector2i(820,580),Vector2i(900,580),Vector2i(1000,580)]:
  root.size=size;await settle();inspect("landscape-"+str(size.x)+"x"+str(size.y))
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"hengwu_overview_passed" if errors.is_empty() else "rejected","touch":touch,"density":density,
  "source_glb_sha256":SOURCE,"runtime_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256("res://tests/test_hengwu_narrow_landscape.gd"),
  "subject_contract_sha256":FileAccess.get_sha256("res://tests/hengwu-arrival-contract.json"),"clock":3.,"errors":errors,"rows":rows,
  "scope":"Actual public actions and farm round trip, completed tweens/fades/draws plus real250msflora, independent saved semantic render-vertex framing above actual UI, low inside-court camera, stable visitor/text, selected detail resize and Look clearing, touch48/final-action reachability. Native desktop density can clamp physical windows; actual pixels/logical sizes recorded. Original visual review, adjacent checks and installed reproduction still required; not final14-site art or physical-phone acceptance."}," ")+"\n");file.close()
 print("HENGWU_OVERVIEW_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
