extends SceneTree

func _initialize() -> void:
 var packed = load("res://assets/garden-of-dreams.glb") as PackedScene
 if packed == null:
  push_error("Garden GLB did not import")
  quit(1)
  return
 var root = Node3D.new()
 root.name = "GardenOfDreams"
 var garden = packed.instantiate()
 root.add_child(garden)
 garden.owner = root
 var counts = {"meshes": 0, "collisions": 0, "room_markers": 0, "cameras": 0}
 var reference_camera: Camera3D
 var nodes: Array[Node] = [garden]
 while not nodes.is_empty():
  var node = nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D: counts.meshes += 1
  if node is CollisionShape3D: counts.collisions += 1
  if node is Camera3D:
   counts.cameras += 1
   if str(node.name).begins_with("CAM_stage_wide"):
    reference_camera = node
  if str(node.name).begins_with("TRG_"):
   counts.room_markers += 1
 if reference_camera == null:
  push_error("Missing establishing camera")
  quit(1)
  return
 var preview_camera = Camera3D.new()
 preview_camera.name = "PreviewCamera"
 preview_camera.fov = reference_camera.fov
 preview_camera.near = reference_camera.near
 preview_camera.far = reference_camera.far
 preview_camera.keep_aspect = reference_camera.keep_aspect
 var camera_transform = reference_camera.transform
 var ancestor = reference_camera.get_parent()
 while ancestor is Node3D:
  camera_transform = ancestor.transform * camera_transform
  ancestor = ancestor.get_parent()
 preview_camera.transform = camera_transform
 preview_camera.current = true
 root.add_child(preview_camera)
 preview_camera.owner = root
 var environment = WorldEnvironment.new()
 environment.name = "GardenEnvironment"
 environment.environment = Environment.new()
 environment.environment.background_mode = Environment.BG_COLOR
 environment.environment.background_color = Color.BLACK
 environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
 environment.environment.ambient_light_color = Color(0.35,0.42,0.30)
 environment.environment.ambient_light_energy = 0.65
 environment.environment.fog_enabled = true
 environment.environment.fog_light_color = Color(0.05,0.2,0.05)
 environment.environment.fog_density = 0.003
 root.add_child(environment)
 environment.owner = root
 var grade = load("res://runtime/color_grade.tscn").instantiate()
 root.add_child(grade)
 grade.owner = root
 var output = PackedScene.new()
 var result = output.pack(root)
 if result != OK:
  push_error("Cannot pack preview")
  quit(1)
  return
 result = ResourceSaver.save(output,"res://garden_preview.tscn")
 var file = FileAccess.open("res://import-validation.json",FileAccess.WRITE)
 file.store_string(JSON.stringify(counts,"  "))
 print("GARDEN_IMPORT_VALIDATED ",counts)
 root.free()
 quit(0 if result == OK and counts.collisions > 50 and counts.room_markers >= 39 else 1)
