extends Node
signal finished(result:Dictionary)
const ENDPOINT="https://app.8bitoracle.ai/api/group-divination/topics?locale=en"
var request:HTTPRequest

func fetch() -> void:
 if request:return
 request=HTTPRequest.new()
 request.timeout=12.0
 request.body_size_limit=2_000_000
 add_child(request)
 request.request_completed.connect(_completed)
 var error=request.request(ENDPOINT)
 if error!=OK:call_deferred("_finish",{"ok":false,"error":"Could not start the connection. Please retry."})

func _completed(result:int,code:int,_headers:PackedStringArray,body:PackedByteArray) -> void:
 if result!=HTTPRequest.RESULT_SUCCESS:
  _finish({"ok":false,"error":"The topics service could not be reached. Please retry."})
 elif code!=200:
  _finish({"ok":false,"error":"The topics service returned HTTP %d. Please retry." % code})
 else:
  _finish(parse_payload(JSON.parse_string(body.get_string_from_utf8())))

func _finish(result:Dictionary) -> void:
 if request:
  request.queue_free()
  request=null
 finished.emit(result)

static func parse_payload(value:Variant) -> Dictionary:
 var invalid={"ok":false,"error":"The topics service returned an unexpected response."}
 if not value is Dictionary:return invalid
 var topics:Array=[]
 for category in ["timeless","temporal"]:
  if not value.get(category) is Array:return invalid
  if value[category].size()>100:return invalid
  for topic in value[category]:
   if not topic is Dictionary:return invalid
   if not topic.get("id") is String or not topic.get("title") is String:return invalid
   if not topic.get("is_active") is bool or not topic.get("locale") is String:return invalid
   var description=topic.get("description","")
   if description==null:description=""
   if not description is String:return invalid
   if not topic.is_active or topic.locale!="en":continue
   topics.append({"id":topic.id,"title":topic.title.left(240),"description":description.left(8000),"category":category})
 return {"ok":true,"topics":topics}
