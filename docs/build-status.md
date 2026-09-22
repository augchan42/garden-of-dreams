# Build status — 2026-09-23

The first modelling pass is saved and exported. It does not yet satisfy every production requirement in the scene spec.

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
