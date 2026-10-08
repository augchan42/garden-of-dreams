extends SceneTree

# Actual imported canopy in a small native shadow fixture. Scaling and the
# diagnostic material affect only this process; source geometry stays intact.
var output_directory=""

func _initialize() -> void:call_deferred("run")

func run() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-directory="):output_directory=arg.trim_prefix("--output-directory=")
 if output_directory.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Shadow pixel fixture requires native graphics and an output directory")
  quit(1)
  return
 assert(DirAccess.make_dir_recursive_absolute(output_directory)==OK)
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(320,240)
 var imported=load("res://assets/garden-of-dreams.glb").instantiate()
 var canopy=imported.find_child("SITE_stage_MAT_stage_canopy_paint",true,false) as MeshInstance3D
 assert(canopy!=null and canopy.get_meta("extras",{}).get("godot_cast_shadow",true)==false)
 var imported_setting=canopy.cast_shadow
 var imported_layers=canopy.layers
 var fixture=Node3D.new()
 root.add_child(fixture)
 canopy.get_parent().remove_child(canopy)
 canopy.owner=null
 fixture.add_child(canopy)
 imported.free()
 canopy.scale=Vector3.ONE*.1
 canopy.layers=1
 var opaque=StandardMaterial3D.new()
 opaque.albedo_color=Color.BLACK
 opaque.cull_mode=BaseMaterial3D.CULL_DISABLED
 canopy.material_override=opaque
 var floor=MeshInstance3D.new()
 floor.mesh=PlaneMesh.new()
 floor.mesh.size=Vector2(8,8)
 var matte=StandardMaterial3D.new()
 matte.albedo_color=Color.WHITE
 matte.roughness=1.0
 matte.metallic_specular=0.0
 floor.material_override=matte
 fixture.add_child(floor)
 var light=SpotLight3D.new()
 light.light_energy=4.0
 light.shadow_enabled=true
 light.spot_range=10.0
 light.spot_angle=60.0
 fixture.add_child(light)
 light.position=Vector3(0,7,0)
 light.look_at(Vector3.ZERO,Vector3.FORWARD)
 var environment=WorldEnvironment.new()
 environment.environment=Environment.new()
 environment.environment.background_mode=Environment.BG_COLOR
 environment.environment.background_color=Color.BLACK
 environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_DISABLED
 fixture.add_child(environment)
 var camera=Camera3D.new()
 camera.projection=Camera3D.PROJECTION_ORTHOGONAL
 camera.size=5.0
 fixture.add_child(camera)
 camera.position=Vector3(0,1.5,8)
 camera.look_at(Vector3.ZERO)
 camera.current=true
 var samples={}
 for setting in [["imported",imported_setting],["forced-shadow-on",GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED],["forced-shadow-off",GeometryInstance3D.SHADOW_CASTING_SETTING_OFF]]:
  canopy.cast_shadow=setting[1]
  await create_timer(.25).timeout
  await RenderingServer.frame_post_draw
  var picture=root.get_texture().get_image()
  var path=output_directory+"/"+setting[0]+".png"
  assert(picture.save_png(path)==OK)
  var center=camera.unproject_position(Vector3(0,.001,0))
  var luminance=0.0
  for y in range(-3,4):
   for x in range(-3,4):
    var pixel=picture.get_pixel(int(center.x)+x,int(center.y)+y)
    luminance+=(pixel.r*.2126+pixel.g*.7152+pixel.b*.0722)/49.0
  samples[setting[0]]={"setting":setting[1],"floor_luminance":luminance,"image_sha256":FileAccess.get_sha256(path)}
 var passed=imported_setting==GeometryInstance3D.SHADOW_CASTING_SETTING_OFF and samples["forced-shadow-off"].floor_luminance>samples["forced-shadow-on"].floor_luminance+.2 and absf(samples.imported.floor_luminance-samples["forced-shadow-off"].floor_luminance)<.001
 var report={"scope":"Actual imported Blender canopy scaled in an isolated native shadow pixel fixture. Opaque diagnostic material, lamp, floor, layer 1 and camera are test-only. Positive forced double-sided shadow control. Not whole-garden lighting or final canopy paint acceptance.","status":"passed" if passed else "failed","imported_layers":imported_layers,"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"importer_sha256":FileAccess.get_sha256("res://garden_import.gd"),"test_sha256":FileAccess.get_sha256("res://tests/test_export_shadow_intent.gd"),"samples":samples}
 FileAccess.open(output_directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 fixture.queue_free()
 await create_timer(.3).timeout
 if not passed:push_error("Imported no-shadow intent or positive shadow pixel control failed")
 print("EXPORTED_SHADOW_INTENT_", "PASS" if passed else "FAIL", " ", samples)
 quit(0 if passed else 1)
