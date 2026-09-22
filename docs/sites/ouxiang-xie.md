# Site sheet: 藕香榭

Slug `ouxiang-xie`. Priority 3. Function: Group readings. Room id `ouxiang_xie`.

## Stage direction

An open water pavilion stands west of the bridge. Its approach stays over water; the group table is visible through the posts, with no solid hall wall behind it.

## Dimensions and access

6 m pavilion width; 1.8 m approach; shared water level at -1.1 m. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Dedicated open pavilion; timber bridge; tea table; six seats; lotus clusters; two lanterns. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Amber practicals near the table with a hard green rim. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Bridge approach; group table; water rail; return east. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_ouxiang_xie_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

Camera crosses the bridge axis and settles on the table without revealing the backstage wall. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

## Current build and acceptance

The generic hall has been replaced with an open rectangular water pavilion, a tea table, six stone seats, two lanterns, lotus and a traversable western approach. Four action markers and two cameras are exported. The Godot route reaches it from Qinfang and continues to the reed island; both return paths passed the physics test. The graded Blender reference is `../reference/ouxiang-xie.png`; the engine view is `../reference/route-ouxiang.png`. Group readings, final materials and sourced reference collection remain unfinished.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.


### Water-kit integration

Four water-kit lotus clusters replace the old flat pad cylinders around the pavilion. The existing deck, six tea seats, two lanterns and route markers are preserved. The bridge uses the shared architectural atlas. Final foliage/lotus materials, lighting, references, runtime LOD switching and phone acceptance remain open.
