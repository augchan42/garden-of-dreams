extends SceneTree

class ControlProducer extends "res://tests/profile_android_full.gd":
 var published = false
 func save_report() -> void:
  published = true

func _initialize() -> void:
 for event in [Node.NOTIFICATION_APPLICATION_PAUSED, Node.NOTIFICATION_APPLICATION_FOCUS_OUT]:
  var producer = ControlProducer.new()
  producer.report = {"status": "running"}
  producer.phase = "control-active-phase"
  producer.notification(event)
  if producer.report.status != "failed" or not producer.published or not producer.phase.is_empty():
   producer.free()
   push_error("Interrupted actual producer still permits a sustained run")
   quit(1)
   return
  producer.free()
 var complete = ControlProducer.new()
 complete.report = {"status": "complete"}
 complete.notification(Node.NOTIFICATION_APPLICATION_PAUSED)
 var unchanged = complete.report.status == "complete" and not complete.published
 complete.free()
 if not unchanged:
  push_error("Completed report was changed by later app pause")
  quit(1)
  return
 print("FULL_PRODUCER_PAUSE_AND_FOCUS_REJECTION_PASS expected_rejections=2")
 quit(0)
