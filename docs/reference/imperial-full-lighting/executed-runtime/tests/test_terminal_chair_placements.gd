extends SceneTree
func _initialize() -> void:
 create_timer(10).timeout.connect(func():push_error("Chair placement check timed out");quit(1))
 call_deferred("run")
func run() -> void:
 var scene=(load("res://assets/garden-of-dreams.glb") as PackedScene).instantiate() as Node3D
 root.add_child(scene)
 var colliders=0
 for node in scene.find_children("*","CollisionShape3D",true,false):
  if str(node.get_parent().name).begins_with("COL_terminal_chair_"):colliders+=1
 assert(colliders==12,str(colliders))
 var batch=scene.find_child("SITE_terminal-cells_MAT_props_atlas*",true,false) as MeshInstance3D
 assert(batch!=null and batch.mesh.surface_get_arrays(0)[Mesh.ARRAY_INDEX].size()/3==5808)
 await physics_frame
 await physics_frame
 var space=scene.get_world_3d().direct_space_state
 var capsule=CapsuleShape3D.new();capsule.radius=.22;capsule.height=1.65
 for x in [-6.5,-3.9,-1.3,1.3,3.9,6.5]:
  var seat=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,.8,37.4),Vector3(x,.3,37.4)))
  assert(not seat.is_empty() and str(seat.collider.name).begins_with("COL_terminal_chair_"))
  assert(abs(seat.position.y-.46)<.005)
  var query=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.transform.origin=Vector3(x,.86,37.98)
  assert(space.intersect_shape(query).is_empty(),"Standing point intersects chair or cell")
  var floor_hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,.2,37.98),Vector3(x,-.2,37.98)))
  assert(not floor_hit.is_empty() and abs(floor_hit.position.y)<.005)
  assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,1.1,37.98),Vector3(x,1.1,38.5))).is_empty())
 var markers=scene.find_children("TRG_cell_seat*","Node3D",true,false)
 assert(markers.size()==6)
 for marker in markers:assert(abs(marker.position.z-37.4)<.005 and abs(marker.position.y)<.005)
 scene.queue_free()
 print("TERMINAL_CHAIR_PLACEMENTS_PASS: six seats, 12 colliders, preserved markers, clear standing points and doorways")
 quit(0)
