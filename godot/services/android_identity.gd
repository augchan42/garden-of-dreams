extends Node
## Provider proofs are transient. A provider result is not a Records session.
signal provider_token_ready(attempt: int, identity_token: String)
signal status_changed(status: String)

var _bridge: Object
var _attempt := -1

func _ready() -> void:
	if OS.get_name() == "Android" and Engine.has_singleton("GardenIdentity"):
		_bridge = Engine.get_singleton("GardenIdentity")
		_bridge.connect("google_token_ready", _on_google_token)
		_bridge.connect("google_sign_in_failed", _on_google_failure)
		_bridge.connect("identity_error", _on_identity_error)

func is_available() -> bool:
	return _bridge != null

func begin_sign_in(web_client_id: String) -> bool:
	if not is_available():
		status_changed.emit("unavailable")
		return false
	_attempt = _bridge.beginGoogleSignIn(web_client_id)
	status_changed.emit("provider_pending")
	return true

func cancel_sign_in() -> void:
	_attempt = -1
	if is_available():
		_bridge.cancelSignIn()

func device_claim_body() -> String:
	if not is_available():
		return ""
	return _bridge.getDeviceClaimBody()

func signed_device_headers(api_key: String, signing_secret: String, serialized_body: String) -> PackedStringArray:
	if not is_available():
		return PackedStringArray()
	var text: String = _bridge.signedDeviceHeaders(api_key, signing_secret, serialized_body)
	var parsed: Variant = JSON.parse_string(text)
	if not parsed is Dictionary:
		return PackedStringArray()
	var headers := PackedStringArray()
	for key in ["X-API-Key", "X-Timestamp", "X-Signature", "X-Device-Credential"]:
		if not parsed.has(key) or not parsed[key] is String:
			return PackedStringArray()
		headers.append("%s: %s" % [key, parsed[key]])
	return headers

func _on_google_token(attempt: int, token: String) -> void:
	if attempt != _attempt:
		return
	_attempt = -1
	status_changed.emit("provider_ready")
	provider_token_ready.emit(attempt, token)

func _on_google_failure(attempt: int, code: String) -> void:
	if attempt != _attempt:
		return
	_attempt = -1
	status_changed.emit(code)

func _on_identity_error(code: String) -> void:
	status_changed.emit(code)

func _exit_tree() -> void:
	cancel_sign_in()
	if is_available():
		_bridge.disconnect("google_token_ready", _on_google_token)
		_bridge.disconnect("google_sign_in_failed", _on_google_failure)
		_bridge.disconnect("identity_error", _on_identity_error)
		_bridge = null
