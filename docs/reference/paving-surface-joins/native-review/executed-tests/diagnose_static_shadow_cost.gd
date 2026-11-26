extends SceneTree
func _initialize():call_deferred("run")
func run():
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1);route._arrive("aojing_guan",true);route._begin_pond_view(true)
 var keys=route.find_children("*","Light3D",true,false).filter(func(l):return l is SpotLight3D or l is DirectionalLight3D)
 route.get_node("PracticalLights").update_lights()
 var report={"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"scope":"Temporary static-light/shadow toggles to diagnose draw cost. Does not establish visual or performance acceptance.","variants":{}}
 var overlaps=keys.filter(func(l):return (l.light_cull_mask&2)!=0)
 report.static_keys=keys.size()
 report.keys_overlapping_baked_layer=overlaps.size()
 print("STATIC_KEY_LAYER_OVERLAP ",overlaps.size()," of ",keys.size())
 for mode in ["baseline","static_shadows_disabled","static_keys_disabled"]:
  if mode=="static_shadows_disabled":
   for light in keys:light.shadow_enabled=false
  if mode=="static_keys_disabled":
   for light in keys:light.visible=false
  for i in range(30):await process_frame
  RenderingServer.force_draw()
  var draws=RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME)
  report.variants[mode]={"reported_main_draw_calls":draws}
  print("POND_LIGHTING_DRAW_DIAGNOSIS ",mode," ",draws)
 FileAccess.open("res://pond-lighting-diagnosis.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 quit()
