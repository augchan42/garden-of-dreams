extends SceneTree
var records = {}
var occluders = []
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 Engine.max_fps = 60
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 var mobile = "--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 for name in ["SITE_terminal-cells_MAT_plaster_rock","SITE_terminal-cells_MAT_wall_general","SITE_rockery-gate_MAT_plaster_rock"]:
  var mesh=route.find_child(name,true,false) as MeshInstance3D
  if mesh==null:continue
  for surface in range(mesh.mesh.get_surface_count()):
   var arrays=mesh.mesh.surface_get_arrays(surface)
   var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
   var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
   var unique=PackedVector3Array()
   var map={}
   var remap=PackedInt32Array()
   for vertex in vertices:
    if not map.has(vertex):
     map[vertex]=unique.size()
     unique.append(vertex)
    remap.append(map[vertex])
   for index in range(indices.size()):indices[index]=remap[indices[index]]
   vertices=unique
   var resource=ArrayOccluder3D.new()
   resource.set_arrays(vertices,indices)
   var occluder=OccluderInstance3D.new()
   occluder.name="ExactOpaque_"+name+"_"+str(surface)
   occluder.occluder=resource
   route.add_child(occluder)
   occluder.global_transform=mesh.global_transform
   occluders.append({"mesh":name,"vertices":vertices.size(),"triangles":indices.size()/3,"transform":str(mesh.global_transform)})
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.0)
 var positions=preload("res://tests/profile_all_viewport_budgets.gd").POSITIONS
 var directory="res://occlusion-portrait-moving" if mobile else "res://occlusion-desktop-moving"
 DirAccess.make_dir_recursive_absolute(directory)
 for room in ["terminal_room","rockery_gate"]:
  route.player.position=positions[room]+Vector3(0,.04,0)
  route._arrive(room,true)
  await create_timer(1.8).timeout
  records[room]={}
  for variant in ["disabled","enabled","disabled_repeat"]:
   root.use_occlusion_culling=variant=="enabled"
   var camera=root.get_camera_3d()
   var original_transform=camera.transform
   var frames_start=Engine.get_frames_drawn()
   for frame in range(60):
    await process_frame
    camera.position.x=original_transform.origin.x+sin(float(frame))*.0001
    RenderingServer.force_draw()
   camera.transform=original_transform
   await process_frame
   RenderingServer.force_draw()
   var image=root.get_texture().get_image()
   var path=directory+"/"+room+"-"+variant+".png"
   assert(image.save_png(path)==OK)
   var pixel_hash=HashingContext.new()
   pixel_hash.start(HashingContext.HASH_SHA256)
   pixel_hash.update(image.get_data())
   records[room][variant]={"pixel_sha256":pixel_hash.finish().hex_encode(),"file_sha256":FileAccess.get_sha256(path),"draws":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME),"drawn_frames":Engine.get_frames_drawn(),"automatic_frames_elapsed":Engine.get_frames_drawn()-frames_start}
  print("EXACT_SOLID_OCCLUSION ",room," ",records[room])
  FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify({"scope":"Isolated exact opaque source-mesh occluder candidate; stationary fixed-clock pixels and native counters only. Not adopted, sustained or phone evidence.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"occluders":occluders,"rooms":records},"  "))
 quit(0)
