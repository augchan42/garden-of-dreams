extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route._arrive("qinfang_ting",true)
 for i in range(8):await process_frame
 var scroll=route.action_scroll
 if scroll.size.y>153 or scroll.get_global_rect().position.y<root.size.y*.5:
  push_error("Portrait actions cover too much of the scene");quit(1);return
 if route.actions.get_child_count()!=route.ROOMS["qinfang_ting"].actions.size():
  push_error("Missing pavilion commands");quit(1);return
 scroll.scroll_vertical=10000
 for i in range(3):await process_frame
 var last=route.actions.get_child(-1)
 if not scroll.get_global_rect().intersects(last.get_global_rect()):
  push_error("Final command is not scrollable into view");quit(1);return
 root.size=Vector2i(1410,600)
 for i in range(8):await process_frame
 if scroll.get_v_scroll_bar().visible:
  push_error("Desktop commands should fit without scrolling");quit(1);return
 print("QINFANG_LAYOUT_PASS: portrait height, complete command list, scroll to last command, desktop resize")
 quit(0)
