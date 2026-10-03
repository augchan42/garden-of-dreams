# Flora kit

The shared kit now contains all eight variants in the scene spec: three bamboo sizes, plum, willow, banana, reed and a potted plant. This completes the reusable library pass. Placement in the garden and runtime distance switching remain open.

Open `blender/kits/KIT_flora.blend` for the editable showroom and sixteen module scenes. Each module has a local ground origin, `PORT_ground`, `UVMap` and `LightmapUV`. Plum and willow have simplified trunk colliders; the potted plant has a planter collider. The other clumps are decorative and have no invisible collision volume.

| Variant | LOD0 triangles | LOD1 triangles | Ratio |
| --- | ---: | ---: | ---: |
| Bamboo small | 684 | 252 | 37% |
| Bamboo medium | 1,140 | 420 | 37% |
| Bamboo large | 1,596 | 588 | 37% |
| Plum | 576 | 244 | 42% |
| Willow | 1,198 | 464 | 39% |
| Banana | 252 | 98 | 39% |
| Reed | 364 | 168 | 46% |
| Potted | 320 | 110 | 34% |

LOD1 changes stem cross-sections and foliage card subdivisions while preserving every stem, leaf and blossom. Its triangle counts are near the spec's 40% target; the ratios vary to preserve small plant shapes. Generic decimation damaged thin stems during review and is not used in the final library.

One original 2048 × 2048 RGBA atlas supplies sage and olive foliage, brown bark, terracotta and pale plum blossoms. The leaves use alpha clipping and render on both sides. Every Godot variant uses `materials/flora_atlas.tres` through `flora_kit_import.gd`, so all sixteen imported meshes share one texture resource. The importer disables automatic extra LODs because the kit already provides explicit detail levels.

Exports are in `export/kits/flora`; Godot copies are in `godot/assets/kits/flora`. Legacy `KIT_flora.glb` and `KIT_flora_LOD1.glb` contain medium bamboo. The general packaging script preserves this completed library.

Regenerate with:

```sh
python3 scripts/make_flora_atlas.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python scripts/complete_flora_kit.py
python3 scripts/verify_flora_kit.py
```

Copy the exported GLBs and atlas to the Godot flora directory, then run Godot's editor import. The tracked `.import` settings select the shared material hook, mipmapped compressed texture and explicit LODs.

Validation covers sixteen exported models, two UV channels, ground anchors, matching collider transforms, triangle budgets, alpha masking and atlas dimensions. The Godot check covers material identity, transparency, UVs, texture size and six imported colliders. `tests/render_flora_kit.gd` generates the overview images for visual review.

![Full detail](../reference/flora-kit.png)

![Lower detail](../reference/flora-kit-lod1.png)

The master garden geometry, site lighting and packaged demo were not rebuilt in this library pass. Next, place the new plants in site libraries, update the assembly and inspect their appearance and collision along the route. Final plant density, phone performance and LOD switching require that placement pass.
