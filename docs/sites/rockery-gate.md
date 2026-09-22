# Site sheet: rockery gate (曲徑通幽)

Slug `rockery-gate`. Priority 1. Function: transition from cell to garden (design doc
"garden transition"). Room id `rockery_gate`.

## Stage direction

In the novel the first thing inside the garden gate is a screen of rockery so that nothing
is seen at once. Here it is a plaster Taihu tunnel, 12 m long, bending twice, 2.2 m wide,
floor fog to the knee. The corridor from the cells ends at its mouth. The tunnel is dark
except for one amber lantern at each bend. At the far end it opens without warning onto the
沁芳 stream and the bridge pavilion, full width, fully lit. The reveal is the shot.

## References

1. The rockery tunnels in the Beijing 大觀園 park reconstruction (1980s), which are
   themselves a film set.
2. The cave corridors in Shaw Brothers *The Magic Blade* (1976): plaster rock, hard side
   light, dry ice.
3. A moon gate in fog, seen from the dark side.

## Light

- Key: none in the tunnel. At the exit, the 沁芳亭 site key (green) spills back 3 m.
- Wash: none.
- Practicals: two hanging lanterns (`#FFA500`), one at each bend, realtime, radius 0.1 m,
  range 4 m.
- Fog: floor fog plane at 0.6 m, density high, `#2EBD2E`. The engine height fog is at
  its maximum here and eases to normal at the tunnel mouth.

## Practicals and dressing

- Lantern ×2, hanging from iron hooks set in the plaster.
- Carved characters 曲徑通幽 above the entrance, in the plaster, catching the lantern.
- Water drip decal at the second bend.
- A single potted banana plant at the exit, silhouetted against the bright garden.

## Assets

| From | Piece |
| --- | --- |
| `KIT_rockery` | Tunnel segment ×4, arch ×2 (entrance and exit), cliff face ×2 (flanking the exit) |
| `KIT_props` | Hanging lantern ×2 |
| `KIT_flora` | Banana leaf clump ×1 |
| `KIT_stage` | Fog plane ×3, studio wall behind the rock |

No hero object. The 曲徑通幽 carving is a decal on the arch.

## Trigger empties

| Name | `room_id` | Position |
| --- | --- | --- |
| `TRG_gate_mouth` | `rockery_gate` | Tunnel entrance. Entering fires the tunnel text and drops the camera to `CAM_shawscope`. |
| `TRG_gate_bend_2` | `rockery_gate` | Second bend. Optional `look` beat: the drip, the carved characters. |
| `TRG_gate_exit` | `qinfang_ting` | Tunnel exit. Entering fires the reveal and hands over to 沁芳亭. |

## Cameras

- `CAM_shawscope` rail: enters low behind the player, tightens through the bends, and at the
  exit pulls back to the stage-wide frame of the pavilion. This is the one scripted move in
  the priority-1 slice.
- `CAM_stage_wide`: from inside the tunnel mouth looking out, the pavilion framed by rock.
