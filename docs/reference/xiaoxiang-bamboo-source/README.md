# Bamboo source repair — 2026-10-10

The three bamboo sizes now use a continuous closed culm for each stalk, three joint collars aligned to its axis, and narrower leaf cards. The small clump now meets the 2.5 m minimum. Four Xiaoxiang and three Qinfang plants match the saved kit. Colors and atlas cells are preserved.

| Asset | LOD0 triangles | LOD1 triangles | Measured height |
| --- | ---: | ---: | ---: |
| Small bamboo | 564 | 204 | 2.511 m |
| Medium bamboo | 940 | 340 | 3.457 m |
| Large bamboo | 1,316 | 476 | 4.370 m |

Complete authoring SHA-256: `0f93c42421a17b85b297fa0ff5447fad95cb7b98afeff183a2282ffe060492a4`. Assembly export and Godot source: `faa8a7fe4a7a399899e84373c0550c8ff2f5f15ab0273109e8ea68f433b8fe0f`. Runtime remains `bde869171ad37d520ce34d10aa1ca825a327a6c6c6ce13e3dfafbeca6be5ba95`.

The assembly has 264,973 render triangles, 1,560 fewer than before. All 167 render batches, 42 cameras, 454 colliders and 71 markers are retained. The source comparison preserves 4,460 other objects and 48 materials. Export comparison preserves 614 other expanded mesh records, all node transforms and metadata, 13 other site exports and ten non-bamboo flora exports.

## Verification

- The portable saved-source validator checks 27 meshes across the kit, assembly, two affected libraries and linked master. The previous source fails for disconnected internodes; the repaired source passes.
- Fresh generation reproduces all sixteen saved flora variants semantically. Default reexport reproduces all sixteen assembly/site GLBs byte for byte.
- Six complete source lighting phases pass. All 124 ordinary receivers have current maps; 141 source PNGs match the engine copies, including wash and terminal spill.
- Thirty primary native checks and ten additional source-guard checks pass. Both actual Mac tours visit fourteen rooms over twenty-six travel legs with no floor misses, time scale 1, physics 60 Hz and no more than four practical lights. The twelve source guards change only the complete assembly digest; their assertions are retained.
- Sixty-four original images were directly inspected: twenty-four public lit/ID views across both detail levels and orientations, twenty-eight all-room arrivals, and twelve affected moving/settled views. `native/direct-original-visual-review.json` records their hashes and observations.

The first isolated review loaded an old 1024 px imperial roof cache despite a 512 px import cap. The stale generated cache was archived and regenerated from the unchanged source/settings. The unchanged lighting check and complete native review then passed. The first retry also stopped on an existing docs directory; only fixture setup was made idempotent. Failed attempts and their recovery records are retained.

Reports retain their executed absolute paths. Only the sixty-four directly inspected originals are archived here; full-tour reports also list other technical captures that were not individually reviewed. Archived file hashes are recorded in `archive-files.json`.

Installed verification passed 21 checks. All 52 public/arrival original images reproduce the reviewed candidate byte for byte. `installed/application.json` records executed commands, logs and exact hashes. Recoverable backups remain in the local ignored adoption directory. The open user editors were not reloaded or saved.

## Remaining work

This accepts the bamboo source repair. Large ceiling fields, leaf cropping, foliage density and granular lighting still need art work. Diagnostic alternative camera poses were not installed. Final fourteen-site art, five missing reference slots (37/42 collected), current physical-phone and sustained performance, release, and authenticated reading/history/AI/presence/social remain open.

![Bamboo arrival, full detail](native/public-views/desktop-arrival-lod0-lit.png)

![Portrait bamboo arrival](native/arrivals-portrait/route-mobile-bamboo.png)
