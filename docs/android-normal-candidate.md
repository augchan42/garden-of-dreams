# Android normal-map experiment

This is an isolated debug experiment at the preceding `b4b322c2` scene. The production pavilion/wall normal maps and their import settings remain at 2048². The corrected `90c4f70e` scene needs separate phone and release verification.

Two actual Pixel 7 Pro runs use the same source, lighting, runtime scripts, DPI, native 1080 × 2340 output, 2.625 UI scale and 60-FPS cap. The candidate changes only the isolated project's pavilion and wall normal import size limits to 1024. Original PNG hashes match. Actual loaded textures are 1024² with mipmaps; all 88 texture resource paths and bindings are retained. The renderer reports exactly 8,388,608 fewer texture bytes in every sampled route and touch state.

| State | Original MiB | Candidate MiB |
| --- | ---: | ---: |
| Cell | 69.79 | 61.79 |
| Pavilion / route peak | 71.30 | 63.30 |
| Reading / recast / close | 72.30 | 64.30 |
| Finale / replay | 74.30 | 66.30 |

The complete candidate demo peaks at **69,518,504 bytes**. It fails the existing diagnostic 64 MiB gate and the spec's decimal 64 MB target. A route-only pass would omit allocations created by reading and finale controls. Real ADB taps exercise cast, recast, close, finish and replay; each run records ten press/release edges and returns to the initial cell controls. This experiment does not justify installing a production normal cap or reducing further texture detail to claim acceptance.

These later phone runs also contain slow frame samples: the highest per-state median is 29.862 ms before and 29.867 ms after, with p95 reaching 31.782 and 32.322 ms. The 60-FPS engine cap is unchanged; sustained 60 FPS is unproven and no timing improvement is claimed. The cause of this variation has not been isolated.

The three phone arrival images freeze water/fog clocks only after real frame sampling, then restore them and settle before the next timed movement. Camera transforms, native image dimensions and capture clock match between runs. Full-image RGB RMSE is 0.000163–0.000196. Eight native Mac captures inspect the actual placed Qinfang/Hengwu normal bindings at arrivals and closer views in desktop/portrait windows. Their maximum full-image RMSE is 0.000229. These small full-frame differences do not prove preservation of every normal-map feature. The Hengwu images are identical under the captured lighting, so they supply no positive evidence of visible normal detail. Roof darkness in these old-source images and portrait moon/enclosure framing remain separate art issues.

Earlier allocation inventories also found matching calculated stored-format bytes for the 88 loaded scene textures on Mac and Pixel: 36,505,432 bytes. Compressed normal/color formats differ by platform. Pixel OpenGL readback expands compressed textures to RGBA8, returning 191,012,856 CPU image bytes; that is **not** its GPU texture allocation. The Mac renderer total is 49,719,899 bytes and Pixel's is 74,761,384. The 25,041,485-byte difference cannot be assigned entirely to screen buffers from this partial inventory. Renderer padding, UI/fallback fonts, render targets and other allocations need separate evidence. Reachable theme-font CPU atlas images total 393,216 bytes on both devices and exclude implicit fallback fonts and GPU overhead.

The viewport texture metadata getter reports 2835 × 6142 on Pixel after UI scaling and returns `FORMAT_MAX`, while actual native PNGs are 1080 × 2340. Use native images as output-resolution evidence; these getter values do not establish a larger render target or its byte cost.

Evidence: [native collections and Mac captures](reference/android-normal-candidate-b4/), [verified comparison](../export/android-normal-candidate-comparison.json), and the allocation collections under `reference/android-profile-b4/`. Each native collection retains source/APK/script hashes, its measured failed budgets and immutable file hashes. The verifier checks saved evidence rather than requiring temporary APK fixtures to survive.

```sh
python3 scripts/build_android_profile.py --report export/android-normal-baseline-build.json --apk build/garden-normal-baseline.apk
python3 scripts/build_android_profile.py --normal-atlas-size-limit 1024 --report export/android-normal-candidate-build.json --apk build/garden-normal-candidate.apk
# Install and start each diagnostic APK on the awake phone, then collect its ready state.
python3 scripts/collect_android_profile.py --device SERIAL --build-report BUILD_REPORT --destination NEW_DIRECTORY
python3 scripts/tap_android_profile.py --device SERIAL --build-report BUILD_REPORT --destination NEW_TOUCH_DIRECTORY
python3 scripts/verify_android_normal_candidate.py
```

Do not run the tap sequence against a production package. It requires an untouched completed diagnostic run and verifies the fixture's build record before touching controls. No internet permission, remote readings, device-wide logs or global phone settings are used.
