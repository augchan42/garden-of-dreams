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
