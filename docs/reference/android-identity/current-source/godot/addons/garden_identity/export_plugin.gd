@tool
extends EditorPlugin

var _exporter: EditorExportPlugin

func _enter_tree() -> void:
	_exporter = IdentityExport.new()
	add_export_plugin(_exporter)

func _exit_tree() -> void:
	remove_export_plugin(_exporter)
	_exporter = null

class IdentityExport extends EditorExportPlugin:
	func _get_name() -> String:
		return "GardenIdentity"

	func _supports_platform(platform: EditorExportPlatform) -> bool:
		return platform is EditorExportPlatformAndroid

	func _get_android_libraries(_platform: EditorExportPlatform, debug: bool) -> PackedStringArray:
		var variant := "debug" if debug else "release"
		return PackedStringArray(["res://addons/garden_identity/bin/%s/garden-identity.aar" % variant])

	func _get_android_dependencies(_platform: EditorExportPlatform, _debug: bool) -> PackedStringArray:
		return PackedStringArray([
			"androidx.fragment:fragment:1.8.6",
			"androidx.credentials:credentials:1.5.0",
			"androidx.credentials:credentials-play-services-auth:1.5.0",
			"com.google.android.libraries.identity.googleid:googleid:1.1.1",
		])
