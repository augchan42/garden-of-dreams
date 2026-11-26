# Full garden phone baseline

On 2026-10-10, the isolated Android profiler completed two whole tours of the
normal garden on a Pixel 7 Pro with Mali-G710 graphics. All fourteen rooms and
52 public-command travel legs passed floor, arrival, destination and restored
control checks. The run used normal time and 60 Hz physics, with source-matched
124/6/7 lighting catalogs. This establishes a traversal baseline; the rendering
budgets still fail.

| Measurement | Result | Target |
| --- | --- | --- |
| Timed rendered frames | 735.865 seconds | At least 600 seconds |
| Whole run, including settling and capture | 946.708 seconds | Recorded separately |
| Grounded floor rays | 35,118 supported; zero misses | Zero misses |
| Complete report reads | 448; zero incomplete | Zero incomplete |
| Texture allocation peak | 71,956,739 bytes (68.62 MiB) | At most 64 MiB |
| Frame-interval P95 across 105 samples | 18.623–28.434 ms | At most 16.667 ms |
| Visible draw calls, maximum | 99 | At most 150 |
| Visible primitives, maximum | 178,601 | At most 300,000 |
| Visible practical lights, maximum | 4 | At most 4 |

All 105 timed phases fail both texture memory and frame timing. None fails the
draw, primitive or practical-light limit. The frame intervals describe delivered
frames, not GPU execution time. PNG readback and the two-second stationary
settling periods are outside the timed phases. The application log contains no
script errors, engine errors or warnings.

The report, application log and all 53 original 1080 × 2340 PNGs are retained in
`actual-phone`. Every capture hash and dimension was verified. Fourteen distinct
first-tour arrival originals were directly inspected; their observations and
hashes are in `direct-original-review.json`. The other 39 originals were not
directly inspected. Hard channel/backdrop boundaries, coarse foliage, mottled
wall lighting and some sign occlusion remain visible. These are not final-art
acceptance images.

`summary.json` contains the derived totals. `phone-pipeline.json` records the
installed APK identity, complete reads, capture hashes and per-phase failures.
`build-report.json`, the three build logs, `phone-profile-build.json` and
`apk-input-verification.json` preserve the actual export provenance. The APK
SHA-256 is `57fecae4f194e5dfa8c4ff0b767aca085176d0c5617fe92ffc8ae2042e548834`;
the APK itself remains outside Git. All 177 bound texture payloads and 212
retained runtime, shader and catalog entries were verified against the prior
atomic-publication APK.

`executed-source` retains the exact four profiling sources used by this APK.
The full profiler extends the frozen demo producer and uses the existing
26-leg public tour. It waits for camera animation completion before stationary
measurements. These are diagnostic source snapshots: the production builder and
collector still run their existing demo profile. The full prototype is not
integrated into those tools. Temporary paths in raw reports identify the actual
run; they are not current production paths.

The first isolated attempt stopped before traversal because its guard tried
to hash a raw GLB that Godot does not ship in the APK. The corrected host runner
checked the packaged GLB remap and imported scene payload against the staged
cache, while the device checked packaged source metadata and full build identity.
Failed-attempt evidence remains in the ignored continuation archive;
`attempt-1-relocation.json` records where its original fixture was moved.

This phone is not the required 2020 Adreno device. This run exercised public
commands and checked control state; it did not inject touch events during the
full tour. Separate demo touch evidence is retained in the
[publication checks](../android-profile-publication/README.md). Rendering
budgets, target hardware, final fourteen-site art, five remaining references,
release and authenticated services remain open. The full goal remains active.
