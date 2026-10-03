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

These are collection requirements, not claims that reference stills have been collected.

## Current build and acceptance

The generic hall has been replaced by a low seven-metre facade with one amber window, dark shutters and a continuous broad roof. Its 1.8 m dry ledge is at -0.65 m, with a guarded descending ramp and pond at -1.1 m. Raised stage canvas was removed beneath the site. Three markers and three cameras are exported.

The red court’s “Visit the water-level hall” action reaches the ledge. A separate pond shader now shows the actual window and roof through a mirrored-camera capture, tinted green and distorted by animated ripples. Fixed-time renderer comparisons verify that excluding the window from the capture removes only its reflected image. Desktop and portrait views were inspected. See `docs/pond-reflection.md`. Final water-dominant composition, lighting and sourced reference stills remain open; this is not final site acceptance.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.

## Painted title — 2026-10-04

The temporary Songti glyph geometry is replaced by original painted 凹晶館 lettering on the wood board. Its wood board now projects 0.60 m forward of the original mount, on two short wood supports, clearing the previously intersecting roof eave. The texture preserves its generated alpha and image aspect ratio; Godot uses compressed mipmapped 512px imports. Cameras, lights, triggers and collision records remain unchanged. Original artwork and provenance: `../../textures/decals/garden-signs/README.md`. Final material/lighting acceptance and external visual references remain open.


## Runtime camera review — 2026-10-04

The arrival and pond action use a centered desktop view with a wider 70° vertical FOV, keeping the roof and reflected window visible above the command panel. Portrait uses its own closer, downward-looking 55° horizontal view to reduce empty sky. The six current arrival/door/pond screenshots replace the earlier green-grade captures. The reviewed views are now stored in Blender and used directly by Godot. The final half-frame water composition still needs review. See `../pond-reflection.md` for positions and renderer checks.


## Source camera alignment — 2026-10-04

`CAM_aojing-guan_wide` and `CAM_aojing-guan_reflection` store the reviewed desktop shot. A third camera, `CAM_aojing-guan_portrait`, stores the portrait shot. The saved library includes a 1410 × 600 landscape scene and a 390 × 844 portrait scene using the same editable collection. The exporter preserves each camera's viewport and projection; the runtime reads the imported position, orientation and FOV.

`test_reflection_camera_alignment.gd` compares actual window and pond screen projections in both aspects, checks the mirrored camera and checks default FOV restoration at the next site. The export preservation report verifies unchanged binary geometry/image data, material/mesh records and all 497 collision/trigger/light records. Lighting and final composition acceptance remain open.
