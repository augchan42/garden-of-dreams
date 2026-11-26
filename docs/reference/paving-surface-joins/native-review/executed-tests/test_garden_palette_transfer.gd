extends SceneTree

var failed := false
var atlas_results: Dictionary = {}

func _initialize() -> void:
 call_deferred("run")

func check(value: bool, message: String) -> bool:
 if not value:
  failed = true
  push_error("GARDEN_PALETTE_TRANSFER_REJECTED: " + message)
  quit(1)
 return value

func expected_color(values: Array) -> Color:
 return Color(values[0], values[1], values[2], values[3]).linear_to_srgb()

func vector(color: Color) -> Array:
 return [color.r, color.g, color.b, color.a]

func inspect_atlas(texture: Texture2D, name: String, record: Dictionary) -> bool:
 if atlas_results.has(name):
  return true
 var image := texture.get_image()
 if not check(image != null, "No decoded color image: " + name): return false
 if image.is_compressed():
  if not check(image.decompress() == OK, "Cannot decompress color image: " + name): return false
 var rows := {}
 for swatch in record.swatches:
  var region: Array = record.swatches[swatch].uv_region
  var wanted: Array = record.swatches[swatch].expected_linear_rgb
  var mean := Vector3.ZERO
  # UV regions use Blender's bottom origin; decoded PNG rows use top origin.
  # Interior samples avoid the padded seams and test the allocated base level.
  for y in range(32):
   for x in range(32):
    var u: float = region[0] + region[2] * (0.05 + 0.90 * (x + 0.5) / 32.0)
    var v: float = 1.0 - region[1] - region[3] + region[3] * (0.05 + 0.90 * (y + 0.5) / 32.0)
    var pixel := image.get_pixel(clampi(int(u * image.get_width()), 0, image.get_width() - 1), clampi(int(v * image.get_height()), 0, image.get_height() - 1)).srgb_to_linear()
    mean += Vector3(pixel.r, pixel.g, pixel.b)
  mean /= 1024.0
  var error := (mean - Vector3(wanted[0], wanted[1], wanted[2])).abs()
  if not check(maxf(error.x, maxf(error.y, error.z)) < 0.012, "Atlas color swatch differs from reviewed palette: " + name + "/" + swatch + " actual=" + str(mean)): return false
  rows[swatch] = {"mean_linear_rgb": [mean.x, mean.y, mean.z], "target_linear_rgb": wanted, "samples": 1024}
 atlas_results[name] = {"size": [image.get_width(), image.get_height()], "decoded_format": image.get_format(), "swatches": rows}
 return true

func run() -> void:
 var args := OS.get_cmdline_user_args()
 var contract_path := "res://tests/garden-palette-contract.json"
 var output := "res://../export/garden-palette-transfer.json"
 for arg in args:
  if arg.begins_with("--contract="): contract_path = arg.trim_prefix("--contract=")
  if arg.begins_with("--output="): output = arg.trim_prefix("--output=")
 if not check(DisplayServer.get_name() != "headless", "Graphical renderer required for decoded texture checks"): return
 var contract = JSON.parse_string(FileAccess.get_file_as_string(contract_path))
 if not check(contract is Dictionary and contract.get("status") == "reviewed_garden_palette_source_contract", "Missing reviewed source contract"): return
 var source_hash := FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 if not check(source_hash == contract.source_glb_sha256, "Contract is for a different source GLB"): return
 var demo := "--demo" in args
 var route = load("res://runtime/first_reading_demo.tscn" if demo else "res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 for frame in range(3):
  await process_frame
  RenderingServer.force_draw()
 var counts := {}
 var baked_counts := {}
 var imported_colors := {}
 var corrupted := false
 for mesh in route.find_children("*", "MeshInstance3D", true, false):
  for surface in range(mesh.mesh.get_surface_count()):
   var original = mesh.mesh.surface_get_material(surface)
   if not original is StandardMaterial3D: continue
   var name: String = original.resource_name
   var plain: bool = contract.plain_materials.has(name)
   var atlas: bool = contract.atlas_materials.has(name)
   if not plain and not atlas: continue
   var record: Dictionary = contract.plain_materials[name] if plain else contract.atlas_materials[name]
   var expected := expected_color(record.base_color_linear_rgba)
   if not check(original.albedo_color.is_equal_approx(expected), "Imported base color differs: " + name): return
   counts[name] = counts.get(name, 0) + 1
   imported_colors[name] = vector(original.albedo_color)
   var active = mesh.get_active_material(surface)
   if active is ShaderMaterial and active.shader == load("res://shaders/baked_diffuse.gdshader"):
    if not corrupted and "--corrupt-plain" in args and plain:
     active.set_shader_parameter("base_color", Color(0.0, 1.0, 0.0, 1.0))
     corrupted = true
    if not check(active.get_shader_parameter("base_color") is Color and active.get_shader_parameter("base_color").is_equal_approx(expected), "Active baked base color differs: " + name): return
    baked_counts[name] = baked_counts.get(name, 0) + 1
    if plain:
     if not check(original.albedo_texture == null and not active.get_shader_parameter("use_albedo_texture"), "Plain material acquired a color texture: " + name): return
     var emits: bool = original.emission_enabled and original.emission_energy_multiplier > 0.0 and maxf(original.emission.r, maxf(original.emission.g, original.emission.b)) > 0.0
     var baked_emission = active.get_shader_parameter("material_emission")
     if not check(not emits and baked_emission is Color and Vector3(baked_emission.r, baked_emission.g, baked_emission.b).is_zero_approx(), "Plain material gained emission: " + name): return
     if not check(is_equal_approx(active.get_shader_parameter("material_roughness"), record.roughness) and is_equal_approx(active.get_shader_parameter("material_metallic"), record.metallic), "Plain PBR factors changed: " + name): return
    else:
     if not check(active.get_shader_parameter("use_albedo_texture") and active.get_shader_parameter("albedo_texture") == original.albedo_texture, "Active atlas color binding differs: " + name): return
     if not check(active.get_shader_parameter("use_orm_texture") and active.get_shader_parameter("orm_texture") == original.roughness_texture and original.roughness_texture == original.metallic_texture, "Atlas ORM binding lost: " + name): return
     if not check(active.get_shader_parameter("use_normal_texture") and active.get_shader_parameter("normal_texture") == original.normal_texture, "Atlas normal binding lost: " + name): return
   else:
    if not check(demo, "Normal exploration material lacks a matching bake: " + name): return
   if atlas:
    if not check(original.albedo_texture != null, "Atlas color image missing: " + name): return
    if not corrupted and "--corrupt-atlas" in args:
     var old = load("res://tests/palette-before/" + name.trim_prefix("MAT_").trim_suffix("_atlas") + "_basecolor.png")
     if not check(old is Texture2D, "Old-color negative fixture missing"): return
     original.albedo_texture = old
     if active is ShaderMaterial: active.set_shader_parameter("albedo_texture", old)
     corrupted = true
    if not inspect_atlas(original.albedo_texture, name, record): return
 for records in [contract.plain_materials, contract.atlas_materials]:
  for name in records:
   if not check(counts.get(name, 0) == int(records[name].source_surface_count), "Imported surface count differs: " + name): return
   if not demo and not check(baked_counts.get(name, 0) == counts[name], "Some normal exploration surfaces retain old materials: " + name): return
 if demo and not check(not baked_counts.is_empty() and atlas_results.size() == 2, "Demo palette bindings were not checked"): return
 if not check(not ("--corrupt-plain" in args or "--corrupt-atlas" in args), "Corrupt fixture unexpectedly passed"): return
 var report := {"status": "passed", "mode": "demo" if demo else "normal", "source_glb_sha256": source_hash,
  "device": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(),
  "contract_sha256": FileAccess.get_sha256(contract_path), "script_sha256": FileAccess.get_sha256("res://tests/test_garden_palette_transfer.gd"),
  "source_surface_counts": counts, "baked_surface_counts": baked_counts, "imported_srgb_colors": imported_colors, "decoded_atlases": atlas_results,
  "scope": "Actual imported plain factors, active baked shader uniforms/PBR texture bindings and decoded architectural swatches. This does not prove final rendered art, phone performance or service acceptance."}
 var file := FileAccess.open(output, FileAccess.WRITE)
 if not check(file != null, "Cannot write palette report"): return
 file.store_string(JSON.stringify(report, " "))
 file.close()
 route.queue_free()
 print("GARDEN_PALETTE_TRANSFER_PASS ", report.mode, " source=", source_hash)
 quit(0)
