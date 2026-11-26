# Android profile report publication

The dedicated profiler previously truncated its public JSON file before writing
the replacement. A reader could see an empty or partial report during capture
and touch updates. It now closes a complete temporary file and publishes it by
renaming within the same directory. The producer remains serialized.

The collector requires the writer's recorded SHA-256 to match both the current
project and staged export before accessing the device.

Validation on 2026-10-10:

- Actual producer regression: original writer yielded 321 incomplete reads out
  of 327 concurrent reads. Replacement yielded zero out of 15, across 32 large
  report generations. Each run used its own temporary project and app data.
- Missing writer proof, changed production writer and changed staged writer
  were each accepted before the fix and rejected afterward, before device
  access. All nine Python tests passed.
- Fresh APK: all three build phases passed without engine diagnostics; original
  scene, runtime, shader/catalog entries and 177 bound texture imports verified.
- Pixel 7 Pro: 479 complete report reads, zero incomplete reads; five actual
  touch stages (ten press/release events) passed using the original reader,
  without JSON retries. All eight original views were inspected.
- Sampled texture peak: 63,270,751 bytes (60.34 MiB). Frame-interval P95 ranged
  from 19.948 to 34.535 ms; the 60 fps target is still unmet.

Raw reports, logs and originals are in `red`, `green` and `phone`; their hashes
are in `manifest.json`. The APK hash is in `phone/build-report.json`; the APK
itself stays outside Git. Paths in raw reports identify the actual temporary
run. Reproduce the producer test with:

```sh
python3 scripts/test_profile_report_publication.py --output /tmp/publication-check
python3 -m unittest discover -s scripts/tests
```

The isolated [full garden phone baseline](../full-garden-phone-baseline/README.md)
subsequently completed two normal tours, 52 legs and 735.865 timed seconds, with
448 complete reads and zero incomplete reports. Texture allocation and frame
timing remain over budget. The full prototype is not yet integrated into the
production profiling tools.

This fixes diagnostic publication. Rendering budgets, 2020 Adreno hardware,
final art, five remaining references, release and authenticated services remain
open. Source Blender files and the user's running editors were retained.
PR #22's GitGuardian finding remains user-owned.
