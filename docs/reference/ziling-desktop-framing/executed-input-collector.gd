extends SceneTree
var route
var output:=""
func _initialize()->void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 create_timer(60).timeout.connect(func():push_error("Desktop input extraction deadline");quit(1))
 call_deferred("run")
func vertices(node:MeshInstance3D,geometry:Mesh=null)->Array:
 assert(node!=null)
 if geometry==null:geometry=node.mesh
 var points:Array=[]
 for surface in range(geometry.get_surface_count()):
  for p in geometry.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
   var v:Vector3=node.global_transform*p;points.append([v.x,v.y,v.z])
 return points
func run()->void:
 assert(output!="")
 root.size=Vector2i(1410,600)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route._configure_ui_scale(false,160)
 for f in range(16):await process_frame
 route.player.position=route.ISLAND_PATH[-1]+Vector3(0,.03,0);route._arrive("ziling_zhou",true)
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
 for f in range(16):await process_frame
 var subjects:Dictionary={}
 for pair in [["island","SITE_ziling-zhou_MAT_plaster_rock"],["bridge","SITE_ziling-zhou_MAT_pavilion_atlas"],["pavilion_roof","SITE_ouxiang-xie_MAT_rooftile"]]:subjects[pair[0]]=vertices(route.find_child(pair[1],true,false))
 subjects.reeds=[]
 for plant in route.get_node("FloraLOD").plants:
  if str(plant.node.name).begins_with("HERO_flora_ziling"):
   subjects.reeds.append_array(vertices(plant.node,plant.base));subjects.reeds.append_array(vertices(plant.node,plant.lower))
 assert(subjects.island.size()==2112 and subjects.bridge.size()==1296 and subjects.pavilion_roof.size()==8116 and subjects.reeds.size()==48320)
 var bounds:Dictionary={}
 for name in subjects:
  var lo:=Vector2(INF,INF);var hi:=Vector2(-INF,-INF)
  for p in subjects[name]:
   var pixel:Vector2=route.camera.unproject_position(Vector3(p[0],p[1],p[2]));lo=lo.min(pixel);hi=hi.max(pixel)
  bounds[name]={"low":[lo.x,lo.y],"high":[hi.x,hi.y]}
 var pos:Vector3=route.camera.global_position;var b:Basis=route.camera.global_transform.basis
 var file:=FileAccess.open(output,FileAccess.WRITE);assert(file!=null)
 file.store_string(JSON.stringify({"status":"actual_native_desktop_inputs_extracted","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("res://tests/collect_ziling_desktop_inputs.gd"),"camera_position":[pos.x,pos.y,pos.z],"camera_basis_columns":[[b.x.x,b.x.y,b.x.z],[b.y.x,b.y.y,b.y.z],[b.z.x,b.z.y,b.z.z]],"fov":route.camera.fov,"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"header_bottom":route.status.get_global_rect().end.y,"panel_top":route.command_panel.get_global_rect().position.y,"subjects":subjects,"native_projected_bounds":bounds,"scope":"Actual imported world vertices and camera basis, including both reed LOD meshes. No rendered appearance or proposed-camera acceptance."}," ")+"\n");file.close();print("ZILING_DESKTOP_INPUTS_PASS ",subjects.reeds.size());quit(0)
