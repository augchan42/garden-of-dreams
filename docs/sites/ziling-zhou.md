# Site sheet: 紫菱洲

Slug `ziling-zhou`. Priority 4. Function: Reed island dressing. Room id `ziling_zhou`.

## Stage direction

An island of reeds and low stone sits in the stream. A small footbridge provides access; no large hall belongs here.

## Dimensions and access

Island roughly 7 × 5 m; 1.8 m footbridge; reeds 0.8–1.6 m. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Reed island; timber footbridge; stone landing; low boundary rocks; sparse lotus. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Green key on reeds; borrowed amber from distant buildings. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Footbridge entry; island overlook; return east. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_ziling_zhou_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

Low view across reeds with distant roofs separated from the island silhouette. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

## Current build and acceptance

The placeholder hall has been removed. A low stone island, reeds, landing and timber footbridge now occupy the site. Three action markers and two cameras are exported. Godot traversal from the water pavilion and back passed with floor support. The graded Blender reference is `../reference/ziling-zhou.png`; the engine view is `../reference/route-ziling.png`. Final foliage/material work and sourced references remain unfinished.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.


### Water-kit integration

The six-metre water-kit wooden bridge replaces the old footbridge, overlapping both the pavilion and island landings. Its deck and two rail colliders remain separate. Two six-leaf lotus clusters replace the old pad cylinders beside the island; reeds, rocks, landing and markers are preserved. The bridge uses the shared architectural atlas. Final foliage/lotus materials, lighting, references, runtime LOD switching and phone acceptance remain open.
