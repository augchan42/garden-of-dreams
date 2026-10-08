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
var canopy_mode = false
var source_canopy_mode = false

func make_canopy() -> MeshInstance3D:
 var canvas=route.find_child("SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas",true,false) as MeshInstance3D
 assert(canvas!=null)
 var tool=SurfaceTool.new()
 tool.begin(Mesh.PRIMITIVE_TRIANGLES)
 var material:ShaderMaterial
 var edges=0
 for surface in range(canvas.mesh.get_surface_count()):
  var current=canvas.get_active_material(surface)
  if not current is ShaderMaterial or not current.get_shader_parameter("source_unshaded"):continue
  material=current.duplicate()
  material.set_shader_parameter("use_lightmap",false)
  material.set_shader_parameter("use_backdrop_wash",false)
  var arrays=canvas.mesh.surface_get_arrays(surface)
  var vertices=arrays[Mesh.ARRAY_VERTEX]
  var uv=arrays[Mesh.ARRAY_TEX_UV]
  var indices=arrays[Mesh.ARRAY_INDEX]
  for t in range(0,indices.size(),3):
   var rim=[]
   for k in range(3):
    var i=indices[t+k]
    if absf(vertices[i].y-20)<.001 and absf(Vector2(vertices[i].x,vertices[i].z).length()-48)<.02:rim.append(i)
   if rim.size()!=2:continue
   edges+=1
   var rings=[[1.0,20.0],[.875,27.0],[.625,33.0],[.3125,37.0],[0.0,38.0]]
   for ring in range(rings.size()-1):
    var points=[]
    var coords=[]
    for pair in [[rim[0],ring],[rim[1],ring],[rim[1],ring+1],[rim[0],ring+1]]:
     var source:Vector3=vertices[pair[0]]
     var ratio:float=rings[pair[1]][0]
     points.append(Vector3(source.x*ratio,rings[pair[1]][1],source.z*ratio))
     coords.append(Vector2(.35+(uv[pair[0]].x-.35)*ratio,uv[pair[0]].y))
    for triangle in ([[0,1,2]] if ring==rings.size()-2 else [[0,1,2],[0,2,3]]):
     for corner in triangle:
      tool.set_uv(coords[corner])
      tool.add_vertex(points[corner])
 assert(edges>0 and material!=null)
 tool.generate_normals()
 tool.set_material(material)
 var canopy=MeshInstance3D.new()
 canopy.name="PortraitCanopyProposal"
 canopy.mesh=tool.commit()
 canopy.layers=6
 canopy.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 route.add_child(canopy)
 canopy.global_transform=canvas.global_transform
 canopy.set_meta("proposal_edges",edges)
 return canopy

func _initialize() -> void:call_deferred("run")

func run() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-directory="):directory=arg.trim_prefix("--output-directory=")
  if arg=="--canopy":canopy_mode=true
  if arg=="--source-canopy":
   canopy_mode=true
   source_canopy_mode=true
 if directory.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Portrait room probe requires native graphics and an output directory")
  quit(1)
  return
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(390,844)
 route=load("res://runtime/entry_route.tscn").instantiate()
 if source_canopy_mode:route.site_bakes_enabled=false
 root.add_child(route)
 route.set_process(false)
 route.set_physics_process(false)
 var canopy:MeshInstance3D
 if source_canopy_mode:
  canopy=route.find_child("SITE_stage_MAT_stage_canopy_paint",true,false) as MeshInstance3D
  assert(canopy!=null and canopy.get_meta("extras",{}).get("godot_cast_shadow",true)==false)
  # Match the existing cyclorama's shared unshaded runtime paint. These are
  # explicit fixture settings; production import/bake adoption remains open.
  var source=load("res://materials/stage/cyclorama_moonlit.tres")
  var paint=preload("res://runtime/baked_materials.gd").material_from_source(source)
  paint.set_shader_parameter("use_lightmap",false)
  paint.set_shader_parameter("use_backdrop_wash",false)
  canopy.material_override=paint
  canopy.layers=6
  canopy.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  canopy.set_meta("proposal_edges",320)
 elif canopy_mode:canopy=make_canopy()
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
  # Imported paint shader uses cull_disabled. Match rendered faces in this
  # visual-coverage helper; this is not a visitor collision repair.
  shape.shape.backface_collision=true
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
 var report={"scope":"Native portrait camera counterfactuals for eight affected rooms, sampled opaque visual-geometry rays and captured views. Helper colliders use an isolated mask. Not source edits, production camera adoption, continuous traversal, performance or final art acceptance.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"probe_sha256":FileAccess.get_sha256("res://tests/probe_portrait_room_views.gd"),"visual_ray_backface_collision":true,"opaque_helper_meshes":opaque_count,"views":{}}
 var rooms=VIEWS.duplicate()
 if canopy_mode:
  report.scope="Native painted-canopy geometry counterfactual with unchanged production arrival cameras. Proposed surface follows exact current canvas rim edges, curves inward to 38 m, has no shadows and uses existing unshaded paint without old lightmaps/wash. Not authored Blender source, fresh lighting, adoption, performance or final art acceptance."
  var canopy_arrays=canopy.mesh.surface_get_arrays(0)
  report.canopy_triangles=canopy_arrays[Mesh.ARRAY_INDEX].size()/3 if canopy_arrays[Mesh.ARRAY_INDEX]!=null else canopy_arrays[Mesh.ARRAY_VERTEX].size()/3
  report.canopy_rim_edges=canopy.get_meta("proposal_edges")
  if source_canopy_mode:
   report.scope="Actual separately authored/exported Blender canopy imported in isolated Godot fixture, unchanged arrival cameras, old site/wash bakes disabled. Canopy explicitly uses existing cyclorama shared unshaded runtime paint and no-shadow metadata in this fixture. Not production importer/baker shadow semantics, fresh lighting, adoption, performance or final paint acceptance."
  var reflection=route._reflection_view()
  rooms.merge({"terminal_room":[Vector3(-1.3,1.6,38.7),Vector3(-1.3,1.1,36.5),Vector3(-1.3,0,37.4)],"qinfang_ting":[Vector3(6,6.98,20),Vector3(0,1.8,0),Vector3(0,0,1.8)],"ouxiang_xie":[Vector3(-15,5,10),Vector3(-23,1.8,0),Vector3(-23,0,0)],"ziling_zhou":[Vector3(-40,3,6),Vector3(-34,.6,0),Vector3(-35.4,0,0)],"tubi_tang":[Vector3(16,10,-20),Vector3(7,4.9,-32),Vector3(7,4,-31)],"aojing_guan":[reflection[0],reflection[1],Vector3(26,-.65,13.1)]})
 for room in rooms:
  route.player.position=rooms[room][2]+Vector3(0,.04,0)
  route._arrive(room,true)
  await create_timer(.25).timeout
  var original=route.camera.transform
  var original_fov=route.camera.fov
  var original_fit=route.camera.keep_aspect
  var target:Vector3=rooms[room][1]
  var variants=["baseline","canopy"] if canopy_mode else ["baseline","vertical-48","vertical-44","horizontal-36-back","vertical-48-back"]
  for variant in variants:
   if canopy_mode:
    canopy.visible=variant=="canopy"
    var body=helpers.get_node("Probe_"+str(canopy.name)) as StaticBody3D
    body.collision_layer=RAY_MASK if canopy.visible else 0
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
