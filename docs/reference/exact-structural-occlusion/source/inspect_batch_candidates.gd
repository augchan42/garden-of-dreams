extends SceneTree
func _initialize():call_deferred("run")
func run():
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var groups={}
 var structural=[]
 for node in route.find_children("*","MeshInstance3D",true,false):
  if node.mesh==null:continue
  var key=str(node.mesh.get_rid())
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   key+=str(material.get_rid()) if material!=null else "null"
  if not groups.has(key):groups[key]=[]
  groups[key].append(node.name)
  if "terminal" in node.name or "rockery" in node.name:
   structural.append({"name":node.name,"bounds":str(node.get_aabb()),"transform":str(node.global_transform),"surfaces":node.mesh.get_surface_count()})
 var repeated=[]
 for key in groups:
  if groups[key].size()>1:repeated.append(groups[key])
 var report={"repeated_geometry_material_groups":repeated,"structural":structural}
 FileAccess.open("res://batch-candidates.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print(JSON.stringify(report))
 quit()
