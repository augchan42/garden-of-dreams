extends SceneTree
var route
var rows:Array=[]
var output:=""
var samples:=0
var misses:=0
func _initialize()->void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 call_deferred("run")
func sample()->void:
 var p:Vector3=route.player.global_position
 var query:=PhysicsRayQueryParameters3D.create(p+Vector3(0,.25,0),p-Vector3(0,.45,0),route.player.collision_mask,[route.player.get_rid()])
 var hit:Dictionary=route.player.get_world_3d().direct_space_state.intersect_ray(query)
 samples+=1
 if hit.is_empty() or p.y<-.3 or (p.y-hit.position.y)>.25:misses+=1
func run()->void:
 assert(output!="")
 route=load("res://runtime/entry_route.tscn").instantiate();route.site_bakes_enabled=false;root.add_child(route)
 for i in range(8):await physics_frame
 route.player.position=Vector3(0,.03,1.8);route._arrive("qinfang_ting",true)
 for i in range(8):await physics_frame
 for step in [["west","ouxiang_xie"],["island","ziling_zhou"],["back","ouxiang_xie"],["back","qinfang_ting"]]:
  route.execute_command(step[0]);var before:=samples
  for i in range(1800):
   await physics_frame;sample()
   if not route.travelling:break
  for i in range(12):await physics_frame;sample()
  rows.append({"command":step[0],"expected_room":step[1],"actual_room":route.room_id,"samples":samples-before,"final_position":str(route.player.position),"travelling":route.travelling})
  assert(route.room_id==step[1] and not route.travelling and route.player.position.y>=-.3)
 var file:=FileAccess.open(output,FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"passed" if misses==0 else "rejected","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("res://tests/test_reed_volume_physics.gd"),"site_bakes_enabled":false,"rows":rows,"floor_samples":samples,"misses":misses,"scope":"Actual native four-leg western approach/island/return with a visitor-excluded downward ray at every physics sample. No source lighting or physical-phone acceptance."}," ")+"\n");file.close()
 assert(misses==0)
 print("REED_VOLUME_PHYSICS_PASS ",samples," support samples, zero misses");quit(0)
