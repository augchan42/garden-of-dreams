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
