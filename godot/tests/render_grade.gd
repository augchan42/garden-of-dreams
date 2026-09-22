extends SceneTree
func _initialize() -> void:
 if not ResourceLoader.exists("res://runtime/color_grade.tscn"):
  push_error("Color grade scene missing")
  quit(1)
  return
 call_deferred("run")
func capture(label:String) -> void:
 await create_timer(.3).timeout
 await RenderingServer.frame_post_draw
 var result=root.get_texture().get_image().save_png("res://../docs/reference/grade-"+label+".png")
 assert(result==OK)
func run() -> void:
 root.size=Vector2i(512,512)
 root.content_scale_size=Vector2i.ZERO
 var layer=CanvasLayer.new()
 layer.layer=0
 root.add_child(layer)
 var image=Image.create(512,512,false,Image.FORMAT_RGB8)
 for y in range(512):
  for x in range(512):
   image.set_pixel(x,y,Color(float(x%64)/63.0,float(y%64)/63.0,float((x/64)+(y/64)*8)/63.0))
 var source=TextureRect.new()
 source.texture=ImageTexture.create_from_image(image)
 layer.add_child(source)
 var grade=load("res://runtime/color_grade.tscn").instantiate()
 root.add_child(grade)
 assert(grade.get_node("ColorRect").mouse_filter==Control.MOUSE_FILTER_IGNORE)
 var ui=CanvasLayer.new()
 ui.layer=2
 root.add_child(ui)
 var marker=ColorRect.new()
 marker.color=Color(1,.2,.7,1)
 marker.size=Vector2(16,16)
 ui.add_child(marker)
 grade.hide()
 await capture("input")
 grade.show()
 await capture("output")
 print("GRADE_RENDER_PASS: input/output captured; overlay does not intercept clicks")
 quit(0)
