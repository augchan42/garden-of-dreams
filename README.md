# Garden of Dreams — 大觀園

Blender scene assets for Godot. First modelled art pass, built from `docs/garden-scene-spec.md`.

Open `blender/master.blend` for the linked garden assembly. Edit individual files in `blender/sites/`, then reload libraries in the master. `blender/authoring.blend` is the consolidated editable source used by the generation scripts; edits to site files do not automatically propagate back to this snapshot.

Open `godot/project.godot`. The default scene is the focused first-reading demo: cell → rockery gate → Qinfang Pavilion → local reading → replay. See `docs/demo-run-guide.md` for the build and controls. The broader command-driven exploration remains at `runtime/entry_route.tscn`: click actions or type `look`, `terminal`, `exit`, `enter`, `west`, `island`, `board`, `hill`, `overlook`, `study`, `read`, `rocks`, `north`, `doors`, `topics`, and `back`. It traverses all 14 site approaches using collision physics and fixed cameras. `garden_preview.tscn` remains the static establishing view. Outside demo mode, Qinfang’s Current topics panel reads live public topics from 8-Bit Oracle; the hilltop’s Current Events panel filters that feed to temporal topics, and Hengwu’s Ongoing Topics panel shows timeless topics. Private history, AI interpretation and live reading creation are not connected yet.

Import `export/garden-of-dreams.glb` into Godot, or use individual files in `export/sites/`. The assembly includes 14 garden sites and a shared stage. Nine starter kits have Blender files, GLB files and reduced-detail `_LOD1.glb` exports.

The complete export has 239,426 render triangles and 128 render meshes before Godot import. This is a geometry count, not a measured draw-call or frame-rate result. Room markers carry `room_id` in glTF extras. Exported collision objects use Godot’s `-colonly` naming convention. Source units are metres; GLB export is Y-up, with modifiers applied, custom properties included and Draco disabled.

Graded reference stills and Godot captures are in `docs/reference/`; `-raw.png` files are the ungraded originals. `grade/tech-noir.cube` is the exact LUT applied by `scripts/grade_references.py`.

See `docs/build-status.md` for remaining full-garden work and `docs/godot-import.md` for import notes. All 14 locations are visitable. The focused demo has fresh bakes for its three spaces; older full-garden lightmaps remain stale and are excluded by the source-hash guard.

Rebuild order inside Blender: `scripts/build_garden.py`, `scripts/complete_garden.py`, `scripts/finish_assets.py`. The scripts use the current repository path. Run `scripts/refine_western_sites.py` against the authoring file to replace the western placeholders, followed by `scripts/refine_bulletin_hall.py` to complete the study furniture and approach, and `scripts/refine_hilltop_hall.py` for the hill terrace and connected stairs. `scripts/refine_study_courtyard.py` completes the Hengwu court, perforated rocks and approach. `scripts/refine_imperial_facade.py` replaces Daguan’s placeholder with the closed two-tier hall. Then run `scripts/export_garden.py`, `scripts/package_libraries.py`, `scripts/kit_lods.py`, and `scripts/render_references.py` against the authoring file in separate Blender processes, passing `--python-exit-code 1` so script errors fail the command. Grade and validate using Python: `scripts/grade_references.py`, `scripts/verify_assets.py`. Rebuilding creates new data; use a fresh Blender process rather than running the full build repeatedly in an existing project.

The focused first-reading showcase is tracked in `docs/demo-milestones.md`.
