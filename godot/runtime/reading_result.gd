extends CanvasLayer
signal recast_requested
var card:RichTextLabel
var result:Dictionary={}

func _ready() -> void:
 layer=3
 var shade=ColorRect.new();shade.color=Color(0,0,0,.78);shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT);add_child(shade)
 var panel=PanelContainer.new();panel.name="ReadingPanel";panel.anchor_left=.06;panel.anchor_right=.94;panel.anchor_top=.08;panel.anchor_bottom=.92
 var style=StyleBoxFlat.new();style.bg_color=Color(.008,.024,.014,1);style.border_color=Color(.5,.42,.22);style.set_border_width_all(1);style.set_content_margin_all(16);panel.add_theme_stylebox_override("panel",style);add_child(panel)
 var column=VBoxContainer.new();column.add_theme_constant_override("separation",10);panel.add_child(column)
 var header=HBoxContainer.new();column.add_child(header)
 var title=Label.new();title.text="THE BRONZE TABLE";title.add_theme_color_override("font_color",Color(1,.65,.2));title.add_theme_font_size_override("font_size",22);title.size_flags_horizontal=Control.SIZE_EXPAND_FILL;header.add_child(title)
 var close=Button.new();close.name="CloseReading";close.text="Close";close.custom_minimum_size=Vector2(74,44);close.pressed.connect(queue_free);header.add_child(close)
 var subtitle=Label.new();subtitle.text="Local three-coin cast · six lines, bottom to top";subtitle.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;column.add_child(subtitle)
 card=RichTextLabel.new();card.name="ReadingText";card.bbcode_enabled=false;card.scroll_active=true;card.size_flags_vertical=Control.SIZE_EXPAND_FILL;card.add_theme_font_size_override("normal_font_size",18);column.add_child(card)
 var again=Button.new();again.name="RecastReading";again.text="Cast again";again.custom_minimum_size.y=44;again.pressed.connect(func():recast_requested.emit());column.add_child(again)
 if not result.is_empty():show_result(result)
 close.grab_focus()

func show_result(cast_result:Dictionary) -> void:
 result=cast_result
 if not card:return
 var first=cast_result.primary;var second=cast_result.transformed
 var text="#%d  %s  ·  %s\n"%[first.number,first.chinese,first.meaning]
 text+="Below: %s   Above: %s\n\n"%[first.lower,first.upper]
 text+="The bronze table shows this pattern from bottom to top.\n"
 if cast_result.moving_lines.is_empty():
  text+="\nNo moving lines in this cast."
 else:
  var positions=[]
  for line in cast_result.moving_lines:positions.append(str(line))
  text+="\nMoving lines: "+", ".join(positions)+"\n"
  text+="Changes toward #%d  %s  ·  %s"%[second.number,second.chinese,second.meaning]
 text+="\n\nThis is a local reading of the hexagram pattern. A detailed interpretation and personal history are not connected yet."
 card.text=text
 card.scroll_to_line(0)

func _unhandled_input(event:InputEvent) -> void:
 if event.is_action_pressed("ui_cancel"):
  get_viewport().set_input_as_handled();queue_free()
