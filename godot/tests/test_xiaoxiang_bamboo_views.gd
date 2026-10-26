extends SceneTree
var route
var output := ""
var expected := ""
var rows: Array = []
var errors: Array[String] = []
var originals: Dictionary = {}
var masks: Dictionary = {}
var materials: Array = []
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg.begins_with("--source="):expected=arg.trim_prefix("--source=")
 if DisplayServer.get_name()=="headless" or output=="" or expected=="":push_error("Native display, output and frozen source required");quit(1);return
 root.show()
 create_timer(180).timeout.connect(func():push_error("Xiaoxiang capture deadline");quit(1))
 call_deferred("run")
func check(ok: bool,message: String) -> void:
 if not ok:errors.append(message);push_error(message)
func settle() -> void:
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 check(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(),"Incomplete camera tween")
 var started:=Time.get_ticks_msec()
 await create_timer(.25).timeout
 while Time.get_ticks_msec()-started<250:await process_frame
 var drawn:=[false]
 RenderingServer.frame_post_draw.connect(func():drawn[0]=true,CONNECT_ONE_SHOT)
 RenderingServer.force_draw()
 deadline=Time.get_ticks_msec()+10000
 while not drawn[0] and Time.get_ticks_msec()<deadline:await process_frame
 check(drawn[0],"No native draw")
func mask_color(node: MeshInstance3D) -> Color:
 var n:=str(node.name)
 if n.begins_with("HERO_flora_"):return Color(.1,.7,.1)
 if n=="SITE_stage_MAT_stage_canopy_paint":return Color(1,1,0)
 if n.begins_with("SITE_stage_MAT_stage_cyclorama"):return Color(0,1,1)
 if n.begins_with("SITE_stage_MAT_painted_mountains"):return Color(.1,.2,1)
 if n.ends_with("MAT_backstage"):return Color(1,0,0)
 if n=="SITE_xiaoxiang-guan_MAT_crt_amber":return Color(1,.5,0)
 if n=="SITE_xiaoxiang-guan_MAT_lattice_wood":return Color(1,0,1)
 return Color(.25,.25,.25)
func ids(enabled: bool) -> void:
 route.find_child("ColorGrade",true,false).visible=not enabled
 if not enabled:
  for node in originals:node.material_override=originals[node].material;node.visible=originals[node].visible
  return
 for node in route.find_children("*","MeshInstance3D",true,false):
  if not originals.has(node):originals[node]={"material":node.material_override,"visible":node.visible}
  if str(node.name).contains("fog"):node.visible=false;continue
  if not masks.has(node):
   var shader:=Shader.new()
   shader.code="shader_type spatial; render_mode unshaded,cull_disabled,fog_disabled; uniform vec3 id_color; uniform bool alpha_leaf=false; uniform sampler2D atlas; void fragment(){if(alpha_leaf && texture(atlas,UV).a<.45){discard;} ALBEDO=id_color;}"
   var material:=ShaderMaterial.new();material.shader=shader;material.set_shader_parameter("id_color",Vector3(mask_color(node).r,mask_color(node).g,mask_color(node).b))
   if str(node.name).begins_with("HERO_flora_"):
    material.set_shader_parameter("alpha_leaf",true);material.set_shader_parameter("atlas",load("res://materials/flora_atlas.tres").albedo_texture)
   masks[node]=material;materials.append(material)
  node.material_override=masks[node]
func capture(label: String,kind: String) -> void:
 var im:Image=root.get_texture().get_image();var path:=output+"/"+label+"-"+kind+".png"
 check(im.save_png(path)==OK,"Capture save failed")
 var panel:Rect2=route.command_panel.get_global_rect();var header:Rect2=route.status.get_global_rect();var viewport:Vector2=root.get_visible_rect().size
 var count:Dictionary={"ceiling":0,"cyclorama":0,"mountains":0,"backstage":0,"window":0,"gate_wood":0,"flora":0}
 if kind=="ids":
  for y in range(ceili(header.end.y*im.get_height()/viewport.y),mini(im.get_height(),floori(panel.position.y*im.get_height()/viewport.y))):
   for x in range(im.get_width()):
    var c:=im.get_pixel(x,y)
    if c.r>.7 and c.g>.7 and c.b<.2:count.ceiling+=1
    elif c.r<.2 and c.g>.7 and c.b>.7:count.cyclorama+=1
    elif c.r<.4 and c.g<.6 and c.b>.7:count.mountains+=1
    elif c.r>.7 and c.g<.2 and c.b<.2:count.backstage+=1
    elif c.r>.7 and c.g>.35 and c.g<.8 and c.b<.2:count.window+=1
    elif c.r>.7 and c.g<.2 and c.b>.7:count.gate_wood+=1
    elif c.r<.5 and c.g>.6 and c.b<.5:count.flora+=1
  if label.contains("arrival") or label.contains("stems"):check(count.window>=60,"Window disappears in "+label)
  check(count.flora>=50,"No bamboo pixels in "+label)
 rows.append({"label":label,"kind":kind,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[im.get_width(),im.get_height()],"logical_viewport":[viewport.x,viewport.y],"panel_top":panel.position.y,"header_bottom":header.end.y,"camera":str(route.camera.transform),"fov":route.camera.fov,"ids":count,"room":route.room_id,"text":route.output_label.text,"clock":3.0})
func run() -> void:
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==expected,"Source changed")
 check(DirAccess.make_dir_recursive_absolute(output)==OK,"Output directory failure")
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var m=node.get_active_material(surface)
   if m is ShaderMaterial:
    for u in m.shader.get_shader_uniform_list():
     if u.name=="timeline_time":m.set_shader_parameter("timeline_time",3.)
 var flora=route.get_node("FloraLOD");flora.set_process(false)
 for size in [Vector2i(1410,600),Vector2i(390,844)]:
  root.size=size;await process_frame;await process_frame
  var shape:="desktop" if size.x>size.y else "portrait"
  for action in ["arrival","doors","stems"]:
   route.player.position=Vector3(-6.6,.04,13);route._arrive("xiaoxiang_guan",true)
   if action!="arrival":route.execute_command(action)
   await settle()
   check(route.room_id=="xiaoxiang_guan" and not route.travelling,"View left court")
   if action=="doors":check("closed" in route.output_label.text,"Gate became open")
   for lower in [false,true]:
    for plant in flora.plants:
     plant.node.mesh=plant.lower if lower else plant.base;plant.is_lower=lower
    var label:String=shape+"-"+action+("-lod1" if lower else "-lod0")
    ids(false);await settle();await capture(label,"lit")
    ids(true);await settle();await capture(label,"ids")
    ids(false)
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==expected,"Source changed during captures")
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 check(file!=null,"No report")
 if file:file.store_string(JSON.stringify({"source_glb_sha256":expected,"runtime_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"rows":rows,"errors":errors,"scope":"Actual native public arrival/doors/stems views at desktop/portrait, both forced flora qualities, source-ID masks and fixed clock. Excludes physical phone, sustained timing and final site art acceptance."},"  "));file.close()
 print("XIAOXIANG_BAMBOO_VIEWS_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
