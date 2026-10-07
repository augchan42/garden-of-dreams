# Android device check

Actual Pixel 7 Pro, Android API 36, Mali-G710, Godot 4.7.2 Compatibility renderer. The debug APK uses the installed `b4b322c2` scene and its matching complete lighting catalogs. The corrected `90c4f70e` roof source is still baking. These measurements do not establish corrected-source, release-build, whole-garden or 2020 Adreno acceptance.

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
