extends "res://tests/test_full_garden_traversal.gd"

# Reuse the complete public-command physics tour. Capture its actual camera and
# UI without resetting the visitor or changing lights, materials or time scale.
var capture_directory = ""
var capture_portrait = false
var capture_error = ""
var capture_records: Array[Dictionary] = []
var last_capture_msec = 0
var captured_arrivals = -1
var capturing = false
var maximum_practicals = 0
var pending_settle_msec = 0
var settled_arrivals: Array[int] = []

func after_leg() -> void:
 # _arrive emits before the normal camera tween finishes. Retain actual time,
 # visitor and lighting while capturing both arrival motion and settled view.
 if route.camera_tween and route.camera_tween.is_running():
  await route.camera_tween.finished
 await create_timer(.2).timeout

func run() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output = arg.trim_prefix("--output=")
  if arg.begins_with("--capture-directory="):
   capture_directory = arg.trim_prefix("--capture-directory=")
  if arg == "--portrait":capture_portrait = true
 if DisplayServer.get_name() == "headless" or capture_directory.is_empty():
  await finish("Rendered tour requires native graphics and --capture-directory")
  return
 if Engine.time_scale != 1.0:
  await finish("Rendered tour must retain normal simulation time")
  return
 root.content_scale_size = Vector2i.ZERO
 root.size = Vector2i(540,960) if capture_portrait else Vector2i(1410,600)
 if DirAccess.make_dir_recursive_absolute(capture_directory) != OK:
  await finish("Could not create rendered-tour capture directory")
  return
 var catalogs = {}
 for filename in ["full-index.json", "backdrop-wash-index.json", "terminal-spill-index.json"]:
  var records = JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/" + filename))
  if not records is Dictionary or not preload("res://runtime/baked_materials.gd").source_matches(records):
   await finish("Rendered tour requires source-matched lighting: " + filename)
   return
  catalogs[filename] = {"sha256": FileAccess.get_sha256("res://lightmaps/" + filename), "receivers": records.size()}
 if catalogs["full-index.json"].receivers != 124 or catalogs["backdrop-wash-index.json"].receivers != 6 or catalogs["terminal-spill-index.json"].receivers != 7:
  await finish("Rendered candidate tour requires complete 124/6/7 receiver catalogs")
  return
 report.scope = "Native rendered continuous fourteen-room, twenty-six-leg public-command tour with production imported materials, cameras, lighting and UI. PNGs sample motion and arrival state; they are not continuous-video art acceptance or target-device performance evidence. Existing strict physics/state checks run throughout."
 report.render_test_sha256 = FileAccess.get_sha256("res://tests/render_full_garden_traversal.gd")
 report.viewport = [root.size.x, root.size.y]
 report.renderer = RenderingServer.get_current_rendering_method()
 report.catalogs = catalogs
 process_frame.connect(sample_frame)
 await super.run()

func sample_frame() -> void:
 if capturing or not capture_error.is_empty() or not is_instance_valid(route) or not is_instance_valid(route.camera):return
 if route.demo_mode or not route.site_bakes_enabled:
  capture_error = "Rendered tour disabled production full-scene lighting"
  return
 var active = route.get_node("PracticalLights").lights.filter(func(light):return light.visible).size()
 maximum_practicals = maxi(maximum_practicals, active)
 if active > 4:
  capture_error = "Rendered tour exceeded the practical light budget"
  return
 var now = Time.get_ticks_msec()
 var arrival_changed = arrivals.size() != captured_arrivals
 if arrival_changed:pending_settle_msec=now+1000
 var camera_moving = route.camera_tween and route.camera_tween.is_running()
 var settled = not route.travelling and not camera_moving and pending_settle_msec>0 and now>=pending_settle_msec
 if not arrival_changed and not settled and (not route.travelling or now - last_capture_msec < 3000):return
 capturing = true
 RenderingServer.force_draw()
 var image = root.get_texture().get_image()
 var phase = "settled" if settled else "travel" if route.travelling else "arrival"
 var filename = "%03d-%s-%s.png" % [capture_records.size(), route.room_id, phase]
 var path = capture_directory.path_join(filename)
 if image.is_empty() or image.get_width() != root.size.x or image.get_height() != root.size.y or image.save_png(path) != OK:
  capture_error = "Could not save a full-size rendered-tour frame"
 else:
  var position: Vector3 = route.player.position
  var camera_position: Vector3 = route.camera.global_position
  capture_records.append({"file":filename, "sha256":FileAccess.get_sha256(path),
   "arrival_count":arrivals.size(), "phase":phase, "room":route.room_id, "destination":route.destination,
   "travelling":route.travelling, "travel_elapsed":route.travel_elapsed,
   "visitor_position":[position.x,position.y,position.z],
   "camera_position":[camera_position.x,camera_position.y,camera_position.z],
   "camera_fov":route.camera.fov, "active_practicals":active})
 captured_arrivals = arrivals.size()
 if settled:
  settled_arrivals.append(arrivals.size())
  pending_settle_msec=0
 last_capture_msec = now
 capturing = false

func finish(error = "") -> void:
 if process_frame.is_connected(sample_frame):process_frame.disconnect(sample_frame)
 report.captures = capture_records
 report.maximum_practicals = maximum_practicals
 report.settled_arrivals = settled_arrivals
 if error.is_empty():
  if not capture_error.is_empty():error = capture_error
  elif capture_records.is_empty() or captured_arrivals != 26:
   error = "Rendered tour did not capture the complete route and final cell return"
  elif settled_arrivals.size()!=26:
   error = "Rendered tour did not capture all twenty-six settled arrival views"
 await super.finish(error)
