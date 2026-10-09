# Scene changes before lighting adoption

Explicit `godot_cast_shadow` mesh metadata now transfers through Godot's
post-import hook and all three native Blender bake paths. Only meshes with a
boolean flag change; other meshes keep their settings. Future ordinary, wash
and spill records include the applied flags. The installed source has no flags,
and native inspection preserves all 558 imported mesh settings.

The actual ceiling export supplies the flagged mesh in isolated pixel tests.
Godot now imports it with shadows off and the existing cyclorama's unshaded
paint, identical color and shared texture. A forced double-sided shadow control
darkens the test floor; the imported setting matches the explicit off control.
The default one-sided caster did not shadow this particular lamp, so the test
does not claim that its previous Godot default darkened the whole garden.

Blender's actual imported ceiling initially casts shadows. The shared bake
helper restores its false flag and preserves 558 unflagged meshes. In the
scaled diagnostic fixture, floor linear luminance changes from 0.000019 to
0.763649; forced on/off controls reproduce that change. An independent sRGB
decode of the saved PNG agrees with the reported linear value. This proves
transfer and the isolated shadow effect, not complete garden GI or final paint.

The first Godot directional fixture lacked a useful shadow control. A later
run used a stale imported scene after the hook changed; a cold rebuild of only
the isolated GLB cache applies the hook and passes. The first Blender report
mislabelled encoded PNG luminance as linear; it is rejected and retained, and
the corrected test explicitly decodes sRGB. Raw reports, exact scripts,
controls and rejected versions remain under `reference/scene-adoption/`.

Native inspection of the earlier floor repair found coplanar rendering artifacts
at the pavilion overlaps. The revised candidate lifts all eight visible joints
and their matching colliders by 2 mm. Both pavilion views lose the observed
white overlap patterns; sixteen route/inspection-light captures show the
actual exported surfaces. Every centre ray reaches its intended joint collider.
The additional white lamp is explicitly diagnostic; its bright views are not
final lighting. Earlier obstructed cameras and the coplanar version are retained.

The revised export preserves all 4,344 existing source objects and materials,
all existing exported transforms/cameras/extras, and thirteen other site GLBs.
The strict actual physics walk passes fourteen rooms, twenty-six legs and
17,581 grounded ray samples without a miss. It uses public commands, one
visitor, no position resets, no substitute paths and no injected collision
shapes. Old bakes are disabled in the isolated fixture because geometry/UVs
have changed; this is not production traversal acceptance.

Both repairs are now composed in a separate saved Blender source and export
`33b20efadae58c5eb137eda3e21236211a5fb9a1047a1ba41d6338cb48fefbce`.
The ceiling adds one node to the verified floor candidate, with unchanged
existing transforms/cameras/extras. Both floor-site exports remain byte-identical
to that verified candidate, and twelve other site exports match canonical
bytes. The combined source has 233,552 render-only triangles; this is not a
measured visible-triangle or draw budget. Scratch pointers are
`/tmp/garden-floor-lift-authoring.json` and
`/tmp/garden-combined-floor-canopy.json`.

Canonical authoring/export, the installed GLB and previous local release remain
unchanged. The new code and unshaded material are prepared for adoption.
The wash pipeline now validates six exact candidate receivers; the unshaded
ceiling remains outside the 124 ordinary targets. Combined native import,
continuous physics walk, sampled portrait coverage and fresh direct wash pass.
The actual current baked garden also exposes moon clipping, and a material
intensity counterfactual restores its brush texture. See `ceiling-lighting.md`.
Authored moon/paint adjustments, complete fresh lighting, production verification
and package/device checks remain open.
Thirty missing references, final site art, performance and authenticated room
services remain part of the full active goal. Evidence is indexed by
`export/scene-adoption-evidence.json`.


## Matching working scene adopted — 2026-10-08

Canonical Blender authoring is now `a273a4c0…`; export and Godot GLBs are both `8d1d9b4e…`. Fifteen site libraries, the portable master, source/engine atlases and all 141 source PNGs were installed together after exact staged/current byte checks. The full exploration route is the default scene; the focused reading demo remains separate. Production import, all camera/collision/marker snapshots and five lighting checks pass.

Both matching native rendered walks visit fourteen rooms over twenty-six public-command legs, check 17,582 supported ground rays with no misses, capture all twenty-six settled arrivals and return to the original cell. Desktop and portrait each retain 139 PNGs. The earlier current-run count of 17,581 was incorrect; that count belongs to the preceding 41b candidate.

The baked moon retains brush variation with no measured channel clipping. Baseline display p05/p95 is 0.662944/0.805190; the original 1254² painting remains unchanged. This accepts a working improvement, not final scene art. Roof striping, visible paint joins, some portrait framing and later-site detail remain open.

Current normal-route Mac allocation is 49,284,173 renderer texture bytes (about 47 MiB), with a highest sampled room of 49,367,461 bytes. This is not target-phone, demo-finale, sustained-traversal or release evidence. The existing local package/movie still represents the earlier source. Twenty required reference slots, final texture/device/performance and authenticated room services remain unfinished.

Evidence: `../export/moon-intensity-final-lighting-evidence.json`, `../export/moon-intensity-baked-review-evidence.json`, `../export/moon-intensity-rendered-traversal-evidence.json` and `../export/moon-intensity-working-adoption-evidence.json`. The original review's stale worker PID is preserved; a separate resume provenance record identifies its successful completion.


## Hengwu stone and matching lighting installed — 2026-10-09

The current working source is `26033c99`, with saved Blender authoring `19eb386d`. Hengwu's closest pierced stone is narrower and lower, with smoother faces and a small bevel. Its collider stays anchored to the original floor position. The table, four stools, two other stones, cameras and fourteen other site GLBs are preserved. Canonical default export reproduces all sixteen GLBs exactly.

All six source-lighting phases passed, covering 124 ordinary receivers and 141 source PNGs. The combined review has 47 completed checks and seven deliberately rejected inputs. Both native Mac walks cover fourteen rooms, twenty-six legs and 139 original captures each, with 17,582 supported grounded samples, no floor misses and at most four practical lights at time scale 1. All 278 walk originals are archived. The first incomplete camera captures and portrait failures remain preserved; the corrected test waits for actual tween completion. Game runtime code is unchanged.

Twenty-two targets were installed using checked staging hashes and local backups. Eleven checks on the installed project passed: import, source contract, complete lighting, both backdrop modes, both terminal-spill modes, surface materials, both palette modes and portrait architecture behavior. All nine completed Hengwu action originals and four settled walk originals were inspected. Evidence: `reference/hengwu-native-review/README.md` and `../export/hengwu-native-review-evidence.json`.

The smaller stone reveals more court, but narrow book/rock framing, roof cropping, the foreground wall cap and facade lighting still need work. This is incremental scene progress, not final all-site art acceptance. Mac stationary normal allocation peaks at 52,600,513 bytes and demo at 43,512,435 bytes; phone, sustained and frame timing remain unverified for this source. Android packages are stale. Five reference slots, remaining site art/framing, physical-device/2020 Adreno budgets, release and authenticated services remain required. The full goal stays active.

## Waterline, source palette and volumetric reeds installed — 2026-10-09

Current authoring is `0d3e84e3`; export and Godot are `1380ceca`. The stream and six lotus clusters rise 0.7 m, saved water colors match the reduced-green engine direction, and ten Ziling plants use readable radial plume volumes with tapered leaves. Full/lower reeds have 1,648/592 triangles; twenty actual world-space checks keep both detail levels within the specified reed height range. All other flora geometry and the shared 2048² source atlas remain unchanged; Godot still allocates the shared atlas at 512px. Stream movement does not move paths, bridge decks, landing or collision.

All six source-lighting phases passed: 124 ordinary receivers, six wash receivers, seven spill maps and 141 source PNGs with exact engine copies. Thirty-nine completed review phases include saved source/default export reproduction, all sixteen fresh-generator flora semantics, source/import contracts, kits, three Ziling modes, adjacent framing, actual texture inventory, all twenty-eight arrivals and both rendered tours. The architecture test passed fifteen captures; the runner's incorrect completion label is retained with the exact log/report correction. Each tour has 139 original captures, fourteen rooms and twenty-six legs: desktop 17,582 supported samples, portrait 17,581, both without floor misses and with at most four practical lights at normal time scale. Those distinct counts are actual measured per-run results.

Thirteen checks on the installed project pass. An earlier final framing timeout triggered a verified rollback; the successful retry uses the same 1410×600 process launch size as the completed fixture and retains the test's 100-second deadline and all assertions. All ten installed Ziling images match the isolated normal originals byte for byte; two installed portrait originals were directly reviewed. The separately repaired flora library displays its six render-hidden colliders as viewport wires so a default cold-open re-export evaluates their transforms. The original failed plum export, update-only failed control, successful visible-collider control, saved repair and fresh canonical reproduction are retained.

All twenty-eight current arrivals, selected Ziling normal/touch/density views, eight settled-tour originals and two explicitly forced lower-detail originals were directly inspected. The water covers most black island sides and the reed heads read clearly, with an open landing. Faceted leaves/plumes, coarse lotus surfaces, hard bank edges, desktop island crop and other sites' stage/ground/backdrop/lighting issues remain. This is incremental source acceptance, not final fourteen-site art acceptance.

The M2 Max normal inventory is 52,517,225 renderer texture bytes; demo is 43,468,745 bytes. These are stationary native Mac allocations, not phone timing or sustained-budget acceptance. Current Android/release packages are stale. External references remain 37/42; authenticated reading/history, identity refresh, AI, presence and social remain open. Evidence: `reference/ziling-source-art/README.md` and `../export/ziling-source-art-evidence.json`.
