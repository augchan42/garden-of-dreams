extends SceneTree

var report_path=""
var expected_source="f411ed55c88d03ce1c94f54baa176ada7605123103b45b4134eb2f1966f84577"
var facts={}

func _initialize():
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--report="):report_path=argument.trim_prefix("--report=")
  if argument.begins_with("--expected-source="):expected_source=argument.trim_prefix("--expected-source=")
 create_timer(90).timeout.connect(func():finish(false,"AOJING_GROUND_NATIVE_DEADLINE"))
 call_deferred("run")

func finish(passed:bool,error:String=""):
 var result={"status":"passed" if passed else "failed","facts":facts,"error":error,"scope":"Actual imported normal-route canvas geometry and matching baked material; native quantization bounds only, no final art or tour/device acceptance."}
 if not report_path.is_empty():
  var file=FileAccess.open(report_path,FileAccess.WRITE)
  file.store_string(JSON.stringify(result," ")+"\n")
 if passed:print("AOJING_GROUND_NATIVE_PASS ",JSON.stringify(facts))
 else:push_error(error)
 quit(0 if passed else 1)

func run():
 facts.source_glb_sha256=FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 if facts.source_glb_sha256!=expected_source:finish(false,"Ground geometry test source does not match the explicitly expected GLB");return
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var catalog=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 if not preload("res://runtime/baked_materials.gd").source_matches(catalog):finish(false,"Ground geometry fixture requires actual matching full lightmaps");return
 var node=route.find_child("SITE_stage_MAT_stage_canvas",true,false) as MeshInstance3D
 if node==null or node.mesh.get_surface_count()!=1:finish(false,"Actual single canvas batch is missing");return
 var material=node.get_active_material(0) as ShaderMaterial
 if material==null or not material.get_shader_parameter("use_lightmap") or material.get_shader_parameter("lightmap")==null:finish(false,"Actual canvas bake is not bound");return
 var arrays=node.mesh.surface_get_arrays(0)
 var vertices=arrays[Mesh.ARRAY_VERTEX]
 var indices=arrays[Mesh.ARRAY_INDEX]
 var normals=arrays[Mesh.ARRAY_NORMAL]
 var normal_basis=node.global_transform.basis.inverse().transposed()
 var box=node.mesh.get_aabb()
 # The importer packs positions; allow two 16-bit position steps, using the
 # actual canvas extent. This is a geometry bound, never a pixel tolerance.
 var extent=max(box.size.x,max(box.size.y,box.size.z))
 var tolerance=2.0*extent/65535.0+0.00001
 var triangles=0
 var top_triangles=0
 var top_area=0.0
 var lo=Vector3(18,-.63,14)
 var hi=Vector3(20.2,-.13,21)
 for offset in range(0,indices.size(),3):
  var points=[]
  var inside=true
  for j in range(3):
   var point=node.global_transform*vertices[indices[offset+j]]
   points.append(point)
   for axis in range(3):inside=inside and point[axis]>=lo[axis]-tolerance and point[axis]<=hi[axis]+tolerance
  if not inside:continue
  triangles+=1
  var cross_normal=(points[1]-points[0]).cross(points[2]-points[0])
  var shading_normal=Vector3.ZERO
  for j in range(3):shading_normal+=(normal_basis*normals[indices[offset+j]]).normalized()
  shading_normal=shading_normal.normalized()
  # Godot imports triangle fronts clockwise: cross points opposite the
  # outward shading normal. Check every closed-box face, not only the top.
  if cross_normal.dot(shading_normal)>=0:finish(false,"Imported infill winding violates Godot clockwise fronts");return
  var face_center=(points[0]+points[1]+points[2])/3.0
  if shading_normal.dot(face_center-(lo+hi)/2.0)<=0:finish(false,"Imported infill shading normal is inward");return
  if abs(points[0].y-hi.y)<=tolerance and abs(points[1].y-hi.y)<=tolerance and abs(points[2].y-hi.y)<=tolerance:
   var normal=(points[1]-points[0]).cross(points[2]-points[0])
   if normal.y>=0 or shading_normal.y<=0:finish(false,"Imported canvas infill top front or shading normal is inward");return
   top_triangles+=1
   top_area+=normal.length()/2.0
 facts.merge({"added_box_triangles":triangles,"added_top_triangles":top_triangles,"added_top_area_m2":top_area,"position_quantization_bound_m":tolerance,"canvas_lightmap_bound":true,"clockwise_outward_faces_checked":triangles})
 if triangles!=12 or top_triangles!=2:finish(false,"Actual imported west infill is missing or incomplete");return
 var area_bound=2.0*tolerance*(2.2+7.0)+4.0*tolerance*tolerance
 if abs(top_area-15.4)>area_bound:finish(false,"Imported infill top area exceeds its position quantization bound");return
 finish(true)
