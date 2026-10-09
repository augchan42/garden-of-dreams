extends SceneTree

var output_directory = "res://../docs/reference"
var report: Dictionary = {}

func _initialize() -> void:
 call_deferred("run")

func capture(route: Node, name: String) -> void:
 await create_timer(1.5).timeout
 RenderingServer.force_draw()
 var path = output_directory + "/demo-" + name + ".png"
 var image = root.get_texture().get_image()
 assert(image.save_png(path) == OK)
 report.captures[name] = {"sha256": FileAccess.get_sha256(path), "image_size": [image.get_width(),image.get_height()]}

func run() -> void:
 var portrait = "--portrait" in OS.get_cmdline_user_args()
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--output-directory="):
   output_directory = argument.trim_prefix("--output-directory=")
 assert(DirAccess.make_dir_recursive_absolute(output_directory) == OK)
 root.size = Vector2i(390, 844) if portrait else Vector2i(1410, 600)
 var suffix = "portrait" if portrait else "desktop"
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 var fixed_clock = "--fixed-clock" in OS.get_cmdline_user_args()
 if fixed_clock:
  for node in route.find_children("*","MeshInstance3D",true,false):
   for surface in range(node.mesh.get_surface_count()):
    var material = node.get_active_material(surface)
    if material is ShaderMaterial:
     for uniform in material.shader.get_shader_uniform_list():
      if uniform.name == "timeline_time":material.set_shader_parameter("timeline_time",3.0)
 report = {"source_glb_sha256": FileAccess.get_sha256("res://assets/garden-of-dreams.glb"), "scope": "Actual native demo arrival/reading/table/finale images; visual review is separate, not route timing or phone acceptance.", "fixed_clock": 3.0 if fixed_clock else -1.0, "captures": {}}
 await capture(route, suffix + "-cell")
 route.player.position = Vector3(0, .03, 32.5)
 route._arrive("rockery_gate", true)
 await capture(route, suffix + "-gate")
 route.player.position = Vector3(0, .03, 1.8)
 route._arrive("qinfang_ting", true)
 await capture(route, suffix + "-pavilion")
 route.cast_rng.seed = 2817
 route.execute_command("cast")
 await capture(route, suffix + "-reading")
 route.get_node("ReadingResult").queue_free()
 await process_frame
 await capture(route, suffix + "-table")
 route.execute_command("finish")
 await capture(route, suffix + "-finale")
 var file = FileAccess.open(output_directory + "/demo-" + suffix + "-report.json",FileAccess.WRITE)
 assert(file != null)
 file.store_string(JSON.stringify(report,"  "))
 file.close()
 print("DEMO_RENDER_PASS ", suffix)
 quit(0)
