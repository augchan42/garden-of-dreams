extends SceneTree

var output := ""
var original := ""

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg.begins_with("--original="):original=arg.trim_prefix("--original=")
 call_deferred("run")

func run() -> void:
 assert(output!="" and original!="")
 var samples: Array=JSON.parse_string(FileAccess.get_file_as_string(original)).rows[0].samples
 var scene=load("res://assets/garden-of-dreams.glb").instantiate()
 root.add_child(scene)
 var rows: Array=[]
 for name in ["SITE_longcui-an_MAT_plaster_rock","SITE_stage_MAT_plaster_rock"]:
  var node=scene.find_child(name,true,false) as MeshInstance3D
  assert(node!=null)
  var surfaces: Array=[]
  for surface in range(node.mesh.get_surface_count()):
   var arrays=node.mesh.surface_get_arrays(surface)
   var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
   var indices: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
   var hits: Array=[]
   var min_height:=INF
   var max_height:=-INF
   for vertex in vertices:
    var y:float=(node.global_transform*vertex).y
    min_height=minf(min_height,y)
    max_height=maxf(max_height,y)
   for sample in samples:
    var o:Vector3=Vector3(sample.ray_origin[0],sample.ray_origin[1],sample.ray_origin[2])
    var d:Vector3=Vector3(sample.ray_normal[0],sample.ray_normal[1],sample.ray_normal[2])
    var ray_hits: Array=[]
    for start in range(0,indices.size(),3):
     var a:Vector3=node.global_transform*vertices[indices[start]]
     var b:Vector3=node.global_transform*vertices[indices[start+1]]
     var c:Vector3=node.global_transform*vertices[indices[start+2]]
     var hit=Geometry3D.ray_intersects_triangle(o,d,a,b,c)
     if hit!=null:
      var normal:Vector3=(b-a).cross(c-a).normalized()
      ray_hits.append({"distance":o.distance_to(hit),"hit_height":hit.y,"triangle_heights":[a.y,b.y,c.y],"normal_y":normal.y})
    ray_hits.sort_custom(func(a,b):return a.distance<b.distance)
    hits.append({"pixel":sample.pixel,"hits":ray_hits})
   surfaces.append({"surface":surface,"format":node.mesh.surface_get_format(surface),"min_height":min_height,"max_height":max_height,"samples":hits})
  rows.append({"node":name,"transform":str(node.global_transform),"surfaces":surfaces})
 var file=FileAccess.open(output,FileAccess.WRITE)
 file.store_string(JSON.stringify({"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"rows":rows,"scope":"Actual imported render vertices and ray intersections. Diagnostic only; no runtime, source or material edits."}," ")+"\n")
 file.close()
 print("IMPORTED_FLOOR_DIAGNOSTIC_RECORDED")
 quit(0)
