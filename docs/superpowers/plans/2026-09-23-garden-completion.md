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

2026-10-10 phone diagnostic publication: the dedicated profiler now publishes
closed JSON replacements by same-directory rename. Actual producer RED321
incomplete reads became GREEN0; Pixel7Pro completed 479 reads with zero partial
reports and all five real touch stages without reader retries. Nine Python
tests and fresh APK/177 bound-import checks pass. Sampled memory is60.34MiB;
P9519.948–34.535ms still misses60fps. This does not close Task5: rendering
budgets,2020Adreno,final art,remaining five references,release and authenticated
services remain required. Evidence:
[reports and originals](../../reference/android-profile-publication/README.md).

2026-10-10 full normal-phone baseline: an isolated current-source Pixel 7 Pro
APK completed two whole tours, 52 public-command legs and 735.865 timed seconds.
All fourteen rooms passed floor, arrival and control checks; 35,118 grounded
rays had zero misses. All 53 original captures were hash/dimension checked;
fourteen distinct arrivals were directly inspected. Report publication remained
complete across 448 reads. Texture allocation peaked at 68.62 MiB and every
phase exceeded the 60 fps frame-interval limit; draw calls, primitives and
practical lights passed. This records failed sustained budgets, not acceptance.
The full profiling prototype is not integrated into production tools. Full-tour
touch interaction, 2020 Adreno hardware and the other Task5 requirements remain
open. Evidence: [full phone baseline](../../reference/full-garden-phone-baseline/README.md).

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

## Source-art checkpoint — 2026-10-09

Installed source `1380ceca` raises stream/lotus waterline, synchronizes neutral saved-water/kit palettes and replaces ten reed clumps with curved tapered leaves and radial plume volumes. All camera/collision/marker contracts are preserved. Six complete source bake phases, thirty-nine completed isolated review phases, two fourteen-room rendered tours and thirteen installed checks pass. The earlier collider re-export failure, architecture runner marker mismatch and installed resize timeout/rollback remain preserved; no assertion was removed. Current references remain 37/42.

The full goal remains active. Next scene work: improve Ziling's retained desktop composition and bank/lotus treatment, then complete remaining per-site materials, stage/ground/background closure and action views. Physical-phone/current-package performance and authenticated services remain separate required work. No site is declared final from these checks. Evidence: `../../reference/ziling-source-art/README.md`.


## Ziling desktop framing checkpoint — 2026-10-09

The reed island now remains clear of the desktop controls. A low 55° view moves back smoothly with shorter landscape height; portrait framing is retained. Native normal/touch/density checks pass with 35 originals, including 480/540/600/720 desktop heights, public Look/Watch the reeds, resizing/rotation, description/visitor preservation and touch48/return access. Thirteen installed originals reproduce the fixture exactly, and the supported western round trip passes with four directly reviewed native arrivals. The capture test now subscribes before forcing a draw, retaining its 100-second deadline and assertions; rejected fit controls and two capture timeouts are retained.

Source `1380ceca`, authoring `0d3e84e3` and matching lightmaps are retained. This is camera progress; bank/lotus/foliage and final fourteen-site art, five references, physical devices/sustained budgets, release and authenticated services remain open. Evidence: [originals and reports](../../reference/ziling-desktop-framing/README.md).


## Stream banks and closed lotus checkpoint — 2026-10-09

Installed source `7a9fc523` and authoring `074ab201` add 54 stock embankment modules/colliders and closed shallow lotus leaves above the raised stream. All 42 cameras,400 earlier colliders,71 markers and runtime are preserved;167 render meshes now contain 266336 triangles. The saved water kit and canonical generator match the 864/360 lotus pair; all ten other modules remain byte-exact. Complete fresh 141 PNG lighting, six source phases,36 completed isolated checks, both 14-location/26-leg tours and 15 installed checks pass. All 19 installed water-edge/Ziling originals match the isolated bytes. Evidence: `../../reference/water-edge-source/README.md` and `../../../export/water-edge-source-evidence.json`. All 14 sheets are updated; references remain 37/42.

Next scene work: dark bank/island faces and stage/ground/background closure, then remaining per-site materials and action views. Final 14-site art, five missing references, current phones/2020 Adreno/sustained budgets, release and authenticated services remain required. Mac capture/allocation checks do not establish phone acceptance. This scene branch starts from main and does not include PR 14’s Records storage or change its pending security approval. Keep the full goal active.


## Reed island exterior repair — 2026-10-09

Current complete source is `73267e2b`; authoring is `2b07ce48`. The 24 island side quads now have outward normals and consistent shell winding. Shape, heights, material, all 42 cameras,454 colliders,71 markers,266336 render triangles and runtime are preserved. Fourteen other site GLBs remain byte-exact; the constructor reproduces the corrected face order. Fresh lightmaps show the stone sides in both desktop and portrait views.

Six complete source phases,25 focused native checks and13 installed checks pass. The 141 source PNGs match engine copies;47 isolated originals have verified hashes/dimensions,12 were directly inspected, and all19 installed lit/Ziling originals reproduce the candidate exactly. The archive preserves153 checked files, with760 installed-file hashes in `export/island-exterior-winding-evidence.json`. Evidence: [executed checks and original renders](../../reference/island-exterior-winding/README.md).

This is focused repair acceptance. Broad stage canvas retains its original green color and will be addressed next; bank sides, ground/water boundaries, signage, foliage and final fourteen-site art remain. Existing PR15 full tours qualify the previous source. No current phone,2020 Adreno,sustained or release acceptance is claimed. References remain37/42; authenticated services remain open and PR14 stays independently held for security approval. The full goal remains active.


## Neutral stage floor — 2026-10-09

The saved canvas base changes from green (.055,.095,.037) to muted warm gray (.065,.060,.055), with all 4,467 objects, 47 other materials and 621 exported mesh attributes preserved. Fourteen other site GLBs remain byte-exact. Current source `c9d4fb30`, authoring `43d7e33e` and runtime `80f64655` are recorded in `export/stage-floor-palette-evidence.json`.

Six source phases refresh 141 lightmaps. Forty native phases pass: 38 positive checks and two expected base-color rejection controls. Saved default exports reproduce 16 GLBs exactly. Both desktop and portrait tours visit 14 rooms across 26 legs, with zero unsupported floor rays and at most four practicals. All 409 review PNGs are hashed and dimension-checked; 52 original files were directly inspected. Fifteen installed checks pass, with 47 installed originals matching the review exactly. Evidence: [neutral stage floor](../../reference/stage-floor-palette/README.md).

Final art remains open, including red-court/imperial portrait composition, Hengwu arrival composition, ground/water closure, foliage and signage. Five reference slots remain (37/42 collected). Current physical phones, 2020 Adreno/sustained budgets, release and authenticated services still require work. The Android package is stale. PR14 remains separately held for security approval. The full goal remains active.


## Courtyard and imperial portrait cameras — 2026-10-10

Runtime `7970380d` fits the courtyard facade, doors and primary banana plant above portrait controls, restores the overview through Look and preserves selected details through rotation. Original desktop poses return correctly; touch actions remain scrollable. The imperial portrait overview gives the facade more usable height while retaining the roof tiers, moon and closed doors. Source `c9d4fb30`, authoring `43d7e33e`, geometry and all141 lighting PNGs remain unchanged.

Positioned courtyard RED20 and imperial RED6 precede32 passing full native checks and three repeated architecture modes after a test-only foliage wait correction. Both actual Mac tours visit14 rooms over26 legs with zero unsupported floor samples and at most four practicals. The452 full-run originals and25 repeated architecture originals are hashed and dimension-checked;25 full-run original file paths and the repeated nunnery original were directly inspected. Twenty-four repeated architecture images reproduce their full-run counterparts exactly. Eleven installed checks pass, and all98 installed camera/arrival images reproduce the reviewed candidate exactly. Evidence: [camera checks and original images](../../reference/courtyard-portrait-framing/README.md).

This is two-room camera acceptance. Hengwu composition, stage seams, dark shading, ground/water closure, foliage, signage and final14-site art remain open. Reference coverage remains37/42; current phones,2020 Adreno/sustained budgets, release and authenticated services remain required. The full goal remains active.


## Paving joins — 2026-10-10

Current source `ba40866e` / authoring `7eba169a` removes 84 positive coplanar paving overlaps by partitioning 26 render objects. The original floor footprint is retained within 10 micrometres; all collision geometry, 42 cameras, 71 markers, materials and runtime `7970380d` are preserved. Render geometry is 266,533 triangles. Eight other site exports remain byte-exact. The nunnery's black forecourt rectangle is replaced by continuous stone and plum shadows.

Six source phases regenerate 141 lighting PNGs. The 45-phase native review has 44 positive passes and one intended baseline-floor rejection. Both actual Mac tours visit 14 rooms over 26 legs with no unsupported floor samples and at most four practical lights. Three Ziling modes are repeated after a test-only real 250-millisecond foliage wait; runtime LOD remains enabled. All 28 arrivals, eight moving samples, eight matched floor controls and 35 repeated reed captures were directly inspected: 79 distinct original paths.

Twenty-two installed checks pass. All 85 installed camera/floor/arrival originals reproduce the reviewed files exactly. The first installation also passed all 22 native checks, then rolled back all 29 targets after a report-field comparison error; its 85 originals match independently. The corrected helper reads actual PNG dimensions. Failed source, native and installation attempts are retained in the evidence archive.

This closes the duplicate paving defect. Hengwu's arrival view is next: show its table and pierced stones while preserving the accepted detail actions. Final fourteen-site art, five missing references (37/42), current phones, 2020 Adreno and sustained budgets, release and authenticated reading/history/AI/presence/social remain open. Evidence: [paving checks and originals](../../reference/paving-surface-joins/README.md). The full goal remains active.


## Engine-wide frame-budget correction — 2026-10-10

The full-phone producer and collector now gate draws/primitives on actual engine-wide per-frame counters, including the pond capture, while retaining main-view visible counts as diagnostics. Native controls exposed and now reject reflection-only overruns; disabling the capture again resets the sample, and a UI rectangle establishes the observed renderer scope. All 26 Python tests and four native regression programs pass. All 28 stationary native arrival samples are retained: desktop terminal 160 and gate 155 exceed the 150-draw limit; portrait arrivals and all primitive totals pass their respective limits. These are static counter diagnostics, not sustained or physical-phone acceptance.

The fresh full debug APK is `6bb60f68` (86,531,491 bytes), with four clean build phases and offline provenance/package checks. It remains uninstalled pending phone availability; earlier 735bf87b and 9dde9d29 packages are historical for the current collector. Continue current-source phone profiling, failed desktop draw budgets and final per-site art. Final art, five exact references (37/42), 2020 Adreno, sustained budgets, release and authenticated services remain open. See [counter evidence](../../reference/all-viewport-profile/README.md).


## Isolated exact structural culling candidate — 2026-10-10

Five actual opaque cell/gate meshes yield desktop terminal160→46 and gate155→77 global draws; portrait87→41 and113→29. All28fixed-clock stationary arrival cases retain identical decoded pixels across off/on/off-repeat captures, with verified actual render-frame progress. Every tracked Godot file remains unchanged; this is a candidate, and the current6bbAPK has no culling optimization. Travel/reveal/detail cameras, actual producer counters and CPU cost must pass before adoption. See [candidate evidence](../../reference/exact-structural-occlusion/README.md). Android/sustained/final-art/full-goal acceptance remains pending.
