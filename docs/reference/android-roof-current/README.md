# Corrected-source Pixel evidence

Source `90c4f70e5b56fbe4c4e0ef2733057bbf962d21b0187601d7e2fcd6a857574df3`, APK `faf380061c0a35d8b9f003091a76246887e51709c5ad69f1af8e8f4a2f7e764a`, actual Pixel 7 Pro/API 36/Mali-G710. Production normal textures remain 2048²; no experimental normal cap is applied.

`route/` retains the actual cell→gate→pavilion physics route, fixed-clock arrival images and loaded texture inventory. Output is native 1080 × 2340, logical UI 411.43 × 891.43, scale 2.625; action controls are 126 physical pixels tall. Roof tile detail is visible in the current native pavilion image.

`touches/{cast,recast,close,finale,replay}` retains real input states and images. Ten pressed/released edges activate the complete sequence, ending in `terminal_room` with initial actions and no reading overlay. Reading/recast/close allocation is 75,809,960 bytes. Finale/replay peaks at 77,907,112 bytes (74.3 MiB); the 64 MiB diagnostic and decimal 64 MB spec targets fail.

The route peak is 74,761,384 bytes. Draw counts, primitives, four practicals and floor tolerance pass for the sampled route. Pavilion frame median is 29.847 ms and p95 31.968 ms; the unchanged 60-FPS engine cap does not establish sustained 60 FPS. This debug run is not release, 2020 Adreno, all-garden traversal, final art or authenticated reading acceptance.

Each collection verifies exact source/APK/script records and immutable payload hashes. The larger normal/reading/finale memory peaks and slow samples are retained. See `../../android-device-profile.md`, `../../android-normal-candidate.md` and `../../../export/android-roof-current-build.json`.
