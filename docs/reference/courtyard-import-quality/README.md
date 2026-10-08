# Courtyard import quality — 2026-10-08

The current 8d source is unchanged. Godot block compression introduces pink checks
in Xiaoxiang's baked wall and timber shadows. The actual same-resolution lossless
256 import removes the checks, establishing the compression cause independently
of resolution. The adopted lossless cap is 512: whitewash allocates 512 × 512 RGB8;
timber remains 256 × 256 because its source is that size. All 141 source PNGs,
Blender authoring, GLB, cameras, collisions, runtime and shaders retain their bytes.
Only two runtime import files changed. The import configurator preserves this rule.

The production importer, source camera/collision/marker contract, full lighting,
normal/demo wash and normal/demo spill checks pass without native errors. All four
production arrival images match the tested 512 candidate pixel for pixel. Native
normal-route texture allocation is 50,507,483 bytes on Apple M2 Max; image data is
35,018,254 bytes across 178 textures. This is neither phone performance nor the
allocation of a completed demo finale or continuous tour. Older APKs do not contain
these import settings even though they share the same GLB hash.

The wall-rectangle diagnostic counts pink display pixels in [47,410,380,192]:
compressed baseline 1.6913%, lossless 256 and 512 both 0%. It is a bounded image
heuristic, not a whole-site art judgement. Qinfang, Daoxiang and Daguan baseline
arrival pixels are identical before/after the import change.

Roof probes show that the strong roof stripes persist with full-resolution
lossless maps and appear in the irradiance component. Removing normal/specular
terms does not resolve them. The source-centroid report includes occluded geometry
and is not visibility acceptance or proof of a geometry defect. Roof lighting/art
remains unfinished; no roof geometry, paint or source lighting is changed here.

The first mask fixture emitted renderer null-material errors despite exit zero.
It is retained under rejected-mask-fixture and explicitly rejected. The repaired
roof run and wall run have no native errors. Raw reports retain temporary paths;
this archive's hash index pins their exact original bytes. Capture test clocks and
arrival placement are controlled; these runs do not establish normal movement.

Directly inspected originals in the preceding diagnostic turn: Qinfang baseline,
lossless-native, paint-only, irradiance-only and roof-mask; Bamboo baseline and
lossless-native; Daoxiang baseline, lossless-native and paint-only; Daguan baseline
and lossless-native; whitewash lossless-native, paint-only and lossless-256; lattice
lossless-256; both-map actual 256 and 512 Bamboo imports. This adoption turn also
inspected the actual production Bamboo original. Other saved originals have not
all been individually reviewed. Full-site visual acceptance stays open.
