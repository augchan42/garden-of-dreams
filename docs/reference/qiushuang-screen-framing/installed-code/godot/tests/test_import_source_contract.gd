extends SceneTree

# Supply scene.glb, source-contract.json and output.json after --.
# Run before and after a forced cold reimport in an isolated project.
var scene: Node3D
var contract: Dictionary
var expected: Dictionary

func _initialize() -> void:
 create_timer(60).timeout.connect(func():push_error("Import contract check timed out");quit(1))
 call_deferred("run")

func matrix_values(t: Transform3D) -> Array:
 return [t.basis.x.x,t.basis.x.y,t.basis.x.z,0,
  t.basis.y.x,t.basis.y.y,t.basis.y.z,0,
  t.basis.z.x,t.basis.z.y,t.basis.z.z,0,t.origin.x,t.origin.y,t.origin.z,1]

func same_matrix(t: Transform3D, values: Array) -> bool:
 var actual=matrix_values(t)
 for i in range(16):
  if abs(actual[i]-float(values[i]))>0.00005:return false
 return true

func vertex_key(v: Vector3) -> String:
 return "%.6f,%.6f,%.6f" % [v.x,v.y,v.z]

func triangle_keys(faces: PackedVector3Array) -> Array:
 var result=[]
 for i in range(0,faces.size(),3):
  var corners=[vertex_key(faces[i]),vertex_key(faces[i+1]),vertex_key(faces[i+2])]
  corners.sort()
  result.append(";".join(corners))
 result.sort()
 return result

func check_structure() -> String:
 var cameras=scene.find_children("*","Camera3D",true,false)
 var shapes=scene.find_children("*","CollisionShape3D",true,false)
 var meshes=scene.find_children("*","MeshInstance3D",true,false)
 if cameras.size()!=contract.cameras.size():return "Camera count changed"
 if shapes.size()!=contract.colliders.size():return "Collider count changed"
 if meshes.size()!=int(contract.render_meshes):return "Render mesh count changed"
 expected={"cameras":{},"colliders":{},"markers":{},"mesh_arrays":{}}
 for camera in cameras:
  if not contract.cameras.has(str(camera.name)):return "Unknown camera: "+str(camera.name)
  var record=contract.cameras[str(camera.name)]
  if not same_matrix(camera.global_transform,record.transform):return "Camera transform changed: "+str(camera.name)
  if camera.projection!=Camera3D.PROJECTION_PERSPECTIVE:return "Camera projection changed"
  if abs(camera.fov-rad_to_deg(float(record.yfov)))>0.0001:return "Camera FOV changed: "+str(camera.name)
  if abs(camera.near-float(record.znear))>0.00001 or abs(camera.far-float(record.zfar))>0.0001:return "Camera clipping changed"
  expected.cameras[str(camera.name)]={"matrix":matrix_values(camera.global_transform),"fov":camera.fov,
   "near":camera.near,"far":camera.far,"keep_aspect":camera.keep_aspect}
 for shape in shapes:
  var body=shape.get_parent() as StaticBody3D
  if body==null or not shape.shape is ConcavePolygonShape3D:return "Wrong collider type"
  var name=str(body.name)
  if not contract.colliders.has(name):return "Unknown collider: "+name
  var record=contract.colliders[name]
  if not same_matrix(shape.global_transform,record.transform):return "Collider transform changed: "+name
  var original=PackedVector3Array()
  for point in record.faces:original.append(Vector3(point[0],point[1],point[2]))
  var faces=shape.shape.get_faces()
  if triangle_keys(original)!=triangle_keys(faces):return "Collider surface changed: "+name
  expected.colliders[name]={"matrix":matrix_values(shape.global_transform),"triangle_keys":triangle_keys(faces),
   "collision_layer":body.collision_layer,"collision_mask":body.collision_mask,"disabled":shape.disabled}
 for name in contract.markers:
  var marker=scene.find_child(name,true,false) as Node3D
  if marker==null:return "Missing room marker: "+name
  if not same_matrix(marker.global_transform,contract.markers[name].transform):return "Room marker transform changed: "+name
  if marker.get_meta("extras",{})!=contract.markers[name].extras:return "Room marker metadata changed: "+name
  expected.markers[name]={"matrix":matrix_values(marker.global_transform),"extras":marker.get_meta("extras",{})}
 for mesh in meshes:
  var digest=HashingContext.new()
  digest.start(HashingContext.HASH_SHA256)
  for surface in range(mesh.mesh.get_surface_count()):digest.update(var_to_bytes(mesh.mesh.surface_get_arrays(surface)))
  expected.mesh_arrays[str(mesh.name)]={"array_sha256":digest.finish().hex_encode(),"matrix":matrix_values(mesh.global_transform),
   "surfaces":mesh.mesh.get_surface_count()}
 return ""

func check_physics() -> String:
 var shapes=scene.find_children("*","CollisionShape3D",true,false)
 var all_rids: Array[RID]=[]
 for shape in shapes:all_rids.append(shape.get_parent().get_rid())
 var space=scene.get_world_3d().direct_space_state
 for shape in shapes:
  var faces=shape.shape.get_faces()
  var area=0.0
  var chosen=0
  for i in range(0,faces.size(),3):
   var size=(faces[i+1]-faces[i]).cross(faces[i+2]-faces[i]).length_squared()
   if size>area:area=size;chosen=i
  if area<0.0000000001:return "Degenerate collider: "+str(shape.get_parent().name)
  var a=shape.global_transform*faces[chosen]
  var b=shape.global_transform*faces[chosen+1]
  var c=shape.global_transform*faces[chosen+2]
  var center=(a+b+c)/3
  # Godot's imported triangle faces use clockwise front-face winding.
  var normal=(c-a).cross(b-a).normalized()
  var query=PhysicsRayQueryParameters3D.create(center+normal*0.05,center-normal*0.05)
  var excluded=all_rids.duplicate()
  excluded.erase(shape.get_parent().get_rid())
  query.exclude=excluded
  query.hit_back_faces=true
  var hit=space.intersect_ray(query)
  if hit.is_empty() or hit.collider!=shape.get_parent():return "Collider does not block its test ray: "+str(shape.get_parent().name)
  if hit.position.distance_to(center)>0.0001:return "Collision surface displaced: "+str(shape.get_parent().name)
 return ""

func run() -> void:
 var args=OS.get_cmdline_user_args()
 assert(args.size()>=3,"Supply source scene, contract and output paths")
 contract=JSON.parse_string(FileAccess.get_file_as_string(args[1]))
 assert(FileAccess.get_sha256(args[0])==contract.source_glb_sha256,"Stale import contract")
 scene=load(args[0]).instantiate()
 root.add_child(scene)
 await physics_frame
 await physics_frame
 # Negative cases edit only the temporary instance, never saved assets.
 if args.has("--corrupt-camera"):scene.find_children("*","Camera3D",true,false)[0].fov+=1
 if args.has("--corrupt-collider"):
  var shape=scene.find_children("*","CollisionShape3D",true,false)[0]
  var changed=shape.shape.get_faces();changed[0].x+=0.1;shape.shape.set_faces(changed)
 if args.has("--corrupt-marker"):
  var marker=scene.find_child(contract.markers.keys()[0],true,false)
  marker.set_meta("extras",{"room_id":"invalid_import_room"})
 var error=check_structure()
 if error.is_empty():error=check_physics()
 if not error.is_empty():
  scene.free();push_error(error);quit(1);return
 var report={"source_glb_sha256":contract.source_glb_sha256,
  "scope":"Actual source-to-Godot camera/collider/marker contracts and one isolated physics ray per collider, plus mesh-array snapshots for forced reimport comparison. Not continuous traversal, rendered materials or lighting acceptance.",
  "cameras_checked":contract.cameras.size(),"colliders_checked":contract.colliders.size(),
  "marker_metadata_checked":contract.markers.size(),"physics_rays_passed":contract.colliders.size(),
  "render_meshes_snapshotted":expected.mesh_arrays.size(),"snapshot":expected,"passed":true}
 var output=FileAccess.open(args[2],FileAccess.WRITE)
 assert(output!=null)
 output.store_string(JSON.stringify(report,"  ")+"\n");output.close()
 scene.free()
 print("IMPORT_SOURCE_CONTRACT_PASS ",report.cameras_checked," cameras; ",report.colliders_checked," collision surfaces/rays; ",report.marker_metadata_checked," marker records")
 quit(0)
