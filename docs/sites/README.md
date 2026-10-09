# Garden site pages

Each page is the contract for one of the 14 garden locations. All 14 locations are now visitable through the command-driven Godot routes. Future-room interiors remain closed. Site-specific scenery is in place, while final art, sourced references, painted signage, lighting and acceptance work remain tracked in these pages and `../build-status.md`.

- [aojing-guan](aojing-guan.md)
- [daguan-lou](daguan-lou.md)
- [daoxiang-cun](daoxiang-cun.md)
- [hengwu-yuan](hengwu-yuan.md)
- [longcui-an](longcui-an.md)
- [ouxiang-xie](ouxiang-xie.md)
- [qinfang-ting](qinfang-ting.md)
- [qiushuang-zhai](qiushuang-zhai.md)
- [rockery-gate](rockery-gate.md)
- [terminal-cells](terminal-cells.md)
- [tubi-tang](tubi-tang.md)
- [xiaoxiang-guan](xiaoxiang-guan.md)
- [yihong-yuan](yihong-yuan.md)
- [ziling-zhou](ziling-zhou.md)

## Sourced night-set references — 2026-10-08

Eight distinct frames from the published Arrow Video and Shaw Brothers Clips trailers were directly reviewed and saved with unchanged source streams, exact decoder PTS, publisher attribution, rights information and hashes. Required reference coverage is now 34/42. The new frames fill seven generic Shaw night-set slots and Qinfang's night-exterior lighting slot. They guide warm wood/lamps, neutral plaster/stone, limited blue background/foliage light and dark unlit areas for the less-green revision. No production scene or lighting is changed by this collection.

Remaining slots: Aojing 3 (material close view), Hengwu 1 (night set), Qinfang 1 (the specified *Come Drink With Me* bridge pavilion), rockery 2–3 (film cave and dark fog/moon gate), and terminal 1–3 (film cell, historical studio dressing room and dark-room green VT 100). Rejected coarse samples do not count, and do not establish that a suitable view is absent from a film. Reference collection is still incomplete. Evidence: `../reference/external/supporting/shaw-trailers/README.md` and `export/shaw-night-reference-evidence.json`. Final art, device budgets, services and release acceptance remain open.

## Reference collection: 36/42 — 2026-10-08

Aojing's close timber/glazing photograph and Hengwu's night wall/window frame are now directly reviewed and saved with original bytes, attribution and hashes. Both sites have all three required references. Remaining six slots: Qinfang 1, rockery 2–3 and terminal 1–3. Source originals and exact film PTS are documented in the two site reference READMEs. These material/lighting observations do not establish scene identity, measured architecture or final art acceptance. Evidence: `export/aojing-hengwu-reference-evidence.json`.

## Ouxiang complete-source working update — 2026-10-08

The installed complete GLB is `be 80374 c`; saved authoring remains `9356 f 6 ec`. The Ouxiang roof's secondary UV charts are corrected. All six fresh lighting phases passed, including all 124 ordinary receivers, shared wash and terminal spill. No old map was relabelled for the new source.

The isolated native review passed 37 phases. Cold reimport preserves geometry, cameras, collisions and markers; deliberate camera/collider/marker corruption and both missing-roof-policy controls reject. The explicit two-roof import uses lossless 512² RGB 8 maps, no mipmaps, with exact source/UV guards. Other maps keep the 256 px policy. Four framing captures retain their actual PNG dimensions: 1410×600, 390×844, 360×800 and 1080×1976. The last was requested as 1080×2340 but constrained by macOS; it is not a physical phone test.

Both native garden walks cover 14 rooms, 26 legs and 139 original PNGs each. Supported floor ray samples are 17,582 desktop and 17,581 portrait, with zero misses and at most four practical lamps. All captured original hashes are checked. The canonical Blender exporter reproduces all 16 GLBs byte for byte. A separate native inspection verifies the exact three approach render boxes and collision proxies in both saved authoring and stage library; this inspection does not repair them.

M2 Max stationary normal-route renderer allocation reaches 52,600,513 bytes (50.16 MiB), versus 52,517,225 bytes at the final arrival. Demo maximum is 43,512,435 bytes. Bound normal image data is 36,525,582 bytes. These figures do not prove phone, sustained performance, frame timing or release budgets.

Sixteen changed targets were installed with recoverable local backups. Eight production checks passed: import, source contract, full lighting with both roof flags, normal/demo wash, normal/demo terminal spill, and animated water/fog materials. Authoring, current runtime and canonical exporter code were not rewritten by adoption.

Selected original Ouxiang desktop, portrait and settled captures plus the moon composition were directly inspected; 14-site contact sheets were inspected for gross assembly. The roof is more consistent. Black paving rectangles, green-heavy materials and other final art remain visible and unaccepted. Full-resolution all-site art acceptance, the last six reference slots, current Android packaging/device and 2020 Adreno/sustained profiling, release and authenticated readings/history/AI/presence/social remain required.

Use `configure_lightmap_imports.py --size-limit 256 --imperial-lossless 512 --ouxiang-lossless 512` and `test_full_scene_lighting.gd -- --imperial-lossless 512 --ouxiang-lossless 512` for this source. Original logs, executed code, reports and captures are archived here. The evidence index records exact SHA 256 s; absolute scratch paths inside original reports are retained as executed provenance. This checkpoint does not complete the full Garden goal.
