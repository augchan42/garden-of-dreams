# Native Pixel 7 Pro evidence

See [device check](../../android-device-profile.md) for scope, measurements and remaining failures. All successful profiles use the staged b4 source, not the corrected roof source.

- `startup-diagnosis`: the first APK opened the normal landscape demo and wrote no profile; its export also reported a missing icon. Kept as failed runner evidence.
- `baseline`: successful portrait route with tiny physical-pixel controls.
- `baseline-tap`: real initial cast; `reading_open` is true. Its `garden-phone-after-touch.png` is stale because the first runner captured before drawing the overlay. `reading-visible.png` is the subsequent actual app screen capture. Do not use the stale image as visual reading evidence.
- `scaled`: final measured route and native cell/gate/pavilion views.
- `scaled-cast`, `scaled-recast`, `scaled-finale`, `scaled-replay`: real touch results after correcting capture timing. Ten pressed/released events in the replay report correspond to five taps. The final report returns to `terminal_room` with initial actions and no reading overlay.
- `checks`: native Godot regression logs. The red log intentionally includes the pre-fix failure and exit cleanup diagnostics; green logs are clean.
- `allocation-readback`, `allocation-stored`: actual native texture inventories after route timing. Mobile readback decompression is distinct from the loaded compressed format and renderer allocation; see `../../android-normal-candidate.md`.

Collection hashes cover the listed payloads. The additional baseline `reading-visible.png` is a separately saved native device screen capture, not one of that collection's original payloads. These are debugging and review artifacts, not final art, authenticated readings or release acceptance.
