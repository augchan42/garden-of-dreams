extends Node3D

signal transition_finished(room_id: String)

@export var demo_mode = false
@export var site_bakes_enabled = true

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
 "qinfang_ting": {"title": "沁芳亭 · Qinfang Pavilion", "text": "Six lanterns hang over the bridge. A bronze hexagram sits in the stone table; covered walks cross the stream.", "actions": [["Look", "look"], ["Examine the table", "table"], ["Cast at the table", "cast"], ["Current topics", "topics"], ["Look over the rail", "water"], ["Visit the bulletin hall", "board"], ["Visit the water pavilion", "west"], ["Visit the study court", "study"], ["Visit the imperial façade", "north"], ["Visit the red court", "east"], ["Visit the bamboo court", "bamboo"], ["Return to the gate", "back"]]},
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
const CELL_PATH = [Vector3(-1.3,0,37.98), Vector3(-1.3,0,39.25), Vector3(8.35,0,39.25), Vector3(8.35,0,33), Vector3(0,0,33), Vector3(0,0,32.5)]
const GATE_PATH = [Vector3(0,0,32.5), Vector3(0,0,31), Vector3(1.273,0,29.5), Vector3(1.8,0,28), Vector3(1.273,0,26.5), Vector3(0,0,25), Vector3(-1.273,0,23.5), Vector3(-1.8,0,22), Vector3(-1.273,0,20.5), Vector3(0,0,19), Vector3(0,0,12), Vector3(0,0,7), Vector3(0,0,3.6), Vector3(.8,0,3.6), Vector3(.8,0,1.8), Vector3(0,0,1.8)]

const WEST_PATH = [Vector3(0,0,1.8),Vector3(-2,0,1.8),Vector3(-2,0,0),Vector3(-7,0,0),Vector3(-19,0,0),Vector3(-23,0,0)]
const ISLAND_PATH = [Vector3(-23,0,0),Vector3(-26,0,0),Vector3(-31,0,0),Vector3(-35.4,0,0)]

var room_id = "terminal_room"
var travelling = false
var player: CharacterBody3D
var camera: Camera3D
var title_label: Label
var output_label: Label
var command_stack: VBoxContainer
var compact_command_header: HBoxContainer
var compact_command_actions: HBoxContainer
var compact_command_layout = false
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
var cast_model: RefCounted
var cast_rng := RandomNumberGenerator.new()
var demo_audio: Node
var demo_has_reading = false
var demo_last_reading: Dictionary = {}
var gate_reveal_active = false
var gate_reveal_done = false
var pond_view_active = false
var pond_return_button: Button
var touch_ui_enabled = false
var pavilion_overview_active = false
var architecture_overview_active = false
var hengwu_detail_action = ""
var tubi_overlook_active = false
var qiushuang_bank_action = ""
var yihong_detail_action = ""
var daguan_detail_active = false
const PORTRAIT_ARCHITECTURE_VIEWS = {
 "daoxiang_cun": [Vector3(-31.968402,1.9,-12.843443),Vector3(-31.968402,-.703797,-23)],
 "daguan_lou": [Vector3(7,6,-6.5),Vector3(.35,-3.25,-23),53.0],
 "longcui_an": [Vector3(-23.587955,1.65,5.246902),Vector3(-25,-.8,13.255)]}
const GATE_REVEAL_TARGET = Vector3(0,1.8,0)
const GATE_REVEAL_RAIL = [Vector3(-2.5,1.8,16.7),Vector3(-3,5.8,16),Vector3(10,5.5,12)]

func _ready() -> void:
 _configure_ui_scale(OS.has_feature("android") or OS.has_feature("ios"), DisplayServer.screen_get_dpi())
 var environment = load("res://garden_preview.tscn").instantiate()
 add_child(environment)
 preload("res://runtime/backdrop_wash.gd").configure(environment)
 var flora = preload("res://runtime/flora_lod.gd").new()
 flora.name = "FloraLOD"
 add_child(flora)
 flora.configure(environment)
 if demo_mode:
  var records = JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/demo-index.json"))
  assert(records is Dictionary and records.size() == 33, "Demo lightmap catalog is incomplete")
  var applied = preload("res://runtime/baked_materials.gd").apply_to_scene(environment, records)
  assert(applied == records.size(), "Demo lightmaps do not match the scene")
  var gate_stone = environment.find_child("SITE_rockery-gate_MAT_plaster_rock", true, false)
  assert(gate_stone is MeshInstance3D, "Demo gate stone is missing")
  for surface in range(gate_stone.mesh.get_surface_count()):
   gate_stone.get_surface_override_material(surface).set_shader_parameter("lightmap_scale", 1.8)
  for light in environment.find_children("*", "Light3D", true, false):
   light.shadow_enabled = false
 elif site_bakes_enabled:
  var records = JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
  assert(records is Dictionary and records.size() == 124, "Complete garden lightmaps are incomplete")
  var applied = preload("res://runtime/baked_materials.gd").apply_to_scene(environment, records)
  assert(applied == records.size(), "Complete garden lightmaps do not match the scene")
  for light in environment.find_children("*", "Light3D", true, false):
   if light is SpotLight3D or light is DirectionalLight3D:
    light.shadow_enabled = false
 if demo_mode or site_bakes_enabled:
  assert(preload("res://runtime/backdrop_wash.gd").apply_baked(environment)==preload("res://runtime/backdrop_wash.gd").receiver_names(environment).size(),"Incomplete native backdrop wash")
  assert(preload("res://runtime/terminal_spill.gd").apply_baked(environment)==7,"Incomplete native terminal indirect spill")
 hexagram_table=preload("res://runtime/hexagram_table.gd").new()
 hexagram_table.name="HexagramTable"
 add_child(hexagram_table)
 if not hexagram_table.configure(environment):push_error("Hexagram table is missing solid/broken line pairs")
 cast_model=preload("res://runtime/local_cast.gd").new()
 cast_rng.randomize()
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
 if not demo_mode:
  var reflection=preload("res://runtime/pond_reflection.gd").new()
  reflection.name="PondReflection"
  add_child(reflection)
  reflection.configure(environment,camera,player)
 _build_ui()
 if demo_mode:
  demo_audio = preload("res://runtime/demo_audio.gd").new()
  demo_audio.name = "DemoAudio"
  add_child(demo_audio)
 get_viewport().size_changed.connect(_on_viewport_resized)
 _arrive("terminal_room", true)

func _configure_ui_scale(mobile: bool, dpi: int) -> void:
 touch_ui_enabled = mobile
 var window = get_tree().root
 window.content_scale_size = Vector2i.ZERO
 window.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 # Scale the interface into density units; canvas_items retains native 3D pixels.
 window.content_scale_factor = clampf(float(dpi)/160.0,1.0,4.0) if mobile else 1.0
 if is_instance_valid(input):input.custom_minimum_size.y = 48 if mobile else 36
 if is_instance_valid(pond_return_button):pond_return_button.custom_minimum_size.y = 48 if mobile else 44
 if is_instance_valid(actions):
  for button in actions.get_children():button.custom_minimum_size.y = 48 if mobile else 38

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
 pond_return_button = Button.new()
 pond_return_button.text = "Return to ledge"
 pond_return_button.custom_minimum_size = Vector2(180,48 if touch_ui_enabled else 44)
 layer.add_child(pond_return_button)
 pond_return_button.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
 pond_return_button.pressed.connect(_finish_pond_view)
 pond_return_button.hide()
 var stack = VBoxContainer.new()
 command_stack = stack
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
 input.placeholder_text = "Optional: type look or help" if demo_mode else "Or type a command: look, help, exit…"
 input.custom_minimum_size.y = 48 if touch_ui_enabled else 36
 input.text_submitted.connect(func(text):
  input.clear()
  execute_command(text))
 stack.add_child(input)
 status = Label.new()
 status.position = Vector2(20,16)
 status.add_theme_font_size_override("font_size",15)
 status.add_theme_color_override("font_color",Color(.8,.9,.75))
 status.text = "GARDEN OF DREAMS · First reading" if demo_mode else "GARDEN OF DREAMS · Local scene exploration"
 layer.add_child(status)

func execute_command(text: String) -> void:
 var cmd = text.strip_edges().to_lower()
 if pond_view_active:
  if cmd in ["back","exit","look"]:_finish_pond_view()
  return
 if travelling:
  output_label.text = "You are on the path. The next room's actions will appear when you arrive."
  return
 if demo_mode and cmd not in _demo_commands():
  output_label.text = "This first reading follows the lanterns to the bronze table. Choose an action below."
  return
 match cmd:
  "look":
   if room_id=="qinfang_ting":_arrive(room_id)
   else:
    output_label.text = ROOMS[room_id].text
    if PORTRAIT_ARCHITECTURE_VIEWS.has(room_id) or room_id in ["hengwu_yuan","tubi_tang","qiushuang_zhai","yihong_yuan"]:_frame_arrival_camera(room_id)
  "help": output_label.text = "Choose an action below or type its command. Movement follows the garden paths; the camera moves with you."
  "terminal":
   output_label.text = "The screen invites you to enter the garden. Follow the lanterns to Qinfang Pavilion, then cast six lines at the bronze table." if demo_mode else ("The terminal is ready. Personal readings and history are not connected yet." if room_id == "terminal_room" else "Your personal terminal is in the cell.")
  "finish":
   if demo_mode and demo_has_reading and room_id == "qinfang_ting":_show_demo_finale()
  "replay":
   if demo_mode and demo_has_reading:_replay_demo()
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
    output_label.text="Six bronze lines run from bottom to top. Cast at the table for a local reading."
    var size=get_viewport().get_visible_rect().size
    camera.keep_aspect=Camera3D.KEEP_WIDTH if size.x<size.y else Camera3D.KEEP_HEIGHT
    camera.fov=55.0
    _camera_to(Vector3(0,2.45,1.15),Vector3(0,.55,0))
   else:output_label.text="The hexagram table is in 沁芳亭."
  "cast":
   if room_id=="qinfang_ting":_cast_at_table()
   else:output_label.text="The bronze table is in 沁芳亭."
  "water":
   if room_id == "qinfang_ting":
    output_label.text = "The stream passes under the bridge. Beyond the roofs, the painted moon hangs against the studio sky."
    camera.fov=55.0
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
    output_label.text = "The pond sits below the dry ledge. The window and roof reflect in dark water, broken by small moving ripples."
    _begin_pond_view()
   else: output_label.text = "The low pond lies beside the water-level hall."
  "nunnery":
   if room_id == "ouxiang_xie": _travel(NUNNERY_PATH,"longcui_an")
   else: output_label.text = "The nunnery approach starts at the water pavilion."
  "incense":
   if room_id == "longcui_an":
    output_label.text = "Three incense sticks stand in an open bronze bowl supported by three feet. The single lantern lights its rim."
    _camera_to(Vector3(-25.3,1.5,10.2),Vector3(-26.6,.5,11.75))
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
    _frame_yihong_detail("leaves")
   else: output_label.text = "The banana plants stand beside the red courtyard."
  "north":
   if room_id == "qinfang_ting": _travel(NORTH_PATH,"daguan_lou")
   else: output_label.text = "The north covered walk starts at Qinfang Pavilion."
  "doors":
   if room_id == "daguan_lou":
    output_label.text = "The ceremonial doors are closed. Bronze studs and paired pulls catch the warm light against red lacquer. This hall has no public interior."
    _frame_daguan_detail()
   elif room_id == "yihong_yuan":
    output_label.text = "The paired lacquer doors are closed. Bronze pulls sit above the stone threshold; this future room has no public interior."
    _frame_yihong_detail("doors")
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
    _frame_hengwu_detail("read")
   else: output_label.text = "The study table is in the herb courtyard."
  "rocks":
   if room_id == "hengwu_yuan":
    output_label.text = "Light passes through nine holes in three plaster stones. Low herbs leave their outlines exposed."
    _frame_hengwu_detail("rocks")
   else: output_label.text = "The perforated stones are in the study courtyard."
  "overlook":
   if room_id == "tubi_tang":
    output_label.text = "The bridge pavilion lies below. Beyond the roofs, the painted cyclorama closes the garden."
    _frame_tubi_overlook()
   else: output_label.text = "The overlook is on the hilltop terrace."
  "left", "centre", "right":
   if room_id == "qiushuang_zhai":
    output_label.text = "The " + cmd + " bank has four amber monitors. Live bulletin content is not connected yet."
    _frame_qiushuang_bank(cmd)
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

func _cast_at_table() -> void:
 var reading=cast_model.cast(cast_rng)
 if reading.is_empty() or not hexagram_table.set_lines(reading.primary_lines):
  output_label.text="The local cast could not be shown. Try again."
  return
 if demo_mode:
  demo_has_reading = true
  demo_last_reading = reading
  demo_audio.cast()
 var size=get_viewport().get_visible_rect().size
 camera.keep_aspect=Camera3D.KEEP_WIDTH if size.x<size.y else Camera3D.KEEP_HEIGHT
 camera.fov=55.0
 _camera_to(Vector3(0,2.45,1.15),Vector3(0,.55,0))
 output_label.text="The bronze lines now show #%d · %s. This is a local cast."%[reading.primary.number,reading.primary.meaning]
 var card:CanvasLayer
 if has_node("ReadingResult"):
  card=get_node("ReadingResult")
  card.show_result(reading)
 else:
  card=preload("res://runtime/reading_result.gd").new()
  card.name="ReadingResult"
  card.touch_ui_enabled=touch_ui_enabled
  card.result=reading
  card.recast_requested.connect(_cast_at_table)
  input.editable=false
  for button in actions.get_children():button.disabled=true
  card.tree_exiting.connect(func():
   input.editable=not travelling
   if demo_mode:_refresh_actions()
   for button in actions.get_children():button.disabled=travelling)
  add_child(card)

func _travel(points: Array, target_room: String) -> void:
 pavilion_overview_active=false
 _clear_pond_view()
 if demo_mode and room_id == "rockery_gate" and target_room == "qinfang_ting":demo_audio.start_tunnel()
 camera.keep_aspect = Camera3D.KEEP_HEIGHT
 camera.fov = 55.0
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
 if demo_mode:demo_audio.reveal()
 gate_reveal_active = true
 gate_reveal_done = true
 command_panel.hide()
 player.velocity.x = 0
 player.velocity.z = 0
 if camera_tween and camera_tween.is_valid(): camera_tween.kill()
 var final_view=_pavilion_camera_view()
 camera.keep_aspect=Camera3D.KEEP_HEIGHT
 camera.fov=55.0
 status.text="THE GARDEN · 沁芳亭"
 output_label.text="The passage opens onto the stream. Beyond the covered walks, the pavilion stands in green light."
 camera_tween=create_tween()
 for i in range(GATE_REVEAL_RAIL.size()):
  var endpoint=final_view[0] if i==GATE_REVEAL_RAIL.size()-1 else GATE_REVEAL_RAIL[i]
  var pose=Transform3D(Basis.IDENTITY,endpoint).looking_at(GATE_REVEAL_TARGET,Vector3.UP)
  camera_tween.tween_property(camera,"transform",pose,[.8,.8,1.8][i]).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
  if i==GATE_REVEAL_RAIL.size()-1:
   camera_tween.parallel().tween_property(camera,"fov",final_view[2],1.8).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
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

func _reflection_view(pond = false) -> Array:
 var portrait = get_viewport().get_visible_rect().size.x < get_viewport().get_visible_rect().size.y
 var name_pattern = "CAM_aojing-guan_portrait*" if portrait else "CAM_aojing-guan_wide*"
 var authored = find_child(name_pattern,true,false) as Camera3D
 if pond:
  var candidates = find_children("CAM_aojing-guan_reflection*","Camera3D",true,false).filter(func(candidate):return ("portrait" in str(candidate.name))==portrait)
  assert(candidates.size()==1,"The pond shot must have one authored camera per aspect")
  authored = candidates[0]
 assert(authored != null,"The reflection hall's authored camera is missing")
 var fov = authored.fov
 if portrait:
  var viewport = authored.get_meta("extras")["runtime_camera_viewport"]
  fov = rad_to_deg(2 * atan(tan(deg_to_rad(fov) / 2) * float(viewport[0]) / float(viewport[1])))
 return [authored.global_position,authored.global_position-authored.global_basis.z*10,fov]

func _begin_pond_view(immediate = false) -> void:
 pond_view_active = true
 command_panel.hide()
 input.editable = false
 pond_return_button.show()
 status.text = "凹晶館 · Pond reflection"
 _position_pond_return_button()
 var view = _reflection_view(true)
 var size = get_viewport().get_visible_rect().size
 camera.keep_aspect = Camera3D.KEEP_WIDTH if size.x<size.y else Camera3D.KEEP_HEIGHT
 camera.fov = view[2]
 _camera_to(view[0],view[1],immediate)
 pond_return_button.grab_focus()

func _position_pond_return_button() -> void:
 var size = get_viewport().get_visible_rect().size
 var top = 56.0 if size.x<size.y else 16.0
 pond_return_button.offset_left = -204
 pond_return_button.offset_right = -24
 pond_return_button.offset_top = top
 pond_return_button.offset_bottom = top+44

func _clear_pond_view() -> void:
 pond_view_active = false
 if is_instance_valid(pond_return_button):pond_return_button.hide()

func _finish_pond_view() -> void:
 if not pond_view_active:return
 _clear_pond_view()
 _arrive("aojing_guan")
 if actions.get_child_count()>0:actions.get_child(0).grab_focus()

func _unhandled_key_input(event: InputEvent) -> void:
 if pond_view_active and event is InputEventKey and event.pressed and not event.echo and event.keycode==KEY_ESCAPE:
  _finish_pond_view()
  get_viewport().set_input_as_handled()

func _on_viewport_resized() -> void:
 call_deferred("_fit_action_list")
 if pond_view_active:call_deferred("_refresh_pond_view")
 elif daguan_detail_active and not travelling:call_deferred("_refresh_daguan_detail")
 elif yihong_detail_action!="" and not travelling:call_deferred("_refresh_yihong_detail")
 elif qiushuang_bank_action!="" and not travelling:call_deferred("_refresh_qiushuang_bank")
 elif tubi_overlook_active and not travelling:call_deferred("_refresh_tubi_overlook")
 elif hengwu_detail_action!="" and not travelling:call_deferred("_refresh_hengwu_detail")
 elif pavilion_overview_active and not travelling:call_deferred("_refresh_pavilion_overview")
 elif architecture_overview_active and not travelling:call_deferred("_refresh_architecture_overview")

func _refresh_daguan_detail() -> void:
 if daguan_detail_active and room_id=="daguan_lou" and not travelling:_frame_daguan_detail(true)

func _frame_daguan_detail(immediate = false) -> void:
 var portrait=get_viewport().get_visible_rect().size.x<get_viewport().get_visible_rect().size.y
 camera.keep_aspect=Camera3D.KEEP_WIDTH if portrait else Camera3D.KEEP_HEIGHT
 camera.fov=55.0
 _camera_to(Vector3(0,1.7,-19.8),Vector3(0,1.7,-23),immediate)
 daguan_detail_active=true

func _refresh_yihong_detail() -> void:
 if yihong_detail_action!="" and room_id=="yihong_yuan" and not travelling:_frame_yihong_detail(yihong_detail_action,true)

func _frame_yihong_detail(action: String, immediate = false) -> void:
 var size=get_viewport().get_visible_rect().size
 var portrait=size.x<size.y
 var position=Vector3(22.2,1.65,1) if action=="doors" else Vector3(21.5,2.3,.5)
 var target=Vector3(25,1.4,1) if action=="doors" else Vector3(23.65,1.7,-1.45)
 camera.keep_aspect=Camera3D.KEEP_WIDTH if portrait else Camera3D.KEEP_HEIGHT
 camera.fov=55.0
 if portrait:
  if action=="doors":
   camera.fov=58.0
   target=Vector3(25,-.1,1)
   if size.y<size.x*2.05:
    position=Vector3(21.8,1.65,1)
    target=Vector3(25,.05,1)
  else:
   position=Vector3(19.35,2.9,2.45)
   target=Vector3(23.65,-.8,-1.45)
 _camera_to(position,target,immediate)
 yihong_detail_action=action

func _refresh_hengwu_detail() -> void:
 if hengwu_detail_action!="" and room_id=="hengwu_yuan" and not travelling:_frame_hengwu_detail(hengwu_detail_action,true)

func _frame_hengwu_detail(action: String, immediate = false) -> void:
 var size=get_viewport().get_visible_rect().size
 var portrait=size.x<size.y
 var position=Vector3(-18,1.8,-13.4) if action=="read" else Vector3(-15.6,1.6,-10.6)
 var target=Vector3(-20,.85,-14.7) if action=="read" else Vector3(-15.4,1.35,-12.5)
 camera.keep_aspect=Camera3D.KEEP_WIDTH if portrait else Camera3D.KEEP_HEIGHT
 camera.fov=55.0
 if portrait:
  if action=="read":target=Vector3(-20,-.35,-14.7)
  else:
   # Stay inside the court wall; widening the view keeps all three holes above the panel.
   position=Vector3(-15.62,1.625,-10.41)
   target=Vector3(-15.4,-.15,-12.5)
   # Shorter portrait viewports need extra clearance below the status line.
   camera.fov=95.0 if size.y<size.x*1.9 else 90.0
 _camera_to(position,target,immediate)
 hengwu_detail_action=action

func _refresh_architecture_overview() -> void:
 if architecture_overview_active and not travelling:_frame_arrival_camera(room_id,true)

func _refresh_qiushuang_bank() -> void:
 if qiushuang_bank_action!="" and room_id=="qiushuang_zhai" and not travelling:_frame_qiushuang_bank(qiushuang_bank_action,true)

func _frame_qiushuang_bank(action: String, immediate = false) -> void:
 var portrait=get_viewport().get_visible_rect().size.x<get_viewport().get_visible_rect().size.y
 var x:float={"left":18.85,"centre":22.0,"right":25.15}[action]
 camera.keep_aspect=Camera3D.KEEP_WIDTH if portrait else Camera3D.KEEP_HEIGHT
 camera.fov=40.0 if portrait else 55.0
 _camera_to(Vector3(x,1.7,-12.7),Vector3(x,.75 if portrait else 1.35,-15.6),immediate)
 qiushuang_bank_action=action

func _refresh_tubi_overlook() -> void:
 if tubi_overlook_active and room_id=="tubi_tang" and not travelling:_frame_tubi_overlook(true)

func _frame_tubi_overlook(immediate = false) -> void:
 var portrait=get_viewport().get_visible_rect().size.x<get_viewport().get_visible_rect().size.y
 camera.keep_aspect=Camera3D.KEEP_WIDTH if portrait else Camera3D.KEEP_HEIGHT
 camera.fov=45.0 if portrait else 55.0
 _camera_to(Vector3(7,12,-30.5),Vector3(0,-1 if portrait else 1.2,0),immediate)
 tubi_overlook_active=true

func _tubi_portrait_view(size: Vector2) -> Array:
 # The shorter view reserves extra space for the title, description and touch list.
 var short=size.y<size.x*2.14
 var narrow=size.x<380.0
 var fov=60.0 if short else (50.0 if narrow else 45.0)
 var target=Vector3(3,-9.1 if narrow else -7.1,-32) if short else Vector3(5,-7.1 if narrow else -5.1,-32)
 return [Vector3(16,6,-12),target,fov]

func _hengwu_overview_view(size: Vector2) -> Array:
 # Keep the book and pierced stones in view from a low position inside the court.
 var portrait=size.x<size.y
 if portrait:
  var short=size.y<size.x*2.14
  var narrow=size.x<380.0
  var target_y=-5.8 if short else (-4.5 if narrow else -4.0)
  var fov=128.0 if short else (118.0 if narrow else 115.0)
  return [Vector3(-19.5,1.8,-17),Vector3(-19,target_y,-12.5),fov]
 if size.x<820.0 and size.y<580.0:
  return [Vector3(-19.5,1.8,-17),Vector3(-19,-6.4 if touch_ui_enabled else -4.5,-12.5),143.0 if touch_ui_enabled else 134.0]
 if size.y<390.0:
  return [Vector3(-19.5,1.8,-17),Vector3(-19,-3.5,-12.5),128.0]
 var short=size.y<580.0
 var target_y=(-3.0 if touch_ui_enabled else -2.8) if short else (-2.8 if touch_ui_enabled else -2.3)
 return [Vector3(-19.5,1.8,-17),Vector3(-19,target_y,-12.5),118.0 if short else 115.0]

func _pavilion_camera_view() -> Array:
 var size=get_viewport().get_visible_rect().size
 # The portrait pose keeps the physical moon and title board inside the scene.
 if size.x<size.y:return [Vector3(6,6.98,20),GATE_REVEAL_TARGET,50.0]
 return [GATE_REVEAL_RAIL[-1],GATE_REVEAL_TARGET,55.0]

func _refresh_pavilion_overview() -> void:
 if not pavilion_overview_active or travelling:return
 var view=_pavilion_camera_view()
 camera.keep_aspect=Camera3D.KEEP_HEIGHT
 camera.fov=view[2]
 _camera_to(view[0],view[1],true)
 pavilion_overview_active=true

func _refresh_pond_view() -> void:
 if pond_view_active:_begin_pond_view(true)

func _arrive(id: String, immediate = false) -> void:
 _clear_pond_view()
 gate_reveal_active = false
 command_panel.show()
 room_id = id
 title_label.text = ROOMS[id].title
 output_label.text = _demo_room_text(id) if demo_mode else ROOMS[id].text
 status.text = "GARDEN OF DREAMS · First reading" if demo_mode else "GARDEN OF DREAMS · Local scene exploration"
 input.editable = true
 if demo_mode:demo_audio.enter_room(id)
 _refresh_actions()
 _frame_arrival_camera(id,immediate)
 transition_finished.emit(id)

func _frame_arrival_camera(id: String, immediate = false) -> void:
 var views = {
  "daoxiang_cun": [Vector3(-34,3.4,-13),Vector3(-34,1.7,-22)],
  "aojing_guan": _reflection_view(),
  "longcui_an": [Vector3(-22,2.6,6),Vector3(-25,1.45,12.2)],
  "xiaoxiang_guan": [Vector3(-2,2.3,13),Vector3(-8.8,1.6,12.5)],
  "yihong_yuan": [Vector3(18,3.1,5),Vector3(24.3,1.25,1)],
  "daguan_lou": [Vector3(5.5,2.5,-13),Vector3(0,2.7,-23)],
  "hengwu_yuan": [Vector3(-17.5,2.6,-10.5),Vector3(-18,1.1,-15.2)],
  "tubi_tang": [Vector3(16,10,-20),Vector3(7,4.9,-32)],
  "qiushuang_zhai": [Vector3(22,3.2,-6.8),Vector3(22,1.45,-15.5)],
  "terminal_room": [Vector3(-1.3,1.6,38.7),Vector3(-1.3,1.1,36.5)],
  "rockery_gate": [Vector3(0,1.85,35.7),Vector3(0,1.9,29)],
  "qinfang_ting": [Vector3(10,5.5,12),Vector3(0,1.8,0)],
  "ouxiang_xie": [Vector3(-15,5,10),Vector3(-23,1.8,0)],
  "ziling_zhou": [Vector3(-40,1.4,10),Vector3(-32,-1.25,0)]}
 var view_position: Vector3 = views[id][0]
 var view_target: Vector3 = views[id][1]
 var viewport_size = get_viewport().get_visible_rect().size
 var portrait = viewport_size.x < viewport_size.y
 camera.fov = views[id][2] if id == "aojing_guan" else 55.0
 camera.keep_aspect = Camera3D.KEEP_WIDTH if portrait and id in ["rockery_gate","qiushuang_zhai","hengwu_yuan","daguan_lou","yihong_yuan","xiaoxiang_guan","longcui_an","aojing_guan","daoxiang_cun","tubi_tang","ziling_zhou"] else Camera3D.KEEP_HEIGHT
 if id=="qinfang_ting":
  var pavilion_view=_pavilion_camera_view()
  view_position=pavilion_view[0]
  view_target=pavilion_view[1]
  camera.fov=pavilion_view[2]
 elif id=="hengwu_yuan":
  var court_view=_hengwu_overview_view(viewport_size)
  view_position=court_view[0]
  view_target=court_view[1]
  camera.fov=court_view[2]
 elif portrait and id=="ouxiang_xie":
  view_target=Vector3(-23,.5,0)
  view_position=view_target+(view_position-view_target)*2.0
 elif portrait and id=="ziling_zhou":
  # Keep the complete footbridge and distant pavilion roof above the controls.
  view_position=Vector3(-41,3.2,4)
  view_target=Vector3(-33,-5,0)
  camera.fov=70.0
 elif not portrait and id=="ziling_zhou":
  # Move back smoothly as landscape controls occupy more of the view.
  var short_view=clampf((600.0-viewport_size.y)/190.0,0.0,1.0)
  view_position=Vector3(-40,1.4,10).lerp(Vector3(-42,1.4,16),short_view)
  view_target=Vector3(-32,-1.25,0).lerp(Vector3(-32,-3.25,0),short_view)
 elif portrait and id=="yihong_yuan":
  view_position=Vector3(16.8,3.45,5.75)
  view_target=Vector3(24.3,-2.4,1)
  camera.fov=62.0
 elif portrait and id=="qiushuang_zhai":
  view_position=Vector3(22,3.2,-4.8)
  view_target=Vector3(22,-5,-15.5)
  camera.fov=80.0
 elif portrait and id=="tubi_tang":
  var hilltop_view=_tubi_portrait_view(viewport_size)
  view_position=hilltop_view[0]
  view_target=hilltop_view[1]
  camera.fov=hilltop_view[2]
 elif portrait and PORTRAIT_ARCHITECTURE_VIEWS.has(id):
  view_position=PORTRAIT_ARCHITECTURE_VIEWS[id][0]
  view_target=PORTRAIT_ARCHITECTURE_VIEWS[id][1]
  if PORTRAIT_ARCHITECTURE_VIEWS[id].size()>2:camera.fov=PORTRAIT_ARCHITECTURE_VIEWS[id][2]
  if id=="daguan_lou" and touch_ui_enabled:
   view_target=Vector3(.35,-4.05,-23)
   camera.fov=54.0
 elif portrait and id not in ["terminal_room","rockery_gate","qiushuang_zhai","xiaoxiang_guan","hengwu_yuan","aojing_guan"]:
  view_position = view_target + (view_position - view_target) * 1.4
 _camera_to(view_position,view_target,immediate)
 pavilion_overview_active=id=="qinfang_ting"
 architecture_overview_active=PORTRAIT_ARCHITECTURE_VIEWS.has(id) or id in ["tubi_tang","qiushuang_zhai","ziling_zhou","yihong_yuan","hengwu_yuan"]

func _refresh_actions() -> void:
 for button in actions.get_children():
  actions.remove_child(button)
  button.queue_free()
 var menu = _demo_actions() if demo_mode else ROOMS[room_id].actions
 for action in menu:
  var button = Button.new()
  button.text = action[0]
  button.custom_minimum_size = Vector2(140,48 if touch_ui_enabled else 38)
  button.pressed.connect(execute_command.bind(action[1]))
  actions.add_child(button)
 call_deferred("_fit_action_list")

func _demo_actions() -> Array:
 match room_id:
  "terminal_room":return [["Read the terminal", "terminal"], ["Enter the garden", "exit"]]
  "rockery_gate":return [["Follow the lanterns", "enter"], ["Return to your cell", "back"]]
  "qinfang_ting":
   if demo_has_reading:return [["Cast again", "cast"], ["Finish the demo", "finish"], ["Return to the gate", "back"]]
   return [["Examine the table", "table"], ["Cast at the table", "cast"], ["Return to the gate", "back"]]
 return []

func _demo_commands() -> Array[String]:
 var allowed: Array[String] = ["look", "help"]
 for action in _demo_actions():allowed.append(action[1])
 if room_id == "rockery_gate":allowed.append("continue")
 return allowed

func _demo_room_text(id: String) -> String:
 match id:
  "terminal_room":return "A green screen lights the cell. It invites you to follow the lanterns to Qinfang Pavilion for a first reading."
  "rockery_gate":return "The lantern-lit passage bends toward the pavilion. Follow the lights to the bronze table."
  "qinfang_ting":
   return "Your six bronze lines remain on the table. Finish this visit or cast again." if demo_has_reading else "The stream opens beneath six lanterns. The bronze table is ready for your first local cast."
 return ROOMS[id].text

func _show_demo_finale() -> void:
 if has_node("DemoFinale"):return
 var finale = preload("res://runtime/demo_finale.gd").new()
 finale.name = "DemoFinale"
 finale.touch_ui_enabled = touch_ui_enabled
 finale.reading = demo_last_reading
 finale.replay_requested.connect(_replay_demo)
 finale.tree_exiting.connect(func():
  input.editable = true
  for button in actions.get_children():button.disabled = false)
 input.editable = false
 for button in actions.get_children():button.disabled = true
 add_child(finale)

func _replay_demo() -> void:
 if has_node("DemoFinale"):get_node("DemoFinale").queue_free()
 if has_node("ReadingResult"):get_node("ReadingResult").queue_free()
 demo_has_reading = false
 demo_last_reading.clear()
 hexagram_table.set_lines([1, 1, 1, 1, 1, 1])
 player.position = CELL_PATH[0] + Vector3(0, .03, 0)
 player.velocity = Vector3.ZERO
 travelling = false
 _arrive("terminal_room", true)

func _set_compact_command_layout(enabled: bool) -> void:
 # Let the compact rows set the panel height; restore the ordinary reserve on exit.
 command_panel.offset_top=-1 if enabled else -195
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
 # Share narrow landscape header width so neither text forces a tall panel.
 var narrow_header=enabled and get_viewport().get_visible_rect().size.x<820.0
 title_label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART if narrow_header else TextServer.AUTOWRAP_OFF
 title_label.size_flags_horizontal=Control.SIZE_EXPAND_FILL if narrow_header else Control.SIZE_FILL
 title_label.size_flags_stretch_ratio=1.0
 output_label.size_flags_stretch_ratio=2.0 if narrow_header else 1.0
 # Prevent wrapping in the compact row; every existing action remains reachable
 # by horizontal scrolling, beside the unchanged command entry field.
 var action_width=0.0
 if enabled:
  for button in actions.get_children():action_width+=button.get_combined_minimum_size().x
  action_width+=maxi(0,actions.get_child_count()-1)*actions.get_theme_constant("h_separation")
 actions.custom_minimum_size.x=action_width
 action_scroll.scroll_horizontal=0

func _fit_action_list() -> void:
 await get_tree().process_frame
 var portrait = get_viewport().get_visible_rect().size.x < get_viewport().get_visible_rect().size.y
 _set_compact_command_layout(not portrait and room_id=="hengwu_yuan" and get_viewport().get_visible_rect().size.y<580.0)
 # Reparenting changes the row width; discard the previous wrapped height first.
 if compact_command_layout:
  action_scroll.custom_minimum_size.y=0
  await get_tree().process_frame
 var action_height=actions.get_combined_minimum_size().y
 if portrait and room_id in ["qinfang_ting","ouxiang_xie","hengwu_yuan","tubi_tang","qiushuang_zhai","yihong_yuan"]:
  # Fixed reserves keep scrollbar wrapping from changing the camera clearance.
  action_height=128.0 if room_id in ["tubi_tang","qiushuang_zhai","yihong_yuan"] else minf(action_height,128.0 if room_id in ["ouxiang_xie","hengwu_yuan"] else 152.0)
 action_scroll.custom_minimum_size.y=action_height
 action_scroll.scroll_vertical = 0

func _camera_to(position: Vector3, target: Vector3, immediate = false) -> void:
 pavilion_overview_active=false
 architecture_overview_active=false
 hengwu_detail_action=""
 tubi_overlook_active=false
 qiushuang_bank_action=""
 yihong_detail_action=""
 daguan_detail_active=false
 if camera_tween and camera_tween.is_valid(): camera_tween.kill()
 var transform_target = Transform3D(camera.basis,position).looking_at(target,Vector3.UP)
 if immediate:
  camera.transform = transform_target
 else:
  camera_tween = create_tween()
  camera_tween.tween_property(camera,"transform",transform_target,1.4).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
