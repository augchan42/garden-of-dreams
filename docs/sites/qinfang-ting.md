# Site sheet: 沁芳亭 (Qinfang Pavilion)

Slug `qinfang-ting`. Priority 1. Function: Central Gathering Space (design doc section 1).
Room id `qinfang_ting`. Scene origin at the centre of the bridge deck, ground level.

## Stage direction

A hexagonal pavilion on a stone bridge over the 沁芳 stream, the crossroads of the garden.
Covered corridors leave it in four directions and vanish into fog. This is where the live
feed of divinations lives and where other players are seen walking. The pavilion holds a
stone table with a hexagram cast in bronze on its top, and lanterns on all six posts. The
water below reflects the lanterns and the painted moon. Beyond the corridors, the roofs of
the other sites show above the fog as silhouettes against the cyclorama; none of them is
reachable in the priority-1 slice, but all of them are visible.

## References

1. The bridge pavilion in *Come Drink With Me* (1966): the fight space as a stage with four
   exits.
2. Shaw Brothers night exteriors: black sky, one blue-green wash, warm practicals, everything
   between lit by nothing.
3. A Suzhou 拙政園 covered bridge (小飛虹) for the silhouette only.

## Light

- Key: Sun, hard, `#2EBD2E` at 0.6 intensity, 35° elevation from the south-east. The one
  sharp shadow: the pavilion roof on the bridge deck.
- Wash: Area light on the cyclorama only, faint green, the moon as an emissive disc in the
  cyclorama texture.
- Practicals: six hanging lanterns on the posts (`#FFA500`), the four nearest the player
  realtime, the rest baked.
- Fog: floor fog at 0.4 m on the corridors and the water; the bridge deck stays clear so the
  hexagram table reads.

## Practicals and dressing

- Stone table with bronze hexagram inlay (the current hexagram of the room, set by the
  game; ships as six slot meshes, `HERO_table_line_1..6`, each with a solid and a broken
  variant).
- Stone stools ×4.
- 美人靠 bench around the inside of the balustrade.
- Lantern ×6.
- Lotus pad clusters on the water, upstream side only.
- A calligraphy board under the eave: 沁芳.
- Distant roofs: 怡紅院 (east), 瀟湘館 (south-west), 秋爽齋 (north-east), 凸碧堂 on its hill
  (north), as low-poly silhouettes with one lit window each.

## Assets

| From | Piece |
| --- | --- |
| `HERO` | `HERO_qinfang_bridge` (stone bridge deck, 14 m span, arch), `HERO_table_hexagram` |
| `KIT_pavilion` | Hexagonal roof, post ×6, bracket set ×6, 美人靠 |
| `KIT_corridor` | Bay ×16 (4 per direction), corner ×0, stair bay ×2 (bridge approaches) |
| `KIT_water` | Stream surface, stone embankment ×2, lotus cluster ×3 |
| `KIT_flora` | Willow ×2 at the embankments, bamboo clump ×3 along the south corridor |
| `KIT_props` | Hanging lantern ×6, stone stools ×4, calligraphy board |
| `KIT_stage` | Cyclorama (moon variant), fog plane ×6, studio wall ×4 (closing the corridor ends) |
| silhouettes | 4 roof masses, `MAT_backstage` with one emissive window quad each |

## Trigger empties

| Name | `room_id` | Position |
| --- | --- | --- |
| `TRG_qinfang_center` | `qinfang_ting` | Bridge deck centre. The room's `look`. |
| `TRG_qinfang_table` | `qinfang_ting` | At the table. Opens the live feed. |
| `TRG_qinfang_rail` | `qinfang_ting` | At the downstream balustrade. `look` at the water, the moon, the roofs. |
| `TRG_exit_east` | `yihong_yuan` | 4 bays down the east corridor. Blocked in priority 1 (studio wall). |
| `TRG_exit_north` | `daguan_lou` | 4 bays north. Blocked in priority 1. |
| `TRG_exit_west` | `ouxiang_xie` | 4 bays west. Blocked in priority 1. |
| `TRG_exit_south` | `rockery_gate` | Bridge foot, south. Returns to the tunnel. |

Other players are placed by the game on `TRG_qinfang_center`, the corridors, and the rail;
the site ships no figures.

## Cameras

- `CAM_shawscope`: on a rail around the pavilion at 6 m radius, 1.6 m height, always facing
  the table. Player movement along the corridors switches to a rail per corridor.
- `CAM_stage_wide`: from the south corridor mouth, pavilion centred, the moon top-left,
  凸碧堂's hill top-right. This is the marketing still and the look-test frame.


## Current implementation

The site is reachable in Godot, including the branches beyond the original priority-1 slice. The central pavilion now uses the reusable hexagonal roof, six posts and six bracket sets from `KIT_pavilion`. Two leaning benches sit inside the south bridge balustrades. Bridge deck, hexagram table, six lanterns and markers are retained. All sixteen straight approach bays now use the completed corridor kit and share the pavilion’s architectural atlas. The bridge balustrades remain in place. The southern route bends around the post rather than passing through it.

The portrait action list scrolls within 152 pixels so the pavilion remains visible above the controls. All commands remain available. Public topics are connected read-only; player presence and the full live divination feed are still unfinished.

This is a kit-integration pass, not final site acceptance. The pavilion kit now uses its shared 2048² PBR atlas. Atlases for the other site assets, painted signage, sourced reference images, final lighting/bakes, runtime LOD switching and target-phone acceptance remain open.

The entrance reveal now slides out through the south corridor’s open side and rises to the wide pavilion camera before the visitor continues. All sixteen corridor bays are retained. The command panel is hidden during the four-second shot so the bridge and water remain visible; normal controls return afterward.

The table now exports all six solid/broken pairs. Its Godot controller supports all 64 patterns, with lines ordered bottom to top (0 broken, 1 solid). “Examine the table” opens a close view; “Look” restores the pavilion view. Desktop and portrait views were inspected. This remains a local display until the live reading feed is connected.

The demo now supports a local three-coin cast at the bronze table. All 64 King Wen patterns use the sister app’s bottom-to-top mapping. The result card shows the Chinese name, English meaning, upper/lower trigram, moving lines and transformed hexagram when applicable; closing it leaves the cast pattern on the table. This is a local reading and has no generated interpretation, account history or live divination feed. Desktop and portrait card/table views were inspected.


## Flora placement — 2026-10-04

Three shared-kit bamboo clumps and two waterside willows now frame the south walk and embankment. The willow trunks have small separate colliders. A visible two-metre opening in the covered walk rail gives the bamboo route its crossing. All placed plants share one compressed runtime atlas and switch detail with distance. The assembly export and editable site libraries are synchronized. Further dressing, final lighting and sourced references remain open.


## Shared prop placement — 2026-10-04

The existing dressing now uses fitted prop-library meshes with a shared PBR atlas. Mount positions, seat/table heights, collision, lights and triggers are retained. The site’s props export as one material batch and stop drawing beyond 28 metres. Desktop and portrait views were reviewed; source-hash-checked bakes apply where this site belongs to the demo or priority-2 catalog. Further art, sourced references and final lighting remain open. Details: `../kits/props.md`.

## Painted title — 2026-10-04

The temporary Songti glyph geometry is replaced by original painted 沁芳 lettering on the wood board. The board now sits 0.50 m forward of its original mount on two short wood supports, clearing the front post that previously crossed the lettering. The texture preserves its generated alpha and image aspect ratio; Godot uses compressed mipmapped 512px imports. Cameras, lights, triggers and collision records remain unchanged. Original artwork and provenance: `../../textures/decals/garden-signs/README.md`. Final material/lighting acceptance and external visual references remain open.


## Owned backdrop wash — 2026-10-06

`LGT_qinfang_ting_backdrop_wash` is saved in authoring and `SITE_qinfang-ting.blend`: a 150 W, 15 × 10 m Area light, faint neutral green (linear RGB 0.68, 0.78, 0.73), aimed at the painted enclosure along `CAM_stage_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.

The owned-key pass below completes the missing-key inventory requirement. Final light and shadow quality remains under review.


## Owned key source — 2026-10-07

`LGT_qinfang-ting_key` is now saved in authoring and the directly openable site library: a Sun at energy 0.6, 35° elevation from the southeast and 0.5° source angle. Its muted green follows the user’s palette revision. Native checks require a single positive owned key, hard shadows and the intended direction/target; they failed before this pass and pass afterward. The shared light named `LGT_stage_green_key` now has neutral cool RGB (0.70, 0.74, 0.78), energy 1.4.

Geometry, materials, images, collision and camera data are unchanged in the new export; the three keys and shared-fill settings are the changes. All 124 ordinary maps were freshly rebaked at 128 samples because the Sun/shared fill affects the whole assembly. The native wash was also refreshed at 128 samples/512². Godot now uses the current source `d74e0ff858748d529029c80f0ea11969c121dd71f645effebf55180104099bde` and hash-matched maps. Imported-key, full-lighting, wash, material and demo-startup checks pass. Desktop and 390 × 844 portrait arrival views are refreshed. Final shadow dominance, palette, materials, filtering and moving-camera acceptance remain open.


## External reference collection — 2026-10-07

The Flying Rainbow Bridge architecture photo is collected, visually checked and attributed in `../reference/external/qinfang-ting/README.md`; its original bytes match the source file checksum. It is reference material only. The two specified film stills remain uncollected, so the three-reference requirement is not complete.


## Outward roof shell — 2026-10-08

All 25 upper-shell faces now point outward in saved authoring and the directly openable site library. Vertex positions, face/vertex primary UVs, material assignments, collision, cameras and transforms are preserved. The exported roof batch has reversed upper normals and newly packed UV2; it requires fresh lighting. The corrected canonical source is `90c4f70e…`. The complete 124-map ordinary refresh, direct backdrop wash and terminal spill are installed with source `90c4f70e…`. Current native images show tile detail on the outward shell. The verified PBR package includes this source; final whole-site art acceptance remains open. Evidence: `../../export/pavilion-roof-orientation-current.json`, `../../export/roof-cone-authoring-source.json` and `../../export/roof-cone-export-preservation.json`.


## Portrait pavilion composition — 2026-10-08

The portrait overview now views the pavilion from the south at `(6, 6.98, 20)` in engine coordinates, aimed at the table with a 50° vertical field of view. This keeps the complete physical moon above the pavilion and clear of the header and command panel; the preceding oblique view clipped half the moon at the right edge. The desktop pose and all other arrival cameras retain their existing projections. The portrait reveal ends at this same pose and interpolates its lens during the lift.

Resizing an overview updates its camera without replacing room text or actions. Table and cast views retain their preceding 55° horizontal portrait lens; resizing a detail view does not restore the overview. Source geometry, authored Blender cameras, moon material and matching bakes are unchanged. Further painted moon/backdrop composition and final site acceptance remain open. Native regression and captures are recorded in `../../export/pavilion-framing-runtime-checks.json`.


The shared physical moon now has original ivory/amber painting with gray-blue washes in the saved Blender source, replacing its constant green emission. Its 5.4 m geometry and all authored/runtime cameras are preserved. Packed base/emission factors and shared texture transfer are verified; complete fresh lighting is running before engine adoption. See `../moon-paint.md`. The playable demo still uses the preceding complete source. Backdrop-edge exposure and final site art remain open.

## Collected Shaw night-set reference — 2026-10-08

Slot 2 now has a directly reviewed frame from the published *The Magic Blade* trailer at 53.0 seconds. A low-key terrace exterior has a warm round lamp at the left, cool blue light at the right, near-black sky and roof/figure silhouettes, and a broad central area that remains unlit. This fills the specified Shaw night-exterior lighting reference: limited cool wash, localized warm practical and dark space between. Night appearance is visually inferred. It does not identify Qinfang or show the four-exit Come Drink With Me bridge pavilion, and it provides no measured colors, light-linking configuration or lamp energy. Use the contrast pattern while reducing the green contribution as the user requested.

Attribution, rights information, original stream hash and exact decoded-frame provenance: `../reference/external/qinfang-ting/README.md`. Remaining reference slots: 1. This does not establish final scene art, lighting, performance or service acceptance.

## Waterline and reed source checkpoint — 2026-10-09

The combined Blender source is now `0d3e84e3`; export and Godot use `1380ceca`. The complete fresh lighting set covers 124 ordinary receivers and 141 source PNGs, with matching wash/spill catalogs. Both native Mac tours visit all fourteen sites over twenty-six public-command legs and return to the cell, with no floor misses and at most four practical lights. All 42 camera, 400 collider and 71 marker contracts are preserved. This is an incremental working-source checkpoint; final site art, references, phone/sustained performance and authenticated services remain open. Evidence: `../reference/ziling-source-art/README.md`.

The shared stream surface is 0.7 m higher, covering more of the western island's dark sides. Its saved Blender color now matches the reduced-green slate-blue direction. Qinfang's geometry, cameras, table, walking surfaces and collision are preserved. Dedicated water modules and both bridge aliases now carry the same neutral water/architectural palette; their geometry, UVs, colliders and ports are preserved. Final table/support composition, bank edges and stage ground remain open.


## Stream bank and lotus checkpoint — 2026-10-09

The current complete source is `7a9fc523` with authoring `074ab201`. The shared stream has 54 bank modules and 54 added colliders; all 42 cameras,400 earlier colliders and 71 markers are preserved. Closed circular lotus pads sit above the water, with a muted shared leaf material and matching saved kit/generator. Fresh lighting covers 124 receivers and 141 source PNGs. Both native Mac tours pass 14 locations and 26 travel legs;15 installed checks pass. This is an incremental source checkpoint. Final site art, five remaining reference slots, current phone/sustained performance, release and authenticated services remain open. Evidence: `../reference/water-edge-source/README.md`.

Twenty-seven repeated embankment modules per side replace the two plain shared banks. Coping is visible along the water; their collision tops are at the surrounding ground level. The table, bridge and camera compositions remain fixed. Dark bank faces and the broad ground/set boundaries still need art work.


## Island exterior winding checkpoint — 2026-10-09

Current assembly `73267e2b` / authoring `2b07ce48` repairs the reed island’s exterior face winding. All other exported mesh attributes and fourteen other site GLBs are preserved; cameras, colliders, markers and runtime are unchanged. Complete matching lighting, twenty-five focused native checks and thirteen installed checks pass. This site is not declared final by the island repair. Five references, current phone/sustained budgets, release and authenticated services remain open. Evidence: [island source review](../reference/island-exterior-winding/README.md).


## Neutral stage-floor checkpoint — 2026-10-09

Current complete source is `c9d4fb30`; authoring is `43d7e33e`. The five broad canvas floor pieces use muted warm gray (.065,.060,.055 linear RGB). Other materials, geometry, cameras, collisions, markers and runtime are preserved. All 141 fresh lightmaps, six source phases, 38 positive native checks plus two intended rejection controls, both 14-room/26-leg tours and 15 installed checks pass. All 47 installed lit/Ziling/arrival originals reproduce the reviewed candidate exactly. References remain 37/42; this is palette repair acceptance, not final site or phone acceptance. Evidence: [neutral stage floor](../reference/stage-floor-palette/README.md).


## Paving-source checkpoint — 2026-10-10

Current assembly is `ba40866e` with authoring `7eba169a`. Duplicate visible paving tops are partitioned while retaining the complete floor footprint, all 454 colliders, 42 cameras, 71 markers, materials and runtime `7970380d`. Complete matching 141 PNG lighting, both actual Mac 14-room/26-leg tours and 22 installed checks pass; all 85 installed originals reproduce the reviewed files. All 28 current arrival originals were directly inspected. This is focused paving acceptance; this site's final art is still open. References remain 37/42; current phone/sustained/release and authenticated services remain required. Evidence: [paving repair](../reference/paving-surface-joins/README.md).
