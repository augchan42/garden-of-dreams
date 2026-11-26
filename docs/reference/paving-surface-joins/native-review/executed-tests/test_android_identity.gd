extends SceneTree
## Exercises GDScript publication boundaries with a fake native transport.
## It does not prove actual Android plugin registration or Google sign-in.

class FakeBridge extends RefCounted:
	signal google_token_ready(attempt: int, token: String)
	signal google_sign_in_failed(attempt: int, code: String)
	signal identity_error(code: String)
	var generation := 0
	var cancellations := 0
	var headers := "{}"
	func beginGoogleSignIn(_client: String) -> int:
		generation += 1
		return generation
	func cancelSignIn() -> void:
		cancellations += 1
	func getDeviceClaimBody() -> String:
		return '{"platform":"android"}'
	func signedDeviceHeaders(_key: String, _secret: String, _body: String) -> String:
		return headers

var statuses: Array[String] = []
var published: Array[int] = []
var checks := 0

func _initialize() -> void:
	call_deferred("_run")

func check(value: bool, description: String) -> bool:
	checks += 1
	if not value:
		push_error(description)
		quit(1)
	return value

func _run() -> void:
	var wrapper_script = load("res://services/android_identity.gd")
	if not check(wrapper_script != null, "Identity wrapper did not load"):
		return
	var wrapper = wrapper_script.new()
	root.add_child(wrapper)
	wrapper.status_changed.connect(func(status: String): statuses.append(status))
	wrapper.provider_token_ready.connect(func(attempt: int, _token: String): published.append(attempt))
	if not check(not wrapper.is_available() and not wrapper.begin_sign_in("fixture"), "Desktop must report unavailable"):
		return
	if not check(statuses == ["unavailable"] and wrapper.device_claim_body().is_empty(), "Unavailable must not create a device identity"):
		return
	var bridge := FakeBridge.new()
	wrapper._bridge = bridge
	bridge.google_token_ready.connect(wrapper._on_google_token)
	bridge.google_sign_in_failed.connect(wrapper._on_google_failure)
	bridge.identity_error.connect(wrapper._on_identity_error)
	if not check(wrapper.begin_sign_in("fixture"), "Fake provider did not begin"):
		return
	var cancelled: int = wrapper._attempt
	wrapper.cancel_sign_in()
	bridge.google_token_ready.emit(cancelled, "fixture-cancelled-proof")
	bridge.google_sign_in_failed.emit(cancelled, "cancelled")
	if not check(published.is_empty() and statuses.back() == "provider_pending", "Cancelled provider callback was published"):
		return
	wrapper.begin_sign_in("fixture")
	var replaced: int = wrapper._attempt
	wrapper.begin_sign_in("fixture")
	var current: int = wrapper._attempt
	bridge.google_token_ready.emit(replaced, "fixture-replaced-proof")
	bridge.google_sign_in_failed.emit(replaced, "provider_unavailable")
	if not check(published.is_empty() and wrapper._attempt == current, "Replaced chooser affected current attempt"):
		return
	bridge.google_token_ready.emit(current, "fixture-current-proof")
	bridge.google_token_ready.emit(current, "fixture-duplicate-proof")
	if not check(published == [current] and statuses.back() == "provider_ready", "Provider proof must publish once without declaring authenticated"):
		return
	wrapper.begin_sign_in("fixture")
	var failed: int = wrapper._attempt
	bridge.google_sign_in_failed.emit(failed, "provider_unavailable")
	bridge.google_token_ready.emit(failed, "fixture-after-failure")
	if not check(published == [current] and statuses.back() == "provider_unavailable", "Completed failure accepted a late token"):
		return
	if not check(wrapper.signed_device_headers("fixture", "fixture", "{}").is_empty(), "Incomplete header object was accepted"):
		return
	bridge.headers = '{"X-API-Key":"fixture","X-Timestamp":"123","X-Signature":"fixture","X-Device-Credential":"fixture"}'
	if not check(wrapper.signed_device_headers("fixture", "fixture", "{}").size() == 4, "Native header conversion failed"):
		return
	bridge.headers = '{"X-API-Key":"fixture","X-Timestamp":123,"X-Signature":"fixture","X-Device-Credential":"fixture"}'
	if not check(wrapper.signed_device_headers("fixture", "fixture", "{}").is_empty(), "Non-string native header accepted"):
		return
	wrapper.free()
	if not check(bridge.cancellations == 2 and bridge.get_signal_connection_list("google_token_ready").is_empty(), "Wrapper removal must cancel and disconnect"):
		return
	var plugin_script = load("res://addons/garden_identity/export_plugin.gd")
	if not check(plugin_script != null, "Editor export addon did not parse"):
		return
	print("ANDROID_IDENTITY_WRAPPER_PASS: ", checks, " publication, fallback and export-parse checks; fake transport only")
	quit(0)
