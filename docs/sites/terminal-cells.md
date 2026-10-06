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
