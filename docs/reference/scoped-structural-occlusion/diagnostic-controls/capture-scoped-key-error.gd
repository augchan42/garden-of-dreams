extends SceneTree
class ControlProducer extends "res://tests/profile_android_full.gd":
 func _ready():pass
 func save_report():pass
var route
var controller
var producer
var occluders=[]
var poses=[]
var records={}
var floor_samples=0
var reveal_frames=0
var arrivals=[]
var directory=""
var shape=""
const DETAILS={"terminal_room":["look","terminal"],"rockery_gate":["look"],"qinfang_ting":["look","table","water"],"ouxiang_xie":["look","tea"],"ziling_zhou":["look","reeds"],"qiushuang_zhai":["look","left","centre","right"],"tubi_tang":["look","overlook"],"hengwu_yuan":["look","read","rocks"],"daoxiang_cun":["look","doors","tools","paddy"],"aojing_guan":["look","doors","reflection"],"longcui_an":["look","doors","incense"],"xiaoxiang_guan":["look","doors","stems"],"yihong_yuan":["look","doors","leaves"],"daguan_lou":["look","doors"]}
func _initialize():
 create_timer(900).timeout.connect(func():push_error("Occlusion path diagnostic deadline");quit(1))
 call_deferred("run")
func add_pose(label,kind):
 var focus=root.gui_get_focus_owner()
 var disabled=[]
 for button in route.actions.get_children():disabled.append(button.disabled)
 poses.append({"label":label,"kind":kind,"room":route.room_id,"player":route.player.position,"camera":route.camera.transform,"fov":route.camera.fov,"aspect":route.camera.keep_aspect,"panel":route.command_panel.visible,"pond_return":route.pond_return_button.visible,"input_editable":route.input.editable,"status":route.status.text,"description":route.output_label.text,"disabled":disabled,"focus":route.get_path_to(focus) if focus!=null else NodePath()})
func run():
 Engine.max_fps=60
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 shape="portrait" if "--mobile" in OS.get_cmdline_user_args() else "desktop"
 if shape=="portrait":root.size=Vector2i(390,844)
 directory="res://occlusion-scoped-path-"+shape
 DirAccess.make_dir_recursive_absolute(directory)
 route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 install_exact()
 controller.set_process(true)
 controller.refresh_scope()
 route.transition_finished.connect(func(room):arrivals.append(room))
 for frame in range(5):await physics_frame
 await create_timer(1.5).timeout
 producer=ControlProducer.new()
 producer.route=route
 producer.report={"status":"native-scoped-candidate","render_budget_scope":"engine_global_all_viewports","samples":{},"budget_results":{},"scope":"Actual four-leg normal-time public round trip using scoped culling and actual full producer; native counter evidence, not target-phone/sustained acceptance."}
 root.add_child(producer)
 producer.set_physics_process(false)
 producer.frame_costs.configure(root)
 producer.begin_sample("public_roundtrip")
 assert(Engine.time_scale==1.0 and Engine.physics_ticks_per_second==60)
 assert(route.room_id=="terminal_room" and not route.travelling)
 var legs=[]
 var tour=[["exit","rockery_gate"],["enter","qinfang_ting"],["back","rockery_gate"],["back","terminal_room"]]
 for leg_index in range(tour.size()):
  var leg=tour[leg_index]
  var origin=route.room_id
  var signals_before=arrivals.size()
  route.execute_command(leg[0])
  assert(route.travelling and route.destination==leg[1])
  var frames=0
  var air_frames=0
  var grounded_before=floor_samples
  while route.travelling and frames<3600:
   await physics_frame
   frames+=1
   assert(Engine.time_scale==1.0 and Engine.physics_ticks_per_second==60)
   air_frames=0 if route.player.is_on_floor() else air_frames+1
   assert(air_frames<=24 and route.player.position.y>-.95,"Actual public route lost floor support")
   if route.player.is_on_floor():
    var query=PhysicsRayQueryParameters3D.create(route.player.position+Vector3(0,.15,0),route.player.position-Vector3(0,.45,0))
    query.exclude=[route.player.get_rid()]
    assert(not route.get_world_3d().direct_space_state.intersect_ray(query).is_empty(),"Grounded centre-ray missed")
    floor_samples+=1
   if route.gate_reveal_active:reveal_frames+=1
   if frames%30==0:add_pose("leg-%d-frame-%d"%[leg_index,frames],"reveal" if route.gate_reveal_active else "travel")
  assert(not route.travelling and route.room_id==leg[1] and arrivals.size()==signals_before+1)
  assert(arrivals.back()==leg[1] and floor_samples>grounded_before)
  await create_timer(1.8).timeout
  assert(route.input.editable and route.command_panel.visible)
  add_pose("leg-%d-arrival"%leg_index,"settled_arrival")
  legs.append({"from":origin,"command":leg[0],"to":leg[1],"physics_frames":frames,"grounded_rays":floor_samples-grounded_before})
  print("OCCLUSION_PUBLIC_LEG_PASS ",leg_index," frames=",frames)
 producer.end_sample()
 producer.set_process(false)
 FileAccess.open(directory+"/actual-producer-roundtrip.json",FileAccess.WRITE).store_string(JSON.stringify(producer.report,"  "))
 print("SCOPED_PUBLIC_ACTUAL_PRODUCER ",JSON.stringify(producer.report.samples.public_roundtrip))
 if not producer.report.budget_results.public_roundtrip.draw_calls_ok or not producer.report.budget_results.public_roundtrip.primitives_ok:
  push_error("Scoped public round trip exceeds actual global frame budget")
  quit(1)
  return
 assert(legs.size()==4 and arrivals.size()==4 and reveal_frames>100)
 var positions=preload("res://tests/profile_all_viewport_budgets.gd").POSITIONS
 for room in DETAILS:
  for command in DETAILS[room]:
   route.player.position=positions[room]+Vector3(0,.04,0)
   route._arrive(room,true)
   route.execute_command(command)
   await create_timer(1.8).timeout
   assert(not route.travelling and route.room_id==room)
   add_pose(room+"-"+command,"public_detail")
 print("OCCLUSION_TRACE_COMPLETE poses=",poses.size()," reveal_frames=",reveal_frames," floor_rays=",floor_samples)
 if route.camera_tween and route.camera_tween.is_valid():route.camera_tween.kill()
 route.process_mode=Node.PROCESS_MODE_DISABLED
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.0)
 for pose in poses:
  route._arrive(pose.room,true)
  route.player.position=pose.player
  route.camera.transform=pose.camera
  route.camera.fov=pose.fov
  route.camera.keep_aspect=pose.aspect
  route.command_panel.visible=pose.panel
  route.pond_return_button.visible=pose.pond_return
  route.input.editable=pose.input_editable
  route.status.text=pose.status
  route.output_label.text=pose.description
  for index in range(route.actions.get_child_count()):route.actions.get_child(index).disabled=pose.disabled[index]
  var focus=root.gui_get_focus_owner()
  if focus!=null:focus.release_focus()
  if not pose.focus.is_empty():route.get_node(pose.focus).grab_focus()
  route.get_node("FloraLOD").update_distance(route.camera.global_position)
  route.get_node("PracticalLights").update_lights()
  route.get_node("PondReflection").update_reflection()
  await process_frame
  var comparison={}
  for variant in ["disabled","enabled","disabled_repeat"]:
   controller.set_process(variant=="enabled")
   controller.refresh_scope()
   var frames_start=Engine.get_frames_drawn()
   for frame in range(24):
    await process_frame
    route.camera.position.x=pose.camera.origin.x+sin(float(frame))*.0001
    RenderingServer.force_draw()
   route.camera.transform=pose.camera
   route.get_node("PondReflection").update_reflection()
   await process_frame
   RenderingServer.force_draw()
   assert(Engine.get_frames_drawn()-frames_start>=20,"Actual render-frame clock stalled")
   var image=root.get_texture().get_image()
   var file=directory+"/"+pose.label+"-"+variant+".png"
   assert(image.save_png(file)==OK)
   var hash=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(image.get_data())
   comparison[variant]={"pixel_sha256":hash.finish().hex_encode(),"file_sha256":FileAccess.get_sha256(file),"draws":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME),"automatic_frames_elapsed":Engine.get_frames_drawn()-frames_start,"occlusion_active":root.use_occlusion_culling}
  records[pose.label]={"kind":pose.kind,"room":pose.room,"camera":var_to_str(pose.camera),"fov":pose.fov,"aspect":pose.aspect,"player":var_to_str(pose.player),"comparisons":comparison}
  assert(comparison.disabled.pixel_sha256==comparison.enabled.pixel_sha256 and comparison.disabled.pixel_sha256==comparison.disabled_repeat.pixel_sha256,"Culling changed pixels: "+pose.label)
  FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify({"scope":"Isolated runtime exact-occluder controller with actual camera-frustum activation. Actual normal-time/60Hz four-leg public cell-gate-pavilion round trip; floor/signals and recorded camera poses. Fixed-clock replay comparisons at travel/reveal poses and public detail endpoints, not continuous per-frame image equality, CPU, phone or sustained acceptance.","shape":shape,"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"fixture_sha256":FileAccess.get_sha256("res://tests/capture_scoped_occlusion_views.gd"),"occluders":occluders,"legs":legs,"arrival_signals":arrivals.slice(0,4),"reveal_frames":reveal_frames,"grounded_rays":floor_samples,"cases":records},"  "))
  print("OCCLUSION_PATH_PIXEL_PASS ",shape," ",pose.label," draws=",comparison.disabled.draws,"/",comparison.enabled.draws)
 print("OCCLUSION_PATH_VIEWS_PASS ",shape," cases=",records.size())
 quit(0)
func install_exact():
 controller=route.get_node("ExactStructuralOcclusion")
 assert(controller.configured)
 for instance in controller.get_children():
  var vertices=instance.occluder.get_vertices()
  var indices=instance.occluder.get_indices()
  occluders.append({"mesh":instance.get_meta("source_mesh"),"vertices":vertices.size(),"triangles":indices.size()/3,"transform":str(instance.global_transform)})
 assert(occluders.size()==5)
