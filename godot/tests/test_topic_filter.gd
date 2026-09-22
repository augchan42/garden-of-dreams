extends SceneTree
func _initialize() -> void:
 var browser=preload("res://runtime/topic_browser.gd").new()
 browser.selection=OptionButton.new()
 browser.body=RichTextLabel.new()
 browser.status=Label.new()
 browser.refresh=Button.new()
 for child in [browser.selection,browser.body,browser.status,browser.refresh]:browser.add_child(child)
 browser.category_filter="temporal"
 var fixture={"ok":true,"topics":[{"title":"Ongoing","category":"timeless","description":"General"},{"title":"Current","category":"temporal","description":"Event"}]}
 browser._received(fixture)
 assert(browser.topics.size()==1 and browser.topics[0].title=="Current")
 assert("Current event" in browser.body.text)
 browser._received({"ok":false,"error":"Offline"})
 assert(browser.topics.size()==1 and "Previously loaded" in browser.status.text)
 browser._received({"ok":true,"topics":[fixture.topics[0]]})
 assert(browser.topics.is_empty() and browser.selection.disabled)
 assert("No active English current-event" in browser.body.text)
 browser.category_filter=""
 browser._received(fixture)
 assert(browser.topics.size()==2)
 browser.category_filter="timeless"
 browser._received(fixture)
 assert(browser.topics.size()==1 and browser.topics[0].title=="Ongoing")
 browser.free()
 print("TOPIC_FILTER_PASS: temporal-only, empty state, stale data and unfiltered pavilion")
 quit(0)
