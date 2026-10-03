extends SceneTree
const VARIANTS=["cyclorama_moonlit","cyclorama_dusk","cyclorama_mist","studio_wall","floor_boards","fog_plane","gel_frame"]
var surfaces=0
var colliders=0
var lights=0
func _initialize() -> void:
 create_timer(15).timeout.connect(func():push_error("Stage kit check timed out");quit(1))
 call_deferred("run")
func run() -> void:
 var atlas=load("res://materials/stage/atlas.tres") as ORMMaterial3D
 assert(atlas.albedo_texture!=null and atlas.albedo_texture.get_width()==512)
 assert(atlas.orm_texture!=null and atlas.orm_texture.get_width()==256)
 for variant in VARIANTS:
  var bounds:AABB
  for suffix in ["","_LOD1"]:
   var scene=(load("res://assets/kits/stage/KIT_stage_%s%s.glb"%[variant,suffix]) as PackedScene).instantiate() as Node3D
   var render=scene.find_child("*render*",true,false) as MeshInstance3D
   assert(render!=null)
   assert(render.mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV2].size()>0)
   if suffix=="":bounds=render.get_aabb()
   else:
    assert(bounds.position.distance_to(render.get_aabb().position)<.035,variant)
    assert(bounds.end.distance_to(render.get_aabb().end)<.035,variant)
   var expected_surfaces=2 if variant.begins_with("cyclorama_") or variant=="gel_frame" else 1
   assert(render.mesh.get_surface_count()==expected_surfaces)
   for i in range(render.mesh.get_surface_count()):
    var material=render.get_active_material(i)
    assert(material==render.mesh.surface_get_material(i))
    assert(material.resource_path.begins_with("res://materials/stage/"))
    surfaces+=1
   if variant.begins_with("cyclorama_"):
    var sky=load("res://materials/stage/"+variant+".tres") as StandardMaterial3D
    assert(render.get_active_material(0)==sky)
    assert(sky.shading_mode==BaseMaterial3D.SHADING_MODE_UNSHADED and sky.albedo_texture.get_width()==1024)
    assert(abs(sky.albedo_color.r-.6)<.001)
    assert(render.get_active_material(1)==atlas)
   elif variant=="studio_wall":
    var black=render.get_active_material(0) as StandardMaterial3D
    assert(black.shading_mode==BaseMaterial3D.SHADING_MODE_UNSHADED and black.albedo_color==Color.BLACK)
   elif variant=="floor_boards":assert(render.get_active_material(0)==atlas)
   elif variant=="fog_plane":assert(render.get_active_material(0) is ShaderMaterial)
   elif variant=="gel_frame":
    assert(render.get_active_material(0)==atlas)
    assert((render.get_active_material(1) as StandardMaterial3D).transparency==BaseMaterial3D.TRANSPARENCY_ALPHA)
   var shapes=scene.find_children("*","CollisionShape3D",true,false)
   assert(shapes.size()==(8 if variant.begins_with("cyclorama_") else 0 if variant=="fog_plane" else 1))
   colliders+=shapes.size()
   lights+=scene.find_children("*","Light3D",true,false).size()
   root.add_child(scene)
   await physics_frame
   await physics_frame
   var from_point=Vector3(0,1.5,1)
   var to_point=Vector3(0,1.5,-1)
   if variant.begins_with("cyclorama_"):from_point=Vector3(0,3.5,2);to_point=Vector3(0,3.5,-1)
   elif variant=="floor_boards" or variant=="fog_plane":from_point=Vector3(0,.8,0);to_point=Vector3(0,-.3,0)
   elif variant=="gel_frame":from_point=Vector3(0,.5,1);to_point=Vector3(0,.5,-1)
   var hit=scene.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(from_point,to_point))
   assert(hit.is_empty() if variant=="fog_plane" else not hit.is_empty(),variant+" collision ray failed")
   if variant=="floor_boards":assert(abs(hit.position.y)<.005)
   scene.free()
 assert(surfaces==22 and colliders==54 and lights==0)
 print("STAGE_RUNTIME_PASS: 14 models, 22 shared material surfaces, 54 colliders, matching bounds, no embedded lights")
 quit(0)
