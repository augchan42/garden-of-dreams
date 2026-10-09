extends SceneTree

func _initialize() -> void:call_deferred("run")

func click(button:Button) -> void:
 # Match the demo pointer harness: resize fitting and native mouse events
 # can move the target or replace hover between the two click edges.
 var previous=Rect2()
 var stable_frames=0
 for i in range(30):
  await process_frame
  RenderingServer.force_draw()
  var bounds=button.get_global_rect()
  stable_frames=stable_frames+1 if bounds==previous else 0
  previous=bounds
  if stable_frames>=2:break
 assert(stable_frames>=2,"Pond pointer target did not settle")
 var position=previous.get_center()
 var motion=InputEventMouseMotion.new()
 motion.position=position
 for down in [true,false]:
  root.push_input(motion,true)
  var event=InputEventMouseButton.new()
  event.button_index=MOUSE_BUTTON_LEFT
  event.position=position
  event.pressed=down
  root.push_input(event,true)
  await process_frame

func run() -> void:
 root.size=Vector2i(1410,600)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1)
 route._arrive("aojing_guan",true)
 for i in range(120):
  await physics_frame
  if route.player.is_on_floor():break
 assert(route.player.is_on_floor(),"The visitor must have floor support before opening the view")
 await physics_frame
 var ledge=route.player.position
 var action:Button
 for button in route.actions.get_children():
  if button.text=="Look across the pond":action=button
 assert(action!=null)
 await click(action)
 assert(route.pond_view_active and not route.command_panel.visible)
 assert(route.pond_return_button.visible and not route.input.editable and not route.travelling)
 await create_timer(1.6).timeout
 assert(route.player.position.distance_to(ledge)<.02,"The visitor must stay on the dry ledge")
 for size in [Vector2i(1410,600),Vector2i(390,844)]:
  root.size=size
  for i in range(3):await process_frame
  var candidates=route.find_children("CAM_aojing-guan_reflection*","Camera3D",true,false).filter(func(c):return ("portrait" in str(c.name))==(size.x<size.y))
  assert(candidates.size()==1)
  var source=candidates[0] as Camera3D
  assert(source.global_position.distance_to(route.camera.global_position)<.001)
  assert(source.global_basis.is_equal_approx(route.camera.global_basis))
  for point in [Vector3(26,.9,12.325),Vector3(20.5,-1.1,14)]:
   assert(source.unproject_position(point).distance_to(route.camera.unproject_position(point))<.05)
  assert(root.get_visible_rect().encloses(route.pond_return_button.get_global_rect()))
  assert(route.pond_return_button.size.y>=44)
  assert(route.camera.global_position.y>-1.1+route.camera.near)
 await click(route.pond_return_button)
 for i in range(3):await process_frame
 assert(not route.pond_view_active and route.command_panel.visible and route.input.editable)
 assert(root.get_visible_rect().encloses(route.command_panel.get_global_rect()),
  "The restored command panel must fit the viewport")
 route.execute_command("reflection")
 await process_frame
 var escape=InputEventKey.new()
 escape.keycode=KEY_ESCAPE
 escape.pressed=true
 root.push_input(escape,true)
 await process_frame
 assert(not route.pond_view_active and route.command_panel.visible)
 assert(route.player.position.distance_to(ledge)<.02)
 route.execute_command("reflection")
 root.size=Vector2i(1410,600)
 route._arrive("yihong_yuan",true)
 for i in range(3):await process_frame
 assert(not route.pond_view_active and not route.pond_return_button.visible,
  "A deferred resize must not reopen a pond view after leaving")
 assert(is_equal_approx(route.camera.fov,55.0))
 print("POND_VIEW_PASS: pointer entry/return, Escape, portrait resize, authored projection, stationary dry-ledge visitor and clean next-room state")
 quit()
