extends CanvasLayer
var client:Node
var selection:OptionButton
var body:RichTextLabel
var status:Label
var refresh:Button
var topics:Array=[]
var category_filter=""

func _ready() -> void:
 layer=3
 var background=ColorRect.new()
 background.color=Color(0,0,0,.7)
 background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 add_child(background)
 var panel=PanelContainer.new()
 panel.name="TopicPanel"
 panel.anchor_left=.05;panel.anchor_right=.95;panel.anchor_top=.08;panel.anchor_bottom=.92
 var style=StyleBoxFlat.new()
 style.bg_color=Color(.008,.024,.014,1)
 style.border_color=Color(.22,.5,.24)
 style.set_border_width_all(1)
 style.set_content_margin_all(18)
 panel.add_theme_stylebox_override("panel",style)
 add_child(panel)
 var column=VBoxContainer.new()
 column.add_theme_constant_override("separation",12)
 panel.add_child(column)
 var heading=HBoxContainer.new()
 column.add_child(heading)
 var title=Label.new()
 title.text={"temporal":"Current events","timeless":"Ongoing topics"}.get(category_filter,"Current topics")
 title.add_theme_color_override("font_color",Color(1,.65,.2))
 title.add_theme_font_size_override("font_size",22)
 title.size_flags_horizontal=Control.SIZE_EXPAND_FILL
 heading.add_child(title)
 var close=Button.new()
 close.name="CloseBrowser"
 close.text="Close";close.custom_minimum_size=Vector2(70,40)
 close.pressed.connect(queue_free)
 heading.add_child(close)
 close.grab_focus()
 status=Label.new()
 status.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
 column.add_child(status)
 selection=OptionButton.new()
 selection.custom_minimum_size.y=42
 selection.size_flags_horizontal=Control.SIZE_EXPAND_FILL
 selection.fit_to_longest_item=false
 selection.clip_text=true
 selection.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS
 selection.item_selected.connect(_select_topic)
 column.add_child(selection)
 body=RichTextLabel.new()
 body.bbcode_enabled=false
 body.size_flags_vertical=Control.SIZE_EXPAND_FILL
 body.add_theme_font_size_override("normal_font_size",18)
 column.add_child(body)
 refresh=Button.new()
 refresh.text="Refresh topics";refresh.custom_minimum_size.y=42
 refresh.pressed.connect(_fetch)
 column.add_child(refresh)
 client=preload("res://services/topics.gd").new()
 add_child(client)
 client.finished.connect(_received)
 _fetch()

func _fetch() -> void:
 refresh.disabled=true
 selection.disabled=true
 status.text="Loading public topics from 8-Bit Oracle…"
 client.fetch()

func _received(result:Dictionary) -> void:
 refresh.disabled=false
 if not result.ok:
  status.text=result.error
  if not topics.is_empty():status.text+=" Previously loaded topics are still shown."
  selection.disabled=topics.is_empty()
  return
 topics=result.topics.filter(func(topic):return category_filter.is_empty() or topic.category==category_filter)
 selection.clear()
 for topic in topics:selection.add_item(topic.title)
 selection.disabled=topics.is_empty()
 status.text="Live public topics · app.8bitoracle.ai"
 if topics.is_empty():body.text={"temporal":"No active English current-event topics are available.","timeless":"No active English ongoing topics are available."}.get(category_filter,"No active English topics are available.")
 else:
  selection.select(0)
  _select_topic(0)

func _select_topic(index:int) -> void:
 var topic=topics[index]
 body.text=topic.title+"\n\n"+("Current event" if topic.category=="temporal" else "Ongoing topic")+"\n\n"+topic.description+"\n\nReading creation is not connected in the garden yet."

func _unhandled_input(event:InputEvent) -> void:
 if event.is_action_pressed("ui_cancel"):
  get_viewport().set_input_as_handled()
  queue_free()
