# Saved site source audit

Inspected all 14 saved site libraries, the authoring scene and the individual site GLBs on 2026-10-04. Evidence: [`export/site-source-audit.json`](../export/site-source-audit.json). Reproduce with Blender in background mode and `scripts/audit_site_sources.py`.

Current assembly SHA256: `4755afea99f052791f9906c7b27d3108d4929fa13bba8c3ad3a0c751edf0846b`.

Each library has a saved scene. All camera, light, collision and trigger names, transforms and room IDs match the corresponding authoring collection. Camera lens, sensor, clipping and runtime viewport/FOV metadata also match. All 71 trigger empties have room IDs. Sign implementations also match. Blender MCP independently checked the saved library catalogs and hashes without modifying the open scene.

This is a structural inspection. It does not establish complete dressing, visual acceptance, working routes, engine bake application, collected references or phone performance. A textured sign is recorded as such; this audit does not judge its lettering quality. Sites without a title are not automatically failures: the terminal cells, open water pavilion and reed island do not have a required building-title sign in their sheets.

| Site | Markers | Cameras | Temporary typeset sign | Current bake records / eligible meshes |
| --- | ---: | ---: | --- | ---: |
| [aojing-guan](sites/aojing-guan.md) | 3 | 3 | — | 0/6 |
| [daguan-lou](sites/daguan-lou.md) | 3 | 2 | — | 9/9 |
| [daoxiang-cun](sites/daoxiang-cun.md) | 4 | 4 | — | 0/8 |
| [hengwu-yuan](sites/hengwu-yuan.md) | 4 | 3 | — | 0/10 |
| [longcui-an](sites/longcui-an.md) | 4 | 3 | — | 0/7 |
| [ouxiang-xie](sites/ouxiang-xie.md) | 4 | 2 | — | 0/6 |
| [qinfang-ting](sites/qinfang-ting.md) | 7 | 3 | — | 20/20 |
| [qiushuang-zhai](sites/qiushuang-zhai.md) | 5 | 4 | — | 10/10 |
| [rockery-gate](sites/rockery-gate.md) | 3 | 4 | — | 6/6 |
| [terminal-cells](sites/terminal-cells.md) | 18 | 2 | — | 7/7 |
| [tubi-tang](sites/tubi-tang.md) | 5 | 3 | — | 10/10 |
| [xiaoxiang-guan](sites/xiaoxiang-guan.md) | 4 | 3 | — | 0/7 |
| [yihong-yuan](sites/yihong-yuan.md) | 4 | 3 | — | 0/7 |
| [ziling-zhou](sites/ziling-zhou.md) | 3 | 2 | — | 0/3 |

The bake column uses the opaque-mesh eligibility rules in `verify_lightmaps.py`: transparent foliage/fog/water and the unlit stage sky are excluded. A current record must match the canonical assembly hash and have its PNG present. Pixel contents and runtime application need their own checks. All eight later sites lack current records, totaling 54 eligible meshes. Older PNGs still on disk are not current evidence. The six demo/priority-2 sites have 62 current records.

## Next scene work

1. The seven temporary signs are replaced by original painted lettering. Four boards previously intersected their roof eaves, and the pavilion board sat behind its front post; all five now project forward on short wood supports. All 14 libraries have zero remaining FONT objects. Review remaining site materials and dressing under the reduced-green grade before the final all-site bake. Final sign views are saved as `docs/reference/sign-<site>-{arrival,detail}[-portrait].png`.
2. Inspect the reflection hall's water-dominant framing against both saved Blender cameras. Its sheet requires water and reflection to occupy half the frame; existing runtime framing is not proof of that requirement.
3. Finish remaining site materials and dressing, then bake all final eligible meshes and check pixel contents, runtime application, route views and practical-light limits. The demo and priority-2 bakes were refreshed after the final lettering and mount changes.
4. Collect the three external visual references required by each site sheet. Generated production art and our game captures do not satisfy those reference requirements.
5. Profile full traversal and a target phone, and verify outstanding service contracts before claiming the full goal complete.

The site sheets and earlier build-status entries contain historical statements about unfinished kits. The later kit completion records supersede those statements. They do not supersede the remaining signage, references, final lighting and acceptance requirements.
