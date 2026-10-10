extends RefCounted

# RenderingServer times cover render work. Performance monitors are separate
# engine frame/physics monitors; these measurements must not be added together.
var viewports: Array[Viewport] = []
var values: Dictionary = {}
var viewport_values: Dictionary = {}

func configure(root: Window) -> void:
 var pending: Array[Node] = [root]
 while not pending.is_empty():
  var node = pending.pop_back()
  pending.append_array(node.get_children())
  if node is Viewport:
   viewports.append(node)
   RenderingServer.viewport_set_measure_render_time(node.get_viewport_rid(), true)

func begin() -> void:
 values = {"process_monitor_ms": [], "physics_monitor_ms": [], "frame_setup_cpu_ms": [], "enabled_viewports_cpu_plus_setup_ms": []}
 viewport_values.clear()

func sample() -> void:
 values.process_monitor_ms.append(Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0)
 values.physics_monitor_ms.append(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0)
 var setup = RenderingServer.get_frame_setup_time_cpu()
 values.frame_setup_cpu_ms.append(setup)
 var total_cpu = setup
 for viewport in viewports:
  if not is_instance_valid(viewport):continue
  # The Garden's only SubViewport is the pond capture, toggled ALWAYS/DISABLED.
  # Conditional update modes cannot establish actual rendering from this flag.
  var enabled = not viewport is SubViewport or viewport.render_target_update_mode == SubViewport.UPDATE_ALWAYS
  var key = str(viewport.get_path())
  if not viewport_values.has(key):
   viewport_values[key] = {"observations": 0, "update_enabled_observations": 0, "update_modes": {}, "size": [viewport.size.x, viewport.size.y], "cpu_ms": [], "gpu_ms": []}
  var record = viewport_values[key]
  record.observations += 1
  var mode = int(viewport.render_target_update_mode) if viewport is SubViewport else -1
  record.update_modes[str(mode)] = true
  if not enabled:continue
  record.update_enabled_observations += 1
  var rid = viewport.get_viewport_rid()
  var cpu = RenderingServer.viewport_get_measured_render_time_cpu(rid)
  record.cpu_ms.append(cpu)
  record.gpu_ms.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
  total_cpu += cpu
 values.enabled_viewports_cpu_plus_setup_ms.append(total_cpu)

static func statistics(samples: Array) -> Dictionary:
 if samples.is_empty():return {"status": "not_sampled", "samples": 0, "positive_samples": 0}
 var sorted = samples.duplicate()
 sorted.sort()
 var positives = samples.filter(func(value):return value > 0.0).size()
 # In particular, all-zero native GLES GPU counters do not mean zero GPU work.
 return {"status": "observed" if positives > 0 else "unavailable_all_zero", "samples": samples.size(), "positive_samples": positives, "median_ms": sorted[sorted.size()/2], "p95_ms": sorted[int(sorted.size()*.95)], "max_ms": sorted.back()}

func finish() -> Dictionary:
 var result = {"scope": "Engine frame/physics monitors and enabled viewport render counters. CPU rendering excludes script/physics work; overlapping monitor values are not additive. All-zero counters are unavailable, not evidence of zero GPU/CPU work.", "monitors": {}, "viewports": {}}
 for key in values:result.monitors[key] = statistics(values[key])
 for key in viewport_values:
  var record = viewport_values[key].duplicate()
  record.cpu_ms = statistics(record.cpu_ms)
  record.gpu_ms = statistics(record.gpu_ms)
  result.viewports[key] = record
 return result
