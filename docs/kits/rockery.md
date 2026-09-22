# Rockery kit

Editable library: `blender/kits/KIT_rockery.blend`. Exports: `export/kits/rockery/`; Godot copies: `godot/assets/kits/rockery/`. Reproduce with `scripts/complete_rockery_kit.py`. The legacy `KIT_rockery.glb` paths now contain the medium stone.

Six variants have independent 40% LODs, two UV channels, separate static concave collision and the shared architectural PBR atlas:

| Variant | Dimensions / features | LOD0 → LOD1 triangles |
| --- | --- | --- |
| Small | 1.1 m high; one piercing | 448 → 178 |
| Medium | 2.2 m high; two piercings | 534 → 213 |
| Large | 3.3 m high; three piercings | 634 → 252 |
| Arch | 1.4 m deep; 2.2 m nominal opening; two side piercings | 500 → 200 |
| Tunnel | 4 m long; 2.2 m nominal opening; uneven outer shell | 824 → 328 |
| Cliff | 6 m wide; roughly 3.6 m high; uneven face and two piercings | 1,024 → 408 |

The arch and tunnel have front/back connection markers on the ground plane. They provide a rock shell, not a walking floor; the receiving site must supply continuous paving. The floor contact lies at Z=0 in Blender. Collision retains the LOD0 shell at both detail levels so traversability does not change with distance.

The source build ray-checks every drilled opening and a nine-ray passage grid against both render LODs. `verify_rockery_kit.py` checks exported triangle budgets, two UV channels, collision identity and port transforms. `verify_pavilion_atlas.py --kit rockery` validates embedded texture pixels, PBR bindings and padded material regions. Godot tests cover imported materials, pierced collision, solid bodies and offset capsule traversal through the arch and tunnel in both directions at both LODs.

The Blender showroom contains twelve instances, a camera and a light. Render: `docs/reference/rockery-kit-0001.png`. Four tunnel sections, two arches and two cliffs are now placed at the rockery gate. The tunnel sections are fitted to the site’s curved centreline with matching collision deformation. Standing-stone placement, automatic LOD switching, final art/lighting and target-phone performance remain open.
