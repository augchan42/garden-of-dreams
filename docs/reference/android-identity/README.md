# Android identity bridge evidence

The addon compiles against the installed Godot 4.7.2 Android ABI. The project does not enable it or call it from room actions yet. It acquires a transient provider proof; it does not declare an authenticated Records account or send HTTP requests.

Current evidence includes the exact native sources, debug/release AAR hashes, installed-template/classes hashes, build log, dedicated storage test APK and installed APK hash. `current-device-storage-tests.json` records three passing Android Keystore tests on the Pixel, including individual raw instrumentation status codes and final `OK (3 tests)`. No real account credentials are in these fixtures.

`jvm-tests.json` records twelve passing cancellation/signing assertions. Independent HMAC vectors include Unicode, whitespace and an empty GET body. `jvm-red.log` records a deliberately broken publication gate rejecting a cancelled-callback test; the exact broken source was not retained, and it is not represented as a complete red baseline for all twelve assertions.

`godot-wrapper-tests.json` and its log record thirteen passing checks in an isolated Godot project with a fake bridge. The export script parses. Real Android Godot registration, Google chooser operation, device claim, Records exchange, account credential storage/refresh, history and profiling remain unverified.

Earlier attempts remain available:

- The first Gradle fixture lacked `gradle.properties`; AndroidX dependency extraction failed. The archive records that file's actual absence.
- The second used a compile-only Fragment version incompatible with runtime dependency resolution. Fragment is now an implementation/export dependency.
- The first storage APK targeted SDK 24 and the Pixel refused installation with `INSTALL_FAILED_VERIFICATION_FAILURE`. It was not installed and no tests ran. Target SDK was then aligned to SDK 36; no device security setting or verification bypass was used.
- The SDK 36 compact instrumentation output reported `OK (3 tests)`, but the collector rejected it because raw completion codes were absent. The corrected runner requests `am instrument -r`, and the current record contains all three completion codes and terminal success.
- An editor-mode wrapper run passed its assertions but exited during the asynchronous filesystem scan, emitting shutdown leaks. That run was rejected. The clean normal headless run passes with no errors.

AGP's compile-SDK warning is preserved in the raw build logs. The archive proves the stated compilation, wrapper and storage scopes, not final release or authentication acceptance.

Build with `python3 scripts/build_android_identity.py --device-tests --report /tmp/garden-android-identity-build.json`. Run the core tests with `python3 scripts/test_android_identity_core.py --report /tmp/garden-identity-core-tests.json`. The dedicated device runner accepts a successful build report and explicit device serial; it checks both owning and instrumentation-target packages before installing, hashes installed APK bytes before executing tests, and never deletes another app's identity fixtures.
