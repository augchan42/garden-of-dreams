extends SceneTree

func _initialize() -> void:
 create_timer(60).timeout.connect(func():push_error("Painted sign capture timed out");quit(1))
 call_deferred("run")

func capture(label:String) -> void:
 await create_timer(.8).timeout
 await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png("res://../docs/reference/sign-"+label+".png")==OK)

func run() -> void:
 var portrait="--portrait" in OS.get_cmdline_user_args()
 root.size=Vector2i(390,844) if portrait else Vector2i(1410,600)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var positions={"qinfang-ting":Vector3(0,.04,1.8),"hengwu-yuan":Vector3(-18,.04,-14.7),
  "yihong-yuan":Vector3(24.3,.04,1),"xiaoxiang-guan":Vector3(-8.8,.04,12.5),
  "longcui-an":Vector3(-25,.04,10.6),"aojing-guan":Vector3(26,-.61,13.1),
  "daoxiang-cun":Vector3(-32,.04,-21)}
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://../export/painted-signs.json"))["placements"]
 for record in records:
  var slug:String=record["site"]
  var title=route.find_child("HERO_"+slug+"_title*",true,false)
  assert(title is MeshInstance3D and title.visibility_range_end==28.0,
   "Painted sign import must retain its 28 metre visibility range")
  var room=slug.replace("-","_")
  route.player.position=positions[slug]
  route._arrive(room,true)
  var suffix="-portrait" if portrait else ""
  await capture(slug+"-arrival"+suffix)
  var points:Array[Vector3]=[]
  for p in record["world_vertices"]:points.append(Vector3(p[0],p[2],-p[1]))
  var center=(points[0]+points[1]+points[2]+points[3])*.25
  var normal=(points[1]-points[0]).cross(points[2]-points[0]).normalized()
  route.camera.keep_aspect=Camera3D.KEEP_WIDTH
  route._camera_to(center+normal*2.2,center,true)
  await capture(slug+"-detail"+suffix)
 print("PAINTED_SIGN_VIEWS_SAVED ",records.size()," sites ","portrait" if portrait else "desktop")
 quit(0)
