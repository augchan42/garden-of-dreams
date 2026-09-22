# Garden of Dreams — Blender scene spec

Status: draft, 2026-09-23. Source design: `8bitoracle-next/docs/ideas/garden-of-dreams.md`
(the text-adventure design this scene gives a body to).

## 1. What this is

A game-engine asset set for the Garden of Dreams (大觀園), built in Blender and exported as
glTF 2.0. It is a walkable classical Chinese garden shot like a 1970s Shaw Brothers kung fu
film and graded into the 8-Bit Oracle tech-noir palette: phosphor green, amber, black.

The garden is a soundstage, not a landscape. Everything the player sees was built on a
backlot: painted sky cycloramas, plaster rockery, a pond that ends at a studio wall. That
is the look, and it is also what makes the asset cheap to build and run.

## 2. Non-goals

- No character rigs. Player and NPC representation belongs to the game project.
- No gameplay logic, triggers or UI. The scene ships trigger volumes as named empties only.
- No photoreal materials. Nothing in the scene should read as a Suzhou garden survey.
- No terrain system. The ground is a modelled stage floor.

## 3. Target and pipeline

| Item | Decision |
| --- | --- |
| Engine | glTF 2.0 (`.glb`) is the canonical export. Unity is the assumed first consumer; Godot and Unreal import the same file. Confirm before the first export. |
| Blender | 4.2 LTS or later. One `.blend` per site plus a master assembly file. |
| Units | Metric, 1 BU = 1 m. Z up in Blender; the exporter converts to Y up. |
| Scale | Human 1.75 m. Door heads 2.1 m. Pavilion eaves 3.0 to 3.4 m. Corridor width 1.8 m. |
| Origin | Master scene origin at the centre of the 沁芳亭 bridge deck, ground level. |
| Export | `File > Export > glTF 2.0`, format `.glb`, `+Y up`, apply modifiers, include custom properties, Draco off (engine importers handle it inconsistently). |
| Textures | PNG for masks and normals, JPEG (quality 90) for albedo. Power-of-two sizes. |
| Lightmaps | Baked in Blender (Cycles) to a second UV channel, exported as separate PNGs. Engines re-bake if they prefer; the Blender bake is the reference look. |

## 4. Art direction

### 4.1 The three layers

1. **Set.** A classical garden as a Shaw Brothers art department would build it in 1974: flat
   fronts, stock lattice panels, everything sized to the camera, backs unfinished.
2. **Camera.** Shawscope framing (2.35:1), hard key lights, coloured gels, fog machines, zoom
   lens flatness. Day-for-night through the whole garden: it is always dusk on the stage.
3. **Grade.** The tech-noir LUT. Shadows go to black, midtones green, warm sources amber.
   Nothing else survives the grade.

Every asset decision should trace back to one of these layers.

### 4.2 Palette

Taken from `8bitoracle-next/src/constants/imageStyles/index.ts` (`colorPalettes['tech-noir']`).

| Role | Hex | Use |
| --- | --- | --- |
| Phosphor green | `#2EBD2E` | Fill light, foliage, water, painted sky, CRT glow |
| Amber | `#FFA500` | Lanterns, interior practicals, brazier coals, the terminal cursor |
| Black | `#000000` | Shadows, backstage, the studio wall behind the cyclorama |

Materials may use any hue in the albedo. The grade pulls them into this range. The
constraint is on the post-process and the lighting rig, not on the texture painter. Test
every material under the grade before calling it done: a material that looks right ungraded
is wrong.

### 4.3 Shaw Brothers cues, in order of importance

1. **Painted cyclorama sky.** A curved backdrop with brushwork mountains and a moon, visibly
   a painting, lit separately from the set. Seams allowed.
2. **Hard light with coloured gels.** One key per site, amber or green, with a sharp shadow
   edge. No soft area lights except the cyclorama wash.
3. **Fog on the floor.** Low volumetric fog at 0.3 to 0.8 m in every exterior. Green-tinted.
4. **Flat fronts.** Buildings are façades with a 1 to 3 m interior. Backs are untextured
   `MAT_backstage` (flat black). The player never sees them; the engine culls them.
5. **Stock parts.** One lattice panel, one baluster, one lantern, one roof tile strip. Reuse
   everywhere. Repetition is period-correct.
6. **Plaster rockery.** Taihu stones as chunky, obviously moulded forms with a wet-paint
   sheen, not scanned limestone.
7. **Studio floor.** The ground plane is boards and painted canvas. Where the pond meets the
   stage edge, it stops at a black wall.

### 4.4 Tech-noir cues

- CRT terminals recessed into garden furniture: the bulletin board in 秋爽齋 is a bank of
  amber monitors behind a lattice; the personal terminal room is a phosphor-green screen in
  a black cell.
- Scanline decal material (`MAT_scanline`) available for any emissive surface.
- Signage in the garden uses hand-painted calligraphy on wood, never printed type. Chinese
  names first, English never on the set.

## 5. Site map

The doc's four functional spaces are placed on named 大觀園 sites. The remaining named sites
exist as dressing and future rooms.

```
                       凸碧堂 (hill, Current Events Pavilion)
                            |
     稻香村 ----- 蘅蕪苑 --- 大觀樓 / 省親別墅 --- 秋爽齋 (Bulletin Board)
        |           |            |                  |
     紫菱洲 ---- 藕香榭 ==== 沁芳亭 (Central Gathering) ==== 怡紅院
                   |     (bridge over the 沁芳 stream)     |
                櫳翠庵 ------------ 瀟湘館 ---------- 凹晶館 (water)
                                     |
                              曲徑通幽 rockery gate
                                     |
                           terminal cells (entry)
```

`====` is the stream. Every path is a covered corridor (遊廊) or a stone walk; the corridors
are the load-bearing navigation and the fog-hiding device.

### 5.1 Sites and their jobs

| Site | Novel association | Function from the design doc | Build priority |
| --- | --- | --- | --- |
| Terminal cells | none (pre-garden) | Personal terminal room. A row of black cells, each with one green CRT and a window onto the garden. | 1 |
| 曲徑通幽 rockery gate | the garden's entrance screen | Transition from cell to garden. A rockery tunnel, fog-filled, opens onto the stream. | 1 |
| 沁芳亭 | bridge pavilion over the stream | Central Gathering Space. Live feed of divinations, players visible walking. Scene origin. | 1 |
| 秋爽齋 | 探春's study, birthplace of the 海棠 poetry club | Divination Bulletin Board. Long study hall, CRT bank behind lattice, calligraphy on the walls. | 2 |
| 凸碧堂 | hilltop hall, moon-viewing | Current Events Pavilion. Highest point, overlooks the whole set and the cyclorama. | 2 |
| 藕香榭 | water pavilion, crab feast, tea | Group readings and private garden spaces. Reached only by the bridge walk. | 3 |
| 蘅蕪苑 | 寶釵's courtyard, herbs, bare stone | Study circles. Rockery courtyard with no trees. | 3 |
| 怡紅院 | 寶玉's court | Dressing. Red lacquer, closed doors. Future room. | 4 |
| 瀟湘館 | 黛玉's bamboo court | Dressing. Bamboo grove, one lit window. Future room. | 4 |
| 櫳翠庵 | 妙玉's nunnery | Dressing. Plum trees, closed gate, one lantern. | 4 |
| 凹晶館 | water-level hall, moon poetry | Dressing. Reflection shot location. | 4 |
| 稻香村 | 李紈's farmhouse | Dressing. Thatch, fence, paddy painted on the cyclorama. | 4 |
| 紫菱洲 | 迎春's islet | Dressing. Reed island, footbridge. | 4 |
| 大觀樓 / 省親別墅 | main hall for the imperial visit | Backdrop. A large façade at the north edge; interior not built. | 2 (façade only) |

Priority 1 is the vertical slice: cell, tunnel, bridge pavilion, plus enough corridor and
cyclorama to stand in the pavilion and turn 360°.

### 5.2 Site sheet

Each site gets one sheet at `docs/sites/<slug>.md` before modelling starts, with: one
paragraph of stage direction, three reference stills, the key light colour, the practicals
list, the asset list, and the trigger empties it must contain. The sheet is the contract
between whoever writes the game's rooms and whoever builds the set.

## 6. Asset inventory

### 6.1 Kits (stock parts, built once)

| Kit | Contents |
| --- | --- |
| `KIT_corridor` | 3 m corridor bay (roof, two posts, balustrade, lattice back), 90° corner, T-junction, stair bay |
| `KIT_pavilion` | Hexagonal and square pavilion roofs, post, bracket set, eave tile strip, 美人靠 bench |
| `KIT_wall` | 3 m whitewashed wall bay, moon gate, vase gate, leak window (4 lattice patterns), roof cap |
| `KIT_rockery` | 6 plaster Taihu stones (S, M, L, arch, tunnel segment, cliff face) |
| `KIT_water` | Stream surface, pond surface, stone embankment, lotus pad clusters, wooden footbridge, stone bridge |
| `KIT_flora` | Bamboo clump (3 sizes), plum tree, willow, banana leaf clump, reed clump, potted plant. Card-based foliage. |
| `KIT_props` | Lantern (hanging, standing), brazier, stone table and stools, incense burner, calligraphy scroll, screen |
| `KIT_tech` | CRT monitor (amber, green), monitor bank, cable run, cell door, terminal desk |
| `KIT_stage` | Cyclorama (curved, 3 painted variants), studio wall, floor boards, fog plane, gel frame |

### 6.2 Per-site unique assets

Kept to a minimum. Each priority-1 and -2 site gets one hero object that cannot come from a
kit: the 沁芳亭 bridge deck, the 秋爽齋 CRT bank, the 凸碧堂 hill and terrace.

## 7. Technical budgets

These are targets, not limits. They come from the aim of running the priority-1 slice at
60 fps on a 2020 mid-range phone GPU (Adreno 6xx class) or any desktop, with the fog and
grade as full-screen passes. Confirm or replace them once the engine is fixed and the first
slice is profiled.

| Item | Target |
| --- | --- |
| Visible triangles per frame | 300k |
| Kit piece | 200 to 2,000 tris; a hero object up to 15,000 |
| Draw calls per frame | 150, by sharing kit materials |
| Materials | One atlas per kit (2048²); hero objects get their own 2048² |
| Texture memory (priority 1) | 64 MB |
| Lights | 1 baked key + 1 baked cyclorama wash per site; realtime lights only for the amber practicals near the player (4 at once) |
| LODs | Two per kit piece (100 % / 40 %). Flora: cards at LOD1. |
| Collision | Separate simplified meshes, `COL_` prefix, never the render mesh |

## 8. Materials

All materials are Principled BSDF, glTF-compatible (base colour, metallic, roughness, normal,
emissive, occlusion). No procedural node trees survive export; bake them.

| Material | Notes |
| --- | --- |
| `MAT_lattice_wood` | Dark lacquer, high roughness, tileable |
| `MAT_whitewash` | Plaster, slight grime gradient at the base |
| `MAT_rooftile` | Grey tile strip, tileable along one axis |
| `MAT_plaster_rock` | Wet-paint sheen: roughness 0.35, faint green tint in the albedo |
| `MAT_water` | Flat plane, animated normal map, green-tinted reflection. Engine replaces with its own water if it has one |
| `MAT_cyclorama` | Unlit emissive at 0.6, painted texture, 4096² |
| `MAT_backstage` | Flat black, unlit, no textures |
| `MAT_crt_amber` / `MAT_crt_green` | Emissive, scanline mask in alpha, bloom-targeted |
| `MAT_foliage_card` | Alpha-clipped, two-sided, green tint baked in |
| `MAT_lantern` | Emissive amber paper, translucent look faked with a gradient |

## 9. Lighting rig

Per site, in Blender, for the bake:

1. **Key.** One Sun or Spot, hard (angle 0.5°), gel colour amber or green per the site
   sheet. Casts the site's one sharp shadow.
2. **Cyclorama wash.** One large Area light aimed at the backdrop only (light linking).
3. **Practicals.** Amber point lights at each lantern and brazier, radius 0.1 m, no shadows.
4. **Fog.** A world volume is not used (does not export). Fog is a `KIT_stage` fog plane
   with a scrolling alpha, plus the engine's own height fog set to `#2EBD2E` at low density.
5. **Grade.** A `.cube` LUT lives at `grade/tech-noir.cube`, built in Blender's compositor:
   lift shadows to black, gamma to green, gain to amber. Applied in the engine as a
   colour-grading LUT. The same LUT is applied to every reference render in this repo.

## 10. Cameras

Two camera presets shipped as Blender cameras and documented for the engine:

- `CAM_shawscope`: 2.35:1, 40 mm equivalent, slight zoom-in on entry to a site. This is the
  default player camera.
- `CAM_stage_wide`: 2.35:1, 24 mm, fixed per site, for establishing shots and marketing
  stills. One per site, position saved in the site sheet.

Camera moves are fixed rails, not free look. Free look breaks the façade trick.

## 11. Naming and file layout

```
garden-of-dreams/
  docs/
    garden-scene-spec.md        this file
    sites/<slug>.md             one sheet per site
    reference/                  stills, palette swatches, LUT test renders
  blender/
    master.blend                assembly, links every site
    kits/KIT_<name>.blend
    sites/SITE_<slug>.blend
  export/
    kits/KIT_<name>.glb
    sites/SITE_<slug>.glb
    textures/
    lightmaps/
  grade/
    tech-noir.cube
```

Object naming: `<TYPE>_<name>_<variant>` with `TYPE` in `KIT`, `SITE`, `HERO`, `COL`, `TRG`
(trigger empty), `CAM`, `LGT`. Trigger empties carry a custom property `room_id` matching the
room id the game's content database uses. Slugs are pinyin without tones:
`qinfang-ting`, `qiushuang-zhai`, `tubi-tang`, `ouxiang-xie`, `hengwu-yuan`, `yihong-yuan`,
`xiaoxiang-guan`, `longcui-an`, `aojing-guan`, `daoxiang-cun`, `ziling-zhou`, `daguan-lou`,
`terminal-cells`, `rockery-gate`.

## 12. Milestones

1. **Look test.** One corridor bay, one lantern, one rockery stone, the cyclorama, the LUT.
   Rendered still under the grade. Decides the palette and material approach before
   anything else is built. Deliverable: `docs/reference/look-test-01.png`.
2. **Vertical slice.** Priority-1 sites exported and loaded in the engine, walkable, fogged
   and graded. Profiled against section 7.
3. **Priority 2.** 秋爽齋, 凸碧堂, 大觀樓 façade.
4. **Priority 3 and 4.** Remaining sites as dressing, then promoted to rooms as the game
   needs them.

## 13. Open questions

- Which engine. The spec assumes Unity; the export is engine-neutral, but the fog, LUT and
  water passes are set up once and differ by engine.
- Whether the garden is a single loaded scene or streamed per site. At the section 7
  budgets a single scene fits; streaming becomes necessary only if priority 3 and 4 sites
  get interiors.
- Player representation. The design doc wants "minimalist representation of users". A
  card-based figure in the poster style would match the set; a rigged character would not.
