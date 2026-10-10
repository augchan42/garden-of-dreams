# Production runtime texture caps

The reviewed four-import candidate is now applied to the Godot project:
1024² pavilion/wall basecolors with VRAM compression, and aligned 512×170
lossless gate color/normal textures. Mipmaps remain enabled. Original source
PNGs, Blender scenes, runtime scene/camera code and all 141 lighting PNGs
retain their bytes. The source-preservation snapshot checks 479 files.

The native resource check verifies actual loaded sizes, formats, mipmaps,
generated cache bytes and original/active bindings in normal and demo routes.
Correct sidecars with stale 2048²/1024×341 pixels reject. Empty active materials
reject. Three disabled-use controls each mutate real materials in both routes:
shader albedo, shader normal and StandardMaterial3D normal. All pass against
the old guard and reject after the fix. The initial shader-normal control had
no target; its evidence is retained in the ignored continuation archive and
is not counted as a valid regression.

The builder invalidates only these assets' generated caches and MD5 records,
then requires the native cap check before export. Its manifest pins checker
source hashes, actual loaded resources, finalized imports and generated pixels.
The collector rejects missing or stale source/checker/cache/binding evidence
before accessing the phone. The Android profiler checks actual device formats,
footprints and enabled demo bindings before timed sampling; collection and taps
require that device proof. The older gate-only configuration command now uses
the same 512px policy and cache invalidation without changing the atlases.
The host-only gate compatibility command was corrected after the phone build;
its default four-cap configuration behavior is unchanged. `executed-source`
contains current adopted source snapshots. The build manifest independently
pins the exact GDScript checkers executed in the APK.
Sixteen Python tests pass. Actual concurrent publication completes 32 report
generations with zero partial reads. `atomic-writer-final` records the result.

All 44 adopted-source native originals reproduce the reviewed candidate bytes:
14 desktop and 14 portrait arrivals, 12 material close controls and four gate
controls. This retains the prior candidate's visual review; it does not certify
final scene art. Original captures and their hashes are retained here.

The fresh debug APK completed all four build phases and passed verification of
177 bound texture imports/payloads. The APK manifest matches its staged bytes;
compiled profiler/inspector/writer remaps and bytecode hashes are recorded.
APK SHA-256: `68bf7ba2256da70d4d0dcd1de51ea7231528b83cbee60165be59d059b1578cdd`.
The 86,530,973-byte APK stays outside Git.

Actual installed-source Pixel 7 Pro results:

| Check | Result |
| --- | --- |
| Device / renderer | Mali-G710 / Compatibility |
| Native output | 1080×2340 |
| Basecolor sizes / device format | 1024² / ETC2_RGB8 |
| Gate color / normal sizes | 512×170 / lossless RGBA8 and RGB8 |
| Peak texture allocation, all five phases and touch states | 56,632,159 bytes (54.01 MiB) |
| Frame-interval P95 range | 22.403–45.723 ms; 60 fps target fails |
| Actual taps | Cast, recast, close, finale, replay; ten press/release edges |
| Host report reads | 32 complete; zero partial |
| Replay | Terminal room, initial two controls, no reading overlay |
| Captures | 23 archived files hash/dimension checked; eight distinct originals viewed |
| Engine diagnostics in collected logs | None |

Direct inspection retains readable gate characters, slate roof color, warm
lanterns, bronze details and complete local-reading/finale controls. Existing
stage/channel rectangles, coarse bakes, faceted roofs/foliage and dark immediate
replay remain art work. The reading still identifies its local/offline scope.

The previous isolated full-garden run in
[texture-memory-caps](../texture-memory-caps/README.md) saved exactly 6.33 MiB
in all 105 phases and peaked at 62.29 MiB over two tours and 735.791 timed
seconds. That remains comparison evidence, not a fresh sustained run of this
adoption. The current production tools still profile the demo only; integrating
the full tour and collecting adopted-source sustained timing is next. The
specified 2020 Adreno device, sustained 60 fps, final fourteen-site art, five
remaining references, release and authenticated services remain required.

Diagnostic command errors (wrong standalone library, headless graphical audit,
staged-versus-production import fingerprints and compiled-script packaging) are
recorded in `apk-verifier-correction.json`; failed originals remain in the
ignored archive. No APK was installed until the corrected final build passed.
The independent review's disabled-use finding was fixed and re-reviewed without
remaining findings. The full goal remains active.

To configure, reimport and check current resources:

```sh
python3 scripts/configure_runtime_texture_caps.py --project godot --report /tmp/runtime-caps.json
/Applications/Godot.app/Contents/MacOS/Godot --headless --editor --path godot --import
/Applications/Godot.app/Contents/MacOS/Godot --headless --path godot --script res://tests/test_runtime_texture_caps.gd -- --output=/tmp/runtime-cap-resources.json
```
