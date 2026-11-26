extends Node

@onready var tree = get_tree()
@onready var window = tree.root

# The release template disables path overrides. This child is inert unless the
# caller explicitly requests acceptance through supported user arguments.
func _ready() -> void:
 if "--demo-acceptance" in OS.get_cmdline_user_args():call_deferred("run")
func fail(message: String) -> void:push_error(message);tree.quit(1)
func button(container: Node, label: String) -> Button:
 for child in container.get_children():
  if child is Button and child.text == label:return child
 return null

func click(target: Button) -> bool:
 if target == null:return false
 var previous = Rect2()
 var stable = 0
 for i in range(30):
  await tree.process_frame
  RenderingServer.force_draw()
  var bounds = target.get_global_rect()
  stable = stable + 1 if bounds == previous else 0
  previous = bounds
  if stable >= 2:break
 if stable < 2:return false
 var motion = InputEventMouseMotion.new()
 motion.position = previous.get_center()
 for down in [true,false]:
  window.push_input(motion,true)
  var event = InputEventMouseButton.new()
  event.button_index = MOUSE_BUTTON_LEFT;event.position = motion.position;event.pressed = down
  window.push_input(event,true)
  await tree.process_frame
 return true

func enter(target: Button) -> bool:
 if target == null:return false
 target.grab_focus()
 await tree.process_frame
 for down in [true,false]:
  var event = InputEventKey.new();event.keycode = KEY_ENTER;event.pressed = down
  window.push_input(event,true)
  await tree.process_frame
 return true

func arrive(route: Node, id: String) -> bool:
 for i in range(3600):
  await tree.physics_frame
  if route.room_id == id and not route.travelling:return true
 return false

func run() -> void:
 var args = OS.get_cmdline_user_args()
 var portrait = "--portrait" in args
 var requested_size = Vector2i(390,844) if portrait else Vector2i(1410,600)
 window.size = requested_size
 var configured = str(ProjectSettings.get_setting("application/run/main_scene",""))
 if configured.begins_with("uid://"):configured = ResourceUID.get_id_path(ResourceUID.text_to_id(configured))
 if configured != "res://runtime/first_reading_demo.tscn":fail("Release pack has the wrong startup scene");return
 var route = get_parent()
 if tree.current_scene != route:fail("Acceptance must inspect the actual default scene");return
 await tree.process_frame
 if not route.demo_mode or route.room_id != "terminal_room" or route.actions.get_child_count() != 2:
  fail("Release did not start the terminal demo");return
 if route.find_child("BackdropWash",true,false) != null:fail("Release skipped baked backdrop wash installation");return
 var spills = JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/terminal-spill-index.json"))
 if not spills is Dictionary or spills.size() != 7:fail("Release terminal spill catalog is missing");return
 for name in spills:
  var mesh = route.find_child(name,true,false) as MeshInstance3D
  if mesh == null:fail("Release terminal spill receiver is missing");return
  for surface in range(mesh.mesh.get_surface_count()):
   var material = mesh.get_active_material(surface) as ShaderMaterial
   if material == null or material.get_shader_parameter("use_terminal_spill") != true:
    fail("Release skipped terminal spill installation: " + str(name));return
 for size in [Vector2i(1410,600),Vector2i(390,844),requested_size]:
  window.size = size
  for frame in range(8):await tree.process_frame;RenderingServer.force_draw()
  for action in route.actions.get_children():
   if not Rect2(Vector2.ZERO,Vector2(size)).encloses(action.get_global_rect()):fail("Release resize clipped a terminal action");return
 if "--screenshots-dir" in args:
  var directory = args[args.find("--screenshots-dir")+1]
  if DirAccess.make_dir_recursive_absolute(directory) != OK:fail("Cannot create release screenshot directory");return
  var suffix = "portrait" if portrait else "desktop"
  if window.get_texture().get_image().save_png(directory + "/release-" + suffix + ".png") != OK:fail("Cannot save release startup image");return
 print("DEMO_RELEASE_STARTUP_PASS: configured terminal, baked wash, seven spills and resize")
 if not await click(button(route.actions,"Read the terminal")) or not route.output_label.text.contains("Follow the lanterns"):
  fail("Release pointer did not activate terminal");return
 if not await enter(button(route.actions,"Enter the garden")) or not await arrive(route,"rockery_gate"):
  fail("Release keyboard did not leave cell");return
 if not await click(button(route.actions,"Follow the lanterns")) or not await arrive(route,"qinfang_ting"):
  fail("Release pointer did not reach pavilion");return
 if not await enter(button(route.actions,"Cast at the table")) or not route.has_node("ReadingResult"):
  fail("Release keyboard did not cast");return
 if not await click(route.get_node("ReadingResult").find_child("CloseReading",true,false)):
  fail("Release pointer did not close reading");return
 await tree.process_frame
 if not await enter(button(route.actions,"Finish the demo")) or not route.has_node("DemoFinale"):
  fail("Release keyboard did not open finale");return
 if not await click(route.get_node("DemoFinale").find_child("ReplayDemo",true,false)):
  fail("Release pointer did not activate replay");return
 await tree.process_frame
 if route.room_id != "terminal_room" or route.demo_has_reading or route.has_node("DemoFinale"):
  fail("Release replay did not reset demo");return
 print("DEMO_RELEASE_ACCEPTANCE_PASS: pointer and keyboard through release route and replay")
 for player in route.demo_audio.players.values():player.stop()
 await tree.create_timer(.2).timeout
 tree.quit(0)
