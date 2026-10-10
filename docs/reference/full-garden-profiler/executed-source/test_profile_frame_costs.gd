extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var helper = preload("res://tests/profile_frame_costs.gd").new()
 assert(helper.statistics([]) == {"status": "not_sampled", "samples": 0, "positive_samples": 0})
 var unavailable = helper.statistics([0.0, 0.0])
 assert(unavailable.status == "unavailable_all_zero" and unavailable.positive_samples == 0)
 var observed = helper.statistics([3.0, 1.0, 2.0])
 assert(observed.status == "observed" and observed.median_ms == 2.0 and observed.p95_ms == 3.0)
 var viewport = SubViewport.new()
 viewport.name = "DisabledReflectionControl"
 viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
 root.add_child(viewport)
 helper.configure(root)
 helper.begin()
 helper.sample()
 var disabled = helper.finish().viewports[str(viewport.get_path())]
 assert(disabled.observations == 1 and disabled.update_enabled_observations == 0)
 assert(disabled.cpu_ms.status == "not_sampled" and disabled.gpu_ms.status == "not_sampled")
 viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
 helper.sample()
 var enabled = helper.finish().viewports[str(viewport.get_path())]
 assert(enabled.observations == 2 and enabled.update_enabled_observations == 1)
 assert(enabled.cpu_ms.samples == 1 and enabled.gpu_ms.samples == 1)
 print("FRAME_COST_STATISTICS_AND_DISABLED_VIEWPORT_PASS")
 viewport.queue_free()
 await process_frame
 quit(0)
