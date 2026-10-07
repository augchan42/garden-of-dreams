# Rendering profile — 2026-09-23

Measured in Godot 4.7.2 Compatibility on Apple M2 Max, at 1410 × 600 with vsync disabled. Each stationary room view has 30 warm-up frames and 120 measured frame intervals. These are wall-clock intervals between rendered frames, not GPU timer measurements. Other desktop activity can affect the timings. This is not evidence for an Adreno phone or route-transition performance.

| View | Median ms | P95 ms | Draw-call counter max | No-shadow diagnostic | Active practicals |
| --- | ---: | ---: | ---: | ---: | ---: |
| ouxiang_xie | 3.35 | 4.48 | 466 | 43 | 2 |
| qinfang_ting | 4.48 | 5.49 | 793 | 94 | 4 |
| qiushuang_zhai | 4.21 | 7.17 | 434 | 52 | 0 |
| rockery_gate | 5.72 | 7.63 | 920 | 132 | 3 |
| terminal_room | 5.26 | 6.23 | 957 | 136 | 2 |
| ziling_zhou | 5.28 | 6.31 | 835 | 105 | 1 |

Texture memory reported by the renderer: 24.16 MiB. Buffer memory: 19.75 MiB. These cover the loaded assembly, not only the priority-1 rooms.

## Findings and next work

The draw-call counter exceeds the 150 target in every current view. Removing shadows only in a diagnostic run reduces it to 43–136. Production retains the hard architectural shadows: the next step is to bake the static keys and wash, then verify the result and repeat measurements. Turning shadows off is not the delivered solution.

The renderer's separate shadow draw counter reported zero even though disabling shadows changed the visible draw counter substantially. Treat that split as unreliable in this Compatibility run; the zero does not mean shadow work is absent. Counters are obtained through Godot's [RenderingServer API](https://docs.godotengine.org/en/4.5/classes/class_renderingserver.html), not inferred from mesh counts.

The command-driven runtime now limits eligible lantern/CRT OmniLight3D nodes to the nearest four within 12 m of the visitor, updated every 0.2 seconds. Practical shadows are disabled. Emissive materials remain visible and zero-energy cell lights remain off. Static key/spot lights are still dynamic pending baking, so the complete lighting budget is not yet met.

`test_practical_lights.gd` checks selection and the four-light limit at five locations. `profile_garden.gd` writes the current baseline to `godot/profile-desktop.json`. Diagnostic flags `--no-shadows` and `--no-lights` modify only the running test scene, with separately named reports. `--portrait` changes the window dimensions; it does not emulate a phone GPU.


## Three-key source pass — 2026-10-07

The current demo source is `d74e0ff858748d529029c80f0ea11969c121dd71f645effebf55180104099bde`. After all 124 ordinary maps and the wash were refreshed, the stationary 1410 × 600 M2 Max demo profile retains a maximum of 146 draws, 177,088 primitives, four practicals and 57,817,992 texture bytes. Forced-draw medians are 1.705–2.176 ms and p95 5.335–5.641 ms. The Western route passes collision traversal in both directions; that is a physics check, not continuous GPU profiling. The earlier pond and all-site arrival profiles are historical measurements. Current full traversal and target-phone GPU acceptance remain open. Evidence: `export/site-key-runtime-checks.json` and `godot/demo-profile-desktop.json`.


## Native terminal spill pass — 2026-10-07

Seven compressed 256px indirect maps raise stationary demo texture allocation to 58,123,920 bytes (55.43 MiB), an increase of 305,928 bytes. Current cell/gate/pavilion views retain 146/140/102 maximum draws, 177,088/143,452/123,740 primitives and two/three/four practicals. Forced-draw median intervals are 2.720/2.106/1.833 ms, with p95 6.271/3.960/4.033 ms on this M2 Max at 1410 × 600.

`godot/demo-profile-desktop.json` records canonical GLB, terminal-spill manifest and shader hashes for this run; `export/terminal-spill-runtime-checks.json` ties those to the final tested pack and movie. The earlier pond/all-site profiles remain historical evidence. This pass does not establish final texture-memory acceptance for the entire garden, moving-camera performance or target-phone GPU behavior.
