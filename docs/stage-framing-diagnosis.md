# Moon and backdrop framing diagnosis

This is a read-only diagnosis of the saved Blender source and current Godot arrival cameras. It does not change geometry, camera poses or lighting, and does not establish final camera acceptance.

Native saved-source inspection confirms an eight-panel, 48 m radius enclosure with its bottom at −2 m and top at 20 m. The moon is still a plain 128-vertex disk: no primary UVs or image nodes. Its base color is warm `(0.62, 0.58, 0.38)`, but its emission remains the earlier green `(0.42, 0.55, 0.20)` at strength 0.8. This is a separate source material from the already corrected mountain painting.

The live Blender MCP connection works through its older addon fallback and reports Blender 5.2.2 LTS. Its loaded scene has 40 cameras; the saved authoring file has 42. The live scene was neither saved nor reloaded. Saved-source evidence is authoritative for further work.

Native Godot projection measurements cover fourteen arrivals at 1410 × 600 and 390 × 844. Most desktop views use 55° vertical FOV, which gives about 101.5° horizontal coverage at that viewport. Portrait views that preserve a 55° horizontal FOV expand to about 96.8° vertically. These are measured with the actual camera projection API, rather than inferred from a Blender lens label.

Top-row rays cross an approximate radius-48 m cylinder above the enclosure in five desktop and eleven portrait arrivals. These indicate possible backdrop exposure; roof, foliage and wall occlusion can hide it, so the counts are not counts of visibly failed images. Qinfang's portrait moon bounds have four of eight corners inside the window, consistent with its existing clipped-moon screenshot. Some other shots deliberately face away from the moon.

The next correction should address the affected shot composition and physical backdrop coverage while retaining the separate authored Aojing arrival/pond cameras and their water-dominant view contracts. The painted moon also needs its own material treatment. A source/UV/material change requires matching exports and lighting refresh; this diagnosis does not justify relabelling existing bakes compatible.

Evidence: `export/stage-framing-saved-source.json`, `export/stage-framing-runtime.json` and `docs/reference/stage-framing/`. Reproduce projection measurements with the installed native Godot:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path godot --script res://tests/inspect_stage_framing.gd -- --output=/tmp/stage-framing.json
```
