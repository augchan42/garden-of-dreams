extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var garden=load("res://garden_preview.tscn").instantiate();root.add_child(garden)
 # Import alone must expose six solid lines, without overlapping broken halves.
 var imported_visible=0
 for mesh in garden.find_children("HERO_table_line_*","MeshInstance3D",true,false):
  if mesh.visible:imported_visible+=1
 if imported_visible!=6:
  push_error("Import did not preserve the six-line default");quit(1);return
 var controller=load("res://runtime/hexagram_table.gd").new();root.add_child(controller)
 if not controller.configure(garden):
  push_error("Missing or duplicate line variants");quit(1);return
 for pattern in range(64):
  var lines=[]
  for i in range(6):lines.append((pattern>>i)&1)
  if not controller.set_lines(lines):
   push_error("Valid pattern rejected");quit(1);return
  for i in range(6):
   var pair=controller.slots[i]
   if pair.solid.visible!=(lines[i]==1) or pair.broken.visible!=(lines[i]==0):
    push_error("Wrong visible variant or bottom-to-top order");quit(1);return
 var before=controller.current_lines.duplicate()
 for invalid in [[],[0,1],[0,0,0,0,0,2],[0,0,0,0,0,"1"],[0,0,0,0,0,1.0]]:
  if controller.set_lines(invalid) or controller.current_lines!=before:
   push_error("Invalid pattern mutated the table");quit(1);return
  for pair in controller.slots:
   if not pair.solid.visible or pair.broken.visible:
    push_error("Invalid pattern changed a visible slot");quit(1);return
 print("HEXAGRAM_TABLE_PASS: import default, all 64 patterns, bottom-to-top slots and atomic rejection of invalid input")
 quit(0)
