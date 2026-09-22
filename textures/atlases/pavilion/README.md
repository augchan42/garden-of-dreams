# Pavilion PBR atlas

Three original 2048 × 2048 PNG maps share one UV layout: base color (sRGB), tangent normal (linear), and ORM (linear: red unoccluded, green roughness, blue metallic). This single architectural atlas set is shared by the pavilion and corridor kits. Its existing filenames retain the pavilion prefix. No external artwork is used.

Reproduce with `python3 scripts/generate_pavilion_atlas.py` (seed 7341). Four quadrants contain lacquer wood, roof tile, plaster stone and bronze. Each used UV rectangle has 32 pixels of edge padding. The textures retain the stock palette and add restrained grain, mottling and roughness variation. `atlas.json` records regions, source checksums and provenance.

The Blender kit builder applies these maps using `scripts/pavilion_material.py`. UV0 is remapped per original material; the lightmap channel is unchanged. All maps are packed into the Blender file and embedded in each glTF export. No procedural shader nodes are required at runtime.

After importing the GLBs in Godot, run `python3 scripts/configure_pavilion_imports.py`, then import again. This keeps 2048 resolution and mipmaps while enabling GPU compression for extracted kit/assembly textures. The generated copies in individual standalone assets duplicate disk data; the garden assembly uses one shared material and texture set. Mobile export formats and target-device performance still need verification.
