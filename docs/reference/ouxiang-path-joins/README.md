# Ouxiang foreground path joins

The directly reviewed 390 × 844 Ouxiang portrait has two nearly black foreground rectangles beside otherwise lit paving. CPU ray/triangle checks attribute both sampled rectangles to overlapping top faces of the stage's stone approach, not the animated water. Nearby water samples intersect the separate Qinfang water mesh. The ray camera matches the saved native camera position, target, 55° FOV and viewport. Transparent blends/fog are excluded. A native surface-ID/control render is still required to confirm runtime visibility and the cause of the visible dark areas.

| Native screenshot pixel | Geometric first hits | Native RGB8 | Source RGB16 red samples | Nearby lit paving comparison |
| --- | --- | --- | --- | --- |
| (34, 468) | Path triangles 171 and 183 at the same depth | (0, 3, 0) | 0.000156 / 0.000057 | Pixel (12, 485): red 0.559 |
| (193, 512) | Path triangles 170 and 158 at the same depth | (0, 2, 0) | 0.000159 / 0.000018 | Pixel (83, 493): red 0.543 |

Both overlapping hits have distinct UV2 ownership. Source-map samples use the uncompressed 1024px RGB16 PNG; they are not measurements of the imported compressed 256px texture or full shader response. PNG CRCs, scanline reconstruction and every high byte were checked. The PNG source record matches installed GLB `361a67c7`; engine/source PNG bytes match. The stage primitive's attributes and indices are unchanged in the pending complete-bake candidate `be80374c`. These findings support a paving-join issue for native confirmation; they do not establish a water shader fault or final water acceptance.

`path-diagnosis.json` records three boxes and a proposed repair: retain the horizontal crosspiece, shorten the first vertical render slab from 5.0 to 4.1m and the second from 7.6 to 5.8m so they meet the crosspiece edges. The source-constructor decimal rectangles have 4.86m² of overlap; the proposal removes this positive-area overlap while preserving their 31.5m² union across all 99 corner/edge/open-cell membership classes. Serialized GLB bounds match those decimals within 1e-5m. This is a proposal, not an applied Blender or engine fix. Existing collision geometry must remain unchanged.

The inferred owners are the three `LONGCUI_approach` render objects created by `scripts/refine_nunnery.py`. Exact saved Blender object ownership has not yet been inspected; it must be confirmed before mutation. After that, the candidate needs controlled native export preservation, fresh source-matched lighting, native before/after views and the nunnery/western route checks. The current Ouxiang complete-source bake and review continue without a second native graphics job. User live Blender and Godot instances are untouched.

The two immutable complete-scene GLBs are reused from the existing imperial/Ouxiang archives, rather than copied again. Original path-map PNG/record/import settings, exact executed CPU scripts and reports are retained here. Temporary script input paths describe the executed environment; immutable input paths and hashes are recorded separately. No geometry, material, lightmap or shader was installed by this diagnosis.
