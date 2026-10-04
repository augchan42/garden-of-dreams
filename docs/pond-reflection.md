# Aojing pond reflection

The runtime uses a mirrored Camera3D and a shared-world SubViewport. `runtime/pond_reflection.gd` reserves render layer 20 for the Aojing hall and distant painted scenery. The pond and stage floor are excluded from that layer, so the capture cannot sample itself or be blocked by the studio floor beneath the water. Other nearby buildings are not included in this selective reflection pass.

The camera mirrors its position, target and up vector around Y = -1.1 m. The pond shader projects world positions through the reflected camera matrix, samples the capture, applies a green tint and distorts the sample with two moving normal-map layers. It synchronizes before drawing so camera tweens do not leave the capture one frame behind. Capture size is capped at 768 pixels on its longest side. Updates stop when the visitor is over 18 m from the ledge or the viewing camera is below the water.

Godot references: [Camera3D projection and cull masks](https://docs.godotengine.org/en/4.4/classes/class_camera3d.html), [Viewport worlds and render layers](https://github.com/godotengine/godot-docs/blob/master/tutorials/rendering/viewports.rst).

## Verification

- `tests/test_planar_reflection.gd`: dedicated pond batch, reflected camera height, capture mask, viewport texture and distance gating.
- `tests/render_reflection_validation.gd` followed by `python3 scripts/verify_reflection.py`: fixed-time comparisons. Disabling reflection changes 460,098 pixels; excluding the source window only from the capture changes 7,027 pixels in its reflected image. Advancing ripple time changes 94,863 pixels. The comparisons use the near-plane-clipped projected pond quad. Pixels outside the pond and the return button stay within the three-level tolerance. The command panel is hidden in this view.
- `tests/render_reflection.gd` with and without `--mobile`: desktop and 390 × 844 views show the window and roof reflection. Arrival and the separate waterline pond view are reviewed; this does not establish full site acceptance.
- `tests/profile_reflection.gd`: on this Apple M2 Max, stationary median frame interval was 7.312 ms with capture active and 6.301 ms frozen. Capture reports 13 visible draw calls and zero additional shadow draws in that measurement, at 768 × 326. Total texture memory was 58,990,586 bytes. These are desktop measurements with dynamic lighting, not phone GPU results or final whole-garden budget acceptance.

The general garden profiler now records reflection capture draw calls separately and includes them in a combined upper bound. Previous profile files predate this pass. Final lighting, later-site bakes and full scene/device performance still require work.


## Runtime framing — 2026-10-04

Arrival uses a centered shot; the later pond action uses the separate waterline view described below. Desktop uses position (26, 4, 24), target (26, -2.5, 14), and 70° vertical FOV. Portrait uses position (26, 4, 23), target (26, -4.5, 14), and 55° horizontal FOV, without the generic portrait pullback. The whole roof is visible in the desktop frame, with the amber window and its reflected image above the controls. Portrait removes the former large empty sky area and keeps the reflected title/window above the controls. Other arrivals restore their 55° FOV.

The eight arrival/door/water/return captures and four deterministic comparison captures are refreshed. Desktop and portrait mirrored projection checks pass. The reviewed shots are now stored in Blender and the runtime reads them from the imported cameras. The later waterline action view meets the half-frame water requirement. Final lighting and reference acceptance remain open.


## Editable camera agreement

`align_reflection_cameras.py` stores both reviewed shots and separate scene render sizes in `blender/sites/SITE_aojing-guan.blend`. Camera extras specify viewport, FOV and which dimension to preserve. `export_garden.py` applies those per-camera projections to glTF; this avoids giving the portrait camera the exporter scene's landscape aspect. The runtime converts the imported vertical FOV to horizontal FOV for its portrait camera.

`test_reflection_camera_alignment.gd` checks the imported and runtime camera transforms and compares projected window/pond coordinates at both render sizes. It also checks mirrored projection and FOV restoration at the next site. The pass changes only camera records in the exported scene: `export/reflection-camera-alignment.json` verifies identical binary geometry/images, mesh/material/texture records and collision/trigger/light records against the predecessor export.


## Unobstructed pond action

The pond action uses a lower camera 0.6 m above the water. A Return to ledge button and Escape restore the normal controls and arrival camera. The visitor remains on the dry ledge. The desktop and portrait action cameras are stored in Blender, exported with their own projection, and read by Godot. Arrival and pond views are separate.

`measure_pond_composition.gd` renders a white pond with black depth-testing occluders, hiding the grade/UI only during measurement. Solid alpha cards make this a conservative coverage measure. The actual return button and caption sit above the water region. Water covers 54.9% of the desktop frame and 57.0% of portrait; every roof vertex stays inside the viewport. Evidence: `godot/pond-composition.json`. `test_pond_view.gd` checks pointer entry/return, Escape, resize, authored projection, ledge position and safe next-room state.

The comparison capture clips the pond quad against the camera near plane before projecting it. It checks that changed pixels remain inside that projected water region and that the return button stays unchanged. This handles the new camera position inside the pond's near edge.

The latest desktop profile reports 819 main visible draws plus 13 capture draws, 115,470 combined visible primitives and 58,990,586 bytes of texture allocation. The 832-draw total exceeds the 150-call target. This is an unresolved full-scene lighting/rendering cost, not a passing performance gate. Static-key receiver masks and complete site lighting need review before final acceptance.

## Camera-only bake compatibility

No lighting input changed in this export. `verify_reflection_camera_export.py` compares binary geometry/images, materials/textures/accessors, all non-camera node records and scene membership, and punctual-light records against the prior GLB. `revalidate_camera_only_lightmaps.py` preserves 62 unchanged lightmaps only after those comparisons pass. Records keep their original `baked_from_source_glb_sha256` and include the compatibility proof and texture hash. This is revalidation of existing bakes, not a new Cycles render. Runtime hash guards remain enabled. Any geometry, material, light, membership or binary change makes the revalidation fail.


`diagnose_static_shadow_cost.gd` isolates the excess work. The reported main counter falls from 819 to 92 when only static-key shadows are disabled; disabling the keys entirely leaves it at 92. This confirms the shadow cost, even though the separate Compatibility shadow counter reports zero. Eleven of twelve static keys also overlap baked receiver layer 2. The diagnostic toggles are temporary and are not shipped behavior: unbaked sites still need their shadows. Finish their baked lighting and isolate baked receivers before disabling redundant static shadow work.

Static receiver isolation was tested after the pond-view release. Clearing layer 2 from Spot/Directional keys passed the 33-map adapter test and preserved the practical and linked backdrop masks. Desktop study, imperial and hilltop captures completed. Visual comparison showed that the imperial roof and bronze doors became too dark when the dynamic key contribution was removed. The correction was reverted before release; three isolated-key captures are saved under `reference/lighting-diagnostics/` as diagnostic evidence. The bake script includes both direct and indirect diffuse light, but the saved maps currently do not provide the reviewed key visibility on their own. Calibrate authored lighting and fresh bakes before installing receiver isolation or removing static shadow maps. The shipped pack retains its verified lighting.
