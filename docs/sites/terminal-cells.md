# Site sheet: terminal cells

Slug `terminal-cells`. Priority 1. Function: personal terminal room (design doc "Entry
Experience"). Room id `terminal_room`.

## Stage direction

A row of six identical black cells under the garden's outer wall, like dressing rooms behind
a stage. Each cell is 2.4 × 2.4 × 2.6 m: a desk, a chair, one green CRT, one barred window at
eye height. The CRT is the only light. Through the window, the rockery gate and a slice of
cyclorama with the moon. The door opposite the window is open onto a black corridor. There
is nothing in the cell to look at except the screen and the window, and that is the choice
the player makes.

## References

1. The cell in *The 36th Chamber of Shaolin* (1978): bare walls, one light source, a door
   to somewhere better lit.
2. A 1970s Hong Kong film-studio dressing room: plywood, one mirror bulb, a folding chair.
3. A green-phosphor VT100 in a dark room, screen glow on the desk only.

## Light

- Key: none. The CRT is the key (`MAT_crt_green`, emissive strength 4, realtime point light
  `#2EBD2E` at the screen, radius 0.05 m, range 3 m).
- Wash: a faint green spill from the window, baked, from the garden's cyclorama wash.
- Practicals: none.
- Fog: none inside. The corridor outside has the standard floor fog.

## Practicals and dressing

- CRT on desk, angled toward the chair.
- Chair, folding, wood.
- Window bars (`KIT_wall` leak window, pattern 1, no glass).
- Cell door frame, no door leaf.
- One calligraphy scroll on the wall behind the desk, unlit, illegible in the dark.

## Assets

| From | Piece |
| --- | --- |
| `KIT_tech` | CRT (green), terminal desk, cell door |
| `KIT_wall` | 3 m wall bay ×3, leak window ×1 |
| `KIT_props` | Folding chair, calligraphy scroll |
| `KIT_stage` | Floor boards, studio wall behind the cell row |

No hero object. Six cells are one cell instanced six times; only the one the player
occupies needs the CRT light on.

## Trigger empties

| Name | `room_id` | Position |
| --- | --- | --- |
| `TRG_cell_seat` | `terminal_room` | At the chair. Entering it focuses the CRT (the divination interface). |
| `TRG_cell_window` | `terminal_room` | 0.5 m in front of the window. `look` fires the garden glimpse text. |
| `TRG_cell_door` | `rockery_gate` | On the threshold. `exit` command target. |

## Cameras

- `CAM_shawscope` entry: from the door, looking in at the screen glow.
- `CAM_stage_wide`: down the corridor, six doorways, six green rectangles on the floor.


## Shared tech placement — 2026-10-04

Six green CRTs, timber desks, open steel frames and cable drops now use the shared tech library. Frames retain the existing 1.12 m clear width and 2.1 m clear height; rays confirm passage through all six openings and collision at their posts. Existing window/seat/door actions and lights remain in place. Desktop and portrait cell views were inspected. The folding wood chairs and dark unlit wall scrolls are now placed. Source-matched bakes and route checks pass. Details: `../kits/tech.md`.


## Folding chair library — 2026-10-04

The required folding wood chair is now available in `KIT_props` at two detail levels (968/356 triangles), with a 0.46 m seat anchor, crossed frame, brass pivots and matching seat/back collision. Export, UV and Godot collision checks pass. All six cells now use fitted chairs with matching seat anchors and two collision boxes each. Seat markers remain unchanged; the visitor standing point moves behind the back to avoid overlap. Capsule clearance, floor support, doorways and outward/return traversal pass. Desktop and portrait chair views were inspected. See `../kits/props.md`.


## Stage placement — 2026-10-04

Six timber floor panels fit the 2.4 m cells and retain walking height zero. Six unshaded black studio panels span the backstage corridor wall; two gel frames hang there as stored equipment. The corridor fog uses the shared neutral gray-blue stage material. Floor support, corridor clearance and outward/return traversal pass. Desktop and portrait floor/chair views and the backstage wall were inspected. The dark calligraphy scrolls are now fitted beside the barred windows. Details: `../kits/stage.md`.


## Terminal wall scrolls — 2026-10-04

All six cells now have one dark calligraphy scroll on the solid right-hand strip of the wall behind the desk. The 0.46 m overall width fits the 0.6 m strip; the barred opening remains clear. The scrolls reuse the prop atlas with a 0.025 base-color multiplier, no emissive pixels, and no added practical light or collision. The dark material exports as a standard glTF color factor and uses the same textures in Godot. Source/export comparisons preserve all 497 collision, light and trigger nodes exactly. The folding-chair batch and its seat/standing clearance remain intact.


## Window spill status — 2026-10-06

The site retains the specified CRT key and has no owned broad key or backdrop Area light. Twelve exterior washes now light the shared backdrop; their separate bake transfers direct light only to five backdrop receivers. The terminal’s indirect window spill from that new wash is not yet baked or verified. Current desktop/portrait views show the window backdrop and local CRT; this does not establish the required indirect illumination.


## Native window spill — 2026-10-07

The separate indirect Cycles pass now covers all seven terminal material batches using the twelve saved exterior washes. It excludes the world, other lights and emissive CRT/lantern geometry; no broad terminal key is added. At 2048 fixed samples and 512², all six cell-floor window-only controls receive light. Direct-wash, sealed-window/door and all-washes-off controls receive zero. The door and window blockers exist only in the temporary control scene; the production bake retains the actual open room geometry.

Adaptive sampling had stopped many rare window paths too early. Floor selection also needed normalized normals under the floor object's nonuniform scale. The current bake disables adaptive sampling and path guiding. PNGs are normalized with their physical maxima; Godot restores those scales without increasing energy. Native 16-bit readback verifies the decoded maxima. Source, terminal, stage and twelve exterior-library hashes, canonical UVs and all PNGs are validated before copying. Five stale/changed-source cases reject without modifying any installed files.

Normal exploration and the demo add the indirect term once to the ordinary bake and retain source materials, CRT emission and practical light masks. The earlier direct-backdrop isolation remains in place. Runtime checks pass in both modes, and a rendered negative/positive fixture checks the normalized transfer. Final shadow, color, filtering and moving-camera acceptance remains open. The three external references remain incomplete. See `../baked-lighting.md`.

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
