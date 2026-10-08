# Ouxiang working-scene adoption — 2026-10-08

The installed complete GLB is `be80374c`; saved authoring remains `9356f6ec`. The Ouxiang roof's secondary UV charts are corrected. All six fresh lighting phases passed, including all 124 ordinary receivers, shared wash and terminal spill. No old map was relabelled for the new source.

The isolated native review passed 37 phases. Cold reimport preserves geometry, cameras, collisions and markers; deliberate camera/collider/marker corruption and both missing-roof-policy controls reject. The explicit two-roof import uses lossless 512² RGB8 maps, no mipmaps, with exact source/UV guards. Other maps keep the 256px policy. Four framing captures retain their actual PNG dimensions: 1410×600, 390×844, 360×800 and 1080×1976. The last was requested as 1080×2340 but constrained by macOS; it is not a physical phone test.

Both native garden walks cover 14 rooms, 26 legs and 139 original PNGs each. Supported floor ray samples are 17,582 desktop and 17,581 portrait, with zero misses and at most four practical lamps. All captured original hashes are checked. The canonical Blender exporter reproduces all 16 GLBs byte for byte. A separate native inspection verifies the exact three approach render boxes and collision proxies in both saved authoring and stage library; this inspection does not repair them.

M2 Max stationary normal-route renderer allocation reaches 52,600,513 bytes (50.16 MiB), versus 52,517,225 bytes at the final arrival. Demo maximum is 43,512,435 bytes. Bound normal image data is 36,525,582 bytes. These figures do not prove phone, sustained performance, frame timing or release budgets.

Sixteen changed targets were installed with recoverable local backups. Eight production checks passed: import, source contract, full lighting with both roof flags, normal/demo wash, normal/demo terminal spill, and animated water/fog materials. Authoring, current runtime and canonical exporter code were not rewritten by adoption.

Selected original Ouxiang desktop, portrait and settled captures plus the moon composition were directly inspected; 14-site contact sheets were inspected for gross assembly. The roof is more consistent. Black paving rectangles, green-heavy materials and other final art remain visible and unaccepted. Full-resolution all-site art acceptance, the last six reference slots, current Android packaging/device and 2020 Adreno/sustained profiling, release and authenticated readings/history/AI/presence/social remain required.

Use `configure_lightmap_imports.py --size-limit 256 --imperial-lossless512 --ouxiang-lossless512` and `test_full_scene_lighting.gd -- --imperial-lossless512 --ouxiang-lossless512` for this source. Original logs, executed code, reports and captures are archived here. The evidence index records exact SHA256s; absolute scratch paths inside original reports are retained as executed provenance. This checkpoint does not complete the full Garden goal.
