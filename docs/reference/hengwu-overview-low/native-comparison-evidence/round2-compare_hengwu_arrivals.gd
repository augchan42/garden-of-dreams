extends SceneTree

const SOURCE := "ba40866e18f9ab3dcb0263855020099b7eedce70243c6a37e4d50c5f74c0e4f2"
var route
var output := ""
var subjects: Dictionary
var poses: Array
var rows: Array = []
var errors: Array[String] = []
var original_materials: Dictionary = {}

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 if DisplayServer.get_name()=="headless" or output=="":
  push_error("Native display and output required");quit(1);return
 root.show()
 create_timer(180).timeout.connect(func():push_error("Hengwu comparison deadline");quit(1))
 call_deferred("run")

func check(ok: bool,message: String) -> void:
 if not ok:errors.append(message);push_error(message)

func settle() -> void:
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 check(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(),"Camera tween incomplete")
 var started:=Time.get_ticks_msec()
 await create_timer(.25).timeout
 while Time.get_ticks_msec()-started<250:await process_frame
 check(Time.get_ticks_msec()-started>=250,"Flora real-time settle incomplete")
 var drawn:=[false]
 RenderingServer.frame_post_draw.connect(func():drawn[0]=true,CONNECT_ONE_SHOT)
 RenderingServer.force_draw()
 var draw_deadline:=Time.get_ticks_msec()+10000
 while not drawn[0] and Time.get_ticks_msec()<draw_deadline:await process_frame
 check(drawn[0],"Native draw incomplete")

func measure() -> Dictionary:
 var result: Dictionary={}
 var viewport:Vector2=root.get_visible_rect().size
 var header:Rect2=route.status.get_global_rect()
 var panel:Rect2=route.command_panel.get_global_rect()
 for name in subjects:
  var low:=Vector2(INF,INF)
  var high:=Vector2(-INF,-INF)
  var behind:=0
  for point in subjects[name].points:
   var world:=Vector3(point[0],point[1],point[2])
   if route.camera.is_position_behind(world):behind+=1
   var pixel:Vector2=route.camera.unproject_position(world)
   low=low.min(pixel);high=high.max(pixel)
  result[name]={"source_object":subjects[name].source_object,"vertices":subjects[name].points.size(),
   "bounds":[[low.x,low.y],[high.x,high.y]],"behind":behind,
   "fits_above_ui":behind==0 and low.x>=12 and high.x<=viewport.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14}
 return result

func capture(label: String,kind: String) -> void:
 var image:Image=root.get_texture().get_image()
 var path:=output+"/"+label+"-"+kind+".png"
 check(image.save_png(path)==OK,"Original capture failed")
 var header:Rect2=route.status.get_global_rect()
 var panel:Rect2=route.command_panel.get_global_rect()
 var size:Vector2=root.get_visible_rect().size
 rows.append({"label":label,"kind":kind,"capture":path,"sha256":FileAccess.get_sha256(path),
  "pixels":[image.get_width(),image.get_height()],"logical_viewport":[size.x,size.y],
  "header_bottom":header.end.y,"panel_top":panel.position.y,"subjects":measure(),
  "camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],
  "camera_transform":str(route.camera.transform),"camera_fov":route.camera.fov,"keep_aspect":route.camera.keep_aspect,
  "room":route.room_id,"visitor":[route.player.position.x,route.player.position.y,route.player.position.z],
  "text":route.output_label.text,"clock":3.,"camera_transition_running":false})

func ids(enabled: bool) -> void:
 var grade=route.find_child("ColorGrade",true,false)
 grade.visible=not enabled
 if not enabled:
  for node in original_materials:node.material_override=original_materials[node]
  return
 var shader:=Shader.new()
 shader.code="shader_type spatial; render_mode unshaded, fog_disabled; varying vec3 world; void vertex(){world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;} void fragment(){vec3 color=vec3(.16); if(world.y>.01 && world.x>=-16.21 && world.x<=-14.59 && world.z>=-13.09 && world.z<=-11.91){color=vec3(1.,.3,0.);} if(world.y>.02 && world.x>=-20.91 && world.x<=-19.09 && world.z>=-15.29 && world.z<=-14.11){color=vec3(0.,1.,1.);} if(world.y>=2.4 && world.z>=-10.3 && world.z<=-9.7){color=vec3(1.,0.,1.);} ALBEDO=color;}"
 var material:=ShaderMaterial.new();material.shader=shader
 for node in route.find_children("SITE_hengwu-yuan_*","MeshInstance3D",true,false):
  if not original_materials.has(node):original_materials[node]=node.material_override
  node.material_override=material

func run() -> void:
 DirAccess.make_dir_recursive_absolute(output)
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE,"Source mismatch")
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/hengwu-arrival-subjects.json"))
 subjects=data.subjects
 poses=JSON.parse_string(FileAccess.get_file_as_string("res://tests/hengwu-arrival-poses.json"))
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await settle()
 check(route.site_bakes_enabled,"Complete matching bakes disabled")
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",3.)
 route.player.position=Vector3(-18,.04,-14.7)
 for size in [Vector2i(1410,600),Vector2i(390,844),Vector2i(360,800)]:
  root.size=size;route._configure_ui_scale(false,160)
  route._arrive("hengwu_yuan",true)
  await create_timer(1.8).timeout
  await settle()
  var suffix:=str(size.x)+"x"+str(size.y)
  capture("baseline-"+suffix,"lit")
  ids(true);await settle();capture("baseline-"+suffix,"ids");ids(false)
  for pose in poses:
   route.camera.keep_aspect=Camera3D.KEEP_WIDTH
   route.camera.fov=pose.horizontal_fov
   route._camera_to(Vector3(pose.eye[0],pose.eye[1],pose.eye[2]),Vector3(pose.target[0],pose.target[1],pose.target[2]),true)
   await settle();capture(pose.label+"-"+suffix,"lit")
   ids(true);await settle();capture(pose.label+"-"+suffix,"ids");ids(false)
 var report={"status":"diagnostic_originals_captured" if errors.is_empty() else "rejected","source_sha256":SOURCE,
  "runtime_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256("res://tests/compare_hengwu_arrivals.gd"),
  "subject_record_sha256":FileAccess.get_sha256("res://tests/hengwu-arrival-subjects.json"),"errors":errors,"rows":rows,
  "scope":"Diagnostic actual public arrival and explicit candidate poses, saved evaluated semantic render vertices, fixed clock3, completed fades/tweens plus250ms flora settle. Orange primary stone, cyan table region and magenta front wall caps are transient world-region ID controls, not exact source-owner segmentation. Original views need direct review. Candidate fit is measured without implying accepted composition, resize or travel behavior. No production change or full scene acceptance."}
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE);file.store_string(JSON.stringify(report," ")+"\n");file.close()
 print("HENGWU_COMPARISON_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
