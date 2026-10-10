extends SceneTree
var route
var occluders=[]
func _initialize():
 create_timer(180).timeout.connect(func():push_error("CPU diagnostic deadline");quit(1))
 call_deferred("run")
func run():
 Engine.max_fps=60
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 install_exact()
 var positions=preload("res://tests/profile_all_viewport_budgets.gd").POSITIONS
 var report={"scope":"Native M2 paired stationary process-CPU and automatic render-frame diagnostics; host measures process user+system CPU at phase markers. Not phone/sustained/final-art acceptance.","phases":{},"pid":OS.get_process_id(),"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb")}
 for room in ["terminal_room","rockery_gate","qinfang_ting"]:
  route.player.position=positions[room]+Vector3(0,.04,0)
  route._arrive(room,true)
  await create_timer(1.8).timeout
  var original_transform=route.camera.transform
  for variant in ["disabled","enabled","disabled_repeat"]:
   root.use_occlusion_culling=variant=="enabled"
   for frame in range(120):
    await process_frame
    route.camera.position.x=original_transform.origin.x+sin(float(frame))*.0001
   var label=room+"-"+variant
   var automatic_start=Engine.get_frames_drawn()
   var intervals=[]
   var draws=0
   var primitives=0
   var previous=Time.get_ticks_usec()
   print("CPU_PHASE_START ",label)
   for frame in range(480):
    await process_frame
    var now=Time.get_ticks_usec()
    intervals.append(float(now-previous)/1000.0)
    previous=now
    route.camera.position.x=original_transform.origin.x+sin(float(frame))*.0001
    draws=maxi(draws,RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))
    primitives=maxi(primitives,RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME))
   intervals.sort()
   var row={"sample_frames":480,"automatic_render_frames":Engine.get_frames_drawn()-automatic_start,"global_draw_calls_max":draws,"global_primitives_max":primitives,"interval_p50_ms":intervals[240],"interval_p95_ms":intervals[456],"interval_max_ms":intervals[-1]}
   assert(row.automatic_render_frames>=460,"Automatic render frame clock failed")
   report.phases[label]=row
   print("CPU_PHASE_END ",label," ",JSON.stringify(row))
   FileAccess.open("res://occlusion-cpu-native.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
   await create_timer(.25).timeout
  route.camera.transform=original_transform
 print("OCCLUSION_CPU_NATIVE_PASS phases=",report.phases.size())
 quit()
func install_exact():
 for name in ["SITE_terminal-cells_MAT_plaster_rock","SITE_terminal-cells_MAT_backstage","SITE_terminal-cells_MAT_stage_backstage","SITE_rockery-gate_MAT_pavilion_atlas","SITE_rockery-gate_MAT_plaster_rock"]:
  var mesh=route.find_child(name,true,false) as MeshInstance3D
  assert(mesh!=null,"Missing exact structural mesh: "+name)
  for surface in range(mesh.mesh.get_surface_count()):
   var material=mesh.get_active_material(surface)
   print("OCCLUDER_MATERIAL ",name," ",material.get_class()," shader=",material.shader.resource_path if material is ShaderMaterial else "none"," transparency=",material.transparency if material is BaseMaterial3D else -1)
   assert((material is ShaderMaterial and material.shader==load("res://shaders/baked_diffuse.gdshader")) or (material is BaseMaterial3D and material.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED),"Candidate requires verified opaque material: "+name)
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
