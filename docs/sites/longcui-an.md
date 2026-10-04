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


## Flora placement — 2026-10-04

Two atlas-textured plum trees replace the previous separate branches and petal meshes; the existing trunk collision and closed-gate approach are retained. All placed plants share one compressed runtime atlas and switch detail with distance. The assembly export and editable site libraries are synchronized. Further dressing, final lighting and sourced references remain open.


## Shared prop placement — 2026-10-04

The existing dressing now uses fitted prop-library meshes with a shared PBR atlas. Mount positions, seat/table heights, collision, lights and triggers are retained. The site’s props export as one material batch and stop drawing beyond 28 metres. Desktop and portrait views were reviewed; source-hash-checked bakes apply where this site belongs to the demo or priority-2 catalog. Further art, sourced references and final lighting remain open. Details: `../kits/props.md`.

## Painted title — 2026-10-04

The temporary Songti glyph geometry is replaced by original painted 櫳翠庵 lettering on the wood board. Its wood board now projects 0.55 m forward of the original mount, on two short wood supports, clearing the previously intersecting roof eave. The texture preserves its generated alpha and image aspect ratio; Godot uses compressed mipmapped 512px imports. Cameras, lights, triggers and collision records remain unchanged. Original artwork and provenance: `../../textures/decals/garden-signs/README.md`. Final material/lighting acceptance and external visual references remain open.


### Current lighting coverage — 2026-10-04

All eligible opaque meshes in this saved site now have current source-matched Cycles lightmaps in the full Godot catalog. Native pixels and engine copies are checked; normal exploration uses the maps with static shadow maps disabled. Desktop and portrait arrival captures are refreshed under `docs/reference/route-*-full-baked.png`. Final color, material, noise/texel-density and external reference acceptance remain open.
