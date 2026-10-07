# Portrait pavilion camera evidence

Seven native camera counterfactuals use the current source `90c4f70e…` and repaired PBR renderer before changing the route. The old overview projects only four of eight moon bounds inside the clear scene; the selected south-six-narrow pose projects all eight. Original images and their native JSON hashes are retained under `counterfactuals/`. The initial probe exited cleanly in tool session 65180; it did not archive stdout. The regression failed on the actual clipped moon in session 34879 before the source correction.

Current source checks and logs cover complete moon bounds, overview resize, preserved room text, table-detail resize, matching portrait reveal endpoint, desktop reveal physics, cell/gate/pavilion physics and actual portrait pointer/keyboard cast/finale/replay. Fourteen normal portrait arrivals, six demo states and eight walking reveal images were captured with current native Godot. Fixed shader time is 3 seconds in the images; reveal camera motion and physics use real elapsed time.

All twenty-seven other desktop/portrait arrival projections match the preceding native measurements exactly; only Qinfang portrait changes. The final pavilion and table images and reveal lift/end frames were directly reviewed. A thin top-edge exposure remains in the final view and the lift exposes more of the enclosure edge; the physical backdrop/moon artwork still needs work. This is camera progress, not final art, continuous all-garden traversal, sustained frame rate or phone acceptance.

Production Blender, source GLB, lights, materials and bakes remain unchanged. Runtime camera source hash and clean phase logs are recorded in `../../../export/pavilion-framing-runtime-checks.json`.

Separate stationary native allocation/draw sampling in one fresh process measures normal then demo at 390 × 844: both have 47 draws, 85,830 primitives and four practical lights. Texture counters are 36,147,703 and 30,336,367 bytes respectively. The counters include render buffers and do not isolate a 3D atlas or establish phone performance. Source/hash-bound records are in `../../../export/pavilion-portrait-budgets.json`.
