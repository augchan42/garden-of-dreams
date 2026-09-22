extends Node3D

signal transition_finished(room_id: String)

const ROOMS = {
 "daoxiang_cun": {"title": "稻香村 · Farmhouse", "text": "Uneven thatch hangs over a closed plank door. A rough fence encloses the yard; painted rice fields rise behind the roof.", "actions": [["Look", "look"], ["Inspect the door", "doors"], ["Inspect the tools", "tools"], ["Look at the paddy", "paddy"], ["Return to study court", "back"]]},
 "aojing_guan": {"title": "凹晶館 · Water-level hall", "text": "A guarded stone ledge sits below the garden paths. One amber window faces the pond beneath a broad tiled roof. The hall remains closed.", "actions": [["Look", "look"], ["Inspect the hall", "doors"], ["Look across the pond", "reflection"], ["Return to red court", "back"]]},
 "longcui_an": {"title": "櫳翠庵 · Nunnery gate", "text": "Sparse plum branches frame the whitewashed wall. One amber lantern hangs beside a closed timber gate; an incense bowl stands beneath it.", "actions": [["Look", "look"], ["Inspect the gate", "doors"], ["Inspect incense bowl", "incense"], ["Return to water pavilion", "back"]]},
 "xiaoxiang_guan": {"title": "瀟湘館 · Bamboo courtyard", "text": "Bamboo clumps frame a narrow stone aisle. One amber window glows between the stems; the timber gate remains closed.", "actions": [["Look", "look"], ["Inspect the gate", "doors"], ["Look through bamboo", "stems"], ["Return to Qinfang", "back"]]},
 "yihong_yuan": {"title": "怡紅院 · Red courtyard", "text": "Banana leaves arch beside paired lacquer doors. A single amber window lights the low court wall. The room beyond remains closed.", "actions": [["Look", "look"], ["Inspect the doors", "doors"], ["Banana leaves", "leaves"], ["Visit the water-level hall", "pond"], ["Return to Qinfang", "back"]]},
 "daguan_lou": {"title": "大觀樓 · Imperial façade", "text": "Two roof tiers span a broad ceremonial front. Bronze studs mark five pairs of closed doors; two amber transoms light the outer bays.", "actions": [["Look", "look"], ["Inspect the doors", "doors"], ["Return to Qinfang", "back"]]},
 "hengwu_yuan": {"title": "蘅蕪苑 · Study courtyard", "text": "Perforated stones stand among low herbs. Four stools surround an open book; no trees rise above the courtyard walls.", "actions": [["Look", "look"], ["Examine the book", "read"], ["Inspect the rocks", "rocks"], ["Ongoing topics", "topics"], ["Visit the farmhouse", "farm"], ["Return to Qinfang", "back"]]},
 "tubi_tang": {"title": "凸碧堂 · Hilltop hall", "text": "A stone table stands on the terrace above the garden. Low parapets frame the roofs below; the painted sky closes the view.", "actions": [["Look", "look"], ["Current events", "topics"], ["Look over the garden", "overlook"], ["Return to bulletin hall", "back"]]},
 "qiushuang_zhai": {"title": "秋爽齋 · Bulletin hall", "text": "Twelve amber screens stand behind lattice panels. Three desks face the courtyard, with scrolls hanging between the screen banks.", "actions": [["Look", "look"], ["Left screens", "left"], ["Centre screens", "centre"], ["Right screens", "right"], ["Climb to the hilltop", "hill"], ["Return to Qinfang", "back"]]},
 "terminal_room": {"title": "Personal terminal", "text": "A green screen lights the desk. Beyond the barred window, a lantern marks the rockery gate.", "actions": [["Look", "look"], ["Use terminal", "terminal"], ["Enter the garden", "exit"]]},
 "rockery_gate": {"title": "曲徑通幽 · Rockery gate", "text": "The plaster passage bends out of sight. Two amber lanterns lead toward the stream.", "actions": [["Look", "look"], ["Follow the lanterns", "enter"], ["Return to your cell", "back"]]},
 "qinfang_ting": {"title": "沁芳亭 · Qinfang Pavilion", "text": "Six lanterns hang over the bridge. A bronze hexagram sits in the stone table; covered walks cross the stream.", "actions": [["Look", "look"], ["Examine the table", "table"], ["Current topics", "topics"], ["Look over the rail", "water"], ["Visit the bulletin hall", "board"], ["Visit the water pavilion", "west"], ["Visit the study court", "study"], ["Visit the imperial façade", "north"], ["Visit the red court", "east"], ["Visit the bamboo court", "bamboo"], ["Return to the gate", "back"]]},
 "ouxiang_xie": {"title": "藕香榭 · Water pavilion", "text": "Two lanterns light an open pavilion over the water. Six seats surround the tea table. A timber bridge leads into the reeds.", "actions": [["Look", "look"], ["Examine the tea table", "tea"], ["Visit the reed island", "island"], ["Visit the nunnery", "nunnery"], ["Return to Qinfang", "back"]]},
 "ziling_zhou": {"title": "紫菱洲 · Reed island", "text": "Reeds surround a low stone landing. Across the timber footbridge, lanterns mark the water pavilion.", "actions": [["Look", "look"], ["Watch the reeds", "reeds"], ["Return to the pavilion", "back"]]}
}
const STUDY_PATH = [Vector3(0,0,1.8),Vector3(2,0,1.8),Vector3(2,0,0),Vector3(7,0,0),Vector3(19.5,0,0),Vector3(19.5,0,-13.5),Vector3(22,0,-13.5)]
const HILL_PATH = [Vector3(22,0,-13.5),Vector3(16.5,0,-13.5),Vector3(16.5,0,-19),Vector3(10,0,-19),Vector3(10,0,-20),Vector3(10,4,-30),Vector3(10,4,-31),Vector3(7,4,-31)]
const COURTYARD_PATH = [Vector3(0,0,1.8),Vector3(-2,0,1.8),Vector3(-2,0,0),Vector3(-7,0,0),Vector3(-19.5,0,0),Vector3(-19.5,0,-3),Vector3(-18,0,-3),Vector3(-18,0,-14.7)]
const FARM_PATH = [Vector3(-18,0,-14.7),Vector3(-18,0,-8),Vector3(-32,0,-8),Vector3(-32,0,-19.3)]
const REFLECTION_PATH = [Vector3(22.6,0,1),Vector3(19.5,0,1),Vector3(19.5,0,9),Vector3(18.5,0,9),Vector3(18.5,0,13.1),Vector3(19.9,0,13.1),Vector3(22.3,-.65,13.1),Vector3(26,-.65,13.1)]
const NUNNERY_PATH = [Vector3(-23,0,0),Vector3(-19.2,0,0),Vector3(-19.2,0,5),Vector3(-25,0,5),Vector3(-25,0,10.6)]
const BAMBOO_PATH = [Vector3(0,0,1.8),Vector3(.8,0,1.8),Vector3(.8,0,3.6),Vector3(0,0,3.6),Vector3(0,0,7),Vector3(0,0,13),Vector3(-5,0,13),Vector3(-6.6,0,13)]
const RED_COURT_PATH = [Vector3(0,0,1.8),Vector3(2,0,1.8),Vector3(2,0,0),Vector3(7,0,0),Vector3(19,0,0),Vector3(22,0,0),Vector3(22.6,0,1)]
const NORTH_PATH = [Vector3(0,0,1.8),Vector3(2,0,1.8),Vector3(2,0,-3.6),Vector3(0,0,-3.6),Vector3(0,0,-7),Vector3(0,0,-19),Vector3(0,0,-20.5)]
const CELL_PATH = [Vector3(-1.3,0,37.4), Vector3(-1.3,0,39.25), Vector3(8.35,0,39.25), Vector3(8.35,0,33), Vector3(0,0,33), Vector3(0,0,32.5)]
const GATE_PATH = [Vector3(0,0,32.5), Vector3(0,0,31), Vector3(1.273,0,29.5), Vector3(1.8,0,28), Vector3(1.273,0,26.5), Vector3(0,0,25), Vector3(-1.273,0,23.5), Vector3(-1.8,0,22), Vector3(-1.273,0,20.5), Vector3(0,0,19), Vector3(0,0,12), Vector3(0,0,7), Vector3(0,0,3.6), Vector3(.8,0,3.6), Vector3(.8,0,1.8), Vector3(0,0,1.8)]

const WEST_PATH = [Vector3(0,0,1.8),Vector3(-2,0,1.8),Vector3(-2,0,0),Vector3(-7,0,0),Vector3(-19,0,0),Vector3(-23,0,0)]
const ISLAND_PATH = [Vector3(-23,0,0),Vector3(-26,0,0),Vector3(-31,0,0),Vector3(-35.4,0,0)]

var room_id = "terminal_room"
var travelling = false
var player: CharacterBody3D
var camera: Camera3D
var title_label: Label
var output_label: Label
var action_scroll: ScrollContainer
var actions: HFlowContainer
var input: LineEdit
var status: Label
var path: Array[Vector3] = []
var destination = ""
var waypoint = 0
var stalled_time = 0.0
var last_position = Vector3.ZERO
var travel_elapsed = 0.0
var camera_tween: Tween
var command_panel: PanelContainer
var hexagram_table: Node
var gate_reveal_active = false
var gate_reveal_done = false
const GATE_REVEAL_TARGET = Vector3(0,1.8,0)
const GATE_REVEAL_RAIL = [Vector3(-2.5,1.8,16.7),Vector3(-3,5.8,16),Vector3(10,5.5,12)]

func _ready() -> void:
 get_tree().root.content_scale_size = Vector2i.ZERO
 var environment = load("res://garden_preview.tscn").instantiate()
 add_child(environment)
 hexagram_table=preload("res://runtime/hexagram_table.gd").new()
 hexagram_table.name="HexagramTable"
 add_child(hexagram_table)
 if not hexagram_table.configure(environment):push_error("Hexagram table is missing solid/broken line pairs")
 # Only this route's camera is current; asset cameras remain available for editing.
 player = CharacterBody3D.new()
 player.name = "Visitor"
 var collider = CollisionShape3D.new()
 var capsule = CapsuleShape3D.new()
 capsule.radius = .22
 capsule.height = 1.65
 collider.shape = capsule
 collider.position.y = .83
 player.add_child(collider)
 add_child(player)
 player.position = CELL_PATH[0] + Vector3(0,.03,0)
 var practicals = preload("res://runtime/practical_lights.gd").new()
 practicals.name = "PracticalLights"
 add_child(practicals)
 practicals.configure(environment,player)
 camera = Camera3D.new()
 camera.name = "RouteCamera"
 camera.near = .06
 camera.far = 160
 camera.fov = 55
 add_child(camera)
 camera.current = true
 var reflection=preload("res://runtime/pond_reflection.gd").new()
 reflection.name="PondReflection"
 add_child(reflection)
 reflection.configure(environment,camera,player)
 _build_ui()
 get_viewport().size_changed.connect(func(): call_deferred("_fit_action_list"))
 _arrive("terminal_room", true)

func _build_ui() -> void:
 var layer = CanvasLayer.new()
 layer.layer = 2
 add_child(layer)
 var panel = PanelContainer.new()
 command_panel = panel
 panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
 panel.offset_top = -195
 panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
 var style = StyleBoxFlat.new()
 style.bg_color = Color(.006,.018,.01,.95)
 style.border_color = Color(.18,.45,.18)
 style.border_width_top = 1
 style.content_margin_left = 24
 style.content_margin_right = 24
 style.content_margin_top = 12
 style.content_margin_bottom = 12
 panel.add_theme_stylebox_override("panel", style)
 layer.add_child(panel)
 var stack = VBoxContainer.new()
 stack.add_theme_constant_override("separation", 7)
 panel.add_child(stack)
 title_label = Label.new()
 title_label.add_theme_font_size_override("font_size",22)
 title_label.add_theme_color_override("font_color",Color(1,.65,.2))
 stack.add_child(title_label)
 output_label = Label.new()
 output_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
 output_label.custom_minimum_size.y = 40
 output_label.add_theme_font_size_override("font_size",16)
 output_label.add_theme_color_override("font_color",Color(.74,.87,.72))
 stack.add_child(output_label)
 actions = HFlowContainer.new()
 actions.add_theme_constant_override("h_separation",10)
 action_scroll = ScrollContainer.new()
 action_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
 action_scroll.custom_minimum_size.y = 80
 actions.size_flags_horizontal = Control.SIZE_EXPAND_FILL
 action_scroll.add_child(actions)
 stack.add_child(action_scroll)
 input = LineEdit.new()
 input.placeholder_text = "Or type a command: look, help, exit…"
 input.custom_minimum_size.y = 36
 input.text_submitted.connect(func(text):
  input.clear()
  execute_command(text))
 stack.add_child(input)
 status = Label.new()
 status.position = Vector2(20,16)
 status.add_theme_font_size_override("font_size",15)
 status.add_theme_color_override("font_color",Color(.8,.9,.75))
 status.text = "GARDEN OF DREAMS · Local scene exploration"
 layer.add_child(status)

func execute_command(text: String) -> void:
 var cmd = text.strip_edges().to_lower()
 if travelling:
  output_label.text = "You are on the path. The next room's actions will appear when you arrive."
  return
 match cmd:
  "look":
   if room_id=="qinfang_ting":_arrive(room_id)
   else:output_label.text = ROOMS[room_id].text
  "help": output_label.text = "Choose an action below or type its command. Movement follows the garden paths; the camera moves with you."
  "terminal":
   output_label.text = "The terminal is ready. Personal readings and history are not connected yet." if room_id == "terminal_room" else "Your personal terminal is in the cell."
  "topics":
   if room_id not in ["qinfang_ting","tubi_tang","hengwu_yuan"]:
    output_label.text="Public topics are available at Qinfang Pavilion, the hilltop hall and the study courtyard."
   elif not has_node("TopicBrowser"):
    var browser=preload("res://runtime/topic_browser.gd").new()
    browser.category_filter={"tubi_tang":"temporal","hengwu_yuan":"timeless"}.get(room_id,"")
    browser.name="TopicBrowser"
    input.editable=false
    for button in actions.get_children():button.disabled=true
    browser.tree_exiting.connect(func():
     input.editable=not travelling
     for button in actions.get_children():button.disabled=travelling)
    add_child(browser)
  "table":
   if room_id=="qinfang_ting":
    output_label.text="Six bronze lines show the local table display, read from bottom to top. The live reading feed is not connected yet."
    var size=get_viewport().get_visible_rect().size
    camera.keep_aspect=Camera3D.KEEP_WIDTH if size.x<size.y else Camera3D.KEEP_HEIGHT
    _camera_to(Vector3(0,2.45,1.15),Vector3(0,.55,0))
   else:output_label.text="The hexagram table is in 沁芳亭."
  "water":
   if room_id == "qinfang_ting":
    output_label.text = "The stream passes under the bridge. Beyond the roofs, the painted moon hangs against the studio sky."
    _camera_to(Vector3(5,2.4,5),Vector3(-3,-.4,0))
  "exit":
   if room_id == "terminal_room": _travel(CELL_PATH,"rockery_gate")
   else: output_label.text = "Choose a path from the actions below."
  "enter", "continue":
   if room_id == "rockery_gate": _travel(GATE_PATH,"qinfang_ting")
   else: output_label.text = "There is no entrance to follow here."
  "board":
   if room_id == "qinfang_ting": _travel(STUDY_PATH,"qiushuang_zhai")
   else: output_label.text = "The bulletin hall approach starts at Qinfang Pavilion."
  "hill":
   if room_id == "qiushuang_zhai": _travel(HILL_PATH,"tubi_tang")
   else: output_label.text = "The hilltop path starts beside the bulletin hall."
  "farm":
   if room_id == "hengwu_yuan": _travel(FARM_PATH,"daoxiang_cun")
   else: output_label.text = "The farmhouse path starts at the study courtyard."
  "tools":
   if room_id == "daoxiang_cun":
    output_label.text = "A wooden rake and a short-bladed hoe lean against the farmhouse wall."
    _camera_to(Vector3(-32.5,1.5,-19.8),Vector3(-34,.8,-21.2))
   else: output_label.text = "The tools stand beside the farmhouse door."
  "paddy":
   if room_id == "daoxiang_cun":
    output_label.text = "Rice terraces and low hills are painted on a framed studio flat beside the farmhouse. Broad brush strokes remain visible across the fields."
    _camera_to(Vector3(-38,2.5,-19),Vector3(-37.3,1.6,-23.8))
   else: output_label.text = "The painted paddy stands behind the farmhouse."
  "pond":
   if room_id == "yihong_yuan": _travel(REFLECTION_PATH,"aojing_guan")
   else: output_label.text = "The pond approach starts at the red courtyard."
  "reflection":
   if room_id == "aojing_guan":
    output_label.text = "The pond sits below the dry ledge. The window and roof reflect in the green water, broken by small moving ripples."
    _camera_to(Vector3(26,4,27),Vector3(26,-2,14.5))
   else: output_label.text = "The low pond lies beside the water-level hall."
  "nunnery":
   if room_id == "ouxiang_xie": _travel(NUNNERY_PATH,"longcui_an")
   else: output_label.text = "The nunnery approach starts at the water pavilion."
  "incense":
   if room_id == "longcui_an":
    output_label.text = "Three incense sticks stand in an open bronze bowl supported by three feet. The single lantern lights its rim."
    _camera_to(Vector3(-25.3,1.5,10.2),Vector3(-26.6,.85,11.75))
   else: output_label.text = "The incense bowl stands beside the nunnery gate."
  "bamboo":
   if room_id == "qinfang_ting": _travel(BAMBOO_PATH,"xiaoxiang_guan")
   else: output_label.text = "The bamboo courtyard path starts at Qinfang Pavilion."
  "stems":
   if room_id == "xiaoxiang_guan":
    output_label.text = "Three heights of jointed bamboo leave gaps around the stone aisle. The amber window remains visible beyond the leaves."
    _camera_to(Vector3(-4.8,2.4,13),Vector3(-8,2,11.3))
   else: output_label.text = "The bamboo court lies along the southern path."
  "east":
   if room_id == "qinfang_ting": _travel(RED_COURT_PATH,"yihong_yuan")
   else: output_label.text = "The red courtyard approach starts at Qinfang Pavilion."
  "leaves":
   if room_id == "yihong_yuan":
    output_label.text = "Broad banana leaves curve from two stems, with raised midribs and drooping tips."
    _camera_to(Vector3(21.5,2.3,.5),Vector3(23.65,1.7,-1.45))
   else: output_label.text = "The banana plants stand beside the red courtyard."
  "north":
   if room_id == "qinfang_ting": _travel(NORTH_PATH,"daguan_lou")
   else: output_label.text = "The north covered walk starts at Qinfang Pavilion."
  "doors":
   if room_id == "daguan_lou":
    output_label.text = "The ceremonial doors are closed. Bronze studs and paired pulls catch the green light. This hall has no public interior."
    _camera_to(Vector3(0,1.7,-19.8),Vector3(0,1.7,-23))
   elif room_id == "yihong_yuan":
    output_label.text = "The paired lacquer doors are closed. Bronze pulls sit above the stone threshold; this future room has no public interior."
    _camera_to(Vector3(22.2,1.65,1),Vector3(25,1.4,1))
   elif room_id == "xiaoxiang_guan":
    output_label.text = "The timber gate is closed. A stone threshold marks the entrance; the future room has no public interior."
    _camera_to(Vector3(-6.4,1.6,13.85),Vector3(-9,1.4,13.85))
   elif room_id == "longcui_an":
    output_label.text = "The nunnery gate is closed. Plum branches cast shadows across the capped wall; there is no public interior."
    _camera_to(Vector3(-25,1.65,10.2),Vector3(-25,1.4,13))
   elif room_id == "aojing_guan":
    output_label.text = "The hall is closed. One amber window faces the water between dark shutters."
    _camera_to(Vector3(26,.95,14),Vector3(26,.8,12.2))
   elif room_id == "daoxiang_cun":
    output_label.text = "The farmhouse door is closed. A narrow warm sliver shows beneath its planks; no public interior is available."
    _camera_to(Vector3(-32,1.7,-19.7),Vector3(-32,1.2,-22))
   else: output_label.text = "There are no closed doors to inspect here."
  "study":
   if room_id == "qinfang_ting": _travel(COURTYARD_PATH,"hengwu_yuan")
   else: output_label.text = "The study courtyard path starts at Qinfang Pavilion."
  "read":
   if room_id == "hengwu_yuan":
    output_label.text = "An open book rests on the stone table. Live study circles are not connected yet; Ongoing topics opens the public topic list."
    _camera_to(Vector3(-18,1.8,-13.4),Vector3(-20,.85,-14.7))
   else: output_label.text = "The study table is in the herb courtyard."
  "rocks":
   if room_id == "hengwu_yuan":
    output_label.text = "Light passes through nine holes in three plaster stones. Low herbs leave their outlines exposed."
    _camera_to(Vector3(-15.6,1.6,-10.6),Vector3(-15.4,1.35,-12.5))
   else: output_label.text = "The perforated stones are in the study courtyard."
  "overlook":
   if room_id == "tubi_tang":
    output_label.text = "The bridge pavilion lies below. Beyond the roofs, the painted cyclorama closes the garden."
    _camera_to(Vector3(7,5.7,-30.5),Vector3(0,1.2,0))
   else: output_label.text = "The overlook is on the hilltop terrace."
  "left", "centre", "right":
   if room_id == "qiushuang_zhai":
    output_label.text = "The " + cmd + " bank has four amber monitors. Live bulletin content is not connected yet."
    var x = {"left":18.85,"centre":22.0,"right":25.15}[cmd]
    _camera_to(Vector3(x,1.7,-12.7),Vector3(x,1.35,-15.6))
   else: output_label.text = "The screen banks are in the bulletin hall."
  "west":
   if room_id == "qinfang_ting": _travel(WEST_PATH,"ouxiang_xie")
   else: output_label.text = "The western covered walk starts at Qinfang Pavilion."
  "island":
   if room_id == "ouxiang_xie": _travel(ISLAND_PATH,"ziling_zhou")
   else: output_label.text = "The island footbridge starts at the water pavilion."
  "tea":
   output_label.text = "Six cups wait around the tea table. Group readings are not connected yet." if room_id == "ouxiang_xie" else "The tea table is in the water pavilion."
  "reeds":
   output_label.text = "Dark seed heads rise above the water. The low island leaves the distant roofs visible." if room_id == "ziling_zhou" else "The reed island is beyond the water pavilion."
  "back":
   if room_id == "daoxiang_cun":
    var reverse = FARM_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"hengwu_yuan")
    return
   if room_id == "aojing_guan":
    var reverse = REFLECTION_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"yihong_yuan")
    return
   if room_id == "longcui_an":
    var reverse = NUNNERY_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"ouxiang_xie")
    return
   if room_id == "xiaoxiang_guan":
    var reverse = BAMBOO_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"qinfang_ting")
    return
   if room_id == "yihong_yuan":
    var reverse = RED_COURT_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"qinfang_ting")
    return
   if room_id == "daguan_lou":
    var reverse = NORTH_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"qinfang_ting")
    return
   if room_id == "hengwu_yuan":
    var reverse = COURTYARD_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"qinfang_ting")
    return
   if room_id == "tubi_tang":
    var reverse = HILL_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"qiushuang_zhai")
    return
   if room_id == "qiushuang_zhai":
    var reverse = STUDY_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"qinfang_ting")
    return
   if room_id in ["ouxiang_xie","ziling_zhou"]:
    var reverse = (WEST_PATH if room_id == "ouxiang_xie" else ISLAND_PATH).duplicate()
    reverse.reverse()
    _travel(reverse,"qinfang_ting" if room_id == "ouxiang_xie" else "ouxiang_xie")
    return
   if room_id == "qinfang_ting":
    var reverse = GATE_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"rockery_gate")
   elif room_id == "rockery_gate":
    var reverse = CELL_PATH.duplicate()
    reverse.reverse()
    _travel(reverse,"terminal_room")
   else: output_label.text = "You are already in your cell."
  _: output_label.text = "Unknown command. Choose an action below, or type help."

func _travel(points: Array, target_room: String) -> void:
 camera.keep_aspect = Camera3D.KEEP_HEIGHT
 if camera_tween and camera_tween.is_valid(): camera_tween.kill()
 gate_reveal_active = false
 gate_reveal_done = false
 command_panel.show()
 path.assign(points)
 waypoint = 1
 destination = target_room
 travelling = true
 stalled_time = 0
 travel_elapsed = 0
 last_position = player.position
 output_label.text = "Walking to " + ROOMS[target_room].title + "…"
 status.text = "ON THE PATH · " + ROOMS[target_room].title
 for button in actions.get_children(): button.disabled = true
 input.editable = false

func _begin_gate_reveal() -> void:
 gate_reveal_active = true
 gate_reveal_done = true
 command_panel.hide()
 player.velocity.x = 0
 player.velocity.z = 0
 if camera_tween and camera_tween.is_valid(): camera_tween.kill()
 var size=get_viewport().get_visible_rect().size
 camera.keep_aspect=Camera3D.KEEP_WIDTH if size.x<size.y else Camera3D.KEEP_HEIGHT
 status.text="THE GARDEN · 沁芳亭"
 output_label.text="The passage opens onto the stream. Beyond the covered walks, the pavilion stands in green light."
 camera_tween=create_tween()
 for i in range(GATE_REVEAL_RAIL.size()):
  var pose=Transform3D(Basis.IDENTITY,GATE_REVEAL_RAIL[i]).looking_at(GATE_REVEAL_TARGET,Vector3.UP)
  camera_tween.tween_property(camera,"transform",pose,[.8,.8,1.8][i]).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
 camera_tween.tween_interval(.6)
 camera_tween.tween_callback(_finish_gate_reveal)

func _finish_gate_reveal() -> void:
 gate_reveal_active = false
 command_panel.show()
 stalled_time = 0
 last_position = player.position
 status.text="ON THE PATH · "+ROOMS[destination].title

func _physics_process(delta: float) -> void:
 if not is_instance_valid(player): return
 player.velocity.y = 0 if player.is_on_floor() else maxf(player.velocity.y - 20*delta,-20)
 if travelling and room_id=="rockery_gate" and destination=="qinfang_ting" and not gate_reveal_done and player.position.z<15.5:
  _begin_gate_reveal()
 if gate_reveal_active:
  player.velocity.x=0
  player.velocity.z=0
  player.move_and_slide()
  return
 if travelling:
  travel_elapsed += delta
  var direction = path[waypoint] - player.position
  direction.y = 0
  if direction.length() < .13:
   waypoint += 1
   if waypoint >= path.size():
    travelling = false
    player.velocity.x = 0
    player.velocity.z = 0
    _arrive(destination)
   else: direction = (path[waypoint]-player.position) * Vector3(1,0,1)
  if travelling:
   var speed = minf(2.4,direction.length()/maxf(delta,.001))
   player.velocity.x = direction.normalized().x * speed
   player.velocity.z = direction.normalized().z * speed
   # Fixed follow rail through cells and tunnel; no free-look controls.
   if not gate_reveal_done:
    var facing = direction.normalized()
    var desired = player.position + Vector3(0,1.55,0) - facing*1.1
    camera.position = camera.position.lerp(desired,minf(delta*4,1))
    camera.look_at(player.position+Vector3(0,1.2,0)+facing*2,Vector3.UP)
   stalled_time = stalled_time + delta if player.position.distance_to(last_position)<.003 else 0
   last_position = player.position
   if stalled_time > 3.0 or player.position.y < -2:
    travelling = false
    player.velocity = Vector3.ZERO
    _arrive(room_id)
    output_label.text = "This path is obstructed. Movement stopped; the route needs repair."
    push_error("ROUTE_OBSTRUCTED: %s waypoint %d at %s" % [destination,waypoint,player.position])
 player.move_and_slide()

func _arrive(id: String, immediate = false) -> void:
 gate_reveal_active = false
 command_panel.show()
 room_id = id
 title_label.text = ROOMS[id].title
 output_label.text = ROOMS[id].text
 status.text = "GARDEN OF DREAMS · Local scene exploration"
 input.editable = true
 for button in actions.get_children():
  actions.remove_child(button)
  button.queue_free()
 for action in ROOMS[id].actions:
  var button = Button.new()
  button.text = action[0]
  button.custom_minimum_size = Vector2(140,38)
  button.pressed.connect(execute_command.bind(action[1]))
  actions.add_child(button)
 call_deferred("_fit_action_list")
 var views = {
  "daoxiang_cun": [Vector3(-34,3.4,-13),Vector3(-34,1.7,-22)],
  "aojing_guan": [Vector3(24,4,27),Vector3(26,-2,14.5)],
  "longcui_an": [Vector3(-22,2.6,6),Vector3(-25,1.45,12.2)],
  "xiaoxiang_guan": [Vector3(-2,2.3,13),Vector3(-8.8,1.6,12.5)],
  "yihong_yuan": [Vector3(18,3.1,5),Vector3(24.3,1.25,1)],
  "daguan_lou": [Vector3(7,3.2,-11),Vector3(0,2.2,-23)],
  "hengwu_yuan": [Vector3(-17.5,2.6,-10.5),Vector3(-18,1.1,-15.2)],
  "tubi_tang": [Vector3(16,10,-20),Vector3(7,4.9,-32)],
  "qiushuang_zhai": [Vector3(22,3.2,-6.8),Vector3(22,1.45,-15.5)],
  "terminal_room": [Vector3(-1.3,1.6,38.7),Vector3(-1.3,1.1,36.5)],
  "rockery_gate": [Vector3(0,1.85,35.7),Vector3(0,1.9,29)],
  "qinfang_ting": [Vector3(10,5.5,12),Vector3(0,1.8,0)],
  "ouxiang_xie": [Vector3(-15,5,10),Vector3(-23,1.8,0)],
  "ziling_zhou": [Vector3(-40,3,6),Vector3(-34,.6,0)]}
 var view_position: Vector3 = views[id][0]
 var view_target: Vector3 = views[id][1]
 var viewport_size = get_viewport().get_visible_rect().size
 var portrait = viewport_size.x < viewport_size.y
 camera.keep_aspect = Camera3D.KEEP_WIDTH if portrait and id in ["rockery_gate","qiushuang_zhai","hengwu_yuan","daguan_lou","yihong_yuan","xiaoxiang_guan","longcui_an","aojing_guan","daoxiang_cun"] else Camera3D.KEEP_HEIGHT
 if portrait and id not in ["terminal_room","rockery_gate","qiushuang_zhai","xiaoxiang_guan","hengwu_yuan"]:
  view_position = view_target + (view_position - view_target) * 1.4
 _camera_to(view_position,view_target,immediate)
 transition_finished.emit(id)

func _fit_action_list() -> void:
 await get_tree().process_frame
 var portrait = get_viewport().get_visible_rect().size.x < get_viewport().get_visible_rect().size.y
 action_scroll.custom_minimum_size.y = minf(actions.get_combined_minimum_size().y,152.0) if portrait and room_id=="qinfang_ting" else actions.get_combined_minimum_size().y
 action_scroll.scroll_vertical = 0

func _camera_to(position: Vector3, target: Vector3, immediate = false) -> void:
 if camera_tween and camera_tween.is_valid(): camera_tween.kill()
 var transform_target = Transform3D(camera.basis,position).looking_at(target,Vector3.UP)
 if immediate:
  camera.transform = transform_target
 else:
  camera_tween = create_tween()
  camera_tween.tween_property(camera,"transform",transform_target,1.4).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
