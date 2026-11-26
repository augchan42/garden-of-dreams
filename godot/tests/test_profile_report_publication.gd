extends SceneTree

# Read the real profiler's public file while a worker publishes large reports.
# The profiler is kept outside the tree so its Android-only run does not start.
func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var output=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 if not str(ProjectSettings.get_setting("application/config/name")).begins_with("Garden Report Publication Regression "):
  push_error("Run only in an isolated publication fixture")
  quit(1)
  return
 var host=load("res://tests/profile_android.gd").new()
 var payload="painted-moon-".repeat(131072)
 host.report={"generation":0,"payload":payload}
 host.save_report()
 var thread=Thread.new()
 assert(thread.start(func():
  for generation in range(1,33):
   host.report={"generation":generation,"payload":payload}
   host.save_report()
 )==OK)
 var reads=0
 var invalid=0
 var errors=[]
 var started=Time.get_ticks_msec()
 while thread.is_alive():
  var raw=FileAccess.get_file_as_string("user://garden-phone-profile.json")
  var parser=JSON.new()
  if parser.parse(raw)!=OK:invalid+=1
  elif not parser.data is Dictionary or parser.data.get("payload")!=payload:invalid+=1
  reads+=1
  OS.delay_usec(100)
 thread.wait_to_finish()
 var final=JSON.parse_string(FileAccess.get_file_as_string("user://garden-phone-profile.json"))
 if reads==0:errors.append("No concurrent reads were made")
 if invalid!=0:errors.append("Reader observed incomplete JSON publications")
 if not final is Dictionary or final.get("generation")!=32 or final.get("payload")!=payload:errors.append("Final report differs from producer")
 host.free()
 var record={"status":"passed" if errors.is_empty() else "failed","concurrent_reads":reads,"incomplete_publications":invalid,"generations":32,"user_data_dir":OS.get_user_data_dir(),"wall_ms":Time.get_ticks_msec()-started,"errors":errors,"scope":"Actual dedicated profiler save_report producer versus concurrent complete-file JSON reader; isolated app data, no game scene or phone performance claim."}
 if not output.is_empty():FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(record," ")+"\n")
 if not errors.is_empty():push_error("PROFILE_REPORT_PUBLICATION_REJECTED "+JSON.stringify(record))
 else:print("PROFILE_REPORT_PUBLICATION_PASS reads=",reads)
 quit(0 if errors.is_empty() else 1)
