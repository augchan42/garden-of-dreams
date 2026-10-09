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

Current saved references and any unfilled slots are recorded below and in the external reference README.

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


## Owned backdrop wash — 2026-10-06

`LGT_longcui_an_backdrop_wash` is saved in authoring and `SITE_longcui-an.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_longcui-an_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.


## External foliage/material reference — 2026-10-08

The slot-3 close reference is collected, directly reviewed and attributed in `../reference/external/longcui-an/README.md`. White five-petal plum flowers with rounded overlapping petals, dense pale stamens with yellow anthers, pink-red central cups, small buds and rough dark bark. Useful for blossom construction and sparse branch dressing; daylight color is not a night-lighting reference. Original bytes match the Commons SHA-1. The night-set and architecture slots remain uncollected. This is reference collection, not acceptance of the current foliage mesh or material.


## External entrance architecture reference — 2026-10-08

The slot-2 entrance reference is collected and directly reviewed in `../reference/external/longcui-an/README.md`. Its gray tiled eave, painted brackets/lintel, red timber and lanterns, and whitewash guide structural and material separation. The publisher identifies Longcui; the image is daylight and cropped above the ground, with an open entrance. It does not establish the sheet's dimensions, closed gate leaves, collision or final palette. Copyright and the Sipa watermark are retained; this is not a shipped asset. Only the night-set slot remains uncollected.

## Collected Shaw night-set reference — 2026-10-08

Slot 1 now has a directly reviewed frame from the published *The Magic Blade* trailer at 3.0 seconds. An upward view of a timber inn entrance shows a sign, exposed roof members, dark recesses and a bare branch against a mostly black background. Cool edges contrast with brown/gold timber and lettering. Night appearance is inferred visually, not a verified scene caption. It guides sparse branch silhouettes, timber separation and dark entrance framing. It is not the Longcui nunnery, its paired closed gates, its measured frontage or plum blossom material, and the low-resolution image cannot supply detailed joinery.

Attribution, rights information, original stream hash and exact decoded-frame provenance: `../reference/external/longcui-an/README.md`. All three reference slots are collected. This does not establish final scene art, lighting, performance or service acceptance.

## Approach join proposal — 2026-10-08

The construction script creates three intersecting stone approach slabs. CPU exported-geometry and source-lightmap probes identify nearly black sampled overlaps in the Ouxiang foreground. Shortening only the two vertical render slabs to the horizontal crosspiece boundaries preserves the decimal-constructor walking footprint and removes positive-area overlap. The proposal is not applied; saved Blender ownership, collider preservation, fresh native lighting/render and route checks remain required. Evidence: `../reference/ouxiang-path-joins/README.md`.


## Runtime portrait framing — 2026-10-09

The runtime portrait view now uses the inspected 10-degree angle: the title stays clear while preserving the specified slight off-axis composition. It fits above the command panel at both narrow sizes and was inspected during the full walk. Blossom/branch detail, floor/lighting treatment and final art remain open. “Look” restores this overview after a detail action; resizing preserves details or adapts the overview. Existing desktop and authored Blender cameras remain unchanged. See `../reference/portrait-architecture-runtime/README.md`.

## Waterline and reed source checkpoint — 2026-10-09

The combined Blender source is now `0d3e84e3`; export and Godot use `1380ceca`. The complete fresh lighting set covers 124 ordinary receivers and 141 source PNGs, with matching wash/spill catalogs. Both native Mac tours visit all fourteen sites over twenty-six public-command legs and return to the cell, with no floor misses and at most four practical lights. All 42 camera, 400 collider and 71 marker contracts are preserved. This is an incremental working-source checkpoint; final site art, references, phone/sustained performance and authenticated services remain open. Evidence: `../reference/ziling-source-art/README.md`.


## Stream bank and lotus checkpoint — 2026-10-09

The current complete source is `7a9fc523` with authoring `074ab201`. The shared stream has 54 bank modules and 54 added colliders; all 42 cameras,400 earlier colliders and 71 markers are preserved. Closed circular lotus pads sit above the water, with a muted shared leaf material and matching saved kit/generator. Fresh lighting covers 124 receivers and 141 source PNGs. Both native Mac tours pass 14 locations and 26 travel legs;15 installed checks pass. This is an incremental source checkpoint. Final site art, five remaining reference slots, current phone/sustained performance, release and authenticated services remain open. Evidence: `../reference/water-edge-source/README.md`.


## Island exterior winding checkpoint — 2026-10-09

Current assembly `73267e2b` / authoring `2b07ce48` repairs the reed island’s exterior face winding. All other exported mesh attributes and fourteen other site GLBs are preserved; cameras, colliders, markers and runtime are unchanged. Complete matching lighting, twenty-five focused native checks and thirteen installed checks pass. This site is not declared final by the island repair. Five references, current phone/sustained budgets, release and authenticated services remain open. Evidence: [island source review](../reference/island-exterior-winding/README.md).
