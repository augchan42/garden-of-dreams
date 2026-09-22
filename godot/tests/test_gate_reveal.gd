extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await physics_frame
 var authored=route.find_children("CAM_gate_reveal_*","Camera3D",true,false).filter(func(c):return "reveal_slide" in c.name or "reveal_lift" in c.name or "reveal_wide" in c.name)
 if authored.size()!=3:
  push_error("Three authored reveal cameras must survive import");quit(1);return
 for camera in authored:
  if abs(camera.fov-55)>.01:
   push_error("Authored reveal camera FOV differs from runtime");quit(1);return
 route.player.position=Vector3(0,.04,15.45);route._arrive("rockery_gate",true)
 route._travel([Vector3(0,0,15.45),Vector3(0,0,12),Vector3(0,0,7)],"qinfang_ting")
 await physics_frame;await physics_frame
 if not route.gate_reveal_active or not route.gate_reveal_done or route.command_panel.visible:
  push_error("Outbound tunnel exit did not trigger reveal");quit(1);return
 var start=route.player.position
 await create_timer(2).timeout
 if Vector2(route.player.position.x-start.x,route.player.position.z-start.z).length()>.02:
  push_error("Visitor moved during the reveal");quit(1);return
 await create_timer(2.2).timeout
 if route.gate_reveal_active or not route.command_panel.visible or route.camera.position.distance_to(route.GATE_REVEAL_RAIL[-1])>.02:
  push_error("Reveal did not finish at the wide camera");quit(1);return
 await create_timer(.5).timeout
 if route.player.position.z>=start.z-.3 or not route.travelling:
  push_error("Travel did not resume after reveal");quit(1);return
 route.travelling=false;route._arrive("qinfang_ting",true)
 route.player.position=Vector3(0,.04,15)
 route._travel([Vector3(0,0,15),Vector3(0,0,19)],"rockery_gate")
 await physics_frame;await physics_frame
 if route.gate_reveal_active or route.gate_reveal_done:
  push_error("Return travel incorrectly triggered the reveal");quit(1);return
 print("GATE_REVEAL_PASS: outbound trigger, stationary visitor, wide endpoint, resumed travel and no return trigger")
 quit(0)
