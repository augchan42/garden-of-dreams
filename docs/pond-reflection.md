# Aojing pond reflection

The runtime uses a mirrored Camera3D and a shared-world SubViewport. `runtime/pond_reflection.gd` reserves render layer 20 for the Aojing hall and distant painted scenery. The pond and stage floor are excluded from that layer, so the capture cannot sample itself or be blocked by the studio floor beneath the water. Other nearby buildings are not included in this selective reflection pass.

The camera mirrors its position, target and up vector around Y = -1.1 m. The pond shader projects world positions through the reflected camera matrix, samples the capture, applies a green tint and distorts the sample with two moving normal-map layers. It synchronizes before drawing so camera tweens do not leave the capture one frame behind. Capture size is capped at 768 pixels on its longest side. Updates stop when the visitor is over 18 m from the ledge or the viewing camera is below the water.

Godot references: [Camera3D projection and cull masks](https://docs.godotengine.org/en/4.4/classes/class_camera3d.html), [Viewport worlds and render layers](https://github.com/godotengine/godot-docs/blob/master/tutorials/rendering/viewports.rst).

## Verification

- `tests/test_planar_reflection.gd`: dedicated pond batch, reflected camera height, capture mask, viewport texture and distance gating.
- `tests/render_reflection_validation.gd` followed by `python3 scripts/verify_reflection.py`: fixed-time comparisons. Disabling reflection changes 68,810 pixels; excluding the source window only from the capture changes 2,456 pixels in its reflected image. Advancing ripple time changes 1,797 pixels. The visible hall and control regions stay unchanged above the comparison tolerance.
- `tests/render_reflection.gd` with and without `--mobile`: desktop and 390 × 844 views show the window and roof reflection. Arrival framing remains part of the final camera/art review; this does not establish full site acceptance.
- `tests/profile_reflection.gd`: on this Apple M2 Max, stationary median frame interval was 5.736 ms with capture active and 4.797 ms frozen. Capture reports 12 visible draw calls and zero additional shadow draws in that measurement, at 768 × 326. Total texture memory was 27,422,271 bytes. These are desktop measurements with dynamic lighting, not phone GPU results or final whole-garden budget acceptance.

The general garden profiler now records reflection capture draw calls separately and includes them in a combined upper bound. Previous profile files predate this pass. Final lighting, fresh bakes, source camera alignment and the site's water-dominant composition still require review.
