extends SceneTree

# Inventory actual allocated texture resources. This deliberately records no
# frame timings: a CPU bake may run independently of this graphical readback.
var textures: Dictionary = {}
var materials_seen: Dictionary = {}

func _initialize() -> void:
 call_deferred("run")

func record_texture(texture: Texture2D, binding: String) -> void:
 if texture == null:
  return
 var key = texture.get_rid().get_id()
 if not textures.has(key):
  var image = texture.get_image()
  assert(image != null, "Cannot read allocated texture: " + binding)
  var source_path = texture.resource_path
  textures[key] = {
   "resource_path": source_path,
   "resource_class": texture.get_class(),
   "size": [texture.get_width(), texture.get_height()],
   "image_format": image.get_format(),
   "image_data_bytes": image.get_data_size(),
   "mipmaps": image.has_mipmaps(),
   "source_sha256": FileAccess.get_sha256(source_path) if FileAccess.file_exists(source_path) else "",
   "import_sha256": FileAccess.get_sha256(source_path + ".import") if FileAccess.file_exists(source_path + ".import") else "",
   "bindings": []
  }
 if not binding in textures[key].bindings:
  textures[key].bindings.append(binding)

func record_material(material: Material, owner: String) -> void:
 if material == null:
  return
 # Do not skip a reused material's bindings; only stop next-pass cycles.
 var active: Dictionary = {}
 while material != null:
  var identity = material.get_instance_id()
  if active.has(identity):
   break
  active[identity] = true
  materials_seen[identity] = true
  if material is ShaderMaterial:
   for uniform in material.shader.get_shader_uniform_list():
    var value = material.get_shader_parameter(uniform.name)
    if value is Texture2D:
     record_texture(value, owner + "/" + str(uniform.name))
  else:
   for property in material.get_property_list():
    if property.type == TYPE_OBJECT:
     var value = material.get(property.name)
     if value is Texture2D:
      record_texture(value, owner + "/" + str(property.name))
  material = material.next_pass

func run() -> void:
 var arguments = OS.get_cmdline_user_args()
 var demo = "--demo" in arguments
 var output = "res://../export/runtime-texture-inventory-" + ("demo" if demo else "normal") + ".json"
 for argument in arguments:
  if argument.begins_with("--output="):
   output = argument.trim_prefix("--output=")
 root.size = Vector2i(1410, 600)
 var route = load("res://runtime/first_reading_demo.tscn" if demo else "res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 root.get_tree().create_timer(90).timeout.connect(func():
  push_error("Runtime texture inventory timed out")
  quit(1))
 var report = {
  "status": "running",
  "scope": "Actual graphical allocation and active 3D material texture bindings, including retained flora LOD materials, after all normal arrival views or the three demo arrivals. Image bytes exclude GPU padding, render targets, shadow maps and UI; RenderingServer totals include renderer allocations. No timing, traversal, target-phone or final-art claim.",
  "mode": "demo" if demo else "normal",
  "device": RenderingServer.get_video_adapter_name(),
  "renderer": RenderingServer.get_current_rendering_method(),
  "source_glb_sha256": FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),
  "source_record_sha256": FileAccess.get_sha256("res://assets/garden-source.json"),
  "full_index_sha256": FileAccess.get_sha256("res://lightmaps/full-index.json"),
  "demo_index_sha256": FileAccess.get_sha256("res://lightmaps/demo-index.json"),
  "wash_manifest_sha256": FileAccess.get_sha256("res://lightmaps/backdrop-wash/manifest.json"),
  "spill_manifest_sha256": FileAccess.get_sha256("res://lightmaps/terminal-spill/manifest.json"),
  "test_script_sha256": FileAccess.get_sha256("res://tests/audit_runtime_textures.gd"),
  "views": {}
 }
 assert(DisplayServer.get_name() != "headless" and not report.device.is_empty(), "A real graphical renderer is required")
 var rooms = ["terminal_room", "rockery_gate", "qinfang_ting"] if demo else route.ROOMS.keys()
 for room in rooms:
  route._arrive(room, true)
  for frame in range(6):
   await process_frame
   RenderingServer.force_draw()
  report.views[room] = {"texture_memory_bytes": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)}
 var meshes = route.find_children("*", "MeshInstance3D", true, false)
 var surfaces = 0
 for node in meshes:
  for surface in range(node.mesh.get_surface_count()):
   surfaces += 1
   record_material(node.get_active_material(surface), str(node.name) + "/surface_" + str(surface))
 var flora = route.get_node("FloraLOD")
 for plant in flora.plants:
  for level in ["base", "lower"]:
   var mesh = plant[level] as Mesh
   for surface in range(mesh.get_surface_count()):
    record_material(mesh.surface_get_material(surface), str(plant.node.name) + "/retained_" + level + "/surface_" + str(surface))
 var records: Array = textures.values()
 records.sort_custom(func(a, b): return str(a.resource_path) < str(b.resource_path))
 var bound_bytes = 0
 for record in records:
  record.bindings.sort()
  bound_bytes += record.image_data_bytes
 report.meshes = meshes.size()
 report.surfaces = surfaces
 report.unique_materials = materials_seen.size()
 report.unique_bound_texture_rids = records.size()
 report.bound_image_data_bytes = bound_bytes
 report.texture_memory_bytes = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
 report.textures = records
 report.demo_texture_target_bytes = 64 * 1024 * 1024
 report.demo_texture_target_passed = report.texture_memory_bytes <= report.demo_texture_target_bytes if demo else null
 report.status = "passed"
 var file = FileAccess.open(output, FileAccess.WRITE)
 assert(file != null, "Cannot save texture inventory")
 file.store_string(JSON.stringify(report, "  "))
 file.close()
 print("RUNTIME_TEXTURE_INVENTORY_PASS ", report.mode, " textures=", records.size(), " image_bytes=", bound_bytes, " renderer_bytes=", report.texture_memory_bytes)
 route.queue_free()
 await process_frame
 quit(0)
