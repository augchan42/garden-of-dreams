extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var world=Node3D.new();root.add_child(world)
 for z in [-3.6,3.6]:
  var platform=StaticBody3D.new();var shape=CollisionShape3D.new();var box=BoxShape3D.new()
  box.size=Vector3(2.4,.2,1.2);shape.shape=box;shape.position=Vector3(0,-.1,z)
  platform.add_child(shape);world.add_child(platform)
 for variant in ["stream","pond","lotus","embankment","wood_bridge","stone_bridge"]:
  for suffix in ["","_LOD1"]:
   var kit=load("res://assets/kits/water/KIT_water_"+variant+suffix+".glb").instantiate();world.add_child(kit)
   var shapes=kit.find_children("*","CollisionShape3D",true,false)
   var expected=3 if variant.ends_with("bridge") else (1 if variant=="embankment" else 0)
   if shapes.size()!=expected:
    push_error("Unexpected collision count: "+variant+suffix);quit(1);return
   if variant in ["stream","pond"]:
    var mesh=kit.find_children("*","MeshInstance3D",true,false)[0]
    if mesh.get_active_material(0)!=load("res://materials/water.tres"):
     push_error("Water shader missing: "+variant+suffix);quit(1);return
   if variant.ends_with("bridge"):
    var visitor=CharacterBody3D.new();var shape=CollisionShape3D.new();var capsule=CapsuleShape3D.new()
    capsule.radius=.22;capsule.height=1.65;shape.shape=capsule;shape.position.y=.83
    visitor.add_child(shape);world.add_child(visitor);visitor.position=Vector3(0,.03,3.6)
    var max_height=0.0
    for target in [Vector3(0,0,-3.6),Vector3(0,0,3.6)]:
     var reached=false
     for i in range(360):
      await physics_frame
      var direction=target-visitor.position;direction.y=0
      if direction.length()<.1:reached=true;break
      visitor.velocity.x=0;visitor.velocity.z=direction.normalized().z*1.6
      visitor.velocity.y-=20.0/Engine.physics_ticks_per_second
      visitor.move_and_slide();max_height=maxf(max_height,visitor.position.y)
      if visitor.position.y<-.2:break
     if not reached:
      push_error("Bridge traversal failed: "+variant+suffix+str(visitor.position));quit(1);return
    if variant=="stone_bridge" and max_height<.45:
     push_error("Visitor did not follow the stone arch");quit(1);return
    visitor.position=Vector3(0,.04 if variant=="wood_bridge" else .55,0)
    for i in range(80):
     await physics_frame
     visitor.velocity=Vector3(1.6,-1,0);visitor.move_and_slide()
    if visitor.position.x>.65:
     push_error("Bridge railing did not block the visitor");quit(1);return
    visitor.queue_free()
   kit.queue_free();await process_frame
 print("WATER_KIT_PASS: surface shaders, collision counts, bridge approaches/returns, arch rise and rail blocking at both LODs")
 quit(0)
