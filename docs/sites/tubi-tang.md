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

Current saved references and any unfilled slots are recorded below and in the external reference README.

Sourced leads reviewed: [Beijing municipal tourism’s Grand View Garden page](https://s.visitbeijing.com.cn/attraction/101918) describes the elevated viewing hall and perimeter seating in the modern reconstruction. The [National Museum’s *Grand View Garden* painting record](https://www.chnmuseum.cn/zp/zpml/ysp/202101/t20210112_248877.shtml) supports its moon-viewing role, not measured architecture. Neither is a Shaw night-set still or a material close-up. The current collected references and remaining night-set slot are documented below.

## Current build and acceptance

The public terrace now has low side/front parapets, two short wood viewing benches, a stone topic table, one amber lantern and five action markers. Twenty visible treads rise four metres; a separate simplified ramp collider supplies continuous capsule movement. The approach runs around the west side of the bulletin hall. `test_hilltop_route.gd` passes the climb to four metres and return descent through actual imported collision geometry; `test_study_route.gd` still passes the shared approach. Godot provides Current Events and an overlook action; the hall interior stays closed.

Desktop and portrait arrival, overlook, table and live-event views are saved as `docs/reference/route-hilltop*.png` and `route-mobile-hilltop*.png`. The live browser filters the public endpoint to temporal topics and does not create readings.

The temporary typeset sign has been replaced with original brush-painted 凸碧堂 lettering on the existing wood board. The source art and prompt are in `textures/decals/hilltop/README.md`; this is production art, not a sourced historical still. The site-specific plaster and sign were checked in desktop and portrait Godot arrival views. The initial plaster pass lowered the terrace and stair regions' green-to-red mean-channel ratio to about 2.2 from 4.8–5.4; the later softer stage light and 20% grade reduce the green further. Nine opaque hall meshes now have current Cycles lightmaps applied in the normal Godot exploration route, including the warm terrace plaster; the transparent painted title retains its source material. Desktop and portrait arrival, overlook and table views were inspected after the bake. The climb, overlook and descent still pass through imported collision. A broad linked Area light now washes only the painted backdrop in Blender; Godot applies a backdrop-only runtime substitute. The Shaw night-set still, material close-up and final material acceptance remain unfinished. The whole-garden export, hilltop bake and demo bake share a source hash.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.


## Shared prop placement — 2026-10-04

The existing dressing now uses fitted prop-library meshes with a shared PBR atlas. Mount positions, seat/table heights, collision, lights and triggers are retained. The site’s props export as one material batch and stop drawing beyond 28 metres. Desktop and portrait views were reviewed; source-hash-checked bakes apply where this site belongs to the demo or priority-2 catalog. Further art, sourced references and final lighting remain open. Details: `../kits/props.md`.

The runtime bake adapter now corrects Cycles diffuse transfer for Compatibility and isolates baked receivers from static keys while preserving shadow-caster masks. Desktop and portrait views are refreshed; final material, bake noise and texel-density acceptance remain open. See `../baked-lighting.md`.


## Owned backdrop wash — 2026-10-06

`LGT_tubi_tang_backdrop_wash` is saved in authoring and `SITE_tubi-tang.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_tubi-tang_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.


## Collected hilltop architecture reference — 2026-10-08

The slot-2 hilltop photograph is collected, directly reviewed and attributed in `../reference/external/tubi-tang/README.md`. An elevated hall on a rocky rise, with thick red columns, a continuous gray tiled eave, painted blue-green brackets, pierced geometric lintel screens, a low green balustrade and hanging lanterns. The visible plaque reads 凸碧山莊. Useful for hilltop frontage, stock construction and roof/rail proportions; this close upward view does not establish terrace height, stair geometry or the required night lighting. Original bytes match the Commons SHA-1. The night-set slot remains uncollected; the material slot is documented below. This is reference collection, not scene acceptance.


## Collected table material reference — 2026-10-08

Slot 3 now retains an unmodified, directly reviewed original by Pseudopanax with an author public-domain release. Its close foreground stone table supplies granular surface, rounded edge, perimeter groove and pedestal/stool finish observations. The photograph is from Hamilton Gardens, not Tubi; it supplies material evidence only. No architectural identity, nighttime lighting, measured proportions or scanned production texture is claimed. Attribution and byte checks: `../reference/external/tubi-tang/README.md`. Tubi now has two of three collected references; the Shaw Brothers night-set slot and final scene art acceptance remain open.

## Collected Shaw night-set reference — 2026-10-08

Slot 1 now has a directly reviewed frame from the published *The Enchanting Shadow* trailer at 3.0 seconds. A tiered pagoda-like upright form is illuminated blue through a dark mesh of branches, with near-black surroundings and small warm/red detail. Night appearance is visually inferred. It demonstrates separating an elevated architectural silhouette from foreground foliage with a restricted cool wash while retaining darkness. This fills the generic Shaw night-set lighting slot, not Tubi identity, hill height, stair count, terrace dimensions or the required stone table. It is not a source model or a detailed construction photograph.

Attribution, rights information, original stream hash and exact decoded-frame provenance: `../reference/external/tubi-tang/README.md`. All three reference slots are collected. This does not establish final scene art, lighting, performance or service acceptance.


## Portrait arrival and garden-overlook framing — 2026-10-09

The painted moon, hall/title and complete staircase now fit above portrait controls at both tested widths, including touch-size and desktop density-scaled layouts. A lower fixed camera uses bounded portrait variants; desktop arrival retains its original transform. The higher garden-overlook camera shows the central bridge pavilion beyond the nearer roof. Resize preserves overlook selection/text, and Look returns to arrival. A stable 128-unit list keeps 48-unit touch targets and its final action reachable by scrolling.

Three final focused modes pass with thirty original PNGs; thirteen adjacent checks include the actual climb/descent and study route. The archive retains 215 originals and 312 checked files. Actual failing actions and the density rotation/wrapping diagnostic remain archived. Seven final originals were inspected. Geometry, saved source cameras, collision and lighting remain unchanged. Evidence: `../reference/tubi-portrait-framing/README.md` and `../../export/tubi-portrait-framing-evidence.json`. Desktop density is not phone acceptance. Small ceiling strips, background/stage edges, surface refinement and final scene art remain open.

## Waterline and reed source checkpoint — 2026-10-09

The combined Blender source is now `0d3e84e3`; export and Godot use `1380ceca`. The complete fresh lighting set covers 124 ordinary receivers and 141 source PNGs, with matching wash/spill catalogs. Both native Mac tours visit all fourteen sites over twenty-six public-command legs and return to the cell, with no floor misses and at most four practical lights. All 42 camera, 400 collider and 71 marker contracts are preserved. This is an incremental working-source checkpoint; final site art, references, phone/sustained performance and authenticated services remain open. Evidence: `../reference/ziling-source-art/README.md`.


## Stream bank and lotus checkpoint — 2026-10-09

The current complete source is `7a9fc523` with authoring `074ab201`. The shared stream has 54 bank modules and 54 added colliders; all 42 cameras,400 earlier colliders and 71 markers are preserved. Closed circular lotus pads sit above the water, with a muted shared leaf material and matching saved kit/generator. Fresh lighting covers 124 receivers and 141 source PNGs. Both native Mac tours pass 14 locations and 26 travel legs;15 installed checks pass. This is an incremental source checkpoint. Final site art, five remaining reference slots, current phone/sustained performance, release and authenticated services remain open. Evidence: `../reference/water-edge-source/README.md`.


## Island exterior winding checkpoint — 2026-10-09

Current assembly `73267e2b` / authoring `2b07ce48` repairs the reed island’s exterior face winding. All other exported mesh attributes and fourteen other site GLBs are preserved; cameras, colliders, markers and runtime are unchanged. Complete matching lighting, twenty-five focused native checks and thirteen installed checks pass. This site is not declared final by the island repair. Five references, current phone/sustained budgets, release and authenticated services remain open. Evidence: [island source review](../reference/island-exterior-winding/README.md).


## Neutral stage-floor checkpoint — 2026-10-09

Current complete source is `c9d4fb30`; authoring is `43d7e33e`. The five broad canvas floor pieces use muted warm gray (.065,.060,.055 linear RGB). Other materials, geometry, cameras, collisions, markers and runtime are preserved. All 141 fresh lightmaps, six source phases, 38 positive native checks plus two intended rejection controls, both 14-room/26-leg tours and 15 installed checks pass. All 47 installed lit/Ziling/arrival originals reproduce the reviewed candidate exactly. References remain 37/42; this is palette repair acceptance, not final site or phone acceptance. Evidence: [neutral stage floor](../reference/stage-floor-palette/README.md).


## Paving-source checkpoint — 2026-10-10

Current assembly is `ba40866e` with authoring `7eba169a`. Duplicate visible paving tops are partitioned while retaining the complete floor footprint, all 454 colliders, 42 cameras, 71 markers, materials and runtime `7970380d`. Complete matching 141 PNG lighting, both actual Mac 14-room/26-leg tours and 22 installed checks pass; all 85 installed originals reproduce the reviewed files. All 28 current arrival originals were directly inspected. This is focused paving acceptance; this site's final art is still open. References remain 37/42; current phone/sustained/release and authenticated services remain required. Evidence: [paving repair](../reference/paving-surface-joins/README.md).
