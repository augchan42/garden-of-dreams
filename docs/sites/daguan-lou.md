# Site sheet: 大觀樓／省親別墅

Slug `daguan-lou`. Priority 2. Function: North backdrop. Room id `daguan_lou`.

## Stage direction

A broad ceremonial facade closes the north view. Layered roofs and repeated doors supply scale; the player should not be able to enter an unfinished building.

## Dimensions and access

13 m frontage; 1–3 m set depth; larger roof silhouette behind normal-height doorways. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Imperial facade; stepped central frontage; closed doors; two roof tiers; black backstage return walls. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Warm-neutral hard side key; red lacquer door leaves, darker recessed panels and sparse amber windows. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Approach; closed-door inspection; return south. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_daguan_lou_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

The facade must read as one large hall, not two adjacent identical pavilions. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

The architectural slot now has a collected and visually inspected photograph of Daguanlou in Beijing Daguanyuan, by 刻意 (2010), with attribution and CC BY-SA 3.0 terms in `../reference/external/daguan-lou/README.md`. It shows the repeated red columns and lattice bays, balcony, grey tiled eave and blue/gold painted brackets. The photograph guides structure and material separation; it does not establish the game's night lighting. The night-set still and separate detail reference remain uncollected.

## Current build and acceptance

The paired-pavilion placeholder has been replaced by a single broad facade with two continuous roof tiers, five paired door bays, central steps, sparse amber transoms and black backstage returns. Three markers define the approach, door inspection and return. The interior is not built and stays inaccessible.

`test_imperial_route.gd` passes outward and return physics traversal, floor support, a ray check against the closed-door collider, and rejection of an entry action. Godot provides a north-walk visit from Qinfang and a close door view.

The initial roof UV check found 24 overlapping sampled texels; triangulation before projection with a tighter angle resolves the sampled overlap. The establishing camera was lowered to reveal the facade under its eaves. The side key is now warm-neutral and aimed below the eaves. Ten door leaves have red lacquer and twenty recessed panels use a darker related material, making the bronze fittings readable in the close view. The arrival camera moves into the east side aisle; the covered walk still borders the left of the frame. The missing typeset glyphs have been replaced by original painted 大觀樓 lettering embedded in the Blender source and glTF; production-art provenance is in `textures/decals/imperial/README.md`. Nine opaque facade meshes now have source-matched Cycles bakes; the transparent title retains its painted material. Sourced stills, final atlas/material review and wider garden rendering acceptance remain unfinished.

Source scripts: `scripts/refine_imperial_facade.py` and `scripts/finish_imperial_art.py`. Graded Godot references: `docs/reference/route-imperial*.png` and `route-mobile-imperial*.png`.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.

The runtime bake adapter now corrects Cycles diffuse transfer for Compatibility and isolates baked receivers from static keys while preserving shadow-caster masks. Desktop and portrait views are refreshed; final material, bake noise and texel-density acceptance remain open. See `../baked-lighting.md`.


## Owned backdrop wash — 2026-10-06

`LGT_daguan_lou_backdrop_wash` is saved in authoring and `SITE_daguan-lou.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_daguan-lou_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.


## Collected painted-wood material reference — 2026-10-08

Slot 3: [original photograph](../reference/external/daguan-lou/painted-wood-roof-detail.jpg), 朱華龍 - Zhu Hua Long, CC BY 2.0. The close upward view shows red lacquer posts and rails, blue/green/gold painted beams, exposed roof members, gray tile edges and carved bracket shapes. Paint wear exposes timber variation rather than a uniform flat surface. It supplies material separation and roof/beam detail for the imperial facade. No exact Daguan building identity, structural dimensions or night lighting are asserted. Full attribution and original-byte hashes are saved beside the image. The night-set slot remains open.

## Isolated roof chart correction — 2026-10-08

The saved two-tier roof uses 576 closed eight-sided cylinders with outward
normals. Their original UV2 side charts are under 0.1 source pixel wide;
89.9% of upward-facing side centroids sample zero baked light. A separate
UV2-only export with a fresh roof bake reduces this to 0.3%, preserving all
geometry, normals, primary UVs and other sites. Native portrait, desktop and
close-up comparisons show thinner, lit ribs. Actual 256px imports retain
patchy shading; the actual 512px lossless RGB8 import is selected for further
validation. Production remains unchanged. Complete lighting, gutter/noise
review, joins, palette, memory and phone acceptance are still required.
See [the recorded experiment](../reference/imperial-roof-charts/README.md).


## Working roof correction installed — 2026-10-08

The complete `361a67c7` working bundle now uses the verified imperial UV2 allocation and lossless 512 roof import. Matching complete source lighting, cold/reimport contracts, saved libraries, both full rendered walks and post-install production checks pass. The canonical Blender exporter reproduces all 16 GLBs exactly. The directly compared desktop/portrait originals show lit narrow tile ribs in place of broad black stripes. Facade mottling, dark eave joins, final palette/materials, gutters, device and sustained budgets remain unaccepted. See [the full recorded review](../reference/imperial-full-lighting/README.md).
