# Godot import

Target selected by the user: Godot. Recommended editor: Godot 4.7.2 Standard on macOS; use the .NET edition only when choosing C# for game code. Both editions can import the same GLB assets.

1. Copy `export/garden-of-dreams.glb` into the Godot project. Alternatively copy selected `export/sites/SITE_*.glb` files; all retain master coordinates, so instantiate them at the origin. Include `SITE_stage.glb` once.
2. Leave import name suffix handling enabled. Collision-only nodes end in `-colonly`, which Godot uses to create collision without visible geometry. Verify floor and tunnel collision before adding navigation.
3. Keep custom properties enabled. `TRG_*` nodes contain `room_id` and `trigger_size` in glTF extras. The game must convert these markers to its own room/trigger system; these assets contain no gameplay code.
4. Create an inherited scene for lighting and WorldEnvironment settings. Tune fog, exposure and bloom against the graded reference images. Fog-card scrolling is metadata only; water is a static material awaiting a Godot shader.
5. Import the supplied LUT through the chosen Godot color-correction workflow. No `.cube` importer or color-correction resource has been bundled or tested here.
6. Set a 2.35:1 viewport for reference cameras. glTF camera data does not force the game viewport aspect ratio.
7. Bake lighting in the engine or finish the Blender bake. Disable distant real-time lamps and enforce the four-nearest-practicals budget in the game.
8. Use `_LOD1.glb` kit variants as explicit lower-detail alternatives. Decimation targets 40% for meshes with more than six polygons; small meshes remain unchanged. Godot distance switching is not configured.

Source documentation: [Godot downloads](https://godotengine.org/download/macos/), [import configuration](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html), [collision import hints](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/node_type_customization.html).

The bundled project uses `garden_import.gd` as its post-import script to calibrate photometric GLB light values for Godot Compatibility rendering. Keep that script assigned when reimporting; raw physical intensities previously washed out the viewport. `build_preview.gd` creates a separately owned `PreviewCamera` so its current-camera setting persists in the saved scene.

## Animated surfaces

The post-import hook maps `MAT_water` to `materials/water.tres` and `MAT_fog_plane` to `materials/floor_fog.tres`. Both are shared resources, so shader changes propagate without regenerating geometry. Changes to the hook itself require a scene reimport; touching an unchanged GLB may be skipped by the import cache.

Run `tests/test_surface_materials.gd` after reimport, rebuild `garden_preview.tscn` with `build_preview.gd`, then run `tests/render_surfaces.gd` using the graphical renderer and `python3 scripts/verify_surface_animation.py`. The render test pins `timeline_time` and changes water/fog phases separately; normal gameplay uses Godot's clock (`timeline_time = -1`).

Shader built-ins and render modes follow the [Godot 4.7 spatial shader reference](https://docs.godotengine.org/en/4.7/tutorials/shaders/shader_reference/spatial_shader.html).

## Color grade

`runtime/color_grade.tscn` applies the shipped cube after 3D rendering, before the command UI. Layer 1 is reserved for grading and layer 2 for controls. The material uses a screen-reading CanvasItem shader following Godot's [custom post-processing documentation](https://docs.godotengine.org/en/4.5/tutorials/shaders/custom_postprocessing.html). The atlas sampler treats pixels as numeric LUT data, not a color texture requiring conversion.

Regenerate the atlas with `python3 scripts/make_grade_atlas.py`. Run `tests/render_grade.gd` with the graphical renderer, then `python3 scripts/verify_engine_grade.py` to verify the full color transform and UI separation. Evidence is saved in `godot/grade-validation.json`.
