extends SceneTree
func _initialize() -> void:
 if not ResourceLoader.exists("res://services/topics.gd"):
  push_error("Topics service missing")
  quit(1)
  return
 var service=load("res://services/topics.gd")
 var good={"timeless":[{"id":"t1","title":"A question","description":"A description","locale":"en","is_active":true}],"temporal":[]}
 var result=service.parse_payload(good)
 assert(result.ok and result.topics.size()==1)
 assert(result.topics[0].category=="timeless")
 for bad in [null,[],{}, {"timeless":"bad","temporal":[]},{"timeless":[{"id":1}],"temporal":[]}]:
  assert(not service.parse_payload(bad).ok)
 good.timeless[0].is_active=false
 assert(service.parse_payload(good).topics.is_empty())
 good.timeless[0].is_active=true
 good.timeless[0].locale="zh"
 assert(service.parse_payload(good).topics.is_empty())
 print("TOPICS_SCHEMA_PASS")
 quit(0)
