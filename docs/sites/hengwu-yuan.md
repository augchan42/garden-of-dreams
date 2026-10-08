# Site sheet: 蘅蕪苑

Slug `hengwu-yuan`. Priority 3. Function: Study circles. Room id `hengwu_yuan`.

## Stage direction

Bare stones and low herbs fill an enclosed court. Keep the skyline free of trees. A study table occupies a clean patch of stone paving, with rooms suggested by shallow fronts.

## Dimensions and access

7 m hall frontage; courtyard roughly 9 × 8 m; 1.8 m paths. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Perforated plaster rocks; herb beds; study table; stools; courtyard wall; leak windows. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Hard green key picks out the rock edges; one amber room practical. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Court entrance; study table; rock inspection; return path. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_hengwu_yuan_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

A low, still camera makes the stones prominent without blocking the table. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

Current saved references and any unfilled slots are recorded below and in the external reference README.

## Current build and acceptance

The 9 × 8 m court now has side walls with diamond and ice-crack lattice openings, a moon gate, low herb beds, a study table and four stools. Three distinct perforated plaster stones replace the solid rock dressing; nine centre-line BVH rays pass through their holes. No trees were added.

Four markers identify entry, table, rock inspection and return. The Qinfang approach turns beyond the covered walk’s end to avoid its railing, then follows the existing northward stone walk. `test_courtyard_route.gd` passes outward and return physics traversal with floor support; the existing western pavilion/island route also passes.

Local book and rock inspection actions are available. Ongoing Topics uses the existing public feed filtered to timeless topics; both desktop and portrait checks loaded five topics. Shared study-circle sessions are explicitly unconnected.

Source script: `scripts/refine_study_courtyard.py`. Reference captures: `docs/reference/route-courtyard*.png` and `route-mobile-courtyard*.png`. Final painted signs, sourced reference stills, material atlases, the prescribed backdrop wash and a fresh light bake remain unfinished. The three court rocks do not complete the six-variant rockery kit.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.

## Wall-kit integration

Nine textured modules now enclose the original 9 × 8 m court: six solid bays, two lattice windows and one moon gate. Side bays are scaled along their width to fit the eight-metre depth. Nine separate collision meshes accompany the walls. The rocks, herbs, study furniture, closed hall and markers remain in place. Reproduce with `scripts/integrate_hengwu_walls.py`.

The wall atlas contributes one material batch and three shared compressed maps. Overlapping window-frame corner faces were corrected in the source kit by using butt joints; the full assembly now passes the sampled lightmap-UV overlap check. Courtyard and farmhouse routes pass through the gate in both directions. Tests also check both windows and gate-side piers for blocking collision.

Portrait arrival keeps its camera inside the courtyard; the previous generic pullback moved it behind the taller front wall. Final lighting, painted signs, references and phone performance remain open.


## Shared prop placement — 2026-10-04

The existing dressing now uses fitted prop-library meshes with a shared PBR atlas. Mount positions, seat/table heights, collision, lights and triggers are retained. The site’s props export as one material batch and stop drawing beyond 28 metres. Desktop and portrait views were reviewed; source-hash-checked bakes apply where this site belongs to the demo or priority-2 catalog. Further art, sourced references and final lighting remain open. Details: `../kits/props.md`.

## Painted title — 2026-10-04

The temporary Songti glyph geometry is replaced by original painted 蘅蕪苑 lettering on the wood board. The texture preserves its generated alpha and image aspect ratio; Godot uses compressed mipmapped 512px imports. Cameras, lights, triggers and collision records remain unchanged. Original artwork and provenance: `../../textures/decals/garden-signs/README.md`. Final material/lighting acceptance and external visual references remain open.


### Current lighting coverage — 2026-10-04

All eligible opaque meshes in this saved site now have current source-matched Cycles lightmaps in the full Godot catalog. Native pixels and engine copies are checked; normal exploration uses the maps with static shadow maps disabled. Desktop and portrait arrival captures are refreshed under `docs/reference/route-*-full-baked.png`. Final color, material, noise/texel-density and external reference acceptance remain open.


## Owned backdrop wash — 2026-10-06

`LGT_hengwu_yuan_backdrop_wash` is saved in authoring and `SITE_hengwu-yuan.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_hengwu-yuan_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.


## Collected references — 2026-10-08

Slot 2: [original photograph](../reference/external/hengwu-yuan/hengwu-entrance-plaque.jpg), by 朱華龍 - Zhu Hua Long, CC BY 2.0. The visible entrance plaque reads 蘅蕪苑 from right to left, identifying the site. A low gray barrel-tile eave, red columns and door surround, blue/green/gold painted beams and irregular ice-crack lattice flank the opening. This supports courtyard entrance, fretwork and beam construction. The cropped daylight photograph does not establish the whole courtyard, herb/rock layout, dimensions or night lighting. Attribution, license and original-byte integrity are saved beside the image. Other reference slots remain open.

Slot 3: [original photograph](../reference/external/hengwu-yuan/ice-crack-lattice-close.jpg), by 朱華龍 - Zhu Hua Long, CC BY 2.0. A close view of four pale painted wood screen leaves with irregular ice-crack lattice around two rectangular clear panes per leaf, carved lower panels and visible joints/hinges. It supports the Hengwu courtyard leak-window material and pattern specified in its wall kit. The photographed building is not identified as Hengwu; this is a distinguishing lattice/material reference, not site-specific architecture, plaster-rock detail or night lighting. Attribution, license and original-byte integrity are saved beside the image. Other reference slots remain open.

## Completed reference collection — 2026-10-08

Slot 1 now has a directly reviewed sourced reference. The frame shows a figure beside broken brick/plaster masonry and a dark geometric lattice opening. Restricted blue light picks out the window and rough masonry edges; warmer brown/amber accents distinguish the near wall and costume while branches and deep openings stay near black. Night appearance is inferred visually from the directed blue light and dark setting; no shot caption supplies the time of day. It fills the generic Shaw night-set lighting/built-set slot, not Hengwu identity, its complete courtyard, herb species, perforated rocks or dimensions. No amber room lamp is visible, and the reference branches do not authorize adding trees to Hengwu's required clear skyline. Use neutral stone/plaster against limited cool fill and warm accents without copying the saturated blue source grade.

All three slots are collected; attribution, rights, originals and hashes are recorded in `../reference/external/hengwu-yuan/README.md`. This does not establish final scene art or rendering/device/service acceptance.

## Foreground stone refinement candidate — 2026-10-09

A native identity capture and saved-source surface inspection locate the crowding at the nearest plaster stone and a side-wall cap. The isolated compact-stone candidate retains the floor anchor and three open holes, reduces width/height and softens its edges. The table, stools, other stones, low herbs and no-tree skyline remain unchanged. Saved-source/export preservation, corrected collider world bounds, actual capsule blocking and both adjacent routes pass. Unbaked native arrival comparisons show a clearer right wall and unchanged table placement. Rock close-up framing and final lighting/art remain open. Fresh complete lighting is running; production is unchanged. See `../reference/hengwu-rock-preparation/README.md` for source, originals, failed controls and remaining acceptance.

## Completed candidate lighting, adoption pending — 2026-10-09

The compact foreground-stone candidate now has completed matching six-phase lighting, preserved saved-source libraries and exact default reexports. Nine arrival/rock/book captures reach their actual completed camera poses; the original frame-count timing error and corrected waits are archived. Selected originals show more court edge beside the compact stone and a readable book/table. Close-up clipping, wall cap, ceiling and final composition remain open. Production still uses the preceding source until the complete rendered review and recoverable adoption pass. See `../reference/hengwu-full-lighting/README.md` and `../reference/hengwu-camera-wait-review/README.md`.


## Compact stone and fresh lighting adoption — 2026-10-09

Saved authoring `19eb386d` / complete source `26033c99` is now installed with matching lighting. Only the nearest pierced stone and its correctly anchored collider change; furniture, other stones, authored cameras and the no-tree skyline remain preserved. Six source bake phases, 47 completed review checks, seven intended rejection controls, sixteen exact default reexports and eleven installed-project checks pass. Both full native desktop and portrait walks pass. Original evidence: `../reference/hengwu-native-review/README.md` and `../../export/hengwu-native-review-evidence.json`.

Nine completed public arrival/rock/book views and four settled walk originals were inspected. The court is less crowded by the nearest stone. Narrow book/rock framing, roof crop, foreground wall cap and facade lighting remain open; final Hengwu art and physical-phone performance are not accepted by this checkpoint.
