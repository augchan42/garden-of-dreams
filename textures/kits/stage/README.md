# Original stage artwork

`scripts/make_stage_art.py` generates the 2048px color/ORM atlas and three 4096px painted-set skies with a fixed seed of 1978. Timber grain and material maps are procedural raster art. Each sky has a gradient, three brushed mountain layers and a pale painted moon. The moon's texture width compensates for the curved canvas's physical aspect ratio. Moonlit uses slate blue; dusk uses plum and amber; mist uses warm gray and blue. No external photographs, source images or fonts are included.

The source paintings are intentionally visible set art. They are production assets, not the sourced Shaw/architectural reference stills required by the site sheets. Godot imports compressed mipmapped skies at 1024px and atlas color/ORM at 512/256px. The source files keep their original resolution.

The fog module reuses `godot/materials/fog-mask.png` and the existing scrolling shader. The gel is a plain alpha-blended material rather than another texture. Blender sources use Principled materials; Godot provides unshaded sky/black materials and animated fog.

Regenerate art with `python3 scripts/make_stage_art.py`, then build geometry with `scripts/complete_stage_kit.py` in background Blender. Copy exports and maps to the matching Godot directories and retain their tracked import settings. Details and reviewed renders: `docs/kits/stage.md`.
