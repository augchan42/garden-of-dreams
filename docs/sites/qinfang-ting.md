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
