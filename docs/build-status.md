# Build status — 2026-09-23

The working garden and standalone kits are saved and exported. Final art, device performance, release and service integration requirements remain open.

## Delivered

- Linked master, consolidated authoring scene, 14 site files and shared stage file.
- Six terminal cells with desks, chairs, barred windows, green CRTs and entry corridor.
- Bent plaster tunnel, two amber lanterns, collision floor and walls, entry/reveal markers.
- Qinfang hexagonal bridge pavilion, 14 m bridge deck, 16 corridor bays, table and six hexagram slots, stools, lanterns, water, lotus pads and bamboo.
- Priority-2 study facade with twelve amber CRTs, hilltop hall with terrace steps, imperial facade.
- Eight additional site facades/dressing groups positioned according to the site map.
- Curved cyclorama, raster brush texture, mountain flats, painted moon, fog cards, hard green and amber lights.
- Nine starter kit libraries and reduced-detail GLB variants. These are representative pieces, not every variant in section 6 of the spec.
- Separate collision meshes, room-marker extras, site cameras, straight camera rail guides.
- Secondary UV maps on batched static export meshes; PNG fog and backdrop textures; 32³ tech-noir LUT.
- Godot preview project in `godot/`, with a saved scene, calibrated lighting and a five-location command-driven exploration route.
- Five rendered views, visually checked. 34 GLB files checked for binary structure, room metadata and absence of Draco. Linked master reopened successfully with 15 site collections and 5,831 objects.

## Remaining before production acceptance

- Collision traversal, camera transitions and device profiling. Godot 4.7.2 Standard was installed into `/Applications/Godot.app` during the build. Import and a headless preview startup passed: 145 meshes, 102 collision shapes, 39 room markers, 17 cameras. The full environment has 251,410 render triangles and 145 render meshes; actual passes, lights, transparency and draw calls need profiling.
- Cycles lightmap baking and PNG lightmaps. UV2 is prepared on batched static meshes only. Current references use dynamic Blender lighting; the four-realtime-light budget is not enforced.
- Material atlases, texture memory audit and remaining normal maps. Water and fog animate in Godot; reflection quality still needs a final art pass. Most materials currently use simple shared Principled colors. The backdrop texture is 4096²; other per-kit atlases are not built.
- Complete kit variants: corners, T-junctions, stair bays, moon/vase gates, four lattice styles, actual pierced Taihu rocks, willow/banana/plum variants, benches, brazier and incense burner.
- Replace Songti glyph geometry with hand-painted calligraphy decals. The existing signage is layout geometry, not finished calligraphy.
- More distinct architecture for the later sites. Their present facades reuse the same hall form. Ouxiang and Ziling now have their dedicated pavilion/island forms; the other later sites still need individual art passes.
- Refine the scripted tunnel reveal: present camera sees down the south corridor rather than the specified unobstructed full-width pavilion reveal. Camera rails are guides, not animated tracks.
- Broken hexagram variants exist hidden in the authoring scene, but only solid slots are in the assembly GLB. Export variant assets before connecting game-driven hexagrams.
- Add the three reference stills per site and finish the look review. The newly written site sheets record directions, not sourced film stills.

## Blender recovery

Blender 5.2.2 crashed in `BKE_view_layer_copy_data` when writing a newly created scene through `bpy.data.libraries.write`. Saving collections first, then creating normal `.blend` files with `save_as_mainfile`, completed successfully. The original Signal Room file was not overwritten. The build continued from the saved garden assembly through the installed Blender executable after the MCP connection closed.

## Active completion work

The user approved proceeding with the remaining work. The accepted plan is `docs/superpowers/plans/2026-09-23-garden-completion.md`. A separate command-driven entry scene is under test; the static preview remains available. The original design explicitly prefers clickable actions and optional typed commands, so travel uses authored routes and fixed camera movement rather than free-look controls. Local authored descriptions are labelled as local exploration; no live AI or feed connection is claimed.

### Entry route evidence

- `godot/tests/test_entry_route.gd` passed twice, including after the camera/UI fixes. It exercises the real imported collision meshes, both route directions, unsupported commands, and the busy state.
- `docs/reference/route-cell.png`, `route-gate.png`, and `route-pavilion.png` were rendered in Godot and inspected. `route-mobile-cell.png` verifies the terminal controls at 390 × 844. The gate camera was then pulled back to avoid cropping the entrance sign; the adjusted gate view still needs another render.
- The project main scene now starts `runtime/entry_route.tscn`. External reading/history/feed actions explicitly report that those services are not connected.
- All 14 site sheets have navigation links in `docs/sites/README.md`; the later eleven now contain detailed contracts rather than short outlines.
- Remaining work still includes site art, reference collection, renderer/material completion, external integration and performance acceptance. The overall goal is not complete.

### Western sites and route evidence

- Replaced Ouxiang’s generic hall with an open water pavilion, tea table, six seats and two lanterns. Replaced Ziling’s hall with a low reed island and timber footbridge. Updated three linked libraries (including the shared stage), authoring scene, assembly export and individual site GLBs.
- The current export is 219,100 triangles and 137 render meshes. Godot import/rebuild passed with 137 meshes, 116 collision shapes, 44 room markers and 19 cameras. Earlier counts above describe the preceding build.
- `godot/tests/test_western_route.gd` passed: Qinfang → Ouxiang → Ziling → Ouxiang → Qinfang through actual collision geometry, with floor support.
- Desktop engine views `route-ouxiang.png`, `route-ziling.png` and the adjusted `route-gate.png` were inspected. The gate sign fits in frame; its missing glyph remains part of the unfinished signage pass. Later-site facades, water, light baking and palette refinement remain unfinished.
- The live Blender master reloaded the three changed libraries through MCP and reports 5,700 objects. Its viewport was inspected after reload.

- The original entry route passed again after the western asset import. All 34 GLBs passed the structural/metadata check. Mobile arrival views and controls were rendered at 390 × 844; portrait establishing views now pull back for the open sites. These desktop viewport checks do not establish phone GPU performance.

### Bulletin hall evidence

- Added three desks/keyboards, two hanging scroll layouts and closed side doors to Qiushuang. Moved structural posts away from screen centres; added a continuous stone approach, wall/desk/post colliders, five room markers and four cameras.
- Re-export/import passed: 220,792 triangles, 137 render meshes; Godot reports 126 collision shapes, 48 room markers and 22 cameras. All 34 GLBs passed the structural/metadata validator.
- `test_study_route.gd` first failed for the missing room, then passed the Qinfang → study → Qinfang physics route and all three monitor-bank actions. Their messages explicitly state live content is not connected.
- `render_study.gd` captures the arrival and three bank views for desktop and 390 × 844. The temporary inscription still has a missing glyph; painted signage and final lighting remain open requirements.
- Live Blender master reloaded the study/stage libraries through MCP; 5,850 objects were present and the viewport was checked.

### Engine surface animation evidence

- `garden_import.gd` now assigns shared water/fog ShaderMaterials by source material name. A forced clean GLB reimport passed `test_surface_materials.gd`: one water surface and three fog material batches retain their shader overrides.
- Water uses a generated seamless 256² normal map sampled in two moving directions, green tint and specular highlights. Floor fog scrolls two alpha-mask samples with fixed edge falloff; depth writing is disabled to preserve scene visibility.
- The Compatibility renderer compiled both shaders and saved `surfaces-baseline.png`, `surfaces-water.png`, and `surfaces-fog.png`. The clock is fixed for these comparisons: only one effect's phase changes at a time. Water changes 2.20% of pixels; fog changes 26.40% above a two-channel-value threshold. `scripts/verify_surface_animation.py` records the measurements in `godot/surface-validation.json`.
- These checks prove visible material animation in the desktop renderer. They do not prove reflection quality, phone performance, lightmap baking, the full-screen grade, or the four-practical-light limit. Those remain unfinished.

### In-engine grade evidence

- Added the source `grade/tech-noir.cube` as a 1024 × 32 slice atlas, using bilinear red/green sampling and linear interpolation between blue slices. `scripts/make_grade_atlas.py` regenerates it from the authoritative cube.
- The saved preview includes the screen-reading grade on CanvasLayer 1. The command UI uses layer 2 and the grade ignores mouse input.
- `render_grade.gd` first failed for the missing scene, then rendered a color grid through the Compatibility renderer. `verify_engine_grade.py` compared 261,888 pixels against CPU interpolation: max channel error 1.457/255, mean 0.330/255. The opaque UI test marker remained identical. Atlas/output 8-bit quantization accounts for the small error.
- All six desktop room views were rerendered and inspected with the grade. The grade is visibly green-dominant and darkens unlit furniture; final lighting/painted signage still need refinement. Mobile performance is not established by this shader check.

### Performance baseline and practical-light budget

- Added an actual-renderer benchmark for six arrival views. See `docs/rendering-profile.md` and `godot/profile-desktop.json`. On this Mac, median intervals are 3.36–5.72 ms, but the draw-call counter remains 434–957 against the 150 target. Texture memory is about 24 MiB. No mobile claim is made.
- A temporary no-shadow diagnostic reduces the draw-call counter to 43–136, identifying static shadow baking as the next optimization. Production shadow settings remain intact.
- Added `runtime/practical_lights.gd`: nearest four eligible lantern/CRT lights within 12 m, no practical shadows, updated as the visitor moves. The test first failed for the missing manager, then passed at five locations. The measured room views have zero to four active practicals. This does not replace the still-required static light baking.
- Arrival-render and benchmark scripts now position the visitor at each room when sampling, so light selection matches actual arrival positions.

### First Cycles lightmap prototype

- Found and fixed missing UV2 on hero meshes in the exporter. The assembly verifier now requires a second UV channel on every render node. All 34 GLBs still pass structural checks.
- Added `scripts/bake_lightmaps.py`, producing a Cycles diffuse direct/indirect PNG from the actual exported Qinfang stone batch (1024², 32 samples). Point practical lights are excluded from the bake. The metadata records source/UV hashes and intensity scale; `verify_lightmaps.py` checks freshness and nonempty contents.
- Imported the updated GLB and prototype PNG into Godot. `render_lightmap.gd` produced dynamic/baked comparisons; roof/post shadow patterns remain visible on the baked corridor, with a darker overall level. Only the test instance receives the experimental baked material; production keys remain dynamic.
- See `docs/lightmap-pipeline.md`. All-site coverage, final lighting setup, atlas/texel-density work, material integration and post-bake profiling remain unfinished.

### Pavilion bake coverage and tunnel UV repair

- Baked and rendered all 15 opaque Qinfang meshes using the experimental adapter. Original material colors and emission were preserved. Corrected Godot's normalized hero-name mapping; the test then applied all 15 maps.
- `verify_uv2.py` detected tunnel UV2 overlap. The exporter now triangulates the tunnel before projection; the subsequent 512² interior-overlap check passes all 137 render meshes. Padding/subtexel quality still needs review.
- This export revision invalidates the previous lightmap hashes. The initial whole-garden batch was explicitly terminated; a replacement full bake is running against the repaired source. Production uses the repaired GLB with dynamic lighting, not unverified lightmaps.
- The remaining bake work still includes the specified backdrop wash, final texel density/packing, all-site visual acceptance, complete material integration and performance verification. Passing UV samples or generating PNGs does not complete those requirements.

### Live public topics

- Verified the existing public topics endpoint from the application's canonical origin. Added Qinfang's `Current topics` browser, with live labels, topic selection, scrollable descriptions, refresh, timeout/error handling, and modal control restoration.
- Schema tests passed. The native Godot client loaded six real public topics and passed desktop/390 × 844 layout checks. A phone title overflow was found visually and fixed before acceptance. No readings were created and no server data was changed.
- The full bake is still running against the repaired GLB. `render_baked_garden.gd` now rejects incomplete coverage before rendering its all-site comparison; it correctly failed against the old Qinfang-only index.

### Full bake completed; production adoption pending

- Fresh-source coverage and engine application pass for all 133 opaque meshes. Fifteen authored camera views were rendered; their contact sheet was inspected, with full-resolution pavilion and terminal checks. The terminal exterior is too dark; remaining art and final lighting acceptance are still open.
- Added `--baked` to the actual-renderer benchmark. Six playable arrival views use 43–136 visible draw calls with the nearest-four practical manager. Median desktop frame intervals are 1.63–2.61 ms.
- Texture memory is 433,752,166 bytes (about 414 MiB), exceeding the 64 MiB target. This prevents adopting the current bake as the finished rendering setup. Production lighting remains dynamic. See `godot/profile-desktop-baked.json` and `docs/lightmap-pipeline.md`.

### Lightmap memory reduction

- Preserved original Cycles PNGs and added reproducible Godot runtime import settings. GPU compression alone measures 89.08 MiB; compression with a 512-pixel cap measures 41.58 MiB for the experimental baked scene, below the 64 MiB texture target on this Mac. Draw calls remain 43–136 across six arrival views.
- Captured 15 fixed-time views for uncompressed, compressed full-resolution and compressed 512-pixel variants. The 512 variant's largest per-view mean channel difference is 0.347/255. Contact-sheet and pavilion inspection retain the overall look; this does not establish route/motion or phone quality.
- Source-bake coverage still passes for all 133 opaque meshes. Production adoption remains pending lighting refinement and route/mobile verification; the smaller import settings apply only to the experimental adapter's lightmaps.

### Baked playable-route checks

- Rendered all six actual arrival cameras at desktop and 390 × 844 portrait sizes. The terminal's CRT and window remain readable against intentionally black walls; its dark exterior overview does not establish a lighting defect. The required backdrop wash is still missing.
- Completed ten physics traversal legs covering both directions of the current routes. `godot/baked-traversal-validation.json` records destination, floor-support and practical-light-budget checks. Saved 30 sample frames; reviewed the first 27 in a contact sheet and the final cell approach at full resolution. Continuous-motion aliasing and phone hardware acceptance remain open.
- Kept production lighting unchanged pending the specified lighting rig and final site art. Next site work is the priority-2 hilltop hall: parapet, topic table, action markers and traversable approach, as required by `docs/sites/tubi-tang.md`.

### Hilltop hall and seventh playable location

- Added a four-metre terrace, twenty visible stair treads, low parapets, a stone topic table, one amber lantern, five action markers and three site cameras. A separate simplified stair ramp and guard colliders support the climb. The closed hall remains a facade.
- Connected the hilltop from the bulletin hall. The physics test found a desk obstruction and a lip at the upper landing; both were fixed in source geometry. Final `test_hilltop_route.gd` passes climbing, the overlook action and return descent. `test_study_route.gd` passes the shared approach.
- Added temporal-topic filtering to the existing public-topic browser. Unit checks cover current events, empty results, retained data on errors and the unfiltered pavilion view. Desktop and portrait renders each loaded one live current-event topic; no readings or server writes were created.
- Inspected desktop arrival/overlook/table and portrait arrival/event-browser renders. Final art requirements still include painted signage, sourced stills and the specified backdrop lighting rig.
- All 34 GLBs pass structure/metadata checks. The new assembly has 221,616 triangles and 121 render meshes; Godot imports 127 collision shapes, 52 room markers and 24 cameras. The UV2 raster check passes. The linked Blender master was reloaded through MCP and contains 5,896 objects; the active hill collection has five markers and one point light.
- An attempted combined Blender build/export command exposed that Python errors can leave a zero shell exit status. Subsequent export uses `--python-exit-code 1`; its log and new source hash were checked before import.
- Current source SHA256: `f4220ffb7ae9e578cd1db181d4c34e9bc0412dc568c9e6c0bf4a0fb79b39027c`. Previous lightmaps are stale and remain excluded by the source-hash guard. The earlier baked performance measurements describe the previous geometry revision, not this expanded scene.

### Hengwu court and eighth playable location

- Built an enclosed 9 × 8 m stone court with crossed-lattice openings, low herb beds, study table, four stools, one amber lantern and four room markers. Replaced the solid rock dressing with three perforated plaster stones; nine hole-centre BVH rays pass through the geometry. Godot rock close-ups visibly show the openings. This does not complete the full six-variant rockery kit.
- Connected Qinfang to the court around the end of the western covered walk, avoiding its railing. `test_courtyard_route.gd` first detected the missing room, then passed outward/return traversal, floor support and local inspection actions. `test_western_route.gd` still passes the pavilion/island routes.
- Added a timeless-topic filter for Hengwu’s Ongoing Topics panel. Unit tests passed; desktop and portrait renders loaded five live ongoing topics. Shared study sessions and reading creation remain explicitly unconnected.
- Inspected desktop court/rock captures and portrait court/book/rock/topic captures. The initial portrait composition cropped out key court features; preserving horizontal framing improved it. Painted signage, sourced stills, atlases and final lighting remain unfinished.
- All 34 GLBs pass structural checks; the UV2 raster check reports no sampled overlaps across 122 meshes. Current export: 224,242 triangles, 122 render meshes. Godot imports 146 collision shapes, 55 room markers and 26 cameras. Linked Blender master was reloaded and inspected through MCP: 6,124 objects; active courtyard has three perforated rocks and four markers.
- Current assembly SHA256: `059338147d34fd837bacaee64398fbd76b99a897cea3c4a794010ae3f95bdf54`. Earlier baked-lighting measurements remain evidence for the previous source revision only; fresh final bakes and target-device acceptance are still required.

### Imperial facade and ninth visitable location

- Replaced Daguan’s two-pavilion placeholder with a single broad facade: two continuous roof tiers, five paired closed-door bays, central steps, two amber transoms and black backstage returns. Added three approach/inspection/return markers and simplified front/side/column/step colliders. No interior was built.
- Connected the Qinfang north walk. `test_imperial_route.gd` first failed for the missing route, then passed both directions, floor support, a direct ray check against the closed front collider and rejection of entry.
- Desktop and portrait establishing/door views were rendered. The establishing camera was lowered after the first view hid the door fronts. The existing green side key was lowered beneath the eaves; the close door view still needs a final readability pass. Roof silhouette and navigation are verified, not final lighting acceptance.
- The new roof UV chart initially had 24 overlapping sampled texels. Triangulating before a 30-degree smart projection resolves the sampled overlap across all 121 render meshes. Final gutter/texel-density quality remains open.
- Current export: 239,358 triangles, 121 render meshes; all 34 GLBs pass structural checks. Godot imports 158 collision shapes, 57 markers and 27 cameras. Linked Blender master reloaded and inspected through MCP: 6,696 objects; the imperial collection has ten door leaves and three markers.
- Current source SHA256: `22c0814d9937cb010ff5d1c0bef0fe7b9569b9585c6e39bdb2650d94466a35db`. Earlier lightmaps remain stale and are excluded by the guard. Remaining later-site art includes the red court, bamboo court, nunnery, water-level reflection hall and farmhouse; kit completion, painted signage, sourced references, services and final rendering acceptance also remain.

### Imperial door readability

- Compared the imported key at energy 1.8 against stronger keys, relocated light, disabled shadows and several depth-bias settings in `godot/tests/diagnose_imperial_light.gd`. Removing shadows alone did not solve the dark doors; energy 20 revealed the panels and fittings. The original 0.03 shadow bias caused visible stripes on columns and doors.
- Calibrated only the imperial preview key to energy 20 and shadow bias 0.5. Shadows remain enabled. Desktop and 390 × 844 portrait arrival/door renders completed; desktop arrival and portrait door captures were inspected. Fittings are readable and column striping is reduced, while roof/handle shadows remain. Fine shadow edges and the missing inscription glyphs still need the final art/bake pass.
- Forced GLB reimport and rebuilt the preview successfully: 121 meshes, 158 collision shapes, 57 markers and 27 cameras. Geometry and its source hash are unchanged; existing lightmaps remain stale. These are Godot preview-unit adjustments, not a claim of matching the final Cycles lighting rig or target-phone performance.

### Yihong red courtyard and tenth visitable location

- Replaced the generic hall with a seven-metre west-facing lacquer front, paired closed doors, bronze pulls, stone threshold, low capped side walls and a small gate roof. One amber window replaces the previous multiple windows. Two banana plants have fourteen curved leaf meshes with raised midribs and pointed tips. Four markers and three cameras are exported.
- The native Blender inspection exposed unevaluated object transforms during the initial site rotation. Updating the view layer before transforming fixes cameras, lights and plant ribs. The corrected library was reloaded through MCP and its viewport inspected: 232 site objects; 6,589 objects in the master.
- Added Qinfang → Visit the red court, door/leaf inspections and return. `test_red_court_route.gd` first failed for the missing room, then passed both travel directions, floor support, closed-door collision and rejection of entry. The shared eastern approach still passes `test_study_route.gd`.
- Desktop and 390 × 844 arrival/door/leaf images were generated. Desktop arrival/foliage and all three portrait views were inspected. The foliage and amber-lit lacquer are readable; painted signage, foliage texture refinement, sourced references and final lighting remain unfinished. Portrait simulation does not establish phone GPU performance.
- All 34 GLBs pass structural checks; 121 render meshes pass the sampled UV2 overlap check. Current assembly has 236,214 triangles; Godot imports 166 collision shapes, 60 markers and 29 cameras. Current SHA256: `dee624c62089da0c580e0c557499468467cdff9c7549ce1607228a5abcc667cf`. Earlier lightmaps remain stale and excluded from production.

### Xiaoxiang bamboo court and eleventh visitable location

- Replaced the generic hall with a six-metre east-facing facade, closed timber gate, one amber window and one shallow pitched roof. Twelve jointed bamboo stalks use three heights (2.5, 3.5 and 4.5 m), arranged in four clumps around a 1.8 m stone aisle. Added four markers, three cameras and blocking front/return/plant-bed colliders.
- Added Qinfang → Visit the bamboo court, gate and bamboo inspections, and return. `test_bamboo_route.gd` first failed for the missing room, then passed both travel directions, floor support, gate collision and rejection of entry.
- Desktop and 390 × 844 arrival/gate/foliage captures completed. Desktop arrival and portrait arrival/foliage views were inspected. The initial portrait pullback placed a foreground post across the window; retaining the authored camera position removes the obstruction. Dynamic shadow striping, painted signage, foliage texture refinement, sourced references and the final bake remain open.
- Reloaded the site library through Blender MCP and inspected its viewport. Master contains 6,502 objects; the site contains 462 objects and twelve bamboo stems.
- All 34 GLBs pass structural checks; the 512-square UV2 sample check passes 120 render meshes. Current assembly has 233,542 triangles. Godot imports 174 collision shapes, 63 markers and 31 cameras. Current SHA256: `6e7af46c3274f80cbddd9b1f9fd04cba21642c8f0c8b7d710d399e58c618d3d9`. Earlier lightmaps remain stale and excluded from production.

### Longcui nunnery gate and twelfth visitable location

- Replaced the generic hall with six metres of capped whitewash wall, paired closed timber gates and a small gate roof. Added two bent plum trunks with sparse branches and five-petal blossom clusters, one hanging lantern, and an open bronze incense bowl with three feet and three sticks. Four markers and three cameras are exported.
- Added a stone approach from the water pavilion around the eastern end of its railing. `test_nunnery_route.gd` first failed for the missing room, then passed travel in both directions, floor support, closed-gate collision and rejection of entry.
- Generated desktop and 390 × 844 arrival/gate/incense views. Arrival and incense views were inspected at both sizes: lantern, branches, gate and bowl remain readable. Painted signage, reference collection, blossom/material refinement and final lighting/bakes remain unfinished. Dynamic wall shadow striping is still visible.
- Reloaded Longcui and stage libraries through Blender MCP and inspected the viewport: 6,476 master objects, 359 site objects, exactly one site point light.
- All 34 GLBs pass structural checks; 118 render meshes pass the sampled UV2 overlap check. Current assembly: 228,542 triangles. Godot imports 184 collision shapes, 66 markers and 33 cameras. SHA256: `cc59452ab46c1e55ab8d23ba3d9ead44ad851b14dba557fe0309df3bcf24c097`. Previous lightmaps remain stale and excluded.
- The shared western route regression passed: water pavilion and reed island remain reachable in both directions with floor support after adding the nunnery branch.

### Aojing lowered hall and thirteenth visitable location

- Replaced the generic hall with a seven-metre low facade, one amber window, dark shutters, broad continuous roof and a 1.8 m dry ledge at -0.65 m. Added a pond at -1.1 m, embankments, ledge parapet and a descending guarded ramp. Cut the raised stage canvas around the pond/hall and removed the old elevated walk through the site. Three markers and two cameras are exported.
- Added the red courtyard's water-level-hall route, hall inspection, pond view and return. The first physics run passed descent but caught an overlapping upper path edge on ascent. Moving the ramp start to the actual slab edge fixes the lip. The final `test_reflection_route.gd` passes descent, return climb, ledge height, floor support, closed-hall collision and rejection of entry.
- `MAT_aojing_water` is a separate batch currently using the existing animated-water shader. Surface import tests cover the original water, this pond and three fog batches. The new water batch is excluded from opaque lightmap baking/coverage. A readable window/roof reflection is NOT implemented yet; pond composition and reflection integration remain the next work.
- Desktop and portrait views were generated; arrival frames were inspected. Camera framing remains provisional until the reflection pass is visible. This does not satisfy the site's final camera/reflection acceptance.
- Initial hall/stage libraries were reloaded and inspected through Blender MCP (6,284 objects; hall 136 objects; pond vertices at -1.1 m). The subsequent ramp correction is saved in source and exports and verified by the Godot traversal test.
- All 34 GLBs pass structural checks; 119 render meshes pass sampled UV2 overlap checks. Current assembly: 222,872 triangles. Godot imports 194 collision shapes, 68 markers and 34 cameras. SHA256: `a92a4c7ae5b65a0c7b86dc7d687e6b01d04a20e9084b4b071bedc01e1b7e4f56`. Earlier lightmaps remain stale and excluded.

### Aojing planar reflection

- Added a mirrored-camera SubViewport and projective pond shader. Only Aojing's hall and distant painted scenery enter the capture; the pond and studio floor are excluded. Camera transform/projection synchronize before drawing, the render target is capped at 768 pixels on its longest side, and capture updates stop beyond 18 m from the visitor or below water.
- Structural reflection test first failed for the missing renderer, then passed camera height, capture layer, pond material/texture and distance gating. Fixed-time renderer comparisons pass after the final synchronization change: reflection disable changes 68,810 pixels, excluding the window only from the capture changes 2,456 pixels in its reflected image, and ripple time changes 1,797 pixels. The visible hall and controls remain unchanged within tolerance.
- Desktop and portrait pond views were inspected; window and roof reflection are visible. Updated the local interaction text to describe the implemented effect. Final water-dominant composition and alignment with the Blender source cameras remain open, alongside art/lighting/reference requirements.
- Stationary desktop capture profile: 12 visible capture draws, 768 × 326 render target, median frame interval 5.736 ms active versus 4.797 ms frozen. This is not target-phone acceptance. The general profiler now includes capture draws in its combined draw-call upper bound. Details and limitations: `docs/pond-reflection.md`.
- Geometry/source hash is unchanged from the prior Aojing pass. Existing static lightmaps remain stale and production still uses dynamic lighting.

### Daoxiang farmhouse and all fourteen locations visitable

- Replaced the generic tiled hall with a six-metre farmhouse, thick uneven thatch mass and 318 layered stalk bundles. Added a rough fence below one metre with a central opening, closed plank door with a warm sliver, rake, hoe and a flat paddy backdrop with field bands/rice strokes. Four markers and four cameras are exported.
- Connected Hengwu → Visit the farmhouse through its front opening and around the courtyard wall. `test_farmhouse_route.gd` first failed for the missing room, then passed both directions, floor support, closed-door collision and rejection of entry. After the final asset import, `test_courtyard_route.gd` passes the shared courtyard approach and local inspections.
- Desktop and portrait arrival/door/tool/paddy renders were generated. Arrival, paddy and tool views were inspected across those sizes. The first paddy camera intersected the eaves; moving it clear and increasing paint contrast improves the view, but the farmhouse still hides much of the flat in the inspection composition. Paddy art/composition, painted signage, sourced references and final lighting remain unfinished. Visitable does not mean final site acceptance.
- Reloaded the farmhouse/stage through Blender MCP and inspected its viewport. Master contains 6,493 objects; the farmhouse has 588 objects and 318 thatch bundles.
- All 34 GLBs pass structural checks; 121 render meshes pass sampled UV2 overlap checks. Current assembly: 224,312 triangles. Godot imports 203 collision shapes, 71 markers and 37 cameras. SHA256: `637c9222941384962eea290d7dc867744d9a59048b327e41056abda014072624`. Existing lightmaps remain stale and excluded.
- All 14 site pages now correspond to reachable locations. Full kit variants, reference collection, painted lettering/material atlases, camera/lighting acceptance, fresh bakes, service integration and phone performance remain outstanding under the original completion plan.

### Painted paddy backdrop and clear inspection view

- Camera-only comparisons confirmed that the old field-line drawing was largely behind the farmhouse. Replaced that geometric placeholder with a generated gouache-style rice-paddy texture on a UV-mapped, framed 6 × 3 m studio flat beside the house. The painting contains receding terraces, rice plants and low hills across its width.
- Preserved the 1774 × 887 generated source under `textures/backdrops/daoxiang-paddy-v1.png`; documented provenance and checksum in that directory. This is original production art, not a sourced film/architecture reference. It is packed into the Blender library and embedded as base-color/emission textures in the GLB.
- Updated the arrival and inspection cameras in Blender and Godot. Native Blender inspection and the graded desktop paddy view show correctly oriented terrain and brush detail instead of the largely occluded grid. Portrait verification is recorded below. Remaining lettering, atlas and final lighting requirements are unchanged.
- Asset structure passes for all 34 GLBs; sampled UV2 overlap passes for 119 render meshes. Current assembly: 223,952 triangles; Godot imports 203 collision shapes, 71 markers and 37 cameras. Linked Blender master has 6,333 objects. Source SHA256: `cf78dd90bf23247ece63e26100e8c84a1460c4e6049ab015a0a8a34e023f265e`. Lightmaps remain stale and excluded.
- The 390 × 844 paddy inspection render was inspected: terraces and brush texture remain visible above the controls. The shadow from the farmhouse remains part of the current dynamic lighting, pending the final backdrop-lighting pass.

### Corridor kit variants and LODs

- Replaced the corridor starter library with straight, 90° corner, T-junction and six-tread stair modules, plus independent 40% LOD variants. Each module has separate collision, named connection ports and two UV channels. The Blender file contains module scenes and an eight-instance showroom; legacy corridor export paths retain the straight module.
- Actual exported LOD0 counts are 972–1,208 triangles, below the 2,000 per-piece target. Actual LOD1 ratios are 39.84–39.92%. `verify_corridor_kit.py` passes all eight GLBs, including matching collision transforms and connector coordinates. General asset validation now passes 42 GLBs.
- `test_corridor_kit.gd` passes physics traversal through every connector at both LODs, including stair ascent/descent. The showroom render was inspected for LOD shape retention.
- Direct overwrite was rejected by Blender while the source library was in use; packaging through a temporary file resolves it. The packaging script now preserves the completed multi-scene corridor library.
- Garden assembly/source hash and route geometry are unchanged. Replacing assembly instances, runtime LOD switching and material atlases remain unfinished. See `docs/kits/corridor.md`.

### Wall kit variants and LODs

- Added eight standalone modules: whitewash bay, moon/vase gates, four lattice window patterns and coping cap. Sixteen GLBs include independent 40% LODs, separate collision, both UV channels and gate connectors. The editable Blender library includes module scenes and a 16-instance showroom.
- First render exposed decimation artifacts from interior segment faces. Removing paired internal faces and welding before decimation fixes the strips and holes; the corrected showroom render was inspected. Collision helpers are hidden in the Blender viewport and render after export. Native MCP reload and scene inspection confirm 18 showroom objects.
- Export verification passes 316–1,584 triangles at LOD0 and 39.73–40.00% LOD1 ratios. General structural validation passes 58 GLBs. Godot physics tests pass both travel directions through both gates and blocking at the wall/four window variants at both LODs. Tested Godot copies match final exports byte-for-byte.
- Garden assembly remains unchanged. Assembly integration, runtime LOD switching, atlas work and collision simplification/mobile profiling remain open. Gate/window modules currently use 89/90 small collision boxes; this is not final mobile acceptance. See `docs/kits/wall.md`.

### Consolidated wall collision

- Replaced 89/90 collision objects per gate/window with one static collision mesh per module. Gates use the actual wall aperture, with welded faces and dissolved coplanar edges; windows use one blocking box. Moon/vase collision meshes contain 380/84 triangles, respectively; other modules contain 12 each.
- Godot tests verify one imported collision shape per tested module, concave shapes for gates, passage in both directions, blocking at both gate piers, and blocking at the wall/four windows at both LODs. All pass. All 58 GLBs pass structural validation; all sixteen Godot wall files match final exports.
- Reloaded the library through Blender MCP and confirmed one collision object for each of sixteen variants. The viewport retains the inspected wall shapes. Assembly geometry is unchanged; this reduces standalone collision complexity but is not a measured phone performance result.

### Pavilion kit variants and LODs

- Added six reusable parts: hexagonal/square roofs, post, three-level bracket set, half-round eave tile strip and curved-back leaning bench. Twelve exports include independent 40% LODs, two UV channels, one collision mesh per part and post/roof mounting markers. The normal editable Blender library includes a twelve-instance showroom; packaging preserves it.
- Render inspection led to weighted roof simplification that prioritizes primary surfaces over tile ridges/rafters. The final showroom render and native Blender viewport were inspected. Roof tile detail still needs the shared atlas to retain its appearance at a distance.
- Actual LOD0 counts are 216–1,672 triangles; LOD1 ratios are 39.68–40.00%. Per-kit export checks pass, and general validation passes 70 GLBs. Godot tests pass collision rays for all six parts at both LODs, mounting-port counts and capsule passage through assembled square/hexagonal pavilions at both LODs.
- Native MCP inspection confirms fourteen showroom objects. Garden assembly remains unchanged. Shared atlas, runtime LOD switching, site integration, lighting and target-phone profiling remain unfinished. Details: `docs/kits/pavilion.md`.

### Qinfang pavilion kit integration and portrait visibility

- Replaced Qinfang's original roof/posts/brackets with the reusable hexagonal roof, six posts and six bracket sets. Added two leaning benches inside the south bridge balustrades. Preserved the bridge/plinth, table, six lanterns, corridors and interaction markers. Fifteen separate collision meshes accompany the fifteen placed render meshes. Authoring and the linked site library are saved; collision helpers are hidden in Blender.
- The new south-post collision correctly exposed the original route passing through that post. Added a 0.8 m lateral detour to both the gate approach and bamboo route. The four local approaches pass in both directions, and full entry-route and bamboo-route regressions pass, including floor support and return travel.
- Portrait Qinfang previously hid the building behind its long command list. Added a scroll container capped at 152 pixels for this room in portrait. Layout tests verify the full command count, scrolling to the last command and restoring the desktop layout on resize. Desktop and portrait captures were inspected; the pavilion roof, posts and table are now visible above the portrait controls.
- Structural checks pass all 70 GLBs; sampled UV2 overlap checks pass 121 render meshes. Current assembly: 223,612 triangles and 121 render meshes. Godot imports 218 collision shapes, 71 markers and 37 cameras. Source SHA256: `4ff27b9b0c75f03a3cda1252d755ffa6725ea5ce604918b567f556fdfdbc4e8b`. Existing lightmaps remain stale and excluded.
- Native Blender MCP reload confirms 826 Qinfang objects, including thirty placed kit objects, and 6,157 objects in the linked master. The revised site page records current implementation and outstanding acceptance. Other site integration, atlases, runtime LOD switching, painted signs, lighting and phone performance remain unfinished.

### Pavilion shared PBR atlas and GPU compression

- Added deterministic original 2048² base-color, normal and ORM textures for lacquer wood, tile, stone and bronze. Four UV regions have 32-pixel padding. Maps are packed in Blender and embedded in all twelve pavilion GLBs; no procedural shader nodes are needed at runtime. UV0 is remapped by source material, while the existing lightmap UV channel is preserved. Texture provenance and checksums are recorded in `textures/atlases/pavilion/`.
- Every standalone part now exports one render primitive/material. Reintegrated the textured parts into Qinfang; the fifteen placed render meshes become one shared atlas batch in the exported garden. Structural validation passes 70 GLBs and the sampled UV2 overlap check passes 120 assembly meshes. Godot imports 218 collision shapes, 71 markers and 37 cameras. Geometry remains 223,612 triangles; assembly SHA256 is `bc803330a754d600ffdaaea083443018fd458342f3d5610ff602e2b159dfde98`.
- `verify_pavilion_atlas.py` checks all twelve files: three embedded 2048 images match source pixels, PBR channel bindings are present, and every triangle's UV0 stays within one padded material region. Godot tests verify one surface per part, all texture bindings and dimensions, and enabled normal maps. Qinfang's four approaches still pass in both directions after reintegration.
- Initial uncompressed import used about 48 MiB for the three atlas maps, including mipmaps. Enabling GPU compression at full resolution reduces their imported image data to about 8 MiB. Whole-scene texture memory in the desktop Qinfang view changes from 84,054,186 to 42,111,189 bytes. These are M2 Max desktop measurements; mobile export formats and target-phone acceptance remain unverified. Individual standalone GLBs duplicate embedded atlas data on disk; the garden uses one shared set.
- Atlas showroom, native Blender scene, desktop and portrait Godot views were inspected. Broader art refinement, other kit atlases, runtime LOD switching, final lighting/bakes, services and phone acceptance remain open. Previous lightmaps remain stale and excluded.

### Corridor atlas and sixteen-bay integration

- Applied the pavilion architectural atlas to all eight corridor exports. Each render module has one material/primitive; glTF checks pass embedded image pixels, PBR bindings, padded UV regions and unchanged triangle/LOD targets. Godot PBR import checks and traversal through all standalone variants at both LODs pass. Corridor/pavilion assets share the same atlas set rather than allocating an additional one.
- Replaced Qinfang's sixteen original approach bays with the completed straight modules. Preserved all 36 bridge railing pieces. Inspection found misplaced legacy beam remnants outside the corridor axes; these were removed. The final native site has 474 objects, including 96 new corridor objects, and the linked master has 5,805 objects.
- The first integrated physics run exposed lost local offsets in unlinked library rail colliders. Copying `matrix_basis` instead of stale evaluated `matrix_world` preserves the offsets. Exported rail transforms now sit at ±0.86 m from each bay's centerline. The east bulletin-hall and pond turns also needed 0.5 m clearance beyond the new rail ends; their paths were adjusted.
- `test_corridor_integration.gd` passes all sixteen bays through four full approach paths and their end junctions in both directions. Pond and nunnery route regressions pass. Desktop and portrait arrival views, plus the final native Blender viewport, were inspected.
- All 70 GLBs pass structural checks; sampled lightmap-UV overlap checks pass 119 assembly render meshes. Current assembly has 230,460 triangles; Godot imports 282 collision shapes, 71 markers and 37 cameras. SHA256: `c27341bc993c45ff6fadc8ac58cbe79816d24f034ed45ddad91fdf6d38fd36b8`. Export/Godot source bytes match. The assembly has one shared architectural atlas material and exactly three associated maps; GPU compression remains enabled.
- Automatic LOD switching, other kit/site work, final lighting/bakes, service integration and target-phone acceptance remain open. Prior lightmaps are stale and excluded.

### Water kit modules and bridge traversal

- Added stream/pond surfaces, a three-metre masonry embankment, six-leaf lotus cluster, six-metre wooden bridge and arched stone bridge. Twelve GLBs include separate LODs and UV channels. Bridges have 1.8 m decks, end markers and separate deck/side collision. Water and leaves intentionally have no walking collision.
- Initial automatic simplification damaged disconnected masonry. Rebuilt the embankment and both bridge LOD1 models as continuous surfaces with simplified supports. Final render inspection confirms retained wall/deck/rail silhouettes. LOD0 counts are 256–792 triangles; LOD1 ratios are 39.20–40.28%.
- Wood/masonry use the compressed shared architectural atlas. Configured stream/pond imports to use the existing animated water shader. Lotus material refinement and final water-kit art remain open.
- Export validation passes all twelve modules; general structure validation passes 82 GLBs. Godot tests pass water shader assignment, collision counts, approaches from separate platforms, both-direction bridge traversal, stone-arch elevation and side-rail blocking at both LODs. Tested Godot files match final exports.
- The editable library includes a twelve-instance showroom. Native Blender MCP inspection confirms fourteen scene objects; showroom render and viewport were inspected. The general packaging script preserves the completed library.
- Garden assembly/source hash is unchanged. Kit placement, runtime LOD switching, remaining materials, other kits, final lighting/bakes, services and target-phone acceptance remain unfinished. Details: `docs/kits/water.md`.

### Western water-kit placement

- Replaced Ziling’s old crossing with the six-metre wooden bridge and three collision meshes. Both ends overlap their landings. Added four lotus clusters by Ouxiang and two beside Ziling; removed the replaced flat pad cylinders. Existing pavilion furnishings, island, reeds, markers and cameras remain. Source: `scripts/integrate_western_water_kit.py`.
- The full western route passed in both directions with floor support. Desktop and portrait captures of both sites were inspected in the placement pass. Blender master inspection recorded 5,734 objects and ten placed water-kit objects.
- The assembly has 233,868 triangles, 119 render meshes, 282 collision shapes, 71 markers and 37 cameras. Source and Godot GLB hashes match `9cc042f70bf58e8ed6f64bd57ca1a94f76f4bf7c66b2238cec9e84a6d9139ed9`. Prior lightmaps remain stale and excluded. Other water-module placement and final lotus art remain open.

### Wall PBR atlas

- Added original limewash plaster with broad trowel variation and fine grain, alongside wood/tile swatches matching the pavilion. Sixteen standalone wall GLBs now use one render primitive/material each and three embedded 2048² PBR maps. UV0 maps into padded material regions; the atlas application preserves UV1. Provenance, regeneration instructions and hashes are in `textures/atlases/wall/`.
- All sixteen exports pass source-pixel, PBR-binding and UV-region checks. Geometry/connector/collision checks retain the prior 316–1,584 LOD0 triangle counts and approximately 40% LOD1 ratios. Godot verifies complete full-resolution PBR texture bindings; all 48 extracted maps have GPU compression and mipmaps enabled.
- The rendered showroom and native Blender viewport were inspected, with both gate shapes and all four lattice patterns retained. Native MCP reports eighteen showroom objects. General structural validation passes all 82 GLBs.
- Garden assembly geometry/hash is unchanged by this standalone atlas pass. Wall placement, runtime LOD switching, final coping refinement, lighting, services and target-phone acceptance remain open.
- Final Godot physics regression passes gate travel in both directions, solid-wall/window blocking and gate-pier blocking at both LODs. All sixteen tested Godot GLBs match the exported files byte-for-byte.

### Hengwu wall-kit integration

- Replaced the courtyard’s original wall pieces with nine textured kit modules: six solid bays, two different lattice windows and one moon gate. Side modules fit the existing eight-metre depth; the front remains nine metres wide. Nine wall collisions are separate from the render geometry. Existing rocks, herbs, furniture, hall and markers remain. Native Blender master inspection confirms 5,707 objects and eighteen placed wall objects.
- Assembly UV checking exposed coplanar window-frame overlaps. Changing projection angles did not resolve them. Exported triangle inspection located overlapping horizontal/vertical frame faces; changing the source kit to butt joints fixes the underlying geometry. All sixteen standalone exports retain their triangle budgets and pass atlas validation. All 120 assembly render meshes now pass sampled UV2 overlap checking.
- The courtyard route passes outward/return travel with floor support, nine placed wall collision shapes, blocking at both windows and both gate piers, and local interaction actions. The farmhouse route through the same gate also passes outward/return travel. The courtyard test passed again after the final corrected asset import.
- Desktop arrival/book views and portrait arrival/book views were inspected. Portrait’s generic camera pullback moved it behind the new front wall; keeping Hengwu’s portrait camera inside the court restores the visible paving and table. Final color grading and lighting remain open.
- All 82 GLBs pass structure validation. Assembly: 239,568 triangles, 120 render meshes, 287 collision shapes, 71 markers and 37 cameras. One wall atlas material shares three compressed maps across the placed pieces. Export and Godot source bytes match SHA256 `8cc0f4c5be1697039106ba95e57701d6dd6ecadf4952b163339c5ec98679d2cf`. Prior lightmaps are stale and excluded. Other kit/site work, final lighting/bakes, service integration and target-phone acceptance remain open.

### Six rockery modules and passage verification

- Added small/medium/large pierced plaster stones, a walk-through arch, four-metre tunnel segment and six-metre cliff face. Twelve GLBs include independent 40% LODs, two UV channels, one separate concave collision mesh each and the existing architectural PBR atlas. Passage modules include front/back ground-level connection markers. The receiving site supplies the walking floor.
- Refined the first render’s regular arch/tunnel contours into uneven outer shells, added two arch-side piercings and varied the standing stones. Final showroom render and native Blender viewport were inspected. MCP confirms fourteen showroom objects: twelve instances, camera and light.
- LOD0 counts are 448–1,024 triangles; LOD1 ratios are 39.73–40.00%. Source BVH rays verify every piercing and a nine-ray passage grid against both render LODs. Export verification passes collision identity, connector transforms and UV channels for all twelve modules. Atlas checks pass source pixels, padded material regions and one render primitive per module. General structural validation now passes 94 GLBs.
- Godot material checks pass all PBR bindings. Physics tests pass rays through the pierced collision, blocking on solid rock and offset capsule traversal through arch/tunnel in both directions at both LODs. All tested Godot GLBs match final exports; 36 extracted maps use GPU compression and mipmaps.
- The normal editable Blender library includes all module scenes and is preserved by the general packaging script. Legacy rockery GLBs now contain the medium stone. Details: `docs/kits/rockery.md`. Garden assembly/source hash is unchanged. Site placement, runtime LOD switching, remaining flora/props/tech/stage kits, final art/lighting/bakes, services and phone acceptance remain open.

### Rockery entrance kit placement and two-bend route

- Replaced the original disconnected rock dressing with four fitted tunnel segments, two arches and two exit cliff faces. The central tunnel spans twelve metres along its axis and bends to either side, with matching deformed collision. A continuous paving slab replaces nine overlapping floor slabs. Two lanterns sit at the bends. Native Blender inspection confirms 5,662 master objects, 82 gate objects, sixteen placed kit objects and two site lights.
- Increased the route’s lateral offsets to follow the new centreline. Added checks that eight placed rock shells import, the straight entrance-to-exit sightline is blocked by tunnel collision, and the exit’s central approach sightline remains clear.
- The first full journey passed the tunnel but the return to the cell caught on the entrance arch’s edge. Moving the horizontal cell approach from 32.5 m to 33 m, then entering the marker along the centreline, resolves the turn. The complete cell → gate → pavilion → gate → cell physics regression now passes with floor support.
- Desktop and portrait tunnel/bend/exit captures were generated; mouth, second-bend and exit compositions were inspected across those sizes. The enclosed tunnel and amber side light are visible. The full-width pavilion reveal remains unfinished: the south covered corridor still dominates the low exit view. This is tracked explicitly in the site page, along with banana dressing, painted/carved lettering, drip decal, final lighting/fog and sourced references.
- All 94 GLBs pass structural checks; all 121 assembly render meshes pass sampled lightmap-UV overlap checks. Assembly: 243,998 triangles, 269 collision shapes, 71 markers and 37 cameras. Rockery shares the existing architectural atlas material and three maps. Export/Godot source bytes match SHA256 `e3b201de9848489236b9e55e5c7d48894a9a3b93724f507e3c3a4e21597175f8`. Earlier lightmaps remain stale and excluded.

### Scripted tunnel-exit reveal

- Added the specified reveal move while preserving all sixteen covered-corridor bays. After the visitor clears the exit arch, the camera slides through the south corridor’s open west side, rises above its roof and moves to the wide pavilion frame. The visitor pauses for the four-second shot; the command panel hides, then returns as walking resumes. Reverse travel does not trigger the shot.
- Captures start from actual walking-camera movement, including its follow lag. The trigger is placed far enough beyond the arch that the observed camera starts at approximately (-0.065, 1.545, 17.196), clear of the arch before moving sideways. Intermediate desktop and portrait frames were inspected; the final frame shows the pavilion, bridge and water with the command panel hidden. Final color/lighting acceptance remains open.
- Stored matching slide/lift/wide cameras and an editable rail curve in the Blender site. Export now inherits the authoring scene’s aspect ratio instead of the exporter scene’s default. Authored reveal cameras use the same 55-degree vertical field of view as Godot; exported positions and projections were checked. The final imported cameras retain that projection. Native Blender inspection recorded 5,666 master objects and all three reveal positions.
- `test_gate_reveal.gd` passes outbound triggering, imported camera projection, stationary visitor during the shot, hidden/restored panel, wide endpoint, resumed movement and suppression on return travel. The complete entry-route physics test passes with the reveal enabled.
- Geometry remains 243,998 triangles and 121 render meshes, with 269 collision shapes and 71 markers. Three added cameras bring the import to 40 cameras. Export/Godot source bytes match SHA256 `26e3de95c0d25df6d7e00295c5d6080114dcc98db7f36826ba734747ae7d6b1c`. Earlier lightmaps remain stale and excluded. Painted signage, banana/drip dressing, reference collection, remaining kits/services and phone acceptance remain open.

### Hexagram table variants and close view

- Exported twelve meshes: six solid/broken pairs, with each broken line joined into one mesh. The importer shows only solid variants initially. The controller accepts six integers ordered bottom to top, 0 broken and 1 solid; invalid input is rejected before visibility changes.
- Geometry verification passes bounds, row order, UV channels and open broken-line gaps. Godot tests pass all 64 patterns, default visibility and invalid-input rejection. The table action and return to the wide view pass desktop and portrait checks; both user-facing captures were inspected. Gate reveal regression passes.
- All 94 GLBs pass structural checks and all 127 assembly render meshes pass sampled UV2 overlap checks. Assembly: 244,142 triangles (including both variants), 269 collision shapes, 71 markers and 40 cameras. Export/Godot source SHA256 matches `fc9e099fc6a1cca451febee2139b99bdcba2cb24958d0cb384baf312d65ae0c6`.
- Bake setup now excludes mutually exclusive line variants from each other’s shadows and the static tabletop bake. This policy has not yet been verified with a fresh bake; old lightmaps remain stale and excluded. Live readings, remaining art/kits, final lighting and target-phone acceptance remain open.

### Rockery-gate banana and water-stain dressing

- Replaced the old exit bamboo with one seven-leaf potted banana. The first position was hidden behind the corridor railing; the final narrow planter sits at source (0.55, -17.35), inside the east approach edge. Leaves extend above the rail. The pot has its own collision; leaf tips stay above the visitor’s head.
- Added an original 512² transparent mineral/water-streak decal, generated with seed 2319 and projected onto the second bend’s actual rock surface with a 12 mm offset. glTF retains the embedded texture and alpha blending. Texture provenance and regeneration instructions are in `textures/decals/README.md`.
- Native Blender inspection confirms the plant and projected decal; the linked master contains 5,728 objects. The temporary unsaved dressing inspection scene contains 95 render objects. Desktop and portrait Godot captures were inspected. The plant reads as a dark silhouette; final lighting and composition acceptance remain open.
- All 94 GLBs pass structure checks, and all 128 assembly render meshes pass sampled UV2 overlap checks. Godot imports 270 collision shapes, 71 markers and 40 cameras. Assembly: 248,390 triangles. The full cell → gate → pavilion → gate → cell physics regression passes with the final planter position and scripted reveal. Export/Godot source SHA256 matches `9ede45b9d560137f9d680343d6b919646bf9c890b6893829719b3a1753cc952d`.
- Entrance lettering, sourced references, final fog/lighting/bakes, remaining kits/services and phone acceptance remain open. Previous lightmaps remain stale and excluded.

### Rockery entrance inscription

- Replaced the temporary typeset signboard with original brush lettering, 曲徑通幽. The 1.8 m decal follows the plaster arch; all projection vertices hit the rock surface. A normal map derived from the artwork alpha gives the letters a shallow recessed response to light. The original RGBA source and prompt are recorded in `textures/decals/gate-inscription-provenance.md`.
- Native Blender and desktop/portrait Godot arrival and close views were inspected. The four characters remain legible over the entrance. Godot imports the alpha material and normal map. All 94 GLBs pass structure checks and 128 assembly render meshes pass sampled UV2 overlap checks. Assembly: 239,426 render triangles, 270 collision shapes, 71 markers and 40 cameras. Export/Godot source SHA256 matches `7bbd626f332ccc52525ae60df847f42efcb98d7ca3f08ce349e14304683b9656`. Final fog, lighting, bakes, references and phone acceptance remain open.

### First-reading demo, milestone 1

- Added `docs/demo-milestones.md` as a four-milestone showcase path under the broader garden completion goal. Milestone 1 is a local cast and result card at the pavilion table.
- `scripts/build_demo_hexagram_catalog.py` extracts 64 unique bottom-to-top patterns, King Wen numbers, Chinese names, English meanings and trigram positions from the sibling 8-Bit Oracle source. The exported JSON is committed with the Godot project; runtime does not require the sibling repository.
- A local three-coin draw yields six values from 6 through 9. The primary and transformed hexagrams, moving-line positions and bronze line variants agree. Invalid casts are rejected. The result card identifies the experience as local and does not claim AI interpretation or private history. Closing retains the table pattern; recasting updates the same card and meshes.
- All 64 catalog entries round-trip in Godot. Tests cover coin outcomes, changing lines, invalid data, UI action/recast/close state and all six visible line slots. Desktop and portrait screenshots of the card and table were inspected. The existing cell → gate → pavilion route and gate-reveal regressions pass. The demo route focus, final look/sound, baking/performance and handoff remain milestones 2–4.

### Focused first-reading demo, milestones 2–4

- `godot/runtime/first_reading_demo.tscn` is the default scene. It uses the cell, gate, pavilion, reading card, and a final replay card. `entry_route.tscn` retains the full 14-location exploration. A button-only novice test and a full mouse/Enter-key input test pass through replay. The original entry-route and gate-reveal regressions still pass.
- Fresh Cycles lighting covers 32/32 opaque demo meshes from assembly SHA256 `7bbd626f332ccc52525ae60df847f42efcb98d7ca3f08ce349e14304683b9656`. The transparent gate inscription keeps its source material. The demo uses compressed 256-pixel runtime lightmaps and disables static-key shadows after applying the bake; the broad exploration scene remains dynamic. Six original, seeded WAV cues cover CRT, lantern, water, tunnel, reveal, and cast. Desktop and 390 × 844 screenshots, the bronze close-up, and 43-second route capture were inspected.
- On an Apple M2 Max at 1410 × 600, 60 explicit forced-draw samples per stationary demo view measured 83–121 visible draw calls, 123,744–161,486 visible primitives, 63,957,192 bytes of texture allocation, median draw intervals 2.5–6.0 ms, and p95 6.4–8.0 ms. These are desktop stationary results, not a phone or full-traversal performance certification.
- A clean Godot import from an empty `.godot` cache passed. The exported 491 MB pack cold-launched in the installed Godot 4.7.2 desktop renderer. The local zip includes the pack, launcher, 43-second H.264/AAC capture, run guide, and SHA256 checksums; archive and checksums passed. The one-page guide is `docs/demo-run-guide.md`. Mid-range phone GPU and other desktop hardware remain untested, and the larger garden completion plan remains open.

### Lower green grade and bulletin hall lighting pass

- Reduced the Godot color grade to 40% strength. The demo's desktop pavilion render now has a green-to-red mean-channel ratio of 2.65 in the scene region, compared with 3.32 at 70% strength. The palette remains green/amber, with more visible warm and neutral values.
- Moved 秋爽齋's key to the front of the facade, changed it to warm neutral, and added two amber lights at the existing lanterns. The Blender authoring scene, standalone hall file and glTF exports were updated. Desktop and portrait Godot views show the centre sign and screen bank more clearly; `test_study_lighting.gd`, `test_study_route.gd` and the four-practical check pass.
- The full garden source hash changed to `40ee57c072d121dbd3b45eb137273df02fdd30c2e3d9af46cfd66270d1efb90c`. Fresh Cycles bakes from that export cover all 32 opaque demo meshes and pass the demo coverage check. Desktop and portrait demo views, the first-reading flow, pointer/keyboard acceptance, and a cold launch of the rebuilt pack pass. The refreshed local archive and checksums pass. Final hall scroll art, site bake, sourced references and wider scene acceptance remain open.

### Bulletin hall painted title and scrolls

- Replaced the temporary typeset 秋爽齋 sign with a transparent brush-painted title on the existing wood board. Replaced twelve rectangular scroll marks with original bamboo and plum ink paintings on the two existing scrolls. Their source PNGs and prompts are in `textures/decals/study/`; the Blender authoring scene, standalone hall and glTF export embed the textures.
- The wide desktop and portrait Godot views keep the title visible. The centre-bank close view shows both distinct paintings beside the four amber monitors. The route test still passes in both directions. The hall's exported render triangle count fell from 21,764 to 12,214 after removing the typeset geometry.
- The assembly source SHA256 is now `cd3cc214a0d04d8c13ebcfd3b6fa36b3f2a3ec532c45d29c9c4c4f5c01b4c4cf`. Fresh Cycles lightmaps cover all 32 opaque demo meshes from that source; desktop and portrait renders and project/pack input acceptance pass. The local pack, video, archive and checksums were refreshed. Compressing the three new imported textures at a 1024-pixel limit brought measured demo texture allocation to 64,991,848 bytes (61.98 MiB), below the 64 MiB target; the centre-bank painting remains legible. The wider hall still needs a site-specific bake, sourced visual references, final material acceptance and live bulletin content.

### Hilltop hall painted sign and warmer plaster

- Replaced the temporary 凸碧堂 font with original brush lettering on the existing signboard and gave the terrace, parapets, twenty treads and topic table a warmer site-specific plaster material. The title PNG, prompt and editable Blender source are preserved; the glTF embeds the art with the distinct `tubi-title` name so it cannot collide with the bulletin hall title.
- Desktop and portrait Godot arrival views, table views and Blender's material viewport were inspected. The terrace/stair render regions' green-to-red mean-channel ratios fell from 4.8–5.4 to about 2.2. The four-metre climb, overlook action, return descent and shared bulletin hall route pass against imported collision. All 94 GLBs pass structural checks. The export and Godot source SHA256 match `9e8955e181738a595087fe7b9a32fe34a00283dd3c398ee877629fbec1adc551`.
- The hilltop artwork remains outside the focused first-reading route, but changes the shared assembly source. Fresh Cycles lightmaps now cover 32/32 demo meshes from this hash; desktop and portrait demo views and project input acceptance pass. The three-view desktop profile records 85–126 draw calls and 65,462,456 bytes (62.43 MiB) of texture allocation after compressing the new title texture. The local pack and capture were refreshed. Site-specific lighting/bake acceptance, sourced stills and the light-linked backdrop wash remain open.

### Softer stage lighting and grade

- Reduced the Godot color-grade strength from 40% to 20%, neutralized the ambient and fog colors, and changed the broad Blender stage and site keys from saturated green to a softer green. The painted moon is pale cream, and the cyclorama and mountain layers are less green. Local CRT and amber practical colors remain.
- Re-exported the editable source and rebaked all 32 demo lightmaps. The canonical export and Godot asset share SHA256 `fc01b60b7250c395ef0ac298b18756eb20b84e7925812155b2637c965273e706`. Desktop and portrait pavilion and hilltop renders were inspected; the demo flow, four-metre hilltop climb, descent, and shared bulletin hall route pass. All 94 GLBs pass structural checks.
- The refreshed desktop profile shows 85–126 visible draw calls and 65,462,456 bytes (62.43 MiB) of texture allocation. A forced exit during the 1.6-second opening CRT sound reports an engine shutdown resource warning; a timed exit after the sound finishes is clean in both project and pack. Normal route and pack input tests exit cleanly. Mobile GPU testing and site-specific bakes remain open.

### Priority-2 hall bakes in exploration

- Baked the bulletin and hilltop halls from the current `fc01b60b7250c395ef0ac298b18756eb20b84e7925812155b2637c965273e706` assembly. The site index verifies all 19 opaque render meshes: ten bulletin hall meshes and nine hilltop meshes. Transparent painted titles stay on their source materials. The lightmap metadata and images are copied into Godot, and the normal exploration scene applies them only when the source hash matches.
- Desktop and portrait arrival/action views were captured after integration. The hall facades and warm hilltop terrace remain readable; scroll paintings and signs remain visible. The study return route, four-metre hilltop climb and descent, and warm-key/lantern test pass. Sourced visual references, the light-linked backdrop wash, and final material acceptance remain open.

### Hilltop viewing seats and reference leads — 2026-10-03

- Added two short wood viewing benches to the hilltop terrace in the editable Blender source and standalone site library. They sit against the side parapets, outside the stair arrival and topic-table route; each has an imported collision mesh. The whole-garden and Godot asset SHA256 match `aaa9ae532e59d816f9c26ea10f8c50644f6330c758875a909023608140607f79`. All 94 GLBs pass structural checks.
- Rebaked 32/32 opaque demo targets and 19/19 opaque priority-2 hall targets from that source. The missing-material guard in the bake target scan now handles collision primitives. The hilltop climb, overlook and descent and the study return route pass after the import. Desktop and portrait hilltop views were rendered.
- Added reviewed public collection links to both site sheets. A Shaw night-set still and a site-specific study exterior are not yet verified. The hilltop material close-up, backdrop wash and final material acceptance also remain open.

### Further green reduction — 2026-10-03

- Added a 50% green-excess neutralization after the existing 20% color grade in the shared Godot renderer. It affects baked and dynamic scenes and keeps amber lantern and window highlights. Refreshed desktop and portrait demo, study and hilltop reference views; the hilltop painted mountains and plaster are less green. The 43-second capture and local pack were refreshed after this grade; a cold pack test passes. This remains a visual pass, not final site material acceptance.

### Light-linked painted backdrop — 2026-10-03

- Added one broad Area light to the editable Blender stage, linked only to the cyclorama, three painted mountain layers and moon. A low-resolution Cycles on/off comparison confirms a mean RGB response of 0.0058 while the receiver collection excludes buildings. The standalone stage library preserves the light and its five receiver links.
- glTF does not support the authored Area light, so export skips it. Godot creates one backdrop-only directional substitute on a separate visual layer. Its mask test confirms five painted receivers and no building receivers. A hilltop render comparison shows the painted mountains brighten while the hall remains separately lit. The canonical glTF and Godot asset remain at SHA256 `aaa9ae532e59d816f9c26ea10f8c50644f6330c758875a909023608140607f79`, so existing bakes remain current.
- Refreshed desktop and portrait demo, study and hilltop views, plus the 43-second video and exported pack. The hilltop and study routes, first-reading flow, and cold pack pass. The final desktop demo profile records 85–126 visible draw calls, 65,462,456 bytes (62.43 MiB) of texture allocation, and 1.30–1.49 ms median forced-draw intervals across three stationary views on this Mac. The archive and checksums pass.

### Imperial facade painted title and lacquer doors — 2026-10-04

- Replaced incomplete typeset 大觀樓 glyphs with original painted gold lettering on the existing board. The transparent source, prompt, and provenance are in `textures/decals/imperial/`; the Blender source and standalone imperial library embed the artwork. Ten closed door leaves now use red lacquer and twenty recessed panels use a darker related material. A warm-neutral hard key aims below the eaves. The arrival camera moves into the east side aisle; the covered walk still borders the left of the frame.
- The canonical export and Godot asset share SHA256 `770f338cee88e00dbbadd14a4ed2b900905e1ce4b375ff0e9d1b6886c6714d0e`. All 94 GLBs pass structural checks and all 136 assembly render meshes pass the sampled UV2 overlap check; the assembly has 218,480 triangles. Fresh Cycles bakes cover 32/32 opaque demo meshes and 28/28 opaque priority-2 meshes across the study, hilltop and imperial facades. Nine imperial targets use 128 samples to reduce visible grain; transparent title artwork retains its source material.
- Desktop and portrait imperial arrival and door captures were inspected. The north walk passes outward and return traversal, floor support, closed-door collision and rejection of entry. The first-reading demo passes through replay. Current desktop profiling records 88–129 visible draw calls and 65,933,064 bytes (62.88 MiB) of texture allocation across three stationary demo views; median forced-draw intervals are 1.29–1.89 ms on this Mac. Study, hilltop and demo reference views were refreshed.
- Sourced visual references, final atlas/material review, wider garden lighting acceptance and target-phone profiling remain open. This facade pass does not complete the full garden spec.
- The updated local pack cold-tests both the first-reading demo and imperial north walk. The 43-second capture, archive and checksums are refreshed and pass.


## Flora library pass — 2026-10-04

- Built all eight specified flora variants and independent LOD1 companions in the editable Blender library. One original 2048px atlas adds muted foliage, brown bark, terracotta and pale pink plum blossoms. Base meshes use 252–1,596 triangles; manually built LOD1 meshes use 34–46% of the base geometry.
- Export checks pass for all sixteen modules: UV0/UV1, alpha masking, ground anchors, collider parity and triangle targets. The Godot test verifies sixteen rendered meshes sharing one alpha-scissor material and texture resource, plus six trunk/planter colliders across the two detail levels. Both overview renders were reviewed after replacing destructive generic decimation. All 110 exported GLBs pass the general structural check.
- Details and images: `docs/kits/flora.md`. The garden assembly, site bakes and packaged demo are unchanged. Site placement and LOD switching, remaining props/tech/stage assets, final art and lighting, services and phone acceptance remain open.


## Flora placement and route pass — 2026-10-04

- Placed 23 shared-kit plants in five authored sites: four bamboo clumps at Xiaoxiang, two banana plants at Yihong, two plum trees at Longcui, ten reed clumps at Ziling, and three bamboo clumps plus two waterside willows at Qinfang. Original planters, beds and approach collision remain in use. Distance LOD switching uses a 14 m cutoff with a 2 m buffer; rendered geometry changes independently of collision.
- The route check found that a covered-walk post and full rail blocked the bamboo turn. The source now has a visible two-metre opening, replacement end posts and matching side collision. The four affected routes pass outward and return movement, floor support and closed-door checks. Atlas sharing is verified on the underlying mesh materials as well as active overrides; a stale import cache was rebuilt during verification.
- The final assembly SHA256 is `8b18e3263ba1bdb5f140e2790e3f5b0f19b1a6be677038c9defcee788c9b62ba`. Its 156 render meshes pass the sampled UV2 overlap check; all 110 GLBs pass structural validation. The 32 demo and 28 priority-2 bakes were refreshed and their source hashes match. The full first-reading demo passes through replay with those bakes.
- A compressed, mipmapped 512px runtime import of the original 2048px flora atlas keeps demo texture allocation at 66,282,616 bytes (63.21 MiB). The three stationary desktop demo views use 104–149 visible draw calls and 119,190–149,946 primitives, with at most four practical lights. This leaves little draw-call headroom for further dressing; new assets need batching or visibility controls. Desktop evidence does not establish phone GPU acceptance.
- Desktop and portrait plant views were reviewed. The editable site files, runtime assembly, source-matched bakes, local playable pack and capture are updated together. Details: `docs/kits/flora.md`. Additional site dressing, remaining props/tech/stage variants, painted signage, sourced references, final lighting, service contracts and phone acceptance remain open.


## Prop library pass — 2026-10-04

- Built all eight specified props with independent LOD1 companions: hanging/standing lanterns, brazier, stone table, stool, incense burner, calligraphy scroll and folding screen. The editable Blender file contains a showroom and sixteen module scenes. Base geometry uses 428–1,420 triangles; LOD1 uses 38–44% while retaining the functional parts.
- One original 2048px atlas layout provides base color, ORM and emission. Cream paper, gray stone, red-brown wood and bronze add color variety. The scroll's four characters 清風明月 were visually checked after fixing a missing glyph in the first font face. Runtime maps are compressed and shared at 1024/256/256px. Lanterns provide light anchors and emission, with no additional realtime lights.
- Export checks pass for geometry, PBR maps, UV0/UV1, connector positions and matching collision. Godot checks pass for sixteen models, one shared material and eighteen colliders. Both detail-level overviews were reviewed. Blender MCP confirms the saved library has sixteen module collections and a showroom. All 126 GLBs pass structural validation.
- Details: `docs/kits/props.md`. The main garden source hash, current bakes and playable pack are unchanged. Prop placement needs route/budget checks and batching; ORM bake support is now checked below. Tech/stage kit variants, remaining site materials and signs, sourced references, final lighting, services and phone acceptance remain open.


## Prop baked-material integration — 2026-10-04

- The Cycles adapter now accepts ORMMaterial3D and preserves the shared packed roughness/metallic map. Baked occlusion is not applied twice. Add and multiply emission operators retain their source behavior. Whole-mesh material overrides are cleared after conversion so they cannot hide the baked surface materials.
- The new prop adapter test passes in headless and desktop Godot, including shader rendering. The existing adapter check passes with all 32 current demo records, and the full first-reading flow passes through replay. Its regression check now uses the current demo index rather than the outdated experimental full-garden index.
- Garden geometry, lightmap files and the local playable pack remain unchanged. Prop placement, batching and route/budget checks are next; the full scene goal remains active.


## Prop placement and budget pass — 2026-10-04

- Replaced existing dressing with 15 hanging lanterns, 14 stone stools, two stone tables and one incense burner across seven sites. Fitted placements preserve mount positions, seat heights and table tops; existing lights, triggers and collision transforms remain unchanged. The interactive hexagram table and wooden tea table retain their authored behavior. All seven Blender site libraries are directly openable; Blender MCP verifies their saved scenes and collections.
- Props export in seven shared-atlas batches. The sampled UV check caught overlapping kit UVs after joining; the exporter now repacks the second channel rather than adding a third channel that glTF would omit. All 158 render meshes pass at 512-square sampling. All 126 GLBs pass structural validation; the assembly has 239,794 triangles.
- Current source SHA256: `562b72dd698ed75504b98c30f8860a0ab24a81dc6de800b8b5b0247e82f40c2a`. Fresh Cycles bakes cover 32/32 demo meshes and 30/30 opaque priority-2 meshes. Their source hashes match. Runtime compression is configured for both current catalogs at 256px, without changing the source PNGs.
- An initial profile exceeded the draw and texture limits. Small prop batches now stop drawing beyond 28 m, and the shared runtime color map uses 512px with 256px ORM/emission. After configuring the newly created lightmap imports, the three stationary demo views pass at 101–145 visible draw calls, 123,148–146,432 primitives, 66,544,800 bytes (63.46 MiB) of texture allocation and at most four practical lights. Forced-draw medians are 1.31–1.97 ms and p95 intervals 2.22–3.15 ms on this Mac. These results do not establish phone or full-traversal GPU acceptance.
- The demo, study courtyard, bulletin hall, hilltop, nunnery and western routes pass. All seven dressed sites have reviewed desktop and portrait references. The incense camera was lowered to keep the burner’s feet above the interface. Kit overview renders were refreshed and the four scroll characters remain legible at the reduced runtime size.
- The full scene goal remains open: tech and stage variants, further site materials/signs and dressing, sourced references, final lighting, service contracts and phone acceptance still remain. Details: `docs/kits/props.md`.
- The local playable pack cold-tests through replay and launches on desktop. The 43.7-second capture and demo references are refreshed. The five-file archive and checksums are refreshed for this source revision.


## Tech library pass — 2026-10-04

- Built all six inventory variants and independent LOD1 companions: amber/green CRTs, four-monitor bank, cable run, open cell door frame and terminal desk. The editable library contains a showroom and twelve module scenes. Base geometry uses 536–1,820 triangles; lower-detail meshes retain 38–43% with matching connectors and collision volumes.
- One original 2048px atlas provides warm gray cases, dark wood, bronze controls, charcoal cable/steel and phosphor screens. CRTs have curved screen grids, case bevels, controls and vents. Text is static set dressing with baked scanline modulation. Source and runtime emission strength are four. Enlarged Menlo Bold lettering resolves the broken-looking text from the first 512px runtime render.
- All twelve GLBs pass PBR, UV-channel, connector, actual triangle-count and collider-parity checks; sampled UV1 overlap checks pass. Godot verifies twelve single-surface models sharing one ORM material, fourteen simplified colliders, clear door passage and solid frame posts, with no added practical lights. Compressed mipmapped runtime color/emission maps use 512px and ORM uses 256px. Both detail-level overviews and the close screen render were reviewed. Blender MCP verifies twelve module collections and the showroom without changing the open scene. All 138 GLBs pass structural validation.
- Details: `docs/kits/tech.md`. The main garden source, existing bakes and local playable pack are unchanged. Tech placement in the terminal cells and bulletin hall, the terminal sheet’s folding chair, stage variants, further site art, sourced references, final lighting, services and phone acceptance remain open.


## Tech placement and release pass — 2026-10-04

- Placed 33 tech modules in the terminal cells and bulletin hall: six CRTs, nine desks, six open frames, three four-monitor banks and nine cable drops. The 18 screens use static phosphor artwork. Warm gray cases, red-brown timber and charcoal steel/cables add color variety. Existing lights, triggers and unrelated collision transforms remain unchanged. The six cell openings retain 1.12 m clear width and 2.1 m clear height. Both site libraries are directly openable; Blender MCP confirms their catalogs without changing the open scene.
- Two shared-material batches add 26,544 tech triangles. The full assembly has 156 render meshes and 262,702 triangles; sampled UV2 overlap checks pass and all 138 GLBs pass structural validation. Source SHA256 is `db2e84a9c6f72dfc6686421b07f0ea1e8334b1f0f9e2818fe02d1b0adfa4c2dd`. Fresh Cycles coverage is 31/31 demo and 29/29 priority-2 opaque meshes, with matching source hashes and compressed 256px runtime lightmaps.
- The placement test verifies underlying and active material sharing, UV2, triangles, 33 added collision shapes, six clear doorways and solid frame posts. The entry, study, hilltop, bake adapter and demo replay checks pass. Desktop and portrait cell, hall arrival and all bank views were inspected. No camera changes were required.
- Stationary desktop demo views pass at 101–143 draw calls, 123,148–163,486 primitives, 66,894,352 bytes (63.80 MiB) of texture allocation and at most four practical lights. Forced-draw medians are 1.28–2.05 ms and p95 intervals 1.98–3.33 ms on this Apple M2 Max. Texture headroom is small; further art needs profiling. These results do not establish full-traversal or phone GPU acceptance.
- The rebuilt pack passes replay and cold desktop launch. The 43.7-second capture, five-file archive and checksums are refreshed. Details: `docs/kits/tech.md`. The full goal remains active: folding chairs, stage variants, remaining site art and dressing, sourced references, final lighting, services and phone acceptance remain open.


## Terminal folding-chair library — 2026-10-04

- Added the terminal sheet’s folding wood chair to the editable prop library, with crossed legs, brass pivots, slatted seat and raked back. LOD0 uses 968 triangles and LOD1 356 (37%). Both share the existing wood/bronze PBR atlas; no new textures or practical lights are needed. The seat anchor is 0.46 m high. Four anchors and two collision boxes match across detail levels.
- Nine-variant export checks and both sampled UV1 overlap checks pass. Godot verifies eighteen prop models, one shared material, twenty-two colliders and no embedded practicals; chair bounds and seat/back ray tests pass at both levels. All 140 GLBs pass structural validation. The other sixteen prop exports remain byte-identical. Close chair views and both refreshed overviews were inspected after correcting render viewport scaling. Blender MCP verifies both saved chair scenes/collections without changing the open scene.
- This is a library pass. Main garden geometry, bakes and packaged demo are unchanged. Six-cell chair placement is next, followed by stage variants, remaining site art/dressing, sourced references, final lighting, services and phone acceptance. The full scene goal remains active.


## Terminal chair placement and release — 2026-10-04

- Replaced six original cell chairs with fitted folding wood chairs, facing the desks and retaining 0.46 m seat height. Seat/window/door markers, lights and unrelated collision transforms remain unchanged. Twelve simplified chair collision boxes are added. The visitor’s standing point moves into the clear gap behind the back (z=37.98 m); seat markers remain at z=37.4 m. The six-chair batch uses 5,808 triangles and the existing shared atlas. Prop placement now totals 38 modules in eight sites/batches.
- All six chairs pass seat-height rays, standing capsule clearance, floor support and clear doorways. The entry route passes outward and return physics traversal; the demo passes through replay. Prop material sharing and UV2 checks pass. The assembly has 157 render meshes and 267,694 triangles; sampled UV2 overlap checks pass and all 140 GLBs pass structural checks. Source SHA256 is `838178b067891de880927663473dedd91ab60dc5bfb03cee6d0680c3677786c4`. Fresh source-matched Cycles coverage is 32/32 demo and 29/29 priority-2 opaque meshes, with compressed 256px runtime lightmaps.
- Desktop and portrait cell/chair views were inspected. Stationary desktop demo profiling passes at 101–144 draw calls, 123,148–168,478 primitives, 66,938,056 bytes (63.84 MiB) of textures and at most four practical lights. Forced-draw medians are 1.47–2.25 ms and p95 intervals 2.41–3.19 ms on this Mac. This does not establish full-traversal or phone GPU acceptance.
- The local pack and 43.5-second capture are rebuilt for this source. Cold-pack replay, desktop launch, archive contents and checksums pass. Stage variants, unlit terminal scrolls and further site art/dressing, sourced references, final lighting, service contracts and phone acceptance remain open. The full goal remains active.


## Stage library pass — 2026-10-04

- Built all seven inventory variants with independent LOD1 companions: three curved painted cycloramas, black studio wall, floor boards, fog plane and gel frame. The editable Blender library contains fourteen module scenes and a showroom. Base geometry uses 200–1,140 triangles; LOD1 retains 36–44% with matching anchors and simplified collision transforms. The floor's walking surface and collider top are at z=0; the fog card is nonblocking at 0.3 m.
- Original 4096px brushwork skies add slate-blue, plum/amber and warm-gray alternatives. A 2048px atlas supplies timber, black, steel and brass. Godot uses unshaded sky materials at a 0.6 multiplier, unshaded black, shared PBR atlas, alpha-blended gel and neutral scrolling fog. Runtime imports use 1024px skies and 512/256px atlas color/ORM with compression and mipmaps. Modules contain no lights; rig positions are connector anchors.
- Export, alpha/PBR, connector, collision-parity and all fourteen sampled UV1 overlap checks pass. Godot checks fourteen models, twenty-two shared material surfaces, fifty-four colliders, bounds, floor height, solid-wall/frame rays and nonblocking fog. All 154 GLBs pass structural checks. Blender MCP confirms fourteen module scenes/collections and the showroom without changing the open scene. Both overviews, three sky views and floor/fog/gel details were inspected; the first render's stretched moon and overlapping label were corrected.
- Details: `docs/kits/stage.md`. This is an isolated library pass: the main garden and current bakes remain at source SHA256 `838178b067891de880927663473dedd91ab60dc5bfb03cee6d0680c3677786c4`; the playable pack is unchanged. Stage placement and budget checks are next. Further site art/dressing, unlit terminal scrolls, sourced references, final lighting, services and phone acceptance remain open. The full goal remains active.


## Stage placement — 2026-10-04

- Placed 35 stage modules: six cell floors, six backstage wall panels, 21 fog cards and two stored gel frames. Six shared render batches use 14,704 triangles. Eight new collision proxies leave the corridor clear; floor rays preserve the original walking height. Lights, triggers and unrelated collision transforms remain unchanged. The hall signs and screens stay unobstructed.
- Assembly: 160 render meshes, 282,284 triangles; 154 GLBs pass structural validation. Source SHA256 is `59bd87306524d62ba7a849e12cccdbead5639ab54faee025493564ac874695ed`. Fresh Cycles coverage is 33/33 demo and 29/29 priority-2 opaque shaded meshes. Unshaded black stage walls and transparent fog/gels do not require lightmaps. Native pixel inspection, source hash and engine bake application pass.
- Stage placement, entry/study/imperial traversal, five backdrop wash receivers and demo replay pass. Blender MCP verifies five saved site scenes/collections without modifying the open scene. Desktop and portrait arrival/action views, floor/chair detail and stored-frame wall were inspected.
- Stationary desktop demo profiling passes at 101–145 draw calls, 123,868–176,110 primitives, 66,850,688 bytes (63.75 MiB) of textures and at most four practical lights. Forced-draw medians are 1.34–2.32 ms; p95 intervals are 2.36–3.40 ms on this Apple M2 Max. Full traversal and phone GPU acceptance remain open.
- Painted cyclorama enclosure fit is next, including curvature and side collider alignment review. The existing circular backdrop remains in place. Unlit terminal scrolls, further site art/dressing, sourced references, final lighting and service contracts remain open. The full goal remains active.
- The rebuilt pack passes cold replay and desktop launch. The 43.5-second video, five-file archive and SHA256 checksums are refreshed for this source.


## Painted stage enclosure — 2026-10-04

- Corrected the kit cycloramas to curve toward the viewer so the painted canvas aligns with the simplified wall proxies. Six rays across both wings pass for all three variants and both detail levels. All fourteen kit exports pass UV2 checks; refreshed library views were inspected.
- Fitted eight moonlit painted arcs around the existing 48 m-radius enclosure, from z=-2 to 20 m. Eight vertex groups keep the panels editable. Their sealed backs and inward painted faces use the shared stage resources. Front UVs exclude the painted moon so the original single physical moon and three mountain flats remain. The original five wash receivers are preserved. Sixty-four separate perimeter proxies pass 120 radial rays. Existing lights, triggers and unrelated collision transforms remain unchanged.
- Assembly: 160 render meshes and 286,604 triangles. All 154 GLBs and sampled assembly UV2 checks pass. Current source SHA256 is `ca9033127e628ed84196989c4bf4ed6b1ac52a081cf2d373302219678e93d22f`. Fresh source-matched Cycles coverage is 33/33 demo and 29/29 priority-2 opaque shaded meshes, with native pixel inspection and runtime bake application passing. The unshaded painted canvas is excluded from the bake.
- Eight graded perimeter inspection views contain no diagnostic background. Normal desktop/portrait demo, study, imperial and hilltop arrival/action views were inspected. Entry, study, hilltop and imperial traversal, stage placement, wash receiver linking and demo replay pass. Blender MCP confirms the saved stage scene with 64 enclosure proxies and the corrected library catalog without changing the user's open scene.
- Stationary desktop profiling passes at 102–146 draw calls, 128,188–180,430 primitives, 56,364,928 bytes (53.75 MiB) of textures and at most four practical lights. Replacing the older backdrop texture saves 10 MiB in the measured demo. Forced-draw medians are 2.64–2.72 ms; p95 intervals are 4.12–5.31 ms on the Apple M2 Max. Full traversal and phone GPU acceptance remain open.
- Unlit terminal scrolls and further site art/dressing, sourced references, final lighting and service contracts remain open. The full goal remains active. Details: `docs/kits/stage.md`.
- The rebuilt pack passes cold replay and desktop launch. The 43.5-second capture, five-file archive and SHA256 checksums are refreshed for this enclosure source.


## Terminal wall scrolls — 2026-10-04

- Fitted one dark calligraphy scroll to the solid wall strip beside each of the six barred terminal windows. The 0.46 m overall width fits the 0.6 m strip and the hanging cord stays below the window head. The material uses a 0.025 glTF base-color factor and reuses the prop atlas textures. It emits no light and adds no practicals or collision. The rendered brightness was reviewed and reduced to keep the CRT and window as the focus.
- Prop placement totals 44 modules in nine material batches, with 3,144 added triangles. The assembly has 161 render meshes and 289,748 triangles. All 154 GLBs and sampled assembly UV2 checks pass. Source SHA256 is `8c837341e293735c695313078c4d2f514c76ea09eba0a39b7be2d5c6f166384a`. Comparison against the preceding committed export preserves all 497 collision/light/trigger nodes exactly. Standard glTF color-factor and shared source texture checks pass.
- Fresh Cycles coverage is 34/34 demo and 29/29 priority-2 opaque shaded meshes. Native pixel inspection and runtime bake application pass. Scroll bounds, zero-emission samples, shared runtime textures, window rays, prop batching and chair seat/capsule/floor/doorway clearance pass. The original chair batch remains 5,808 triangles. Blender MCP confirms the directly openable saved terminal scene, dark material and twelve placed props without modifying the live scene. Source catalog: `export/prop-placements.json`; preservation evidence: `export/terminal-scroll-preservation.json`.
- Stationary demo views pass at 102–147 draw calls, 128,188–183,574 visible primitives, 56,408,632 bytes (53.80 MiB) of textures and at most four practical lights. Forced-draw medians are 1.36–2.03 ms and p95 intervals 2.76–3.32 ms on this Apple M2 Max. Phone and full-traversal GPU acceptance remain open.
- Desktop and portrait scroll/cell/chair views were inspected. Entry traversal, demo replay, packaged replay and cold desktop launch pass. The four demo milestones remain complete.
- The next pass checks the site sheets against their saved scenes and finishes missing dressing. Sourced reference stills, remaining site art/materials/signs, final lighting and service contracts remain open. The full goal remains active.
- The 43.5-second capture, five-file archive and SHA256 checksums are refreshed for this source.

## Saved site source audit — 2026-10-04

- Inspected all 14 saved Blender site libraries against the authoring collections and individual GLB bake eligibility. Structural records (camera/light/collision/trigger transforms and room IDs) and sign implementations match. All 71 markers carry room IDs. Blender MCP independently checked saved catalogs and library hashes without altering the open scene.
- Seven original typeset signs remain: 沁芳, 蘅蕪苑, 怡紅院, 瀟湘館, 櫳翠庵, 凹晶館 and 稻香村. The painted-sign requirement remains open at those sites.
- Six demo/priority-2 sites have 63 source-matched bake records. Eight later sites have no current records for their 55 eligible opaque meshes. This report checks metadata and file presence, not pixel quality or runtime application.
- Added a reproducible read-only scene inspection in `scripts/audit_site_sources.py`, detailed evidence in `export/site-source-audit.json` and the next work order in `docs/site-source-audit.md`. Scene sources, canonical GLB, bakes and playable pack remain unchanged. The full goal remains active; this structural audit does not establish final site acceptance.

## Painted garden titles and clear mounts — 2026-10-04

- Replaced the seven remaining Songti titles with original brush-lettered gold textures: 沁芳, 蘅蕪苑, 怡紅院, 瀟湘館, 櫳翠庵, 凹晶館 and 稻香村. All 14 saved site libraries now contain no temporary FONT signs. Full-resolution source artwork, exact characters and provenance are in `textures/decals/garden-signs/README.md`; these are production textures, not historical references.
- Arrival/detail renders exposed four roof-intersecting boards and the pavilion board behind its front post. Five boards now project forward on two short wood brackets each. Cameras, collision, triggers and lights remain unchanged: all 537 corresponding exported node records and the punctual-light records match the prior assembly. Editable sources, site exports and runtime GLB are synchronized. Blender MCP checks all saved catalogs/hashes without changing the open scene.
- The seven transparent title surfaces use compressed mipmapped 512px imports and a 28 m draw distance. This resolves an initial 152-call terminal view; the wood boards remain in their site batches. The reflection hall title is included in its pond capture. All 28 desktop/portrait sign arrival/detail views and twelve demo views are refreshed. Inspection cameras stop before capture and preserve horizontal framing.
- Current assembly SHA256: `0a697db4e396c3ee422838feafb0d6a438ac70186d7761e469d11366d25e1ea0`. There are 166 render meshes and 231,216 triangles, 58,532 fewer triangles than the previous assembly. All 154 GLBs pass structural validation, and sampled UV2 checks pass for all 166 meshes. Source-matched Cycles coverage is 33/33 demo and 29/29 priority-2 eligible meshes. The pavilion's bronze glyph batch was removed; its transparent title keeps the source material. Native pixel checks and runtime bake application pass.
- Entry, courtyard, red court, bamboo court, nunnery, reflection hall and farmhouse traversal checks pass. The final pavilion mount is rechecked through entry traversal, reflection inclusion, bake application and cold-pack first-reading/replay. Original collision records are unchanged.
- Stationary desktop profiling passes at 102–146 visible draw calls, 123,740–177,088 visible primitives, 57,249,840 bytes (54.60 MiB) of textures and at most four practicals. Forced-draw medians are 2.18–6.50 ms and p95 intervals 3.61–8.63 ms on this Apple M2 Max. These are stationary Mac measurements; full traversal and phone GPU acceptance remain open.
- The local pack and 43.5-second capture are rebuilt. The next scene pass reviews the reflection hall's water-dominant composition and remaining site materials before baking the 55 eligible meshes across eight later sites. Sourced references, final lighting, service contracts and full acceptance remain open. The full goal remains active.
- Final release verification: cold desktop launch, cold-pack first-reading/replay, 43.466667-second movie, exact five-file archive contents and SHA256 checksums pass for this assembly.


## Reflection hall runtime framing — 2026-10-04

- Replaced the distant off-centre arrival shot with a centered wider desktop view shared by the pond action. The full roof and reflected amber window remain above the controls. Portrait has a separate closer downward view, reducing empty sky; the next room restores the default FOV.
- Refreshed six desktop/portrait views and four fixed-time comparison captures. The comparison verifier uses the projected pond quad instead of old hardcoded screen rows. It checks unaffected scene pixels and HUD text/buttons/input while allowing the pond to show through the translucent panel background.
- Deterministic comparisons report 85,856 changed pixels when reflection is disabled, 1,161 when only the reflected window is excluded, and 4,272 when ripple time advances. Desktop and portrait capture projection checks pass. The guarded approach and return, floor support and closed-door collision pass.
- Stationary Apple M2 Max desktop profiling reports 13 capture draws, no capture shadow draws, 59,165,348 bytes of texture allocation, and 8.406 ms median frame interval active versus 8.133 ms frozen. This is not full traversal or phone GPU acceptance.
- Geometry, Blender cameras and source-matched bakes are unchanged. Source camera alignment, final water-dominant establishing composition, later-site materials/lighting, references and full acceptance remain open. The goal remains active.


## Reflection hall source camera alignment — 2026-10-04

- Stored the reviewed desktop shot in the two existing hall cameras and added a portrait camera. The editable library contains 1410 × 600 landscape and 390 × 844 portrait scenes sharing one collection. Blender MCP confirms the saved catalog and hash without changing the open scene.
- The glTF exporter preserves each camera's viewport and projection. Godot reads the imported transform and FOV instead of keeping a separate pose. The alignment test compares window/pond screen coordinates in both aspects, mirrored projection and the next site's default FOV restoration.
- Source SHA256 is `4755afea99f052791f9906c7b27d3108d4929fa13bba8c3ad3a0c751edf0846b`. Binary geometry/image data, all mesh/material/texture/accessor records and 497 collision/trigger/light records match the predecessor. The source-library audit now compares camera lens, sensor, clipping and viewport metadata too.
- All 154 GLBs pass structural checks; all 166 assembly meshes pass sampled UV2 overlap checks. Refreshed 33 demo and 29 priority-2 bakes are source matched, have finite nonzero native pixels and apply in the runtime. Reflection traversal, source camera agreement and project/pack first-reading plus replay pass. Fixed-time comparisons change 85,856 pixels with reflection disabled, 1,161 with its window excluded and 4,273 with ripple time advanced; non-pond pixels and HUD text/buttons/input remain stable.
- The demo pack is rebuilt and its cold desktop launch passes. The existing demo video remains valid because its scene geometry, image data and camera views are unchanged. Final water-dominant composition, later-site materials/lighting, reference collection, service contracts and phone/full-traversal acceptance remain open. The goal remains active.

The latest source audit totals **54** eligible meshes without current bakes across eight later sites. The previous JSON audit also totals 54; earlier prose saying 55 was a counting error.

Final import evidence: 166 render meshes, 392 collision shapes, 71 room markers and 41 cameras. The five-file local release archive is rebuilt and every archived checksum verifies.


## Water-dominant pond viewer — 2026-10-04

- The pond action opens a fixed waterline view with a Return to ledge button and Escape support. The visitor stays on the dry ledge. Desktop/portrait resize selects the matching authored shot; closing restores the arrival view and a fitted command panel. Eight arrival/door/pond/return renders are reviewed.
- Actual depth-tested raster coverage is 54.9% water on desktop and 57.0% in portrait; all roof vertices are in frame. Authored pond cameras sit 0.6 m above the water. The saved library contains four cameras and four scenes. Blender MCP checks the saved catalog/hash while keeping the open scene unchanged.
- Source SHA256 is `13d247b4ffc4588e23fb795d8d0d431ebee0213271cd92d0347616485ab5c257`. All non-camera node records, scene membership, binary geometry/images, material/texture/accessor records and light records match the previous export. Existing 62 lightmaps are retained with original bake provenance and a hashed compatibility proof; they are not newly rendered bakes. Negative checks reject mesh transform, light, material and binary edits without altering the proof. Native PNG hashes and runtime copies match.
- Pointer entry/return, Escape, resize, authored projection, dry-ledge position, fitted restored controls and next-room cleanup pass. Reflection traversal and arrival-camera agreement pass. Fixed-time comparisons change 460,098 pixels with reflection disabled, 7,027 with only the reflected window excluded and 94,863 with ripple time advanced; changes stay inside the near-plane-clipped pond region and the return button remains stable. All 154 GLBs and 166 sampled UV2 meshes pass. All fourteen saved libraries match source structural/projection records. Import contains 392 collision shapes, 71 markers and 42 cameras.
- The stationary desktop pond profile reports 832 combined draws, 115,470 combined visible primitives and 58,990,586 bytes of texture allocation, with 7.312 ms median frame interval active versus 6.301 ms frozen. The draw count exceeds the 150-call target. A temporary diagnostic isolates static shadow cost: the reported main counter is 819 normally and 92 with static-key shadows disabled; disabling keys entirely also gives 92. Eleven of twelve static keys overlap baked receiver layer 2. These toggles are not saved scene behavior.
- Next: fix static-key receiver isolation, finish later-site lighting/bakes, and remove redundant static shadow work while retaining the set's hard shadows. Final lighting/material/reference acceptance, service contracts, full traversal and phone GPU checks remain open. The goal remains active.
- The final exported pack passes the pond pointer/keyboard/resize test and a cold desktop launch. Project and pack first-reading/replay checks pass. The rebuilt five-file demo archive passes CRC checks and all four payload SHA256 checks.

## Static-key isolation probe — 2026-10-04

- The pond-view release is committed and pushed as `7ef5140`; its exported pack and archive passed controls, replay, cold launch and checksum checks.
- A temporary runtime probe cleared baked receiver layer 2 from static Spot/Directional lights. The 33-map source/material/layer test and shared ORM prop adapter test passed, including practical light and linked backdrop masks.
- Desktop study, imperial and offline hilltop captures completed. Comparing the imperial view against the saved release showed loss of roof and bronze-door visibility. The probe and replacement site references were reverted; three diagnostic captures are retained separately. No production light masks or shadows changed.
- Next: calibrate authored keys and fresh bakes to retain detail before installing static receiver isolation. Remaining later-site bakes, final colors and references, full traversal/phone performance and service integration acceptance keep the goal active.

## Cycles diffuse transfer correction — 2026-10-04

- The static-key darkness investigation found a transfer mismatch, rather than a missing bake pass. Cycles bakes direct and indirect diffuse without material color and returns 0.318303 under unit sunlight. Compatibility dynamic lighting on a gray plane gives display RGB 0.501961; the old bake shader gives 0.152941. Multiplying only baked diffuse by π gives 0.498039. The all-channel regression was observed failing before the correction and passing afterward, including the imported fixture resource.
- Static Spot/Directional keys now exclude baked receiver layer 2. Practical lights retain layers 1+2 and the backdrop wash retains layer 4. Separate shadow-caster masks are preserved. The adapter contract was observed failing before isolation and passing afterward; the shared ORM/emission material and warm study light checks also pass. Existing GLB, Blender files, lightmaps and source-provenance records are unchanged.
- Corrected isolated imperial captures preserve roof and door detail. Desktop and portrait study, imperial, hilltop, reading-table, pond and complete first-reading demo captures finish. Offline first-reading/replay, reading-line state, pond controls and imperial physics traversal pass. Actual graphical pointer/keyboard demo acceptance passes.
- Stationary desktop demo profiling passes: maximum draws 146/140/102 for cells/gate/pavilion; 57,249,840 texture bytes; at most four active practicals. Pond profiling reports 785 combined draws and 58,990,586 texture bytes; its 150-draw target remains unmet. Final materials, bake noise/density, later-site bakes, sourced references, full traversal, phone GPU and service acceptance remain open. The goal remains active.
- Exported-pack verification caught a test-harness startup race: the terminal button moved from y=465 to y=502 between the initial process frame and the first draw. The pointer helper now waits for `frame_post_draw` before reading the actual visible button bounds; it still dispatches real pointer events. No production UI behavior was changed for this race.
- Final project and pack graphical input/replay checks pass with visible button coordinates. The final pack also passes the transfer fixture, retains the verified pond controls, and launches cold. The updated H.264/AAC movie is 1410×600 and 43.466667 seconds. The rebuilt five-file archive passes CRC checks and all four payload SHA256 checks.


## Complete static bake coverage — 2026-10-04

- Rendered 62 additional native Cycles maps at 128 samples: 54 later-site meshes and eight shared stage meshes. All 124 current eligible meshes pass source-hash, UV channel, finite/nonzero pixel and identical engine-copy checks. Fourteen saved site libraries still match the authoring structure; all 116 eligible site meshes have current records. Source geometry, cameras and lights are unchanged.
- Normal exploration applies the full compressed 256-pixel catalog. Static Spot/Directional keys now use primary receiver layer 1; clearing only layer 2 allowed reflection/wash bits to admit duplicate lighting. Exclusive wash layer 4 and practical layers 1+2 remain intact. Mesh reflection/wash bits and shadow-caster masks are preserved. Static shadow maps are disabled. Full-route and demo adapter checks pass.
- Baked materials now retain normal textures and depth. The side-light rendered fixture reports 0.439216 mapped versus 0.301961 flat/zero-depth. The unit-light diffuse transfer check still passes. The water/fog test now checks the current shared stage fog and reflective pond shaders after full-route bake application instead of expecting the removed legacy fog material.
- Refreshed all 28 desktop/portrait arrival captures. Stationary desktop pond rendering reports 105 combined draws, 115,470 combined visible primitives and 63,142,466 texture bytes. All fourteen desktop arrival views have at most 146 combined draws and 63,233,940 texture bytes; portrait views have at most 98 draws and 56,513,880 bytes. Both retain at most four active practicals. These are Apple M2 Max stationary-view measurements, not phone or full-traversal GPU acceptance.
- Final color/material, bake noise/texel-density and external reference reviews remain open. The linked backdrop wash remains dynamic because glTF omits Blender Area lights; final baked-wash acceptance remains open. Service contracts and phone/full-traversal acceptance remain open. The full goal remains unfinished.

- Release checks caught an intermittent test-harness startup click failure and a draw-signal wait that remained suspended while physics continued. The pointer helper now requires stable bounds across forced draws and sends its motion with both button edges. Project and final-pack full pointer/keyboard replay pass. Production controls are unchanged. The final pack also passes all 124 receiver checks, pond pointer/keyboard/resize controls, the diffuse fixture and normal-response fixture.

- Automatic movie attempts completed the route but recorded too few frames; those captures were rejected. The optional native frame-sequence capture saves every fixed-time frame, and the assembler requires a contiguous complete route and all six cues. The replacement H.264/AAC movie is 1410 × 600, exactly 43 seconds and 1,290 frames at 30 FPS. Audio uses the original PCM at recorded cue transitions with runtime gains and loop/stop rules. The timeline, source hash and movie hash are recorded in `docs/reference/demo-capture-timeline.json`.

- The final exported pack passes real pointer/keyboard replay and cold launch after the capture-tool update. The refreshed five-file local archive passes CRC and all four payload SHA256 checks. Temporary diagnostics and native frame sequences remain outside the repository.


## Native shared-stage wash — 2026-10-06

- The separate Cycles pass reconstructs the saved Area light omitted by glTF and verifies world bounds against all five canonical receivers. It isolates that light from the world, keys and emissive geometry. The real building control receives zero direct wash.
- Final output is nine front/back PNGs at 512² and 128 samples. Double-sided mountain cards face outward; the camera sees their backs. Temporary face reversal preserves exact UV-to-vertex mapping. The outermost layer is fully shadowed; its isolated inward-face control receives light. The middle layer is mostly shadowed, with a small nonzero final peak. Hash-checked installation retains the unchanged canonical GLB and saved Blender library. A stale-stage negative check leaves all engine files unchanged.
- Normal exploration and demo startup apply the wash without a realtime wash light. The demo also retains the four ordinary painted-flat stage maps. Source material properties are preserved. Image review caught loss of the unshaded sky base; the native rendered check fails without preservation and passes with identical original/converted RGB (0.298, 0.4, 0.502). Front/back selection and additive lighting checks pass at RGB 0.498/0.0/0.498.
- Refreshed all fourteen desktop and fourteen portrait arrival captures. Reviewed pavilion, hilltop and pond images, including portrait pavilion/hilltop. These checks do not certify final color, noise, every seam or continuous camera motion.
- Actual exported-pack pointer and keyboard entry-to-replay acceptance passes. Both demo and normal-route wash checks, the 124-receiver static lighting check, and material/startup checks pass. Stationary demo profiling retains at most 146 draws, 177,088 visible primitives, four practicals and 57,817,992 texture bytes. The production pond remains at 105 combined draws, zero shadow draws and 63,535,802 texture bytes. These are desktop Mac measurements.
- This pass transfers the existing single shared stage wash. The saved-rig audit confirms all fourteen sites lack the specification's per-site washes. Final color/materials, texel density and noise, external references, full traversal, phone hardware and service contracts remain open. The full goal remains active.

- Final pack source-manifest fallback, normal/demo wash and full static receiver checks pass; packed pond pointer/keyboard/resize checks pass. Rebuilt the native 1,290-frame, 43-second H.264/AAC capture and five-file local archive. Video/audio dimensions, frame count, CRC and four archived payload hashes pass. Capture metadata now includes the wash manifest and shader hashes as well as the GLB, pack and movie hashes.

- The traversal harness now uses production maps instead of reapplying a stale experimental catalog, and forces capture draws instead of waiting indefinitely for a post-draw signal. Its ten actual walking legs pass destinations, floor support and the four-practical limit. Sampled captures remain a subset of the full garden route; they do not establish continuous-motion or phone acceptance.


## Twelve exterior-site backdrop washes — 2026-10-07

- Added twelve saved 150 W, 15 × 10 m Area lights aimed along each exterior site’s establishing camera toward the painted enclosure. Eleven use neutral gray-blue, Qinfang faint neutral green, following the reduced-green revision. The old 1,800 W shared wash is disabled. Detailed sheets retain two exceptions: terminal cells borrow window spill and the tunnel has no wash. All twelve linked-master lights reference the same five visible stage object IDs. Source scripts: `author_site_washes.py`, `package_site_washes.py`; rig record: `export/site-wash-rig.json`.
- Native export to a temporary root matches the canonical master and all fifteen site/stage GLBs byte for byte. Existing geometry, collision, cameras, materials and punctual lights are unchanged, so the 124 ordinary maps remain current. All fourteen saved site libraries match authoring structure with zero differences and current sheet hashes. Blender MCP verifies twelve saved site lights and matching library/authoring hashes without modifying the open scene.
- Baked combined native direct diffuse at 128 samples, 512²: five receivers, nine front/back textures. Building direct control is zero; isolated outer mountain inward control is 0.168890, middle mountain peak 0.002963. Hash-checked installation now requires authoring, stage and twelve site-library provenance as well as canonical GLB and PNG hashes. Stale authoring/site negative checks reject both inputs and leave all 25 installed files unchanged. Engine import settings retain compression and 256px caps.
- All fourteen desktop and portrait arrival views rendered; contact sheets and pavilion, hilltop and terminal details were inspected. Sky is more slate-blue, amber practicals remain, and mountain flats/buildings still need color and filtering work. Several portrait views show the enclosure’s upper edge; final framing remains open. No final art acceptance is claimed.
- Rebuilt pack passes normal/demo wash checks, 124-receiver lighting and material/mask checks. The adapter test initially failed in the pack because it tried to hash the omitted raw GLB; using the existing production raw-source/manifest validator passes in project and pack while retaining stale-record rejection. Actual packed pointer/keyboard demo replay and pond entry/return/Escape/portrait resizing pass.
- Stationary demo measures 102–146 visible draws, 123,740–177,088 primitives, at most four practicals and 57,817,992 texture bytes. Forced-draw medians are 1.209–2.129 ms, p95 2.299–2.486 ms on this M2 Max. These measurements do not establish phone or full-traversal performance.
- Refreshed the native 1,290-frame, 43-second H.264/AAC capture, source/pack/movie hashes and five-file local archive. Codecs, 1410 × 600 dimensions, 30 FPS, frame count, CRC and all four archived payload hashes pass. Desktop demo stills come from the current frame sequence.
- Three owned keys remain: Qinfang Pavilion, Ouxiang water pavilion and Ziling reed island. The new wash transfers direct backdrop light only; terminal indirect window spill is not yet baked or verified. Complete those lights/spill with affected ordinary rebakes, then continue palette/materials, noise/texel density, external references, full traversal, phone hardware and service contracts. The full goal remains active.


## Three owned keys and neutral shared fill — 2026-10-07

- Added Qinfang’s Sun (0.6 energy, 35° southeast, 0.5° source) and hard Spot keys for Ouxiang’s tea table (450 W) and Ziling’s reeds (400 W). Shared green fill becomes neutral cool RGB (0.70, 0.74, 0.78), energy 1.4. CRTs, amber practicals, all other keys and twelve Area washes retain their saved settings. Native key check failed on missing Qinfang before implementation and passes for all three after saving. Blender MCP verifies the three names in saved site libraries without altering the open scene.
- Four changed standalone libraries are packaged; linked master still resolves all twelve washes to the same five visible stage receiver IDs. The new canonical export is `d74e0ff858748d529029c80f0ea11969c121dd71f645effebf55180104099bde`. Binary mesh/image buffer and mesh, material, image, texture, camera data are identical to the prior export; 33 unrelated punctual-light records are identical. Preservation evidence: `export/site-key-export-preservation.json`.
- Saved rig audit has no missing required keys or washes, retaining the terminal and tunnel exceptions. This inventory does not establish final lighting acceptance. Added Sun/shared fill changes require all 124 ordinary maps to be rebaked; no old record is relabelled compatible. `refresh_full_lighting.py` runs ordinary maps at 128 samples, up to 1024², native wash maps at 128 samples/512², native PNG inspection and complete current-source coverage checks sequentially. Its live phase/log records are in `export/full-lighting-refresh.json`.
- The source refresh finished: all 124 ordinary maps were freshly rendered at 128 samples, the wash at 128 samples/512², and native pixels plus complete current-source coverage passed. Current GLB and identical maps are installed in Godot. All fourteen saved libraries have zero structural differences and matching final sheet hashes. No current ordinary record uses camera-only revalidation.
- Project checks pass for the three imported keys, all 124 static receivers, normal/demo wash, material/masks, water/fog and demo replay. Western physics traversal passes in both directions with floor support. The final pack passes the same seven lighting/startup checks, real pointer/keyboard replay and pond controls. All fourteen desktop/portrait arrival views and six desktop/portrait demo views are refreshed.
- Current stationary demo profile reports max 146 draws, 177,088 primitives, four practicals and 57,817,992 texture bytes. Forced-draw medians are 1.705–2.176 ms, p95 5.335–5.641 ms. The top 360 rows of three unchanged arrival cameras have 13–20% less mean positive green excess than the preceding pass; this display metric is not final color acceptance. Roof undersides, green/checkered mountain flats, stretched moon framing and portrait enclosure edges remain visible art issues.
- Rebuilt native capture has 1,290 frames at 30 FPS, exactly 43 seconds, H.264/AAC at 1410 × 600. Current source, pack, wash and movie hashes are recorded in the timeline; the five-file archive passes CRC and four payload hash checks. One attributed, licensed Qinfang architecture photo is collected; its two film references remain missing. Terminal indirect window spill, final shadow/palette/material/filtering work, references, phone/traversal and service acceptance remain open. The full goal remains active.


## Native terminal window spill — 2026-10-07

- Added seven independent Cycles indirect maps from the saved twelve exterior Area washes. Sampling is fixed at 2,048 samples/512² with adaptive sampling and guiding disabled. Ordinary maps, source geometry, cameras, materials and saved lights are unchanged. Every cell receives positive window-only indirect light; direct, windows-and-doors-sealed and all-washes-off controls are zero. Production bakes retain the actual open rooms.
- Native 16-bit PNGs are normalized by their physical maxima, including scales below one, so compressed engine maps retain the faint signal without a brightness gain. All seven native readbacks decode to their recorded physical maxima. Installer checks complete source, UV and PNG provenance before copying. Five invalid-source/map cases reject while all 23 installed files remain unchanged.
- Normal exploration and the demo add the indirect term once to the existing base bake. All seven terminal materials retain base textures, normal/ORM maps, emission and receiver masks. No direct backdrop wash or new realtime light reaches the cells. The rendered combined-energy fixture fails with the indirect term removed and passes with normalized scale restored; its display RGB is 0.502 against the 0.498 unit reference.
- Project and final exported-pack checks pass for normal/demo spill, all 124 ordinary receivers, direct wash isolation, keys, material adapters, animated surfaces and startup. Actual packed pointer/keyboard demo replay and pond controls pass. The pond test now waits for stable drawn bounds after resizing; production pond behavior is unchanged. All fourteen desktop and portrait arrival captures and six demo views are refreshed.
- Current stationary Mac demo profile records maximum 146 draws, 177,088 primitives, four practicals and 58,123,920 texture bytes (55.43 MiB). Forced-draw medians are 1.833–2.720 ms and p95 3.960–6.271 ms. Source, indirect-manifest and shader hashes are recorded. These are stationary desktop intervals, not continuous traversal or phone measurements.
- Rebuilt capture contains 1,290 native frames at 30 FPS, seven cue transitions, exactly 43 seconds and H.264/AAC at 1410 × 600. Current source/wash/indirect/shader/pack/movie hashes are in `docs/reference/demo-capture-timeline.json`. The five-file local archive passes CRC and all four payload hashes. Evidence is in `export/terminal-spill-runtime-checks.json`.
- Lighting transfer is implemented; final art acceptance remains open. Dark roof undersides, mountain-flat color/checker patterns, moon shape and portrait enclosure framing still need work, as do reference collection, final texture/filtering audits, full traversal, phone hardware and service contracts. The full goal remains active.


## Smooth painted-mountain gradients — 2026-10-07

- Temporary native Godot comparisons isolated the regular mountain checker pattern to DXT1 texture compression: same-resolution uncompressed native maps remove it. The actual portrait-region regression fails before the fix (RMSE 0.019418 against 2/255). BPTC passes but this Mac decodes it to RGBA8; production therefore imports only the nine mountain maps losslessly at the unchanged 256px cap. Final regression passes at RMSE 0.002240 with no unsupported-format warning. All native PNGs, UVs, scales, source geometry and lights are unchanged. The import configuration script retains this exception on future refreshes.
- Stationary demo budget passes at 60,089,871 texture bytes (57.31 MiB), an increase of 1,965,951 bytes; maximum draws/primitives/practicals remain 146/177,088/four. Cell/gate/pavilion median intervals are 6.299/5.477/2.827 ms and p95 8.711/7.889/7.047 ms. Nine import hashes identify the exact runtime settings. These are desktop measurements; whole-garden final memory and phone performance remain open.
- Final pack passes all lighting/material/startup checks, actual pointer/keyboard replay, pond controls and energy-transfer fixtures. All fourteen desktop/portrait arrival views and six demo views are refreshed. Inspected portrait Qinfang and desktop hilltop: broad mountain gradients are smooth; residual green, roof darkness, moon shape and enclosure framing remain art work.
- The current native capture has 1,290 frames at 30 FPS, seven cue transitions, exactly 43 seconds and H.264/AAC at 1410 × 600. Source/import/manifest/shader/pack/movie hashes are recorded in the timeline; exact five-file archive, CRC and four payload hashes verify. Evidence: `export/mountain-filtering-checks.json`, `export/mountain-filtering-runtime-checks.json` and `export/mountain-lightmap-filtering.json`.
- Source inspection found the mountain materials still emit their original green despite earlier base-color reductions. Correcting the saved material colors and paint texture requires affected fresh bakes, rather than an engine-only recolor. Continue that art pass, final texture/filtering/seam acceptance, external references, full traversal, phone hardware and verified service integration. The full goal remains active.

## Mountain paint source; lighting refresh in progress — 2026-10-07

- Saved three textured slate-blue mountain materials and their primary UVs in authoring and the stage library. One original 4096² atlas supplies color and emission at strength 0.6. Native checks retain mean emitted luminance within 3.4% of the predecessor and preserve 4,344 scene objects and 44 unrelated materials.
- New canonical source is `b4b322c2f15b698f1aacf348c27e9734bf21f94d1e540417309b23a5870bbfc4`. Export comparison checks expanded indexed triangles to permit only the three new primary UV channels; geometry, secondary UVs, nodes, lights, cameras, collisions and unrelated materials/images are preserved. All fourteen other site GLBs are byte-identical. Corrupted camera, unrelated material, mountain secondary-UV and wrong paint-band cases reject. Sampled secondary-UV coverage passes for 166 render meshes with no interior overlap at 512²; gutters and subtexel behavior remain a separate acceptance item.
- Full native lighting refresh is running for all 124 ordinary maps, direct backdrop wash and terminal indirect spill. Engine installation remains separate. Godot and the existing package still use the preceding `d74e0ff…` source. No new runtime color, texture budget or final art acceptance is claimed.
- Isolated native Godot headless transfer checks now pass: all three painted stage layers share one material and one lossless mipmapped 512px painting; color/emission textures and the 0.6 multiplier survive the baked adapter. The check failed before the texture cap. The updated import hook requires source paint metadata; a separate preceding-stage check proves its bare materials and original linear emitted colors remain. Headless contracts do not establish GPU allocation or rendered color. Evidence: `export/mountain-paint-runtime-transfer.json` and `export/mountain-paint-staged-checks.json`.
- A broader isolated source import reports rejected equal inner/outer cone angles on `LGT_ouxiang-xie_key` and `LGT_ziling-zhou_key`. This is an existing source issue, separate from mountain paint. Source correction and actual reimport checks remain required after the locked lighting refresh; `export/spot-cone-import-diagnosis.json` records the two exact light records. No complete reimport acceptance is claimed.
- A native-precision CPU diagnostic of the preceding matching pavilion source/lightmap finds zero irradiance at approximately 97.5% of sampled downward roof triangle centroids and 29.9% of upward centroids. Shading normals agree with geometric winding at those samples, and the atlas has no additional base-color multiplier. These samples omit visibility, filtering, realtime practicals and tone mapping; they guide the next native lighting investigation and do not establish a final roof fix. Evidence: `export/pavilion-roof-source-diagnosis.json`.
- The full goal remains open for final site art, external references, complete texture/reimport acceptance, continuous traversal and target-phone performance, and authenticated room services.

## External architecture references — 2026-10-07

- Collected two unmodified site-specific photographs by 刻意: Daguanlou and Yihongyuan in Beijing Daguanyuan, dated 20 December 2010 and published under CC BY-SA 3.0. Source pages, author, license, exact original checksums and visual notes are recorded in `docs/reference/external/daguan-lou/` and `docs/reference/external/yihong-yuan/`. Both original files match the Commons imageinfo SHA-1. Their site sheets now identify the architectural slot and the two remaining reference slots.
- Together with the preceding Qinfang covered-bridge photo, collected coverage is three of 42 references across fourteen sites. `scripts/audit_external_references.py` checks unique slots, attribution metadata and local original-byte hashes; `--require-all` correctly rejects the incomplete collection. The coverage report is metadata evidence, not a replacement for direct relevance review.
- Visually rejected the two daylight forest stills in Celestial's Magic Blade article for cave/night-set slots. The Kaohsiung Film Archive April 2018 catalogue cover and Come Drink With Me page were rendered and inspected: a festival montage and a courtyard fight do not supply the specified bridge-pavilion image. Those candidates are documented and do not increase coverage.
- The saved fourteen-library source audit is refreshed after the two site-sheet edits; structural contracts remain unchanged. Its current bake counts reflect an in-progress native refresh. Reference collection, final art and full-goal acceptance remain open.


## Painted mountain source installed — 2026-10-07

- The full locked refresh completed at source `b4b322c2f15b698f1aacf348c27e9734bf21f94d1e540417309b23a5870bbfc4`: all 124 ordinary maps, nine front/back wash maps and seven terminal indirect maps were freshly rendered. Native pixel and complete-coverage checks pass. Complete catalogs and the exact source are now installed in Godot; the earlier bake report retains its source-only installation boundary.
- The complete imported scene passes the three-band shared-paint contract, normal/demo lighting, material-transfer, surface and demo-startup checks. The portrait mountain filtering regression passes. Stationary Mac demo profiling records 61,138,446 texture bytes (58.31 MiB), at most 146 draw calls, 177,088 primitives and four practicals; median forced-draw intervals are 1.881–2.688 ms, p95 4.152–4.711 ms. The source painting and its import settings are hashed in the profile. This is stationary desktop evidence.
- Current desktop and portrait arrival views are refreshed for all fourteen sites. The portrait contact sheets and Qinfang detail were reviewed: the mountains are cooler slate-blue; roof darkness and the exposed enclosure edge remain visible. A fixed 100 × 35-pixel portrait mountain region has 73.3% less mean positive green excess than the preceding source. This narrow display metric does not establish whole-scene palette acceptance.
- Initial complete-source glTF import still logs the two known equal-cone light errors. Runtime key-presence checks pass, but they do not prove correct cone properties; complete reimport acceptance remains open.
- The dark Qinfang roof is now traced to an outward-orientation defect: all 25 upper-shell faces point downward in saved authoring; the reusable hexagonal/square shells fail at 25/25 and 17/17 faces. Actual Godot orientation/irradiance overrides show the same visible slopes. In-memory correction passes while retaining positions, face/vertex UVs and transforms. No corrected roof source or bake is claimed. Evidence: `export/pavilion-roof-render-diagnosis.json`, orientation reports and `docs/kits/pavilion.md`.
- The full goal remains active for the roof/spot corrections, remaining art and camera work, references, complete texture/reimport acceptance, continuous traversal/phone profiling, and authenticated room services.

The painted-source exported pack passes its material/lighting/startup checks, actual pointer/keyboard replay, pond controls and transfer fixture. Native capture has 1,290 frames at 30 FPS and seven cues; assembled H.264/AAC movie is 1410 × 600 and 43 seconds. Exact five-file archive, CRC and four payload hashes pass. Timeline records the new source, source paint/import settings, wash/spill, shader, pack and movie hashes. Current evidence: `export/mountain-paint-runtime-checks.json`. Original cue PCM is mixed at the recorded runtime transitions; this is not a native audio capture.


## Saved roof and strict Spot correction — 2026-10-08

- The Qinfang upper roof shell and both reusable roof/LOD sources now face outward. Native checks pass for the placed 25-face shell and all four kit meshes (25 hexagonal/17 square faces each). Source authoring preserves positions, face/vertex UV ownership, material assignments, transforms, camera/light contracts and all unrelated objects.
- Ouxiang and Ziling retain their 65° cones, energy, direction, color and 0.01 m shadow source radius. Their edge blend is now 0.0001, yielding a 0.00325° glTF edge band so inner angles are strictly smaller than outer angles. Native authoring defaults and kit generation retain these corrections.
- Canonical assembly is `90c4f70e5b56fbe4c4e0ef2733057bbf962d21b0187601d7e2fcd6a857574df3`. Export preservation checks pass for the assembly, three affected site exports and four roof/LOD exports; twelve unaffected site exports are byte-identical. The LODs retain identical vertex/UV data and bidirectional planar surface coverage despite alternate diagonals. The largest normal difference after inversion is 0.00009935; the finite 0.0002 tolerance applies only to an actually retriangulated LOD. Ten injected camera/light/material/position/UV/normal corruptions reject. Kit triangle/connector/collision/PBR checks and sampled UV2 overlap checks pass.
- An isolated cold Godot 4.7.2 import finishes with zero errors or warnings. Actual imported Spot half-angles are 32.5°, cone attenuation 1999.568, distance attenuation 2, preview energy 1.8, range 14 m and shadows enabled. The strengthened test distinguishes cone-edge attenuation from distance falloff. These checks establish valid source import, not final rendered acceptance.
- A fresh locked lighting refresh is running for all 124 ordinary maps (128 samples, maximum 1024²), backdrop wash (128 samples/512²) and terminal indirect spill (2048 fixed samples/512²). Production Godot and the playable package retain the preceding complete `b4b322c2…` source and lighting. No old maps are relabelled compatible with the changed roof/UV2 source. Final rendered roof acceptance and runtime installation follow complete fresh-map verification.
- Evidence: `export/roof-cone-authoring-{source,kit}.json`, current orientation reports, `roof-cone-export-preservation.json`, `roof-cone-export-rejections.json` and `roof-cone-runtime-checks.json`. Full goal remains active for final art/material/camera work, references, complete reimport/texture acceptance, traversal/phone performance and authenticated room services.


## Close foliage references — 2026-10-08

Three directly reviewed original photographs now fill the distinguishing foliage/material slots: five-petal Prunus mume blossoms for Longcui, common-reed stems/leaves/plumes for Ziling, and the lotus leaf surface/edge/veins for Ouxiang. Attribution, licenses and original-byte SHA-1/SHA256 checks are saved beside each image. These are design references; none is installed as a scene texture or counted as a night-lighting/architecture reference. External coverage is now 6/42; 36 references remain. Current source lighting refresh remains independent.


## Hilltop architecture reference — 2026-10-08

A directly reviewed original photograph of the Beijing reconstruction's hilltop hall now fills Tubi Tang's architecture slot. The visible plaque reads 凸碧山莊; the image shows an elevated frontage, gray tiled eave, painted brackets, columns, low rail and lanterns. Attribution, CC BY-SA 3.0 and original-byte checksum proof are saved under `docs/reference/external/tubi-tang/`. This close upward view does not supply surveyed heights, stair geometry or night lighting. Reference coverage is 7/42, with 35 still missing. A different double-tier Dicuiting pavilion candidate was reviewed but not counted for the open water-pavilion requirement.


## Repeatable source import and bamboo reference — 2026-10-08

Two forced cold imports of corrected source `90c4f70e…` pass against an independent glTF contract: 42 camera transforms/projections, 392 collision surfaces/transforms, 71 room-marker transforms/metadata and identical snapshots of all 166 render meshes. Every collider passes an isolated physics ray in both imports. Calibrated keys and the shared painted material/adapter contract also pass. Three actual camera/collider/marker corruptions reject. These isolated checks leave the production cache intact and do not establish final baked lighting, rendered material acceptance, continuous traversal or phone performance. Evidence: `export/godot-reimport-checks.json`.

A directly reviewed bamboo culm photograph now fills Xiaoxiang’s close foliage/material slot. Source, CC0 1.0 credit and verified original checksums are recorded in `docs/reference/external/xiaoxiang-guan/`. External coverage is 8/42; 34 references remain. Source lighting continues under the same locked worker; engine installation awaits complete fresh maps.


## Entrance inscription allocation — 2026-10-08

The complete installed b4 scene was inspected through the actual Godot Compatibility renderer. The entrance color/normal pair had been imported at uncapped 2172 × 724; aligned lossless 1024 × 341 imports preserve original artwork and reduce actual texture allocation by 11,418,547 bytes (10.9 MiB). Demo allocation is now 49,719,899 bytes (47.4 MiB), normal exploration 55,535,327 bytes (53.0 MiB). Four fixed-clock captures pass comparison inside projected inscription bounds; desktop/portrait arrival lettering was directly reviewed. The diagnostic portrait close view retains the baseline’s edge clipping and is not camera acceptance. No timings were measured during the separate CPU bake. Evidence and retained baseline/capped images: `runtime-texture-audit.md`, `export/gate-inscription-runtime-cap.json`.

These are source b4 runtime results; corrected source90 lighting is still running. The playable package still contains its preceding imports. Complete corrected-source import/render/allocation and rebuilt package checks follow fresh lighting installation. No final texture/atlas, art, traversal or phone requirement is marked complete.

## Complete corrected roof lighting installed — 2026-10-08

- The same locked refresh finished all six phases at `90c4f70e…`, including exactly 124 ordinary maps, direct wash, terminal indirect spill and native pixel/coverage verification. Godot now contains the matching master, four roof/LOD exports and complete 124/33/29/5/7 full/demo/priority-2/wash/spill catalogs. Source libraries were not changed during the bake.
- Actual current-source import is clean. Calibrated keys, shared paint/material adapter, full static receivers, surface shaders, normal/demo wash and spill, entry physics, demo reading/replay and UI checks pass. The initial pixel test used an invalid headless runner; native graphics pass its face/linear-energy checks. The UI assertions passed but fast shutdown intermittently leaked resources; its test now waits for asynchronous cleanup and passes two clean runs. Failed attempts remain in `export/roof-current-runtime-checks.json`.
- Twelve demo-state images and twenty-eight normal arrival images are refreshed and hashed in `docs/reference/roof-current-runtime/`. Direct inspection shows visible tile detail on the outward Qinfang upper shell. The portrait enclosure edge and clipped moon still need work. All fourteen saved site libraries match authoring structurally and have complete source-matched maps. This is not final art acceptance.
- Actual Mac demo texture memory is 49,719,899 bytes (47.4 MiB), normal exploration 55,529,183 (53.0 MiB). Arrival maximums remain 146 draws, 177,088 primitives and four practicals. Demo forced-draw median intervals are 7.054–10.1 ms; normal stationary arrivals reach a 10.684 ms median and 16.907 ms p95. These checks do not establish continuous traversal or sustained device performance.
- A real Pixel debug build now uses corrected source90 and matching complete lighting at native 1080 × 2340 with 48-unit scaled controls. Route texture peak remains 74,761,384 bytes (71.3 MiB), failing the target. Actual cast/recast/close/finish/replay taps pass and return to the initial cell; complete-demo allocation reaches 77,907,112 bytes (74.3 MiB) after finale/replay. Pavilion median is 29.847 ms and p95 31.968 ms in this run; no sustained 60-FPS claim is made. Actual source/APK/script hashes and touch evidence are under `docs/reference/android-roof-current/`.
- The isolated old-source normal-map experiment saves exactly 8 MiB, but reading/finale allocations expose a higher complete-demo peak. Its candidate reaches 69,518,504 bytes (66.3 MiB) at finale/replay and still fails. Production normal PNGs and 2048² imports remain intact. See `docs/android-normal-candidate.md` and `export/android-normal-candidate-comparison.json`.

The existing package/movie remains at the preceding source until rebuilt and verified. Full-goal work remains: camera/enclosure/moon and site art, 34 missing references, texture/font/render-target allocation, continuous traversal and target-phone/release profiling, authenticated readings/history and verified room services. No full-scope acceptance item is marked complete by this checkpoint.

Corrected-source pack follow-up: the separate `build/garden-roof-current.pck` exports successfully with an absolute destination and passes nine actual packaged checks, including native pointer/keyboard traversal and replay. Pack SHA256 is `d7f598302e6e4c7e5b7b2dac18c0a27a33de5bf21aa789cde34aba0487cc0c5a`; evidence is `export/roof-current-pack-checks.json` and `docs/reference/roof-current-runtime/pack-checks/`. The initial relative-path export failed because Godot resolved it inside the project; that terminal failure is retained. New native capture/movie/archive and all remaining art/performance/service requirements remain open.


## Corrected-source demo movie and local archive — 2026-10-08

- Captured the exact packed source already verified by nine packaged material/lighting/startup/native-input checks. Native Godot capture completed cleanly: 1,290 contiguous 1410 × 600 frames at fixed 30 FPS, covering the complete first-reading route, local cast, finale and replay. Seven cue transitions match the original six audio cues. This is a fixed-time capture, not sustained gameplay FPS.
- Assembled H.264/AAC movie is exactly 43 seconds. ffprobe verifies dimensions, rate and frame count; complete ffmpeg video/audio decode finishes without errors. Original cue PCM is mixed using runtime gains/loop rules; duration and nonclipping peak pass. The requested AAC bitrate was clamped by ffmpeg to its supported maximum. Audio is not native capture.
- Native contact sheet and representative original frames were inspected. Corrected upper-roof tile detail is visible. Every frame is hashed; exact capture and assembly logs are archived in `docs/reference/roof-current-runtime/capture/`. The source, pack, movie, cue-source and archive hashes are recorded in the timeline and `export/roof-current-demo-release.json`.
- A repeatable finalizer rejects a mismatched pack hash before promotion. The corrected pack/movie/run guide now replace the preceding local demo payloads; the previous release is preserved under ignored `build/previous-release/`. Both local ZIP aliases contain exactly five expected files, pass CRC and four payload hash checks, and are byte-identical. Build artifacts remain local and ignored by Git.
- The run guide now reports actual Mac and Pixel evidence, outward roofs and corrected Spot cones. It removes stale phone-untested and roof-downward claims. Pixel finale/replay still reaches 74.30 MiB and fails the 64 MiB target. Final site art, moon/enclosure framing, full traversal, target-phone performance, remaining references and authenticated room services remain open. The full goal remains active.


## Native viewport and UI-density allocation — 2026-10-08

- Three fresh native Compatibility processes on M2 Max separately compare desktop size, a larger portrait window, and that same portrait size at the phone's UI density. Scene texture bindings remain identical: 88 RIDs, calculated stored mip data 36,505,432 bytes. Readbacks do not change renderer allocation.
- Larger actual native size adds exactly 17,288,184 bytes in all five states. At identical native size, UI scale 2.625 adds 1,135,958–4,416,850 bytes, with the largest increment at finale. Partial reachable theme-font CPU caches remain identical between densities; they cannot establish complete GPU font cost.
- The requested 1080 × 2340 Mac window is clamped to 1080 × 1984. Direct native image readback proves the actual dimensions; multiplied ViewportTexture metadata is not proof of larger physical buffers. Actual Pixel remains 1080 × 2340, so exact same-size platform attribution is still open.
- Versioned Godot Compatibility implementation confirms its texture-memory counter includes tracked render-buffer bytes. Full native records, clean logs and installed API reflection are archived under `docs/reference/viewport-allocation/`, with hashes and comparisons in `export/viewport-allocation-diagnosis.json`.
- Production source, textures, normal-map detail, font sizes, UI density and resolution are unchanged. Continue actual phone allocation and complete performance acceptance alongside scene art, references, traversal and services. The full goal remains active.

## Imported PBR repair and verified phone allocation — 2026-10-08

- Repaired dropped StandardMaterial3D roughness/metallic maps in the baked adapter, retaining packed G/B factors and all five independent channel choices. Native ORM factor behavior and the default specular response are matched. Explicit Burley/Schlick-GGX modes resolve a separate native lighting mismatch; all twelve pixel fixtures now match their source materials exactly, with visible missing-map controls. Baked unit-light energy still passes.
- Two corrected-renderer Pixel APKs complete actual physics and ten touch edges. Four 1024 normal/ORM imports save exactly 12 MiB in the route; shared 16/22 UI sizes lower the sampled finale/replay peak from 77,907,112 to 62,178,472 bytes (74.3 to 59.3 MiB). This passes both sampled memory thresholds. Pavilion frame intervals remain about 17.4 ms median, with 19.3–19.7 ms p95; sustained 60 FPS is unproven. Casts are stochastic and exhaustive glyph-cache warming is not measured.
- Twelve placed arrival/close/inspection-light comparisons pass at both window shapes. The four inspection views have positive normal/ORM controls. Original 2048 PNGs and color imports are unchanged. The verified limits/font sizes are installed; production reimport is clean, thirteen lighting/material/physics/reading/UI/native checks pass, and all twelve installed captures are byte-identical to the tested candidate.
- Exact source/renderer/build/evidence hashes, failures and installation checks are recorded in `export/android-pbr-{candidate-comparison,adoption}.json`, `export/pbr-{runtime-checks,transfer-evidence}.json` and `docs/pbr-material-transfer.md`. Earlier three phone variants remain explicitly pre-fix allocation diagnostics. The asleep-device launch and cropped wall probe are rejected evidence, not accepted measurements.
- The existing local PCK/movie/ZIP still contains the previous adapter/imports. A fresh packaged verification and native capture must replace it before release claims. Full site art, moon/enclosure framing, 34 references, continuous/full-garden/target-phone performance and authenticated room services remain open; the goal stays active.


## Current PBR demo package and framing diagnosis — 2026-10-08

- The local PCK, 43-second movie and both ZIP aliases now contain the repaired PBR adapter, four 1024 normal/ORM imports and shared UI font sizes. Eleven actual packaged checks pass, including native material pixel controls and pointer/keyboard replay. The finalizer rejects four missing/stale/mismatched provenance cases before promotion. All eight guarded runtime/import files still match the pack, capture and profile records.
- Native capture has 1,290 contiguous frames and seven cue transitions. The H.264/AAC movie completely decodes; archive CRC, exact five-member layout and all four payload hashes pass. Both archives have SHA256 `456a5cc8994c1e8a959f173ab840f739e6b53c2e3276ff484afc2c73a8f59ef7`. Original cue PCM is mixed at runtime transitions; audio is not a native capture. Preceding payloads are retained under ignored `build/previous-release/`.
- A separate stationary desktop profile reports 37,136,987 texture bytes (35.42 MiB), 102–146 draws, 123,740–177,088 primitives and at most four practical lights. Median forced-draw intervals are 6.989–7.774 ms, p95 9.647–12.626 ms. These measurements were made without another host GPU job. The preceding repaired-renderer Pixel candidate remains 59.3 MiB at sampled finale/replay; sustained 60 FPS and full-garden/target-device acceptance remain open.
- Read-only saved-source/runtime diagnosis covers all fourteen arrival cameras in desktop and portrait shapes. Potential top-edge enclosure exposure occurs in five desktop and eleven portrait views; these projection counts do not establish visible failure because foreground geometry can occlude it. Qinfang portrait clips the moon bounds. The physical moon also retains its earlier green emission and lacks painted UVs. Saved Blender has 42 cameras while the user's live scene has 40; neither the live scene nor saved art was changed by this diagnosis.
- Evidence: `export/pbr-current-{pack-checks,demo-profile,demo-release}.json`, `export/pbr-release-evidence.json`, `docs/reference/pbr-release/` and `docs/stage-framing-diagnosis.md`. Final moon/backdrop/shot composition, site art, 34 references, continuous traversal, complete texture/performance acceptance and authenticated room services remain unfinished. The full goal stays active.


## Portrait pavilion camera and rebuilt demo — 2026-10-08

- A native regression fails on the old clipped moon and passes after moving the portrait overview south of the pavilion with a 50° vertical lens. All eight physical moon bounds now fit above the pavilion, clear of header and controls. The title board and table remain visible. The reveal interpolates to the same pose and lens; overview resize preserves room content, and table/cast views retain their preceding 55° horizontal lens.
- All twenty-seven other desktop/portrait arrival projections exactly match preceding native measurements. Source GLB, Blender cameras, lighting and matching bakes are unchanged. Actual desktop reveal/cell-gate-pavilion physics and portrait pointer/keyboard cast/finale/replay pass. Fourteen normal portrait arrivals, six demo states and eight walking-reveal images are captured. Thin canvas-edge exposure remains at the final pose and is larger during the lift; physical backdrop and painted moon work remain open.
- Stationary 390 × 844 normal and demo overviews each measure 47 draws, 85,830 visible primitives and four practicals. Texture counters are 36,147,703/30,336,367 bytes in the same fresh native process. Desktop demo remains 37,136,987 bytes (35.42 MiB), maximum 146 draws/177,088 primitives/four practicals; median forced-draw intervals 5.743–6.823 ms, p95 8.545–8.828 ms. These are stationary Mac counters; the preceding Pixel results do not measure the new portrait camera.
- The separate current PCK passes thirteen actual packaged checks, including native PBR pixels, portrait camera/resize/reveal and both desktop/portrait input/replay. Native capture completes 1,290 frames, 43 seconds and seven cues. Full H.264/AAC decode, exact five-file ZIP CRC/all four payload hashes and byte-identical aliases pass. Current archive SHA256 is `27dc8a63701964c9988cc66c098a08f7b247f963220f52c606d8a1d222753462`. Older local payloads are preserved under ignored `build/previous-release/`.
- The finalizer now requires nine runtime/import hashes including `runtime/entry_route.gd` and the portrait acceptance phases. Actual old missing-route capture, a synthetic wrong route hash and an omitted portrait phase all reject before decode/promotion with preceding release hashes unchanged. Evidence: `export/pavilion-framing-runtime-checks.json`, `pavilion-portrait-budgets.json`, `pavilion-current-{pack-checks,demo-profile,demo-release}.json`, `pavilion-release-provenance-rejections.json` and `docs/reference/pavilion-{framing,release}/`.
- The full goal remains active for physical moon/backdrop art, other site architecture/materials, 34 external references, full-garden continuous traversal, complete texture/target-phone/release performance and authenticated room services. No final site or whole-goal acceptance item is marked complete by this checkpoint.


## Original painted moon source — 2026-10-08

- Saved the original warm ivory/gray-blue painting into the physical moon's projected UV and packed base/emission material. Native reopened checks and an isolated 128-sample Cycles source render pass. All 4,344 objects and 46 unrelated source materials are preserved. The user's older live Blender scene was not saved or reloaded.
- Canonical export is now `c68f6d1e…`; strict comparison preserves 243,042 expanded triangles, 708 node contracts and 46 other materials. Fourteen other site files are byte-identical. Six actual/injected bad camera/collision/material/factor/image cases reject. Supported Mix nodes retain both source factors; the legacy-node exporter loss was diagnosed and avoided.
- Isolated native Godot source/adapter transfer passes emissive, keyed and graded comparisons with positive missing-paint controls. A 512px lossless candidate preserves more sampled detail than a 1024px compressed candidate. Larger phone pixels and current-scene memory remain unverified; no production cap is installed. Original PNG remains 1254 × 1254. Full prompt/provenance and evidence are in `docs/moon-paint.md` and `export/moon-paint-evidence.json`.
- All six complete lighting-refresh phases pass: 124 ordinary maps, backdrop wash, terminal spill, native pixels and current coverage. No old map was relabelled current. Current source and matching catalogs are installed in Godot; native import is clean and thirteen runtime/render checks pass, including current Standard/adapter paint pixels and both fourteen-room arrival sets. The local playable package remains the preceding verified source until a separate pack/movie rebuild. The refreshed fourteen-library audit reports no structural differences and complete current ordinary-map coverage. The actual arrival moon is warm cream but its paint texture appears flat; physical top-edge exposure remains in several portrait rooms, so final art is still open.
- Physical backdrop coverage, final scene art, 30 references, continuous full-garden traversal/device performance and authenticated room services remain open. The full goal remains active.


## Continuous walk and proposed floor repair — 2026-10-08

- A new strict test walks one visitor through all fourteen rooms and all thirteen connections in both directions, returning to the actual cell. It uses public commands and actual physics, with no position resets, private arrivals, path replacements or time-scale changes. The production source reaches all rooms but fails floor support on ten of twenty-six legs at three small gaps: the cell doorway and the east/west pavilion approaches. The visitor dips up to 2.9 cm; production traversal acceptance remains open.
- A separate Blender candidate adds six narrow wooden doorway thresholds and two short stone crosswalk joints, each with matching visible and collision geometry. All 4,344 existing objects and source materials/moon are preserved. Thirteen unrelated site GLBs remain byte-identical; two affected sites require fresh lighting after adoption. Render geometry increases by 96 triangles.
- The actual candidate export, imported into an isolated Godot project, passes all fourteen rooms, twenty-six legs and 17,581 grounded ray samples without a miss. Independent import checks pass 42 cameras, 400 collider surfaces/rays and 71 markers. A prior test-only counterfactual also passes; removing each of the three joint groups independently restores its original failure. Only old baked-lighting application is disabled in the actual candidate fixture, because its floor UVs have changed; production movement and the strict test are unchanged.
- Candidate files are retained separately; canonical Blender/export, production Godot and local release are unchanged by this repair. Native rendered inspection, adoption after the active source bake finishes, new matching lighting and repeated production traversal are still required. Evidence and limitations: `docs/full-garden-traversal.md`, `docs/reference/full-garden-traversal/`, `export/full-garden-traversal-evidence.json`.

## Portrait backdrop candidate — 2026-10-08

- Forty native camera comparisons show that narrower or farther-back views crop architecture/signs or pass behind walls. Those changes are rejected. A separately authored painted ceiling covers the exposed backdrop areas while keeping current arrival cameras and building views.
- The saved ceiling adds 2,240 inward-facing triangles and preserves all 4,344 existing objects/materials; only thirteen linked wash receiver lists gain the new object. Actual export preserves all 708 existing node contracts, including mesh/index/UV data, embedded paint/materials, lights and cameras. Fourteen unrelated site GLBs remain byte-identical. Planar upper-sky UVs reduce the first version's radial paint streaks.
- Actual Blender exports are imported and captured in isolated Godot fixtures across fourteen portrait arrivals. Old maps are disabled; the new ceiling explicitly uses existing shared unshaded paint and no-shadow intent. A final per-surface-culling ray probe verifies sampled coverage with canopy-removal controls. This is not production import/bake shadow transfer, fresh lighting, continuous traversal, device performance or final art acceptance.
- The candidate stage library and immutable native comparisons are retained separately. Canonical source/export, production runtime and local release remain unchanged. Next: verify shadow intent through import/bakers, refine final paint/moon contrast, combine accepted floor/backdrop geometry and generate fresh matching lighting. Remaining thirty references, scene art, full traversal/performance and authenticated services stay in scope. Details: `docs/portrait-backdrop.md`, `export/portrait-backdrop-evidence.json`.

## Shadow transfer and revised floor joints — 2026-10-08

- Godot import and all three native bake paths now restore explicit boolean mesh shadow intent. Native ceiling pixel controls pass after a cold isolated import; shared unshaded paint/color/texture matches the existing cyclorama. Blender restores the actual ceiling's false flag, with positive shadow controls and preservation of 558 unflagged mesh settings. The current source has no flags and remains unchanged. Rejected directional/stale-cache/luminance-label diagnostics are retained.
- Actual floor inspection exposed coplanar overlap artifacts. A separate revised source raises matching visible and collision inserts by 2 mm. The observed pavilion artifacts disappear; sixteen native captures and centre rays inspect all eight joints. The actual revised export passes the strict fourteen-room, twenty-six-leg continuous walk with 17,581 supported ray samples and no misses. Old lighting remains disabled in that fixture; this is not production traversal or final lighting acceptance.
- A separately saved combined floor/ceiling export is prepared at `33b20efa…`, 233,552 render-only triangles. Both floor-site exports preserve the verified revised bytes, and twelve other site exports remain canonical. Source snapshots preserve existing objects/materials/cameras. The combined source is not installed or freshly baked; strict six-receiver wash support, combined import/walk/render and final moon/paint checks precede lighting adoption. Remaining art, thirty references, performance/package/device and authenticated services remain open. Details: `docs/scene-adoption.md`, `export/scene-adoption-evidence.json`.


### Combined candidate lighting and contrast — 2026-10-08

The separate floor/ceiling candidate passes actual native import, fourteen-room
continuous physics traversal (26 legs, 17,581 grounded rays, zero misses), and
portrait upper-image coverage with production imported materials/shadows.
Strict five/six receiver contracts reject missing and substituted surfaces;
the ordinary catalog remains 124 targets. All fifteen candidate libraries
are packaged, with twelve linked washes sharing six visible stage objects.
Fresh 128-sample/512-pixel direct wash maps pass all source/library checks and
the zero building-leak control. Fresh wash combined with stale ordinary maps
is rejected without material/layer changes. Installed-source normal/demo
lighting and receiver-layer regression checks pass.

Actual currently baked moon counterfactuals show complete ungraded white
clipping; lower linear base/emission restores brush detail. This diagnostic
change is not installed or authored. Final moon/paint source adjustments and
complete matching lighting must precede production adoption. The canonical
source/GLB and preceding packaged release remain unchanged; its runtime
provenance is older than the current source code. `docs/ceiling-lighting.md`
and `export/ceiling-lighting-evidence.json` retain the current evidence. Full
site art, thirty references, device/performance/package acceptance and room
services remain part of the active goal.

### Authored contrast candidate — 2026-10-08

The combined floor/ceiling source now has a separate authored moon candidate
with base/emission factors reduced to 45% and explicit matching atlas metadata.
Original paint/UV/geometry and all other objects/materials are preserved. Native
reopened-source checks and actual full/stage export comparison pass; fourteen
other site exports are unchanged. Native material-transfer comparisons and
fourteen-room portrait coverage pass with old bakes disabled. The unbaked view
still looks too bright and is not final art acceptance.

The exact adjusted export passes the continuous headless fourteen-room,
twenty-six-leg walk with 17,582 supported grounded rays and no misses. It uses
actual imported colliders and public commands without resetting the visitor;
old bakes remain disabled in the separate fixture. Production adoption and
fully lit rendered traversal remain pending.

Complete fresh lighting is running against the frozen candidate export. The
canonical source and production runtime retain the preceding source; no partial
maps are installed. Fully baked visual review, rendered traversal, matching
source/library/atlas/lighting adoption and a separate package rebuild remain
required. Evidence and limits: `docs/moon-contrast.md` and
`export/moon-contrast-evidence.json`.

A newly identified Xiaoxiang entrance photo fills its architecture reference
slot with attribution and verified original bytes. Required references are now
13/42, leaving 29. A daylight rock portal is retained as supporting modelling
evidence only; it does not fill the rockery tunnel/fog slots. Full site art,
texture/device/performance acceptance and authenticated services remain in scope.

Daoxiang's close material slot is now filled by an original reed-thatch
photograph with verified bytes and linked author public-domain release. It
supplies stem/bundle/roughness detail rather than Chinese roof structure or site
identity. Required reference coverage is 14/42, leaving 28 slots.

Three more directly reviewed originals fill Ziling's entrance architecture,
Daguan's painted timber material and Qiushuang's painted-scroll material slots.
Original metadata, attribution, licence and byte checks are retained. Two
misidentified architecture candidates are explicitly rejected. Current reference
coverage is 17/42, leaving 25; daylight photos do not fill the required night-set
slots. The fresh candidate lighting bake remains separate from production.

Xiaoxiang now has all three collected references. An official Archive night-set
still supplies bamboo silhouettes and warm torch/cool fill separation with
explicit copyright attribution and reference-only scope. Three daylight film
stills are rejected for bridge/night/cave slots. Current total is 18/42, leaving
24; reference collection does not establish completed scene art.

The complete-route native capture harness is prepared for desktop and portrait
inspection after the candidate bake. It reuses the strict fourteen-room,
twenty-six-leg physics tour and requires matching 124/6/7 lighting catalogs.
Native parsing and its headless refusal guard pass; positive rendered runs are
pending. Existing physics proof is unchanged, and no final visual/traversal or
performance acceptance is claimed. See `docs/full-garden-traversal.md` and
`export/rendered-full-garden-tour-preflight.json`.


### Complete candidate bake and rejected moon appearance — 2026-10-08

The separate 41b81c17 candidate has completed all six source lighting phases:
124 ordinary maps, six wash receivers, seven terminal-spill maps and native
pixel/coverage checks. Two forced cold imports preserve 42 cameras, 400
colliders/ground rays, 71 markers and 167 render mesh snapshots. Five actual
fully baked headless lighting contracts pass after matching catalogs and
original PNG bytes are installed in a separate acceptance project.

The 28 native desktop/portrait arrival captures pass capture checks but fail
final moon appearance. Direct review and pixel measurements show near-flat
white paint: 99.90% raw interior clipping, graded p05/p95 0.915020/0.915304.
An additional 0.45 linear multiplier on both base and emission restores
visible detail with no raw clipped samples in the tested Qinfang portrait.
The next source candidate targets 0.2025 of the original calibrated luminance;
new source/export/full lighting/art checks are required. The ceiling is present,
but visible paint joins remain unfinished. No canonical source or package
adoption is claimed. Evidence: `docs/moon-contrast.md` and the three new
moon-contrast lighting, reimport and baked-review indexes.

A Sun Wen painting labelled Longcui was directly reviewed and rejected as the
required architectural reference: it shows an interior rather than the closed
gate, exterior whitewash or plum frontage. Required coverage remains 18/42,
with 24 references missing. Full site art, continuous rendered traversal,
texture/device/performance/release acceptance and authenticated services remain
in scope. The full goal stays active.


The complete native desktop and portrait walks now pass on 41b81c17 and its
matching lighting: fourteen rooms, twenty-six legs and 17,581 supported
floor-ray samples per run, no misses, true cell return, controls/signals checked
and at most four practicals. Desktop has 114 captures; portrait has 139,
including all twenty-six settled arrivals. A too-short fixed-pause portrait
attempt was explicitly stopped/rejected; the corrected harness waits for the
actual camera tween completion. Raw results and scope are retained in
`export/moon-contrast-rendered-traversal-evidence.json`. These remain separate
candidate results; canonical production adoption and final art are pending.

The additional lower moon is actually authored and reopened, not just a shader
override: saved source a273a4c0, actual export 8d1d9b4e, explicit absolute
luminance ratio 0.2025. All 4,361 objects and 47 other materials are preserved;
717 complete export node contracts and fourteen identical other site GLBs pass.
Seven source and eight export corruptions reject. Fifteen libraries and the
portable master preserve twelve Areas linked to six actual stage receivers,
and all fourteen saved site structures match. Fresh whole-source lighting is
running in its own frozen tree; native final art/adoption is still required.
Evidence: `export/moon-intensity-final-source-evidence.json` and
`docs/moon-contrast.md`.

Yihong's banana-leaf close-up is now collected and directly reviewed with Hysocc
CC BY-SA 3.0 attribution and verified original bytes. Current required reference
coverage is 19/42, leaving 23 slots. A different Dicuiting pavilion photo was
reviewed but not accepted as the required Ouxiang architecture. The full goal
remains active for art, references, texture/device/performance/current release
and authenticated room services.


Tubi's close foreground stone table material reference is collected with directly reviewed original bytes and Pseudopanax's author public-domain release. Current coverage is 20/42, leaving 22 slots. Two mismatched pavilion/mosaic candidates are explicitly rejected. This reference pass changes no scene assets or lighting; the frozen 8d1d9b4e full bake remains separate and running. Final art/adoption, texture/device/performance/current release and authenticated room services remain open.


Aojing's named windowed facade is now collected from Beijing Tourism with direct plaque/structure review, publisher copyright attribution and original bytes. Required coverage is 21/42, leaving 21 slots. The Longcui gallery's lake/flower/open-hall images do not establish its specified closed outer gate; that slot remains open. Scene assets, production lighting and release remain unchanged by reference collection.


Qiushuang now has all three collected references. The Archive zither interior supplies a local candle against a blue opening and dark built-set panels; the scene/night match is recorded as an inference with primary newsletter context and the low-resolution limit. Original bytes and copyright credit are preserved. Required reference coverage is 22/42, leaving 20 slots. Two blue-text terminal photos are rejected for the specified green-phosphor dark-room reference. Final art/adoption, memory/device/performance/current release and authenticated room services remain open.


## Matching working scene adopted — 2026-10-08

Canonical Blender authoring is now `a273a4c0…`; export and Godot GLBs are both `8d1d9b4e…`. Fifteen site libraries, the portable master, source/engine atlases and all 141 source PNGs were installed together after exact staged/current byte checks. The full exploration route is the default scene; the focused reading demo remains separate. Production import, all camera/collision/marker snapshots and five lighting checks pass.

Both matching native rendered walks visit fourteen rooms over twenty-six public-command legs, check 17,582 supported ground rays with no misses, capture all twenty-six settled arrivals and return to the original cell. Desktop and portrait each retain 139 PNGs. The earlier current-run count of 17,581 was incorrect; that count belongs to the preceding 41b candidate.

The baked moon retains brush variation with no measured channel clipping. Baseline display p05/p95 is 0.662944/0.805190; the original 1254² painting remains unchanged. This accepts a working improvement, not final scene art. Roof striping, visible paint joins, some portrait framing and later-site detail remain open.

Current normal-route Mac allocation is 49,284,173 renderer texture bytes (about 47 MiB), with a highest sampled room of 49,367,461 bytes. This is not target-phone, demo-finale, sustained-traversal or release evidence. The existing local package/movie still represents the earlier source. Twenty required reference slots, final texture/device/performance and authenticated room services remain unfinished.

Evidence: `export/moon-intensity-final-lighting-evidence.json`, `export/moon-intensity-baked-review-evidence.json`, `export/moon-intensity-rendered-traversal-evidence.json` and `export/moon-intensity-working-adoption-evidence.json`. The original review's stale worker PID is preserved; a separate resume provenance record identifies its successful completion.


### Current Android diagnostic export — 2026-10-08

The profiling builder now accepts the full exploration or focused-demo main scene before selecting its isolated profiler. Current 8d source Android import/export passes, and the diagnostic APK is installed on the Pixel. The locked device has not produced fresh samples; its existing report is the older 90c4 source and is explicitly rejected as current evidence. Unlock is required to resume the running diagnostic app. The broad APK export also contains about 453 MB of KIT imports; dependency-based packaging remains work. Exact evidence: `export/moon-intensity-android-preparation-evidence.json`.


The corrected diagnostic export now filters KIT-prefixed previews and retains runtime shared atlases/foliage. Its APK is 91,542,782 bytes, saving 453,217,688 bytes. All 177 file-backed normal-route texture imports, generated reflection and every used foliage LOD survive the payload check. A too-broad filter that removed six used textures rejects. Native import/export passes; the filtered package awaits fresh device testing and is not a release. Evidence: `export/moon-intensity-android-packaging-evidence.json`.

## Courtyard compression fix — 2026-10-08

Xiaoxiang's pink wall/timber checker is a GPU compression artifact. An actual
same-resolution lossless import removes it; the adopted 512px cap sharpens the
whitewash shadows. The timber source stays 256px. Only these two import files
change, and the configurator preserves their exceptions during later refreshes.
All 141 source PNGs, authoring, GLB, runtime, shaders, cameras and collision retain
their bytes. Production import, camera/collision/marker and five lighting checks
pass. Four native production captures match the tested candidate pixel for pixel.
Normal Mac allocation is 50,507,483 renderer texture bytes (48.17 MiB), across
178 textures. This does not establish phone, demo-finale or sustained performance.

Roof stripes persist in the baked irradiance after normal/specular and filtering
controls; source-art correction remains work. The first roof-mask fixture emitted
renderer errors and is retained as rejected. Evidence and limits:
`export/courtyard-import-quality-evidence.json` and
`docs/reference/courtyard-import-quality/README.md`. Existing Android APKs share
the source GLB but predate these GPU import settings; fresh packaging and device
samples are required. Final site art, twenty reference slots, current release,
device/performance and authenticated services remain open.

## Android import provenance — 2026-10-08

The fresh isolated filtered profiling APK includes the adopted courtyard imports:
91,579,636 bytes, SHA256 `21a3ed66…`. Native mobile import/debug export pass.
Its embedded manifest pins 355 production texture inputs and 356 finalized staged
inputs, including source bytes, raw imports and effective parameter sections.
The archive retains all 177 file-backed textures bound by the actual normal-route
inventory, with exact Android cache payload hashes, plus required foliage LODs.
Runtime scripts, shaders and catalogs match the older filtered APK; the two
courtyard payloads and profile manifest intentionally change.

Collection and the touch helper now verify current production/staged texture and
runtime inputs and the installed dedicated APK's SHA256 before accepting reports
or sending taps. Seven local input tests, four actual-APK corruption rejections
and three mocked installed-APK preflight cases pass. These checks do not invoke
ADB or establish device behavior. The new APK remains local and uninstalled while
the pending unlock reply is unanswered. Evidence:
`export/courtyard-android-provenance-evidence.json`. Full scene art, twenty reference
slots, current release, mobile/sustained performance and authenticated services
remain open.


## Pavilion tile chart correction — 2026-10-08

A separate candidate corrects 336 inward tile faces and reserves actual lighting
pixels for Qinfang’s 42 raised strips. The old exported triangles are only
0.113–0.130 source pixels wide; normal correction and a shallower geometry
control both retain dark bands. Explicit charts give each triangle a 9.370px
minimum altitude, and black centroid samples fall from 76.8% in the shallow
control to 1.79% with the original tile shape and revised charts.

Native roof/portrait comparisons show the broad black ribs replaced by lit
thin tile strips, including the 256px imported map. The selected candidate keeps
all original vertex positions and primary paint UVs. All 716 unrelated nodes and
fourteen other site exports match production. These are frozen target-mesh
comparisons, not a full new lighting installation or final site acceptance.

Matching fifteen Blender libraries and portable master are prepared; a full
fresh ordinary/wash/spill lighting refresh is running separately for source
`b540496a…`. Production remains `8d1d9b4e…` until matching lighting and native
validation pass. Evidence: `export/pavilion-tile-chart-evidence.json` and
`docs/reference/pavilion-tile-charts/README.md`. Final palette/site art, twenty
reference slots, current release, device/sustained performance and authenticated
services remain open.

## Android identity bridge and storage checks — 2026-10-08

The native Godot v2 Android addon compiles in debug and release against the installed 4.7.2 template. Twelve JVM cancellation/signing assertions and thirteen actual Godot wrapper checks pass; the wrapper uses a fake native transport. Three dedicated-package Android Keystore tests pass on the Pixel, with exact installed APK hash verification. Persistence, tampered ciphertext and missing-key behavior are verified. The first rejected SDK 24 installation, corrected SDK 36 build, compact-result collector rejection and editor-shutdown rejection remain archived. No device security settings were changed.

The addon is disabled and room controls remain unconnected. Real Android Godot registration/Google provider operation, server provisioning/device claim/Records exchange, encrypted account credentials, refresh rotation and owner-scoped history remain required. No session or reading was created. Evidence: `export/android-identity-evidence.json` and `docs/reference/android-identity/README.md`. The full goal remains active.

## Pavilion roof correction adopted — 2026-10-08

The original-shape tile correction and its complete fresh lighting bundle are installed: authoring `9356f6ec…`, export/engine `b540496a…`. All six source bake phases, twenty-seven isolated native review phases, both fourteen-room/26-leg rendered walks and seven post-install production checks pass. The desktop/portrait walks record 17,582/17,581 supported floor samples respectively, with zero misses. All fourteen saved libraries match after correcting the audit to evaluate scene-less collections. The corrected roof charts are now the exporter default; an actual default export reproduces the complete and all fifteen site GLBs byte for byte.

The stationary Mac normal-route texture audit remains 178 textures, 35,018,254 image bytes and 50,507,483 renderer texture bytes. Both courtyard lossless import parameter sets are preserved; resource UIDs changed during cold import. Exact evidence and inspection limits: `export/pavilion-tile-full-lighting-evidence.json` and `docs/reference/pavilion-tile-full-lighting/README.md`. Other roof/paint joins, palette/site architecture, twenty references, fresh release/device/2020 Adreno/sustained performance and authenticated services remain open. Older local Android profiling APKs are stale for this source.

## Current pavilion-source Android preparation — 2026-10-08

A fresh diagnostic Android import/export passes for the installed b540496a source. The APK is 91,579,996 bytes (`5a0aa30e…`), with finalized embedded texture provenance and all 177 normal-route bound file imports, their actual cache payloads and required foliage LODs verified. A byte-matched copy is in `build/garden-phone-profile.apk`. The Pixel remains locked; this APK is uninstalled and has no fresh device samples. Evidence: `export/pavilion-tile-android-evidence.json`. This is a diagnostic package, not release or authentication acceptance.


## Isolated imperial roof chart correction — 2026-10-08

Production authoring9356/export+Godot b540 remains installed. The separate
361a67c7 Daguan candidate preserves geometry/normals/primary UVs, 716 other
resolved nodes and fourteen other site GLB bytes. All 576 closed tile cylinders
have outward normals; their original side charts were under 0.1 source pixel.
Explicit UV2 charts plus a fresh 128-sample roof bake reduce zero upward-side
centroids from 4065/4520 to 15/4520. These are RGB16 centroid diagnostics.

Four native Godot fixed-clock comparisons pass: portrait, desktop and close-up,
90 captures and twelve byte-identical baseline restorations. Sixteen originals
were directly inspected. Actual 256px imports retain patchy shading; actual
512px lossless RGB8 improves the inspected roof views and is selected for
complete-source validation. Its decoded image is 786432 bytes, not a renderer
or device budget measurement. Full matching lighting, gutters/noise, moving
camera, all-site art, memory/device acceptance and adoption remain pending.
No new full bake or Android package was started. All experiment jobs exited.
See docs/reference/imperial-roof-charts/README.md and
export/imperial-roof-charts-evidence.json for source/maps/code/logs and failed
attempts. Full Garden scope, 20 missing references and service work remain open.


## Complete imperial candidate preparation and two references — 2026-10-08

The separate `361a67c7…` export now has fifteen saved libraries and a portable master. The twelve Area washes share the six visible stage receivers. Both native preparation commands exited successfully. The complete GLB, unchanged `9356f6ec…` authoring, libraries/master, 187 source scripts and 169 runtime inputs match their frozen hashes. Exact logs, scripts and preparation records are in `docs/reference/imperial-full-preparation/README.md` and `export/imperial-full-preparation-evidence.json`.

A fresh complete bake is running from an empty lightmap folder. The separate Godot review waits for all six source phases and the baker exit, then runs sequential native imports, corruption controls, saved-library checks, actual normal/demo memory, arrival captures and full rendered walks. The imperial roof uses the previously inspected 512px lossless import policy in that fixture. Preparation is not finished lighting, visual/device acceptance or adoption; production remains b540/9356.

Ouxiang's open water-pavilion photograph and Longcui's upper gateway photograph now fill their architecture slots. Both publisher originals were directly inspected; source HTML, hashes, Sipa credit/copyright and framing/daylight limits are saved. Neither is a shipped asset or a night reference. Collection is now **24/42**, with **18** slots missing. Final scene art, performance/device/release and authenticated room services remain open.


## Rockery and courtyard lighting references — 2026-10-08

The Beijing south-entrance rockery reference fills rockery slot 1. Its directly reviewed dry path, piled stone, overhangs and dark gaps support the obstructed reveal and organic surface work. A different pool/overhang photograph does not fill another slot. Original publisher bytes, Sipa copyright/watermark and article attribution are saved.

The Film Archive's credited *The Magic Blade* courtyard still fills Yihong's night-set lighting slot. Its black sky/tree masses, directional blue-violet light on pale walls and warm/red figure accents guide courtyard contrast. Night appearance is a visual inference; no warm window/lantern is visible. The original encoded JPX stream, full source PDF and credited full-page/colophon renders are retained. The courtyard is not the specified cave corridor; the separate *36th Chamber* training still is not the required cell. Neither rejected slot is counted.

All three Yihong references are now collected. Total collection passes original-byte/slot checks at **26/42**, leaving **16** missing. This does not accept the finished site art, lighting, phone performance, release or service integration.


## Imperial working bundle and Ouxiang comparison — 2026-10-08

Working export/Godot is now `361a67c7…`; saved authoring remains `9356f6ec…`. All six fresh source-lighting phases pass. The first engine review's generic 256px roof-cap failure is retained. Its revised explicit imperial option verifies the exact UV hash, lossless 512 import, RGB8 dimensions and 786,432 decoded bytes; the default cap still rejects. Thirty-one successful native phases, both 14-room/26-leg/139-capture walks, exact default-export reproduction of all 16 GLBs and seven post-install production checks pass. Renderer texture memory on M2 Max is 51,512,354 bytes (49.1 MiB), not phone/sustained acceptance. Recoverable working-bundle backups remain local. Full evidence: `export/imperial-full-lighting-evidence.json`.

The separate Ouxiang `be80374c…` proposal preserves physical geometry and other scene contracts. All 169 saved roof-object vertex sets match unique export components. A fresh 128-sample 1024px roof bake removes zero upward-side centroids (117/1344 to 0/1344); upward cap zeros remain 229/1008. Three native runs preserve twelve baseline/restored pairs and 96 original captures. Actual lossless 512 looks cleaner than either actual 256 import; smaller manual previews are insufficient evidence. Lower/further portrait framing exposes more platform and water but remains a proposal. Source/default exporter, complete matching lighting, final framing/material/gutter/memory/device acceptance remain open. Evidence: `export/ouxiang-roof-proposal-evidence.json`, `export/ouxiang-roof-native-evidence.json`.

All existing Android packages, including uninstalled 5a0aa30e, are stale for the installed 361a source. No current phone, 2020 Adreno, sustained traversal or release acceptance is claimed. Sixteen reference slots, final site art/palette/joins and authenticated reading/history/AI/presence/social remain required. The full Garden goal remains active.

The selected Ouxiang portrait pose now has a matching actual 512px lossless render: target height 0.5/distance 2.0 fits more roof/platform/water above UI. Eight native capture hashes and baseline/restoration verify. The pose is selected for runtime testing; canonical camera, complete lighting and device/final-art acceptance remain pending. Evidence: `export/ouxiang-portrait512-evidence.json`.


## Ouxiang reproducible export and installed portrait view — 2026-10-08

The default Blender exporter now reproduces candidate `be80374c…` exactly. Its disabled-option control reproduces the installed `361a67c7…` complete export and all fifteen site GLBs; the correction changes only the Ouxiang site and complete candidate. Saved authoring remains `9356f6ec…`. Four real exported-fixture tests pass, including source geometry preservation, dedicated-site attribute identity, idempotence and rejected deformed tile geometry. Five new Ouxiang import-policy fixtures and four existing imperial fixtures pass. Native complete-candidate import validation remains pending.

Ouxiang's portrait camera is installed against the existing complete `361a67c7` lighting. It targets height 0.5 and doubles the camera offset. A camera-only attempt and a 152-unit action-area attempt still hid a pier at 360px, so both rejected reports/captures are retained. The accepted 128-unit action area keeps commands reachable by scrolling. Native 390×844, 360×800 and actual 1080×1976 at simulated 420-DPI density pass roof/support/interface and 48-unit control checks; desktop and thirteen other room poses match before/after. Tea/look preserve the view, and both western and nunnery physics routes pass. Four original views were inspected. Water patches, coarse paving, backdrop, palette and other final art remain open. This does not prove real-device behavior.

A separate complete Ouxiang source now has fifteen freshly saved site libraries and a portable master with twelve wash lights sharing six visible receivers. Source preparation passed after a first wrapper helper-import failure; that failure is preserved. The new `be80374c` all-scene lighting refresh and its waiting isolated engine review are running separately. No candidate GLB or new lighting maps are installed. The default exporter therefore produces the next source; use `--no-ouxiang-tile-uvs` only to reproduce the current installed source. Full matching lighting and engine acceptance are required before adoption.

Evidence: `export/ouxiang-export-camera-evidence.json` and `docs/reference/ouxiang-export-camera/README.md`. Reference coverage remains 26/42. Current Android/device/2020 Adreno/sustained performance/release, final art and authenticated services remain required; the full goal is active.

The native density window requested 1080×2340 but macOS constrained it to 1080×1976 (logical 411×753). Original PNG headers confirm this; the projection checks used that actual logical viewport. The separate headless UI test passes at full 1080×2340/logical 411×891. Neither is real-device acceptance. The earlier requested-size wording is corrected above.

## Sourced night-set references — 2026-10-08

Eight distinct frames from the published Arrow Video and Shaw Brothers Clips trailers were directly reviewed and saved with unchanged source streams, exact decoder PTS, publisher attribution, rights information and hashes. Required reference coverage is now 34/42. The new frames fill seven generic Shaw night-set slots and Qinfang's night-exterior lighting slot. They guide warm wood/lamps, neutral plaster/stone, limited blue background/foliage light and dark unlit areas for the less-green revision. No production scene or lighting is changed by this collection.

Remaining slots: Aojing 3 (material close view), Hengwu 1 (night set), Qinfang 1 (the specified *Come Drink With Me* bridge pavilion), rockery 2–3 (film cave and dark fog/moon gate), and terminal 1–3 (film cell, historical studio dressing room and dark-room green VT100). Rejected coarse samples do not count, and do not establish that a suitable view is absent from a film. Reference collection is still incomplete. Evidence: `reference/external/supporting/shaw-trailers/README.md` and `export/shaw-night-reference-evidence.json`. Final art, device budgets, services and release acceptance remain open.

## Ouxiang paving-join diagnosis — 2026-10-08

CPU pixel rays through the existing native 390 × 844 capture identify two overlapping stone-path top-face pairs at the nearly black foreground rectangles. Their exact RGB16 source-map samples are much darker than adjacent paving; separate sampled water pixels intersect the animated water mesh. A source-constructor trim proposal removes 4.86m² of path overlap while preserving its union across 99 rectangular partition classes. This is diagnostic evidence and an unapplied proposal. Native saved-object ownership, causal control render, source repair/fresh lighting/visual and route acceptance are pending. No production scene or shader changed. Evidence: `reference/ouxiang-path-joins/README.md` and `export/ouxiang-path-join-evidence.json`.

## Reference collection: 36/42 — 2026-10-08

Aojing's close timber/glazing photograph and Hengwu's night wall/window frame are now directly reviewed and saved with original bytes, attribution and hashes. Both sites have all three required references. Remaining six slots: Qinfang 1, rockery 2–3 and terminal 1–3. Source originals and exact film PTS are documented in the two site reference READMEs. These material/lighting observations do not establish scene identity, measured architecture or final art acceptance. Evidence: `export/aojing-hengwu-reference-evidence.json`.

## Ouxiang complete-source working update — 2026-10-08

The installed complete GLB is `be80374c`; saved authoring remains `9356f6ec`. The Ouxiang roof's secondary UV charts are corrected. All six fresh lighting phases passed, including all 124 ordinary receivers, shared wash and terminal spill. No old map was relabelled for the new source.

The isolated native review passed 37 phases. Cold reimport preserves geometry, cameras, collisions and markers; deliberate camera/collider/marker corruption and both missing-roof-policy controls reject. The explicit two-roof import uses lossless 512² RGB8 maps, no mipmaps, with exact source/UV guards. Other maps keep the 256px policy. Four framing captures retain their actual PNG dimensions: 1410×600, 390×844, 360×800 and 1080×1976. The last was requested as 1080×2340 but constrained by macOS; it is not a physical phone test.

Both native garden walks cover 14 rooms, 26 legs and 139 original PNGs each. Supported floor ray samples are 17,582 desktop and 17,581 portrait, with zero misses and at most four practical lamps. All captured original hashes are checked. The canonical Blender exporter reproduces all 16 GLBs byte for byte. A separate native inspection verifies the exact three approach render boxes and collision proxies in both saved authoring and stage library; this inspection does not repair them.

M2 Max stationary normal-route renderer allocation reaches 52,600,513 bytes (50.16 MiB), versus 52,517,225 bytes at the final arrival. Demo maximum is 43,512,435 bytes. Bound normal image data is 36,525,582 bytes. These figures do not prove phone, sustained performance, frame timing or release budgets.

Sixteen changed targets were installed with recoverable local backups. Eight production checks passed: import, source contract, full lighting with both roof flags, normal/demo wash, normal/demo terminal spill, and animated water/fog materials. Authoring, current runtime and canonical exporter code were not rewritten by adoption.

Selected original Ouxiang desktop, portrait and settled captures plus the moon composition were directly inspected; 14-site contact sheets were inspected for gross assembly. The roof is more consistent. Black paving rectangles, green-heavy materials and other final art remain visible and unaccepted. Full-resolution all-site art acceptance, the last six reference slots, current Android packaging/device and 2020 Adreno/sustained profiling, release and authenticated readings/history/AI/presence/social remain required.

Use `configure_lightmap_imports.py --size-limit 256 --imperial-lossless512 --ouxiang-lossless512` and `test_full_scene_lighting.gd -- --imperial-lossless512 --ouxiang-lossless512` for this source. Original logs, executed code, reports and captures are archived here. The evidence index records exact SHA256s; absolute scratch paths inside original reports are retained as executed provenance. This checkpoint does not complete the full Garden goal.

## Paving repair and less-green material candidates — 2026-10-08

The isolated47ac858e source removes the two overlapping nunnery approach corner faces while preserving all collision proxies and the path union. Native source-matched128sample lighting and256/1024Godotcontrols resolve both blackcorners. Surface-IDimages differ at one edgepixel; all717exportnode contracts and14other siteGLBs match. No candidate adoption yet. See `reference/nunnery-path-repair/README.md` and `export/nunnery-path-repair-evidence.json`.

Four plain shared materials have a native less-green preview on49baked surfaces: brownwood, warmneutralwhitewash/stone and slate rooftiles. Sixteenoriginals cover four rooms at desktop andportrait. Geometry/current lighting/grade/UI are unchanged; saved-source application/fresh indirect lighting are pending. Pavilion/corridor and other atlascolors still need a later pass. See `reference/neutral-material-preview/README.md` and `export/neutral-material-preview-evidence.json`. Full finalart/6references/currentAndroid+device/2020Adreno/sustainedrelease/authservices remain required.

## Complete neutral-material and paving source prepared — 2026-10-08

Separate5ae484f9/42579f68source combines the controlled paving repair and four neutral shared-material colors. Palette-only preservation proves all717node contracts and245,474expanded indexed triangles/attributes match the repaired47acsource; only fourbaseColorFactors change. Fifteen savedlibraries and portable shared-wash master are ready, with an empty lighting directory before refreshing. Complete matching freshlighting is running; a separate native review waits for all six phases and bakerexit. Currentproductionbe8/9356 is retained. Preparation is not fullbake/adoption/finalart/device/services acceptance. See `reference/neutral-path-full-preparation/README.md` and `export/neutral-path-full-preparation-evidence.json`.

## Neutral pavilion and wall atlas candidates — 2026-10-08

Separate procedural atlas candidates replace green wood/tile/stone/whitewash swatches with the reviewed brown, slate and neutral palette. UV regions, 2048² size, padding and ORM channel conventions match; normal and ORM PNGs are byte-identical, and bronze/unused quarters are unchanged. The CPU verifier passes and rejects the original atlas as an unrevised candidate. Originals were visually viewed; saved-source attachment, native texture/geometry checks and fresh lighting remain pending. The current 5ae bake and working be8 scene are unchanged. Evidence: `reference/neutral-architecture-atlases/README.md`, `export/neutral-architecture-atlas-evidence.json`.


## Neutral architectural atlas source preparation — 2026-10-08

The new wall and pavilion color textures have an export preservation gate. A CPU substitution of the exact two candidate PNGs into neutral-material/paving source `5ae484f9` preserves all 717 nodes, 567 meshes and 245,474 indexed triangles, including collision geometry, plus both UV channels. Only two embedded color images change; the other 33 images, material properties and texture/sampler contracts remain unchanged. This is a CPU fixture, not a Blender export or a rendering-budget measurement.

Nine unwanted-change controls reject. All fifteen site fixtures are covered; four contain the changed architectural atlases. The packed-image Blender update helper and sequential source-preparation runner pass Python syntax checks. Their native phases have not yet run.

A separate source update is queued behind the existing neutral-material/paving bake and native review. It has 238 frozen input files and a passing CPU atlas check. It requires the preceding six bake phases and 37 review phases to pass and their orchestration processes to exit before starting Blender. It will then save/export the two-image revision, check complete and site exports, package the site libraries and bake lighting for that exact source. It does not install any assets. Live status is referenced by the archived checkpoint.

Production remains `be80374c` / saved authoring `9356f6ec`. The new paving, plain colors and architectural atlas colors are still candidates. Native source agreement, fresh lighting, scene visual acceptance and adoption remain required, as do remaining site art, six references, current phone/2020 Adreno/sustained performance, release and authenticated services. Evidence: `../export/neutral-atlas-integration-evidence.json` and `reference/neutral-atlas-integration/README.md`.


## Paving/plain colors verified; architectural colors saved — 2026-10-09

The separate paving and four plain-color source `5ae484f9` / authoring `42579f68` has complete fresh six-phase lighting. All 124 ordinary receivers and all 141 source/engine PNGs are accounted for. Its 37 native review phases pass, including five expected rejected controls, cold reimport, saved-site audit and both fourteen-room/26-leg/139-capture physics traversals. Dynamic floor rays have no misses; practicals remain at most four at time scale 1. Original source scripts, logs, runtime inputs and captures are archived. Evidence: `../export/neutral-path-full-lighting-evidence.json` and `../export/neutral-path-native-review-evidence.json`.

Five named original captures were directly inspected. Ouxiang shows repaired foreground paving, a blue-gray roof and brown timber. Qinfang/corridor atlas roofs remain green in this intermediate source. This is partial visual review, not final acceptance of all sites. M2 stationary normal-route texture allocation peaks at 52,600,513 bytes (50.16 MiB); the demo peaks at 43,512,435. These are not phone, timing or sustained measurements.

The new pavilion/wall color images are now attached to a separate saved Blender source `3a3ae253`, exporting complete GLB `59de1ca2`. The native export gate preserves every expanded geometry/UV attribute, node, material and texture/sampler contract while changing exactly two embedded images. All fifteen site exports pass; eleven are byte-identical and four have the intended image changes. Portable site libraries and linked wash packaging pass. Complete fresh lighting is running for this combined candidate. Evidence: `../export/neutral-atlas-full-preparation-evidence.json`.

A new source-palette contract accepts the actual native `59de1ca2` export, as well as the earlier CPU fixture; preceding atlas/plain colors reject. The queued 42-phase final review adds actual imported/plain shader color, atlas PBR binding and decoded swatch checks in normal and demo modes, with two corrupt-color controls. The new GDScript has not yet run; its preparation is not native color-transfer acceptance. Evidence: `../export/garden-palette-transfer-preparation-evidence.json`.

Production remains `be80374c` / saved authoring `9356f6ec`. Neither intermediate source is installed. The combined candidate still needs completed fresh lighting, native review, reexport agreement, visual inspection and recoverable adoption. Final site art/framing, six references, current phone/2020 Adreno/sustained performance, release and authenticated services remain open.

## Neutral palette and paving installed — 2026-10-09

The working source is now `59de1ca2`, with saved Blender authoring `3a3ae253`. The repaired paving, four plain neutral colors and two pavilion/wall color images are installed with complete fresh six-phase lighting. All 124 ordinary receivers and 141 source PNGs are accounted for. Normal and ORM atlas images, UV regions and geometry are retained apart from the previously controlled paving trim. Source evidence: `../export/neutral-atlas-full-lighting-evidence.json`.

All 42 native review phases pass, including seven expected rejected inputs, both fourteen-room/26-leg walks, actual imported/shader palette transfer in normal and demo modes and decoded atlas swatches. Both walks have no supported-floor ray misses, with at most four practicals at time scale 1. All 139 original hashes per walk were verified; the repository archive retains the 26 settled originals per walk, all arrival/framing/moon captures and the original reports/logs. Transient travel PNGs remain in the recorded local review folder. The density capture requested 1080×2340 but is actually 1080×1978, as checked from its PNG header. This is not a physical phone test.

Native inspection verifies the saved plain factors, packed architectural images and repaired path ownership in authoring and the stage library. The canonical default exporter reproduces all sixteen GLBs byte for byte. Seven named originals were directly viewed for this working revision: roofs are slate, timber is brown, plaster is neutral, the paving corners are repaired and CRT green is retained. This is not final all-site art acceptance. Evidence: `../export/neutral-atlas-native-review-evidence.json`.

Twenty-six targets were installed with recoverable local backups. Ten production checks pass: cold import, source contract, complete lighting, normal/demo wash, normal/demo window spill, surface materials and normal/demo palette transfer. Atlas documentation was restored after directory replacement and updated to describe the neutral palette. Runtime cameras and game logic retain the reviewed code. Evidence: `../export/neutral-atlas-working-adoption-evidence.json`.

All fourteen intermediate-source arrival views were directly inspected in desktop and portrait, with remaining issues recorded in `scene-art-review.md`. Twelve new native camera-only comparisons cover Daoxiang, Daguan and Longcui at two portrait sizes. All six proposals fit the measured architecture above the interface; composition, action/resize behavior and authored-camera synchronization remain pending, so no camera proposal is installed. See `../export/portrait-framing-comparison-evidence.json`.

Final art/framing, six references, standalone kit palette synchronization, current Android/phone/2020 Adreno/sustained performance, release and authenticated readings/history/AI/presence/social remain required. Existing Android packages are stale for this source. The full goal remains active.

## Standalone architectural kit palette installed — 2026-10-09

Pavilion, corridor, wall and rockery now use the same neutral architectural colors as the assembled garden. Four saved Blender libraries, 48 module/LOD exports, eight legacy aliases and matching Godot assets were updated. Each saved baseline reproduced all its preceding exports exactly; reopened candidates preserve native geometry, UVs, metadata and scene contracts. Export comparison checks all 39,175 indexed triangles, both UV channels and every node/material/texture binding. Only one exact packed base-color image changes per library/export; normal and ORM images remain unchanged.

The four CPU atlas checks changed from pixel-mismatch failures to passes. Missing exports now reject instead of allowing an empty directory to pass. Eleven deliberately corrupted inputs reject. Ten isolated native phases cover cold import, each kit's PBR and actual collision/connector behavior at both LODs, and wrong-color rejection. All 48 decoded imported atlases match the reviewed swatches, with actual normal and ORM channel checks. Four original kit galleries were inspected; their actual pixels are 1600×680, with a logical 1600×900 viewport. Revised and installed captures are byte-identical to those inspected originals.

204 changed kit files were installed with recoverable local backups and hash guards. All ten post-install checks pass. The assembled authoring/master, complete GLBs, site libraries/exports, runtime and lighting are hash-unchanged. Original failed diagnostic attempts and corrections are retained with completed evidence: `../export/standalone-kit-neutral-palette-evidence.json` and `reference/standalone-kit-neutral-palette/README.md`.

Standalone palette synchronization is complete. Final rock/foliage/architecture art and scene framing, six references, current phone/2020 Adreno/sustained performance, release and authenticated services remain required. The full goal stays active.

## Portrait architecture and camera actions installed — 2026-10-09

Daoxiang Farmhouse, Daguan Hall and Longcui Nunnery now have larger portrait overviews. The building silhouettes fit above the interface at 390×844 and 360×800. Longcui uses the inspected slight off-axis view with a clear title. “Look” returns from the selected detail view to the overview; viewport rotation preserves detail poses/text or restores the appropriate portrait/landscape overview. Existing desktop and Blender authored cameras are retained. This is runtime camera work; source `59de1ca2` and lighting remain unchanged.

The focused behavior regression changed from 13 failures to a pass with 15 original captures. Seven existing regressions and both full 14-room/26-leg native walks pass. Each walk has 17,581 supported floor rays, no misses/floor failures and at most four practicals at ordinary time scale 1. Actual tour captures are 1410×600 and 540×960; narrow-screen behavior is checked separately. All 139 original hashes per walk were verified, with all 26 settled originals per walk archived. Production cold import passes. Evidence: `../export/portrait-architecture-runtime-evidence.json` and `reference/portrait-architecture-runtime/README.md`.

The farmhouse, hall and nunnery settled portrait originals were inspected under normal runtime lamps. Framing and overview actions are accepted for these three rooms. Remaining ceiling/floor/backdrop treatment, foliage/rock/architecture art and other room compositions are still open, along with six references, current physical-phone/2020 Adreno/sustained budgets, release and authenticated services. Android packages remain stale. The full goal stays active.

## Hengwu foreground stone candidate prepared — 2026-10-09

Actual color-ID pixels and saved-source inspection identify Hengwu's near foreground stone and wall cap. Five native camera alternatives at three sizes retain the crowding, so a separate saved Blender candidate compacts and softens the nearest plaster stone while keeping its three holes. Only this stone and its collider change in native source fingerprints. Export comparison preserves every other node/material/image/geometry contract; fourteen other site GLBs are byte-identical. The world-anchor test rejected an initial collider error, then passed after correction. Native collider rays, actual capsule blocking and both adjacent bidirectional routes pass.

Eighteen completed unbaked original/candidate arrival, rock and book captures have verified hashes/dimensions/poses. Directly inspected originals show less stone crowding at the right edge and a clear table. These geometry comparisons disable baking in both scenes; they do not establish final lighting. Fifteen libraries and portable shared-receiver master are prepared for candidate `26033c99` / authoring `19eb386d`, with frozen inputs and an initially empty lighting folder. Complete fresh six-phase lighting is running separately. Production remains `59de1ca2` / `3a3ae253`; no candidate is installed. Evidence: `reference/hengwu-rock-preparation/README.md` and `../export/hengwu-rock-preparation-evidence.json`.

Matching lighting, native rendered/material/full-walk checks and recoverable adoption remain required, along with all remaining art/framing, six references, current physical-device/sustained budgets, release and authenticated services. The full goal stays active.

## Reference collection: 37/42 — 2026-10-09

Rockery slot 3 now has a directly inspected original image of a dark moon-gate surround, low cool fog and four warm lanterns beyond. The published Ningde project has landscape, lighting and project-level photography credits; the individual frame is not captioned. Original JPEG bytes, source limits, failed fetch diagnostics and collection-time metadata are retained. Byte/slot coverage passes at 37/42; the require-all gate correctly rejects the five remaining slots: Qinfang 1, rockery 2 and terminal 1–3. See `reference/external/rockery-gate/README.md` and `../export/moon-gate-reference-evidence.json`.

This reference does not accept production art or change assets. The compact Hengwu source remains separate with fresh lighting running and native review queued. Final all-site art/framing, current physical-phone/2020 Adreno/sustained budgets, release and authenticated services remain required. The full goal stays active.

## Hengwu source lighting and camera waits — 2026-10-09

The isolated compact-stone source `26033c99` / authoring `19eb386d` now passes all six complete fresh lighting phases, with 124 ordinary receivers and 141 original source PNGs. All 240 frozen inputs, fifteen libraries/shared-receiver master and completed logs/reports are preserved by `../export/hengwu-full-lighting-evidence.json` (537 verified archive files). Cold reimport, deliberate source/cap-policy rejection controls, native full/wash/spill bindings, default byte reproduction of all sixteen exports and stationary M2 texture inventories pass. These results do not establish physical-device or sustained budgets.

The first uncapped camera review saved six incomplete Hengwu action poses and reported five portrait resize/framing errors. Fixed render-frame waits were shorter than the timed camera animations. The tests now wait for actual tween completion with a timeout; nine exact Hengwu action poses and fifteen portrait captures pass, with no active tween at capture. Original failures and all 48 first/completed PNGs are retained in `reference/hengwu-camera-wait-review/README.md` and `../export/hengwu-camera-wait-evidence.json`. Runtime code is unchanged; only the production portrait test wait is corrected.

Three completed source-matched originals were directly inspected: desktop arrival, portrait rock and desktop book. The compact stone opens more of the court edge; table and holes remain readable. Rock/roof clipping, wall cap, ceiling, facade filtering and final all-site art remain open. Adjacent courtyard/farmhouse and other route/UI checks pass; both full native walks and final palette controls are running or pending. No candidate is installed: production remains `59de1ca2` / `3a3ae253`. Five references, target-device/sustained budgets, release and authenticated services remain required. The full goal stays active.


## Hengwu stone and matching lighting installed — 2026-10-09

The current working source is `26033c99`, with saved Blender authoring `19eb386d`. Hengwu's closest pierced stone is narrower and lower, with smoother faces and a small bevel. Its collider stays anchored to the original floor position. The table, four stools, two other stones, cameras and fourteen other site GLBs are preserved. Canonical default export reproduces all sixteen GLBs exactly.

All six source-lighting phases passed, covering 124 ordinary receivers and 141 source PNGs. The combined review has 47 completed checks and seven deliberately rejected inputs. Both native Mac walks cover fourteen rooms, twenty-six legs and 139 original captures each, with 17,582 supported grounded samples, no floor misses and at most four practical lights at time scale 1. All 278 walk originals are archived. The first incomplete camera captures and portrait failures remain preserved; the corrected test waits for actual tween completion. Game runtime code is unchanged.

Twenty-two targets were installed using checked staging hashes and local backups. Eleven checks on the installed project passed: import, source contract, complete lighting, both backdrop modes, both terminal-spill modes, surface materials, both palette modes and portrait architecture behavior. All nine completed Hengwu action originals and four settled walk originals were inspected. Evidence: `reference/hengwu-native-review/README.md` and `../export/hengwu-native-review-evidence.json`.

The smaller stone reveals more court, but narrow book/rock framing, roof cropping, the foreground wall cap and facade lighting still need work. This is incremental scene progress, not final all-site art acceptance. Mac stationary normal allocation peaks at 52,600,513 bytes and demo at 43,512,435 bytes; phone, sustained and frame timing remain unverified for this source. Android packages are stale. Five reference slots, remaining site art/framing, physical-device/2020 Adreno budgets, release and authenticated services remain required. The full goal stays active.


## Hengwu portrait details — 2026-10-09

Runtime `3d157a7b` now frames the nearest stone and full book/tabletop above portrait controls. Rotation restores the original desktop details, resize preserves their text, and Look restores the courtyard overview. The 128-unit portrait action list preserves 48-unit touch targets and scrolling to the last action. Source `26033c99`, authoring `19eb386d` and all 282 source/engine lighting PNGs remain unchanged.

Actual public-action checks went from eight baseline failures to zero. Two narrow touch failures and two density/header failures were corrected. All three final graphical modes pass with thirty originals, and ten adjacent import/route/UI/camera/demo regressions pass. Evidence retains all 174 originals from comparison, failure and passing stages, with 269 checked files: `reference/hengwu-detail-framing/README.md` and `../export/hengwu-detail-framing-evidence.json`. Eight final original stone/book frames were inspected. One native command timed out before captures; its cause is unproven and its diagnostics are retained.

Desktop density windows were host-clamped, so these are not physical-phone checks. The preceding full walks used the previous runtime. Hengwu arrival wall cap, roof crop and facade lighting, other site art, five references, device/sustained budgets, release and authenticated services remain open. Android packages are stale. The full goal stays active.


## Hilltop portrait arrival and garden overlook — 2026-10-09

Runtime `995707af` keeps Tubi's complete moon, hall/title and stairs above portrait controls. The overlook camera is higher, exposing the central bridge pavilion beyond the nearer roof. Resize preserves the selected overlook and text; rotation restores the original desktop arrival; Look returns to the hall. A stable 128-unit portrait scroll reserve prevents button wrapping from changing the composition and preserves 48-unit touch targets.

The actual public-action baseline had 29 failures. The first candidate passed normal/touch modes but failed two density return/Look stair-clearance checks; the diagnostic recorded list growth from 100 to 128 units. Three final graphical modes pass with thirty originals. Thirteen adjacent regressions, including the actual hilltop climb/descent, also pass. The archive retains 215 original PNGs and 312 checked files. Original evidence and the final adjacent-regression results are indexed in `reference/tubi-portrait-framing/README.md` and `../export/tubi-portrait-framing-evidence.json`. Seven final frames were directly inspected.

Saved authoring `19eb386d`, complete source `26033c99` and all 282 source/engine lighting PNGs were rechecked unchanged. Desktop density windows are host-clamped, and Android packages remain stale. Small ceiling strips, stage/backdrop/ground edges, coarse surfaces and final scene art remain open, as do other sites, five references, physical-phone/2020 Adreno and sustained budgets, release and authenticated services. The full goal stays active.


## Bulletin hall overview and screen banks — 2026-10-09

Runtime `6c80b98a` fits the complete Qiushuang facade in portrait and brings each four-monitor bank closer through its public action. Resize preserves the selected bank and text; rotation restores the original desktop arrival or bank pose; Look restores the overview. A stable 128-unit portrait action area preserves 48-unit touch targets and scrolling to the final action.

The actual baseline failed 22 assertions. Three final graphical modes pass with 54 originals, and fourteen adjacent import/source, actual bulletin approach/return and hilltop climb/descent, route/UI/demo and camera regressions pass. Eight final originals were directly inspected. The evidence archive retains all 273 comparison, rejected, failing and final/regression originals in 352 checked files: `reference/qiushuang-screen-framing/README.md` and `../export/qiushuang-screen-framing-evidence.json`. Whole-batch boxes were too conservative for the roof; the final test projects all 30,987 actual facade vertices. Four-monitor rack bounds and original-image visibility review remain distinct checks.

Saved authoring `19eb386d`, complete export/engine source `26033c99` and all 282 source/engine lightmap PNGs were rehashed unchanged. No new full fourteen-room walk or physical-phone acceptance is claimed. Desktop density windows are host-clamped; Android packages are stale. Lattice/text intersections, bright/mottled walls, broad ceiling/ground areas, stage/background closure and other site art remain open, as do five references, current physical-phone/2020 Adreno and sustained budgets, release and authenticated services. The full goal stays active.


## Neutral water and atmosphere — 2026-10-09

The engine stream water is slate-blue, ambient fill is neutral, distance fog is blue-gray, and the pond reflection no longer boosts green. Amber windows and lanterns remain distinct. The actual attached stage fog was already neutral and is unchanged. Saved Blender water material parity remains part of the final source-art pass.

Eleven native review phases pass. All 28 current desktop/portrait arrival originals across fourteen rooms were directly inspected. Separate fixed-clock controls verify moving water, actual live fog and reflected window geometry/ripples. The immutable archive preserves 201 original PNGs in 276 checked files, including preliminary comparisons, the failed environment lookup and rejected zero-capture clock run: `reference/neutral-water-runtime/README.md` and `../export/neutral-water-runtime-evidence.json`. Eight unused legacy-fog negative controls have exactly equal decoded pixels.

Saved authoring `19eb386d`, complete export/engine source `26033c99`, runtime route `6c80b98a` and all 282 source/engine lightmap PNGs remain unchanged. No new full moving walk or physical-phone/sustained acceptance is claimed. Island sides, portrait bridge framing, coarse foliage, wall mottling, lattice/text intersections and stage/ground/backdrop closure remain open, along with five references, device budgets, release and authenticated services. Android packages are stale. The full goal remains active.


## Reed island portrait framing — 2026-10-09

Runtime `ba6410c0` keeps the complete island, footbridge, both reed-detail silhouettes and distant Ouxiang pavilion roof above portrait controls. Resize preserves the Watch the reeds text; rotation restores the original desktop arrival; Look restores arrival text. No new UI reserve was needed, and touch actions/input remain at least 48 logical units with scrolling to the return action.

The actual baseline failed 50 assertions. Three final graphical modes pass with thirty originals; ten adjacent source/import, actual western approach/island/return, mobile UI and pond/Ouxiang/Hengwu/architecture/Tubi/Qiushuang camera regressions pass. Eight final originals were directly inspected. All 161 comparison, baseline, focused and regression originals are preserved in 248 checked files: `reference/ziling-portrait-framing/README.md` and `../export/ziling-portrait-framing-evidence.json`. The final test projects all actual island/bridge/roof vertices and both reed LODs; early lower-LOD-only probes and rejected ceiling/roof-clipped compositions remain qualified in the archive.

Saved authoring `19eb386d`, complete source `26033c99`, all 282 source/engine lighting PNGs and the installed palette remain unchanged. Density windows are desktop-host-clamped; Android packages are stale. No new complete moving tour or phone/sustained acceptance is claimed. Black island sides, coarse reeds/lotus, stream boundaries, stage/ground/enclosure edges and final source/desktop/all-site art remain open, along with five reference slots, physical-phone/2020 Adreno and sustained budgets, release and authenticated services. Reference coverage stays 37/42 with all fourteen current sheet hashes. The full goal stays active.
