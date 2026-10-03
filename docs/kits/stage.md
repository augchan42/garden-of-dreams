# Stage kit

The library contains all seven stage inventory variants and independent lower-detail companions: three curved painted cycloramas, a black studio wall, floor boards, a fog plane and a lighting gel frame. Open `blender/kits/KIT_stage.blend` for the showroom and fourteen module scenes. The wall, floor, fog and gel modules are placed in the main garden; the painted cyclorama enclosure fit remains open.

| Variant | LOD0 triangles | LOD1 triangles | Ratio | Colliders per level | Material surfaces |
|---|---:|---:|---:|---:|---:|
| Moonlit cyclorama | 564 | 228 | 40% | 8 | 2 |
| Dusk cyclorama | 564 | 228 | 40% | 8 | 2 |
| Mist cyclorama | 564 | 228 | 40% | 8 | 2 |
| Studio wall | 384 | 156 | 41% | 1 | 1 |
| Floor boards | 1,140 | 504 | 44% | 1 | 1 |
| Fog plane | 200 | 72 | 36% | 0 | 1 |
| Gel frame | 680 | 288 | 42% | 1 | 2 |

The cyclorama is a sealed curved canvas shell, 7.5 m high and 18.46 m wide between its end anchors, with a 14 m radius. The front has the painted sky; the back and sealed edges use the black atlas cell. Its eight separate wall proxies retain the same transforms at both detail levels. LOD1 reduces arc segments from forty to sixteen. Four vertical rows remain, and the moon artwork is proportioned for the physical canvas rather than a square image.

The studio wall is a 3 m black panel with rear studs, cross braces and bolts. The floor is a 3 × 3 m board module whose walking top is at z=0 in Blender; its separate slab collider ends at the same height. LOD1 reduces board divisions and nail-head segments. The 3 m fog card sits 0.3 m above its ground anchor and has no collision. The gel frame has a rounded steel rim, brass hanging pins and a translucent amber sheet; the lower-detail frame retains its outline and mount positions.

## Materials and original art

A shared original 2048px atlas supplies timber, steel, black and brass color/ORM maps. The three original 4096px painted skies use layered brushwork mountains and a pale moon: slate blue for moonlit, plum/amber for dusk, and warm gray/slate for mist. Art regeneration and provenance are in `textures/kits/stage/README.md`.

Blender sources use glTF-compatible Principled materials. Painted fronts have emission strength 0.6. Godot replaces them with shared unshaded materials at a 0.6 color multiplier; the studio wall is unshaded black. Runtime compression and mipmaps use 1024px skies, 512px atlas color and 256px ORM. Those import sizes retain the higher-resolution source art. The gel is alpha blended and two-sided. The fog reuses the existing scrolling-alpha shader and mask with a neutral gray-blue color; its low opacity is intentional. It does not add a world volume.

The import hook replaces both mesh surface materials and active overrides. Fourteen modules share seven resources: three sky materials, one timber/metal atlas, black, fog and gel. Atlas rear surfaces on the cycloramas and gel rims share the same resource as the floor boards. Embedded-image extraction and additional automatic LOD generation are disabled. No module contains a light; `PORT_wash` and `PORT_light` are placement anchors for the existing rig. A preview Sun exists only in the Blender showroom.

## Connectors and verification

Each piece has `PORT_ground`. Cycloramas add left/right/wash anchors; walls add left/right/top; floor boards add left/right/front/back; fog adds its layer height; the gel frame adds hang/light/left/right. Source coordinates use Blender metres; Godot maps `(x,y,z)` to `(x,z,-y)`.

`verify_stage_kit.py` checks actual exported triangles, two UV channels, PBR maps, opaque/alpha modes, 0.6 sky emission, connector coordinates and exact collision-transform parity. All fourteen exports pass the 512-square sampled UV1 overlap check. `test_stage_kit.gd` confirms runtime texture sizes, shared underlying and active materials, fourteen models, twenty-two material surfaces, fifty-four colliders, bounds within 35 mm between levels, floor height and collision rays. Fog remains nonblocking and there are no embedded practical lights. Blender MCP verifies all fourteen saved module scenes/collections and the showroom without changing the user's open scene.

[Full-detail overview](../reference/stage-kit.png) · [Lower-detail overview](../reference/stage-kit-lod1.png)

[Moonlit sky](../reference/stage-cyclorama-moonlit.png) · [Dusk sky](../reference/stage-cyclorama-dusk.png) · [Mist sky](../reference/stage-cyclorama-mist.png)

[Floor boards](../reference/stage-floor-detail.png) · [Fog over boards](../reference/stage-fog-detail.png) · [Gel frame](../reference/stage-gel-detail.png)

All views were inspected. These are isolated, ungraded asset previews; they do not establish final site lighting or full-garden acceptance.

## Integration status

Thirty-five modules now occupy the assembly: six 2.4 m floor-board panels in the terminal cells, six black studio panels behind the corridor, twenty-one fog cards across the stage, terminal corridor and rockery, and two stored gel frames on the backstage wall. Six shared-material render batches add 14,704 triangles. Eight new collision proxies belong to the studio panels and gel frames; the original cell floor colliders retain walking height zero. The corridor is clear, and the stored gels do not obstruct the hall titles or screens. No new lights are added. The black panels are unshaded and excluded from the bake; transparent fog and gels retain their shared source materials.

The assembly has 160 render meshes and 282,284 triangles. Source SHA256 is `59bd87306524d62ba7a849e12cccdbead5639ab54faee025493564ac874695ed`. Fresh source-matched Cycles coverage is 33/33 demo and 29/29 priority-2 opaque shaded meshes. Stage placement, entry/study/imperial traversal, backdrop receiver linking, bake application and demo replay pass. Blender MCP confirms five directly openable site libraries without changing the user's open scene. Desktop and portrait views were inspected, including the floor and stored-frame wall.

Stationary demo views on the Apple M2 Max measure 101–145 draw calls, 123,868–176,110 primitives and 66,850,688 bytes (63.75 MiB) of textures, with at most four practical lights. Forced-draw medians are 1.34–2.32 ms and p95 intervals 2.36–3.40 ms. This leaves little texture headroom and does not establish phone or full-traversal acceptance.

[Placed floor and chair](../reference/terminal-chair-placed.png) · [Backstage wall and stored frames](../reference/stage-backstage-wall.png)

The existing circular painted backdrop and five linked wash receivers remain in place. Before fitting the new painted cycloramas, review their curvature and side collider alignment, then check enclosure coverage from all garden views. Further site dressing/signs, unlit terminal scrolls, sourced reference stills, final lighting, service contracts and phone acceptance remain open.
