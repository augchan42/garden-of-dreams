extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route.player.position=Vector3(0,.04,1.8);route._arrive("qinfang_ting",true)
 route.command_panel.hide();route.camera.fov=35
 route._camera_to(Vector3(0,2.15,.8),Vector3(0,.91,0),true)
 for entry in [["solid",[1,1,1,1,1,1]],["broken",[0,0,0,0,0,0]],["alternating",[1,0,1,0,1,0]]]:
  if not route.hexagram_table.set_lines(entry[1]):push_error("Pattern rejected");quit(1);return
  await create_timer(.5).timeout;await RenderingServer.frame_post_draw
  root.get_texture().get_image().save_png("res://../docs/reference/hexagram-"+entry[0]+".png")
  print("HEXAGRAM_RENDER_SAVED ",entry[0])
 quit(0)
