extends SceneTree
func _initialize() -> void:
 create_timer(15).timeout.connect(func():push_error("Enclosure check timed out");quit(1))
 call_deferred("run")
func run() -> void:
 var scene=(load("res://assets/garden-of-dreams.glb") as PackedScene).instantiate() as Node3D;root.add_child(scene)
 var canvas=scene.find_child("SITE_stage_MAT_stage_cyclorama_*",true,false) as MeshInstance3D
 assert(canvas!=null and canvas.mesh.get_surface_count()==2)
 assert(canvas.get_active_material(0)==load("res://materials/stage/cyclorama_moonlit.tres"))
 var arrays=canvas.mesh.surface_get_arrays(0);var vertices=arrays[Mesh.ARRAY_VERTEX];var indices=arrays[Mesh.ARRAY_INDEX];var uv=arrays[Mesh.ARRAY_TEX_UV];var normals=arrays[Mesh.ARRAY_NORMAL]
 for i in range(vertices.size()):
  var p=canvas.global_transform*vertices[i]
  assert(abs(Vector2(p.x,p.z).length()-48.0)<.01,"Canvas vertex is off its 48 m radius: "+str(p)+" transform "+str(canvas.global_transform))
  assert(p.y>=-2.001 and p.y<=20.001)
  assert(uv[i].x>=-.001 and uv[i].x<=.701,"Canvas must not repeat the painted moon")
 for i in range(0,indices.size(),3):
  var a=canvas.global_transform*vertices[indices[i]];var b=canvas.global_transform*vertices[indices[i+1]];var c=canvas.global_transform*vertices[indices[i+2]]
  var normal=(b-a).cross(c-a);var centre=(a+b+c)/3.0
  # Godot front triangles use clockwise winding; vertex normals face inward.
  assert(normal.dot(Vector3(centre.x,0,centre.z))>0,"Painted face winding must face into the garden")
  for index in [indices[i],indices[i+1],indices[i+2]]:
   var n=canvas.global_transform.basis*normals[index]
   assert(n.dot(Vector3(centre.x,0,centre.z))<0,"Painted normals must face inward")
 var colliders=scene.find_children("COL_stage_enclosure_*","StaticBody3D",true,false)
 assert(colliders.size()==64)
 await physics_frame;await physics_frame
 var space=scene.get_world_3d().direct_space_state
 for i in range(120):
  var angle=float(i)*TAU/120.0;var direction=Vector3(sin(angle),0,cos(angle))
  # Start beyond buildings and mountain flats, then check the perimeter.
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(direction*46.0+Vector3(0,12,0),direction*50.0+Vector3(0,12,0)))
  assert(not hit.is_empty() and str(hit.collider.name).begins_with("COL_stage_enclosure_"),"Missing perimeter collision at "+str(i))
  assert(abs(Vector2(hit.position.x,hit.position.z).length()-48.0)<.35)
 assert(scene.find_child("SITE_stage_MAT_painted_moon*",true,false)!=null)
 print("STAGE_ENCLOSURE_PASS: inward painted shell at 48 m, 64 proxies, 120 perimeter rays, one preserved moon")
 scene.queue_free();quit(0)
