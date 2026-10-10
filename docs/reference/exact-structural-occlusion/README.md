# Exact structural occluder candidate — 2026-10-10

This is an isolated optimization candidate, not an installed change. The production scene still exceeds the 150-draw desktop limit at the terminal and rockery gate. The current prepared Android APK 6bb60f68 does not contain these occluders.

Five exact opaque structural meshes are converted to ArrayOccluder3D resources in a copy of the normal route: terminal plaster floor, cell backstage walls, terminal stage backstage, gate pavilion structure and gate plaster rock. Duplicate positions are merged exactly; triangle indices and mesh transforms are preserved. No source surface is simplified, expanded, closed or replaced by collision geometry. The guard accepts the current baked diffuse shader or a BaseMaterial3D with transparency disabled. The main viewport enables culling for the candidate; the pond reflection viewport remains unchanged.

At each of fourteen room arrivals, the candidate captures culling disabled, enabled and disabled again. Water/fog shaders use a fixed clock. Sixty warm-up frames move the camera by at most 0.0001 world units; its exact original transform is restored before capture. Each capture requires at least twenty actual Engine.get_frames_drawn() advances. The comparison checks decoded RGBA pixels, PNG hashes, baseline repeat counts and global RenderingServer draws/primitives. These are stationary native counter observations, not frame-rate measurements or a moving-camera test.

The desktop terminal measures 160 → 46 draws and the gate 155 → 77. Desktop arrival images remain byte-identical; the other twelve desktop arrivals have unchanged counts. The renderer is Godot 4.7.2 Compatibility on Apple M2 Max. All 28 desktop/portrait arrival cases pass the pixel comparison and candidate draw/primitive limits; all 84 PNG files are decoded and verified. Portrait terminal and gate results are listed in comparison.json. The remaining twelve portrait arrival counts are unchanged.

All 1,561 tracked Godot files in the isolated copy match production commit 214496ff, including source geometry, paintings, lighting, runtime, shaders, cameras and test dependencies. Only isolated diagnostic scripts and results are added. This does not verify untracked files. Protected editors and the phone were not changed.

## Rejected and diagnostic controls

The first candidate used only the terminal plaster floor and gate plaster rock. It did not save draws. Early explicit-force-draw runs also held the actual render-frame counter at 57, so those runs cannot establish culling behavior. The corrected two-room run advances 61 render frames per capture and still shows no savings from that limited candidate. Adding the actual cell walls and gate structure produces the savings above. The synthetic box control changes 51 → 1 → 51 draws with advancing render frames, confirming culling works on this renderer.

The initial material assertion required the baked shader for every occluder and correctly stopped at the terminal stage backstage, which uses an opaque StandardMaterial3D. The final guard verifies that material's transparency mode instead. The failed log and executed sources are retained. Godot's [occlusion timer implementation](https://github.com/godotengine/godot/blob/4.7.2-stable/servers/rendering/renderer_scene_occlusion_cull.cpp#L112) reads the engine render-frame counter; an explicit force_draw call alone does not establish that the counter advanced.

## Reproduction and remaining work

Copy the installed godot directory to an isolated location. Place source/diagnose_solid_occlusion.gd under its tests directory, run Godot with --script res://tests/diagnose_solid_occlusion.gd, then repeat with -- --mobile. Run verify_comparison.py --root PROJECT --output SUMMARY.json with Python and Pillow. Do not run the fixture against a user's live editor project; it creates candidate nodes and diagnostic files.

Before adoption, check public detail views, cell/gate travel and reveal cameras, the actual full producer and CPU cost. Add a runtime material/geometry guard and packaging provenance if the candidate passes those checks. Android, sustained performance, final art and the full project goal remain pending. This archive is progress toward the failed draw budgets; it grants none of those acceptances.
