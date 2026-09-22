# Water kit

`blender/kits/KIT_water.blend` contains six editable modules with independent LOD companions and a twelve-instance showroom. Exports are in `export/kits/water/`; Godot copies are in `godot/assets/kits/water/`.

| Module | LOD0 triangles | LOD1 triangles | Collision shapes |
| --- | ---: | ---: | ---: |
| Stream, 3 × 6 m | 256 | 102 | 0 |
| Pond, 6 × 6 m | 512 | 203 | 0 |
| Embankment, 3 m | 288 | 116 | 1 |
| Six lotus leaves | 792 | 316 | 0 |
| Wooden bridge, 6 m | 704 | 276 | 3 |
| Stone bridge, 6 m | 700 | 276 | 3 |

Bridges have a 1.8 m deck, two end markers and separate deck/side collisions. The stone bridge rises 0.5 m at its center; its walking collision follows the arch. Water and leaves intentionally have no walking collision. Leaves have radial veins and a cutout slit.

Wood and masonry use the shared architectural atlas. Stream/pond GLBs use the existing animated water shader through `garden_import.gd`; run `scripts/configure_water_imports.py` after the first Godot import, then import again. The same script enables GPU compression for the structural atlas textures. Lotus material/art refinement and the kit's full final material treatment remain open.

LOD1 bridges and embankment use separately built continuous surfaces. Automatic decimation initially damaged disconnected masonry blocks; the explicit models retain deck, rail and wall silhouettes. LOD ratios are 39.20–40.28%. Both UV channels are exported; no collision geometry is decimated.

Rebuild using Blender on `blender/authoring.blend` with `--python-exit-code 1 --python scripts/complete_water_kit.py`. The general packager preserves this library. Legacy `KIT_water.glb` exports point to the wooden bridge; new consumers should use the named parts.

Verification: `scripts/verify_water_kit.py` checks actual exported geometry, connectors, UVs, LOD ratios and collision counts. `godot/tests/test_water_kit.gd` checks shader assignment, collision counts, movement from separate approach platforms across both bridges and back, the stone arch's elevation and side-rail blocking at both LODs. `docs/reference/water-kit-0001.png` shows full detail in front and simplified versions behind.

The wooden bridge now replaces the approach to Ziling reed island, and six lotus clusters are placed beside Ouxiang/Ziling. Other water surfaces, the stone bridge and embankment remain standalone parts awaiting placement. Automatic LOD switching, final art, lightmaps and target-phone acceptance remain unfinished.
