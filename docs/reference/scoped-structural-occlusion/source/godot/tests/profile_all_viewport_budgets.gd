extends SceneTree

class ControlProducer extends "res://tests/profile_android_full.gd":
 func _ready() -> void:
  pass
 func save_report() -> void:
  pass

const POSITIONS = {"terminal_room":Vector3(-1.3,0,37.4),"rockery_gate":Vector3(0,0,32.5),"qinfang_ting":Vector3(0,0,1.8),"ouxiang_xie":Vector3(-23,0,0),"ziling_zhou":Vector3(-35.4,0,0),"qiushuang_zhai":Vector3(22,0,-13.5),"tubi_tang":Vector3(7,4,-31),"hengwu_yuan":Vector3(-18,0,-14.7),"daoxiang_cun":Vector3(-32,0,-19.3),"aojing_guan":Vector3(26,-.65,13.1),"longcui_an":Vector3(-25,0,10.6),"xiaoxiang_guan":Vector3(-6.6,0,13),"yihong_yuan":Vector3(22.6,0,1),"daguan_lou":Vector3(0,0,-20.5)}

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 Engine.max_fps = 60
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 var shape = "portrait" if "--mobile" in OS.get_cmdline_user_args() else "desktop"
 if shape == "portrait":root.size = Vector2i(390,844)
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var producer = ControlProducer.new()
 producer.route = route
 producer.report = {"status":"native-diagnostic", "render_budget_scope":"engine_global_all_viewports", "samples":{}, "budget_results":{}, "scope":"Native stationary fourteen-room arrivals using the actual full-phone producer. Explicit draw scheduling; frame intervals are diagnostic only. Not continuous traversal, phone, sustained, release or final-art acceptance.", "device":RenderingServer.get_video_adapter_name(), "viewport":[root.size.x,root.size.y], "source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"), "producer_sha256":FileAccess.get_sha256("res://tests/profile_android_full.gd")}
 root.add_child(producer)
 producer.set_physics_process(false)
 producer.frame_costs.configure(root)
 for room in POSITIONS:
  route.player.position = POSITIONS[room] + Vector3(0,.04,0)
  route._arrive(room,true)
  await create_timer(1.8).timeout
  for frame in range(20):
   await process_frame
   RenderingServer.force_draw()
  producer.begin_sample(room)
  for frame in range(30):
   await process_frame
   RenderingServer.force_draw()
  producer.end_sample()
  var sample = producer.report.samples[room]
  assert(sample.frames > 0 and sample.global_draw_calls_max >= sample.visible_draw_calls_max)
  assert(sample.global_primitives_max >= sample.visible_primitives_max)
  print("NATIVE_ALL_VIEWPORT_ARRIVAL ",room," root_draws=",sample.visible_draw_calls_max," global_draws=",sample.global_draw_calls_max," global_primitives=",sample.global_primitives_max)
  FileAccess.open("res://all-viewport-budgets-"+shape+".json",FileAccess.WRITE).store_string(JSON.stringify(producer.report,"  "))
 print("NATIVE_ALL_VIEWPORT_ARRIVALS_PASS ",shape)
 quit(0)
