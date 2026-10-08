extends Node

# Keys remain dynamic until the lightmap pass. This budget controls only local
# lantern/CRT practicals; emissive paper and screen materials remain visible.
const MAX_ACTIVE = 4
var activation_distance = 12.0
var lights: Array[OmniLight3D] = []
var visitor: Node3D
var elapsed = 0.0

func configure(environment: Node, target: Node3D) -> void:
 visitor = target
 lights.clear()
 var nodes: Array[Node] = [environment]
 while not nodes.is_empty():
  var node = nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is OmniLight3D:
   node.shadow_enabled = false
   if node.light_energy > 0:
    lights.append(node)
 update_lights()

func _process(delta: float) -> void:
 elapsed += delta
 if elapsed >= 0.2:
  elapsed = 0.0
  update_lights()

func update_lights() -> void:
 if not is_instance_valid(visitor): return
 var nearby: Array[OmniLight3D] = []
 for light in lights:
  if light.global_position.distance_to(visitor.global_position) <= activation_distance:
   nearby.append(light)
 nearby.sort_custom(func(a,b): return a.global_position.distance_squared_to(visitor.global_position) < b.global_position.distance_squared_to(visitor.global_position))
 nearby.resize(mini(MAX_ACTIVE,nearby.size()))
 for light in lights:
  light.visible = nearby.has(light)
