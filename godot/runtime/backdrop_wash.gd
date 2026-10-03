extends RefCounted

# glTF omits Blender Area lights and light linking. The runtime substitute
# uses a separate visual layer so it reaches only the painted backdrop.
static func configure(garden: Node3D) -> int:
 var receivers = 0
 var stack: Array[Node] = [garden]
 while not stack.is_empty():
  var node = stack.pop_back()
  stack.append_array(node.get_children())
  if not node is MeshInstance3D:
   continue
  var name_string = str(node.name)
  if name_string.begins_with("SITE_stage_MAT_cyclorama") or name_string.begins_with("SITE_stage_MAT_painted_mountains_") or name_string.begins_with("SITE_stage_MAT_painted_moon"):
   node.layers |= 4
   receivers += 1
 assert(receivers == 5, "Painted backdrop wash must have five receiver meshes")

 var wash = DirectionalLight3D.new()
 wash.name = "BackdropWash"
 wash.light_color = Color(0.72, 0.78, 0.84)
 wash.light_energy = 3.0
 wash.light_cull_mask = 4
 wash.shadow_enabled = false
 garden.add_child(wash)
 wash.position = Vector3(0, 100, 20)
 wash.look_at(Vector3(0, 0, 0), Vector3.UP)
 return receivers
