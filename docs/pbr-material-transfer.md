# Baked material transfer and mobile allocation

The Godot adapter now retains the imported pavilion and wall roughness/metallic maps. glTF supplies these as `StandardMaterial3D` textures, with roughness in green and metallic in blue. The former adapter handled only `ORMMaterial3D`, so the imported maps were dropped. Standard numeric factors, independent maps and all five channel choices are preserved. Native ORM uses its channels directly and ignores its hidden Standard factors. AO stays in the Cycles bake and is not multiplied again.

The adapter also explicitly matches Godot's Burley diffuse and Schlick-GGX specular modes. A native pixel comparison initially detected this separate mode mismatch. After correction, all twelve Standard/ORM cases match their original Godot materials exactly. Removing a map changes every case visibly. Baked unit-sun energy still matches within 0.01 display RGB. The source semantics are in [Godot 4.7.2 material.cpp](https://github.com/godotengine/godot/blob/4.7.2-stable/scene/resources/material.cpp).

## Phone comparison

Two fresh debug APKs use corrected source `90c4f70e…`, matching lightmaps and the same repaired renderer. Both run on the same Pixel 7 Pro at native 1080 × 2340, UI scale 2.625 and 126-pixel action targets. Actual physics travel and ten touch edges cover cast, recast, close, finale and replay.

| Setting | Full-resolution baseline | Verified candidate |
| --- | ---: | ---: |
| Pavilion/wall normal imports | 2048² | 1024² |
| Pavilion/wall ORM imports | 2048² | 1024² |
| Reading body / finale heading | 18 / 28 | 16 / 22 |
| Complete sampled demo peak | 77,907,112 bytes | 62,178,472 bytes |
| MiB | 74.30 | 59.30 |

Atlas allocation falls by exactly 12 MiB in all route samples. Finale/replay show another 3 MiB reduction with shared UI font sizes. The sampled candidate passes both 64 MiB and decimal 64 MB. Casts remain stochastic; exhaustive glyph-cache warming is not measured. This is not sustained 60-FPS, release, full-garden or 2020 Adreno acceptance.

Twelve native placed-material comparisons cover Qinfang and Hengwu arrivals, close views and an inspection light in landscape and portrait. Every inspection view has positive normal and ORM controls. The first Hengwu portrait camera cropped out the wall; its failed assertion is retained and the inspection camera now targets the west wall. Maximum image RMSE is 0.000831, and the 99th-percentile difference is at most one 8-bit level. Phone arrival comparisons also pass. Reading and finale images were directly reviewed for legibility and fit.

The four 1024 import settings and existing 16/22 font sizes are now applied to the project. Original 2048 PNGs, color maps, Blender source and bake energy are unchanged. `export/android-pbr-adoption.json` records the installation and subsequent checks. Future scene/material revisions still require per-site visual acceptance.

## Evidence

`docs/reference/pbr-transfer/` retains regression failure, imported material inspection, the first lighting-mode mismatch, native positive/negative controls, twelve baseline/candidate placed captures, and six immutable phone collections per APK. `export/android-pbr-candidate-comparison.json` records exact renderer hashes, controlled settings, atlas dimensions, memory and image comparisons. Reproduce verification with `python3 scripts/verify_android_pbr_candidate.py`.

The first phone baseline launched while the display was dozing and retained an older report. It was rejected; no old report is counted as a new measurement. The current candidate resumed the same process after waking the display. The final baseline ran afterward, with the display awake. The workers verify exact embedded build metadata before collecting any report. All accepted engine build and runtime logs are checked for diagnostics.

Three earlier font/normal/ORM variants are preserved separately under `docs/reference/android-font-candidate/` and summarized in `export/android-font-candidate-pre-fix.json`. They establish allocation changes before this repair. Their missing renderer provenance and dropped roughness maps make them insufficient for material acceptance.

The local demo PCK/movie/ZIP now contains the verified material adapter, 1024 imports and shared UI sizes. Eleven actual packed checks, including native pointer/keyboard replay and twelve PBR pixel cases, pass. The fresh 1,290-frame movie and five-file archive are recorded in `export/pbr-current-demo-release.json`; prior payloads are preserved locally. The run guide now correctly distinguishes Android process-frame intervals from Mac forced draws. Final per-site art, framing, full-garden traversal and target-phone performance remain open.
