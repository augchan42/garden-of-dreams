extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var world=Node3D.new()
 root.add_child(world)
 var paths={
  "straight":[Vector3(0,0,1.3),Vector3(0,0,-1.3),Vector3(0,0,1.3)],
  "corner":[Vector3(0,0,1.3),Vector3.ZERO,Vector3(1.3,0,0),Vector3.ZERO,Vector3(0,0,1.3)],
  "tee":[Vector3(0,0,1.3),Vector3(0,0,-1.3),Vector3.ZERO,Vector3(1.3,0,0),Vector3.ZERO,Vector3(0,0,1.3)],
  "stair":[Vector3(0,0,1.3),Vector3(0,.6,-1.3),Vector3(0,0,1.3)]}
 for variant in paths:
  for suffix in ["","_LOD1"]:
   var kit=load("res://assets/kits/corridor/KIT_corridor_"+variant+suffix+".glb").instantiate()
   world.add_child(kit)
   var visitor=CharacterBody3D.new()
   var collision=CollisionShape3D.new()
   var capsule=CapsuleShape3D.new()
   capsule.radius=.22;capsule.height=1.65
   collision.shape=capsule;collision.position.y=.83
   visitor.add_child(collision);world.add_child(visitor)
   visitor.position=paths[variant][0]+Vector3(0,.15,0)
   for destination in paths[variant].slice(1):
    var reached=false
    for i in range(240):
     await physics_frame
     var delta=1.0/Engine.physics_ticks_per_second
     var direction=destination-visitor.position;direction.y=0
     if direction.length()<.12:
      reached=true;break
     visitor.velocity.x=direction.normalized().x*1.6
     visitor.velocity.z=direction.normalized().z*1.6
     visitor.velocity.y-=20.0*delta
     visitor.move_and_slide()
     if visitor.position.y<-.25:break
    if not reached:
     push_error("Corridor traversal failed: "+variant+suffix+" at "+str(visitor.position))
     quit(1);return
    if variant=="stair" and destination.y>.5:
     assert(visitor.position.y>.5,"Stair collider must rise to the upper connector")
   visitor.queue_free();kit.queue_free()
   await process_frame
 print("CORRIDOR_PHYSICS_PASS: all four modules, both LODs, all ports and stair ascent/descent")
 quit(0)
