extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func fail(message:String) -> void:
 push_error(message);quit(1)
func run() -> void:
 var world=Node3D.new()
 root.add_child(world)
 var floor_body=StaticBody3D.new()
 var floor_shape=CollisionShape3D.new()
 var floor_box=BoxShape3D.new()
 floor_box.size=Vector3(12,.2,12)
 floor_shape.shape=floor_box;floor_shape.position.y=-.1
 floor_body.add_child(floor_shape);world.add_child(floor_body)
 for suffix in ["","_LOD1"]:
  # Verify every imported part has one collision shape and blocks a ray at its body.
  for item in ["roof_hex","roof_square","post","bracket","eave_strip","bench"]:
   var kit=load("res://assets/kits/pavilion/KIT_pavilion_"+item+suffix+".glb").instantiate()
   world.add_child(kit)
   if kit.find_children("*","CollisionShape3D",true,false).size()!=1:
    fail("Incorrect collision count: "+item+suffix);return
   await physics_frame
   var height={"roof_hex":.3,"roof_square":.3,"post":1.5,"bracket":.2,"eave_strip":.02,"bench":.5}[item]
   var query=PhysicsRayQueryParameters3D.create(Vector3(0,height,5),Vector3(0,height,-5))
   var hit=world.get_world_3d().direct_space_state.intersect_ray(query)
   if hit.is_empty():
    fail("Missing collision: "+item+suffix);return
   kit.queue_free();await process_frame
  for roof_name in ["roof_hex","roof_square"]:
   var assembly=Node3D.new();world.add_child(assembly)
   var roof=load("res://assets/kits/pavilion/KIT_pavilion_"+roof_name+suffix+".glb").instantiate()
   assembly.add_child(roof);roof.position.y=3.58
   var ports=roof.find_children("PORT_post_*","Node3D",true,false)
   if ports.size()!=(6 if roof_name=="roof_hex" else 4):
    fail("Missing roof mounting ports");return
   for port in ports:
    var post=load("res://assets/kits/pavilion/KIT_pavilion_post"+suffix+".glb").instantiate()
    assembly.add_child(post);post.position=Vector3(port.position.x,0,port.position.z)
    var bracket=load("res://assets/kits/pavilion/KIT_pavilion_bracket"+suffix+".glb").instantiate()
    assembly.add_child(bracket);bracket.position=post.position+Vector3(0,3.1,0)
   var visitor=CharacterBody3D.new()
   var shape=CollisionShape3D.new();var capsule=CapsuleShape3D.new()
   capsule.radius=.22;capsule.height=1.65;shape.shape=capsule;shape.position.y=.83
   visitor.add_child(shape);world.add_child(visitor);visitor.position=Vector3(-4,.02,0)
   for i in range(310):
    await physics_frame
    visitor.velocity=Vector3(1.6,-1,0);visitor.move_and_slide()
   if visitor.position.x<3.9 or visitor.position.y<-.1:
    fail("Assembled pavilion obstructed: "+roof_name+suffix+str(visitor.position));return
   visitor.queue_free();assembly.queue_free();await process_frame
 print("PAVILION_PHYSICS_PASS: six parts, both LODs, roof mounting ports and assembled passage")
 quit(0)
