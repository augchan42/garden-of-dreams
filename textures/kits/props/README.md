# Original prop atlas

`make_props_atlas.py` generates three aligned 2048 × 2048 RGB maps: base color, ORM and emission. The 4 × 4 cell layout supplies timber, gray stone, bronze, lantern paper, coals, linen, calligraphy paper, screen art, lacquer and ash. It uses deterministic grain and vector shapes; there are no photographs or downloaded textures.

The four-character scroll reads 清風明月. It uses the installed macOS Songti TC Bold face at index 2 of `Songti.ttc`. The generator verifies glyph coverage before drawing. The font file is not bundled; the textures contain rendered glyphs. This is original typeset production art, not a historical calligraphy reference. The bamboo screen pattern and small red seal mark are procedural drawings.

All three Blender maps are packed into the editable kit and embedded in each GLB. Godot shares one ORM material across variants and imports compressed mipmapped maps at 512px for base color and 256px for ORM/emission. Only paper and coals have nonblack emission. The kit contains no realtime light objects.

Regenerate with `python3 scripts/make_props_atlas.py` on macOS with Songti installed, then run the Blender kit builder. `atlas.json` records the cell names and inscription.
