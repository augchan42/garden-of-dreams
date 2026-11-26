# Records session storage evidence

This adds encrypted Android account-session persistence to the disabled Garden identity addon. Six package-private classes retain server-verified access/refresh credentials under one owner. Plugin methods, Godot controls and HTTP flows are not connected yet.

The owner epoch stays stable across refresh so a refused request can retry under its original owner lease. Each refresh changes a separate credential revision, preventing two competing refresh writers from both committing. Another sign-in, even for the same account, replaces the owner epoch. Sign-out persists an encrypted empty state and invalidates prior completions.

The AES-256-GCM envelope uses a separate Android Keystore alias and the app no-backup directory. Missing storage creates only an empty state. Corruption, malformed payloads and missing keys fail without replacing existing bytes or inventing credentials. A shared process lock serializes store instances. Callers must run storage off the main thread and recheck the owner lease when a queued UI result is actually delivered.

Verified on the exact current sources and installed test APK:

- 34 JVM assertions: 8 provider callback/cancellation, 4 independent HMAC vectors, 22 Records state and payload checks.
- Debug and release library compilation against the installed Godot 4.7.2 Android template ABI. The raw log retains AGP's compile-SDK warning.
- 11 actual Pixel 7 Pro Android Keystore tests: persistence, refresh predecessor/races, owner switching, sign-out, stable owner across refresh, same-owner re-sign-in, corruption, key loss and file size.
- 3 existing device-identity storage tests pass with the same APK. Its installed bytes match tested-device-fixture.apk.
- All compiled source and AAR hashes match the adopted files. The installed JVM runner passes after adoption.

The first candidate genuinely passed its narrower tests but was rejected: it changed the owner lease during refresh, contrary to the inspected 401-retry contract. rejected-v1 contains the exact predecessor state and test that fails that contract. Earlier successful V1 build/device artifacts remain in the ignored work ledger. These are qualified storage results, not authenticated service acceptance.

The authenticated plaintext schema is version 2; the envelope remains version 1. No released-storage migration is claimed. Expirations are Unix seconds. Expired credentials remain stored so the eventual service adapter can distinguish refresh, refusal and outage without downgrading an account request to device-only history. The adapter must establish server ownership before storing credentials.

Real Android Godot registration, Google chooser/provisioning, client/device exchange, authenticated Records exchange, private history/pagination, reading writes, AI, presence, social services and release remain required. All test credentials are synthetic. No real provider token, account credentials or private history were read or sent. No Garden activity or phone performance test ran. Scene sources and the ongoing water-edge bake are unchanged.

Reproduce with scripts/build_android_identity.py --device-tests, scripts/test_android_identity_core.py, scripts/run_android_records_storage_tests.py and scripts/run_android_identity_storage_tests.py. Each device runner requires a successful build report and explicit serial, checks both manifest packages, hashes the installed APK and requires individual completed instrumentation codes. Run only the dedicated fixture package.

Older identity evidence is historical at docs/reference/android-identity. This archive records the new AAR/storage source; it does not rewrite older reports.
