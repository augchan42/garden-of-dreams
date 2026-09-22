extends SceneTree
func _initialize() -> void:
 var scene=load("res://garden_preview.tscn").instantiate()
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/index.json"))
 var digest=FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 for name in records:
  if records[name].source_glb_sha256!=digest:
   push_error("Bake does not match the imported garden: "+name)
   scene.free()
   quit(1)
   return
 var sources={}
 var nodes:Array[Node]=[scene]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D and records.has(str(node.name)):
   sources[str(node.name)]=node.get_active_material(0)
 var invalid=records.duplicate(true)
 invalid[invalid.keys()[0]].source_glb_sha256="outdated"
 assert(not preload("res://runtime/baked_materials.gd").source_matches(invalid))
 var count=preload("res://runtime/baked_materials.gd").apply_to_scene(scene,records)
 if count!=records.size():
  push_error("A lightmap record did not match an imported node")
  scene.free()
  quit(1)
  return
 nodes=[scene]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D and sources.has(str(node.name)):
   var source=sources[str(node.name)]
   var material=node.get_active_material(0)
   if not material is ShaderMaterial or node.layers!=2:
    push_error("Baked mesh was not isolated from static keys")
    scene.free()
    quit(1)
    return
   if material.get_shader_parameter("base_color")!=source.albedo_color or material.get_shader_parameter("material_roughness")!=source.roughness:
    push_error("Baked adapter changed source material properties")
    scene.free()
    quit(1)
    return
 scene.free()
 print("BAKE_ADAPTER_PASS ",count," maps, matching source hash and material properties")
 quit(0)
