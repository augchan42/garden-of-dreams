extends CanvasLayer

signal replay_requested

var reading: Dictionary = {}
var touch_ui_enabled = false

func _ready() -> void:
 layer = 4
 var shade = ColorRect.new()
 shade.color = Color(0, 0, 0, .82)
 shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 add_child(shade)
 var panel = PanelContainer.new()
 panel.name = "FinalePanel"
 panel.anchor_left = .08
 panel.anchor_right = .92
 panel.anchor_top = .19
 panel.anchor_bottom = .81
 var style = StyleBoxFlat.new()
 style.bg_color = Color(.008, .024, .014)
 style.border_color = Color(.7, .52, .25)
 style.set_border_width_all(1)
 style.set_content_margin_all(24)
 panel.add_theme_stylebox_override("panel", style)
 add_child(panel)
 var column = VBoxContainer.new()
 column.alignment = BoxContainer.ALIGNMENT_CENTER
 column.add_theme_constant_override("separation", 16)
 panel.add_child(column)
 var heading = Label.new()
 heading.text = "YOUR FIRST READING"
 heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
 heading.add_theme_font_size_override("font_size", 22)
 heading.add_theme_color_override("font_color", Color(1, .68, .28))
 column.add_child(heading)
 var summary = Label.new()
 summary.name = "ReadingSummary"
 var first: Dictionary = reading.get("primary", {})
 summary.text = "#%d · %s · %s" % [first.get("number", 0), first.get("chinese", ""), first.get("meaning", "")]
 summary.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
 summary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
 summary.add_theme_font_size_override("font_size", 22)
 column.add_child(summary)
 var note = Label.new()
 note.text = "The six lines remain on the bronze table. Thank you for visiting the garden."
 note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
 note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
 column.add_child(note)
 var replay = Button.new()
 replay.name = "ReplayDemo"
 replay.text = "Begin again"
 replay.custom_minimum_size.y = 48
 replay.pressed.connect(func(): replay_requested.emit())
 column.add_child(replay)
 var close = Button.new()
 close.name = "CloseFinale"
 close.text = "Stay at the pavilion"
 close.custom_minimum_size.y = 48 if touch_ui_enabled else 44
 close.pressed.connect(queue_free)
 column.add_child(close)
 replay.grab_focus()

func _unhandled_input(event: InputEvent) -> void:
 if event.is_action_pressed("ui_cancel"):
  get_viewport().set_input_as_handled()
  queue_free()
