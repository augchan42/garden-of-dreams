# Runtime texture audit — 2026-10-08

The installed `b4b322c2…` scene was inspected with the native Godot 4.7.2 Compatibility renderer on an Apple M2 Max. This is the complete preceding scene and lighting. Corrected roof source `90c4f70e…` is still baking; these results do not establish its final rendering or allocation.

The inventory covers active 3D material bindings, retained flora detail meshes and actual renderer texture allocation. It records no frame timings. Image-data totals exclude renderer padding, render targets, shadow maps and UI; the renderer's allocation total includes those resources. Normal exploration visits all fourteen arrival views; the demo visits its three arrivals. This does not replace continuous traversal or target-phone measurements.

## Current runtime caps — 2026-10-10

The cyclorama wash now imports losslessly at 256×256. This removes compression blocks in the dim backdrop lighting while retaining the original bake pixels, geometry and painted surface. Its loaded RGB8 resource is checked before wash materials are applied; the Android builder invalidates only this texture's generated cache and preserves the lossless setting. All 28 installed desktop/portrait arrivals reproduce the reviewed candidate. Native renderer allocation increases by 218,439 bytes. The rebuilt full profiler is verified but uninstalled; Android allocation and uninterrupted phone timing remain pending. See [lossless wash evidence](reference/lossless-backdrop-wash/README.md).

Pavilion/wall basecolors now import at 1024², with the lossless gate color/normal pair at 512×170. Source artwork, scene geometry and lighting are retained. Mandatory actual-size, format, mip, active-use and generated-cache checks protect native builds and phone collection. All 44 native arrivals/close views reproduce the reviewed candidate; the fresh phone demo stays at 54.01 MiB through five actual touch stages. Frame timing still fails. The preceding isolated full-garden comparison peaked at 62.29 MiB; fresh adopted-source sustained verification remains required. See [adoption evidence](reference/runtime-texture-caps/README.md).

The sections below retain earlier source-specific measurements and comparisons.

## Entrance inscription — historical 1024px comparison

The color image and recessed normal image were both imported at their full 2172 × 724 resolution without compression. Together their mipmapped readbacks occupied 14,674,436 bytes. That earlier comparison uses aligned, lossless, mipmapped 1024 × 341 imports, occupying 3,255,889 bytes. Original PNGs, alpha, geometry, UVs and source lighting are unchanged. Automatic compression detection is disabled for this pair.

| Mode | Before | After | Saving |
| --- | ---: | ---: | ---: |
| Demo | 58.3 MiB | 47.4 MiB | 10.9 MiB |
| Normal exploration | 63.9 MiB | 53.0 MiB | 10.9 MiB |

The real cap test fails before the change and passes after editor reimport. Desktop and portrait arrival and diagnostic close views use fixed shader time. Comparison regions come from the inscription mesh's actual projected bounds. RGB RMSE is 0.00426–0.00539, below 2/255; the 99th-percentile error is below 8/255. Both arrival images were directly reviewed and retain all four characters. The diagnostic portrait close view clips the same outer edges in the baseline and capped images; it is not final camera acceptance.

The current inventories contain 88 unique bound texture RIDs in the demo and 174 in normal exploration. Source paths do not duplicate across distinct bound RIDs in the normal inventory. Sharing, dimensions and readback formats are recorded per texture rather than inferred from file sizes.

![Capped portrait arrival](reference/gate-inscription-runtime-b4/after/portrait-arrival.png)

## Evidence and repeat commands

`export/gate-inscription-runtime-cap.json` records source/artwork/import hashes, image comparisons and actual allocation changes. Baseline and capped native images, reports and inventories are preserved in `reference/gate-inscription-runtime-b4/`. The independent current inventories are `export/runtime-texture-inventory-{normal,demo}.json`.

```sh
python3 scripts/configure_runtime_texture_caps.py --report /tmp/runtime-caps.json
/Applications/Godot.app/Contents/MacOS/Godot --headless --editor --path godot --import
/Applications/Godot.app/Contents/MacOS/Godot --path godot --script tests/test_gate_inscription_texture.gd
/Applications/Godot.app/Contents/MacOS/Godot --path godot --script tests/audit_runtime_textures.gd
/Applications/Godot.app/Contents/MacOS/Godot --path godot --script tests/audit_runtime_textures.gd -- --demo
python3 scripts/verify_gate_inscription_cap.py
```

The last command verifies the preserved same-source comparison. Fresh runtime runs identify their actual source hash and must not be used to relabel these earlier images. Final corrected-source allocation, all kit/hero atlas and power-of-two requirements, filtering/seams/texel density, art acceptance and phone performance remain open.

## Current source inventory — 2026-10-09

The native M2 Max Compatibility inventory for `1380ceca` reports 52,517,225 renderer texture bytes in normal exploration (maximum sampled arrival 52,600,513) and 43,468,745 in the focused demo (maximum sampled arrival 43,512,435). Bound image data is 36,525,582/30,245,390 bytes respectively; renderer allocations include additional resources. The demo stationary allocation is under 64 MiB. This does not establish physical-phone, sustained traversal or frame-time acceptance. Detailed per-texture bindings/dimensions and current source/runtime hashes are retained in `reference/ziling-source-art/review/texture-memory-{normal,demo}.json`. Current released/installed Android builds remain on the prior source.


## Full-garden profiling tools — 2026-10-10

The normal tour is now integrated into the builder/collector, with mandatory two-tour/600-second coverage, actual Android normal loaded-cap checks, all producer/dependency and packaged scene/script identity checks, atomic reads, floor/camera/capture/budget validation and pause/focus rejection. Twenty-two Python tests, actual Godot minimum-tour/pause/counter controls and final isolated build/APK resource checks pass. The final pause-protected package has not been installed: the phone switched apps during the preceding run. Its five completed legs reached62.29MiB, which is partial evidence only.

The full goal remains open. Restart the sustained test when the phone can remain in Garden for about15minutes. Then measure combined viewport draws/primitives and isolate rendering/process costs with controls; zero native GLES GPU counters are unavailable, while Godot's process monitors are repeated once-per-second window maxima. Continue final per-site art, five references,2020Adreno,release andauthenticated services. See [tooling and retained incomplete attempts](reference/full-garden-profiler/README.md).


## Engine-wide frame-budget correction — 2026-10-10

The full-phone producer and collector now gate draws/primitives on actual engine-wide per-frame counters, including the pond capture, while retaining main-view visible counts as diagnostics. Native controls exposed and now reject reflection-only overruns; disabling the capture again resets the sample, and a UI rectangle establishes the observed renderer scope. All 26 Python tests and four native regression programs pass. All 28 stationary native arrival samples are retained: desktop terminal 160 and gate 155 exceed the 150-draw limit; portrait arrivals and all primitive totals pass their respective limits. These are static counter diagnostics, not sustained or physical-phone acceptance.

The fresh full debug APK is `6bb60f68` (86,531,491 bytes), with four clean build phases and offline provenance/package checks. It remains uninstalled pending phone availability; earlier 735bf87b and 9dde9d29 packages are historical for the current collector. Continue current-source phone profiling, failed desktop draw budgets and final per-site art. Final art, five exact references (37/42), 2020 Adreno, sustained budgets, release and authenticated services remain open. See [counter evidence](reference/all-viewport-profile/README.md).
