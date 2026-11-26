# Current-source demo handoff

This work finishes the bounded offline desktop route: terminal, rockery gate,
Qinfang Pavilion, local hexagram, finale and replay. The implementation plan is
`docs/superpowers/plans/2026-10-23-demo-handoff.md`.

## Stream-bank repair

The visible stream-bank masonry and coping had less than one lightmap texel per
triangle. The baseline coverage check fails at a minimum 0.00785 source texels;
the repaired layout passes at 3.0828. It assigns continuous front and top charts
for 54 bank modules into unused space alongside the pavilion tile charts.

The comparison proves that only 3,240 bank triangles change UV2. All positions,
normals, primary UVs, materials, lights, cameras, colliders and other receiver
UV2 remain unchanged. The other fourteen site exports are byte-identical.
`export/stream-bank-lightmap-compatibility.json` records this proof. The Qinfang
atlas receives one fresh 1024px/128-sample Cycles bake. The 280 other source and
engine PNG copies are retained; their records preserve original bake provenance
and explicitly reference the UV-only compatibility proof.

The repaired atlas uses lossless 1024px runtime import. This is a desktop art
decision and increases texture allocation; it does not establish mobile budget
acceptance. Native pavilion, gate and table originals were inspected. The banks
now show masonry instead of black strips. Other atlas surfaces also benefit from
the higher import resolution; no whole-image equality claim is made.

The first allocator used rounded coordinates and missed 26 faces after Blender's
join transform. It was replaced by nearest-centroid matching with explicit vertex
distance checks below 0.1 mm and exactly 1,620 matched quads. The failed export
and subsequent source/bake/native logs remain under the ignored
`build/demo-handoff-20261023/evidence` directory.

## Package workflow

`scripts/build_demo_handoff.py` stages the current Godot project, selects the
focused demo startup, includes required JSON data, and enables the texture
formats required by the universal macOS export. Production startup remains the
full garden. The app is ad-hoc signed locally; Apple notarization and Intel
execution testing are outside this handoff.

The shipped release template disables script and path overrides. A passive
acceptance child runs only for the explicit `--demo-acceptance` user argument;
it tests the actual default scene and embedded pack. Assertion tests run with
installed Godot against that same pack. Normal and extracted launches use no
test flag or scene override. The workflow preserves logs, native video frames,
audio cue times, exact source/PCK hashes and archive verification.

The release test reproduced a separate lighting defect: `assert()` expressions
contained the backdrop and terminal-spill installation calls. Release exports
skip those expressions. The calls now execute outside assertions and fail
explicitly if installation is incomplete. The original release failure remains
in `build/demo-handoff-20261023/evidence/release-lighting-red.log`.

The final build passed all six packaged checks without warnings or errors,
including pointer/keyboard traversal and replay in the actual release executable
at desktop and portrait sizes. The native capture has 1,290 frames at 30 FPS
(43 seconds), H.264 video and AAC audio; full decode passes. The archive is
426,153,827 bytes, with matching clean-extraction hashes, valid signature and a
normal extracted launch. `acceptance.json` records exact hashes and results.

The archive is `build/demo-handoff-final/GardenOfDreamsDemo-macOS.zip`. The run
guide is `docs/demo-run-guide.md`. Source integration into main remains held by
the user-owned GitGuardian failures on dependency PRs 22 and 35; PR14 remains
independent. The demo handoff does not complete the wider garden roadmap.
