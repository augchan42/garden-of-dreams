# Corrected-source native demo capture

The captured pack SHA-256 is `d7f598302e6e4c7e5b7b2dac18c0a27a33de5bf21aa789cde34aba0487cc0c5a`, using canonical source `90c4f70e5b56fbe4c4e0ef2733057bbf962d21b0187601d7e2fcd6a857574df3`. Nine prior packed material, lighting, startup and native input checks are in `export/roof-current-pack-checks.json`.

Godot captured 1,290 contiguous native 1410 × 600 frames at fixed 30 FPS. The sequence covers cell, gate, tunnel, garden reveal, table, local reading, finale and replay. `frame-sha256.json` records every native frame; ten representative original PNGs and `contact.png` are retained here. The original frame directory remains in the capture job's system temporary location and is not a durable release requirement.

The movie contains H.264 video and AAC audio, verified at 30 FPS and 43 seconds by ffprobe and a complete error-free ffmpeg decode. Audio is assembled from the six original PCM cues at the seven logged runtime transitions using runtime gains and stop/loop rules; it is not native audio capture. PCM duration, nonzero peak and absence of clipping were checked. ffmpeg's requested AAC bitrate was clamped to its supported maximum; the resulting stream decodes successfully.

`capture.log` and `assembly.log` retain exact native outputs. The movie is `build/GardenOfDreamsDemo.mp4`; the local `GardenOfDreamsDemo.zip` and `GardenOfDreamsDemo-macOS.zip` aliases contain exactly the pack, movie, run guide, launcher and checksum list. CRCs and all four payload hashes verify, and both archives are byte-identical. The previous release is preserved under ignored `build/previous-release/`.

`scripts/finalize_demo_capture.py` rechecks pack/source/log provenance, contiguous frames, cue transitions, PCM and complete movie decoding before promotion. An intentionally incorrect captured pack hash was rejected before promotion. `export/roof-current-demo-release.json` and `docs/reference/demo-capture-timeline.json` record final evidence and hashes.

The sampled roof and garden reveal were inspected: the upper roof has tile detail; the slate-blue mountain backdrop and local amber light remain visible. This is a progress checkpoint, not final art or performance acceptance. Moon shape/framing, portrait enclosure edges, complete room art, continuous traversal and phone budgets remain open.
