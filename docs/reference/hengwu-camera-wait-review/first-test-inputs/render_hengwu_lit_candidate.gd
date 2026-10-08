extends SceneTree
var output := ""
const SOURCE := "26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38"
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="): output = arg.trim_prefix("--output=")
 call_deferred("run")
func settle(frames: int = 12) -> void:
 for frame in range(frames): await process_frame
 RenderingServer.force_draw()
 await RenderingServer.frame_post_draw
func run() -> void:
 assert(output != "" and DisplayServer.get_name() != "headless")
 assert(FileAccess.get_sha256("res://assets/garden-of-dreams.glb") == SOURCE)
 DirAccess.make_dir_recursive_absolute(output)
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await settle()
 assert(route.site_bakes_enabled and not route.demo_mode)
 var rock := route.find_child("SITE_hengwu-yuan_MAT_plaster_rock", true, false) as MeshInstance3D
 assert(rock != null and rock.get_active_material(0) is ShaderMaterial)
 var material := rock.get_active_material(0) as ShaderMaterial
 var texture := material.get_shader_parameter("lightmap") as Texture2D
 assert(texture != null)
 var catalog: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 var record: Dictionary = catalog["SITE_hengwu-yuan_MAT_plaster_rock"]
 assert(record.source_glb_sha256 == SOURCE)
 route.player.position = Vector3(-18, .03, -11)
 var rows: Array = []
 for size in [Vector2i(1410, 600), Vector2i(390, 844), Vector2i(360, 800)]:
  root.size = size
  route._configure_ui_scale(false, 160)
  await settle()
  route._arrive("hengwu_yuan", true)
  await settle()
  for action in ["arrival", "rocks", "read"]:
   if action != "arrival":
    route.execute_command(action)
    await settle(110)
   assert(route.room_id == "hengwu_yuan")
   var pixels := root.get_texture().get_image()
   var path: String = output + "/candidate-" + action + "-%dx%d.png" % [size.x, size.y]
   assert(pixels.save_png(path) == OK)
   rows.append({"action": action, "capture": path, "sha256": FileAccess.get_sha256(path), "actual_pixels": [pixels.get_width(), pixels.get_height()], "logical_viewport": [root.size.x, root.size.y], "camera_position": [route.camera.position.x, route.camera.position.y, route.camera.position.z], "camera_transform": str(route.camera.transform), "site_bakes_enabled": route.site_bakes_enabled, "lightmap_resource": texture.resource_path, "lightmap_source_sha256": record.source_glb_sha256})
 var file := FileAccess.open(output + "/report.json", FileAccess.WRITE)
 file.store_string(JSON.stringify({"status": "source_matched_hengwu_actions_rendered_visual_review_pending", "source_glb_sha256": SOURCE, "rows": rows, "script_sha256": FileAccess.get_sha256("res://tests/render_hengwu_lit_candidate.gd"), "scope": "Native normal exploration with fresh matching source lighting and completed public action camera poses. Original PNGs require visual review; direct setup does not establish traversal physics."}, " ") + "\n")
 file.close()
 print("HENGWU_LIT_ACTIONS_RECORDED ", rows.size())
 quit(0)
