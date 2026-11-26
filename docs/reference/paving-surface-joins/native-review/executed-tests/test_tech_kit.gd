extends SceneTree
const VARIANTS=["crt_amber","crt_green","monitor_bank","cable_run","cell_door","terminal_desk"]
var meshes=0
var collisions=0
var lights=0
var material:ORMMaterial3D
func _initialize() -> void:
 create_timer(10).timeout.connect(func():push_error("Tech test timed out");quit(1))
 call_deferred("run")
func inspect(node:Node) -> void:
 if node is MeshInstance3D:
  meshes+=1
  assert(node.mesh.get_surface_count()==1)
  assert(node.mesh.surface_get_material(0)==material)
  assert(node.get_active_material(0)==material)
  assert(node.mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV2].size()>0)
 if node is CollisionShape3D:
  collisions+=1
  assert(node.shape!=null)
 if node is Light3D:lights+=1
 for child in node.get_children():inspect(child)
func mesh_in(node:Node) -> MeshInstance3D:
 if node is MeshInstance3D:return node
 for child in node.get_children():
  var mesh=mesh_in(child)
  if mesh!=null:return mesh
 return null
func run() -> void:
 material=load("res://materials/tech_atlas.tres")
 assert(material.albedo_texture.get_width()==512)
 assert(material.orm_texture.get_width()==256)
 assert(material.emission_texture.get_width()==512)
 assert(material.emission_enabled and material.emission_operator==BaseMaterial3D.EMISSION_OP_MULTIPLY)
 assert(material.emission_energy_multiplier==4.0)
 for variant in VARIANTS:
  var base: AABB
  for suffix in ["","_LOD1"]:
   var scene=(load("res://assets/kits/tech/KIT_tech_%s%s.glb"%[variant,suffix]) as PackedScene).instantiate()
   var before=collisions
   inspect(scene)
   assert(collisions-before=={"crt_amber":1,"crt_green":1,"monitor_bank":1,"cable_run":0,"cell_door":3,"terminal_desk":1}[variant])
   var bounds=mesh_in(scene).mesh.get_aabb()
   if suffix=="":base=bounds
   else:
    assert(base.position.distance_to(bounds.position)<.035)
    assert(base.size.distance_to(bounds.size)<.035)
   scene.free()
 assert(meshes==12 and collisions==14 and lights==0)
 var door=(load("res://assets/kits/tech/KIT_tech_cell_door.glb") as PackedScene).instantiate()
 root.add_child(door)
 await physics_frame
 await physics_frame
 var space=door.get_world_3d().direct_space_state
 assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(0,1.1,-1),Vector3(0,1.1,1))).is_empty(),"Open doorway is blocked")
 for x in [-.61,.61]:
  assert(not space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,1.1,-1),Vector3(x,1.1,1))).is_empty(),"Door frame lost collision")
 door.queue_free()
 print("TECH_RUNTIME_PASS: 12 models, shared PBR material, 14 colliders, clear door opening, no practical lights")
 quit(0)
