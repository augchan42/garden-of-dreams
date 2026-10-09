extends "res://tests/test_full_garden_traversal.gd"

# Test-only collision counterfactual. These boxes are not production geometry.
# The inherited strict tour still moves one visitor through the original paths.
var omit_group = ""

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--omit="):omit_group = arg.trim_prefix("--omit=")
 root.child_entered_tree.connect(_add_candidate_seams)
 call_deferred("run")

func _add_candidate_seams(node: Node) -> void:
 if not node is Node3D or node.scene_file_path != "res://runtime/entry_route.tscn":return
 var seam_file = "res://tests/floor-seam-candidate.json"
 var proposal = JSON.parse_string(FileAccess.get_file_as_string(seam_file))
 assert(proposal.status == "proposal_only")
 report.scope = "Test-only narrow floor collision inserts with the unchanged production route, source and strict continuous tour. Not adopted geometry, visual, lighting, performance or production traversal acceptance."
 report.collision_counterfactual = true
 report.proposal_sha256 = FileAccess.get_sha256(seam_file)
 report.candidate_test_sha256 = FileAccess.get_sha256("res://tests/test_floor_seam_candidate.gd")
 report.omitted_group = omit_group
 report.candidate_seams = []
 for seam in proposal.seams:
  if seam.group == omit_group:continue
  var body = StaticBody3D.new()
  body.name = "TestOnly_" + seam.name
  var collision = CollisionShape3D.new()
  var box = BoxShape3D.new()
  box.size = Vector3(seam.size_godot[0], seam.size_godot[1], seam.size_godot[2])
  collision.shape = box
  body.add_child(collision)
  body.position = Vector3(seam.position_godot[0], seam.position_godot[1], seam.position_godot[2])
  node.add_child(body)
  report.candidate_seams.append(seam)
