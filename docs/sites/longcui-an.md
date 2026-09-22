# Site sheet: 櫳翠庵

Slug `longcui-an`. Priority 4. Function: Nunnery dressing. Room id `longcui_an`.

## Stage direction

A closed nunnery gate is framed by sparse plum branches. One lantern marks the threshold. The quiet frontage should differ from the larger social halls.

## Dimensions and access

6 m frontage; 2.1 m gate opening; 1–2 m facade depth. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Closed gate; two plum trees; single hanging lantern; incense burner; capped whitewash wall. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

One amber lantern; restrained green key on branches. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Closed gate inspection; return path. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_longcui_an_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

A still, slightly off-axis view keeps the branches and lantern separate. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

## Current build and acceptance

The generic hall has been replaced by a six-metre capped whitewash frontage with paired closed timber gates, two sparse plum trees with small five-petal blossoms, one hanging lantern and an open bronze incense bowl with three feet and three sticks. Four markers and three cameras are exported.

The water pavilion’s “Visit the nunnery” action follows a new stone approach around its eastern railing end. `test_nunnery_route.gd` passes both directions, floor support, closed-gate collision and rejection of entry. `render_nunnery.gd` produces desktop and portrait arrival/gate/incense views. Sourced references, painted signage, blossom/material refinement and final lighting remain unfinished.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.
