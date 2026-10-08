extends SceneTree

const PARTS = {
 "pavilion": ["roof_hex", "roof_square", "post", "bracket", "eave_strip", "bench"],
 "corridor": ["straight", "corner", "tee", "stair"],
 "wall": ["bay", "moon_gate", "vase_gate", "window_square", "window_diamond", "window_ice", "window_hex", "roof_cap"],
 "rockery": ["small", "medium", "large", "arch", "tunnel", "cliff"]
}
var output := "/tmp/garden-standalone-kit-palette"
var report := {}
var failed := false

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="): output = arg.trim_prefix("--output=")
 call_deferred("run")

func check(value: bool, message: String) -> bool:
 if not value:
  failed = true
  push_error("STANDALONE_KIT_PALETTE_REJECTED: " + message)
  quit(1)
 return value

func swatches(texture: Texture2D, record: Dictionary) -> Dictionary:
 var image := texture.get_image()
 if not check(image != null, "Missing decoded atlas"): return {}
 if image.is_compressed():
  if not check(image.decompress() == OK, "Cannot decompress atlas"): return {}
 var rows := {}
 for name in record.swatches:
  var region: Array = record.swatches[name].uv_region
  var target: Array = record.swatches[name].expected_linear_rgb
  var mean := Vector3.ZERO
  for y in range(32):
   for x in range(32):
    var u: float = region[0] + region[2] * (0.05 + 0.90 * (x + 0.5) / 32.0)
    var v: float = 1.0 - region[1] - region[3] + region[3] * (0.05 + 0.90 * (y + 0.5) / 32.0)
    var pixel := image.get_pixel(clampi(int(u * image.get_width()), 0, image.get_width()-1), clampi(int(v * image.get_height()), 0, image.get_height()-1)).srgb_to_linear()
    mean += Vector3(pixel.r, pixel.g, pixel.b)
  mean /= 1024.0
  var error := (mean - Vector3(target[0], target[1], target[2])).abs()
  if not check(maxf(error.x, maxf(error.y, error.z)) < 0.012, "Atlas swatch differs: " + name + " " + str(mean)): return {}
  rows[name] = {"mean_linear_rgb": [mean.x, mean.y, mean.z], "target_linear_rgb": target, "samples": 1024}
 return rows

func run() -> void:
 if not check(DisplayServer.get_name() != "headless", "Graphical renderer required"): return
 DirAccess.make_dir_recursive_absolute(output)
 var contract = JSON.parse_string(FileAccess.get_file_as_string("res://tests/garden-palette-contract.json"))
 for kit_name in PARTS:
  var rows := {}
  var world := Node3D.new()
  root.add_child(world)
  var light := DirectionalLight3D.new()
  light.rotation_degrees = Vector3(-45, -30, 0)
  light.light_color = Color(1.0, 0.95, 0.86)
  light.light_energy = 1.0
  world.add_child(light)
  var environment := WorldEnvironment.new()
  environment.environment = Environment.new()
  environment.environment.background_mode = Environment.BG_COLOR
  environment.environment.background_color = Color(0.04, 0.045, 0.055)
  environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
  environment.environment.ambient_light_color = Color(0.8, 0.85, 1.0)
  environment.environment.ambient_light_energy = 0.55
  world.add_child(environment)
  var panel := Control.new()
  root.add_child(panel)
  var title := Label.new()
  title.text = kit_name.capitalize() + " — LOD0 upper rows / LOD1 lower rows — neutral preview lighting"
  title.position = Vector2(24, 18)
  title.add_theme_font_size_override("font_size", 22)
  panel.add_child(title)
  var count: int = PARTS[kit_name].size()
  var columns := 4 if count == 8 else 3 if count == 6 else 2
  var base_rows := ceili(float(count) / columns)
  var bounds := AABB()
  var first := true
  for index in range(count):
   var part: String = PARTS[kit_name][index]
   for lod in range(2):
    var suffix := "_LOD1" if lod == 1 else ""
    var path: String = "res://assets/kits/" + kit_name + "/KIT_" + kit_name + "_" + part + suffix + ".glb"
    var module = load(path).instantiate()
    world.add_child(module)
    module.position = Vector3((index % columns) * 7.0, 0, (index / columns + lod * base_rows) * 7.0)
    var meshes = module.find_children("*", "MeshInstance3D", true, false)
    if not check(meshes.size() == 1 and meshes[0].mesh.get_surface_count() == 1, "Render surface inventory: " + path): return
    var material = meshes[0].get_active_material(0)
    var name: String = "MAT_wall_atlas" if kit_name == "wall" else "MAT_pavilion_atlas"
    if not check(material is StandardMaterial3D and material.resource_name == name and material.normal_enabled, "PBR material: " + path): return
    for texture in [material.albedo_texture, material.normal_texture, material.roughness_texture, material.metallic_texture]:
     if not check(texture != null and texture.get_size() == Vector2(2048, 2048), "PBR atlas dimensions: " + path): return
    if not check(material.roughness_texture == material.metallic_texture, "ORM texture binding: " + path): return
    if not check(material.roughness_texture_channel == BaseMaterial3D.TEXTURE_CHANNEL_GREEN and material.metallic_texture_channel == BaseMaterial3D.TEXTURE_CHANNEL_BLUE, "ORM channels: " + path): return
    var wanted: Array = contract.atlas_materials[name].base_color_linear_rgba
    if not check(material.albedo_color.is_equal_approx(Color(wanted[0], wanted[1], wanted[2], wanted[3]).linear_to_srgb()), "Base color multiplier: " + path): return
    if "--corrupt-color" in OS.get_cmdline_user_args() and index == 0 and lod == 0:
     var bad := Image.create(2048, 2048, false, Image.FORMAT_RGB8)
     bad.fill(Color(0, 1, 0))
     material.albedo_texture = ImageTexture.create_from_image(bad)
    var measured := swatches(material.albedo_texture, contract.atlas_materials[name])
    if failed: return
    rows[part + suffix] = {"source_glb_sha256": FileAccess.get_sha256(path), "swatches": measured, "surface_count": 1, "normal_enabled": true, "orm_channels": "roughness=green, metallic=blue"}
    var box: AABB = meshes[0].global_transform * meshes[0].get_aabb()
    bounds = box if first else bounds.merge(box)
    first = false
  var camera := Camera3D.new()
  world.add_child(camera)
  camera.projection = Camera3D.PROJECTION_ORTHOGONAL
  camera.size = maxf(bounds.size.x, bounds.size.z) * 1.25 + bounds.size.y
  camera.position = bounds.get_center() + Vector3(12, 24, 32)
  camera.look_at(bounds.get_center())
  camera.current = true
  for frame in range(4):
   await process_frame
   RenderingServer.force_draw()
  var capture := output + "/" + kit_name + ".png"
  if not check(root.get_texture().get_image().save_png(capture) == OK, "Capture save failed"): return
  report[kit_name] = {"modules": rows, "capture": capture, "capture_sha256": FileAccess.get_sha256(capture), "viewport": [root.size.x, root.size.y]}
  world.queue_free()
  panel.queue_free()
  await process_frame
 var file := FileAccess.open(output + "/report.json", FileAccess.WRITE)
 file.store_string(JSON.stringify({"status": "48_native_kit_palette_and_pbr_bindings_passed", "kits": report, "scope": "Imported palette/PBR bindings and four neutral-lighting galleries. Physics and final artistic acceptance are separate."}, " "))
 file.close()
 print("STANDALONE_KIT_PALETTE_PASS: all 48 modules/LODs and four rendered galleries")
 quit(0)
