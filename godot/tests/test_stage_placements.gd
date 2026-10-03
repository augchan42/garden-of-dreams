extends SceneTree
func _initialize() -> void:
 create_timer(10).timeout.connect(func():push_error("Stage placement check timed out");quit(1))
 call_deferred("run")
func run() -> void:
 var scene=(load("res://assets/garden-of-dreams.glb") as PackedScene).instantiate() as Node3D;root.add_child(scene)
 var nodes:Array[Node]=[scene];var stage_batches=0;var triangles=0;var colliders=0
 var atlas=load("res://materials/stage/atlas.tres");var fog=load("res://materials/stage/fog.tres");var black=load("res://materials/stage/backstage.tres");var gel=load("res://materials/stage/gel.tres")
 assert((black as StandardMaterial3D).shading_mode==BaseMaterial3D.SHADING_MODE_UNSHADED and (black as StandardMaterial3D).albedo_color==Color.BLACK)
 while not nodes.is_empty():
  var node=nodes.pop_back();nodes.append_array(node.get_children())
  if node is CollisionShape3D and str(node.get_parent().name).begins_with("COL_stage_placed_"):colliders+=1
  if node is MeshInstance3D and str(node.name).contains("MAT_stage_") and not str(node.name).contains("MAT_stage_canvas"):
   stage_batches+=1
   for i in range(node.mesh.get_surface_count()):
    var material=node.get_active_material(i)
    assert(material==node.mesh.surface_get_material(i))
    assert(material in [atlas,fog,black,gel])
    var arrays=node.mesh.surface_get_arrays(i);assert(not arrays[Mesh.ARRAY_TEX_UV2].is_empty());triangles+=arrays[Mesh.ARRAY_INDEX].size()/3
 assert(stage_batches==6 and colliders==8 and triangles==14704,str([stage_batches,colliders,triangles]))
 await physics_frame;await physics_frame
 var space=scene.get_world_3d().direct_space_state
 for x in [-6.5,-3.9,-1.3,1.3,3.9,6.5]:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x+.9,.1,37),Vector3(x+.9,-.2,37)))
  assert(not hit.is_empty() and abs(hit.position.y)<.005 and str(hit.collider.name).begins_with("COL_cell_floor"))
  var wall=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,1.5,39.7),Vector3(x,1.5,40.6)))
  assert(not wall.is_empty() and str(wall.collider.name).begins_with("COL_stage_placed_"))
  assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x-.5,1.1,39.25),Vector3(x+.5,1.1,39.25))).is_empty())
 scene.queue_free();print("STAGE_PLACEMENTS_PASS: 35 modules, 6 shared batches, 8 colliders, unchanged floor height and clear corridor")
 quit(0)
