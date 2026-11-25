extends SceneTree
func _initialize():
 create_timer(90).timeout.connect(func():push_error("CORRIDOR_ROOF_UV_DEADLINE");quit(1))
 call_deferred("run")
func run():
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var catalog=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 assert(preload("res://runtime/baked_materials.gd").source_matches(catalog))
 var node=route.find_child("SITE_qinfang-ting_MAT_pavilion_atlas",true,false) as MeshInstance3D
 assert(node!=null and node.mesh.get_surface_count()==1)
 var material=node.get_active_material(0) as ShaderMaterial
 assert(material!=null and material.get_shader_parameter("use_lightmap"))
 var texture=material.get_shader_parameter("lightmap") as Texture2D
 assert(texture!=null and texture.get_width()==256 and texture.get_height()==256)
 var arrays=node.mesh.surface_get_arrays(0)
 var vertices=arrays[Mesh.ARRAY_VERTEX]
 var primary=arrays[Mesh.ARRAY_TEX_UV]
 var uv2=arrays[Mesh.ARRAY_TEX_UV2]
 var indices=arrays[Mesh.ARRAY_INDEX]
 var count=0
 var failures=0
 var minimum=INF
 for offset in range(0,indices.size(),3):
  var tri=[indices[offset],indices[offset+1],indices[offset+2]]
  var center=Vector3.ZERO
  var roof=true
  for index in tri:
   var world=node.global_transform*vertices[index]
   center+=world/3.0
   roof=roof and world.y>2.79 and primary[index].x>0.515624 and primary[index].x<0.984376 and primary[index].y>0.015624 and primary[index].y<0.484376
  if not roof:continue
  if not ((abs(center.x)<1.21 and abs(center.z)>6.84 and abs(center.z)<19.16) or (abs(center.z)<1.21 and abs(center.x)>6.84 and abs(center.x)<19.16)):continue
  count+=1
  for index in tri:assert(uv2[index].is_finite())
  var a=uv2[tri[0]]*256
  var b=uv2[tri[1]]*256
  var c=uv2[tri[2]]*256
  var area=abs((b-a).cross(c-a))/2.0
  minimum=min(minimum,area)
  if area<=1.0:failures+=1
 assert(count==784)
 print("CORRIDOR_ROOF_UV_MEASURE count=",count," subtexel=",failures," minimum256=",minimum)
 if failures>0:
  push_error("Subtexel native corridor roof charts: "+str(failures))
  quit(1)
  return
 print("CORRIDOR_ROOF_UV_NATIVE_PASS: 784 actual normal-route roof triangles above one runtime texel")
 quit()
