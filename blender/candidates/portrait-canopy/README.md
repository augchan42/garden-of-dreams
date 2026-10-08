# Painted ceiling candidate

`SITE_stage.blend` contains the planar-sky ceiling candidate. It is not the
installed stage library. The full authoring and export remain in the separate
scratch folder recorded by `/tmp/garden-canopy-planar-authoring.json`.

Recreate from the saved current source with installed Blender and
`scripts/prepare_canopy_candidate.py --output-root <separate scratch folder>`.
The tool refuses a project destination or an existing candidate. Export the
saved candidate with `scripts/export_garden.py --output-root <same folder>`,
then run `scripts/verify_canopy_candidate.py --candidate-root <same folder>`.

The library adds a 2,240-triangle coved ceiling, primary paint UVs, a copied
paint material, no-shadow intent and membership in the existing linked wash
receiver collection. Existing source objects/materials remain unchanged.
Production shadow transfer, fresh lighting and final paint are pending.
See `docs/portrait-backdrop.md` for actual native comparisons and limits.
