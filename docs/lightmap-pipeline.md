# Cycles lightmap pipeline

**Current revision:** The hilltop art pass changed the assembly after the measurements below. Those maps are now stale; the source-hash guard rejects them. Production continues to use dynamic lighting until a fresh bake is generated for the final art.

The current Cycles bake covers all 133 opaque exported meshes. Source hashes, material transfer and engine application pass. A compressed 512-pixel runtime profile now meets the desktop texture-memory target, but production still uses dynamic keys while lighting, route quality and mobile acceptance remain open.

## Current process

1. Export the authoring scene with `scripts/export_garden.py`. Static batches and hero meshes receive UV2. Each mesh has its own unit-square chart; different mesh charts are not a shared atlas.
2. Run Blender in a separate background process with `scripts/bake_lightmaps.py`. Its default target is the Qinfang stone batch, at 1024² and 32 Cycles samples. `--mesh`, `--size`, and `--samples` select another target or quality.
3. The script imports the actual exported GLB, hides collision meshes and fog cards, and bakes diffuse direct/indirect lighting without material color. Point lights are excluded because those practicals remain dynamic. Emissive surfaces can still contribute indirect light.
4. The linear lighting is divided by a recorded peak scale and saved as a PNG. The adjacent JSON records the scale, UV-channel/hash, source GLB hash, samples and nonzero coverage. `scripts/verify_lightmaps.py` rejects stale or empty bakes.
5. Copy matching PNG/JSON files into `godot/lightmaps/`, import, and run `tests/render_lightmap.gd` for the Qinfang comparison. The test assigns `baked_diffuse.gdshader` only in that test instance: UV2 supplies the lighting, while practicals can light layer 2. The production scene remains unchanged.

## Evidence and limitations

The exported assembly now passes an explicit UV2 check for every render node, including previously missing bridge/table/stair hero meshes. The Qinfang bake contains light data in 19.32% of the image and uses a scale of 1.86289. `lightmap-dynamic.png` and `lightmap-baked.png` were rendered and visually inspected in Godot; roof/post shadows are visible on the baked corridor. The bake is darker than the calibrated Godot dynamic result.

Remaining: finish the per-site bake lighting rig (including the specified backdrop wash), choose texel density and atlas layout, verify UV seams/overlap and noisy small islands, bake all opaque geometry, preserve emission/roughness/textures in the final material adapter, verify baked shadows from all camera routes, replace dynamic keys only after coverage is complete, then profile again. The first PNG is not evidence that these requirements are done.

## Full-site bake and UV repair

The bake tool now accepts `--site qinfang-ting` or `--site all`, resolving mesh membership from the individual exported site GLBs. Small props receive 256² maps; larger batches receive the requested size. A complete Qinfang comparison applied 15 opaque-mesh lightmaps and retained source albedo, roughness, metallic and emission properties. Water remains on its own shader.

Godot normalizes the exported hero names' periods to underscores. `sync_lightmaps.py` explicitly maps those names, rejects collisions and stale source hashes, and builds the adapter index. The adapter remains experimental and is only used by the comparison test.

A new `verify_uv2.py` raster check found overlapping triangle interiors in the tunnel's stone batch: 24 texels at 512². Lowering the projection angle alone left five. Triangulating the tunnel before unwrapping eliminated the detected overlap across all 137 render meshes. This tests sampled interior coverage, not subtexel overlap or padding quality.

The source GLB changed during this repair, so preceding lightmaps are conservatively stale. The all-site bake was stopped by its confirmed process ID and restarted only after the UV check passed. Baking now captures the source hash once at startup, preventing records from being labelled with a later changed file. `verify_lightmaps.py --require-all` is the coverage gate after that run finishes; do not sync incomplete/stale results into the adapter.

## Full-garden validation and performance

The replacement bake completed against source SHA256 `c1dd22febfd8797463ddb4a2bce5e75c8f1ecf0cc5334c306c71f0e552b8e7ee`. `export/lightmaps-coverage.json` records 133 expected and 133 baked meshes, with no missing or unexpected meshes. Native Blender pixel inspection preserves 16-bit precision when checking very dark maps; the verifier requires the inspection record to match the PNG hash.

`godot/bake-render-validation.json` records application to all 133 meshes and 15 rendered camera views. A contact-sheet review shows continuous site coverage, but terminal exteriors are too dark and the overall palette remains strongly green. This is an initial composition review, not final seam/noise or route acceptance.

`tests/profile_garden.gd -- --baked` measures the actual playable scene with the existing nearest-four practical manager and static shadow maps disabled. The six desktop arrival views report 43–136 visible draw calls, median frame intervals 1.63–2.61 ms and 433,752,166 bytes (413.66 MiB) of texture memory. The latter exceeds the 64 MiB target. See `godot/profile-desktop-baked.json`. These results are from an Apple M2 Max, not a phone.

Next: reduce resident lightmap storage through measured resolution/compression/packing choices while checking image quality; finish the backdrop wash and dark terminal lighting; then rerender route views and profile again. Production adoption remains pending.

## Runtime compression comparison

Source PNGs remain at their original Cycles resolution and precision. `scripts/configure_lightmap_imports.py` configures only Godot's import settings (VRAM compression, runtime size limit, existing non-mipmapped filtering). Its default is now a 512-pixel cap; `--size-limit 0` restores full resolution and `--uncompressed` selects the baseline storage. Run the Godot editor import after changing settings. See the [Godot image import documentation](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_images.html) for platform compression and PNG precision limits. This Mac imports S3TC; the phone's texture format remains untested.

Measured texture memory for the complete experimental baked scene:

| Profile | Bytes | MiB | Evidence |
| --- | ---: | ---: | --- |
| Original uncompressed | 433,752,166 | 413.66 | Original full-bake measurement above |
| Compressed, full resolution | 93,403,779 | 89.08 | `godot/profile-desktop-baked-compressed-1024.json` |
| Compressed, 512-pixel cap | 43,596,419 | 41.58 | `godot/profile-desktop-baked-compressed-512.json` |

All six measured views still use 43–136 visible draw calls. The current `profile-desktop-baked.json` is the latest 512-pixel run; the named files preserve both compressed measurements.

The render comparison fixes water/fog time and captures the same 15 authored views for each profile. `scripts/compare_lightmap_renders.py` records differences in `godot/lightmap-compression-comparison.json`. The worst per-view mean channel error for the 512-pixel profile is 0.347/255; the worst per-view 99th percentile is 5/255, with at most 0.38% of pixels changing by more than 8 channel values. A full contact-sheet review and full-resolution pavilion comparison show the same composition and overall lighting. These image-wide numbers do not certify tiny islands, seams, moving-camera aliasing or final art quality.

The 512-pixel profile is the working experimental configuration. Dark terminal lighting, backdrop wash, mip/filtering quality during movement, route-view acceptance and actual mobile GPU tests remain before production adoption.

## Playable cameras and traversal

`render_entry_route.gd -- --baked --views-only` now captures all six playable arrival cameras; adding `--mobile` captures 390 × 844 portrait views. Their images were inspected as desktop and portrait contact sheets, with full-resolution terminal, gate and study checks. The terminal interior retains the screen, desk and window silhouette. Its site contract intentionally specifies black cells with CRT illumination, so the dark exterior overview is not by itself a reason to add broad fill light. The specified cyclorama spill/wash remains unfinished.

`render_baked_traversal.gd` completed ten actual physics legs: cell → gate → pavilion → water pavilion → island → water pavilion → pavilion → bulletin hall → pavilion → gate → cell. The result in `godot/baked-traversal-validation.json` verifies destinations, floor support and at most four active practicals, with 30 sampled frames in `docs/reference/baked-traversal/`. Contact-sheet inspection covered the first 27 samples; the final cell-approach sample was checked at full resolution. These samples do not establish continuous-motion aliasing quality or mobile GPU performance.

The scene still needs its specified light-linked backdrop wash and final site art before the final bake/production adoption. Further modelling will invalidate the source hash, so this bake remains a verified intermediate asset rather than a completed lighting deliverable.
