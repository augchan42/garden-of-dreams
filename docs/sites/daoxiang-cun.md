# Site sheet: 稻香村

Slug `daoxiang-cun`. Priority 4. Function: Farmhouse dressing. Room id `daoxiang_cun`.

## Stage direction

A small farmhouse interrupts the repeated tiled roofs. Rough fence rails and a thatched roof stand in front of a visibly painted paddy flat.

## Dimensions and access

6 m frontage; low 2.7 m eaves; fence below 1 m. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Actual thatched roof silhouette; rough fence; closed farmhouse door; paddy backdrop; small tools. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Warm interior sliver; green key on thatch. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Fence opening; closed house inspection; return path. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_daoxiang_cun_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

Show enough backdrop to reveal the painted rice field without exposing empty space. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

## Current build and acceptance

The generic tiled hall has been replaced by a six-metre farmhouse with a thick, uneven thatch silhouette and 318 layered stalk bundles. A fence below one metre leaves a central opening. The closed plank door has a warm sliver beneath it; a rake and hoe lean against the wall. A framed 6 × 3 m paddy flat beside the farmhouse carries a generated gouache-style painting of rice terraces and low hills. The texture is packed into Blender and embedded in the GLB; it is production art, not one of the required sourced references. Four markers and four cameras are exported.

Hengwu’s “Visit the farmhouse” action leaves the court through its front gate and follows the new western approach. `test_farmhouse_route.gd` passes both directions, floor support, closed-door collision and rejection of entry. `render_farmhouse.gd` produces desktop and portrait arrival/door/tool/paddy views. The original geometric paddy placeholder and obscured inspection view were replaced by the painted texture and matched Blender/Godot cameras. Source references, painted lettering, kit atlases and final lighting remain unfinished.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.
