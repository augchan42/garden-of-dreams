extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var output = ""
 var corrupt = "--corrupt-active" in OS.get_cmdline_user_args()
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="): output = arg.trim_prefix("--output=")
 var inspector = preload("res://tests/runtime_texture_caps.gd").new()
 var record = inspector.resources()
 record.control_mutations = {}
 for mode in ["normal", "demo"]:
  var route = load("res://runtime/entry_route.tscn" if mode == "normal" else "res://runtime/first_reading_demo.tscn").instantiate()
  root.add_child(route)
  await process_frame
  var mutations = 0
  if corrupt:
   for mesh in route.find_children("*", "MeshInstance3D", true, false):
    for surface in range(mesh.mesh.get_surface_count()):
     var original = mesh.mesh.surface_get_material(surface)
     if original is StandardMaterial3D and original.albedo_texture == inspector.loaded.get("pavilion_basecolor"):
      mesh.set_surface_override_material(surface, StandardMaterial3D.new())
      mutations += 1
  for mesh in route.find_children("*", "MeshInstance3D", true, false):
   for surface in range(mesh.mesh.get_surface_count()):
    var original = mesh.mesh.surface_get_material(surface)
    var active = mesh.get_active_material(surface)
    if original is StandardMaterial3D and active is ShaderMaterial:
     if "--disable-albedo" in OS.get_cmdline_user_args() and original.albedo_texture == inspector.loaded.get("pavilion_basecolor"):
      active.set_shader_parameter("use_albedo_texture", false)
      mutations += 1
    if "--disable-normal" in OS.get_cmdline_user_args() and original is StandardMaterial3D and original.normal_texture == inspector.loaded.get("gate-inscription-normal"):
     var replacement = preload("res://runtime/baked_materials.gd").material_from_source(original)
     replacement.set_shader_parameter("use_normal_texture", false)
     mesh.set_surface_override_material(surface, replacement)
     mutations += 1
    if "--disable-standard-normal" in OS.get_cmdline_user_args() and original is StandardMaterial3D and original.normal_texture == inspector.loaded.get("gate-inscription-normal"):
     var replacement = original.duplicate(false)
     replacement.normal_enabled = false
     mesh.set_surface_override_material(surface, replacement)
     mutations += 1
  record.control_mutations[mode] = mutations
  inspector.bindings(route, mode, record)
  route.queue_free()
  await process_frame
 inspector.finish(record)
 if not output.is_empty():
  FileAccess.open(output, FileAccess.WRITE).store_string(JSON.stringify(record, " ") + "\n")
 await create_timer(.2).timeout
 if record.status != "passed": push_error("RUNTIME_TEXTURE_CAPS_REJECTED " + JSON.stringify(record.errors))
 else: print("RUNTIME_TEXTURE_CAPS_PASS actual sizes, formats, mips and normal/demo active bindings")
 quit(0 if record.status == "passed" else 1)
