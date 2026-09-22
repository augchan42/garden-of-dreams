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

The generic hall has been replaced by a low seven-metre facade with one amber window, dark shutters and a continuous broad roof. Its 1.8 m dry ledge is at -0.65 m, with a guarded descending ramp and pond at -1.1 m. Raised stage canvas was removed beneath the site. Three markers and two cameras are exported.

The red court’s “Visit the water-level hall” action reaches the ledge. A separate pond shader now shows the actual window and roof through a mirrored-camera capture, tinted green and distorted by animated ripples. Fixed-time renderer comparisons verify that excluding the window from the capture removes only its reflected image. Desktop and portrait views were inspected. See `docs/pond-reflection.md`. Final water-dominant composition, source camera alignment, lighting, painted signage and sourced reference stills remain open; this is not final site acceptance.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.
