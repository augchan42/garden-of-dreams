# Site sheet: 大觀樓／省親別墅

Slug `daguan-lou`. Priority 2. Function: North backdrop. Room id `daguan_lou`.

## Stage direction

A broad ceremonial facade closes the north view. Layered roofs and repeated doors supply scale; the player should not be able to enter an unfinished building.

## Dimensions and access

13 m frontage; 1–3 m set depth; larger roof silhouette behind normal-height doorways. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Imperial facade; stepped central frontage; closed doors; two roof tiers; black backstage return walls. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Green hard side key; sparse amber windows. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Approach; closed-door inspection; return south. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_daguan_lou_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

The facade must read as one large hall, not two adjacent identical pavilions. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

## Current build and acceptance

The paired-pavilion placeholder has been replaced by a single broad facade with two continuous roof tiers, five paired door bays, central steps, sparse amber transoms and black backstage returns. Three markers define the approach, door inspection and return. The interior is not built and stays inaccessible.

`test_imperial_route.gd` passes outward and return physics traversal, floor support, a ray check against the closed-door collider, and rejection of an entry action. Godot provides a north-walk visit from Qinfang and a close door view.

The initial roof UV check found 24 overlapping sampled texels; triangulation before projection with a tighter angle resolves the sampled overlap. The establishing camera was lowered to reveal the facade under its eaves. The existing side key was lowered to reach below the eaves; the close door view remains dark and needs further readability work in the final lighting pass. Final painted signage, sourced stills, atlases and the specified baked-lighting rig remain unfinished.

Source script: `scripts/refine_imperial_facade.py`. Graded Godot references: `docs/reference/route-imperial*.png` and `route-mobile-imperial*.png`.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.
