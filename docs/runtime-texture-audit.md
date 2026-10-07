# Runtime texture audit — 2026-10-08

The installed `b4b322c2…` scene was inspected with the native Godot 4.7.2 Compatibility renderer on an Apple M2 Max. This is the complete preceding scene and lighting. Corrected roof source `90c4f70e…` is still baking; these results do not establish its final rendering or allocation.

The inventory covers active 3D material bindings, retained flora detail meshes and actual renderer texture allocation. It records no frame timings. Image-data totals exclude renderer padding, render targets, shadow maps and UI; the renderer's allocation total includes those resources. Normal exploration visits all fourteen arrival views; the demo visits its three arrivals. This does not replace continuous traversal or target-phone measurements.

## Entrance inscription

The color image and recessed normal image were both imported at their full 2172 × 724 resolution without compression. Together their mipmapped readbacks occupied 14,674,436 bytes. They now use aligned, lossless, mipmapped 1024 × 341 imports, occupying 3,255,889 bytes. Original PNGs, alpha, geometry, UVs and source lighting are unchanged. Automatic compression detection is disabled for this pair.

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
python3 scripts/configure_gate_inscription_imports.py
/Applications/Godot.app/Contents/MacOS/Godot --headless --editor --path godot --import
/Applications/Godot.app/Contents/MacOS/Godot --path godot --script tests/test_gate_inscription_texture.gd
/Applications/Godot.app/Contents/MacOS/Godot --path godot --script tests/audit_runtime_textures.gd
/Applications/Godot.app/Contents/MacOS/Godot --path godot --script tests/audit_runtime_textures.gd -- --demo
python3 scripts/verify_gate_inscription_cap.py
```

The last command verifies the preserved same-source comparison. Fresh runtime runs identify their actual source hash and must not be used to relabel these earlier images. Final corrected-source allocation, all kit/hero atlas and power-of-two requirements, filtering/seams/texel density, art acceptance and phone performance remain open.
