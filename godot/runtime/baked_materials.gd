extends RefCounted

# Experimental adapter, used by the bake comparison scene until all sites pass.
static func source_matches(records:Dictionary) -> bool:
 if records.is_empty():return false
 var digest=FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 for record in records.values():
  if record.get("source_glb_sha256","")!=digest:return false
 return true

static func apply_to_scene(scene:Node, records:Dictionary) -> int:
 if not source_matches(records):
  push_error("Lightmaps do not match the imported garden")
  return -1
 var count=0
 var nodes:Array[Node]=[scene]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is OmniLight3D:node.light_cull_mask=3
  if not node is MeshInstance3D or not records.has(str(node.name)):continue
  var record=records[str(node.name)]
  var texture=load("res://lightmaps/"+record.texture)
  assert(texture!=null,"Missing baked lightmap")
  for i in range(node.mesh.get_surface_count()):
   var source=node.get_active_material(i)
   assert(source is StandardMaterial3D,"Unsupported baked source material")
   var material=ShaderMaterial.new()
   material.shader=load("res://shaders/baked_diffuse.gdshader")
   material.set_shader_parameter("lightmap",texture)
   material.set_shader_parameter("lightmap_scale",record.scale)
   material.set_shader_parameter("base_color",source.albedo_color)
   material.set_shader_parameter("material_roughness",source.roughness)
   material.set_shader_parameter("material_metallic",source.metallic)
   material.set_shader_parameter("material_emission",source.emission if source.emission_enabled else Color.BLACK)
   material.set_shader_parameter("emission_energy",source.emission_energy_multiplier)
   if source.albedo_texture:
    material.set_shader_parameter("albedo_texture",source.albedo_texture)
    material.set_shader_parameter("use_albedo_texture",true)
   if source.emission_texture:
    material.set_shader_parameter("emission_texture",source.emission_texture)
    material.set_shader_parameter("use_emission_texture",true)
   node.set_surface_override_material(i,material)
  node.layers=2
  count+=1
 return count
