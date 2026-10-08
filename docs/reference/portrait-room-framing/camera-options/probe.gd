extends SceneTree

# Native camera counterfactuals only. No production camera/source changes.
const VIEWS = {
 "rockery_gate": [Vector3(0,1.85,35.7),Vector3(0,1.9,29),Vector3(0,0,32.5)],
 "qiushuang_zhai": [Vector3(22,3.2,-6.8),Vector3(22,1.45,-15.5),Vector3(22,0,-13.5)],
 "hengwu_yuan": [Vector3(-17.5,2.6,-10.5),Vector3(-18,1.1,-15.2),Vector3(-18,0,-14.7)],
 "daguan_lou": [Vector3(5.5,2.5,-13),Vector3(0,2.7,-23),Vector3(0,0,-20.5)],
 "yihong_yuan": [Vector3(18,3.1,5),Vector3(24.3,1.25,1),Vector3(22.6,0,1)],
 "xiaoxiang_guan": [Vector3(-2,2.3,13),Vector3(-8.8,1.6,12.5),Vector3(-6.6,0,13)],
 "longcui_an": [Vector3(-22,2.6,6),Vector3(-25,1.45,12.2),Vector3(-25,0,10.6)],
 "daoxiang_cun": [Vector3(-34,3.4,-13),Vector3(-34,1.7,-22),Vector3(-32,0,-19.3)]
}
const RAY_MASK = 128
var route
var directory = ""

func _initialize() -> void:call_deferred("run")

func run() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-directory="):directory=arg.trim_prefix("--output-directory=")
 if directory.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Portrait room probe requires native graphics and an output directory")
  quit(1)
  return
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(390,844)
 route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.set_process(false)
 route.set_physics_process(false)
 # Test-only physics surfaces match visible opaque triangle geometry. Their
 # isolated mask cannot collide with the visitor; no resource is modified.
 var helpers=Node3D.new()
 route.add_child(helpers)
 var opaque_count=0
 for mesh in route.find_children("*","MeshInstance3D",true,false):
  if not mesh.is_visible_in_tree():continue
  var opaque=true
  for surface in range(mesh.mesh.get_surface_count()):
   var material=mesh.mesh.surface_get_material(surface)
   if material is BaseMaterial3D and material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED:opaque=false
   if material and material.resource_name in ["MAT_water","MAT_aojing_water","MAT_fog_plane"]:opaque=false
  if not opaque:continue
  var body=StaticBody3D.new()
  body.name="Probe_"+str(mesh.name)
  body.collision_layer=RAY_MASK
  body.collision_mask=0
  var shape=CollisionShape3D.new()
  shape.shape=mesh.mesh.create_trimesh_shape()
  body.add_child(shape)
  helpers.add_child(body)
  body.global_transform=mesh.global_transform
  opaque_count+=1
 for i in range(3):await physics_frame
 for mesh in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(mesh.mesh.get_surface_count()):
   var material=mesh.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.0)
 var report={"scope":"Native portrait camera counterfactuals for eight affected rooms, sampled opaque visual-geometry rays and captured views. Helper colliders use an isolated mask. Not source edits, production camera adoption, continuous traversal, performance or final art acceptance.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"probe_sha256":FileAccess.get_sha256("res://tests/probe_portrait_room_views.gd"),"opaque_helper_meshes":opaque_count,"views":{}}
 for room in VIEWS:
  route.player.position=VIEWS[room][2]+Vector3(0,.04,0)
  route._arrive(room,true)
  await create_timer(.25).timeout
  var original=route.camera.transform
  var original_fov=route.camera.fov
  var original_fit=route.camera.keep_aspect
  var target:Vector3=VIEWS[room][1]
  for variant in ["baseline","vertical-48","vertical-44","horizontal-36-back","vertical-48-back"]:
   route.camera.transform=original
   route.camera.keep_aspect=original_fit
   route.camera.fov=original_fov
   if variant.begins_with("vertical"):
    route.camera.keep_aspect=Camera3D.KEEP_HEIGHT
    route.camera.fov=44 if variant=="vertical-44" else 48
   elif variant=="horizontal-36-back":route.camera.fov=36
   var scale=1.55 if variant=="horizontal-36-back" else 1.75 if variant=="vertical-48-back" else 1.0
   var position=target+(original.origin-target)*scale
   route._camera_to(position,target,true)
   await create_timer(.25).timeout
   await RenderingServer.frame_post_draw
   var name=room+"-"+variant
   var path=directory+"/"+name+".png"
   assert(root.get_texture().get_image().save_png(path)==OK)
   var misses=[]
   var hits=[]
   var space=route.get_world_3d().direct_space_state
   for y in [2.0,30.0,65.0]:
    for x in [2.0,49.0,97.0,146.0,195.0,244.0,293.0,341.0,387.0]:
     var pixel=Vector2(x,y)
     var start=route.camera.project_ray_origin(pixel)
     var end=start+route.camera.project_ray_normal(pixel)*160
     var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(start,end,RAY_MASK))
     if hit.is_empty():misses.append([x,y])
     else:hits.append({"pixel":[x,y],"mesh":str(hit.collider.name)})
   report.views[name]={"room_id":room,"variant":variant,"position":[position.x,position.y,position.z],"target":[target.x,target.y,target.z],"fov":route.camera.fov,"fit":route.camera.keep_aspect,"opaque_ray_misses":misses,"opaque_ray_hits":hits,"image_sha256":FileAccess.get_sha256(path),"command_panel_top":route.command_panel.position.y}
 FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 route.queue_free()
 await create_timer(.3).timeout
 print("PORTRAIT_ROOM_PROBE_PASS views=",report.views.size())
 quit(0)
