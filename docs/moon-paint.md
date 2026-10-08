# Painted moon source and transfer

The saved Blender moon now uses original warm ivory painting, amber pigment and gray-blue washes. The retained 1254 × 1254 PNG is `textures/backdrops/moon-paint/moon-paint.png`; its built-in image-generation prompt and hash are recorded beside it. The physical 5.4 m disc supplies the silhouette. No mesh positions, normals, cameras, lights, collision objects or room markers changed.

The packed sRGB image feeds separate base and emission multiply nodes. Factors preserve the sampled preceding mean linear luminance, with source emission strength 0.8. This calibration does not establish unchanged whole-scene illumination: spatial detail and emitted color changed, so a genuinely fresh complete lighting pass is required. The source Cycles inspection is under `reference/moon-paint/source/`.

The native glTF exporter drops factors from legacy MixRGB nodes. The source uses its supported RGBA Mix/Multiply nodes. A narrow export pass shares equivalent base/emission texture indices only after comparing embedded PNG bytes, sampler and UV settings. Different images reject. The final export preserves 243,042 expanded triangles, 708 node contracts and 46 unrelated materials; all fourteen other site GLBs are byte-identical. Camera, collision, unrelated material, factor, actual legacy export and image-alias corruption checks reject.

Isolated native Godot tests import the exact source export and compare its Standard material against the existing baked adapter with ordinary lighting disabled. Emissive, keyed and graded cases retain the image and linear factors, with visible missing-paint controls. These are material-transfer checks, not final baked garden appearance or performance acceptance.

At a 130 px moon diameter, a 512 px lossless mipmapped import has graded moon-region RMSE 0.007182 and p99 error 6/255 versus the untouched original. A 1024 px desktop compressed import has larger graded RMSE 0.013137 and p99 10/255. Direct inspection favors the lossless candidate. This sampled size covers the measured Mac arrival projections; larger physical phone pixels, full-scene visual quality and actual phone allocation remain unverified. No production import cap has been installed yet. The original PNG stays intact. Earlier fixture reports predate the addition of texture readback counters to the transfer test; only the compressed report records those counters.

Canonical source export is `c68f6d1eb115d167906d9fd9094b32df52cf05e2eb775e46cb07e521d20d36e2`. The saved source/library and export checks pass. All six fresh ordinary/wash/spill/pixel/coverage phases now pass, including 124 ordinary maps. Matching full/demo/priority-2/wash/spill catalogs (124/33/29/5/7) and the new source are installed in Godot. Native import is clean and thirteen current runtime/render phases pass. Both fourteen-room desktop and portrait arrival capture sets are retained. The local PCK/movie/archive still contain the preceding verified `90c4f70e…` source and need a separate package rebuild. Old maps were not relabelled compatible.

Saved raw evidence is under `reference/moon-paint/`, indexed by `export/moon-paint-evidence.json`. The user's open older Blender scene was not saved or reloaded. Physical backdrop edge exposure, final moon/site composition, remaining references, complete traversal/device performance and authenticated services remain open.


The actual current arrival views show a warm cream moon against the gray-blue
backdrop. Its brush texture appears flat at those captured sizes, so final moon
contrast still needs work. The backdrop's physical top edge remains clearly
exposed in several portrait rooms. Neither issue is accepted as final art.
Actual source/adapter paint transfer at 223 px has zero pixel difference in
emissive, keyed and graded cases, with visible missing-paint controls. The shared
original texture reads 1254 × 1254 and 6,288,054 RGB bytes in this isolated
fixture; its 6,972,438-byte renderer counter is not a whole-garden/phone budget.
No runtime paint cap is installed. Evidence is in
`export/moon-paint-current-{runtime,evidence}.json` and
`reference/moon-paint/current-garden/`.

The initial demo wash test under a forced simulation clock reported a shutdown
resource leak after its lighting assertions passed and was rejected. Verbose
forced-clock and normal-clock diagnostics did not reproduce that warning. The
final thirteen-phase runner uses the normal clock for audio/render checks and
fixed physics only for the route test; all its accepted logs are clean. The
initial failure and diagnostic logs are retained separately. This does not
establish a production audio bug or prove its absence under every schedule.
