# Current PBR demo capture

Native Godot frames from the exact pack in `export/pbr-current-pack-checks.json`: 1,290 contiguous frames at fixed 30 FPS, 1410 × 600, seven original cue transitions, 43 seconds. This is a fixed-time capture, not sustained gameplay FPS.

Ten original frames and `contact.png` were inspected for route, repaired materials, reading/finale text and replay. Every source frame has a recorded SHA256 in `frame-sha256.json`. Audio is assembled from original cue PCM using runtime gains and loop rules; it is not native audio capture. Complete H.264/AAC decode passes.

`export/pbr-current-demo-release.json` records runtime, pack, movie and archive provenance. Eight runtime/import files must match between packed checks, capture, current source and the fresh profile. Four synthetic missing/stale/corrupted provenance cases reject before publication; their test preserves all seven preceding local release payloads.

Local pack/movie/README and both ZIP aliases are promoted only after validation. Prior payloads remain under ignored `build/previous-release/`. The final archive contains exactly five expected files, passes CRC and matches all four payload hashes. Full scene art, framing, continuous traversal, sustained performance and target-phone acceptance remain open.
