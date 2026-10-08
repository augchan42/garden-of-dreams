extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate();route.site_bakes_enabled=false;root.add_child(route);await physics_frame
 var space=route.get_world_3d().direct_space_state
 var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-17,1,-12.5),Vector3(-14,1,-12.5)))
 assert(not hit.is_empty() and "COL_hengwu_rock" in str(hit.collider.name),"Compact rock lost its collider")
 var clear=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-17,2.3,-12.5),Vector3(-14,2.3,-12.5)))
 assert(clear.is_empty(),"Old tall collider remains above compact stone")
 var body:=CharacterBody3D.new();var shape:=CollisionShape3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.22;capsule.height=1.65;shape.shape=capsule;shape.position.y=.83;body.add_child(shape);root.add_child(body);body.position=Vector3(-17,.03,-12.5)
 for tick in range(120):
  await physics_frame
  body.velocity=Vector3(2,-2,0);body.move_and_slide()
 assert(body.position.x < -16.3 and body.position.x > -16.8,"Visitor capsule passed through or stopped at misplaced rock")
 assert(body.is_on_floor() and body.position.y>-.05,"Collider test lost floor support")
 print("COMPACT_ROCK_PHYSICS_PASS: world anchor, reduced height and actual visitor capsule blocked at ",body.position);quit(0)
