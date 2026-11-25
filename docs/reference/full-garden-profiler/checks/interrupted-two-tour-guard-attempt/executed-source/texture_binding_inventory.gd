extends RefCounted

# Read actual allocated resources after profiling, never inside timed frames.
var textures: Dictionary = {}

func record_texture(texture: Texture2D, binding: String) -> void:
 if texture == null:return
 var key = texture.get_rid().get_id()
 if not textures.has(key):
  var image = texture.get_image()
  assert(image != null, "Texture image unavailable: " + binding)
  var stored_format = texture.get_format()
  var stored_size = Image.create_empty(texture.get_width(),texture.get_height(),image.has_mipmaps(),stored_format).get_data_size()
  textures[key] = {"resource_path": texture.resource_path, "resource_class": texture.get_class(), "size": [texture.get_width(),texture.get_height()], "readback_image_format": image.get_format(), "image_data_bytes": image.get_data_size(), "stored_format": stored_format, "stored_format_mip_data_bytes": stored_size, "mipmaps": image.has_mipmaps(), "bindings": []}
 if not binding in textures[key].bindings:textures[key].bindings.append(binding)

func record_material(material: Material, owner: String) -> void:
 var active: Dictionary = {}
 while material != null:
  var identity = material.get_instance_id()
  if active.has(identity):break
  active[identity] = true
  if material is ShaderMaterial:
   for uniform in material.shader.get_shader_uniform_list():
    var value = material.get_shader_parameter(uniform.name)
    if value is Texture2D:record_texture(value,owner+"/"+str(uniform.name))
  else:
   for property in material.get_property_list():
    if property.type == TYPE_OBJECT:
     var value = material.get(property.name)
     if value is Texture2D:record_texture(value,owner+"/"+str(property.name))
  material = material.next_pass

func font_caches(route: Node) -> Dictionary:
 var fonts: Dictionary = {}
 var server = TextServerManager.get_primary_interface()
 for control in route.find_children("*","Control",true,false):
  for font_name in ["font","normal_font","bold_font","italics_font","bold_italics_font","mono_font"]:
   var font = control.get_theme_font(font_name)
   for rid in font.get_rids():fonts[rid.get_id()] = rid
 var images: Array = []
 var total = 0
 for id in fonts:
  var rid = fonts[id]
  for size in server.font_get_size_cache_list(rid):
   for index in range(server.font_get_texture_count(rid,size)):
    var image = server.font_get_texture_image(rid,size,index)
    assert(image != null)
    total += image.get_data_size()
    images.append({"font_rid_id": id, "size_cache": [size.x,size.y], "index": index, "image_size": [image.get_width(),image.get_height()], "format": image.get_format(), "bytes": image.get_data_size()})
 return {"scope": "CPU atlas image bytes for theme font RIDs reachable from current controls; not all implicit platform fallback fonts or complete GPU allocations", "image_data_bytes": total, "images": images}

func collect(route: Node) -> Dictionary:
 textures.clear()
 var memory_before = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
 var meshes = route.find_children("*","MeshInstance3D",true,false)
 for node in meshes:
  for surface in range(node.mesh.get_surface_count()):
   record_material(node.get_active_material(surface),str(node.name)+"/surface_"+str(surface))
 var flora = route.get_node("FloraLOD")
 for plant in flora.plants:
  for level in ["base","lower"]:
   var mesh = plant[level] as Mesh
   for surface in range(mesh.get_surface_count()):
    record_material(mesh.surface_get_material(surface),str(plant.node.name)+"/retained_"+level+"/surface_"+str(surface))
 var records: Array = textures.values()
 records.sort_custom(func(a,b):return str(a.resource_path)<str(b.resource_path))
 var bytes = 0
 var stored_bytes = 0
 for record in records:
  record.bindings.sort()
  bytes += record.image_data_bytes
  stored_bytes += record.stored_format_mip_data_bytes
 var window = route.get_tree().root
 var output = window.get_texture()
 return {"scope": "Actual active 3D bindings and retained flora LOD texture RIDs. Readback may be decompressed by OpenGL; stored-format mip data size is calculated with Godot Image allocation for the loaded Texture2D format. Neither includes GPU padding, UI, render targets or other renderer allocations. No timing in this inventory.", "unique_bound_texture_rids": records.size(), "bound_image_data_bytes": bytes, "stored_format_mip_data_bytes": stored_bytes, "texture_memory_before_readback_bytes": memory_before, "texture_memory_after_readback_bytes": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED), "textures": records, "viewport_output": {"size": [output.get_width(),output.get_height()], "format": output.get_format(), "hdr_2d": window.use_hdr_2d, "msaa_3d": window.msaa_3d}, "reachable_font_caches": font_caches(route)}
