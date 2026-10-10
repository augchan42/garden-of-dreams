extends RefCounted

# Shared by the native build check and the actual Android profiler.
const SIZES = {
 "pavilion_basecolor": Vector2i(1024, 1024),
 "wall_basecolor": Vector2i(1024, 1024),
 "gate-inscription": Vector2i(512, 170),
 "gate-inscription-normal": Vector2i(512, 170)
}
const COUNTS = {"pavilion_basecolor": 15, "wall_basecolor": 1, "gate-inscription": 1, "gate-inscription-normal": 1}
var loaded: Dictionary = {}

func resources(include_payloads: bool = true) -> Dictionary:
 var record = {"status": "running", "source_glb_sha256": "", "textures": {}, "errors": [], "modes": []}
 if include_payloads:
  record.source_glb_sha256 = FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 for name in SIZES:
  var path = "res://assets/garden-of-dreams_" + name + ".png"
  var texture = load(path) as Texture2D
  if texture == null:
   record.errors.append("Missing texture " + name)
   continue
  loaded[name] = texture
  var image = texture.get_image()
  if Vector2i(texture.get_width(), texture.get_height()) != SIZES[name]:
   record.errors.append("Actual loaded size differs: " + name)
  if image == null or not image.has_mipmaps():
   record.errors.append("Missing mip image: " + name)
  if image == null:
   continue
  var format = texture.get_format()
  var formats = [Image.FORMAT_DXT1, Image.FORMAT_ETC2_RGB8] if "basecolor" in name else [Image.FORMAT_RGB8 if name.ends_with("normal") else Image.FORMAT_RGBA8]
  if not format in formats:
   record.errors.append("Stored texture format differs: " + name)
  var footprint = Image.create_empty(texture.get_width(), texture.get_height(), image.has_mipmaps(), format).get_data_size()
  var item = {"loaded_size": [texture.get_width(), texture.get_height()], "stored_format": format,
   "stored_mip_bytes": footprint, "readback_bytes": image.get_data_size(),
   "mipmaps": image.has_mipmaps(), "bindings": {}}
  if include_payloads:
   item.source_sha256 = FileAccess.get_sha256(path)
   item.import_sha256 = FileAccess.get_sha256(path + ".import")
   item.cache_payloads = {}
   var config = ConfigFile.new()
   if config.load(path + ".import") != OK:
    record.errors.append("Missing import metadata: " + name)
   else:
    for key in config.get_section_keys("remap"):
     if key == "path" or key.begins_with("path."):
      var cache = str(config.get_value("remap", key))
      if not cache.begins_with("res://.godot/imported/") or not FileAccess.file_exists(cache):
       record.errors.append("Missing generated pixels: " + name)
      else:
       item.cache_payloads[cache.trim_prefix("res://")] = FileAccess.get_sha256(cache)
  record.textures[name] = item
 return record

func bindings(route: Node, mode: String, record: Dictionary) -> void:
 for name in loaded:
  var count = 0
  var texture = loaded[name]
  var field = "normal_texture" if name == "gate-inscription-normal" else "albedo_texture"
  for mesh in route.find_children("*", "MeshInstance3D", true, false):
   for surface in range(mesh.mesh.get_surface_count()):
    var original = mesh.mesh.surface_get_material(surface)
    if original is StandardMaterial3D and original.get(field) == texture:
     count += 1
     var active = mesh.get_active_material(surface)
     if name == "gate-inscription-normal" and not original.normal_enabled:
      record.errors.append(mode + ": imported normal texture disabled " + name)
     if active is ShaderMaterial:
      var enable = "use_normal_texture" if name == "gate-inscription-normal" else "use_albedo_texture"
      if active.get_shader_parameter(enable) != true:
       record.errors.append(mode + ": active shader texture disabled " + name)
      if active.get_shader_parameter(field) != texture:
       record.errors.append(mode + ": active shader binding differs " + name)
     elif active is StandardMaterial3D:
      if name == "gate-inscription-normal" and not active.normal_enabled:
       record.errors.append(mode + ": active standard normal disabled " + name)
      if active.get(field) != texture:
       record.errors.append(mode + ": active standard binding differs " + name)
     else:
      record.errors.append(mode + ": unexpected active material type " + name)
  if record.textures.has(name):
   record.textures[name].bindings[mode] = count
  if count != COUNTS[name]:
   record.errors.append(mode + ": actual imported binding count differs " + name)
 record.modes.append(mode)

func finish(record: Dictionary) -> void:
 record.status = "passed" if record.errors.is_empty() else "failed"
