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

These are collection requirements, not claims that reference stills have been collected.

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
