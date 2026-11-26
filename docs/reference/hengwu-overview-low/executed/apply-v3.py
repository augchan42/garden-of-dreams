"""Apply the verified short-layout fix only to the isolated runtime."""
from pathlib import Path
import json
root=Path('/tmp/garden-hengwu-arrival-20261010')
work=Path(__file__).parent
path=root/'godot/runtime/entry_route.gd'
red=json.loads((root/'overview-short-baseline-red/report.json').read_text())
assert red['status']=='rejected' and len(red['errors'])==8
s=path.read_text()
(root/'runtime-v2-before-compact-layout.gd').write_text(s)
s=s.replace('var output_label: Label\n','''var output_label: Label
var command_stack: VBoxContainer
var compact_command_header: HBoxContainer
var compact_command_actions: HBoxContainer
var compact_command_layout = false
''',1)
s=s.replace(' var stack = VBoxContainer.new()\n',' var stack = VBoxContainer.new()\n command_stack = stack\n',1)
start=s.index('func _hengwu_overview_view(')
end=s.index('func _pavilion_camera_view()',start)
s=s[:start]+'''func _hengwu_overview_view(size: Vector2) -> Array:
 # Keep the book and pierced stones in view from a low position inside the court.
 var portrait=size.x<size.y
 if portrait:
  var short=size.y<size.x*2.14
  var narrow=size.x<380.0
  var target_y=-5.8 if short else (-4.5 if narrow else -4.0)
  var fov=128.0 if short else (118.0 if narrow else 115.0)
  return [Vector3(-19.5,1.8,-17),Vector3(-19,target_y,-12.5),fov]
 var short=size.y<500.0
 var target_y=(-3.0 if touch_ui_enabled else -2.8) if short else (-2.8 if touch_ui_enabled else -2.3)
 return [Vector3(-19.5,1.8,-17),Vector3(-19,target_y,-12.5),118.0 if short else 115.0]

'''+s[end:]
helper='''func _set_compact_command_layout(enabled: bool) -> void:
 if enabled!=compact_command_layout:
  if enabled:
   compact_command_header=HBoxContainer.new()
   compact_command_header.add_theme_constant_override("separation",16)
   compact_command_actions=HBoxContainer.new()
   compact_command_actions.add_theme_constant_override("separation",16)
   command_stack.add_child(compact_command_header)
   command_stack.add_child(compact_command_actions)
   title_label.reparent(compact_command_header)
   output_label.reparent(compact_command_header)
   action_scroll.reparent(compact_command_actions)
   input.reparent(compact_command_actions)
   title_label.vertical_alignment=VERTICAL_ALIGNMENT_CENTER
   output_label.size_flags_horizontal=Control.SIZE_EXPAND_FILL
   action_scroll.size_flags_horizontal=Control.SIZE_EXPAND_FILL
   input.custom_minimum_size.x=220
   action_scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_AUTO
   action_scroll.vertical_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
  else:
   for control in [title_label,output_label,action_scroll,input]:control.reparent(command_stack)
   for index in range(4):command_stack.move_child([title_label,output_label,action_scroll,input][index],index)
   title_label.vertical_alignment=VERTICAL_ALIGNMENT_TOP
   output_label.size_flags_horizontal=Control.SIZE_FILL
   action_scroll.size_flags_horizontal=Control.SIZE_FILL
   input.custom_minimum_size.x=0
   action_scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
   action_scroll.vertical_scroll_mode=ScrollContainer.SCROLL_MODE_AUTO
   compact_command_header.queue_free()
   compact_command_actions.queue_free()
  compact_command_layout=enabled
 # Prevent wrapping in the compact row; every existing action remains reachable
 # by horizontal scrolling, beside the unchanged command entry field.
 var action_width=0.0
 if enabled:
  for button in actions.get_children():action_width+=button.get_combined_minimum_size().x
  action_width+=maxi(0,actions.get_child_count()-1)*actions.get_theme_constant("h_separation")
 actions.custom_minimum_size.x=action_width
 action_scroll.scroll_horizontal=0

'''
s=s.replace('func _fit_action_list() -> void:',helper+'func _fit_action_list() -> void:',1)
needle=' var action_height=actions.get_combined_minimum_size().y\n'
assert needle in s
s=s.replace(needle,' _set_compact_command_layout(not portrait and room_id=="hengwu_yuan" and get_viewport().get_visible_rect().size.y<500.0)\n'+needle,1)
path.write_text(s)
(work/'runtime-candidate-v3.gd').write_text(s)
print('Isolated compact layout V3 written after densityRED26 and shortRED8')
