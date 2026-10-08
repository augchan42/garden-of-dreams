extends Node
## Six line values, bottom to top: 0 = broken/yin, 1 = solid/yang.
## The default is an authored display; a live reading source is not connected.
var slots: Array = []
var current_lines: Array[int] = [1,1,1,1,1,1]
var configured = false

func configure(garden: Node) -> bool:
 var found: Array = [{},{},{},{},{},{}]
 var pattern=RegEx.new()
 pattern.compile("^HERO_table_line_([1-6])_(solid|broken)(?:_|$)")
 for mesh in garden.find_children("HERO_table_line_*","MeshInstance3D",true,false):
  var match_result=pattern.search(str(mesh.name))
  if match_result==null:continue
  var index=int(match_result.get_string(1))-1
  var variant=match_result.get_string(2)
  if found[index].has(variant):return false
  found[index][variant]=mesh
 for pair in found:
  if not pair.has("solid") or not pair.has("broken"):return false
 slots=found
 configured=true
 return set_lines(current_lines)

func set_lines(lines: Array) -> bool:
 if not configured or lines.size()!=6:return false
 for value in lines:
  if typeof(value)!=TYPE_INT or (value!=0 and value!=1):return false
 # Validate the entire request before changing any visible slot.
 current_lines.assign(lines)
 for i in range(6):
  slots[i].solid.visible=current_lines[i]==1
  slots[i].broken.visible=current_lines[i]==0
 return true
