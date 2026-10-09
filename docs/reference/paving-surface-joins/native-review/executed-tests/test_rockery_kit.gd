extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var world=Node3D.new();root.add_child(world)
 var floor_body=StaticBody3D.new();var floor_shape=CollisionShape3D.new();var box=BoxShape3D.new()
 box.size=Vector3(12,.2,12);floor_shape.shape=box;floor_shape.position.y=-.1
 floor_body.add_child(floor_shape);world.add_child(floor_body)
 var holes={"small":[Vector2(0,.58)],"medium":[Vector2(-.22,.65),Vector2(.2,1.4)],"large":[Vector2(-.35,.75),Vector2(.36,1.65),Vector2(-.2,2.65)],"cliff":[Vector2(-1.6,1.3),Vector2(1.5,2.2)],"arch":[Vector2(-1.75,1.15),Vector2(1.7,.75)],"tunnel":[]}
 for variant in ["small","medium","large","arch","tunnel","cliff"]:
  for suffix in ["","_LOD1"]:
   var kit=load("res://assets/kits/rockery/KIT_rockery_"+variant+suffix+".glb").instantiate();world.add_child(kit)
   await physics_frame
   var shapes=kit.find_children("*","CollisionShape3D",true,false)
   if shapes.size()!=1 or not shapes[0].shape is ConcavePolygonShape3D:
    push_error("Expected one concave rock collision: "+variant+suffix);quit(1);return
   var space=world.get_world_3d().direct_space_state
   for hole in holes[variant]:
    var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(hole.x,hole.y,5),Vector3(hole.x,hole.y,-5)))
    if not hit.is_empty():
     push_error("Piercing blocked: "+variant+suffix);quit(1);return
   var solid_point=Vector2(1.8,.2) if variant in ["arch","tunnel"] else Vector2(0,.1)
   var solid=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(solid_point.x,solid_point.y,5),Vector3(solid_point.x,solid_point.y,-5)))
   if solid.is_empty():
    push_error("Rock body has no collision: "+variant+suffix);quit(1);return
   if variant in ["arch","tunnel"]:
    var visitor=CharacterBody3D.new();var shape=CollisionShape3D.new();var capsule=CapsuleShape3D.new()
    capsule.radius=.22;capsule.height=1.65;shape.shape=capsule;shape.position.y=.83
    visitor.add_child(shape);world.add_child(visitor)
    var end=1.3 if variant=="arch" else 2.6
    for x in [-.6,.6]:
     visitor.position=Vector3(x,.03,end);visitor.velocity=Vector3.ZERO
     for target in [-end,end]:
      var reached=false
      for i in range(260):
       await physics_frame
       if abs(visitor.position.z-target)<.08:reached=true;break
       visitor.velocity=Vector3(0,-1,sign(target-visitor.position.z)*2.0);visitor.move_and_slide()
       if visitor.position.y<-.1:break
      if not reached:
       push_error("Rock passage failed: "+variant+suffix+str(visitor.position));quit(1);return
    visitor.queue_free()
   kit.queue_free();await process_frame
 print("ROCKERY_PHYSICS_PASS: pierced collision, solid bodies and offset passage traversal in both directions at both LODs")
 quit(0)
