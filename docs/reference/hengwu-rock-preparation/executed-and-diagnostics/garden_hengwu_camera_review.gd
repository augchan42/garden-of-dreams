extends SceneTree
var route
var output := "/tmp/garden-hengwu-camera-review-identity-corrected"
var rows: Array = []
var errors: Array[String] = []
var colors := {"plaster_rock":Color(1,0,0),"wall_atlas":Color(0,1,1),"props_atlas":Color(0,0,1),"whitewash":Color(1,1,0),"rooftile":Color(1,0,1)}
var ids: Array = []
func _initialize() -> void: call_deferred("run")
func settle() -> void:
 for f in range(12):await process_frame
 RenderingServer.force_draw()
 await RenderingServer.frame_post_draw
func capture(name: String) -> Image:
 var pixels := root.get_texture().get_image()
 var path := output+"/"+name+".png"
 if pixels.save_png(path)!=OK:errors.append("Cannot save "+path)
 var viewport: Vector2 = root.get_visible_rect().size
 var furniture: Array = []
 for point in [Vector3(-20,.94,-14.7),Vector3(-21.3,.48,-14.7),Vector3(-18.7,.48,-14.7),Vector3(-20,.48,-13.55),Vector3(-20,.48,-15.85)]:
  var projected: Vector2 = route.camera.unproject_position(point)
  furniture.append({"world":[point.x,point.y,point.z],"pixel":[projected.x,projected.y],"behind":route.camera.is_position_behind(point)})
 var panel: Rect2 = route.command_panel.get_global_rect()
 rows.append({"variant":name,"capture":path,"sha256":FileAccess.get_sha256(path),"actual_pixels":[pixels.get_width(),pixels.get_height()],"logical_viewport":[viewport.x,viewport.y],"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_basis":[[route.camera.basis.x.x,route.camera.basis.x.y,route.camera.basis.x.z],[route.camera.basis.y.x,route.camera.basis.y.y,route.camera.basis.y.z],[route.camera.basis.z.x,route.camera.basis.z.y,route.camera.basis.z.z]],"fov":route.camera.fov,"panel_top":panel.position.y,"furniture_points":furniture})
 return pixels
func run() -> void:
 if DisplayServer.get_name()=="headless":quit(1);return
 if FileAccess.get_sha256("res://assets/garden-of-dreams.glb")!="59de1ca29bc9d02235fc29a18b78c7b2c3dfde893a27f3b8fb318af6e042ddc8":quit(1);return
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route);await settle()
 root.size=Vector2i(1410,600);route._configure_ui_scale(false,160);await settle();route._arrive("hengwu_yuan",true);await settle();capture("baseline-desktop")
 var old: Dictionary = {}
 var grade = route.find_child("ColorGrade",true,false)
 if grade == null:errors.append("Missing color grade");quit(1);return
 grade.hide()
 for key in colors:
  var mesh = route.find_child("SITE_hengwu-yuan_MAT_"+key,true,false) as MeshInstance3D
  if mesh==null:errors.append("Missing "+key);continue
  old[mesh]=mesh.material_override
  var shader := Shader.new();shader.code="shader_type spatial; render_mode unshaded, fog_disabled; uniform vec4 identity_color: source_color; void fragment(){ALBEDO=identity_color.rgb;}"
  var material := ShaderMaterial.new();material.shader=shader;material.set_shader_parameter("identity_color",colors[key]);mesh.material_override=material
 await settle()
 var identity := capture("surface-identity-desktop")
 for spec in [[Vector2i(1300,120),"plaster_rock"],[Vector2i(1150,100),"wall_atlas"],[Vector2i(1250,300),"plaster_rock"]]:
  var p: Vector2i=spec[0];var actual:=identity.get_pixel(p.x,p.y);var expected: Color=colors[spec[1]]
  var difference:=Vector3(actual.r,actual.g,actual.b).distance_to(Vector3(expected.r,expected.g,expected.b))
  ids.append({"pixel":[p.x,p.y],"expected_batch":spec[1],"rgb":[actual.r,actual.g,actual.b],"distance_from_encoded_id":difference})
  if difference>.08:errors.append("Surface identity mismatch at "+str(p))
 for mesh in old:mesh.material_override=old[mesh]
 grade.show()
 var candidates := {
  "low-center":[Vector3(-18,1.7,-10.7),Vector3(-18,1.15,-15.4),55],
  "low-left":[Vector3(-18.8,1.7,-10.8),Vector3(-18,1.1,-15.5),55],
  "low-right":[Vector3(-17,1.7,-10.8),Vector3(-18.2,1.1,-15.5),55],
  "low-center-wide":[Vector3(-18,1.7,-10.7),Vector3(-18,1.1,-15.4),65],
  "mid-center-wide":[Vector3(-18,2.0,-10.7),Vector3(-18,1.0,-15.4),65]}
 for size in [Vector2i(1410,600),Vector2i(390,844),Vector2i(360,800)]:
  root.size=size;route._configure_ui_scale(false,160);await settle()
  route._arrive("hengwu_yuan",true);await settle()
  if size.x<size.y:capture("baseline-%dx%d"%[size.x,size.y])
  for name in candidates:
   route._arrive("hengwu_yuan",true)
   var view: Array=candidates[name];route.camera.fov=view[2];route.camera.keep_aspect=Camera3D.KEEP_WIDTH if size.x<size.y else Camera3D.KEEP_HEIGHT
   route._camera_to(view[0],view[1],true);await settle();capture(name+"-%dx%d"%[size.x,size.y])
 var file := FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"native_identity_and_camera_comparisons_recorded" if errors.is_empty() else "rejected","errors":errors,"rows":rows,"surface_samples":ids,"id_colors":colors,"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("/tmp/garden_hengwu_camera_review.gd"),"scope":"Diagnostic transient material overrides with the grade temporarily hidden identify three sampled native pixels; normal grade restored for all candidate images; candidate cameras use unchanged production geometry. Furniture projections are positions, not an occlusion/visibility proof. Visual selection and action/resize/traversal acceptance remain separate."}," ")+"\n");file.close()
 print("HENGWU_NATIVE_CAMERA_COMPARISON ",rows.size()," captures; ",errors.size()," errors")
 quit(0 if errors.is_empty() else 1)
