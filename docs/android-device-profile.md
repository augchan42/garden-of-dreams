# Android device check

The measurements below are historical Pixel 7 Pro results for source `90c4f70e`, Android API 36, Mali-G710 and Godot 4.7.2 Compatibility. The repaired PBR comparison with 1024 normal/ORM imports and shared font sizes reaches 62,178,472 bytes (59.3 MiB) through route, reading, finale and replay; see [that material-transfer evidence](pbr-material-transfer.md).

The preceding production baseline completed two full fourteen-room tours on 2026-10-10: 52 travel legs, 735.865 timed seconds and zero floor misses. Texture memory peaked at 68.62 MiB and frame-interval P95 was 18.623–28.434 ms, failing both the 64 MiB and 60 fps targets. See the [full phone baseline](reference/full-garden-phone-baseline/README.md).

An isolated candidate caps two basecolor imports at 1024² and the lossless inscription pair at 512×170. It completed the same two tours with a 62.29 MiB peak, saving 6.33 MiB in all 105 matched phases. Separate cast, recast, close, finale and replay taps passed at 54.01 MiB. See the [texture cap comparison](reference/texture-memory-caps/README.md).

These four caps are now adopted with actual-resource, enabled-material and finalized-cache provenance checks. A fresh installed-source Pixel 7 Pro APK passed all five native touch stages, with 54.01 MiB peak texture memory and zero partial report reads. Its P95 was 22.403–45.723 ms, so the 60 fps target still fails. All 44 native arrival/close images reproduce the candidate exactly. See [production adoption evidence](reference/runtime-texture-caps/README.md). A fresh adopted-source full tour, release, sustained 60 fps and the specified 2020 Adreno hardware remain open.

The tables and original UI measurements below are historical `b4b322c2` results. Later corrected-roof evidence is under `docs/reference/android-roof-current/`; the repaired-renderer comparison is under `docs/reference/pbr-transfer/`. Their source/build hashes keep these separate.

## Controls

The first phone run exposed physical-pixel UI sizing: action buttons were only 38 pixels high on the 420-DPI display. The route now scales Android/iOS UI by reported DPI / 160, bounded to 1–4, using `canvas_items`. Android actions, command input, reading and finale controls have a 48-unit minimum height. Desktop scale remains 1.

On this phone, native output remains 1080 × 2340, the logical interface is 411.43 × 891.43 and the scale is 2.625. Action buttons are 126 physical pixels high. The native cell, gate and pavilion images were reviewed, as were the reading and finale overlays. Actual ADB touch events activated cast, recast, close, finish and replay. Replay returned to the cell with the initial two actions and no reading overlay. Route travel uses the actual physics paths; taps occur after the profiler finishes its automatic route.

`test_mobile_ui_scaling.gd` failed before the change and passes after it. The existing portrait action scrolling test and native desktop pointer/keyboard route and replay test also pass. iOS is configured by the shared scaling code but has not been run on hardware. Soft keyboard, rotation, all normal room menus and safe areas across other devices remain unverified.

The scale follows Godot's [canvas-items stretch behavior](https://docs.godotengine.org/en/stable/tutorials/rendering/multiple_resolutions.html). This changes interface density while retaining native 3D rendering.

## Measured budgets

Final scaled run, 60-FPS engine cap, actual frame intervals; no forced draws or synthetic frame clock during measurement:

| View / movement | Median ms | p95 ms | Maximum draws | Maximum primitives | Texture bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cell | 17.255 | 20.531 | 73 | 131,906 | 73,184,428 |
| Cell → gate | 17.302 | 21.683 | 78 | 131,906 | 74,757,292 |
| Gate | 17.407 | 20.498 | 103 | 138,624 | 74,757,292 |
| Gate → pavilion | 17.363 | 20.418 | 67 | 116,132 | 74,761,384 |
| Pavilion | 17.164 | 19.128 | 53 | 95,300 | 74,761,384 |

Draws, primitives and the four-practical limit pass in these sampled views and paths. Lowest player Y is −0.02862 m, within the floor tolerance. The 64 MiB texture target fails: peak allocation is 71.3 MiB. Before the UI fix, the peak was 69.1 MiB. Larger UI glyph allocations add memory; screen buffers and mobile texture formats still need an actual allocation diagnosis. A 60-FPS cap is not proof of sustained 60 FPS: the observed medians are around 17.3 ms and tails are slower. The 2022 Mali device is not the specified 2020 Adreno class.

The staged roof remains dark, and the portrait moon/enclosure framing still needs art work. The scene does not gain visual acceptance merely because these measurements exist.

Later native touch-state measurements expose a larger complete-demo peak: 75,809,960 bytes after cast/recast/close and 77,907,112 after finale/replay (74.3 MiB). The table above remains the original scaled route measurement. An isolated 1024 normal-map experiment saves 8 MiB but still reaches 66.3 MiB at finale/replay; production normal imports remain unchanged. See [the allocation and candidate evidence](android-normal-candidate.md). These old-source phone measurements remain distinct from the subsequently installed corrected roof source.

## Evidence and reproduction

Evidence is under `docs/reference/android-profile-b4/`. `baseline` records the unscaled successful profiling run; `scaled` records the final measured route. `scaled-cast`, `scaled-recast`, `scaled-finale` and `scaled-replay` retain touch-state reports and native images. Each collection records source/build hashes and hashes of its files. The initial `--script` APK launched the regular demo without a report; `startup-diagnosis` preserves that observation. The builder now uses an explicit isolated startup scene and icon, and rejects engine import/export diagnostics. An early after-touch image preceded the completed draw; the corrected collector runner waits for `frame_post_draw`.

The profiling export is generated in a separate temporary project, enables mobile texture imports there and installs under `org.godotengine.gardendreams.profile`. Production startup and export settings are unchanged. The large diagnostic APK includes the installed full scene/resources; its size is not a release size claim. It has no internet permission. The collector reads only this app's private diagnostic files and its process log.

Actual `aapt2` permission inspection confirms no INTERNET permission and reports a missing themed-icon XML reference from the APK. The diagnostic app installed and ran, but this icon warning still needs fixing for a release export.

```sh
python3 scripts/build_android_profile.py
adb -s SERIAL install -r build/garden-phone-profile.apk
adb -s SERIAL shell am start -n org.godotengine.gardendreams.profile/com.godot.game.GodotAppLauncher
# Phone must be awake. Wait for PHONE_PROFILE_READY_FOR_TAPS in the app log.
python3 scripts/collect_android_profile.py --device SERIAL --destination NEW_EVIDENCE_DIRECTORY
```

Use the report's `buttons` screen centers for real touch checks. Collections require a new directory, a finished current profile and matching APK, source and runtime-script records. They preserve failed budget results rather than treating successful collection as performance acceptance. `export/android-profile-build.json` points to the latest collected evidence.


## Reusable full-garden profiling

The builder accepts `--mode full` for the normal fourteen-room route. The full producer uses the canonical public commands, records every grounded floor ray, waits for each camera to settle and completes at least two whole tours with at least 600 timed seconds. Image readback happens after each timed phase. Normal time scale, 60 Hz physics and the 60 fps cap are checked; a completed tour can still fail performance budgets.

The staged build records every profiler dependency. Before collection, current source scripts, imported texture inputs, enabled material bindings, generated cache files and the installed APK must match. APK inspection also verifies the actual compiled script remaps and imported scene payload. All 53 two-tour captures require the exact expected filename, published hash, dimensions and room. The collector checks coverage, command order, arrival signals, floor support and every budget result. It preserves failed budgets.

```sh
python3 scripts/build_android_profile.py --mode full --report export/android-full-profile-build.json --apk build/garden-full-profile.apk
adb -s SERIAL install -r build/garden-full-profile.apk
adb -s SERIAL shell am force-stop org.godotengine.gardendreams.profile
adb -s SERIAL shell run-as org.godotengine.gardendreams.profile rm -f files/garden-phone-profile.json files/garden-phone-profile.json.tmp
adb -s SERIAL shell am start -n org.godotengine.gardendreams.profile/com.godot.game.GodotAppLauncher
python3 scripts/collect_android_profile.py --device SERIAL --build-report export/android-full-profile-build.json --destination NEW_FULL_EVIDENCE_DIRECTORY --wait-timeout 2100
```

Keep the phone awake. The wait accepts an explicit “file not yet published” marker for at most 20 seconds at startup. Empty, partial or diagnostic text is a failure. Reports publish atomically on the phone and in the host progress file. Source/cache/installed identity is rechecked after the sustained wait.

The full profiler separately records the engine's frame and physics monitors, frame setup CPU time and CPU/GPU counters for each update-enabled viewport. Rendering CPU time excludes script/physics work, and the engine monitors overlap with rendering work; their values must not be added together. A disabled pond reflection viewport is recorded without sampling its stale render counters. All-zero timing counters are marked unavailable. See [Godot's viewport timing documentation](https://docs.godotengine.org/en/4.7/classes/class_renderingserver.html#class-renderingserver-method-viewport-get-measured-render-time-cpu) and [engine monitor definitions](https://docs.godotengine.org/en/4.7/classes/class_performance.html#enum-performance-monitor).


Godot 4.7.2 updates the process and physics monitors once per second with the preceding window's maximum. Their sampled quantiles contain repeated window maxima and can retain an untimed screenshot/readback stall after travel starts. They are not per-frame script/physics percentiles. Use the delivered-frame intervals for the 60 fps gate and the separate viewport counters for rendering CPU observations; raw process monitor spikes need further instrumentation before identifying a hot path. This behavior is visible in the [4.7.2 main-loop implementation](https://github.com/godotengine/godot/blob/4.7.2-stable/main/main.cpp#L4743-L4765).

An Android pause or application focus loss during a running full tour publishes a failed report and stops timing. Returning later cannot turn an interrupted run into sustained acceptance. The completed report is retained when the app loses focus afterward.
