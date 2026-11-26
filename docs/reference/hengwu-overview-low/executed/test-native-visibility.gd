extends SceneTree

const SOURCE := "ba40866e18f9ab3dcb0263855020099b7eedce70243c6a37e4d50c5f74c0e4f2"
var route
var output := ""
var subjects: Dictionary
var probes: Dictionary
var rows: Array = []
var errors: Array[String] = []
var original_materials: Dictionary = {}

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 if DisplayServer.get_name()=="headless" or output=="":
  push_error("Native display and output required");quit(1);return
 root.show()
 create_timer(220).timeout.connect(func():push_error("Hengwu comparison deadline");quit(1))
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
 shader.code="shader_type spatial; render_mode unshaded, fog_disabled; varying vec3 world; void vertex(){world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;} void fragment(){vec3 color=vec3(.16); if(world.x>=-16.239065 && world.x<=-14.583691 && world.y>.05 && world.y<=2.102 && world.z>=-13.0427 && world.z<=-11.951552){color=vec3(1.,.3,0.);} if(world.y>.65 && world.x>=-20.902 && world.x<=-19.098 && world.z>=-15.277 && world.z<=-14.123){color=vec3(0.,1.,1.);} ALBEDO=color;}"
 var material:=ShaderMaterial.new();material.shader=shader
 for node in route.find_children("SITE_hengwu-yuan_*","MeshInstance3D",true,false):
  if not original_materials.has(node):original_materials[node]=node.material_override
  node.material_override=material

func visibility(label: String) -> Dictionary:
 var image:Image=root.get_texture().get_image()
 var size:Vector2=root.get_visible_rect().size
 var measured:=measure()
 var passed_probes:=0
 var sampled:Array=[]
 for p in probes.tabletop_probes:
  var projected:Vector2=route.camera.unproject_position(Vector3(p[0],p[1],p[2]))
  var pixel:=Vector2i(roundi(projected.x*image.get_width()/size.x),roundi(projected.y*image.get_height()/size.y))
  var inside:=pixel.x>=0 and pixel.x<image.get_width() and pixel.y>=0 and pixel.y<image.get_height()
  var color:=image.get_pixelv(pixel) if inside else Color.BLACK
  var visible:=inside and color.r<.2 and color.g>.7 and color.b>.7
  if visible:passed_probes+=1
  sampled.append({"world":p,"pixel":[pixel.x,pixel.y],"rgb":[color.r,color.g,color.b],"visible_in_native_ids":visible})
 var primary:Dictionary=measured["primary-pierced-stone"]
 var low:Array=primary.bounds[0];var high:Array=primary.bounds[1]
 var orange:=0;var area:=0
 for y in range(maxi(0,floori(low[1]*image.get_height()/size.y)),mini(image.get_height(),ceili(high[1]*image.get_height()/size.y))):
  for x in range(maxi(0,floori(low[0]*image.get_width()/size.x)),mini(image.get_width(),ceili(high[0]*image.get_width()/size.x))):
   area+=1
   var color:=image.get_pixel(x,y)
   if color.r>.7 and color.g>.2 and color.g<.8 and color.b<.15:orange+=1
 check(passed_probes>=15,"Tabletop/book obscured in native control: "+label)
 check(orange>=40 and float(orange)/maxi(1,area)>=.08,"Primary stone obscured in native control: "+label)
 for subject in measured:check(measured[subject].fits_above_ui,"Subject covered in native control: "+label+" "+subject)
 return {"table_probes":sampled,"visible_table_probes":passed_probes,"total_table_probes":probes.tabletop_probes.size(),"primary_orange_pixels":orange,"primary_projected_box_pixels":area,"primary_visible_box_fraction":float(orange)/maxi(1,area)}

func run() -> void:
 DirAccess.make_dir_recursive_absolute(output)
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE,"Source mismatch")
 var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/hengwu-arrival-contract.json"))
 subjects=contract.subjects
 probes=JSON.parse_string(FileAccess.get_file_as_string("res://tests/hengwu-visibility-probes.json"))
 check(contract.source_glb_sha256==SOURCE and probes.source_glb_sha256==SOURCE,"Independent records/source mismatch")
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
 var modes:Array=[
  {"label":"normal-desktop","size":Vector2i(1410,600),"touch":false,"dpi":160},
  {"label":"normal-portrait","size":Vector2i(390,844),"touch":false,"dpi":160},
  {"label":"normal-narrow","size":Vector2i(360,800),"touch":false,"dpi":160},
  {"label":"normal-short-wide","size":Vector2i(1410,480),"touch":false,"dpi":160},
  {"label":"normal-short","size":Vector2i(844,390),"touch":false,"dpi":160},
  {"label":"touch-short","size":Vector2i(844,390),"touch":true,"dpi":160},
  {"label":"density-portrait","size":Vector2i(1080,2340),"touch":true,"dpi":420},
  {"label":"density-landscape","size":Vector2i(2340,1080),"touch":true,"dpi":420}]
 for mode in modes:
  root.size=mode.size;route._configure_ui_scale(mode.touch,mode.dpi)
  route._arrive("hengwu_yuan",true)
  await create_timer(1.8).timeout;await settle()
  capture(mode.label,"lit")
  ids(true);await settle();capture(mode.label,"ids")
  rows[-1]["visibility"]=visibility(mode.label)
  ids(false)
 var report={"status":"hengwu_native_visibility_passed" if errors.is_empty() else "rejected","source_glb_sha256":SOURCE,
  "runtime_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256("res://tests/test_hengwu_native_visibility.gd"),
  "subject_contract_sha256":FileAccess.get_sha256("res://tests/hengwu-arrival-contract.json"),"probe_record_sha256":FileAccess.get_sha256("res://tests/hengwu-visibility-probes.json"),"errors":errors,"rows":rows,
  "scope":"Actual public arrival, completed fades/tweens plus250ms native settle, independent saved semantic vertices, fixedclock3. Transient orange primary stone bbox and cyan tabletop/book world-region IDs measure native visibility with depth occlusion; these are not exact source-owner masks or through-hole tests. Direct original review remains necessary. Source geometry/lightmaps unchanged; no full scene acceptance."}
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE);file.store_string(JSON.stringify(report," ")+"\n");file.close()
 print("HENGWU_NATIVE_VISIBILITY_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
