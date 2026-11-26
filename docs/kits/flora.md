# Flora kit

The shared kit now contains all eight variants in the scene spec: three bamboo sizes, plum, willow, banana, reed and a potted plant. This completes the reusable library pass. Twenty-three plants are now placed across five sites, with runtime distance switching. Further dressing and phone acceptance remain open.

Open `blender/kits/KIT_flora.blend` for the editable showroom and sixteen module scenes. Each module has a local ground origin, `PORT_ground`, `UVMap` and `LightmapUV`. Plum and willow have simplified trunk colliders; the potted plant has a planter collider. The other clumps are decorative and have no invisible collision volume.

| Variant | LOD0 triangles | LOD1 triangles | Ratio |
| --- | ---: | ---: | ---: |
| Bamboo small | 564 | 204 | 36% |
| Bamboo medium | 940 | 340 | 36% |
| Bamboo large | 1,316 | 476 | 36% |
| Plum | 576 | 244 | 42% |
| Willow | 1,198 | 464 | 39% |
| Banana | 252 | 98 | 39% |
| Reed | 364 | 168 | 46% |
| Potted | 320 | 110 | 34% |

LOD1 changes stem cross-sections and foliage card subdivisions while preserving every stem, leaf and blossom. Bamboo uses one closed culm per stalk with three aligned joint collars. Narrow leaf cards and measured clump heights of 2.51, 3.46 and 4.37 m replace the earlier disconnected internodes; both detail levels retain the same stalks. Its triangle counts are near the spec's 40% target; the ratios vary to preserve small plant shapes. Generic decimation damaged thin stems during review and is not used in the final library.

One original 2048 × 2048 RGBA atlas supplies sage and olive foliage, brown bark, terracotta and pale plum blossoms. The leaves use alpha clipping and render on both sides. Every Godot variant uses `materials/flora_atlas.tres` through `flora_kit_import.gd`, so all sixteen imported meshes share one texture resource. The authoring atlas stays 2048px; Godot imports a compressed, mipmapped 512px version to keep the first-reading demo below its 64 MiB texture target. The importer disables automatic extra LODs because the kit already provides explicit detail levels.

Exports are in `export/kits/flora`; Godot copies are in `godot/assets/kits/flora`. Legacy `KIT_flora.glb` and `KIT_flora_LOD1.glb` contain medium bamboo. The general packaging script preserves this completed library.

Regenerate with:

```sh
python3 scripts/make_flora_atlas.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python scripts/complete_flora_kit.py
python3 scripts/verify_flora_kit.py
```

Copy the exported GLBs and atlas to the Godot flora directory, then run Godot's editor import. The tracked `.import` settings select the shared material hook, mipmapped compressed texture and explicit LODs.

Validation covers sixteen exported models, two UV channels, ground anchors, matching collider transforms, triangle budgets, alpha masking and atlas dimensions. The Godot check covers material identity, transparency, UVs, 512px runtime texture size and six imported colliders. `tests/render_flora_kit.gd` generates the overview images for visual review.

![Full detail](../reference/flora-kit.png)

![Lower detail](../reference/flora-kit-lod1.png)

The placement pass replaces four bamboo clumps in Xiaoxiang, two banana plants in Yihong, two plum trees at Longcui, ten reed clumps on Ziling, and three bamboo clumps at Qinfang. Qinfang also gains two waterside willows. The 23 plants retain their existing bed and planter positions. A two-metre opening in the covered walk now gives the bamboo route a clear crossing; both its visible rail and collision are changed.

The assembly and five directly openable site libraries are updated. The 32 demo and 28 priority-2 lightmaps were refreshed from the final export. `runtime/flora_lod.gd` switches at 14 m with a 2 m buffer on either side, changes only the rendered mesh and preserves collision. The garden importer replaces both mesh surface materials and overrides with the shared atlas.

All four affected outward and return routes pass physics checks. Desktop and portrait views were reviewed. Final site lighting and art, additional dressing and phone GPU acceptance remain open.

## Saved bamboo source check — 2026-10-10

The saved kit, assembly, Xiaoxiang and Qinfang libraries, and linked master must contain matching bamboo. The read-only validator checks 27 meshes for continuous culms, joint collars, the 2.5–4.5 m height range, UVs, finite coordinates and LOD budgets. The previous saved source fails this check because its internodes are disconnected.

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python scripts/verify_saved_bamboo_sources.py -- --root "$PWD" --output /tmp/garden-bamboo-verification.json
```

Review evidence: [bamboo source repair](../reference/xiaoxiang-bamboo-source/README.md). Final dressing and phone acceptance remain open.
