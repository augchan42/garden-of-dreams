extends SceneTree

func _initialize() -> void:
 create_timer(10.0).timeout.connect(func():push_error("Props bake test timed out");quit(1))
 call_deferred("_run")

func _run() -> void:
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/demo-index.json"))
 var record=records.values()[0]
 var scene=Node3D.new()
 root.add_child(scene)
 var props=load("res://materials/props_atlas.tres") as ORMMaterial3D
 var mesh=MeshInstance3D.new()
 mesh.name="PropsBakeProbe"
 mesh.mesh=BoxMesh.new()
 mesh.material_override=props
 scene.add_child(mesh)
 assert(preload("res://runtime/baked_materials.gd").apply_to_scene(scene,{"PropsBakeProbe":record})==1)
 assert(mesh.material_override==null)
 var baked=mesh.get_active_material(0) as ShaderMaterial
 assert(baked!=null)
 assert(baked.get_shader_parameter("use_orm_texture")==true)
 assert(baked.get_shader_parameter("orm_texture")==props.orm_texture)
 assert(baked.get_shader_parameter("albedo_texture")==props.albedo_texture)
 assert(baked.get_shader_parameter("emission_texture")==props.emission_texture)
 assert(baked.get_shader_parameter("emission_add")==false)
 assert(baked.get_shader_parameter("material_roughness")==props.roughness)
 assert(baked.get_shader_parameter("material_metallic")==props.metallic)
 assert(mesh.layers==2)
 assert(props.emission_operator==BaseMaterial3D.EMISSION_OP_MULTIPLY)
 if DisplayServer.get_name()!="headless":
  var camera=Camera3D.new()
  camera.position=Vector3(0,0,3)
  camera.current=true
  scene.add_child(camera)
  await process_frame
  await RenderingServer.frame_post_draw
  assert(not root.get_texture().get_image().is_empty())
 var standard=StandardMaterial3D.new()
 standard.emission_enabled=true
 standard.emission_operator=BaseMaterial3D.EMISSION_OP_ADD
 standard.emission=Color(0.2,0.1,0.05)
 mesh.set_surface_override_material(0,standard)
 assert(preload("res://runtime/baked_materials.gd").apply_to_scene(scene,{"PropsBakeProbe":record})==1)
 baked=mesh.get_active_material(0)
 assert(baked.get_shader_parameter("emission_add")==true)
 assert(baked.get_shader_parameter("material_emission")==standard.emission)
 assert(baked.get_shader_parameter("use_orm_texture")!=true)
 scene.free()
 print("PROPS_BAKE_ADAPTER_PASS: shared ORM maps and both emission operators preserved")
 quit(0)
