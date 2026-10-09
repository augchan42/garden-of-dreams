# Saved site source audit

Inspected all 14 saved site libraries, the authoring scene and the individual site GLBs on 2026-10-07. Evidence: [`export/site-source-audit.json`](../export/site-source-audit.json). Reproduce with Blender in background mode and `scripts/audit_site_sources.py`.

Current assembly SHA256: `d74e0ff858748d529029c80f0ea11969c121dd71f645effebf55180104099bde`.

Each library has a saved scene. All camera, light, collision and trigger names, transforms and room IDs match the corresponding authoring collection. Camera lens, sensor, clipping and runtime viewport/FOV metadata also match. All 71 trigger empties have room IDs. Sign implementations also match. Blender MCP independently checked the saved library catalogs and hashes without modifying the open scene.

This is a structural inspection. It does not establish complete dressing, visual acceptance, working routes, engine bake application, collected references or phone performance. A textured sign is recorded as such; this audit does not judge its lettering quality. Sites without a title are not automatically failures: the terminal cells, open water pavilion and reed island do not have a required building-title sign in their sheets.

| Site | Markers | Cameras | Temporary typeset sign | Current bake records / eligible meshes |
| --- | ---: | ---: | --- | ---: |
| [aojing-guan](sites/aojing-guan.md) | 3 | 4 | — | 6/6 |
| [daguan-lou](sites/daguan-lou.md) | 3 | 2 | — | 9/9 |
| [daoxiang-cun](sites/daoxiang-cun.md) | 4 | 4 | — | 8/8 |
| [hengwu-yuan](sites/hengwu-yuan.md) | 4 | 3 | — | 10/10 |
| [longcui-an](sites/longcui-an.md) | 4 | 3 | — | 7/7 |
| [ouxiang-xie](sites/ouxiang-xie.md) | 4 | 2 | — | 6/6 |
| [qinfang-ting](sites/qinfang-ting.md) | 7 | 3 | — | 20/20 |
| [qiushuang-zhai](sites/qiushuang-zhai.md) | 5 | 4 | — | 10/10 |
| [rockery-gate](sites/rockery-gate.md) | 3 | 4 | — | 6/6 |
| [terminal-cells](sites/terminal-cells.md) | 18 | 2 | — | 7/7 |
| [tubi-tang](sites/tubi-tang.md) | 5 | 3 | — | 10/10 |
| [xiaoxiang-guan](sites/xiaoxiang-guan.md) | 4 | 3 | — | 7/7 |
| [yihong-yuan](sites/yihong-yuan.md) | 4 | 3 | — | 7/7 |
| [ziling-zhou](sites/ziling-zhou.md) | 3 | 2 | — | 3/3 |

The bake column uses the opaque-mesh eligibility rules in `verify_lightmaps.py`: transparent foliage/fog/water and the unlit stage sky are excluded. A current record must match the canonical assembly hash and have its PNG present. Pixel contents and runtime application need their own checks. All 116 eligible site meshes now have current records; none are missing. All 124 ordinary maps, including the eight shared stage meshes, were freshly rendered at 128 samples for the current owned-key and neutral-fill source. No current record uses camera-only compatibility. The full catalog also passes native finite/nonzero pixel and identical engine-copy checks. Runtime application is checked separately by `test_full_scene_lighting.gd`.

## Next scene work

1. The seven temporary signs are replaced by original painted lettering. Four boards previously intersected their roof eaves, and the pavilion board sat behind its front post; all five now project forward on short wood supports. All 14 libraries have zero remaining FONT objects. Review remaining site materials and dressing under the reduced-green grade alongside the current all-site bakes. Final sign views are saved as `docs/reference/sign-<site>-{arrival,detail}[-portrait].png`.
2. Inspect the reflection hall's water-dominant framing against both saved Blender cameras. Its sheet requires water and reflection to occupy half the frame; the separate pond action has measured desktop/portrait coverage above half-frame and checked return controls.
3. Finish remaining site materials and dressing, rebake any altered lighting or geometry and check pixel contents, runtime application, route views and practical-light limits. The demo and priority-2 bakes were refreshed after the final lettering and mount changes.
4. Collect the three external visual references required by each site sheet. Generated production art and our game captures do not satisfy those reference requirements.
5. Profile full traversal and a target phone, and verify outstanding service contracts before claiming the full goal complete.

The site sheets and earlier build-status entries contain historical statements about unfinished kits. The later kit completion records supersede those statements. They do not supersede the remaining signage, references, final lighting and acceptance requirements.


The 2026-10-07 refresh includes twelve owned exterior-site Area washes. All fourteen source libraries retain zero structural differences from authoring and matching current site-sheet hashes. The separate rig inventory distinguishes terminal/window and tunnel/no-wash exceptions, and records three newly saved owned keys with no missing required key or wash. Area lights remain absent from glTF and transfer through native backdrop maps; those are additional to the table’s ordinary bake counts. See `export/lighting-rig-audit.json` and `baked-lighting.md`.

## Current source checkpoint — 2026-10-09

The working source is now `1380ceca` with authoring `0d3e84e3`. Fresh ordinary/wash/spill lighting and the updated water/reed kits are installed together. Both current native rendered tours pass fourteen rooms, twenty-six legs and 139 original captures each, including cell return; desktop 17,582 / portrait 17,581 support samples, no misses, maximum four practicals and time scale 1. The saved-source/import contracts retain 42 cameras, 400 colliders and 71 markers. Current original reports and hashes are retained in `reference/ziling-source-art/README.md`. Final site art, physical-device/sustained performance, packages and authenticated services remain open.
