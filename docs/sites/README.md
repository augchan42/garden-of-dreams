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


## Neutral stage floor — 2026-10-09

The saved canvas base changes from green (.055,.095,.037) to muted warm gray (.065,.060,.055), with all 4,467 objects, 47 other materials and 621 exported mesh attributes preserved. Fourteen other site GLBs remain byte-exact. Current source `c9d4fb30`, authoring `43d7e33e` and runtime `80f64655` are recorded in `export/stage-floor-palette-evidence.json`.

Six source phases refresh 141 lightmaps. Forty native phases pass: 38 positive checks and two expected base-color rejection controls. Saved default exports reproduce 16 GLBs exactly. Both desktop and portrait tours visit 14 rooms across 26 legs, with zero unsupported floor rays and at most four practicals. All 409 review PNGs are hashed and dimension-checked; 52 original files were directly inspected. Fifteen installed checks pass, with 47 installed originals matching the review exactly. Evidence: [neutral stage floor](../reference/stage-floor-palette/README.md).

Final art remains open, including red-court/imperial portrait composition, Hengwu arrival composition, ground/water closure, foliage and signage. Five reference slots remain (37/42 collected). Current physical phones, 2020 Adreno/sustained budgets, release and authenticated services still require work. The Android package is stale. PR14 remains separately held for security approval. The full goal remains active.


## Courtyard and imperial portrait cameras — 2026-10-10

Runtime `7970380d` fits the courtyard facade, doors and primary banana plant above portrait controls, restores the overview through Look and preserves selected details through rotation. Original desktop poses return correctly; touch actions remain scrollable. The imperial portrait overview gives the facade more usable height while retaining the roof tiers, moon and closed doors. Source `c9d4fb30`, authoring `43d7e33e`, geometry and all141 lighting PNGs remain unchanged.

Positioned courtyard RED20 and imperial RED6 precede32 passing full native checks and three repeated architecture modes after a test-only foliage wait correction. Both actual Mac tours visit14 rooms over26 legs with zero unsupported floor samples and at most four practicals. The452 full-run originals and25 repeated architecture originals are hashed and dimension-checked;25 full-run original file paths and the repeated nunnery original were directly inspected. Twenty-four repeated architecture images reproduce their full-run counterparts exactly. Eleven installed checks pass, and all98 installed camera/arrival images reproduce the reviewed candidate exactly. Evidence: [camera checks and original images](../reference/courtyard-portrait-framing/README.md).

This is two-room camera acceptance. Hengwu composition, stage seams, dark shading, ground/water closure, foliage, signage and final14-site art remain open. Reference coverage remains37/42; current phones,2020 Adreno/sustained budgets, release and authenticated services remain required. The full goal remains active.


## Paving joins — 2026-10-10

Current source `ba40866e` / authoring `7eba169a` removes 84 positive coplanar paving overlaps by partitioning 26 render objects. The original floor footprint is retained within 10 micrometres; all collision geometry, 42 cameras, 71 markers, materials and runtime `7970380d` are preserved. Render geometry is 266,533 triangles. Eight other site exports remain byte-exact. The nunnery's black forecourt rectangle is replaced by continuous stone and plum shadows.

Six source phases regenerate 141 lighting PNGs. The 45-phase native review has 44 positive passes and one intended baseline-floor rejection. Both actual Mac tours visit 14 rooms over 26 legs with no unsupported floor samples and at most four practical lights. Three Ziling modes are repeated after a test-only real 250-millisecond foliage wait; runtime LOD remains enabled. All 28 arrivals, eight moving samples, eight matched floor controls and 35 repeated reed captures were directly inspected: 79 distinct original paths.

Twenty-two installed checks pass. All 85 installed camera/floor/arrival originals reproduce the reviewed files exactly. The first installation also passed all 22 native checks, then rolled back all 29 targets after a report-field comparison error; its 85 originals match independently. The corrected helper reads actual PNG dimensions. Failed source, native and installation attempts are retained in the evidence archive.

This closes the duplicate paving defect. Hengwu's arrival view is next: show its table and pierced stones while preserving the accepted detail actions. Final fourteen-site art, five missing references (37/42), current phones, 2020 Adreno and sustained budgets, release and authenticated reading/history/AI/presence/social remain open. Evidence: [paving checks and originals](../reference/paving-surface-joins/README.md). The full goal remains active.
