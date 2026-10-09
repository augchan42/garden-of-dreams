# Garden completion implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the garden's site requirements and a working command-driven entry route, then connect its room interactions and verify rendering and performance.
**Architecture:** Keep Blender site libraries and GLB exports as scene assets. Godot owns movement, camera rails, command UI and room state; data adapters own external divination, news and presence. A playable route is the first milestone, not completion of the whole goal.
**Tech Stack:** Blender 5.2, Godot 4.7.2 Standard, GDScript, glTF 2.0.
**Spec:** docs/garden-scene-spec.md; docs/sites/*.md; original design at ../8bitoracle-next/docs/ideas/garden-of-dreams.md.

## Global constraints

- Metres, source Z-up, glTF Y-up. No rigged character required.
- 2.35:1 camera framing; fixed rails rather than free look.
- Click/tap commands with optional typed commands. AI-driven decisions require an actual service integration; do not misrepresent local authored responses as AI output.
- Neutral wood/plaster/slate with amber practicals and selective green CRT/gel accents, following the user's reduced-green revision; retain visible architectural detail.
- 300k visible triangles and 150 draw-call targets require measured engine evidence, not mesh-count inference.
- Keep game logic out of Blender assets. Room markers retain room_id.

## Task 1: Command-driven entry route
Files: godot/runtime/entry_route.gd, godot/runtime/entry_route.tscn, godot/tests/test_entry_route.gd, godot/project.godot.
Interfaces: room_id, execute_command(text), transition_finished(room_id), player CharacterBody3D, camera Camera3D. UI buttons and typed input share one dispatcher.
- [x] Test missing route scene and initial terminal_room state.
- [x] Add room descriptions, contextual actions, optional command input and a status line.
- [x] Add collision-aware movement between the cell, gate and pavilion; stop rather than teleport on obstruction.
- [x] Animate fixed cameras during travel; frame the pavilion at arrival.
- [x] Test both directions using actual physics, command rejection during travel, unsupported commands, and no falling through floors.
- [x] Inspect the running scene visually at each location and at mobile window sizes.

## Task 2: Site contracts and art completion
Files: docs/sites/*.md, Blender site libraries, source scripts and GLB exports.
- [x] Expand the 11 short site sheets to specific asset, lighting, camera and trigger contracts.
- [ ] Collect three references per site with source attribution.
- [ ] Complete missing kit variants and distinctive later-site architecture.
- [ ] Replace temporary typeset signage with painted decals; refine foliage and pierced rockery.
- [x] Fix the tunnel reveal geometry/camera relationship and export both hexagram variants.
- [ ] Render and inspect every site against its contract.

## Task 3: Godot rendering
Files: godot/garden_import.gd, materials and shaders, export/lightmaps, grade/tech-noir.cube.
- [x] Bake lighting with matching secondary UVs and verify PNG maps in engine.
- [x] Add animated water and scrolling floor fog; verify separate fixed-clock render differences.
- [x] Apply and verify the consistent in-engine grade (rendered color grid versus source cube; UI unchanged).
- [ ] Complete atlases and final texture-memory audit.
- [x] Limit realtime practicals to four nearby lamps; verify selection in runtime tests.
- [x] Verify that reimport retains lighting, material, collision and camera behavior.

## Task 4: Room interactions and data
Files: Godot runtime room controllers, content resources and service adapters.
- [x] Inspect the public topic schema and deployed origin; connect read-only topics.
- [ ] Finish reading/history authentication and write-contract audit before connecting actual readings.
- [ ] Personal terminal/history, pavilion feed, bulletin board and room transitions.
- [ ] Distinguish offline/local content from live data; handle service unavailability.
- [ ] Integrate AI movement decisions through validated room connections and state changes.
- [ ] Add social/news/group functionality only against verified available services; document unresolved dependencies.

## Task 5: Acceptance
- [x] Automated traversal of collision routes and command/state behavior.
- [ ] Visual check of all rooms, UI and camera transitions.
- [x] Measure desktop arrival-view draw calls, frame intervals and memory; record failed budgets.
- [ ] Meet rendering budgets and complete target-device/mobile and traversal profiling.
- [ ] Update build-status with evidence, preserving any unresolved requirements.
- [ ] Complete the goal only after all accepted requirements are verified.

Current evidence (2026-10-08): installed GLB `be80374c`, authoring `9356f6ec`, has the verified Ouxiang and imperial roof UV2 charts with complete fresh matching six-phase lighting. All37 native candidate phases, both fourteen-room/26-leg walks, default byte equality for all16GLBs and eight post-install checks pass. Actual stationary M2 Max normal-route texture allocation peaks at52,600,513bytes (50.16MiB), final52,517,225; phone/sustained budgets remain unaccepted. See `ouxiang-full-lighting-evidence.json`. Named original captures show more consistent Ouxiang roof shading; paving rectangles, green-heavy materials and final site art/framing remain open. Reference coverage36/42 leaves six slots missing. Current Android/device/2020Adreno/release and authenticated services remain required.


Pending candidate evidence (2026-10-09): paving/plain colors `5ae484f9` has six completed source phases and 37 passed native phases, both full walks with no floor-ray misses, and partial named visual review. Combined architectural colors are now saved as authoring `3a3ae253` / export `59de1ca2`; complete/site export preservation and portable libraries pass. Fresh lighting is running and a 42-phase native review, including palette-transfer controls, is queued. The new GDScript is not yet executed. Neither candidate is adopted; installed source remains `be80374c`. Full art, six references, target devices/sustained/release and services scope remains required.

Later checkpoint (2026-10-09): `59de1ca2` / authoring `3a3ae253` is now installed after six source phases, all 42 native phases, exact default reproduction of all sixteen GLBs, selected visual inspection and ten production checks. Both full walks have no floor-ray misses. See `neutral-atlas-full-lighting-evidence.json`, `neutral-atlas-native-review-evidence.json` and `neutral-atlas-working-adoption-evidence.json`. All fourteen intermediate-source desktop/portrait arrivals were inspected for remaining art. Twelve actual camera-only comparisons for three sites are recorded but not installed; action/resize/authored-camera acceptance is pending. Final art/framing, six references, standalone kit palettes, current target devices/sustained/release and authenticated services remain open.

Standalone kit checkpoint (2026-10-09): all four architectural kit libraries, 48 variant/LOD exports, eight aliases and matching Godot assets now share the installed neutral palette. Saved-source baseline reproduction, expanded export preservation, eleven unwanted-change controls, native decoded/PBR/physics checks and ten production checks pass. Four inspected galleries match the installed captures exactly. Evidence: `standalone-kit-neutral-palette-evidence.json`. Assembled source/lighting/runtime remain unchanged. Final site art/framing, six references, target-device/sustained/release and authenticated service requirements remain open.

## Completed checkpoint: three portrait overviews — 2026-10-09

Daoxiang, Daguan and Longcui have reviewed adaptive portrait camera poses, public Look restoration and resize behavior that preserves details/text. The final nunnery angle retains its specified slight off-axis composition. A focused 13-error regression now passes; seven existing regressions and both complete 14-room/26-leg native walks pass, with zero floor-support misses. Cold import and unchanged runtime/source hashes were checked. Source geometry, saved Blender cameras and lighting are retained. See `../../reference/portrait-architecture-runtime/README.md` for original captures, code, reports and scope. Final all-site art, remaining references, device/sustained budgets, release and services are not complete.

## Prepared checkpoint: Hengwu foreground stone — 2026-10-09

The separate compact-stone candidate has saved/reopened source preservation, controlled complete/site exports, native surface identity, unbaked arrival/action comparisons and real adjacent-route/capsule checks. Fifteen site libraries and portable shared-light receiver master are prepared. Full matching six-phase lighting is running for that source; source agreement, complete rendered review and recoverable adoption remain required. No production geometry or camera changed. See `../../reference/hengwu-rock-preparation/README.md`. Full goal scope remains unchanged.

Reference checkpoint (2026-10-09): rockery slot 3 is collected with original JPEG, direct visual review and project-level attribution. Coverage is 37/42; five specified references remain. Immutable collection-time source/coverage snapshots are indexed by `moon-gate-reference-evidence.json`. Hengwu matching lighting/native review and all other scene, device, release and service requirements remain open.

Hengwu checkpoint (2026-10-09): complete fresh six-phase source lighting and 141 source PNGs are archived with all 240 frozen inputs. Native reimport/lighting/source library/default-sixteen-export checks pass. A real camera-wait regression changed from five portrait failures/six incomplete action poses to fifteen zero-error portrait captures/nine exact completed Hengwu poses. Runtime is unchanged; tests wait for tween completion rather than assuming rendered frames equal elapsed animation time. Full walks/palette checks and adoption remain separate; final all-site art, five references, devices/release/services remain required.


### Hengwu adoption checkpoint — 2026-10-09

Completed: compact nearest stone and floor-anchored collision, matching full source lighting, 47 review checks with seven intended negative controls, sixteen exact default GLB reexports, both full fourteen-room native walks, checked backups and eleven tests on the installed project. Current source `26033c99` / authoring `19eb386d`. Evidence: `../../reference/hengwu-native-review/README.md` and `../../../export/hengwu-native-review-evidence.json`.

Remaining: final art/framing across the fourteen sites, including Hengwu wall-cap/roof/close-view composition; five reference slots (37/42 collected); current physical-phone/2020 Adreno and sustained budgets; release; authenticated reading/history/AI/presence/social flows. Do not mark the full goal complete from this checkpoint.


### Hengwu portrait-action checkpoint — 2026-10-09

Completed: portrait stone/book fits, selection/text preservation on resize, original desktop camera restoration on rotation, Look returning to overview, and a 128-unit scroll area with 48-unit touch targets. Three final native graphical modes pass with thirty original captures; ten adjacent import/source/route/UI/camera/demo regressions pass. Source and lighting are unchanged. The archive retains 174 original PNGs and 269 checked files, including actual failed actions, rejected occluded comparisons and an unexplained native command timeout. Evidence: `../../reference/hengwu-detail-framing/README.md` and `../../../export/hengwu-detail-framing-evidence.json`.

Remaining: final art across fourteen sites, including Hengwu arrival wall-cap/roof/facade work; five reference slots; current physical-phone/2020 Adreno and sustained budgets; release; authenticated service flows. The preceding full walks tested the previous runtime. These desktop density checks do not establish phone acceptance. Keep the full goal active.


### Tubi portrait and overlook checkpoint — 2026-10-09

Completed focused work: full portrait moon/hall/stair fits, a higher bridge-pavilion overlook, selected-view/text preservation on resize, original desktop arrival restoration, Look returning to arrival, and a stable 128-unit scroll reserve with 48-unit touch actions. Three final native modes pass with thirty original captures; thirteen adjacent regressions, including actual climb/descent and study routes, pass. The evidence archive contains 215 originals and 312 checked files. Original public-action RED29 and later density RED2 remain archived. Seven final originals were directly inspected. The saved authoring/source and all matching lighting bytes are unchanged. Final adjacent regression evidence: `../../reference/tubi-portrait-framing/README.md` and `../../../export/tubi-portrait-framing-evidence.json`.

Remaining: final art across fourteen sites, including stage/background closure, surface and foliage refinement; five references; current physical-phone/2020 Adreno and sustained budgets; release; authenticated services. No new complete fourteen-room walk or physical-phone test is claimed for this camera update. Keep the full goal active.


### Qiushuang screen-framing checkpoint — 2026-10-09

Completed focused work: portrait facade and all three public four-monitor bank views; selected-bank/text preservation on resize; original desktop poses on rotation; Look restoring the overview; stable 128-unit portrait action area, 48-unit touch targets and final-action scroll reachability. Three final graphical modes pass with 54 originals; fourteen adjacent regressions pass, including actual bulletin approach/return and hilltop climb/descent. All 273 originals and 352 checked files are preserved, including the RED22 baseline, failed first comparison and rejected later compositions. Eight final originals were directly inspected. Source and all matching lighting bytes are unchanged. Evidence: `../../reference/qiushuang-screen-framing/README.md` and `../../../export/qiushuang-screen-framing-evidence.json`.

Remaining: final art across fourteen sites, including lattice/text intersections, facade lighting, ground/background closure and foliage/surface refinement; five references; current physical-phone/2020 Adreno and sustained budgets; release; authenticated services. No new full fourteen-room walk or physical-phone acceptance is claimed for this camera update. Keep the full goal active.


### Neutral water and atmosphere checkpoint — 2026-10-09

Completed focused work: slate-blue stream water, neutral ambient fill, blue-gray distance fog and equal-channel pond reflection tint. The existing neutral live stage fog is unchanged. Eleven native phases pass; all 28 installed desktop/portrait arrival originals were directly inspected. Separate actual attached-material clocks verify water/fog motion, and pond controls verify window geometry/strength/ripples. The immutable archive retains 201 original PNGs and 276 checked files, including preliminary and failed attempts. Eight legacy-fog negative controls have exactly equal decoded pixels. Evidence: `../../reference/neutral-water-runtime/README.md` and `../../../export/neutral-water-runtime-evidence.json`. Source `26033c99`, authoring `19eb386d`, runtime route `6c80b98a` and all 282 matching lightmaps are unchanged.

Remaining: final source/material parity and art across fourteen sites, including Ziling bridge/island framing, coarse foliage and stage/ground/backdrop closure; five reference slots; current physical-phone/2020 Adreno and sustained budgets; release and authenticated services. This palette update does not claim a new complete moving walk or phone acceptance. Android packages are stale. Keep the full goal active.


### Ziling portrait-framing checkpoint — 2026-10-09

Completed focused work: complete island/footbridge/reed/pavilion-roof portrait fits, Watch the reeds text preservation on resize/rotation, original desktop camera restoration, Look text restoration, visitor invariants and touch48/final return-action reachability. The actual baseline failed 50 assertions; three final native modes pass with thirty originals. Ten adjacent source/import/western route/UI/pond and camera regressions pass. Eight final originals were directly inspected. Evidence preserves all 161 originals and 248 checked files, including lower-LOD-only and rejected earlier camera proposals: `../../reference/ziling-portrait-framing/README.md` and `../../../export/ziling-portrait-framing-evidence.json`. Runtime `ba6410c0`; authoring `19eb386d`, both complete GLBs `26033c99`, all 282 lightmap PNGs and the installed palette are unchanged. Site-sheet coverage was refreshed after the final Ziling sheet edit and remains 37/42.

Remaining: final art across fourteen sites, particularly Ziling island waterline/sides, reeds/lotus, stream/stage boundaries and final desktop composition; five references; current physical-phone/2020 Adreno and sustained budgets; release and authenticated service flows. No new full moving tour, physical-phone or final-art acceptance is claimed. Android packages are stale. Keep the full goal active.
