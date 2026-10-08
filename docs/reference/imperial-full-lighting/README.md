# Imperial roof working-scene adoption — 2026-10-08

Production GLB is `361a67c7`; saved authoring remains `9356f6ec`. Only the
imperial roof export's secondary UV allocation changes. The complete source
has fresh matching ordinary, wash and terminal-spill lighting: all six native
bake/pixel/coverage phases passed. Earlier preparation remains separately
recorded in `../imperial-full-preparation/`; it is not final bake evidence.

The first engine run passed 17 phases, then failed its generic 256px roof cap.
Its report, runner, gate and log are retained. An explicit candidate option
checks the exact verified roof UV hash, lossless 512 import settings, disabled
mipmaps, actual 512² RGB8 image and 786,432 decoded bytes. The default 256 cap
still rejects. Resuming the unchanged fixture passed all remaining checks.
The derived accepted report combines 31 actually executed successful phases;
it links both original reports and retains the default-policy rejection.

Cold reimport preserves scene/collision/camera contracts. Corrupted camera,
collider and marker controls reject. Saved 14 site sources agree with authoring.
All 124 ordinary receivers, shared wash and terminal spill checks pass. Both
native 14-room walks cover 26 legs and 139 captures, with 17,582/17,581 supported
floor rays and no centre-ray misses. All 278 original walk PNG hashes verify.

Actual M2Max normal renderer texture allocation is 51,512,354bytes (49.1 MiB);
active image data is 35,771,918bytes. Demo allocation is 43,468,745bytes. These
measurements do not prove phone or sustained performance acceptance.

The default Blender exporter reproduces the complete GLB and all 15 site GLBs
byte for byte, retaining the option to disable imperial tile charts. The
verified 24-item working bundle is installed with recoverable local backups;
production import, source contract, full lighting, wash and spill checks pass.
Use `configure_lightmap_imports.py --size-limit 256 --imperial-lossless512`
and `test_full_scene_lighting.gd -- --imperial-lossless512` for this bundle.

Direct desktop/portrait comparisons and settled walk views show narrower lit
roof ribs. Facade mottling, dark eave joins, final materials/palette and camera
framing remain open. Only named originals were visually reviewed here.

Final art, 16 missing references, current Android packaging/device profiling,
2020 Adreno/sustained budgets and authenticated readings/history/AI/presence/
social remain required. This checkpoint does not complete the Garden goal.
