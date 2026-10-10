extends Node

const SOURCE_NAMES = ["SITE_terminal-cells_MAT_plaster_rock", "SITE_terminal-cells_MAT_backstage", "SITE_terminal-cells_MAT_stage_backstage", "SITE_rockery-gate_MAT_pavilion_atlas", "SITE_rockery-gate_MAT_plaster_rock"]
const BAKED_SHADER_SHA256 = "4040728147086d2411be2575edb35805bc56d849d453ea112c9b5fbeb2a0318c"
const FRUSTUM_MARGIN = 0.05
var viewport: Viewport
var camera: Camera3D
var bounds: Array[AABB] = []
var configured = false
var previous_occlusion = false

func _ready() -> void:
 set_process(false)
 RenderingServer.frame_pre_draw.connect(refresh_scope)

func _exit_tree() -> void:
 RenderingServer.frame_pre_draw.disconnect(refresh_scope)
 if configured and is_instance_valid(viewport):viewport.use_occlusion_culling = previous_occlusion

func configure(environment: Node3D, source_camera: Camera3D, target_viewport: Viewport) -> Dictionary:
 if configured:return {"status":"disabled", "reason":"Controller is already configured"}
 var prepared: Array[Dictionary] = []
 for source_name in SOURCE_NAMES:
  var source = environment.find_child(source_name, true, false) as MeshInstance3D
  if source == null or not source.mesh is ArrayMesh or not source.is_visible_in_tree():
   return {"status":"disabled", "reason":"Missing visible static array mesh: " + source_name}
  if source.transparency != 0.0 or source.skin != null or source.mesh.get_blend_shape_count() != 0 or source.visibility_range_begin != 0.0 or source.visibility_range_end != 0.0:
   return {"status":"disabled", "reason":"Structural mesh changes opacity or geometry: " + source_name}
  for surface in range(source.mesh.get_surface_count()):
   if source.mesh.surface_get_primitive_type(surface) != Mesh.PRIMITIVE_TRIANGLES:
    return {"status":"disabled", "reason":"Structural surface is not triangles: " + source_name}
   var geometry = _geometry(source.mesh.surface_get_arrays(surface))
   if geometry.is_empty() or not _opaque(source.get_active_material(surface), geometry.indices):
    return {"status":"disabled", "reason":"Structural surface is not verified opaque static geometry: " + source_name}
   prepared.append({"source":source, "surface":surface, "vertices":geometry.vertices, "indices":geometry.indices})
 if prepared.is_empty():return {"status":"disabled", "reason":"No structural surfaces"}
 viewport = target_viewport
 camera = source_camera
 previous_occlusion = viewport.use_occlusion_culling
 var triangles = 0
 for record in prepared:
  var resource = ArrayOccluder3D.new()
  resource.set_arrays(record.vertices, record.indices)
  var instance = OccluderInstance3D.new()
  instance.name = "ExactOpaque_" + str(record.source.name) + "_" + str(record.surface)
  instance.occluder = resource
  instance.set_meta("source_mesh", str(record.source.name))
  add_child(instance)
  instance.global_transform = record.source.global_transform
  triangles += record.indices.size() / 3
 for source_name in SOURCE_NAMES:
  var source = environment.find_child(source_name, true, false) as MeshInstance3D
  bounds.append(source.global_transform * source.get_aabb())
 configured = true
 set_process(true)
 refresh_scope()
 return {"status":"ready", "occluders":prepared.size(), "triangles":triangles, "scope":"main_camera_frustum"}

func refresh_scope() -> void:
 if not configured or not is_instance_valid(camera) or not is_instance_valid(viewport):return
 # Camera tweens finish after _process. Use the pose about to be rendered.
 viewport.use_occlusion_culling = is_processing() and _intersects_view()

func _intersects_view() -> bool:
 var planes = camera.get_frustum()
 for box in bounds:
  var outside = false
  for plane in planes:
   var closest = Vector3(box.position.x if plane.normal.x >= 0 else box.end.x, box.position.y if plane.normal.y >= 0 else box.end.y, box.position.z if plane.normal.z >= 0 else box.end.z)
   if plane.distance_to(closest) > FRUSTUM_MARGIN:
    outside = true
    break
  if not outside:return true
 return false

static func _geometry(arrays: Array) -> Dictionary:
 if arrays.size() != Mesh.ARRAY_MAX or not arrays[Mesh.ARRAY_VERTEX] is PackedVector3Array or not arrays[Mesh.ARRAY_INDEX] is PackedInt32Array:return {}
 var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
 var original_indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
 if vertices.is_empty() or original_indices.is_empty() or original_indices.size() % 3 != 0:return {}
 var unique = PackedVector3Array()
 var lookup = {}
 var remap = PackedInt32Array()
 for vertex in vertices:
  if not vertex.is_finite():return {}
  if not lookup.has(vertex):
   lookup[vertex] = unique.size()
   unique.append(vertex)
  remap.append(lookup[vertex])
 var indices = PackedInt32Array()
 for index in original_indices:
  if index < 0 or index >= remap.size():return {}
  indices.append(remap[index])
 return {"vertices":unique, "indices":indices}

static func _opaque(material: Material, indices: PackedInt32Array) -> bool:
 if material is ShaderMaterial:
  return material.shader != null and material.shader.code.sha256_text() == BAKED_SHADER_SHA256
 if not material is BaseMaterial3D:return false
 if material.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED or material.grow or material.billboard_mode != BaseMaterial3D.BILLBOARD_DISABLED or material.fixed_size or material.proximity_fade_enabled or material.distance_fade_mode != BaseMaterial3D.DISTANCE_FADE_DISABLED or material.heightmap_enabled or material.refraction_enabled or material.no_depth_test or material.depth_draw_mode == BaseMaterial3D.DEPTH_DRAW_DISABLED:return false
 return material.cull_mode == BaseMaterial3D.CULL_DISABLED or _closed_shell(indices)

static func _closed_shell(indices: PackedInt32Array) -> bool:
 var counts = {}
 var windings = {}
 for offset in range(0, indices.size(), 3):
  for edge in [[0,1], [1,2], [2,0]]:
   var a = indices[offset + edge[0]]
   var b = indices[offset + edge[1]]
   if a == b:return false
   var key = Vector2i(mini(a,b), maxi(a,b))
   counts[key] = counts.get(key,0) + 1
   windings[key] = windings.get(key,0) + (1 if a < b else -1)
 for key in counts:
  if counts[key] < 2 or counts[key] % 2 != 0 or windings[key] != 0:return false
 return true
