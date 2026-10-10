extends SceneTree

class ControlProducer extends "res://tests/profile_android_full.gd":
 func _ready() -> void:
  pass
 func save_report() -> void:
  pass

class Lights extends Node:
 var lights = []

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 Engine.max_fps = 60
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 var scene = Node3D.new()
 root.add_child(scene)
 var lights = Lights.new()
 lights.name = "PracticalLights"
 scene.add_child(lights)
 var camera = Camera3D.new()
 camera.position.z = 5
 camera.cull_mask = 1
 scene.add_child(camera)
 camera.current = true
 var capture = SubViewport.new()
 capture.size = Vector2i(256,256)
 capture.world_3d = scene.get_world_3d()
 capture.render_target_update_mode = SubViewport.UPDATE_DISABLED
 scene.add_child(capture)
 var mirror_camera = Camera3D.new()
 mirror_camera.position.z = 5
 mirror_camera.cull_mask = 2
 capture.add_child(mirror_camera)
 mirror_camera.current = true
 var meshes = []
 for index in range(152):
  var mesh = MeshInstance3D.new()
  mesh.mesh = BoxMesh.new()
  var material = StandardMaterial3D.new()
  material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
  mesh.material_override = material
  mesh.layers = 1 if index == 0 else 2
  mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  scene.add_child(mesh)
  meshes.append(mesh)
 var producer = ControlProducer.new()
 producer.route = scene
 producer.report = {"status":"control", "samples":{}, "budget_results":{}}
 root.add_child(producer)
 producer.set_physics_process(false)
 producer.frame_costs.configure(root)
 var evidence = {"scope":"Native synthetic two-viewport control of the actual full-phone producer; no phone or garden-performance acceptance.", "samples":{}}
 for variant in ["capture_disabled", "reflection_draw_over_budget", "reflection_primitives_over_budget", "capture_disabled_again", "canvas_control"]:
  var capture_enabled = variant.begins_with("reflection_")
  capture.render_target_update_mode = SubViewport.UPDATE_ALWAYS if capture_enabled else SubViewport.UPDATE_DISABLED
  if variant == "canvas_control":
   var rectangle = ColorRect.new()
   rectangle.size = Vector2(64,64)
   root.add_child(rectangle)
  if variant == "reflection_primitives_over_budget":
   for index in range(2, meshes.size()):meshes[index].visible = false
   var plane = PlaneMesh.new()
   plane.subdivide_width = 400
   plane.subdivide_depth = 400
   meshes[1].mesh = plane
   meshes[1].rotation.x = PI/2
   meshes[1].material_override.cull_mode = BaseMaterial3D.CULL_DISABLED
  for frame in range(20):
   await process_frame
   RenderingServer.force_draw()
  producer.begin_sample(variant)
  for frame in range(20):
   await process_frame
   RenderingServer.force_draw()
  producer.end_sample()
  var sample = producer.report.samples[variant]
  var budgets = producer.report.budget_results[variant]
  evidence.samples[variant] = {"producer":sample, "budgets":budgets, "global_draws":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME), "global_primitives":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)}
  print("FULL_RENDER_BUDGET_CONTROL ", variant, " root_draws=",sample.visible_draw_calls_max," global_draws=",evidence.samples[variant].global_draws," global_primitives=",evidence.samples[variant].global_primitives," budgets=",budgets)
  var expected_draws = variant != "reflection_draw_over_budget"
  var expected_primitives = variant != "reflection_primitives_over_budget"
  if sample.visible_draw_calls_max > 150 or sample.visible_primitives_max > 300000 or sample.global_draw_calls_max != evidence.samples[variant].global_draws or sample.global_primitives_max != evidence.samples[variant].global_primitives or budgets.draw_calls != expected_draws or budgets.primitives != expected_primitives:
   FileAccess.open("res://full-render-budget-control.json",FileAccess.WRITE).store_string(JSON.stringify(evidence,"  "))
   push_error("Actual full producer missed a reflection-only budget violation: " + variant)
   quit(1)
   return
 FileAccess.open("res://full-render-budget-control.json",FileAccess.WRITE).store_string(JSON.stringify(evidence,"  "))
 print("FULL_PRODUCER_ALL_VIEWPORT_BUDGET_PASS")
 quit(0)
