# Prop kit

The reusable library contains all eight specified prop variants, each with an independent lower-detail mesh. The garden placement pass remains open.

| Variant | LOD0 triangles | LOD1 triangles | Ratio | Colliders |
| --- | ---: | ---: | ---: | ---: |
| Hanging lantern | 1,140 | 452 | 40% | 0 |
| Standing lantern | 1,420 | 588 | 41% | 2 |
| Brazier | 736 | 278 | 38% | 1 |
| Stone table | 628 | 252 | 40% | 1 |
| Stone stool | 428 | 164 | 38% | 1 |
| Incense burner | 712 | 280 | 39% | 1 |
| Scroll | 524 | 204 | 39% | 0 |
| Folding screen | 576 | 252 | 44% | 3 |

Open `blender/kits/KIT_props.blend` for the editable showroom and sixteen module scenes. Modules use metres and local ground origins. `PORT_` anchors provide lantern hang/light positions, the table top, stool seat, scroll wall/hang positions and screen hinge. The hanging lantern and wall scroll have no walking collision. Other props use separate boxes for the base, body or screen panels; those transforms match across detail levels.

LOD1 reduces cylinder and bowl subdivisions and removes secondary ornament. It retains lantern tassels, the table top, stool seat, burner bowl and sticks, scroll rollers and all screen panels. No generic decimator is used. Both general packaging and fallback LOD generation preserve completed kit manifests.

One original 2048px atlas layout supplies base color, packed occlusion/roughness/metallic and emission maps. Its colors are cream paper, gray stone, red-brown wood and bronze. Only lantern paper and coals emit light. The scroll reads 清風明月, rendered with Songti TC Bold on procedural paper; it is typeset art, not a sourced historical calligraphy image. The screen's bamboo ink pattern is original procedural drawing. Provenance and regeneration details are in `textures/kits/props/README.md`.

Godot's sixteen models share `materials/props_atlas.tres`. The import hook replaces both mesh surface materials and overrides, discards redundant embedded texture extraction, and disables additional automatic LODs. Compressed mipmapped runtime maps use 1024px for base color and 256px for ORM and emission. The lanterns export light markers and emissive paper, with no point lights; placement must use the existing four-practical light pool.

Exports are in `export/kits/props`; Godot copies are in `godot/assets/kits/props`. Legacy `KIT_props.glb` and `_LOD1` now contain the hanging lantern.

```sh
python3 scripts/make_props_atlas.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python scripts/complete_props_kit.py
python3 scripts/verify_props_kit.py
```

Copy exports and atlas maps to the Godot prop directory, then import the project. The tracked `.import` settings apply the shared material and runtime sizes. `tests/test_props_kit.gd` checks sixteen models, two UV channels, shared texture/material identity, eighteen colliders and the absence of embedded lights. The export verifier checks actual triangle counts, PBR maps, anchor positions and collision parity. Blender MCP also read the saved library catalog and confirmed sixteen module collections plus the showroom without changing the user's open scene.

![Full detail](../reference/props-kit.png)

![Lower detail](../reference/props-kit-lod1.png)

The master garden, current bakes and playable pack are unchanged in this library pass. Placement must preserve trigger/table behavior, route clearance, practical-light limits and the demo draw/texture budgets. The baked-material adapter currently expects StandardMaterial3D; integration must support the shared ORM material and preserve its packed roughness/metallic values. Final scene lighting, additional dressing and phone acceptance remain open.
