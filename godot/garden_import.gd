@tool
extends EditorScenePostImport

# glTF carries photometric intensities. This project uses Godot's nonphysical
# Compatibility lighting, so use calibrated preview energies on every import.
func _post_import(scene: Node) -> Object:
 var surfaces = {"MAT_aojing_water": load("res://materials/water.tres"), "MAT_water": load("res://materials/water.tres"), "MAT_fog_plane": load("res://materials/floor_fog.tres")}
 var nodes: Array[Node] = [scene]
 while not nodes.is_empty():
  var node = nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D:
   if str(node.name).begins_with("HERO_table_line_"):
    node.visible=not str(node.name).contains("_broken")
   for i in range(node.mesh.get_surface_count()):
    var material = node.mesh.surface_get_material(i)
    if material and material.resource_name in surfaces:
     node.set_surface_override_material(i,surfaces[material.resource_name])
  if node is DirectionalLight3D:
   node.light_energy = 1.4 if str(node.name).contains("green_key") else 0.65
   node.shadow_enabled = true
  elif node is SpotLight3D:
   # The broad imperial facade needs a stronger preview key at this distance.
   var imperial = str(node.name).contains("daguan")
   node.light_energy = 20.0 if imperial else 1.8
   if imperial: node.shadow_bias = 0.5
   node.spot_range = 14.0
   node.shadow_enabled = true
  elif node is OmniLight3D:
   # Keep unoccupied cells' light switches off.
   node.light_energy = 0.0 if node.light_energy == 0.0 else (0.65 if str(node.name).contains("CRT") else 1.3)
   node.omni_range = 3.0 if str(node.name).contains("CRT") else 4.0
 return scene
