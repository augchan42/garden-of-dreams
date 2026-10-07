extends SceneTree
func _initialize() -> void:
 var scene=load("res://garden_preview.tscn").instantiate()
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/demo-index.json"))
 # Exports replace the raw GLB with an imported scene. Use the production
 # validator, which checks the raw source in project runs and its preserved
 # source manifest in packs. The stale-record rejection below covers both.
 if not preload("res://runtime/baked_materials.gd").source_matches(records):
  push_error("Bakes do not match the imported garden")
  scene.free()
  quit(1)
  return
 var sources={}
 var static_masks={}
 var static_shadow_masks={}
 var wash=DirectionalLight3D.new()
 wash.name="BakeAdapterBackdropProbe"
 wash.light_cull_mask=4
 scene.add_child(wash)
 var nodes:Array[Node]=[scene]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is SpotLight3D or node is DirectionalLight3D:
   static_masks[node]=node.light_cull_mask
   static_shadow_masks[node]=node.shadow_caster_mask
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
  if node is SpotLight3D or node is DirectionalLight3D:
   if (node.light_cull_mask&2)!=0 or node.light_cull_mask!=(4 if node==wash else 1) or node.shadow_caster_mask!=static_shadow_masks[node]:
    push_error("Static keys must use primary receivers; exclusive backdrop washes retain their mask")
    scene.free()
    quit(1)
    return
  elif node is OmniLight3D:
   if node.light_cull_mask!=3:
    push_error("Practical lights must illuminate both receiver layers")
    scene.free()
    quit(1)
    return
  if node is MeshInstance3D and sources.has(str(node.name)):
   var source=sources[str(node.name)]
   var material=node.get_active_material(0)
   if not material is ShaderMaterial or node.layers!=2:
    push_error("Baked mesh was not isolated from static keys")
    scene.free()
    quit(1)
    return
   var expected_roughness=1.0 if source is ORMMaterial3D else source.roughness
   var expected_metallic=1.0 if source is ORMMaterial3D else source.metallic
   var expected_specular=0.5 if source is ORMMaterial3D else source.metallic_specular
   if material.get_shader_parameter("base_color")!=source.albedo_color or material.get_shader_parameter("material_roughness")!=expected_roughness or material.get_shader_parameter("material_metallic")!=expected_metallic or material.get_shader_parameter("material_specular")!=expected_specular:
    push_error("Baked adapter changed source material properties")
    scene.free()
    quit(1)
    return
   if source.normal_enabled and (material.get_shader_parameter("use_normal_texture")!=true or material.get_shader_parameter("normal_texture")!=source.normal_texture or material.get_shader_parameter("normal_scale")!=source.normal_scale):
    push_error("Baked adapter lost the source normal map: "+str(node.name))
    scene.free()
    quit(1)
    return
 scene.free()
 print("BAKE_ADAPTER_PASS ",count," maps, source/material properties and static/practical/backdrop receiver masks")
 quit(0)
