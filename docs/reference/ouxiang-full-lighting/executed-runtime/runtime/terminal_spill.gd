extends RefCounted

# The independent Cycles indirect term adds once to the existing base bake.
# Validate and prepare all receivers before changing any scene materials.
static func apply_baked(garden:Node3D) -> int:
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/terminal-spill-index.json"))
 if not records is Dictionary or records.size()!=7 or not preload("res://runtime/baked_materials.gd").source_matches(records):
  push_error("Terminal spill bakes do not match the imported garden")
  return -1
 var manifest=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/terminal-spill/manifest.json"))
 var wash=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/backdrop-wash/manifest.json"))
 if not manifest is Dictionary or not wash is Dictionary:return -1
 for field in ["source_glb_sha256","authoring_blend_sha256","stage_blend_sha256","site_blend_sha256"]:
  if manifest.get(field)!=wash.get(field):
   push_error("Terminal spill and backdrop wash use different saved rigs")
   return -1
 var controls=manifest.get("controls",{})
 for name in ["direct","window_only","sealed","washes_off"]:
  var cells=controls.get(name,[])
  if not cells is Array or cells.size()!=6:return -1
  for cell in cells:
   var maximum=float(cell.get("linear_max",-1))
   if not is_finite(maximum) or maximum<0:return -1
   if (maximum<=1e-9 if name=="window_only" else maximum>1e-7):return -1
 var prepared={}
 var shader=load("res://shaders/baked_diffuse.gdshader")
 for name in records:
  if not str(name).begins_with("SITE_terminal-cells_"):return -1
  var record=records[name]
  if record.get("pass_filter",[])!=["INDIRECT"] or record.get("adaptive_sampling",true) or record.get("samples",0)<2048 or record.get("lights_baked",0)!=12:return -1
  if record.get("point_lights_baked",true) or record.get("emissive_geometry_baked",true):return -1
  for field in ["source_glb_sha256","authoring_blend_sha256","stage_blend_sha256","site_blend_sha256","terminal_blend_sha256"]:
   if record.get(field)!=manifest.get(field):return -1
  var mesh=garden.find_child(name,true,false) as MeshInstance3D
  var texture=load("res://lightmaps/"+record.texture) as Texture2D
  var scale=float(record.get("scale",0))
  if mesh==null or texture==null or not is_finite(scale) or scale<=0:return -1
  var materials:Array[ShaderMaterial]=[]
  for surface in range(mesh.mesh.get_surface_count()):
   var source=mesh.get_active_material(surface) as ShaderMaterial
   if source==null or source.shader!=shader or not source.get_shader_parameter("use_lightmap"):return -1
   var material=source.duplicate() as ShaderMaterial
   material.set_shader_parameter("terminal_spill",texture)
   material.set_shader_parameter("terminal_spill_scale",scale)
   material.set_shader_parameter("use_terminal_spill",true)
   materials.append(material)
  prepared[name]={"mesh":mesh,"materials":materials}
 for name in prepared:
  var mesh=prepared[name].mesh as MeshInstance3D
  for surface in range(prepared[name].materials.size()):
   mesh.set_surface_override_material(surface,prepared[name].materials[surface])
 return prepared.size()
