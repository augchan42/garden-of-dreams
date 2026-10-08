extends RefCounted

# Apply source-hash-checked Cycles lightmaps to selected imported meshes.
static func source_matches(records:Dictionary) -> bool:
 if records.is_empty():return false
 var digest=""
 if FileAccess.file_exists("res://assets/garden-of-dreams.glb"):
  digest=FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 else:
  var manifest=JSON.parse_string(FileAccess.get_file_as_string("res://assets/garden-source.json"))
  if manifest is Dictionary:digest=manifest.get("source_glb_sha256","")
 if digest.is_empty():return false
 for record in records.values():
  if record.get("source_glb_sha256","")!=digest:return false
 return true

static func channel_mask(channel:int) -> Vector4:
 match channel:
  BaseMaterial3D.TEXTURE_CHANNEL_RED:return Vector4(1,0,0,0)
  BaseMaterial3D.TEXTURE_CHANNEL_GREEN:return Vector4(0,1,0,0)
  BaseMaterial3D.TEXTURE_CHANNEL_BLUE:return Vector4(0,0,1,0)
  BaseMaterial3D.TEXTURE_CHANNEL_ALPHA:return Vector4(0,0,0,1)
  BaseMaterial3D.TEXTURE_CHANNEL_GRAYSCALE:return Vector4(1.0/3.0,1.0/3.0,1.0/3.0,0)
 return Vector4(1,0,0,0)

static func material_from_source(source:BaseMaterial3D) -> ShaderMaterial:
 var material=ShaderMaterial.new()
 material.shader=load("res://shaders/baked_diffuse.gdshader")
 material.set_shader_parameter("source_unshaded",source.shading_mode==BaseMaterial3D.SHADING_MODE_UNSHADED)
 material.set_shader_parameter("base_color",source.albedo_color)
 material.set_shader_parameter("material_roughness",source.roughness)
 material.set_shader_parameter("material_metallic",source.metallic)
 material.set_shader_parameter("material_specular",source.metallic_specular)
 material.set_shader_parameter("material_emission",source.emission if source.emission_enabled else Color.BLACK)
 material.set_shader_parameter("emission_energy",source.emission_energy_multiplier)
 material.set_shader_parameter("emission_add",source.emission_operator==BaseMaterial3D.EMISSION_OP_ADD)
 if source is ORMMaterial3D:
  # Native ORM channels replace the hidden Standard numeric factors.
  material.set_shader_parameter("material_roughness",1.0)
  material.set_shader_parameter("material_metallic",1.0)
  material.set_shader_parameter("material_specular",0.5)
  if source.orm_texture:
   material.set_shader_parameter("orm_texture",source.orm_texture)
   material.set_shader_parameter("use_orm_texture",true)
 elif source is StandardMaterial3D:
  # glTF imports packed G/B maps as StandardMaterial3D, not ORMMaterial3D.
  if source.roughness_texture and source.roughness_texture==source.metallic_texture and source.roughness_texture_channel==BaseMaterial3D.TEXTURE_CHANNEL_GREEN and source.metallic_texture_channel==BaseMaterial3D.TEXTURE_CHANNEL_BLUE:
   material.set_shader_parameter("orm_texture",source.roughness_texture)
   material.set_shader_parameter("use_orm_texture",true)
  else:
   if source.roughness_texture:
    material.set_shader_parameter("roughness_texture",source.roughness_texture)
    material.set_shader_parameter("roughness_channel_mask",channel_mask(source.roughness_texture_channel))
    material.set_shader_parameter("use_roughness_texture",true)
   if source.metallic_texture:
    material.set_shader_parameter("metallic_texture",source.metallic_texture)
    material.set_shader_parameter("metallic_channel_mask",channel_mask(source.metallic_texture_channel))
    material.set_shader_parameter("use_metallic_texture",true)
 if source.albedo_texture:
  material.set_shader_parameter("albedo_texture",source.albedo_texture)
  material.set_shader_parameter("use_albedo_texture",true)
 if source.emission_texture:
  material.set_shader_parameter("emission_texture",source.emission_texture)
  material.set_shader_parameter("use_emission_texture",true)
 if source.normal_enabled and source.normal_texture:
  material.set_shader_parameter("normal_texture",source.normal_texture)
  material.set_shader_parameter("normal_scale",source.normal_scale)
  material.set_shader_parameter("use_normal_texture",true)
 return material

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
  elif node is SpotLight3D or node is DirectionalLight3D:
   # Static keys illuminate primary unbaked receivers only. Reflection and
   # backdrop bits must not reintroduce lighting on baked meshes. Exclusive
   # linked washes retain their mask; shadow caster masks remain unchanged.
   node.light_cull_mask=1 if (node.light_cull_mask&1)!=0 else (node.light_cull_mask&~2)
  if not node is MeshInstance3D or not records.has(str(node.name)):continue
  var record=records[str(node.name)]
  var texture=load("res://lightmaps/"+record.texture)
  assert(texture!=null,"Missing baked lightmap")
  for i in range(node.mesh.get_surface_count()):
   var source=node.get_active_material(i)
   assert(source is StandardMaterial3D or source is ORMMaterial3D,"Unsupported baked source material")
   var material=material_from_source(source)
   material.set_shader_parameter("use_lightmap",true)
   material.set_shader_parameter("lightmap",texture)
   material.set_shader_parameter("lightmap_scale",record.scale)
   node.set_surface_override_material(i,material)
  node.material_override=null
  # Replace the static receiver layer, retaining linked lighting such as the
  # painted backdrop's layer 4 wash.
  node.layers=(node.layers&~1)|2
  count+=1
 return count
