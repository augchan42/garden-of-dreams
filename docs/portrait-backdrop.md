# Portrait backdrop candidate

The current garden's 20 m backdrop ends inside several portrait arrival views.
Forty native camera comparisons cover eight affected rooms. Narrower lenses
hide some gaps but crop roof bays, signs and foreground props. Moving cameras
back can put them behind walls. Those camera changes were rejected.

A separate painted ceiling joins the exact 320 front rim edges at radius
48 m and curves inward through four bands to height 38 m. Its 2,240 triangles
face inward. The current cameras, buildings, signs, colliders and moon remain
unchanged. The selected candidate uses the existing moon-free upper paint with
planar UVs above the first band; the original wall UVs remain at the join.
This reduces the first version's radial paint streaks. Paint and lighting at
the join still need work.

The candidate library is `blender/candidates/portrait-canopy/SITE_stage.blend`.
It is separate from the installed scene. Preparation preserves all 4,344
existing objects and all existing materials. Thirteen linked receiver lists
(including the disabled source wash) gain the ceiling; six receiver objects
replace the preceding five in this candidate only. The actual export preserves
all 708 existing node contracts, including vertex/index data, both UV channels,
embedded image bytes, material factors, cameras, lights, transforms and extras.
All fourteen other site GLBs are byte-identical. Render geometry changes from
231,216 to 233,456 triangles. These source counts are not measured draw or
visible-triangle budgets.

The actual Blender export is imported into an isolated Godot project and
captured with all fourteen unchanged portrait arrival cameras. Old site and
wash bakes are disabled. The ceiling explicitly uses the existing cyclorama's
shared unshaded paint and its no-shadow intent in the fixture. These settings
were explicit fixture overrides in that first comparison. The source
stores `visible_shadow = false` and exports `godot_cast_shadow = false`; glTF
alone does not transfer Blender ray visibility. The current import hook and
three native bake paths now restore explicit mesh shadow intent; native pixel
controls verify the flag and its effect. Shared unshaded ceiling paint also
passes an actual cold import. See `scene-adoption.md` for the current evidence.

The final coverage probe creates test-only triangle colliders on mask 128,
with no visitor collision. Each surface's culling matches its active rendered
material. Twenty-seven top-screen rays per view sample geometry coverage;
this does not verify every pixel or continuous travel. Removing the ceiling
produces 201 missed rays across the affected arrivals. Those same 201 rays hit
the actual imported ceiling when it is present; all fourteen canopy arrivals
have zero sampled misses. Earlier probes that omitted backface collisions,
then enabled them for every surface, are retained as diagnostic history.
Use `planar-surface-culling/report.json` for the final sampled coverage result.

Native imports and renders finish cleanly. Blender exports retain sampler
warnings about multiple texture nodes. Resolved existing GLB image/sampler and
material comparisons pass; new ceiling material transfer and final lighting
remain separate adoption requirements.

Raw camera, prototype, authored and planar comparisons are under
`reference/portrait-room-framing/`, indexed by
`export/portrait-backdrop-evidence.json`. Each completed probe keeps its exact
script and captured-image hashes. The first failed unindexed-mesh report is
also retained. Canonical authoring/export, production Godot and the previous
verified release are unchanged.

The floor inspection exposed coplanar overlap artifacts. A revised candidate
lifts both visible inserts and colliders by 2 mm, removes the observed artifacts
and passes the full twenty-six-leg walk. It has been combined with this ceiling
in a separate saved/exported source; that combined source is not installed.

The combined source now passes actual imported material/shadow settings,
sampled portrait coverage and the continuous twenty-six-leg physics walk. Strict
six-receiver wash support and genuine direct maps also pass. See
`ceiling-lighting.md` for source hashes and scope. Before adoption, adjust the
authored moon/paint contrast and bake complete matching lighting, then repeat
production traversal, arrival/transition renders and device/package checks.
Final moon contrast, site art, thirty missing references, authenticated room
services and full performance acceptance remain part of the active goal.
