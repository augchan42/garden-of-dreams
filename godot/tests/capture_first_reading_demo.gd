extends SceneTree

var frames_dir=""
var captured_frames=0
var cue_events=[]
var captured_cue=""
var captured_route:Node

func record_frame():
 RenderingServer.force_draw(true,1.0/30.0)
 var image=root.get_texture().get_image()
 assert(image.save_png(frames_dir+"/frame-%05d.png" % captured_frames)==OK)
 if is_instance_valid(captured_route) and captured_route.demo_audio.last_cue!=captured_cue:
  captured_cue=captured_route.demo_audio.last_cue
  if not captured_cue.is_empty():cue_events.append({"cue":captured_cue,"frame":captured_frames})
 captured_frames+=1

func _initialize() -> void:
 call_deferred("run")

func wait_for_room(route: Node, id: String) -> bool:
 for i in range(3600):
  await physics_frame
  if route.room_id == id and not route.travelling:return true
 return false

func run() -> void:
 root.size = Vector2i(1410, 600)
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 var args=OS.get_cmdline_user_args()
 if "--frames-dir" in args:
  frames_dir=args[args.find("--frames-dir")+1]
  assert(DirAccess.make_dir_recursive_absolute(frames_dir)==OK)
  captured_route=route
  process_frame.connect(record_frame)
 await create_timer(1.0).timeout
 route.execute_command("terminal")
 await create_timer(2.0).timeout
 route.execute_command("exit")
 if not await wait_for_room(route, "rockery_gate"):quit(1);return
 await create_timer(1.0).timeout
 route.execute_command("enter")
 if not await wait_for_room(route, "qinfang_ting"):quit(1);return
 await create_timer(1.0).timeout
 route.execute_command("table")
 await create_timer(1.5).timeout
 route.cast_rng.seed = 2817
 route.execute_command("cast")
 await create_timer(3.0).timeout
 route.get_node("ReadingResult").find_child("CloseReading", true, false).pressed.emit()
 await process_frame
 await create_timer(1.5).timeout
 route.execute_command("finish")
 await create_timer(2.0).timeout
 route.get_node("DemoFinale").find_child("ReplayDemo", true, false).pressed.emit()
 await create_timer(1.0).timeout
 print("DEMO_CAPTURE_PASS")
 if not frames_dir.is_empty():
  process_frame.disconnect(record_frame)
  FileAccess.open(frames_dir+"/capture.json",FileAccess.WRITE).store_string(JSON.stringify({"fps":30,"frames":captured_frames,"cues":cue_events,"scope":"Native Godot frames and cue transitions at fixed 30 FPS; audio assembled from original cue PCM with runtime gains/loop rules."},"  "))
  print("DEMO_FRAME_SEQUENCE_PASS ",captured_frames)
 for player in route.demo_audio.players.values():player.stop()
 await create_timer(.2).timeout
 route.queue_free()
 await create_timer(.2).timeout
 quit(0)
