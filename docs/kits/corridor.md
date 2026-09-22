# Corridor kit

`blender/kits/KIT_corridor.blend` contains an editable scene for each module and LOD, plus a showroom containing eight collection instances. Modules use local origins and metre units. The original `export/kits/KIT_corridor.glb` and `_LOD1` paths now point to the straight module; individual modules live in `export/kits/corridor/`.

| Module | LOD0 triangles | LOD1 triangles | Ports | Rise |
| --- | ---: | ---: | --- | ---: |
| Straight, 3 m | 1,148 | 458 | South, north | 0 m |
| 90° corner | 1,004 | 400 | South, east | 0 m |
| T-junction | 972 | 388 | South, north, east | 0 m |
| Stair bay, 3 m | 1,208 | 482 | South, north | 0.6 m |

Every module has a 1.8 m walking width, roof, posts/brackets, balustrades on closed sides, west-side lattice, separate collision meshes and named `PORT_` empties carrying `connection=corridor_1.8m`. The straight module has two shared-end posts. Connection coordinates are in `export/kits/corridor/manifest.json`; the validator records their exported Godot coordinates in `validation.json`.

The stair bay has six visible treads with a smooth collision ramp. Its rails and roof follow the rise. Corner and T roofs use a continuous gridded surface across the junction rather than intersecting gable meshes. Both LODs retain the same connector positions and collision geometry. LOD1 measures 39.84–39.92% of the corresponding full-detail triangle count.

Rebuild with Blender on `blender/authoring.blend`, using `--python-exit-code 1 --python scripts/complete_corridor_kit.py`. The authoring garden is read for shared materials and is not saved by this script. `package_libraries.py` preserves the completed corridor library instead of replacing it with the starter bay.

Verification:

- `python3 scripts/verify_corridor_kit.py` reads all eight GLBs and checks actual triangle counts, the 2,000-triangle budget, LOD ratios, UV0/UV2, connector metadata/positions and matching collision transforms.
- `godot/tests/test_corridor_kit.gd` imports the actual assets and moves a capsule through all ports at both LODs, including ascending and descending the stair ramp.
- `docs/reference/corridor-kit-0001.png` shows LOD0 in front and LOD1 behind; reviewed for shape retention.

All eight variants now use the same 2048² architectural PBR atlas as the pavilion. Each exports one render primitive with base-color, normal and metallic/roughness maps. Sharing the atlas avoids a second texture set in the garden. `scripts/verify_pavilion_atlas.py --kit corridor` checks the actual embedded images and UV regions.

Sixteen straight bays replace Qinfang’s four approach corridors. The integration script preserves the bridge balustrades and removes the old corridor parts, including misplaced beam remnants. Use local `matrix_basis` when copying unlinked library objects; evaluated `matrix_world` can be stale and lose rail collider offsets.

Automatic distance-based LOD switching, remaining site placement, final lighting and target-phone acceptance remain unfinished. Other kits still need their missing variants; this library does not complete the whole asset inventory.
