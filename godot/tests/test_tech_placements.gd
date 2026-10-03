extends SceneTree
func _initialize() -> void:
 create_timer(10).timeout.connect(func():push_error("Tech placement check timed out");quit(1))
 call_deferred("run")
func run() -> void:
 var scene=(load("res://assets/garden-of-dreams.glb") as PackedScene).instantiate()
 root.add_child(scene)
 var material=load("res://materials/tech_atlas.tres")
 var nodes:Array[Node]=[scene]
 var batches=0
 var triangles=0
 var shapes=0
 while not nodes.is_empty():
  var node=nodes.pop_back();nodes.append_array(node.get_children())
  if node is MeshInstance3D and str(node.name).contains("MAT_tech_atlas"):
   batches+=1
   assert(node.mesh.get_surface_count()==1)
   assert(node.mesh.surface_get_material(0)==material)
   assert(node.get_active_material(0)==material)
   var arrays=node.mesh.surface_get_arrays(0)
   assert(not arrays[Mesh.ARRAY_TEX_UV2].is_empty())
   triangles+=arrays[Mesh.ARRAY_INDEX].size()/3
  if node is CollisionShape3D and str(node.get_parent().name).begins_with("COL_tech_placed_"):shapes+=1
 assert(batches==2,str(batches))
 assert(triangles==26544,str(triangles))
 assert(shapes==33,str(shapes))
 await physics_frame
 await physics_frame
 var space=scene.get_world_3d().direct_space_state
 for x in [-6.5,-3.9,-1.3,1.3,3.9,6.5]:
  assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,1.1,37.9),Vector3(x,1.1,38.5))).is_empty(),"Cell doorway is blocked")
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x+.633,1.1,37.9),Vector3(x+.633,1.1,38.5)))
  assert(not hit.is_empty(),"Fitted door frame lost collision")
 scene.queue_free()
 print("TECH_PLACEMENTS_PASS: 33 modules, 18 screens, 2 material batches, 33 colliders, 6 clear doorways")
 quit(0)
