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

Current saved references and any unfilled slots are recorded below and in the external reference README.

## Current build and acceptance

The generic tiled hall has been replaced by a six-metre farmhouse with a thick, uneven thatch silhouette and 318 layered stalk bundles. A fence below one metre leaves a central opening. The closed plank door has a warm sliver beneath it; a rake and hoe lean against the wall. A framed 6 × 3 m paddy flat beside the farmhouse carries a generated gouache-style painting of rice terraces and low hills. The texture is packed into Blender and embedded in the GLB; it is production art, not one of the required sourced references. Four markers and four cameras are exported.

Hengwu’s “Visit the farmhouse” action leaves the court through its front gate and follows the new western approach. `test_farmhouse_route.gd` passes both directions, floor support, closed-door collision and rejection of entry. `render_farmhouse.gd` produces desktop and portrait arrival/door/tool/paddy views. The original geometric paddy placeholder and obscured inspection view were replaced by the painted texture and matched Blender/Godot cameras. Source references, painted lettering, kit atlases and final lighting remain unfinished.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.

## Painted title — 2026-10-04

The temporary Songti glyph geometry is replaced by original painted 稻香村 lettering on the wood board. Its wood board now projects 0.58 m forward of the original mount, on two short wood supports, clearing the previously intersecting roof eave. The texture preserves its generated alpha and image aspect ratio; Godot uses compressed mipmapped 512px imports. Cameras, lights, triggers and collision records remain unchanged. Original artwork and provenance: `../../textures/decals/garden-signs/README.md`. Final material/lighting acceptance and external visual references remain open.


### Current lighting coverage — 2026-10-04

All eligible opaque meshes in this saved site now have current source-matched Cycles lightmaps in the full Godot catalog. Native pixels and engine copies are checked; normal exploration uses the maps with static shadow maps disabled. Desktop and portrait arrival captures are refreshed under `docs/reference/route-*-full-baked.png`. Final color, material, noise/texel-density and external reference acceptance remain open.


## Owned backdrop wash — 2026-10-06

`LGT_daoxiang_cun_backdrop_wash` is saved in authoring and `SITE_daoxiang-cun.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_daoxiang-cun_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.


## Collected reference — 2026-10-08

Slot 2: [original photograph](../reference/external/daoxiang-cun/daoxiang-modern-frontage.jpg), by 朱華龍 - Zhu Hua Long, CC BY 2.0. The visible plaque reads 稻香村 from right to left. The modern reconstruction has a low tiled hall, red columns and rails, stepped stone approach, rectangular green lattice and a shallow porch. It supplies site-specific entry/frontage construction evidence. Its tiled roof differs from the project's required actual thatch silhouette: retain thatch, rough low fence and painted paddy, and collect the separate close thatch/material reference. This photo does not establish farmhouse dimensions or the required night lighting. Attribution, license and original-byte integrity are saved beside the image. Other reference slots remain open.


## Collected thatch material reference — 2026-10-08

Slot 3: [original reed close-up](../reference/external/daoxiang-cun/reed-thatch-close.jpg), Titus Tscharntke, published author public-domain release. Close reed thatch shows packed narrow stems, exposed blunt and hollow ends, uneven stalk lengths and parallel bundles. Dark gaps between stems supply small-scale relief and roughness guidance for the required farmhouse thatch. The photo does not establish Daoxiang identity, Chinese roof construction, ridge/eave silhouette, roof thickness or night lighting; use it only for the distinguishing material slot. Attribution and original-byte hashes are saved beside the image. The night-set slot remains open.

## Collected Shaw night-set reference — 2026-10-08

Slot 1 now has a directly reviewed frame from the published *Come Drink With Me* trailer at 24.607917 seconds. The frame shows a thatched rustic dwelling with exposed bundles along the eave, rough matte walls, narrow timber/bamboo poles and a simple rail. Cool blue-gray fog separates the dark foreground and warm brown timber/red costume. Night or dusk appearance is inferred from the dark, cool scene treatment; no source caption supplies its time of day. This fills the generic Shaw built-set/lighting slot, not Daoxiang identity, measured thatch thickness, roof dimensions or an amber-door practical. Use neutral rough walls and brown thatch against restrained cool background rather than copying a uniform green grade.

Attribution, rights information, original stream hash and exact decoded-frame provenance: `../reference/external/daoxiang-cun/README.md`. All three reference slots are collected. This does not establish final scene art, lighting, performance or service acceptance.


## Runtime portrait framing — 2026-10-09

The runtime portrait view is now centered and closer, with the thatched farmhouse occupying at least 75% of the width above the command panel. Normal runtime lamps illuminate the doors in the inspected full-walk arrival. Painted backdrop edges, coarse shadow/material treatment and final art remain open. “Look” restores this overview after a detail action; resizing preserves details or adapts the overview. Existing desktop and authored Blender cameras remain unchanged. See `../reference/portrait-architecture-runtime/README.md`.
