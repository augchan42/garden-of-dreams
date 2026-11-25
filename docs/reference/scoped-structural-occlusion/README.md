# Structural culling: public views and CPU tradeoff — 2026-10-10

The culling optimization remains an isolated candidate. Production Godot files and the prepared, uninstalled Android APK `6bb60f68` are unchanged. The wider tests show fewer draw calls, additional CPU work, and an unresolved one-pixel discrepancy. This archive does not establish that the optimization should ship.

## Tests and results

The first candidate enabled five exact opaque source occluders throughout the main viewport. Two actual public-command walks followed cell → gate → pavilion → gate → cell at normal time and 60 Hz physics, once per desktop/portrait shape. Each walk checked 3,222 grounded centre rays, four correct arrival signals and 240 reveal frames. Camera poses were recorded every 30 physics ticks. The fixture also recorded all 37 public detail endpoints across fourteen rooms.

All 294 recorded-pose cases passed disabled/enabled/disabled-repeat image equality: 882 decoded PNGs with matching file and pixel hashes. Each shape includes 98 travel, eight reveal, four settled arrival and 37 detail cases. The candidate peaks at 146 global draws/171,675 primitives on desktop and 114/147,647 in portrait. These are fixed-clock replays of sampled poses, not continuous per-frame equality or full-garden traversal acceptance. Detail setup uses direct room positioning after the actual four-leg walk; it is not a public walk through all fourteen rooms.

The later isolated controller derives the same five resources but enables main-viewport culling only when at least one source mesh's world bounds intersects the camera frustum, with a conservative 0.05 m margin. It checks all source surfaces before creating any nodes: exact known opaque baked shader code, static opaque materials, valid triangle arrays, and balanced closed edge windings for a material with backface culling. Nine native controls pass, including transparency, growth, billboard, fade, object alpha, shader alpha, open backface geometry and a missing final mesh. Source triangle positions, index order and transforms remain intact; rejected configurations create no partial occluders. The normal-route integration test creates exactly five occluders and leaves reflection-viewport culling disabled.

The controller's actual four-leg desktop walk, measured by the current full-profile producer, peaks at 139 engine-wide draws and 163,083 primitives over 3,642 samples. Its frame-interval P95 is 18.324 ms, exceeding the 60 fps threshold. GPU-time counters are all zero and unavailable; process-monitor statistics are window observations, not per-frame CPU quantiles.

The controller replay passes 63 cases, then stops at `leg-2-frame-150`. One pixel at (779,259) changes from RGBA (54,35,18,255) to (54,35,17,255); the disabled repeat matches the first disabled capture exactly. The first fixture did not persist the failed pose before its assertion. A focused fresh walk records every return pose at ticks 140–160: all 21 cases/63 decoded images match, but these are new poses and cannot establish that the original discrepancy is resolved. The failed captures, log and executed source remain in this archive; no tolerance was relaxed. The controller has no completed 147-case desktop or portrait replay.

## CPU measurements

The actual controller was measured in nine automatic-render phases: disabled, enabled and disabled-repeat for each of three rooms, with 120 warm-up frames and 480 measured frames per phase. Host `ps` samples the owned process's aggregate user-plus-system CPU at phase markers, at 0.01 s resolution. Query timing and baseline variation are retained. No other owned graphics test or image verifier ran concurrently with this measurement.

| Room | Disabled → enabled draws | Enabled process CPU / mean disabled CPU | Disabled-repeat / first-disabled CPU |
| --- | --- | --- | --- |
| Cell | 160 → 46 | 1.424 | 0.881 |
| Gate | 155 → 77 | 1.645 | 0.986 |
| Pavilion | 135 → 135 | 1.069 | 1.058 |

Culling is inactive in all three pavilion phases. This single paired native diagnostic shows a CPU cost in the cell and gate; it does not establish target-device performance or GPU savings. The earlier always-enabled and first frustum prototypes are separate diagnostic controls, not measurements of the final controller. The first always-enabled terminal baseline may overlap an image verifier and is retained with that limitation. See `diagnostic-controls/` for their exact scripts and reports.

## Evidence and reproduction

`source-preservation.json` records all 1,561 tracked Godot files against base commit `eaebff566d2a43bb98105180404da247160ba7be`. Only the isolated copy's `entry_route.gd` differs, by adding the experimental controller after normal arrival. The production route is also archived separately. Canonical geometry, lighting, paintings, shaders, cameras, physics and UI code remain unchanged. Untracked source files are outside this comparison.

`archive-manifest.json` covers every published file except itself. Thirty representative PNGs are published, including all three failing captures. The complete 1,137 PNGs and five result files are retained locally in `.superpowers/sdd/2026-09-23-garden-completion/occlusion-views-20261010/final-scoped/images/`; their hashes appear in `full-image-backup-manifest.json`. Two candidate runtime sources are also covered by that backup manifest. The full PNG set is not included in this Git archive.

Use an isolated copy of the Godot project at the recorded base. For the first always-enabled walk fixture, copy `source/godot/tests/capture_occlusion_path_views.gd` into its tests directory while retaining the production route. Run native Godot with `--script res://tests/capture_occlusion_path_views.gd`, then repeat with `-- --mobile`. Run `verify_path_views.py --root PROJECT --output SUMMARY.json` with Python and Pillow to decode and verify all 882 PNGs.

For the scoped controller, copy the archived candidate route and controller, the full producer/counter dependencies and the scoped/guard/focused fixtures into the isolated project. Run the two `test_exact_occlusion_*.gd` scripts, then `capture_scoped_occlusion_views.gd`. Its assertion can stop on a changed pixel; the archived failed run was terminated after that assertion, with exit 143. Run `diagnose_scoped_return_pixels.gd` to retain nearby poses before evaluating their differences. The focused script's native completion message means captures completed, not that all pixels match; the offline verifier establishes that result.

The original report-key error (`draw_calls_ok`/`primitives_ok` instead of the producer's `draw_calls`/`primitives`) and its source/report are retained separately. The corrected run later encounters the visual discrepancy described above. The initial topology query used the wrong `grow_enabled` property; the corrected executed source queries `grow`. These failed diagnostics are not acceptance evidence.

For the exact CPU command, create the isolated fixture at `/tmp/garden-occlusion-views-20261010/godot`, copy `source/godot/tests/benchmark_occlusion_cpu.gd` into its `tests/` directory, and run `measure_cpu.py`; it launches and measures only its owned process. Run graphics fixtures and CPU measurements sequentially. `verify_scoped_diagnostics.py --root PROJECT --cpu CPU_JSON --output SUMMARY.json` verifies the archived 63 passing cases, the precise failed pixel, 21 focused cases, producer counters and nine CPU phases. Its success means this evidence of failure/tradeoff is verified; it does not approve the candidate.

Next steps are to persist complete pose state before any assertion, reproduce and isolate the pixel difference, compare CPU/GPU cost on an available physical device, and choose whether the draw savings justify adoption. Phone availability remains unanswered, so no device was installed, restarted or foregrounded. Protected Blender/Godot editors were not changed. Final art, five missing references, sustained/2020 Adreno budgets, release and services remain open. The full project goal remains active.
