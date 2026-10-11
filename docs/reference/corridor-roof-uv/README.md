# Corridor roof lightmap charts

Sixteen Qinfang corridor roofs had lightmap triangles smaller than one texel at the installed 256 px resolution. The roofs now use continuous charts with padding. Roof geometry, primary texture UVs, materials, lights and runtime code remain unchanged.

![Previous north corridor roof](native-baseline-corridor/desktop-north.png)

![Corrected north corridor roof](installed-native-corridor/desktop-north.png)

![Corrected portrait roof view](installed-native-corridor/portrait-north.png)

The canonical export reserves sixteen 128 px cells with 4 px padding in the 1024 px atlas. All 784 roof triangles exceed one texel at 256 px: minimum source area is 5.11362 texels and actual native mesh area is 5.11246 texels. All 167 batch UV overlap checks pass. Only the pavilion batch's secondary UV buffer and its accessor change; every other binary byte and all fourteen other site exports are preserved. All sixteen saved-source canonical exports reproduce exactly.

The source and engine GLB are `7fb3bbc1`. Authoring remains `4eb31445`; runtime remains `ec42ec55`. Six complete source-lighting phases produce 124 ordinary, ten backdrop-wash and seven terminal-spill maps. Fifteen isolated native phases pass, with 78 decoded and hashed originals. All fourteen roof views and all 28 room arrival views were directly inspected. Both actual desktop and portrait tours pass fourteen rooms and 26 public-command legs at normal 60 Hz physics; all 278 tour PNGs decode and match their recorded hashes.

Installed validation passes nineteen phases. All 141 import parameter sets are retained, 285 engine inputs match the isolated candidate, and fourteen installed roof images match the reviewed candidate byte for byte. The 26 Python tests pass. The offline full diagnostic Android APK passes compiled dependency, texture payload and provenance checks: 86,523,299 bytes, SHA-256 `218c9f2583fb6f34af0d16985e01878506ced3a21d88fd91112da924927fcfcf`. It remains uninstalled.

The first native runner used the wrong framing-result marker. Its actual test had exited successfully with eighteen valid images. The failed runner and records are retained; only the marker was corrected before the remaining phases resumed. The separate wrong Python test-discovery path is also retained; the correct `scripts/tests` suite passes. No source bake was restarted to hide either failure.

This accepts the roof UV correction. Final site art, five missing references, the Aojing ground strip, stream elevation, physical-phone performance, release and service integration remain open. The independent one-pixel Ouxiang comparison remains unresolved. User Blender and Godot editor sessions were not reloaded.

Run source coverage with `python3 scripts/verify_corridor_roof_uv.py` and actual native coverage with Godot's `res://tests/test_corridor_roof_uv.gd`. Proof reports, executed helpers and original reviewed images are included here; all tour originals and source maps are retained in the durable local plan archive. `files.json` records every published file except itself.
