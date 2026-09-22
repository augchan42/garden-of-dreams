# Garden completion implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the garden's site requirements and a working command-driven entry route, then connect its room interactions and verify rendering and performance.
**Architecture:** Keep Blender site libraries and GLB exports as scene assets. Godot owns movement, camera rails, command UI and room state; data adapters own external divination, news and presence. A playable route is the first milestone, not completion of the whole goal.
**Tech Stack:** Blender 5.2, Godot 4.7.2 Standard, GDScript, glTF 2.0.
**Spec:** docs/garden-scene-spec.md; docs/sites/*.md; original design at ../8bitoracle-next/docs/ideas/garden-of-dreams.md.

## Global constraints

- Metres, source Z-up, glTF Y-up. No rigged character required.
- 2.35:1 camera framing; fixed rails rather than free look.
- Click/tap commands with optional typed commands. AI-driven decisions require an actual service integration; do not misrepresent local authored responses as AI output.
- Green/amber/black rendered palette; retain visible architectural detail.
- 300k visible triangles and 150 draw-call targets require measured engine evidence, not mesh-count inference.
- Keep game logic out of Blender assets. Room markers retain room_id.

## Task 1: Command-driven entry route
Files: godot/runtime/entry_route.gd, godot/runtime/entry_route.tscn, godot/tests/test_entry_route.gd, godot/project.godot.
Interfaces: room_id, execute_command(text), transition_finished(room_id), player CharacterBody3D, camera Camera3D. UI buttons and typed input share one dispatcher.
- [x] Test missing route scene and initial terminal_room state.
- [x] Add room descriptions, contextual actions, optional command input and a status line.
- [x] Add collision-aware movement between the cell, gate and pavilion; stop rather than teleport on obstruction.
- [x] Animate fixed cameras during travel; frame the pavilion at arrival.
- [x] Test both directions using actual physics, command rejection during travel, unsupported commands, and no falling through floors.
- [ ] Inspect the running scene visually at each location and at mobile window sizes.

## Task 2: Site contracts and art completion
Files: docs/sites/*.md, Blender site libraries, source scripts and GLB exports.
- [x] Expand the 11 short site sheets to specific asset, lighting, camera and trigger contracts.
- [ ] Collect three references per site with source attribution.
- [ ] Complete missing kit variants and distinctive later-site architecture.
- [ ] Replace temporary typeset signage with painted decals; refine foliage and pierced rockery.
- [x] Fix the tunnel reveal geometry/camera relationship and export both hexagram variants.
- [ ] Render and inspect every site against its contract.

## Task 3: Godot rendering
Files: godot/garden_import.gd, materials and shaders, export/lightmaps, grade/tech-noir.cube.
- [ ] Bake lighting with matching secondary UVs and verify PNG maps in engine.
- [x] Add animated water and scrolling floor fog; verify separate fixed-clock render differences.
- [x] Apply and verify the consistent in-engine grade (rendered color grid versus source cube; UI unchanged).
- [ ] Complete atlases and final texture-memory audit.
- [x] Limit realtime practicals to four nearby lamps; verify selection in runtime tests.
- [ ] Verify that reimport retains lighting, material, collision and camera behavior.

## Task 4: Room interactions and data
Files: Godot runtime room controllers, content resources and service adapters.
- [x] Inspect the public topic schema and deployed origin; connect read-only topics.
- [ ] Finish reading/history authentication and write-contract audit before connecting actual readings.
- [ ] Personal terminal/history, pavilion feed, bulletin board and room transitions.
- [ ] Distinguish offline/local content from live data; handle service unavailability.
- [ ] Integrate AI movement decisions through validated room connections and state changes.
- [ ] Add social/news/group functionality only against verified available services; document unresolved dependencies.

## Task 5: Acceptance
- [ ] Automated traversal of collision routes and command/state behavior.
- [ ] Visual check of all rooms, UI and camera transitions.
- [x] Measure desktop arrival-view draw calls, frame intervals and memory; record failed budgets.
- [ ] Meet rendering budgets and complete target-device/mobile and traversal profiling.
- [ ] Update build-status with evidence, preserving any unresolved requirements.
- [ ] Complete the goal only after all accepted requirements are verified.
