# Texture memory cap comparison

An isolated four-import candidate brought the full garden below the 64 MiB
texture budget on a Pixel 7 Pro with Mali-G710 graphics. Production remains
unchanged. The same normal-physics profiler completed two whole tours of all
fourteen rooms, with 52 public-command travel legs and 735.791 timed seconds.

| Measurement | Production baseline | Isolated candidate | Target |
| --- | --- | --- | --- |
| Peak texture allocation | 71,956,739 bytes (68.62 MiB) | 65,318,147 bytes (62.29 MiB) | At most 64 MiB |
| Frame-interval P95, 105 phases | 18.623–28.434 ms | 18.643–28.465 ms | At most 16.667 ms |
| Maximum visible draw calls | 99 | 99 | At most 150 |
| Maximum visible primitives | 178,601 | 178,601 | At most 300,000 |
| Maximum practical lights | 4 | 4 | At most 4 |
| Supported grounded floor rays | 35,118; zero misses | 35,120; zero misses | Zero misses |

Each of the 105 matched phases saves exactly 6,638,592 bytes (6.33 MiB).
The candidate has 1,790,717 bytes of headroom below 64 MiB. All phases pass
memory, draw, primitive and light limits; all still fail frame timing. There
were 456 complete JSON reads, zero partial reads and no engine diagnostics.
Frame intervals describe delivered frames, not GPU execution time. Settling
and image readback are outside the timed phases.

Only four import size limits change in the isolated fixtures:

| Original image | Imported baseline | Imported candidate | Compression |
| --- | --- | --- | --- |
| Pavilion basecolor | 2048² | 1024² | VRAM compression |
| Wall basecolor | 2048² | 1024² | VRAM compression |
| Gate inscription color | 1024×341 | 512×170 | Lossless RGBA8 |
| Gate inscription normal | 1024×341 | 512×170 | Lossless RGB8 |

Original PNGs, normal/ORM atlases, the scene, runtime, shaders, cameras and
lighting maps retain their bytes. All four imports retain mipmaps. Native
checks verify actual loaded dimensions and the original and active material
bindings in normal and demo routes. An empty StandardMaterial3D override was
incorrectly accepted by the first guard; the corrected guard rejects it, and
both baseline and candidate checks pass. That failure and correction are
retained in `active-guard-red-accepted.json` and `active-guard-green-rejected.json`.

The full APK checks the actual Android resource sizes, formats and stored mip
footprints before running the unchanged timed profiler. Both basecolors load
as ETC2_RGB8 at 699,064 stored bytes each; inscription color and normal use
463,772 and 347,829 bytes. Decompressed readback bytes are reported separately
and are not GPU allocations. The previously capped moon remains 512² RGB8.

Native quality evidence retains 88 original images in 44 baseline/candidate
pairs; seven pairs are byte-exact. Maximum normalized RGB RMSE is 0.004910.
Twenty-six native originals were directly inspected, including all fourteen
candidate portrait arrivals and inscription/material close views. Phone
review covers fourteen distinct normal-route arrivals, eight demo/touch
originals and five prior baseline originals. Gate strokes, timber color,
lanterns and bronze details remain visible. Fine inscription plaster detail
is softer. Existing stage/channel edges, coarse plants, wall bake artifacts
and some sign occlusion remain final-art work. The other 39 full-tour phone
captures were hash/dimension checked but not directly inspected.

A separate APK restores the byte-exact production demo profiler and retains
the same 177 bound texture imports/payloads, imported scene and protected
runtime/shader/catalog entries as the full candidate. Actual taps passed
cast, recast, close, finale and replay, recording ten press/release edges.
Texture allocation stayed at 56,632,159 bytes (54.01 MiB) across all five
sampled phases and five touch states. Demo P95 remains 19.266–35.084 ms.
Replay returns to the cell with the two initial controls and no reading
overlay. Its darker immediate capture, and flatter demo background facade,
also appear in the prior atomic-publication baseline; they are not changes
established by this cap comparison.

`full-phone-comparison.json`, `phone-pipeline.json`, `phone-profile-build.json`
and `actual-phone` retain the full run. `touch-phone` retains the demo build,
manifest, reports and touch evidence. Full APK SHA-256:
`a44a0b5e17469eed46a859ed84c41df6bed25e68c8b14f25b89df16be0f59d95`;
demo APK SHA-256:
`c32672fe3826036eabc3f2cdf2e147cfa01da5a7e15fa53a22e971725e1c3674`.
The APKs stay outside Git. `archive-manifest.json` pins every retained file.
Temporary paths in raw records identify the executed fixtures.

`executed-source` contains diagnostic snapshots. The production builder and
collector still use their existing demo path and do not enforce these four
caps. Production adoption needs reusable import/resource/provenance guards
and current installed-source verification. Native fixture failures from old
normal/ORM dimensions and the historical inscription-ratio assertion were
corrected before phone testing; original failed evidence remains in the
ignored continuation archive. The first evidence-publication attempt had a
wrong capture-source path and is also retained there.

This 2022 Mali phone is not the specified 2020 Adreno device. The full tour
uses public travel commands; actual touch input is tested separately in the
demo. Sustained 60 fps, final fourteen-site art, five remaining references,
release and authenticated services remain open. The full goal remains active.
