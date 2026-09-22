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
| `KIT_props` | Folding chair (add to kit), calligraphy scroll |
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
