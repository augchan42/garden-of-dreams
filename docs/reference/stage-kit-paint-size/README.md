# Standalone stage paint export size

The seven stage modules retain their existing geometry and editable paintings. Their delivered GLBs now embed 2048 px cyclorama paint, matching the kit texture target. The three original 4096 px paintings and editable Blender library remain unchanged in production.

![Current stage modules](native-installed/stage-kit.png)

![Moonlit paint in the raw candidate](native-raw/candidate-moonlit.png)

The current export recipe reproduces all fourteen preceding GLBs exactly. Its corrected recipe reproduces all sixteen new GLBs, including two legacy aliases, exactly. Expanded indices, vertex attributes, UVs, normals, nodes, material settings, scenes and nonpaint image bytes are preserved. Six variant GLBs and two aliases change only their paint payload and corresponding buffer layout. The fourteen variant files shrink from48,311,736 to21,993,976bytes; all sixteen delivered files shrink from63287680 to28297464bytes. This is an asset-size reduction, not measured phone performance.

The actual source inspection checks140 objects,68 meshes and all three packed4096 paintings across installed, baseline and candidate source files. An injected export failure restores the original image links and bytes and removes temporary copies. The production source library is retained byte for byte. The assembled garden source/engine remain7fb3bbc1 and runtimeec42ec55; source lighting is unchanged.

Actual raw native imports verify4096paint bindings before and2048after, with one image shared by base color and emission. All six raw before/after originals were directly inspected for colors, contours, moon and brushwork. Existing Godot material overrides still use1024px paint. Both native resource/collision checks pass14 models/22 shared surfaces/54 colliders. All eight fixed-clock native gallery images match byte for byte, and eight installed originals match the candidate. These eight originals were directly inspected.

The first gallery comparison had two small animated-fog differences; the other six views matched. The fixed-clock root-window runs then timed out with partial images, including one90-second run. Those runs and original files remain retained and unaccepted. The complete comparison uses the same geometry, cameras and materials in an always-updating native SubViewport with an explicit draw, independent of the root-window draw signal. Each complete gallery finishes in about ten seconds. This establishes standalone render equality; it does not resolve or claim root-window timing or target-device performance.

All nine current kit verifiers pass. The inventory independently checks60 named variants/120 LOD exports and byte-identical Godot copies. Every actual material-bound kit atlas and paint image decodes at2048; the special fog mask remains512. This establishes the delivered inventory and texture dimensions, not source reproduction for all nine kits, final site art, texture allocation or device acceptance. The26 Python tests pass.

The initial independent inventory check incorrectly treated the512fog mask as a2048atlas; the corrected role-aware check retains the fog mask and fixes the actual oversized paint exports. An export comparison initially expected renamed image records; the exporter retains their original names. The stricter successful comparison preserves all JSON except buffer lengths/offsets. Both failed controls are retained.

Final fourteen-site art, five missing references, Aojing ground adoption, current phone/2020 Adreno/sustained budgets, release and authenticated services remain open. The current offline APK predates this kit input change and must be rebuilt before claiming current provenance. User editor sessions were not reloaded.

Run `python3 scripts/verify_stage_kit.py` for the complete source export checks. Run `res://tests/test_stage_kit.gd` for native resources/collisions and `res://tests/render_stage_kit_offscreen.gd -- --output=<directory>` for the fixed native gallery. All published files except this manifest are hashed in `files.json`.

A fresh-context GPT-6.1 Sol medium whole-branch review found no actionable issues. It independently verified136 published hashes,16 delivered GLBs,six preserved source/runtime hashes and24 gallery originals. Native and device tests were not repeated by the reviewer.
