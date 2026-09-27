# First-reading demo milestones

**Audience experience:** A new visitor starts at a green CRT, walks through the lantern-lit rockery, sees the pavilion reveal, and receives a local hexagram at the bronze table in about four minutes. The demo is a focused desktop build. It does not claim live AI interpretation or private account history.

The full garden completion plan remains in `docs/superpowers/plans/2026-09-23-garden-completion.md`. These milestones are a shorter showcase path, not a replacement for that plan.

## Milestone 1 — the reading works

- [x] Add a reproducible Godot catalog of the 64 hexagrams from the sister application's canonical number, Chinese name, meaning, and bottom-to-top pattern data.
- [x] Cast six lines locally with the traditional three-coin 6/7/8/9 outcomes; identify primary and transformed hexagrams and moving lines.
- [x] Change the six bronze meshes and show a readable result card at Qinfang. Identify the reading as local, allow closing and recasting, and keep the current table state after closing.
- [x] Verify all 64 pattern mappings, cast invariants, command flow, and desktop/portrait legibility.

**Exit verified:** Starting in Qinfang, a visitor can cast, see a matching physical and textual result, close it, and cast again without a service or account. The original cell → gate → pavilion route still passes.

## Milestone 2 — the four-minute route

- [x] Give the terminal a clear invitation to enter the garden and lead visitors through cell → gate → pavilion → table.
- [x] Keep the demo's primary action list short while leaving the wider garden available outside demo mode.
- [x] Add a deliberate final beat and replay path after the reading.
- [x] Test a novice path through the route without typed-command knowledge.

**Exit verified:** `first_reading_demo.tscn` is the default scene. `test_first_reading_demo.gd` drives every step through buttons, including the finale and replay. `entry_route.tscn` retains full exploration. Desktop and portrait captures are in `docs/reference/demo-*`.

## Milestone 3 — one finished visual and sound pass

- [x] Finish the cell, tunnel, reveal, and pavilion lighting as one sequence; bake static lighting and retain readable shadows and bronze lines.
- [x] Add original or licensed CRT, lantern, water, tunnel, and reveal sounds at restrained levels.
- [x] Check camera framing, typography, texture treatment, and transition timing at desktop and portrait sizes.
- [x] Reprofile these three spaces and resolve the demo's draw-call and texture budget issues.

**Exit verified:** Fresh Cycles lightmaps cover 32/32 opaque demo meshes (the transparent inscription keeps its source material). Desktop and portrait captures show the cell, gate, pavilion, table, reading, and finale; the captured traversal includes the tunnel and reveal. Six original procedural cues run at −22 to −30 dB. On the Apple M2 Max desktop at 1410 × 600, forced-draw samples show 83–121 visible draw calls, 123,744–161,486 visible primitives, and 63,957,192 bytes of texture allocation. These are stationary desktop measurements, not a phone result.

## Milestone 4 — demo acceptance and handoff

- [x] Run an uninterrupted start-to-result-to-replay test, including keyboard and pointer input, service-offline operation, fresh import, and one cold launch.
- [x] Check target hardware, frame pacing, and memory; record any platform limitation explicitly.
- [x] Package a build and short capture with a one-page run guide and exact asset provenance.

**Exit verified:** `test_demo_input_acceptance.gd` sends mouse and Enter-key events through the entire route, both from the project and from the exported pack. The demo runs without the reading service; a fresh `.godot` cache import and a cold desktop launch of `GardenOfDreamsDemo.pck` passed. The local `build/GardenOfDreamsDemo-macOS.zip` contains the pack, launcher, checksums, run guide, and 43-second capture. `docs/demo-run-guide.md` records the Apple M2 Max profile and the untested phone/other-desktop limitation. Archive integrity and checksums passed.
