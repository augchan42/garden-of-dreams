extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func settle() -> void:
 for frame in range(12):
  await process_frame
  RenderingServer.force_draw()

func capture(route: Node3D, path: String) -> Dictionary:
 var inscription = route.find_child("HERO_gate_inscription*", true, false) as MeshInstance3D
 assert(inscription != null, "Entrance inscription mesh is missing")
 var bounds = inscription.get_aabb()
 var minimum = Vector2(INF, INF)
 var maximum = Vector2(-INF, -INF)
 for corner in range(8):
  var screen = route.camera.unproject_position(inscription.global_transform * bounds.get_endpoint(corner))
  minimum = minimum.min(screen)
  maximum = maximum.max(screen)
 var rect = Rect2(minimum, maximum - minimum).intersection(Rect2(Vector2.ZERO, Vector2(root.size)))
 assert(rect.has_area(), "Inscription is outside the captured view")
 assert(root.get_texture().get_image().save_png(path) == OK)
 return {"sha256": FileAccess.get_sha256(path), "inscription_rect": [int(floor(rect.position.x)), int(floor(rect.position.y)), int(ceil(rect.end.x)), int(ceil(rect.end.y))]}

func run() -> void:
 var arguments = OS.get_cmdline_user_args()
 var capture_only = "--capture-only" in arguments
 var folder = "res://../docs/reference/gate-inscription-runtime"
 for argument in arguments:
  if argument.begins_with("--output-directory="):
   folder = argument.trim_prefix("--output-directory=")
 assert(DirAccess.make_dir_recursive_absolute(folder) == OK)
 var textures: Array[Texture2D] = []
 for suffix in ["", "-normal"]:
  var texture = load("res://assets/garden-of-dreams_gate-inscription" + suffix + ".png") as Texture2D
  assert(texture != null)
  if not capture_only:
   if texture.get_size() != Vector2(512, 170):
    push_error("Entrance inscription differs from reviewed 512x170 runtime cap")
    quit(1)
    return
   assert(texture.get_image().has_mipmaps(), "Inscription needs mipmaps")
   assert(not texture.get_image().is_compressed(), "Inscription must retain lossless pixels")
  textures.append(texture)
 assert(textures[0].get_size() == textures[1].get_size(), "Color and recessed normal texels do not align")
 var report = {
  "source_glb_sha256": FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),
  "scope": "Actual lossless runtime cap, aligned color/normal dimensions, and fixed-clock desktop/portrait arrival/close captures. Visual comparison is separate; this does not verify later roof bakes or final whole-garden art.",
  "capture_only": capture_only,
  "textures": [],
  "captures": {}
 }
 for texture in textures:
  report.textures.append({"source_sha256": FileAccess.get_sha256(texture.resource_path), "import_sha256": FileAccess.get_sha256(texture.resource_path + ".import"), "size": [texture.get_width(), texture.get_height()], "image_bytes": texture.get_image().get_data_size(), "image_format": texture.get_image().get_format()})
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.set_process(false)
 route.set_physics_process(false)
 route.player.position = Vector3(0, 0.04, 32.5)
 route.get_node("PracticalLights").update_lights()
 for node in route.find_children("*", "MeshInstance3D", true, false):
  for surface in range(node.mesh.get_surface_count()):
   var material = node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name == "timeline_time":
      material.set_shader_parameter("timeline_time", 3.0)
 for shape in ["desktop", "portrait"]:
  root.size = Vector2i(1410, 600) if shape == "desktop" else Vector2i(390, 844)
  await settle()
  route._arrive("rockery_gate", true)
  route.command_panel.hide()
  await settle()
  var arrival = folder + "/" + shape + "-arrival.png"
  report.captures[shape + "-arrival"] = capture(route, arrival)
  route._camera_to(Vector3(0, 2.6, 34.1), Vector3(0, 3, 32.4), true)
  await settle()
  var close = folder + "/" + shape + "-close.png"
  report.captures[shape + "-close"] = capture(route, close)
 var file = FileAccess.open(folder + "/report.json", FileAccess.WRITE)
 file.store_string(JSON.stringify(report, "  "))
 file.close()
 print("GATE_INSCRIPTION_TEXTURE_PASS ", "capture-only" if capture_only else "512x170 lossless mipmapped", " source=", report.source_glb_sha256)
 route.queue_free()
 await process_frame
 quit(0)
