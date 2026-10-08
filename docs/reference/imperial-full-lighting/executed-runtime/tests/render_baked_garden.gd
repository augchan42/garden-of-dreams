extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var suffix="-"+OS.get_cmdline_user_args()[0] if not OS.get_cmdline_user_args().is_empty() else ""
 for path in ["res://materials/water.tres","res://materials/floor_fog.tres"]:
  load(path).set_shader_parameter("timeline_time",0.0)
 var scene=load("res://garden_preview.tscn").instantiate()
 root.add_child(scene)
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/index.json"))
 var nodes:Array[Node]=[scene]
 var expected:Array[String]=[]
 var cameras:Array[Camera3D]=[]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is Camera3D and str(node.name).begins_with("CAM_"):
   if "_wide" in str(node.name) or "shawscope" in str(node.name) or "gate_reveal" in str(node.name):cameras.append(node)
  if node is MeshInstance3D:
   var source=node.mesh.surface_get_material(0)
   if source and source.resource_name not in ["MAT_water","MAT_aojing_water","MAT_fog_plane"]:expected.append(str(node.name))
 for name in expected:
  if not records.has(name):
   push_error("Missing bake: "+name)
   quit(1)
   return
 var count=preload("res://runtime/baked_materials.gd").apply_to_scene(scene,records)
 if count!=expected.size():
  push_error("Bake coverage differs from imported geometry")
  quit(1)
  return
 # Diagnostic only: static shadows are already in the maps. Directionals still
 # shade the animated water. This does not install a production lighting setup.
 nodes=[scene]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is Light3D:node.shadow_enabled=false
 var snapshots=[]
 for camera in cameras:
  camera.make_current()
  await create_timer(.3).timeout
  await RenderingServer.frame_post_draw
  var label=str(camera.name)
  var result=root.get_texture().get_image().save_png("res://../docs/reference/baked-"+label+suffix+".png")
  if result!=OK:
   push_error("Cannot save baked reference")
   quit(1)
   return
  snapshots.append(label)
 var report={"applied_meshes":count,"expected_meshes":expected.size(),"captures":snapshots,"scope":"Experimental full bake, dynamic shadow maps disabled, water retains dynamic light. Not installed as production lighting."}
 var file=FileAccess.open("res://bake-render-validation.json",FileAccess.WRITE)
 file.store_string(JSON.stringify(report,"  "))
 print("BAKED_GARDEN_RENDERED ",report)
 quit(0)
