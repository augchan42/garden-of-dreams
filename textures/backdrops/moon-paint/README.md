# Original moon painting

`moon-paint.png` is original imagery generated with the built-in image tool for this project. The requested square warm ivory scenic-paint texture has soft gray-blue washes and dry-brush/canvas detail, flat lighting and no stars, glow, silhouette, text or green pigment. The generated original is 1254 × 1254; it is retained without resizing. Full prompt summary, source path and PNG hash are in `provenance.json`. The physical moon mesh supplies its circular silhouette.

`atlas.json` decodes the original sRGB PNG into linear RGB and averages the central unit-circle region. Separate scalar base/emission factors preserve the preceding moon's mean linear base luminance (0.574064) and emitted luminance (0.3976736 at strength 0.8). This is a sampled texture calibration, not proof of whole-scene illumination, palette or art acceptance.

The native authoring script adds one projected primary UV channel and one shared packed image, with separate source multiply factors for base and emission. Source geometry, transforms, materials outside the moon, lighting, camera/collision/marker properties remain protected. Native/glTF/runtime checks, actual source render and genuinely fresh lighting are required before engine adoption. Godot should import the retained original at a 512px mipmapped limit after rendered transfer checks.
