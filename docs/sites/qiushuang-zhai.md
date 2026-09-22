# Site sheet: 秋爽齋

Slug `qiushuang-zhai`. Priority 2. Function: Bulletin board. Room id `qiushuang_zhai`.

## Stage direction

A long study hall faces a shallow courtyard. Three banks of amber screens sit behind repeated lattice panels. Keep the centre aisle clear so a visitor can approach a screen without crossing furniture.

## Dimensions and access

9 m wide, 2 m deep facade; 1.8 m clear front walk; eaves at 3.1 m. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

12 amber monitors in three groups of four; lattice screen fronts; three desks; two scrolls; closed side doors. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Green hard key across the frontage; amber screens are the dominant warm source. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Board entrance; left, centre and right screen banks; return to the central walk. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_qiushuang_zhai_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

A frontal medium view must show the individual monitors rather than merge them into one lit window. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

## Current build and acceptance

The hall now has twelve screens, three desks with keyboards, two scrolls, closed side doors, five room markers, three bank cameras and a frontal camera. A stone approach connects the east covered walk to the courtyard. Scroll marks are temporary graphic layout. Live bulletin content, final signage/materials and reference collection remain unfinished.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.
