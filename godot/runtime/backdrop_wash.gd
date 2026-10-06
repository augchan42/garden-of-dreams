extends RefCounted

# glTF omits Blender Area lights and light linking. The runtime substitute
# uses a separate visual layer so it reaches only the painted backdrop.
static func configure(garden: Node3D) -> int:
 var receivers = 0
 var stack: Array[Node] = [garden]
 while not stack.is_empty():
  var node = stack.pop_back()
  stack.append_array(node.get_children())
  if not node is MeshInstance3D:
   continue
  var name_string = str(node.name)
  if (name_string.begins_with("SITE_stage_MAT_cyclorama") or name_string.begins_with("SITE_stage_MAT_stage_cyclorama_")) or name_string.begins_with("SITE_stage_MAT_painted_mountains_") or name_string.begins_with("SITE_stage_MAT_painted_moon"):
   node.layers |= 4
   receivers += 1
 assert(receivers == 5, "Painted backdrop wash must have five receiver meshes")

 var wash = DirectionalLight3D.new()
 wash.name = "BackdropWash"
 wash.light_color = Color(0.72, 0.78, 0.84)
 wash.light_energy = 3.0
 wash.light_cull_mask = 4
 wash.shadow_enabled = false
 garden.add_child(wash)
 wash.position = Vector3(0, 100, 20)
 wash.look_at(Vector3(0, 0, 0), Vector3.UP)
 return receivers

# Install native Blender Area-light maps after the ordinary site maps. The
# independent terms add in linear space; source emission is retained once.
static func apply_baked(garden:Node3D) -> int:
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/backdrop-wash-index.json"))
 if not records is Dictionary or records.size()!=5 or not preload("res://runtime/baked_materials.gd").source_matches(records):
  push_error("Backdrop wash bakes do not match the imported garden")
  return -1
 var receivers={}
 var textures={}
 var prepared={}
 var static_records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 if not static_records is Dictionary or not preload("res://runtime/baked_materials.gd").source_matches(static_records):return -1
 # Validate every target before changing any materials.
 for name in records:
  var node=garden.find_child(name,true,false) as MeshInstance3D
  if node==null:
   push_error("Missing painted backdrop receiver: "+name)
   return -1
  var record=records[name]
  var texture=load("res://lightmaps/"+record.texture) as Texture2D
  if texture==null or record.get("pass_filter",[])!=["DIRECT"]:
   push_error("Invalid native backdrop wash map: "+name)
   return -1
  receivers[name]=node
  var back=load("res://lightmaps/"+record.sides.back.texture) as Texture2D if record.double_sided else texture
  if back==null:return -1
  textures[name]={"front":texture,"back":back}
 for name in records:
  var materials:Array[ShaderMaterial]=[]
  var node=receivers[name] as MeshInstance3D
  for surface in range(node.mesh.get_surface_count()):
   var source=node.get_active_material(surface)
   var material:ShaderMaterial
   if source is ShaderMaterial and source.shader==load("res://shaders/baked_diffuse.gdshader"):
    material=source.duplicate()
   elif source is StandardMaterial3D or source is ORMMaterial3D:
    material=preload("res://runtime/baked_materials.gd").material_from_source(source)
    material.set_shader_parameter("use_lightmap",false)
    # Demo startup has only the priority-1 catalog. Retain the ordinary
    # stage bake on the four painted flats when adding their wash.
    if static_records.has(name):
     var base_map=load("res://lightmaps/"+static_records[name].texture) as Texture2D
     if base_map==null:return -1
     material.set_shader_parameter("lightmap",base_map)
     material.set_shader_parameter("lightmap_scale",static_records[name].scale)
     material.set_shader_parameter("use_lightmap",true)
   else:
    push_error("Unsupported painted backdrop source: "+name)
    return -1
   material.set_shader_parameter("backdrop_wash",textures[name].front)
   material.set_shader_parameter("backdrop_wash_scale",records[name].scale)
   material.set_shader_parameter("backdrop_wash_double_sided",records[name].double_sided)
   material.set_shader_parameter("backdrop_wash_back",textures[name].back)
   material.set_shader_parameter("backdrop_wash_back_scale",records[name].sides.back.scale if records[name].double_sided else records[name].scale)
   material.set_shader_parameter("use_backdrop_wash",true)
   materials.append(material)
  prepared[name]=materials
 for name in records:
  var node=receivers[name] as MeshInstance3D
  for surface in range(prepared[name].size()):
   node.set_surface_override_material(surface,prepared[name][surface])
  node.material_override=null
  node.layers=(node.layers&~1)|2
 var dynamic=garden.get_node_or_null("BackdropWash")
 if dynamic:dynamic.free()
 return receivers.size()
