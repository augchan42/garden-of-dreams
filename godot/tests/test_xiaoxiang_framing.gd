extends "res://tests/test_xiaoxiang_bamboo_views.gd"
var touch := false
var density := false
var subjects: Dictionary = {}
var measurements: Array = []
func _initialize() -> void:
 super._initialize()
 for arg in OS.get_cmdline_user_args():
  if arg=="--touch":touch=true
  if arg=="--density":density=true;touch=true
func press(label: String) -> void:
 for button in route.actions.get_children():
  if button is Button and button.text==label:
   check(not button.disabled,"Disabled public action "+label);button.pressed.emit();return
 check(false,"Missing public action "+label)
func measure(points: Array) -> Dictionary:
 var low:=Vector2(INF,INF);var high:=Vector2(-INF,-INF);var behind:=0
 for p in points:
  var world:=Vector3(p[0],p[1],p[2]);if route.camera.is_position_behind(world):behind+=1
  var pixel:Vector2=route.camera.unproject_position(world);low=low.min(pixel);high=high.max(pixel)
 var size:Vector2=root.get_visible_rect().size;var header:Rect2=route.status.get_global_rect();var panel:Rect2=route.command_panel.get_global_rect()
 return {"low":[low.x,low.y],"high":[high.x,high.y],"width_fraction":(high.x-low.x)/size.x,"fits":behind==0 and low.x>=12 and high.x<=size.x-12 and low.y>=header.end.y+12 and high.y<=panel.position.y-14,"behind":behind,"panel_top":panel.position.y,"header_bottom":header.end.y}
func inspect(label: String,kind: String,portrait: bool) -> void:
 ids(false);await settle();await capture(label,"lit")
 var shape:=measure(subjects[kind]);measurements.append({"label":label,"subject":kind,"measurement":shape})
 if portrait:
  check(route.camera.keep_aspect==Camera3D.KEEP_WIDTH,"Portrait projection: "+label)
  check(shape.fits,"Subject clipped or covered: "+label)
  if kind=="arrival":check(shape.width_fraction>=.6,"Facade too small: "+label)
 ids(true);await settle();await capture(label,"ids");ids(false)
 var row:Dictionary=rows[-1]
 if portrait and kind=="arrival":
  var scene_pixels:float=row.pixels[0]*(floorf(row.panel_top*row.pixels[1]/row.logical_viewport[1])-ceilf(row.header_bottom*row.pixels[1]/row.logical_viewport[1]))
  check(float(row.ids.ceiling)/scene_pixels<=.15,"Ceiling dominates portrait overview: "+label)
 if kind=="doors":check(row.ids.gate_wood>=200,"Gate disappeared: "+label)
func desktop_pose(kind: String) -> void:
 var position:Vector3={"arrival":Vector3(-2,2.3,13),"doors":Vector3(-6.4,1.6,13.85),"stems":Vector3(-4.8,2.4,13)}[kind]
 var target:Vector3={"arrival":Vector3(-8.8,1.6,12.5),"doors":Vector3(-9,1.4,13.85),"stems":Vector3(-8,2,11.3)}[kind]
 var wanted:=Transform3D(Basis.IDENTITY,position).looking_at(target,Vector3.UP)
 check(route.camera.transform.is_equal_approx(wanted) and is_equal_approx(route.camera.fov,55.) and route.camera.keep_aspect==Camera3D.KEEP_HEIGHT,"Original desktop pose not restored: "+kind)
func run() -> void:
 check(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==expected,"Source changed")
 check(DirAccess.make_dir_recursive_absolute(output)==OK,"Output directory failure")
 var geometry:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/xiaoxiang-camera-subjects-complete.json"))
 check(geometry.source_glb_sha256==expected,"Projection source mismatch")
 subjects.arrival=geometry.subjects.XIAOXIANG_closed_front.points
 subjects.doors=[]
 for name in ["XIAOXIANG_gate_leaf","XIAOXIANG_gate_leaf.001","XIAOXIANG_threshold"]:subjects.doors.append_array(geometry.subjects[name].points)
 subjects.stems=geometry.subjects.HERO_flora_xiaoxiang_guan_1.points.duplicate()
 subjects.stems.append_array(geometry.subjects.XIAOXIANG_amber_window.points)
 check(subjects.arrival.size()==8 and subjects.doors.size()==24 and subjects.stems.size()==968,"Saved subject inventory changed")
 var fit_geometry:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/xiaoxiang-camera-subjects.json"))
 check(fit_geometry.source_glb_sha256==expected,"Runtime camera geometry source mismatch")
 for kind in ["doors","stems"]:
  check(fit_geometry.subjects[kind].size()==subjects[kind].size(),"Runtime subject inventory changed: "+kind)
  for point in fit_geometry.subjects[kind]:check(subjects[kind].has(point),"Runtime subject differs from saved source: "+kind)
 var portrait_size:=Vector2i(1080,2340) if density else Vector2i(390,844)
 var narrow_size:=Vector2i(945,2100) if density else Vector2i(360,800)
 var wide_size:=Vector2i(1440,2560) if density else Vector2i(540,960)
 var desktop_size:=Vector2i(2340,1080) if density else Vector2i(1410,600)
 root.size=portrait_size
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route);route._configure_ui_scale(touch,420 if density else 160)
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.)
 await settle();check(route.site_bakes_enabled,"Completed lighting disabled")
 route.player.position=Vector3(-6.6,.04,13);route._arrive("xiaoxiang_guan",true);await settle()
 var visitor:Vector3=route.player.position;var initial:Transform3D=route.camera.transform
 await inspect("arrival-portrait","arrival",true)
 root.size=narrow_size;await settle();await inspect("arrival-narrow","arrival",true)
 root.size=wide_size;await settle();await inspect("arrival-wide","arrival",true)
 root.size=desktop_size;await settle();desktop_pose("arrival");await inspect("arrival-desktop","arrival",false)
 root.size=portrait_size;await settle();await inspect("arrival-return","arrival",true)
 initial=route.camera.transform
 for kind in ["doors","stems"]:
  press("Inspect the gate" if kind=="doors" else "Look through bamboo");await settle()
  var selected_text:String=route.output_label.text
  await inspect(kind+"-portrait",kind,true)
  root.size=narrow_size;await settle();await inspect(kind+"-narrow",kind,true)
  check(route.output_label.text==selected_text,"Resize replaced selected text: "+kind)
  root.size=desktop_size;await settle();desktop_pose(kind);await inspect(kind+"-desktop",kind,false)
  root.size=portrait_size;await settle();await inspect(kind+"-return",kind,true)
  check(route.output_label.text==selected_text,"Rotation replaced selected text: "+kind)
  var selected:Transform3D=route.camera.transform
  press("Look");await settle();await inspect(kind+"-look","arrival",true)
  check(not route.camera.transform.is_equal_approx(selected) and route.camera.transform.is_equal_approx(initial),"Look did not restore overview: "+kind)
  check(route.output_label.text==route.ROOMS.xiaoxiang_guan.text,"Look did not restore arrival text")
 check(route.player.position.distance_to(visitor)<.005 and route.room_id=="xiaoxiang_guan","Camera actions changed visitor or room")
 if touch:
  check(route.input.size.y>=48,"Touch input below48")
  for button in route.actions.get_children():check(button.size.y>=48,"Touch action below48")
  route.action_scroll.scroll_vertical=10000;await settle()
  var last=route.actions.get_child(route.actions.get_child_count()-1)
  check(route.action_scroll.get_global_rect().encloses(last.get_global_rect()),"Return action unreachable")
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE);file.store_string(JSON.stringify({"status":"xiaoxiang_framing_passed" if errors.is_empty() else "rejected","source_glb_sha256":expected,"runtime_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"test_sha256":FileAccess.get_sha256("res://tests/test_xiaoxiang_framing.gd"),"touch":touch,"density":density,"rows":rows,"measurements":measurements,"errors":errors,"scope":"Completed-lighting native public overview/gate/stems/Look, projected saved facade and full gate+threshold or selected medium clump+pane above actual UI, actual ID visibility and ceiling fraction, resize/rotation/text/visitor preservation, original desktop poses and touch targets/return access. No physical-phone, full moving tour or final-art acceptance."},"  "));file.close()
 print("XIAOXIANG_FRAMING_RESULT ",rows.size()," originals; ",errors.size()," failures");quit(0 if errors.is_empty() else 1)
