extends SceneTree
func _initialize():call_deferred("run")
func run():
 var scene=load("res://assets/garden-of-dreams.glb").instantiate()
 var rows=[]
 for name in ["SITE_terminal-cells_MAT_plaster_rock","SITE_terminal-cells_MAT_backstage","SITE_terminal-cells_MAT_stage_backstage","SITE_rockery-gate_MAT_pavilion_atlas","SITE_rockery-gate_MAT_plaster_rock"]:
  var node=scene.find_child(name,true,false) as MeshInstance3D
  assert(node!=null)
  var arrays=node.mesh.surface_get_arrays(0)
  var vertices=arrays[Mesh.ARRAY_VERTEX]
  var indices=arrays[Mesh.ARRAY_INDEX]
  var lookup={};var remap=[]
  for vertex in vertices:
   if not lookup.has(vertex):lookup[vertex]=lookup.size()
   remap.append(lookup[vertex])
  var counts={};var windings={}
  for offset in range(0,indices.size(),3):
   for edge in [[0,1],[1,2],[2,0]]:
    var a=remap[indices[offset+edge[0]]];var b=remap[indices[offset+edge[1]]]
    var key=Vector2i(mini(a,b),maxi(a,b))
    counts[key]=counts.get(key,0)+1
    windings[key]=windings.get(key,0)+(1 if a<b else -1)
  var open_edges=0;var unbalanced=0;var histogram={}
  for key in counts:
   histogram[str(counts[key])]=histogram.get(str(counts[key]),0)+1
   if counts[key]<2 or counts[key]%2!=0:open_edges+=1
   if windings[key]!=0:unbalanced+=1
  var material=node.get_active_material(0)
  var props={}
  if material is BaseMaterial3D:
   for field in ["transparency","cull_mode","billboard_mode","grow_enabled","proximity_fade_enabled","distance_fade_mode","heightmap_enabled"]:props[field]=material.get(field)
  rows.append({"mesh":name,"unique_vertices":lookup.size(),"triangles":indices.size()/3,"open_or_odd_edges":open_edges,"unbalanced_edge_winding":unbalanced,"edge_counts":histogram,"base_material_properties":props})
 FileAccess.open("res://occluder-topology.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "))
 print(JSON.stringify(rows))
 scene.free()
 quit()
