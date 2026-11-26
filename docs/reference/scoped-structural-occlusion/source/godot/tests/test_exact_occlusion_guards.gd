extends SceneTree
func _initialize():
 create_timer(25).timeout.connect(func():quit(1))
 call_deferred("run")
func run():
 assert(ResourceLoader.exists("res://runtime/exact_structural_occlusion.gd"),"Exact occlusion controller must reject unsafe structural materials and geometry")
 var script=load("res://runtime/exact_structural_occlusion.gd")
 var index=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 for control in ["valid","transparent","growth","billboard","fade","object_alpha","shader_alpha","open_backface","missing_last"]:
  root.use_occlusion_culling=false
  var environment=load("res://garden_preview.tscn").instantiate()
  root.add_child(environment)
  assert(preload("res://runtime/baked_materials.gd").apply_to_scene(environment,index)==124)
  var camera=Camera3D.new()
  environment.add_child(camera)
  camera.position=Vector3(-1.3,1.45,39.5)
  camera.look_at(Vector3(-1.3,1.3,35.8))
  camera.fov=55
  camera.current=true
  var stage=environment.find_child("SITE_terminal-cells_MAT_stage_backstage",true,false)
  var original=stage.get_active_material(0)
  var material=original.duplicate()
  stage.set_surface_override_material(0,material)
  var changed_shader=null
  var original_code=""
  match control:
   "transparent":material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
   "growth":material.grow=true;material.grow_amount=-.2
   "billboard":material.billboard_mode=BaseMaterial3D.BILLBOARD_ENABLED
   "fade":material.proximity_fade_enabled=true
   "object_alpha":stage.transparency=.5
   "shader_alpha":
    changed_shader=load("res://shaders/baked_diffuse.gdshader")
    original_code=changed_shader.code
    changed_shader.code=original_code.replace("void fragment() {","void fragment() {\n ALPHA=0.5;")
    assert(changed_shader.code!=original_code)
   "open_backface":
    var plane=PlaneMesh.new()
    var mesh=ArrayMesh.new()
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,plane.surface_get_arrays(0))
    stage.mesh=mesh
    stage.set_surface_override_material(0,material)
   "missing_last":
    var missing=environment.find_child("SITE_rockery-gate_MAT_plaster_rock",true,false)
    missing.get_parent().remove_child(missing)
    missing.free()
  var before={}
  for node in environment.find_children("*","MeshInstance3D",true,false):before[str(node.name)]=hash(var_to_bytes(node.mesh.surface_get_arrays(0)))
  var controller=script.new()
  environment.add_child(controller)
  var result=controller.configure(environment,camera,root)
  if changed_shader!=null:changed_shader.code=original_code
  var derived=environment.find_children("ExactOpaque_*","OccluderInstance3D",true,false)
  if control=="valid":
   assert(result.status=="ready" and derived.size()==5 and root.use_occlusion_culling)
   for occluder in derived:
    var source=environment.find_child(occluder.get_meta("source_mesh"),true,false)
    var original_arrays=source.mesh.surface_get_arrays(0)
    var vertices=occluder.occluder.get_vertices()
    var indices=occluder.occluder.get_indices()
    assert(indices.size()==original_arrays[Mesh.ARRAY_INDEX].size())
    for offset in range(indices.size()):assert(vertices[indices[offset]]==original_arrays[Mesh.ARRAY_VERTEX][original_arrays[Mesh.ARRAY_INDEX][offset]])
    assert(occluder.global_transform==source.global_transform)
   camera.position=Vector3(0,3,7)
   camera.look_at(Vector3(0,.5,0))
   controller.refresh_scope()
   assert(not root.use_occlusion_culling,"Occluders behind the camera must not consume culling work")
  else:
   assert(result.status=="disabled", "Unsafe control accepted: "+control)
   assert(derived.is_empty() and not root.use_occlusion_culling,"Rejected configure must be atomic: "+control)
  for node in environment.find_children("*","MeshInstance3D",true,false):assert(before[str(node.name)]==hash(var_to_bytes(node.mesh.surface_get_arrays(0))),"Source surface modified")
  print("EXACT_OCCLUSION_GUARD_PASS ",control)
  environment.queue_free()
  await process_frame
  assert(not root.use_occlusion_culling,"Controller must restore prior viewport flag on exit")
 print("EXACT_OCCLUSION_GUARDS_PASS controls=9")
 quit()
