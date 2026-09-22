# Wall material atlas

Original 2048 × 2048 base-color, tangent normal and packed ORM maps. The wall kit uses one material per module, with separate padded regions for whitewash plaster, wood and tile. Wood/tile pixels match the pavilion atlas. Limewash uses deterministic broad trowel marks and fine grain, preserving the garden's green palette. No baked lighting or external imagery is included.

Regenerate with `python3 scripts/generate_wall_atlas.py`; hashes and UV rectangles are in `atlas.json`. UV0 addresses the atlas; UV1 remains reserved for lightmaps. Godot import settings enable GPU compression and mipmaps at full resolution.

The files are embedded in each standalone GLB. The atlas is separate from the pavilion atlas because plaster needs its own region; garden placement should share one wall material and one set of maps. Final mobile memory acceptance remains outstanding.
