# Lossless backdrop wash — 2026-10-10

The cyclorama wash now imports losslessly at 256×256. The previous compressed resource produced block patches in its dim lighting. This changes one texture import, adds a loaded-resource guard and makes the same configuration reproducible in the Android builder. Original painting, source geometry, UVs and all baked lighting pixels are retained.

The native Godot 4.7.2 Compatibility comparison on Apple M2 Max uses six counterfactuals per import. Repeated baselines match exactly, and disabling the wash produces identical pixels across compressed/lossless imports. Disabling ordinary lighting changes nothing because this surface already does not use that map. The physical canvas seam and baked moon shadow remain visible; this correction does not remove them or establish final art acceptance.

Compressed wash:

![Compressed backdrop](diagnosis/compressed256/baseline.png)

Lossless wash:

![Lossless backdrop](diagnosis/lossless256/baseline.png)

Current verification:

- 25 Python tests pass. The configurator's positive RED run failed for the missing implementation; GREEN verifies the lossless settings, source preservation and owned cache invalidation. Missing parameters and escaped cache paths reject before mutation.
- The actual compressed 256px texture was accepted in normal/demo modes before the guard, then rejected in both after it. The two errors in `resource-rejection-green.log` are deliberate negative controls. The actual lossless RGB8 resource applies all six wash receivers, including both cyclorama surfaces.
- Seven installed native checks pass without engine diagnostics: wash resource, normal/demo wash bindings, existing caps, moon, desktop arrivals and portrait arrivals. All 28 installed originals match the reviewed candidate byte for byte; all 28 candidate originals were directly reviewed.
- The fresh installed normal inventory has 178 bound texture RIDs and 40,857,593 renderer texture bytes. Only the wash resource changes in the same-source comparison, adding 218,439 native renderer bytes and 163,840 stored image bytes. These are separate allocation measures, not phone estimates.
- Current-source preservation is recorded per file in `checks/installed-source-preservation.json`. The cyclorama import and its runtime guard are the only differences in the checked scene/lighting/runtime inputs. The native inventory was rerun after adoption rather than reusing its earlier import hash.
- The rebuilt full Android profiler passes four build phases with no engine diagnostics. APK inspection verifies 177 bound imports/payloads, seven compiled diagnostic dependencies, the imported scene, and the compiled wash guard. Current/staged renderer hashes match. APK SHA-256 is `735bf87be0221775c40e308268b61696c71ddb5b93ad66e39b017bb14171bf20`, size 86,531,491 bytes.

**The new APK is uninstalled.** No phone operation or user-editor mutation occurred in this adoption. Actual Android lossless-resource/allocation proof and an uninterrupted two-tour/600-second run remain pending phone availability. The preceding `9dde9d…` profiler is historical after the import/guard change. The full goal still requires final fourteen-site art, five reference slots (37/42), sustained rendering budgets, 2020 Adreno verification, release and authenticated services.

Archive layout:

- `diagnosis/`: compressed/lossless six-case originals, reports, source analysis and allocation comparison. `conclusion.json` is the unchanged **pre-adoption checkpoint**, with four arrival views reviewed at that time. Its production/APK status and next steps are historical; `checks/adoption-summary.json` records the current adoption and all 28 reviewed arrivals.
- `installed/`: 28 installed arrival originals and native route reports.
- `checks/`: actual RED/GREEN reports, native checks, source preservation, current inventory and final Python log. The initial additional inventory launch exited 134 inside the restricted sandbox without output; a permitted separate native process then completed successfully. The original no-fog diagnostic stalled; its log/source are retained, and the completed comparisons hold fog fixed.
- `android/`: build report, finalized manifest, four exact build logs and payload/renderer verification. The debug APK is retained in the ignored task backup rather than Git.
- `executed-source/`: source snapshots used for the checks. `archive-manifest.json` pins every other archived file by hash and size.

Reproduce the import and native resource check:

```sh
python3 -m unittest discover -s scripts/tests
python3 scripts/configure_backdrop_wash_import.py --report /tmp/backdrop-import.json
/Applications/Godot.app/Contents/MacOS/Godot --headless --editor --path godot --import
/Applications/Godot.app/Contents/MacOS/Godot --path godot --script res://tests/test_backdrop_wash_import.gd -- --output=/tmp/backdrop-resource.json
python3 scripts/build_android_profile.py --mode full --report /tmp/android-full-build.json --apk /tmp/garden-full-profile.apk
```

Fresh evidence must identify its own source and package hashes. Refer to the [phone profiling procedure](../../android-device-profile.md#reusable-full-garden-profiling) when the phone can stay in Garden for the full run.
