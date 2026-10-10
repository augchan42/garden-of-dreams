extends SceneTree

func _initialize() -> void:
 var producer = load("res://tests/profile_android_full.gd")
 if not producer.has_method("needs_another_tour"):
  push_error("Full producer minimum-two-tour predicate is missing")
  quit(1)
  return
 if not producer.needs_another_tour(0, 900000000) or not producer.needs_another_tour(1, 900000000) or not producer.needs_another_tour(2, 599999999) or producer.needs_another_tour(2, 600000000):
  push_error("Full producer must require both two tours and600timedseconds")
  quit(1)
  return
 print("FULL_PRODUCER_TWO_TOURS_AND_TIMED_MINIMUM_PASS")
 quit(0)
