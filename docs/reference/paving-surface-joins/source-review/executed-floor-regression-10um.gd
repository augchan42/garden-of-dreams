extends SceneTree

# These portrait pixels map to the three inspected shared nunnery floor rays.
# Read the ordinary lit view first, then transient surface IDs and hide controls.
const SHARED_PIXELS := [Vector2i(210,440),Vector2i(235,455),Vector2i(310,464)]
const CONTROL_PIXELS := [Vector2i(18,442),Vector2i(43,444)]
var route
var output := ""
var rows: Array = []
var errors: Array[String] = []

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 if DisplayServer.get_name()=="headless" or output=="":
  push_error("PAVING_TRANSFER_REJECTED: Native display and output required")
  quit(1)
  return
 root.show()
 create_timer(120).timeout.connect(func():push_error("PAVING_TRANSFER_REJECTED: Deadline exceeded");quit(1))
 call_deferred("run")

func check(ok: bool,message: String) -> void:
 if not ok:
  errors.append(message)
  push_error("PAVING_TRANSFER_REJECTED: "+message)

func settle() -> void:
 var deadline := Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:
  await process_frame
 check(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(),"Camera tween incomplete")
 # Allow the actual practical-light transition and flora LOD work to finish.
 await create_timer(1.8).timeout
 var drawn := [false]
 RenderingServer.frame_post_draw.connect(func():drawn[0]=true,CONNECT_ONE_SHOT)
 RenderingServer.force_draw()
 var draw_deadline := Time.get_ticks_msec()+10000
 while not drawn[0] and Time.get_ticks_msec()<draw_deadline:await process_frame
 check(drawn[0],"Native draw incomplete")

func red(color: Color) -> bool:
 return color.r>.8 and color.g<.05 and color.b<.05

func cyan(color: Color) -> bool:
 return color.r<.05 and color.g>.8 and color.b>.8

func capture(label: String) -> Image:
 var image: Image=root.get_texture().get_image()
 var path := output+"/"+label+".png"
 check(image.save_png(path)==OK,"Capture save failed: "+label)
 var samples: Array = []
 for point in SHARED_PIXELS+CONTROL_PIXELS:
  var origin: Vector3=route.camera.project_ray_origin(Vector2(point))
  var ray: Vector3=route.camera.project_ray_normal(Vector2(point))
  var color: Color=image.get_pixelv(point)
  samples.append({"pixel":[point.x,point.y],"rgb":[color.r,color.g,color.b],
   "ray_origin":[origin.x,origin.y,origin.z],"ray_normal":[ray.x,ray.y,ray.z]})
 rows.append({"label":label,"capture":path,"sha256":FileAccess.get_sha256(path),
  "pixels":[image.get_width(),image.get_height()],"samples":samples,
  "camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],
  "site_bakes_enabled":route.site_bakes_enabled,"camera_transition_running":false})
 return image

func run() -> void:
 var declared: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/garden-source.json"))
 var source := FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 check(source==declared.source_glb_sha256,"Source declaration differs")
 DirAccess.make_dir_recursive_absolute(output)
 root.size=Vector2i(390,844)
 route=load("res://runtime/entry_route.tscn").instantiate()
 route.site_bakes_enabled=true
 route.demo_mode=false
 root.add_child(route)
 route._configure_ui_scale(false,160)
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.)
 var reflection=route.get_node("PondReflection")
 reflection.material.set_shader_parameter("timeline_time",3.)
 route.player.position=Vector3(-25,.04,10.6)
 route._arrive("longcui_an",true)
 await settle()
 check(route.site_bakes_enabled and not route.demo_mode,"Complete source lighting disabled")
 capture("nunnery-lit")
 var grade=route.find_child("ColorGrade",true,false)
 var stage=route.find_child("SITE_stage_MAT_plaster_rock",true,false) as MeshInstance3D
 var nunnery=route.find_child("SITE_longcui-an_MAT_plaster_rock",true,false) as MeshInstance3D
 assert(grade!=null and stage!=null and nunnery!=null)
 grade.hide()
 var shader=Shader.new()
 # Restrict IDs to the inspected floor plane. The retained slab bottom/sides
 # must not masquerade as a duplicate top when the site floor is hidden.
 shader.code="shader_type spatial; render_mode unshaded, fog_disabled; uniform vec4 identity_color : source_color; varying float floor_height; void vertex(){floor_height=(MODEL_MATRIX*vec4(VERTEX,1.0)).y;} void fragment(){if(abs(floor_height)>0.00001){discard;} ALBEDO=identity_color.rgb;}"
 var connecting=ShaderMaterial.new()
 connecting.shader=shader
 connecting.set_shader_parameter("identity_color",Color(0,1,1))
 var site=ShaderMaterial.new()
 site.shader=shader
 site.set_shader_parameter("identity_color",Color(1,0,0))
 stage.material_override=connecting
 nunnery.material_override=site
 await settle()
 var both := capture("nunnery-both-surface-ids")
 for point in SHARED_PIXELS:
  check(red(both.get_pixelv(point)),"Connecting floor still owns shared pixel "+str(point))
 for point in CONTROL_PIXELS:
  check(red(both.get_pixelv(point)),"Unchanged site floor control missing at pixel "+str(point))
 stage.hide()
 await settle()
 var only_site := capture("nunnery-hide-stage")
 for point in SHARED_PIXELS:
  check(red(only_site.get_pixelv(point)),"Site floor missing at pixel "+str(point))
 for point in CONTROL_PIXELS:
  check(red(only_site.get_pixelv(point)),"Site-only floor control missing at pixel "+str(point))
 stage.show()
 nunnery.hide()
 await settle()
 var only_connecting := capture("nunnery-hide-nunnery")
 for point in SHARED_PIXELS:
  check(not cyan(only_connecting.get_pixelv(point)),"Duplicate connecting floor survives at pixel "+str(point))
 var file=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"paving_native_transfer_passed" if errors.is_empty() else "rejected",
  "source_glb_sha256":source,"runtime_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),
  "script_sha256":FileAccess.get_sha256(get_script().resource_path),"errors":errors,"rows":rows,
  "fixed_clock":3.,"settle_seconds":1.8,"identity_plane_height":0.,"identity_height_tolerance":.00001,
  "scope":"Four original native portrait captures at retained nunnery camera. Actual source declaration and complete baked lighting enabled. Transient unshaded floor IDs/hide controls prove retained site ownership and absence of duplicate connecting tops at three previously shared rays. Lit appearance requires direct original review; all-site routes/art/phone/adoption remain separate."}," ")+"\n")
 file.close()
 print("PAVING_NATIVE_TRANSFER_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
