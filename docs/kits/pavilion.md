# Pavilion kit

`blender/kits/KIT_pavilion.blend` contains six independently editable modules and their 40% LOD companions. The showroom contains twelve collection instances. Exports are under `export/kits/pavilion/`, with matching Godot assets under `godot/assets/kits/pavilion/`.

| Part | LOD0 triangles | LOD1 triangles |
| --- | ---: | ---: |
| Hexagonal roof | 1,672 | 668 |
| Square roof | 1,128 | 450 |
| Post | 252 | 100 |
| Bracket set | 216 | 86 |
| Eave tile strip | 520 | 208 |
| Leaning bench | 540 | 216 |

Roofs have curved profiles, timber undersides, fascia, radial rafters, raised tile strips and bronze finials. Weighted simplification gives priority to the main surfaces over decorative strips. The bench is 2.4 m wide with a 0.48 m seat and an outward-curving back. The eave strip is 1.2 m long with ten hollow half-round tiles. Brackets have three stacked levels of alternating arms and bearing blocks.

All modules use metre units, two UV channels and one separate simplified static collision mesh. Roofs have four/six post mounting markers at radius 2.7 m. For a freestanding assembly, place posts at those horizontal coordinates, bracket bases at 3.1 m and the roof origin at 3.58 m. Roof collision is a simplified closed volume above the eave, leaving the walking space clear.

Rebuild using Blender on `blender/authoring.blend` with `--python-exit-code 1 --python scripts/complete_pavilion_kit.py`. The general packaging script preserves the completed library. Legacy `KIT_pavilion.glb`/`_LOD1` exports now contain the hexagonal roof; use named part exports for new assemblies.

Verification: `scripts/verify_pavilion_kit.py` checks actual triangle counts, LOD ratios, UV channels, mounting coordinates and collision transforms. `godot/tests/test_pavilion_kit.gd` checks imported collision for all six parts, then assembles both roof types at both LODs and moves a capsule through their interiors. The showroom render is `docs/reference/pavilion-kit-0001.png`.

The shared 2048² PBR atlas is implemented for all twelve exports and the placed Qinfang parts. It contains original wood grain, tile/stone mottling and bronze variation, plus roughness/metallic and normal maps. UV0 maps into padded material regions; UV1 remains reserved for lightmaps. Every standalone part has one render surface, and the placed Qinfang parts batch into one atlas mesh.

On the M2 Max, GPU compression reduces the three atlas textures from about 48 MiB to 8 MiB including mipmaps, retaining 2048 resolution. Whole-scene texture memory in the stationary pavilion view drops from 80.16 MiB to 40.16 MiB. These are desktop measurements, not target-phone acceptance. `scripts/verify_pavilion_atlas.py` verifies embedded pixels, all triangle UV regions and PBR bindings; `godot/tests/test_pavilion_atlas.gd` verifies the imported textures.

Remaining: runtime LOD switching, other site integration and final lighting/performance acceptance. Decorative tile geometry is substantially reduced at LOD1; further authored tile texture detail can improve its appearance at a distance. Qinfang now uses the hexagonal roof, six posts, six brackets and two benches. Other sites still use their existing authored pavilion geometry. The runtime currently uses LOD0 for these placed parts.
