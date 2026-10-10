extends RefCounted

# One serialized producer closes a complete replacement before publishing it.
# Readers keep seeing the prior report until the same-directory rename.
static func publish(path: String, report: Dictionary) -> Error:
 var absolute = ProjectSettings.globalize_path(path)
 var temporary = absolute + ".tmp"
 var encoded = JSON.stringify(report, "  ")
 var file = FileAccess.open(temporary, FileAccess.WRITE)
 if file == null:
  return FileAccess.get_open_error()
 file.store_string(encoded)
 file.flush()
 var error = file.get_error()
 file.close()
 if error == OK:
  error = DirAccess.rename_absolute(temporary, absolute)
 if error != OK:
  DirAccess.remove_absolute(temporary)
 return error
