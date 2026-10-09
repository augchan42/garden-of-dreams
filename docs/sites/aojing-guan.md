# Site sheet: 凹晶館

Slug `aojing-guan`. Priority 4. Function: Water reflection dressing. Room id `aojing_guan`.

## Stage direction

The hall sits low at the water edge. Its window and roof should form a readable reflection; an accessible dry ledge gives the player a place to stop.

## Dimensions and access

Floor -0.65 m; water -1.1 m; 7 m facade; 1.8 m dry ledge. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Low hall; dry ledge; embankment; one amber window; water surface with reflection treatment. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Amber window against green reflected sky; minimal frontal fill. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Ledge arrival; reflection viewpoint; return to east path. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_aojing_guan_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

Keep the horizon high enough to give water and reflection half the frame. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

Current saved references and any unfilled slots are recorded below and in the external reference README.

## Current build and acceptance

The generic hall has been replaced by a low seven-metre facade with one amber window, dark shutters and a continuous broad roof. Its 1.8 m dry ledge is at -0.65 m, with a guarded descending ramp and pond at -1.1 m. Raised stage canvas was removed beneath the site. Three markers and four cameras are exported.

The red court’s “Visit the water-level hall” action reaches the ledge. A separate pond shader now shows the actual window and roof through a mirrored-camera capture, tinted green and distorted by animated ripples. Fixed-time renderer comparisons verify that excluding the window from the capture removes only its reflected image. Desktop and portrait views were inspected. See `docs/pond-reflection.md`. Final lighting and sourced reference stills remain open; this is not final site acceptance.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.

## Painted title — 2026-10-04

The temporary Songti glyph geometry is replaced by original painted 凹晶館 lettering on the wood board. Its wood board now projects 0.60 m forward of the original mount, on two short wood supports, clearing the previously intersecting roof eave. The texture preserves its generated alpha and image aspect ratio; Godot uses compressed mipmapped 512px imports. Cameras, lights, triggers and collision records remain unchanged. Original artwork and provenance: `../../textures/decals/garden-signs/README.md`. Final material/lighting acceptance and external visual references remain open.


## Runtime camera review — 2026-10-04

The arrival uses a centered desktop view with a wider 70° vertical FOV, keeping the roof and reflected window visible above the command panel. The separate pond action is described below. Portrait uses its own closer, downward-looking 55° horizontal view to reduce empty sky. The six current arrival/door/pond screenshots replace the earlier green-grade captures. The reviewed views are now stored in Blender and used directly by Godot. The pond action now has a separate water-dominant view; the visible water area exceeds half the frame in both aspects. See `../pond-reflection.md` for positions and renderer checks.


## Source camera alignment — 2026-10-04

`CAM_aojing-guan_wide` and `CAM_aojing-guan_portrait` store the arrival shots. `CAM_aojing-guan_reflection` and `CAM_aojing-guan_reflection_portrait` store the separate pond shots. The saved library has landscape and portrait scenes for each view, sharing the same editable collection. The exporter preserves each camera's viewport and projection; the runtime reads the imported position, orientation and FOV.

`test_reflection_camera_alignment.gd` compares actual window and pond screen projections in both aspects, checks the mirrored camera and checks default FOV restoration at the next site. The export preservation report verifies unchanged binary geometry/image data, material/mesh records and all 497 collision/trigger/light records. Final lighting and reference acceptance remain open.


## Water-dominant pond view — 2026-10-04

“Look across the pond” hides the command panel and moves to a fixed waterline camera. Return to ledge or Escape restores the arrival camera and controls. The visitor stays on the collision-supported dry ledge. Rotation switches between the authored desktop and portrait shots, and the return button keeps a 44px minimum height.

Desktop position is (26, -0.5, 20.7), target (26, -1.7, 14), with 70° vertical FOV. Portrait uses the same position, target (26, -2.5, 14), and 68° horizontal FOV. All roof vertices fit inside both viewports. Flat-color depth-tested renders measure 54.9% visible water at 1410 × 600 and 57.0% at 390 × 844. The scene library has four cameras and four editable scenes for arrival/pond in each aspect. The existing guarded visitor route remains constrained; this is a camera move, not a move into the pond.

The current reflection checks distinguish the actual reflected window and moving ripples. Final art/lighting acceptance is still open: a stationary desktop profile reports 832 combined main/capture draw calls, above the 150-call target. Static-key isolation and the all-site lighting/material pass must address this. External references and phone/full-traversal performance are also open.


### Current lighting coverage — 2026-10-04

All eligible opaque meshes in this saved site now have current source-matched Cycles lightmaps in the full Godot catalog. Native pixels and engine copies are checked; normal exploration uses the maps with static shadow maps disabled. Desktop and portrait arrival captures are refreshed under `docs/reference/route-*-full-baked.png`. Final color, material, noise/texel-density and external reference acceptance remain open.


## Owned backdrop wash — 2026-10-06

`LGT_aojing_guan_backdrop_wash` is saved in authoring and `SITE_aojing-guan.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_aojing-guan_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.


## Collected facade reference — 2026-10-08

Architecture slot 2 now retains Beijing Tourism's named facade image. Direct review reads 凹晶溪館 on the plaque and shows a broad gray-tiled roof, painted lintel members, timber columns and glazed lattice doors. It supports facade/window construction, without proving the measured frontage, waterline, reflection, complete dry ledge or one amber nighttime window. The publisher watermark and copyright attribution remain; no open reuse licence or individual photographer is invented. Original bytes and source version: `../reference/external/aojing-guan/README.md`. Night-set/material close-view references and final scene art remain open.

## Collected Shaw night-set reference — 2026-10-08

Slot 1 now has a directly reviewed frame from the published *The Magic Blade* trailer at 5.0 seconds. A wet night lane has pale plaster walls, octagonal openings, puddle highlights, dark foreground cart/timber silhouettes and small warm lights at the distant gate. Blue/cool wall light and warm practicals separate materials without lighting the entire foreground. Night appearance is a visual inference from the dark exterior and visible lamps. This supplies the generic night-set lighting slot only: it is a street, not Aojing or a water-level reflection hall, and proves no pond waterline, dry ledge, facade dimensions or one-window placement. The low-resolution frame cannot establish fine plaster texture.

Attribution, rights information, original stream hash and exact decoded-frame provenance: `../reference/external/aojing-guan/README.md`. Remaining reference slots: 3. This does not establish final scene art, lighting, performance or service acceptance.

## Completed reference collection — 2026-10-08

Slot 3 now has a directly reviewed sourced reference. The close photograph shows dull weathered timber grain, chipped pale paint along the jambs and glazing bars, recessed clear panes, dark reflected foliage and thin surface dirt/webs. It supplies a timber-and-glazing surface reference for Aojing's shutter/window dressing. This is not verified Chinese or Aojing architecture, a survey, night lighting or a prescription to copy the shingle facade, pediment, grid proportions or extreme paint decay. Use grain/roughness and glass contrast only; retain the game's authored dark shutters, single amber window and stage-set treatment.

All three slots are collected; attribution, rights, originals and hashes are recorded in `../reference/external/aojing-guan/README.md`. This does not establish final scene art or rendering/device/service acceptance.

## Waterline and reed source checkpoint — 2026-10-09

The combined Blender source is now `0d3e84e3`; export and Godot use `1380ceca`. The complete fresh lighting set covers 124 ordinary receivers and 141 source PNGs, with matching wash/spill catalogs. Both native Mac tours visit all fourteen sites over twenty-six public-command legs and return to the cell, with no floor misses and at most four practical lights. All 42 camera, 400 collider and 71 marker contracts are preserved. This is an incremental working-source checkpoint; final site art, references, phone/sustained performance and authenticated services remain open. Evidence: `../reference/ziling-source-art/README.md`.

The saved pond base color is now dark blue-gray (linear RGB 0.022, 0.03, 0.04), matching the reduced-green direction already present in Godot. Its surface height and geometry, reflection shader, cameras and walk surfaces remain unchanged. Reflected roof/window remain visible in directly reviewed arrival and settled-tour images. Stage/path closure and actual phone reflection cost remain open.


## Stream bank and lotus checkpoint — 2026-10-09

The current complete source is `7a9fc523` with authoring `074ab201`. The shared stream has 54 bank modules and 54 added colliders; all 42 cameras,400 earlier colliders and 71 markers are preserved. Closed circular lotus pads sit above the water, with a muted shared leaf material and matching saved kit/generator. Fresh lighting covers 124 receivers and 141 source PNGs. Both native Mac tours pass 14 locations and 26 travel legs;15 installed checks pass. This is an incremental source checkpoint. Final site art, five remaining reference slots, current phone/sustained performance, release and authenticated services remain open. Evidence: `../reference/water-edge-source/README.md`.


## Island exterior winding checkpoint — 2026-10-09

Current assembly `73267e2b` / authoring `2b07ce48` repairs the reed island’s exterior face winding. All other exported mesh attributes and fourteen other site GLBs are preserved; cameras, colliders, markers and runtime are unchanged. Complete matching lighting, twenty-five focused native checks and thirteen installed checks pass. This site is not declared final by the island repair. Five references, current phone/sustained budgets, release and authenticated services remain open. Evidence: [island source review](../reference/island-exterior-winding/README.md).
