# Painted garden titles

These seven PNGs are original AI-generated production art made with Codex's built-in image-generation tool on 2026-10-04. They are game textures, not sourced historical references. The characters were visually inspected in the generated artwork.

| File prefix | Characters, left to right |
| --- | --- |
| qinfang-ting | 沁芳 |
| hengwu-yuan | 蘅蕪苑 |
| yihong-yuan | 怡紅院 |
| xiaoxiang-guan | 瀟湘館 |
| longcui-an | 櫳翠庵 |
| aojing-guan | 凹晶館 |
| daoxiang-cun | 稻香村 |

Each prompt requested only the exact characters in one horizontal row, bold hand-brushed regular script with accurate Traditional Chinese structure, varied brush pressure, restrained dry-brush edges, warm aged-gold strokes and transparent alpha. Boards, paper, borders, seals, signatures, Latin text, extra characters, perspective, shadows and lighting were excluded. The two-character title requested a 2:1 layout; three-character titles requested 3:1.

The original full-resolution PNGs retain their generated alpha. `scripts/finish_garden_signs.py` fits the lettering without stretching its image aspect ratio, moves four boards forward of their intersecting eaves and the pavilion board forward of its front post, with two wood supports each, and replaces the Songti geometry, embeds the images in the Blender sources and preserves all structural records. `scripts/configure_garden_sign_imports.py` uses compressed mipmapped 512px Godot imports. The lettering uses the same 0.55 emission-strength treatment as the previously completed signs, for legibility under the grade; it adds no practical lights.

Godot keeps the small painted lettering surfaces within a 28-metre visibility range. The wood boards remain in their site material batches. This keeps distant lettering from adding draw calls through the terminal window; arrival and detail captures check that each title still draws on its site approach.
