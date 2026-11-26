extends SceneTree
var route
var failures:Array[String]=[]
var completions=0
func _initialize() -> void:
 if DisplayServer.get_name()=="headless":quit(1);return
 call_deferred("run")
func check(ok: bool,message: String) -> void:
 if not ok:failures.append(message);push_error(message)
func run() -> void:
 root.size=Vector2i(1410,600)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await create_timer(.5).timeout
 route._arrive("qinfang_ting",true)
 await create_timer(.5).timeout
 route._arrive("xiaoxiang_guan")
 var arrival_tween:Tween=route.camera_tween
 arrival_tween.finished.connect(func():completions+=1)
 await create_timer(.35).timeout
 check(arrival_tween.is_valid() and arrival_tween.is_running(),"Control layout cancelled the arrival animation")
 await create_timer(1.3).timeout
 check(completions==1,"Arrival camera did not emit its completion signal")
 check(route.room_id=="xiaoxiang_guan" and not route.travelling,"Transition changed room state")
 print("XIAOXIANG_CAMERA_TRANSITION_RESULT ",failures.size()," failures")
 quit(0 if failures.is_empty() else 1)
