extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var world=Node3D.new()
 root.add_child(world)
 var floor_body=StaticBody3D.new()
 var floor_shape=CollisionShape3D.new()
 var floor_box=BoxShape3D.new()
 floor_box.size=Vector3(8,.2,8)
 floor_shape.shape=floor_box;floor_shape.position.y=-.1
 floor_body.add_child(floor_shape);world.add_child(floor_body)
 for variant in ["bay","moon_gate","vase_gate","window_square","window_diamond","window_ice","window_hex"]:
  for suffix in ["","_LOD1"]:
   var kit=load("res://assets/kits/wall/KIT_wall_"+variant+suffix+".glb").instantiate()
   world.add_child(kit)
   var imported_shapes=kit.find_children("*","CollisionShape3D",true,false)
   if imported_shapes.size()!=1:
    push_error("Expected one collision shape: "+variant+suffix);quit(1);return
   if variant.ends_with("gate") and not imported_shapes[0].shape is ConcavePolygonShape3D:
    push_error("Gate must retain a concave opening");quit(1);return
   var visitor=CharacterBody3D.new()
   var shape=CollisionShape3D.new()
   var capsule=CapsuleShape3D.new()
   capsule.radius=.22;capsule.height=1.65
   shape.shape=capsule;shape.position.y=.83
   visitor.add_child(shape);world.add_child(visitor)
   var gate=variant.ends_with("gate")
   for side in [1.0,-1.0]:
    visitor.position=Vector3(0,.02,side)
    visitor.velocity=Vector3.ZERO
    for i in range(100):
     await physics_frame
     visitor.velocity=Vector3(0,-1,-side*1.6)
     visitor.move_and_slide()
    if gate and visitor.position.z*side>-.8:
     push_error("Gate obstructed: "+variant+suffix+str(visitor.position));quit(1);return
    if not gate and visitor.position.z*side<.3:
     push_error("Wall/window failed to block: "+variant+suffix);quit(1);return
   if gate:
    # The opening must be passable, but its side piers must still block movement.
    for x in [-1.3,1.3]:
     visitor.position=Vector3(x,.02,1)
     for i in range(65):
      await physics_frame
      visitor.velocity=Vector3(0,-1,-1.6)
      visitor.move_and_slide()
     if visitor.position.z<.3:
      push_error("Gate pier failed to block: "+variant+suffix);quit(1);return
   visitor.queue_free();kit.queue_free()
   await process_frame
 print("WALL_PHYSICS_PASS: gates passable and walls/windows blocked from both sides at both LODs")
 quit(0)
