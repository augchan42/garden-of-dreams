# Continuous garden traversal

The unchanged production route reaches all fourteen rooms and visits all thirteen
connections in both directions, but has three floor gaps. Ten of the twenty-six
legs miss ground rays. The cell doorway has a 20 cm gap and the east and west
Qinfang crosswalks each have a 10 cm gap. The visitor stays above the gaps but
dips up to 2.9 cm. Production traversal acceptance remains open. The same ten failing legs were independently rechecked after installing the current painted-moon source and matching lighting; `current-production-red.json` records that current result.

`godot/tests/test_full_garden_traversal.gd` starts one visitor in the actual cell,
uses public commands and actual physics, and returns to that cell. It does not
set visitor positions, call private arrivals, replace paths or change time scale.
It checks floor support, arrival signals and heights, commands during travel,
unknown commands, and restored room actions. `--diagnose-floor` records the rest
of a tour after a recoverable floor mismatch; its final result still fails.

## Proposed repair and evidence

Eight narrow inserts close these seams: six 1.1 m wide wooden cell thresholds
and two short stone crosswalk joints. They overlap adjacent floor ends and stay
inside the existing doorway/path widths. The proposal includes visible floor
geometry and matching collision geometry.

The test-only collision counterfactual passes all twenty-six legs with 17,581
grounded ray samples and no misses. Removing the cell, east or west group
independently fails at its corresponding gap. These controls verify that the
strict tour still detects the original failures.

A separate saved Blender candidate adds the eight visible pieces and eight
colliders while preserving all 4,344 existing objects, existing materials and
the moon painting. Its export preserves all existing node transforms, lights,
cameras and material definitions. Thirteen unrelated site GLBs remain byte
identical. The two affected site exports need fresh matching lighting.

The actual separately exported candidate, imported into an isolated Godot
project, passes the same strict tour without test-injected colliders: fourteen
rooms, twenty-six legs, 17,581 supported grounded ray samples, and no misses.
The source/import check also passes all 42 cameras, 400 collider surfaces and
isolated rays, and 71 markers. Only baked-lighting application is disabled in
the fixture scene because the new floor UVs require new bakes; the production
movement, player, paths and test script are unchanged.

This is candidate physics evidence. The candidate has not been adopted into
the canonical source, production Godot assets or release. Rendered inspection,
fresh lighting and production traversal verification are still required.

Raw logs, reports, source bounds, proposal and script snapshots are under
`docs/reference/full-garden-traversal/`; hashes are recorded in
`export/full-garden-traversal-evidence.json`. The separate Blender candidate and
isolated project are retained at the temporary path recorded by
`/tmp/garden-floor-seam-authoring.json` and `/tmp/garden-floor-seam-fixture.json`.

## Commands

Run the strict test on the installed production assets:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --headless --fixed-fps 60 \
  --path godot --script res://tests/test_full_garden_traversal.gd \
  -- --output=/tmp/garden-full-traversal.json
```

The current production result is expected to fail until the repair is adopted.
The test-only `test_floor_seam_candidate.gd` accepts `--omit=cell`, `--omit=east`
or `--omit=west` for the independently verified rejection controls.

Prepare a new separate Blender candidate, using the matching diagnosed source:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background \
  blender/authoring.blend --threads 1 --python-exit-code 1 \
  --python scripts/prepare_floor_seam_candidate.py \
  -- --output-root /tmp/garden-floor-seam-candidate
```

The preparer rejects workspace destinations and existing candidate files. It
does not modify canonical authoring, libraries, GLBs or lightmaps.

## Rendered complete-route harness — 2026-10-08

`godot/tests/render_full_garden_traversal.gd` extends the strict physics tour
above. It records the real route camera and command UI during all twenty-six
legs and each arrival, retaining the same visitor, public commands and normal
simulation time. It does not override lights, materials, positions or paths.
The harness requires source-matched 124 ordinary, six backdrop and seven spill
receiver catalogs for the separate ceiling/contrast candidate and checks the
four-practical limit. Its sampled PNGs carry hashes and camera/visitor state.

Native Godot parses the complete harness and correctly rejects headless mode
before creating a capture directory or loading the scene. Exact scripts, log
and rejection report are retained under `reference/rendered-full-garden-tour/`,
indexed by `../export/rendered-full-garden-tour-preflight.json`. This proves the
headless guard only. The subsequent native passes below use the completed
candidate lighting and a separately imported acceptance project.

Run each view sequentially in the prepared candidate acceptance project after
all matching lighting is installed. Do not run another host graphics job while
the source baker is active:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path /path/to/candidate/godot \
  --script res://tests/render_full_garden_traversal.gd -- \
  --output=/tmp/garden-rendered-tour-desktop.json \
  --capture-directory=/tmp/garden-rendered-tour-desktop

/Applications/Godot.app/Contents/MacOS/Godot --path /path/to/candidate/godot \
  --script res://tests/render_full_garden_traversal.gd -- \
  --output=/tmp/garden-rendered-tour-portrait.json \
  --capture-directory=/tmp/garden-rendered-tour-portrait --portrait
```

Successful captures still require direct review for backdrop joins, floor
seams, architecture intersections, UI and camera transitions. Sampled frames
do not prove continuous-video art acceptance or target-device performance.


## Native continuous candidate walks — 2026-10-08

The 41b81c17 source with complete fresh 124/6/7 lighting passes both actual
native tours. Each covers fourteen rooms, twenty-six public-command legs,
17,581 supported grounded-ray samples with no misses, and a true return to the
original cell. Unsupported/busy commands, signals and restored controls are
checked. At most four practicals are visible. No visitor reset, private arrival
placement, fixture floors or lighting/material overrides are used.

Desktop records 114 PNGs at 1410 × 600. These sample travel and immediate
arrival state; an arrival signal precedes the camera's normal 1.4-second tween,
so they do not prove settled framing. The final portrait harness waits for the
actual tween's `finished` signal before proceeding. It records 139 PNGs at
540 × 960, including all twenty-six settled arrivals. The strict headless tour's
new `after_leg` hook defaults to no pause; native captures override it without
changing the production visitor, camera or simulation speed.

The first portrait attempt used a fixed 1.2-second hold, shorter than that
camera tween. Its specifically identified process was stopped after verifying
the capture defect. Exact partial-run log, scripts and rejection are retained;
that run is not accepted as settled framing. The corrected run passes.

The complete portrait settled-view contact sheet and desktop travel samples
were directly reviewed. Floor support and sampled framing improve confidence
in the separate repair, but the moon is still flat white and some ceiling paint
joins are visible. Site art, continuous-video quality and device performance
remain open. The canonical production assets still lack the repair; these
passes are not production adoption.

Raw reports, PNGs and exact test variants are retained in the desktop/portrait
subdirectories of `reference/rendered-full-garden-tour/`, indexed by
`../export/moon-contrast-rendered-traversal-evidence.json`. The original four
headless-preflight artifacts remain unchanged.


## Matching working scene adopted — 2026-10-08

Canonical Blender authoring is now `a273a4c0…`; export and Godot GLBs are both `8d1d9b4e…`. Fifteen site libraries, the portable master, source/engine atlases and all 141 source PNGs were installed together after exact staged/current byte checks. The full exploration route is the default scene; the focused reading demo remains separate. Production import, all camera/collision/marker snapshots and five lighting checks pass.

Both matching native rendered walks visit fourteen rooms over twenty-six public-command legs, check 17,582 supported ground rays with no misses, capture all twenty-six settled arrivals and return to the original cell. Desktop and portrait each retain 139 PNGs. The earlier current-run count of 17,581 was incorrect; that count belongs to the preceding 41b candidate.

The baked moon retains brush variation with no measured channel clipping. Baseline display p05/p95 is 0.662944/0.805190; the original 1254² painting remains unchanged. This accepts a working improvement, not final scene art. Roof striping, visible paint joins, some portrait framing and later-site detail remain open.

Current normal-route Mac allocation is 49,284,173 renderer texture bytes (about 47 MiB), with a highest sampled room of 49,367,461 bytes. This is not target-phone, demo-finale, sustained-traversal or release evidence. The existing local package/movie still represents the earlier source. Twenty required reference slots, final texture/device/performance and authenticated room services remain unfinished.

Evidence: `../export/moon-intensity-final-lighting-evidence.json`, `../export/moon-intensity-baked-review-evidence.json`, `../export/moon-intensity-rendered-traversal-evidence.json` and `../export/moon-intensity-working-adoption-evidence.json`. The original review's stale worker PID is preserved; a separate resume provenance record identifies its successful completion.
