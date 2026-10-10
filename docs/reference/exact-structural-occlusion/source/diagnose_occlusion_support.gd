extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 Engine.max_fps=60
 var scene=Node3D.new()
 root.add_child(scene)
 var camera=Camera3D.new()
 camera.position.z=5
 scene.add_child(camera)
 camera.current=true
 var wall=MeshInstance3D.new()
 var box=BoxMesh.new()
 box.size=Vector3(5,5,.2)
 wall.mesh=box
 wall.position.z=1
 scene.add_child(wall)
 var arrays=box.surface_get_arrays(0)
 var resource=BoxOccluder3D.new()
 resource.size=Vector3(5,5,.2)
 var occluder=OccluderInstance3D.new()
 occluder.occluder=resource
 scene.add_child(occluder)
 occluder.global_transform=wall.global_transform
 print("OCCLUSION_SETUP vertices=",resource.get_vertices().size()," indices=",resource.get_indices().size()," occluder_world=",occluder.get_world_3d().scenario," scene_world=",scene.get_world_3d().scenario," occluder_visible=",occluder.visible)
 for index in range(50):
  var mesh=MeshInstance3D.new()
  mesh.mesh=BoxMesh.new()
  mesh.material_override=StandardMaterial3D.new()
  scene.add_child(mesh)
 var report={}
 for enabled in [false,true,false]:
  root.use_occlusion_culling=enabled
  print("OCCLUSION_PROPERTY ",root.use_occlusion_culling)
  for frame in range(90):
   await process_frame
   camera.position.x=sin(float(frame))*.0001
   RenderingServer.force_draw()
  var draws=RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)
  print("OCCLUSION_SUPPORT_CONTROL enabled=",enabled," draws=",draws," frames_drawn=",Engine.get_frames_drawn()," frame_counter=",Engine.get_process_frames())
  report[str(enabled)]=draws
 FileAccess.open("res://occlusion-support.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 quit(0)
