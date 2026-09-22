# Site sheet: 凸碧堂

Slug `tubi-tang`. Priority 2. Function: Current events pavilion. Room id `tubi_tang`.

## Stage direction

A hall occupies the highest terrace. The climb should gradually expose the garden and then the painted cyclorama beyond it. The terrace edge frames the view without hiding that this is a stage.

## Dimensions and access

Terrace floor 4 m above origin; 2.2 m stair width; 3.1 m eaves above terrace. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Plaster hill; terrace; steps with collision; low parapet; stone topic table; one amber lantern. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Amber hard key at the hall; green wash on the distant garden. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Stair foot; terrace arrival; news table; overlook; return to stair. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_tubi_tang_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

Establishing view includes the central pavilion below and the edge of the painted sky. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

## Current build and acceptance

The public terrace now has low side/front parapets, a stone topic table, one amber lantern and five action markers. Twenty visible treads rise four metres; a separate simplified ramp collider supplies continuous capsule movement. The approach runs around the west side of the bulletin hall. `test_hilltop_route.gd` passes the climb to four metres and return descent through actual imported collision geometry; `test_study_route.gd` still passes the shared approach. Godot provides Current Events and an overlook action; the hall interior stays closed.

Desktop and portrait arrival, overlook, table and live-event views are saved as `docs/reference/route-hilltop*.png` and `route-mobile-hilltop*.png`. The live browser filters the public endpoint to temporal topics and does not create readings.

Final painted signage, sourced reference stills, light-linked backdrop wash and a fresh bake remain unfinished. This site pass changes the assembly hash, so the previous whole-garden bake cannot be reused unchanged.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.
