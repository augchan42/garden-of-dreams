@tool
extends EditorScenePostImport

# glTF carries photometric intensities. This project uses Godot's nonphysical
# Compatibility lighting, so use calibrated preview energies on every import.
func _post_import(scene: Node) -> Object:
 var surfaces = {"MAT_aojing_water": load("res://materials/water.tres"), "MAT_water": load("res://materials/water.tres"), "MAT_fog_plane": load("res://materials/floor_fog.tres")}
 var flora_material = load("res://materials/flora_atlas.tres")
 var props_material = load("res://materials/props_atlas.tres")
 var tech_material = load("res://materials/tech_atlas.tres")
 var nodes: Array[Node] = [scene]
 while not nodes.is_empty():
  var node = nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D:
   var extras=node.get_meta("extras",{})
   if extras is Dictionary and extras.has("sign_board"):
    # Painted lettering is a small surface detail, needed on the site's approach.
    node.visibility_range_end=28.0
   if str(node.name).begins_with("HERO_table_line_"):
    node.visible=not str(node.name).contains("_broken")
   for i in range(node.mesh.get_surface_count()):
    var material = node.mesh.surface_get_material(i)
    if str(node.name).begins_with("HERO_flora_"):
     node.mesh.surface_set_material(i,flora_material)
     node.set_surface_override_material(i,flora_material)
    if material and material.resource_name.begins_with("MAT_props_atlas"):
     node.mesh.surface_set_material(i,props_material)
     node.set_surface_override_material(i,props_material)
     # Small dressing props need not draw beyond their approach view.
     node.visibility_range_end=28.0
    if material and material.resource_name in surfaces:
     node.set_surface_override_material(i,surfaces[material.resource_name])
    if material and material.resource_name.begins_with("MAT_terminal_scroll"):
     var dark_scroll=load("res://materials/terminal_scroll.tres")
     node.mesh.surface_set_material(i,dark_scroll)
     node.set_surface_override_material(i,dark_scroll)
     node.visibility_range_end=28.0
    if material and material.resource_name.begins_with("MAT_tech_atlas"):
     node.mesh.surface_set_material(i,tech_material)
     node.set_surface_override_material(i,tech_material)
    if material and material.resource_name.begins_with("MAT_stage_"):
     var key=material.resource_name.trim_prefix("MAT_stage_").split(".")[0]
     # Older canvas materials are not part of the modular stage library.
     var path="res://materials/stage/"+key+".tres"
     if ResourceLoader.exists(path):
      var shared=load(path)
      node.mesh.surface_set_material(i,shared)
      node.set_surface_override_material(i,shared)
  if node is DirectionalLight3D:
   node.light_energy = 1.4 if str(node.name).contains("green_key") else 0.65
   node.shadow_enabled = true
  elif node is SpotLight3D:
   # The broad imperial facade needs a stronger preview key at this distance.
   var imperial = str(node.name).contains("daguan")
   node.light_energy = 20.0 if imperial else (3.0 if str(node.name).contains("qiushuang") else 1.8)
   if imperial: node.shadow_bias = 0.5
   node.spot_range = 14.0
   node.shadow_enabled = true
  elif node is OmniLight3D:
   # Keep unoccupied cells' light switches off.
   node.light_energy = 0.0 if node.light_energy == 0.0 else (0.65 if str(node.name).contains("CRT") else 1.3)
   node.omni_range = 3.0 if str(node.name).contains("CRT") else 4.0
 return scene
