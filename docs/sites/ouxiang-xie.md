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


## Shared prop placement — 2026-10-04

The existing dressing now uses fitted prop-library meshes with a shared PBR atlas. Mount positions, seat/table heights, collision, lights and triggers are retained. The site’s props export as one material batch and stop drawing beyond 28 metres. Desktop and portrait views were reviewed; source-hash-checked bakes apply where this site belongs to the demo or priority-2 catalog. Further art, sourced references and final lighting remain open. Details: `../kits/props.md`.


### Current lighting coverage — 2026-10-04

All eligible opaque meshes in this saved site now have current source-matched Cycles lightmaps in the full Godot catalog. Native pixels and engine copies are checked; normal exploration uses the maps with static shadow maps disabled. Desktop and portrait arrival captures are refreshed under `docs/reference/route-*-full-baked.png`. Final color, material, noise/texel-density and external reference acceptance remain open.


## Owned backdrop wash — 2026-10-06

`LGT_ouxiang_xie_backdrop_wash` is saved in authoring and `SITE_ouxiang-xie.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_ouxiang-xie_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.

The owned-key pass below completes the missing-key inventory requirement. Final light and shadow quality remains under review.


## Owned key source — 2026-10-07

`LGT_ouxiang-xie_key` is now saved in authoring and the directly openable site library: a 450 W Spot with 65° cone, zero edge blend and 0.01 m source radius, aimed at the tea table. Its muted green follows the user’s palette revision. Native checks require a single positive owned key, hard shadows and the intended direction/target; they failed before this pass and pass afterward. The shared light named `LGT_stage_green_key` now has neutral cool RGB (0.70, 0.74, 0.78), energy 1.4.

Geometry, materials, images, collision and camera data are unchanged in the new export; the three keys and shared-fill settings are the changes. All 124 ordinary maps were freshly rebaked at 128 samples because the Sun/shared fill affects the whole assembly. The native wash was also refreshed at 128 samples/512². Godot now uses the current source `d74e0ff858748d529029c80f0ea11969c121dd71f645effebf55180104099bde` and hash-matched maps. Imported-key, full-lighting, wash, material and demo-startup checks pass. Desktop and 390 × 844 portrait arrival views are refreshed. Final shadow dominance, palette, materials, filtering and moving-camera acceptance remain open.


## Strict Spot cone export — 2026-10-08

The saved key edge blend is now 0.0001 instead of zero: glTF requires an inner angle smaller than its outer angle. The full cone remains 65° and its 0.01 m source radius, energy, color, target and placement are retained. An isolated cold Godot import has no errors or warnings and preserves the 32.5° half-angle and hard cone falloff (angle attenuation 1999.568). The canonical assembly and this site export are corrected. Production Godot remains on the preceding complete lighting set until the running fresh 124-map/wash/spill refresh passes; final rendered acceptance is pending. Evidence: `../../export/roof-cone-export-preservation.json` and `../../export/roof-cone-runtime-checks.json`.


## External foliage/material reference — 2026-10-08

The slot-3 close reference is collected, directly reviewed and attributed in `../reference/external/ouxiang-xie/README.md`. A broad rounded lotus leaf with a gently undulating edge, radial veins, matte waxy surface and distinct water beads; a pale pink petal provides scale and color contrast. Useful for leaf/material detail, not architecture or night lighting. Original bytes match the Commons SHA-1. The night-set and architecture slots remain uncollected. This is reference collection, not acceptance of the current foliage mesh or material.


## Collected water-pavilion architecture reference — 2026-10-08

Slot 2: [original water-pavilion view](../reference/external/ouxiang-xie/oux-pavilion-over-water.jpg), a Sipa Photo image published in the [Beijing Tourism Ouxiang gallery](https://s.visitbeijing.com.cn/gallery/19014), 2022-05-20. The open red-column pavilions, connecting covered gallery, low geometric rails and raised platforms above water guide structure and access. Gray tiled eaves, painted blue/green/gold beams and lanterns guide material separation; the visible reflections expose platform supports. The gallery supplies the site identification. Exact dimensions, six-seat furniture, original historical construction and night lighting are not established. The watermark and original bytes are retained with copyrighted-source attribution. The night-set slot remains missing.


## Isolated roof and portrait comparison — 2026-10-08

Saved-source inspection matches all 168 closed tile cylinders and the roof shell to unique exported components. Their subpixel UV2 charts have a separate geometry-preserving proposal with fresh 128-sample roof lighting. Upward side zero samples fall 117/1344 to 0/1344; cap zeros persist. Actual 512px lossless native views look cleaner than actual 256px lossless or compressed imports. A lower/further portrait pose reveals more platform and water. This roof/camera proposal is uninstalled: default exporter equivalence, complete matching lighting, final framing/materials and memory/device checks remain open. See [the native comparison](../reference/ouxiang-roof-native/README.md).
