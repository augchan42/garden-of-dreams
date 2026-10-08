# Portrait architecture and overview behavior — 2026-10-09

Daoxiang Farmhouse, Daguan Hall and Longcui Nunnery now have separate Godot portrait arrival views. The measured building silhouettes fit between the header and command panel at 390×844 and 360×800 and occupy at least 75%, 70% and 70% of the width respectively. Longcui uses the inspected 10-degree view: the title stays clear while the branch and lantern remain separated. Existing landscape views and authored Blender cameras remain unchanged. These runtime views adapt the authored scene to a narrow screen.

“Look” restores each room's overview after “Doors.” Resizing keeps a selected detail pose and its text; resizing an overview switches between the portrait and existing landscape pose without changing room, visitor position or text. Camera framing is separate from room arrival, so resizing does not re-enter the room or emit another arrival signal.

## Verification

The regression first failed with 13 measured fit/scale/centering and restoration errors. Its original script, unchanged prior runtime, report, log and all 15 original captures are retained. A centered nunnery intermediate passed before the final off-axis composition was selected; its runtime and 15 captures are retained too. The final behavior test passes with 15 original captures and no errors. It uses the actual graphical renderer, mesh vertices projected through the camera, public detail/Look commands and real viewport resizing. Initial room setup uses direct arrival; continuous movement is checked separately.

Seven existing route/UI/pavilion/pond regressions pass. Both complete native tours pass through all 14 rooms over 26 legs from the initial cell without actor resets. They use ordinary time scale 1 and 60 Hz physics, with at most four active practicals. Each walk has 17,581 grounded floor-ray samples and 17,581 supported samples, with zero misses or floor failures. The tour portrait fixture is actually 540×960; the focused behavior fixture is 390×844 and 360×800. Desktop is 1410×600. Actual PNG dimensions were checked, rather than inferred from launch arguments. Production cold import finishes without script/import errors.

`frozen-inputs.json` identifies the exact runtime, test and contract files used by the successful regressions and tours. The final source GLB remains `59de1ca29bc9d02235fc29a18b78c7b2c3dfde893a27f3b8fb318af6e042ddc8`; runtime SHA is `db32d9c058a732c330d9df910b22b961f755045c5904c47e8fde68fd3c056138`. No geometry, textures, saved Blender source or lighting was changed in this checkpoint.

## Visual review

The final nunnery arrival and Look originals at both narrow sizes, the imperial Look original, and three settled portrait originals from the actual continuous walks were directly inspected. Earlier farm/imperial originals were inspected before the nunnery-only adjustment. The farmhouse is larger and centered; the imperial roof fits; the nunnery title remains clear. Normal room lamps still illuminate the farmhouse doors during the continuous walk. Ceiling and floor dominance, backdrop edges, foliage/rock detail and remaining facade shading still require art work. This checkpoint accepts these three portrait compositions and camera actions, not all site art.

## Evidence retained

`artifact-locations.json` maps every logical artifact to an unchanged-byte archived file, its original local path and SHA-256. Identical originals share a stored file. The archive contains all 12 nunnery angle comparisons, all 45 before/intermediate/final behavior originals, 26 settled originals from each tour, complete original reports/logs and executed source snapshots. All 139 original capture hashes and actual dimensions per tour were verified at collection. Transient travel images remain in the local review folders named in the original reports; they are not included in the repository archive. `review-summary.json` records the verified counts. The evidence index is `../../../export/portrait-architecture-runtime-evidence.json`.

The angle-selection document records its pre-runtime-review status and is retained unchanged. The successful final behavior and tour reports supersede that pending status. Archived before/intermediate source snapshots are evidence, not current production code.

Final site art, six missing references, current physical-device and sustained rendering budgets, release packaging and authenticated services remain open. These desktop tests do not establish phone performance.
