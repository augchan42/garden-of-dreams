# Site sheet: 凸碧堂

Slug `tubi-tang`. Priority 2. Function: Current events pavilion. Room id `tubi_tang`.

## Stage direction

A hall occupies the highest terrace. The climb should gradually expose the garden and then the painted cyclorama beyond it. The terrace edge frames the view without hiding that this is a stage.

## Dimensions and access

Terrace floor 4 m above origin; 2.2 m stair width; 3.1 m eaves above terrace. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

Plaster hill; terrace; steps with collision; low parapet; stone topic table; one amber lantern. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Amber hard key at the hall; green wash on the distant garden. The terrace, parapets, twenty treads and topic table use a warmer site-specific plaster so the occupied hilltop does not inherit the stage's full green cast. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Stair foot; terrace arrival; news table; overlook; return to stair. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_tubi_tang_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

Establishing view includes the central pavilion below and the edge of the painted sky. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

Sourced leads reviewed: [Beijing municipal tourism’s Grand View Garden page](https://s.visitbeijing.com.cn/attraction/101918) describes the elevated viewing hall and perimeter seating in the modern reconstruction. The [National Museum’s *Grand View Garden* painting record](https://www.chnmuseum.cn/zp/zpml/ysp/202101/t20210112_248877.shtml) supports its moon-viewing role, not measured architecture. Neither is a Shaw night-set still or a material close-up. Those two references remain to be collected.

## Current build and acceptance

The public terrace now has low side/front parapets, two short wood viewing benches, a stone topic table, one amber lantern and five action markers. Twenty visible treads rise four metres; a separate simplified ramp collider supplies continuous capsule movement. The approach runs around the west side of the bulletin hall. `test_hilltop_route.gd` passes the climb to four metres and return descent through actual imported collision geometry; `test_study_route.gd` still passes the shared approach. Godot provides Current Events and an overlook action; the hall interior stays closed.

Desktop and portrait arrival, overlook, table and live-event views are saved as `docs/reference/route-hilltop*.png` and `route-mobile-hilltop*.png`. The live browser filters the public endpoint to temporal topics and does not create readings.

The temporary typeset sign has been replaced with original brush-painted 凸碧堂 lettering on the existing wood board. The source art and prompt are in `textures/decals/hilltop/README.md`; this is production art, not a sourced historical still. The site-specific plaster and sign were checked in desktop and portrait Godot arrival views. The initial plaster pass lowered the terrace and stair regions' green-to-red mean-channel ratio to about 2.2 from 4.8–5.4; the later softer stage light and 20% grade reduce the green further. Nine opaque hall meshes now have current Cycles lightmaps applied in the normal Godot exploration route, including the warm terrace plaster; the transparent painted title retains its source material. Desktop and portrait arrival, overlook and table views were inspected after the bake. The climb, overlook and descent still pass through imported collision. The Shaw night-set still, material close-up, light-linked backdrop wash and final material acceptance remain unfinished. The whole-garden export, hilltop bake and demo bake share a source hash.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.
