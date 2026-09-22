# Wall kit

Editable library: `blender/kits/KIT_wall.blend`. Exports: `export/kits/wall/`; Godot copies: `godot/assets/kits/wall/`.

Eight modules: 3 m whitewash bay, moon gate, vase gate, square/diamond/ice-crack/hexagonal lattice windows, and a separate coping cap. Each has an independent 40% LOD, UV0/UV1, and separate collision meshes. Gates have front/back connector markers and real through-openings. Window lattices have no opaque backing; collision blocks walking through them.

LOD0 is 316–1,584 triangles; LOD1 is 39.73–40.00%. The showroom places original modules in the two front rows and their simplified versions behind them. `scripts/complete_wall_kit.py` reproduces the library; the general packaging script preserves it.

Verification: `scripts/verify_wall_kit.py` checks actual exported triangles, UV channels, connector coordinates and matching collision transforms. `godot/tests/test_wall_kit.gd` tests capsule movement in both directions through the gates and blocking at the solid wall/four windows at both LODs. The showroom render is `docs/reference/wall-kit-0001.png`.

The first decimation pass exposed interior segment faces. Removing paired internal faces, welding vertices and recalculating normals before simplification fixes the visible strips and holes. The corrected render retains wall and opening silhouettes at both LODs.

All sixteen exports now use one shared wall PBR atlas with original limewash plaster and wood/tile swatches matching the pavilion. Each module exports one render primitive, three embedded 2048² maps and preserved lightmap UVs. Godot uses compressed textures with mipmaps. `verify_pavilion_atlas.py --kit wall` validates pixels, padded UV regions and material bindings; `test_pavilion_atlas.gd -- --wall` validates Godot texture bindings. The textured showroom render is `docs/reference/wall-kit-atlas-0001.png`.

Hengwu now uses nine modules: six bays, the moon gate, diamond window and ice-crack window. Site batching exposed coplanar overlaps at window-frame corners; horizontal rails now meet the jambs with butt joints. This resolves the sampled lightmap-UV overlap without changing triangle budgets.

Remaining: other site integration, runtime LOD switching, detailed coping refinement and mobile collision-cost profiling. Each module now imports as one static collision shape. Gate meshes preserve concave openings: moon gate 380 collision triangles, vase gate 84. Bay, window and cap collision each use 12 triangles. Tests also verify that the gate side piers block movement. The Hengwu integration is recorded in its site page.
