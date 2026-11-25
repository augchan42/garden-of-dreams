# Qiushuang screen openings

The old lattice crossed the amber CRT faces. Thirty-three of the 42 existing bars now sit in the gaps around the screens. All three banks retain four monitors and seven bars in each direction. Desks, scrolls, doors, aisle, cameras, collisions and materials are preserved.

![Before: original lattice, equal unbaked view](native-unbaked-baseline/desktop-left.png)

![After: cleared screen faces, equal unbaked view](native-unbaked-candidate/desktop-left.png)

![Installed source with fresh lighting](native-fixed-installed/portrait-centre.png)

## Source and rebuild checks

The saved authoring is `f3ed820c`; the complete GLB is `72ad817f`. Source rays from both authored and runtime bank positions test all 576 actual phosphor-quad centres per pose. Blocked samples drop from 180 to zero of 1,152. Restoring the old bar positions reproduces the failure. The saved file repeats the clear result. These sampled rays do not prove every pixel of text is legible.

Only 33 object translations change. All 4,434 other objects, 49 materials and 35 packed image hashes are preserved. The export changes only Qiushuang wood positions and its repacked UV2. Every other expanded attribute, node transform and embedded image is exact; the other 14 site GLBs are byte-identical. Counts stay at 264,973 render triangles, 167 batches, 42 cameras, 454 colliders and 71 markers.

The first exporter shifted the joined wood origin and changed unrelated normals. The canonical exporter now applies lattice translations to disposable copies before joining. Re-exporting the saved candidate reproduces all 16 exports exactly and preserves all 4,467 source objects in memory. The same exporter reproduces all 16 previous-source exports exactly. The generator also reproduces the revised openings: native rays give 180 blocked samples for its old layout and zero for the revised one, with the saved placements reproduced and non-monitor hall patterns unchanged.

Re-run saved-source rays in a separate process:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background blender/authoring.blend --threads 8 --python-exit-code 1 --python scripts/verify_qiushuang_lattice.py
```

## Lighting and native integration

All six fresh lighting phases pass for the new source: 124 ordinary maps, 10 backdrop-wash maps and seven terminal-spill maps. Ordinary bakes use 128 samples at up to 1024px, washes use 128 at 512px and spill uses 2,048 at 512px. No old map is relabelled as a new bake. Fresh sampling changes 127 source PNGs; 14 remain byte-identical. All 141 reviewed engine import parameter sets are preserved.

The isolated integration passes its 14 phases and verifies 72 native PNG hashes and dimensions: eight hall views, 36 normal/touch framing views and 28 all-room arrival views. Both actual Mac tours pass 14 rooms and 26 route legs, with all 26 camera arrivals settled, no floor failures and at most four practical lights. All 278 tour PNGs decode and match their recorded hashes. Complete tour images remain in the durable local archive; the tracked reports retain all original hashes and eight representative event/settled images are included here.

Installed validation passes 16 phases, including saved-source reproduction, site-library audit, UV2 sampling, current catalogs, native resource/cap checks and two forced cold imports with rejection controls. All 285 engine PNG/catalog inputs match the isolated project exactly. Eight fresh candidate/installed screen views also match byte for byte under the same fixture clock. Product runtime remains `ec42ec55`.

The initial installed capture and a serial retry hit the unchanged 150-second deadline. The trace identifies the wait for an automatic `frame_post_draw` after the scene is static. The capture fixture now requests a native draw through [RenderingServer.force_draw](https://docs.godotengine.org/en/stable/classes/class_renderingserver.html#class-renderingserver-method-force-draw) before readback. An unfrozen comparison then exposes a one-level difference in the lower interface of one portrait image; all scene pixels and the seven other images match. Freezing animated shader clocks equally at 3 seconds produces eight exact images. Original failed reports, diagnostics and captures are retained; no pixel tolerance or deadline was relaxed. The product scene and runtime are unchanged by these fixture corrections.

## Android diagnostic package

The full debug APK is `d6e42f19`, 86,531,491 bytes, for source `72ad817f`. Offline preflight reaches the first device-call boundary through a stub without calling ADB. All 194 exported texture caches match the staged project and seven compiled dependencies are verified. All 177 previously bound payload paths remain present; 70 corresponding fresh lightmap payloads change. The APK is preserved locally and has not been installed. It is not a release or physical-device acceptance.

## Remaining work

This accepts the bounded screen-opening repair. The centre wall is still bright and mottled; coarse bakes, backdrop boundaries and faceted geometry remain final art work. Static screen artwork is not live bulletin content. Final art for all 14 sites, five missing references (37/42 collected), current phone/2020 Adreno/sustained budgets, authenticated services and release remain open. The desktop draw-budget failure recorded before this change is not closed by these checks.

`files.json` verifies the published archive. Source preservation, failed controls, canonical/generator reproduction, direct image review, installed validation and APK checks are under `proof/`. The complete local archives and reversible adoption backup are under `.superpowers/sdd/2026-09-23-garden-completion/`.
