# Aojing pond reflection

The runtime uses a mirrored Camera3D and a shared-world SubViewport. `runtime/pond_reflection.gd` reserves render layer 20 for the Aojing hall and distant painted scenery. The pond and stage floor are excluded from that layer, so the capture cannot sample itself or be blocked by the studio floor beneath the water. Other nearby buildings are not included in this selective reflection pass.

The camera mirrors its position, target and up vector around Y = -1.1 m. The pond shader projects world positions through the reflected camera matrix, samples the capture, applies a green tint and distorts the sample with two moving normal-map layers. It synchronizes before drawing so camera tweens do not leave the capture one frame behind. Capture size is capped at 768 pixels on its longest side. Updates stop when the visitor is over 18 m from the ledge or the viewing camera is below the water.

Godot references: [Camera3D projection and cull masks](https://docs.godotengine.org/en/4.4/classes/class_camera3d.html), [Viewport worlds and render layers](https://github.com/godotengine/godot-docs/blob/master/tutorials/rendering/viewports.rst).

## Verification

- `tests/test_planar_reflection.gd`: dedicated pond batch, reflected camera height, capture mask, viewport texture and distance gating.
- `tests/render_reflection_validation.gd` followed by `python3 scripts/verify_reflection.py`: fixed-time comparisons. Disabling reflection changes 85,856 pixels; excluding the source window only from the capture changes 1,161 pixels in its reflected image. Advancing ripple time changes 4,273 pixels. The comparisons use the projected pond quad. Pixels outside the pond, HUD text, buttons and input stay within the three-level tolerance; the translucent panel background can show ripple changes behind it.
- `tests/render_reflection.gd` with and without `--mobile`: desktop and 390 × 844 views show the window and roof reflection. Arrival framing remains part of the final camera/art review; this does not establish full site acceptance.
- `tests/profile_reflection.gd`: on this Apple M2 Max, stationary median frame interval was 8.406 ms with capture active and 8.133 ms frozen. Capture reports 13 visible draw calls and zero additional shadow draws in that measurement, at 768 × 326. Total texture memory was 59,165,348 bytes. These are desktop measurements with dynamic lighting, not phone GPU results or final whole-garden budget acceptance.

The general garden profiler now records reflection capture draw calls separately and includes them in a combined upper bound. Previous profile files predate this pass. Final lighting, fresh bakes, source camera alignment and the site's water-dominant composition still require review.


## Runtime framing — 2026-10-04

Arrival and “Look across the pond” now share a centered shot. Desktop uses position (26, 4, 24), target (26, -2.5, 14), and 70° vertical FOV. Portrait uses position (26, 4, 23), target (26, -4.5, 14), and 55° horizontal FOV, without the generic portrait pullback. The whole roof is visible in the desktop frame, with the amber window and its reflected image above the controls. Portrait removes the former large empty sky area and keeps the reflected title/window above the controls. Other arrivals restore their 55° FOV.

The six arrival/door/water captures and four deterministic comparison captures are refreshed. Desktop and portrait mirrored projection checks pass. The reviewed shots are now stored in Blender and the runtime reads them from the imported cameras. The requested final water-dominant establishing composition remains open. This pass is a runtime framing improvement, not final site acceptance.


## Editable camera agreement

`align_reflection_cameras.py` stores both reviewed shots and separate scene render sizes in `blender/sites/SITE_aojing-guan.blend`. Camera extras specify viewport, FOV and which dimension to preserve. `export_garden.py` applies those per-camera projections to glTF; this avoids giving the portrait camera the exporter scene's landscape aspect. The runtime converts the imported vertical FOV to horizontal FOV for its portrait camera.

`test_reflection_camera_alignment.gd` checks the imported and runtime camera transforms and compares projected window/pond coordinates at both render sizes. It also checks mirrored projection and FOV restoration at the next site. The pass changes only camera records in the exported scene: `export/reflection-camera-alignment.json` verifies identical binary geometry/images, mesh/material/texture records and collision/trigger/light records against the predecessor export.
