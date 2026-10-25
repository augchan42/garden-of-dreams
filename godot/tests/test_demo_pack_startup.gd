extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func fail(message: String) -> void:
 push_error(message)
 quit(1)

func run() -> void:
 # These are read with FileAccess rather than resource imports. Check the
 # shipped release pack explicitly so disabled assertions cannot hide omissions.
 for path in ["res://data/hexagrams.json", "res://assets/garden-source.json",
              "res://lightmaps/demo-index.json", "res://lightmaps/full-index.json",
              "res://lightmaps/backdrop-wash-index.json", "res://lightmaps/backdrop-wash/manifest.json",
              "res://lightmaps/terminal-spill-index.json", "res://lightmaps/terminal-spill/manifest.json"]:
  if not FileAccess.file_exists(path) or JSON.parse_string(FileAccess.get_file_as_string(path)) == null:
   fail("Required JSON is missing or invalid in the shipped pack: " + path)
   return
 var configured = str(ProjectSettings.get_setting("application/run/main_scene", ""))
 # Export may serialize a scene UID; resolve it before checking the entry point.
 if configured.begins_with("uid://"):
  configured = ResourceUID.get_id_path(ResourceUID.text_to_id(configured))
 if configured != "res://runtime/first_reading_demo.tscn":
  fail("Pack startup must be first_reading_demo, got " + configured)
  return
 var scene = load(configured)
 if not scene is PackedScene:
  fail("Configured demo startup does not load")
  return
 var route = scene.instantiate()
 root.add_child(route)
 await process_frame
 # Release builds omit assertion expressions. Lighting installation must still
 # run, including removing the replaced realtime wash and applying all spills.
 if route.find_child("BackdropWash", true, false) != null:
  fail("Release startup skipped the baked backdrop wash")
  return
 if not route.demo_mode or route.room_id != "terminal_room" or route.actions.get_child_count() != 2:
  fail("Configured startup did not open the focused demo at the terminal")
  return
 var screenshot_dir = ""
 var args = OS.get_cmdline_user_args()
 if "--screenshots-dir" in args:
  screenshot_dir = args[args.find("--screenshots-dir") + 1]
  if DirAccess.make_dir_recursive_absolute(screenshot_dir) != OK:
   fail("Cannot create startup screenshot directory")
   return
 var sizes = [Vector2i(1410,600), Vector2i(390,844), Vector2i(1410,600)]
 for index in range(sizes.size()):
  root.size = sizes[index]
  for frame in range(6):
   await process_frame
   RenderingServer.force_draw()
  var viewport = Rect2(Vector2.ZERO, Vector2(root.size))
  for button in route.actions.get_children():
   if not button is Button or not button.is_visible_in_tree() or not viewport.encloses(button.get_global_rect()):
    fail("Demo startup action is missing or outside the resized viewport")
    return
  if route.room_id != "terminal_room" or route.demo_has_reading:
   fail("Resizing changed the startup state")
   return
  if not screenshot_dir.is_empty():
   var result = root.get_texture().get_image().save_png(screenshot_dir + "/startup-%d.png" % index)
   if result != OK:
    fail("Cannot save native startup image")
    return
 print("DEMO_PACK_STARTUP_PASS: configured demo scene, terminal actions and desktop/portrait/desktop resize")
 for player in route.demo_audio.players.values():
  player.stop()
 route.queue_free()
 await process_frame
 quit(0)
