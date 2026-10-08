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

Current saved references and any unfilled slots are recorded below and in the external reference README.

## Current build and acceptance

The placeholder hall has been removed. A low stone island, reeds, landing and timber footbridge now occupy the site. Three action markers and two cameras are exported. Godot traversal from the water pavilion and back passed with floor support. The graded Blender reference is `../reference/ziling-zhou.png`; the engine view is `../reference/route-ziling.png`. Final foliage/material work and sourced references remain unfinished.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.


### Water-kit integration

The six-metre water-kit wooden bridge replaces the old footbridge, overlapping both the pavilion and island landings. Its deck and two rail colliders remain separate. Two six-leaf lotus clusters replace the old pad cylinders beside the island; reeds, rocks, landing and markers are preserved. The bridge uses the shared architectural atlas. Final foliage/lotus materials, lighting, references, runtime LOD switching and phone acceptance remain open.


## Flora placement — 2026-10-04

Ten atlas-textured reed clumps replace the previous individual reeds around the landing, preserving the clear footbridge approach. All placed plants share one compressed runtime atlas and switch detail with distance. The assembly export and editable site libraries are synchronized. Further dressing, final lighting and sourced references remain open.


### Current lighting coverage — 2026-10-04

All eligible opaque meshes in this saved site now have current source-matched Cycles lightmaps in the full Godot catalog. Native pixels and engine copies are checked; normal exploration uses the maps with static shadow maps disabled. Desktop and portrait arrival captures are refreshed under `docs/reference/route-*-full-baked.png`. Final color, material, noise/texel-density and external reference acceptance remain open.


## Owned backdrop wash — 2026-10-06

`LGT_ziling_zhou_backdrop_wash` is saved in authoring and `SITE_ziling-zhou.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_ziling-zhou_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.

The owned-key pass below completes the missing-key inventory requirement. Final light and shadow quality remains under review.


## Owned key source — 2026-10-07

`LGT_ziling-zhou_key` is now saved in authoring and the directly openable site library: a 400 W Spot with 65° cone, zero edge blend and 0.01 m source radius, aimed at the reed overlook. Its muted green follows the user’s palette revision. Native checks require a single positive owned key, hard shadows and the intended direction/target; they failed before this pass and pass afterward. The shared light named `LGT_stage_green_key` now has neutral cool RGB (0.70, 0.74, 0.78), energy 1.4.

Geometry, materials, images, collision and camera data are unchanged in the new export; the three keys and shared-fill settings are the changes. All 124 ordinary maps were freshly rebaked at 128 samples because the Sun/shared fill affects the whole assembly. The native wash was also refreshed at 128 samples/512². Godot now uses the current source `d74e0ff858748d529029c80f0ea11969c121dd71f645effebf55180104099bde` and hash-matched maps. Imported-key, full-lighting, wash, material and demo-startup checks pass. Desktop and 390 × 844 portrait arrival views are refreshed. Final shadow dominance, palette, materials, filtering and moving-camera acceptance remain open.


## Strict Spot cone export — 2026-10-08

The saved key edge blend is now 0.0001 instead of zero: glTF requires an inner angle smaller than its outer angle. The full cone remains 65° and its 0.01 m source radius, energy, color, target and placement are retained. An isolated cold Godot import has no errors or warnings and preserves the 32.5° half-angle and hard cone falloff (angle attenuation 1999.568). The canonical assembly and this site export are corrected. Production Godot remains on the preceding complete lighting set until the running fresh 124-map/wash/spill refresh passes; final rendered acceptance is pending. Evidence: `../../export/roof-cone-export-preservation.json` and `../../export/roof-cone-runtime-checks.json`.


## External foliage/material reference — 2026-10-08

The slot-3 close reference is collected, directly reviewed and attributed in `../reference/external/ziling-zhou/README.md`. Tall jointed stems, long narrow drooping leaves and fine tawny-purple branching plumes, with varied angles and clear gaps between stems. Useful for reed silhouette and plume/leaf density; the daylight sky and lighting are not the scene palette. Original bytes match the Commons SHA-1. The night-set and architecture slots remain uncollected. This is reference collection, not acceptance of the current foliage mesh or material.


## Collected entrance architecture reference — 2026-10-08

Slot 2: [original photograph](../reference/external/ziling-zhou/ziling-entrance-plaque.jpg), 朱華龍 - Zhu Hua Long, CC BY 2.0. The visible plaque reads 紫菱洲 from right to left, identifying the modern Ziling entrance. Paired red timber doors, a gray barrel-tile eave, painted crossbeams and white plaster side walls supply site-specific entrance construction. This photo does not show the island, reeds, landing or footbridge and does not prescribe replacing the project's low island with a gatehouse. Island/bridge composition and night lighting still need separate art review. Full attribution and original-byte hashes are saved beside the image. The night-set slot remains open.

## Collected Shaw night-set reference — 2026-10-08

Slot 1 now has a directly reviewed frame from the published *The Enchanting Shadow* trailer at 11.0 seconds. A ruined brick opening and sparse table/bench dressing are framed by dark foliage; blue-lit leaves and masonry edges sit beside a warmer lit figure. Large black gaps keep the foreground sparse and layered. Night appearance is visually inferred from the dark exterior and directed cool/warm treatment. This guides generic night foliage and built-set composition, not Ziling identity, reed species, island geometry, waterline or footbridge construction. The separate close reed reference supplies botanical form; the saturated source blue is qualitative lighting guidance.

Attribution, rights information, original stream hash and exact decoded-frame provenance: `../reference/external/ziling-zhou/README.md`. All three reference slots are collected. This does not establish final scene art, lighting, performance or service acceptance.
