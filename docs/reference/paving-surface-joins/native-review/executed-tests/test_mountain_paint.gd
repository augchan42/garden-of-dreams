extends SceneTree

func _initialize():
 create_timer(20).timeout.connect(func():push_error("Mountain paint check timed out");quit(1))
 call_deferred("run")

func run():
 var args=OS.get_cmdline_user_args()
 var scene_path="res://assets/garden-of-dreams.glb" if args.is_empty() else args[0]
 var scene=load(scene_path).instantiate()
 var shared=load("res://materials/stage/painted_mountains.tres") as StandardMaterial3D
 assert(shared!=null and shared.albedo_color==Color.WHITE)
 assert(shared.roughness==1 and shared.metallic==0 and shared.cull_mode==BaseMaterial3D.CULL_DISABLED)
 assert(shared.emission_enabled and shared.emission==Color.WHITE)
 assert(abs(shared.emission_energy_multiplier-.6)<.000001)
 assert(shared.emission_operator==BaseMaterial3D.EMISSION_OP_MULTIPLY)
 var paint=shared.albedo_texture
 assert(paint!=null and paint==shared.emission_texture)
 assert(paint.get_size()==Vector2(512,512))
 var image=paint.get_image()
 assert(image.has_mipmaps() and not image.is_compressed())
 var adapter=load("res://runtime/baked_materials.gd")
 for index in range(3):
  var node=scene.find_child("SITE_stage_MAT_painted_mountains_"+str(index),true,false) as MeshInstance3D
  assert(node!=null and node.mesh.get_surface_count()==1)
  assert(node.get_active_material(0)==shared and node.mesh.surface_get_material(0)==shared)
  var arrays=node.mesh.surface_get_arrays(0)
  assert(arrays[Mesh.ARRAY_TEX_UV].size()>0 and arrays[Mesh.ARRAY_TEX_UV2].size()>0)
  var baked=adapter.material_from_source(shared)
  assert(baked.get_shader_parameter("albedo_texture")==paint)
  assert(baked.get_shader_parameter("emission_texture")==paint)
  assert(baked.get_shader_parameter("use_albedo_texture") and baked.get_shader_parameter("use_emission_texture"))
  assert(not baked.get_shader_parameter("emission_add"))
  assert(baked.get_shader_parameter("base_color")==Color.WHITE)
  assert(baked.get_shader_parameter("material_emission")==Color.WHITE)
  assert(abs(baked.get_shader_parameter("emission_energy")-.6)<.000001)
 if args.size()>1:
  var report={"tested_scene_glb_sha256":FileAccess.get_sha256(scene_path),
   "paint_png_sha256":FileAccess.get_sha256("res://materials/stage/mountain-paint.png"),
   "paint_import_sha256":FileAccess.get_sha256("res://materials/stage/mountain-paint.png.import"),
   "scope":"Headless imported scene/material/texture and baked-adapter contracts; not GPU allocation, rendered transfer or complete scene acceptance.",
   "paint_size":[paint.get_width(),paint.get_height()],"mipmaps":image.has_mipmaps(),
   "compressed":image.is_compressed(),"shared_material_nodes":3,
   "emission_energy_multiplier":shared.emission_energy_multiplier,"passed":true}
  var output=FileAccess.open(args[1],FileAccess.WRITE)
  assert(output!=null)
  output.store_string(JSON.stringify(report,"  ")+"\n")
  output.close()
 scene.free()
 print("MOUNTAIN_PAINT_RUNTIME_PASS: three imported bands, one shared 512px mipmapped paint, matching base/emission transfer")
 quit()
