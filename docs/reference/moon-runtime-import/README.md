# Moon runtime import and sampled phone memory

The moon painting remains unchanged in Blender, the GLB and the original PNG. Godot now resizes its runtime import from 1254×1254 to 512×512, with mipmaps and lossless compression. Automatic 3D recompression is disabled for this painted texture. The decoded RGB8 mip chain occupies 1,048,575 bytes.

Editing the sidecar alone had left an oversized generated cache. `scripts/configure_moon_paint_import.py` validates the cache path, changes only the moon settings and invalidates only its CTEX and MD5. The Android debug builder regenerates this import and checks the resource Godot actually loads before export. The collector requires that proof and the matching test/painting contract digests; legacy manifests must be rebuilt.

The final actual-resource test rejects the original 1254px import and passes the installed normal and demo scenes at 512px. Both imported and active materials retain the same albedo/emission painting resource. Native palette and allocation checks pass in both modes. Across 28 fixed-clock normal arrival pairs, 16 are pixel-identical and 12 change within the visible moon. All 28 installed arrival images reproduce the candidate exactly.

The 223px and 253px native/adapter/missing-paint controls pass. Runtime downsampling changes paint samples: the 18 old/new image pairs have maximum RMSE 0.004343 and maximum channel difference 0.043137. Missing-paint controls remain exact. The final controls reproduce all 36 PNGs from the previously reviewed prototype, despite different generated CTEX bytes. Direct original review is recorded in `direct-original-review.json`.

The final dedicated Pixel 7 Pro debug APK is 91,056,452 bytes. Its finalized imports and 177 normal-route file bindings match the archive payloads. Five actual demo samples and cast/recast/close/finale/replay (10 touch edges) complete. Peak sampled texture memory is 63,270,751 bytes (60.339 MiB), below 64 MiB. The original uncapped current-source run peaked at 68,510,230 bytes (65.336 MiB); the reduction is 5,239,479 bytes.

This is sampled memory acceptance on a 2022 Mali phone. Final-run p95 frame intervals are 22.383–45.863 ms, so 60 fps remains unmet. Full normal-garden phone traversal, sustained performance, the 2020 Adreno target, final site art, release packaging and authenticated services remain open. Replay images are captured immediately after input and do not establish settled lighting. The producer's incomplete-JSON publication race is a separate follow-up; this diagnostic used bounded reader retries and complete build-manifest matching.

Evidence includes actual-resource RED/GREEN reports, native captures, original PNGs, import/cache configuration records, the unchanged source hashes, final APK manifest and payload checks, raw phone reports and logs, and the collector regression. The initial negative resource test emitted shutdown warnings before test cleanup was fixed; `moon-runtime-final-red.log` is the clean final control. Earlier collector test-fixture setup failures are retained separately from the final intended RED/GREEN. The failed source-inventory attempts are described in `installed-preserved-inputs.json`. The final APK and generated caches remain in ignored working evidence rather than this archive.

Reproduce the loaded-resource check after reimport:

```sh
python3 scripts/configure_moon_paint_import.py
/Applications/Godot.app/Contents/MacOS/Godot --headless --editor --path godot --import
/Applications/Godot.app/Contents/MacOS/Godot --headless --path godot --script res://tests/test_moon_runtime_import.gd
python3 -m unittest discover -s scripts/tests
```

`evidence-manifest.json` pins archived bytes. Large source scenes, existing runtime scripts, painting bytes, palette, lighting maps and the protected open editors were not edited by this change.
