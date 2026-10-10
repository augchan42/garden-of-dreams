# Engine-wide frame budgets — 2026-10-10

The full-phone profiler previously gated draws and primitives on the main viewport's visible pass. Reflection-only controls exposed false passes: 1 main-view draw versus 152 engine-wide draws, and 12 main-view primitives versus 321,614 engine-wide primitives. The producer now records `global_draw_calls_max` and `global_primitives_max` and uses them for the 150/300,000 limits. Root-visible fields remain diagnostics. These are maxima of actual per-frame engine totals, not sums of independent viewport maxima.

The full report declares `render_budget_scope="engine_global_all_viewports"`. Collection rejects missing scope/counters, noninteger counts, totals below root-visible maxima and inconsistent budget flags. A measured failure remains collectable with its failure flag; collection does not convert it into acceptance. Producer/dependency pins require a fresh build; earlier 735bf87b and 9dde9d29 APKs are historical for this collector.

## Verification

All 26 Python tests pass. The new regression failed before the correction; its final native run passes five controls using the actual producer: reflection disabled, reflection-only draw overrun, reflection-only primitive overrun, reflection disabled again, and one canvas rectangle. Existing actual producer pause/focus, two-tour/600-second and frame-cost disabled/unavailable tests pass. Expected rejection messages in `checks/pause.log` are deliberate negative controls.

On native Godot 4.7.2 Compatibility on Apple M2 Max, the canvas rectangle adds 1 global draw and 2 global primitives while root-visible 3D counts remain unchanged. The fields therefore say engine-global rather than 3D-only. The [RenderingServer API](https://docs.godotengine.org/en/4.7/classes/class_renderingserver.html#class-renderingserver-method-get-rendering-info) distinguishes global and per-viewport statistics, but its 3D-only note does not match this observed native canvas control. These counters describe work exposed by this renderer; they are not a complete GPU-command or GPU-time trace. All-zero GLES GPU-time counters remain unavailable.

## Actual garden arrivals

Both native shapes run the installed normal fourteen-room route and the actual full producer in an isolated copy. Each arrival settles, warms up 20 frames, then samples 30 frames. Draws are explicitly scheduled to make native diagnostics reproducible; the retained frame intervals/CPU monitors do not establish 60 fps, sustained or phone performance. These static `_arrive` views do not establish moving-tour floor support. Desktop is 1410×600; portrait is 390×844.

| Room | Desktop root / global draws | Portrait root / global draws | Maximum global primitives across shapes |
| --- | ---: | ---: | ---: |
| aojing_guan | 89 / 118 | 51 / 79 | 125,885 |
| daguan_lou | 51 / 65 | 35 / 49 | 117,925 |
| daoxiang_cun | 20 / 38 | 21 / 39 | 60,993 |
| hengwu_yuan | 109 / 129 | 94 / 114 | 133,391 |
| longcui_an | 29 / 45 | 22 / 38 | 75,751 |
| ouxiang_xie | 58 / 76 | 47 / 65 | 125,827 |
| qinfang_ting | 103 / 135 | 48 / 74 | 147,217 |
| qiushuang_zhai | 41 / 61 | 33 / 53 | 97,207 |
| rockery_gate | 141 / 155 | 99 / 113 | 165,311 |
| terminal_room | 147 / 160 | 74 / 87 | 199,017 |
| tubi_tang | 42 / 58 | 35 / 51 | 103,807 |
| xiaoxiang_guan | 73 / 89 | 56 / 72 | 123,877 |
| yihong_yuan | 32 / 56 | 24 / 49 | 75,231 |
| ziling_zhou | 110 / 124 | 95 / 109 | 155,537 |

Desktop terminal 160 and gate 155 exceed 150; all portrait arrivals remain within 150. All 28 arrival primitive totals remain below 300,000. The failed desktop limits remain open optimization work. No scene, source painting, baked map, shader or product camera has changed in this branch. Source GLB remains `faa8a7fe4a7a399899e84373c0550c8ff2f5f15ab0273109e8ea68f433b8fe0f`.

## Prepared Android diagnostic

The final uninstalled full debug APK is `6bb60f6826d6af89d3db8f020fecd357effa937156ce5654ffb2183b507b2952`, 86,531,491 bytes. Four build phases pass without engine diagnostics. Offline collection preflight validates current/staged source and finalized inputs, then stops before the first device call. Actual APK inspection verifies 7 compiled diagnostic dependencies, the imported scene and 194 exported texture payloads against their staged caches; the preceding 177 normal bound payloads remain byte-identical. The APK is at `/private/tmp/garden-viewport-budget-20261010/garden-all-viewport-full.apk`; build reports retain its isolated staging path. Android installation, actual counter behavior and uninterrupted two-tour/600-second evidence are pending phone availability. No ADB call was made for this checkpoint.

Reproduce the native controls and diagnostics in an isolated copy with `--script res://tests/test_android_full_render_budget.gd` and `--script res://tests/profile_all_viewport_budgets.gd` (append `-- --mobile` for portrait). Build with `python3 scripts/build_android_profile.py --mode full --report PATH --apk PATH`; verify the artifact using the retained `android/verify_artifact.py --project PROJECT --build REPORT --output JSON`.

Final fourteen-site art, five missing exact external-reference slots (37/42), current physical-phone and 2020 Adreno/sustained budgets, release and authenticated reading/history/AI/presence/social remain required. This is profiling progress; the full goal remains active. PR #22's GitGuardian finding remains user-owned and unresolved, so the dependency stack is unmerged.
