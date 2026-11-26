# Qiushuang facade lighting

The old close frontal spotlight reached only the centre screen bank and made a circular bright patch on the wall. A farther diagonal, warm-neutral hard key now covers all three banks. The twelve amber screens, two amber lanterns and existing geometry remain in place.

![Previous full lighting](native-installed-baseline/desktop-overview.png)

![Current full lighting](installed-native-qiushuang/desktop-overview.png)

![Current portrait screen view](installed-native-qiushuang/portrait-centre.png)

## Source and rebuild

Authoring is `4eb31445`; the complete source and engine GLB are `ba0e8b16`. The key moves from (22,12,2.6) to (26.5,6,3.6), aims at (22,15.94,1.6), changes from 450 to 1200 W and from 45 to 60 degrees, and uses linear RGB (.9,.82,.68). Its source radius remains zero with shadows enabled. Both 65 W amber point lights are retained.

Actual source phosphor-quad centres inside the spotlight cone increase from 192 to 576 of 576 across the three banks. The old layout is restored temporarily and reproduces 192; the verifier then restores the full source state and checks the saved file hash. This is cone geometry, not exposure, occlusion or text-legibility proof. Separate actual Godot editor import checks the source position, aim, cone, range, shadow size and color conversion: all 1152 screen-triangle centres fit the native cone and its 14 m range.

The lighting recipe now reuses existing lantern lights, including Blender-suffixed names. The old recipe duplicates the saved two lights into four; two consecutive corrected runs keep the same two. All 4466 other objects,49 materials and 35 packed images are preserved. The complete GLB binary chunk is byte-identical; restoring the single key record restores the previous JSON. Fourteen other site exports are byte-identical. Sixteen saved-source canonical exports reproduce exactly. Counts stay 264973 render triangles,167 batches,42 cameras,454 colliders and 71 markers.

Run the saved-key check in a separate process:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background blender/authoring.blend --threads 8 --python-exit-code 1 --python scripts/verify_study_lighting.py
```

## Lighting and Godot validation

All six fresh source-lighting phases pass:124 ordinary maps at 128 samples/up to 1024 px,10 backdrop-wash maps at 128 samples/512 px, and seven terminal-spill maps at 2048 samples/512 px. All 141 source PNGs decode. Fourteen isolated Godot phases pass and 72 captured originals verify: eight hall views,36 normal/touch framing views and 28 all-room arrivals. All eight hall and 28 arrival originals were directly inspected; this accepts the one-key adjustment while retaining final art work.

Both actual Mac tours pass 14 rooms and 26 public-command legs at normal 60 Hz physics, with 26 settled camera arrivals, no floor failures and at most four practical lights. All 278 tour images decode and match their recorded hashes. Complete original tours remain in the durable local archive; eight representative originals and complete reports are published here.

Source and engine adoption use verified reversible backups and reject changed disk inputs. Installed validation passes 17 phases, including saved-key/lattice controls, exact canonical exports, site libraries, UV 2, catalogs, resources, runtime caps and cold imports. All 141 reviewed import parameter sets are retained. All 285 engine PNG/catalog inputs match the isolated project; eight installed fixed-clock originals match the reviewed candidate byte for byte. Runtime remains `ec42ec55`. The 26 Python tests pass. User editor sessions were not reloaded.

## Offline Android package

The full debug APK is `589ec5a083157b4897e439ac7178e477303338da402d0fc4d2b2548eb0a56614`, 86,531,491 bytes, for source `ba0e8b16dc984c0655da1290bbb438e6b2a2a2b92d36b31c32f42c083690341f`. Canonical export and the actual offline payload/provenance verifier pass, including packaged texture caches and compiled dependencies. The verifier stops at its first device-call boundary through a stub; no ADB call or installation occurred. The APK is preserved locally. The earlier `d6e42f19` package is historical for this source. Neither package establishes release or physical-device performance.

## Remaining work

This accepts the bounded facade-key correction. Wall texture/bake noise, stage and water boundaries, dark canopy backs, foliage, signage and final composition across all 14 sites remain open. Screen artwork is static; live bulletin content is not connected. Five reference slots (37/42 collected), current phone/2020 Adreno and sustained budgets, authenticated reading/history/AI/presence/social and release remain required. Earlier desktop draw-budget failures are not closed by these checks. The full goal remains active.

`files.json` checks the published originals and proof. Failed fixtures, source controls and import checks remain in `proof/`; all tour originals, the APK and reversible backups remain under `.superpowers/sdd/2026-09-23-garden-completion/`.
