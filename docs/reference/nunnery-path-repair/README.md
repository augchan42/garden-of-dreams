# Nunnery approach paving repair candidate — 2026-10-08

The installed source remains `be80374c`. The isolated candidate `47ac858e` trims two rendered slabs against the crosspiece, eliminating 4.86m² of coplanar corner overlap. Native inspection proves all 4,359 other saved objects and all three collision proxies retain their snapshots. The walkable union is unchanged within 1e-5m source precision, checked across 99 edge/corner/open-cell membership classes.

Expanded GLB comparison preserves all 717 node contracts, lights, cameras, collisions, markers, materials and embedded images. Among 245,474 indexed triangles, only the stage plaster-rock batch POSITION and UV2 change. Exactly 36 expanded vertices move along the path direction; all 14 other site GLBs are byte-identical. The canonical construction script now keeps render slabs separate from original collision boxes.

A fresh 128-sample 1024² paving lightmap uses the candidate's exact source and UVs. Native controlled before/after renders use the production baked-diffuse adapter, the original material, production 256px import parameters and separate source-resolution1024 controls. Other geometry is flat gray, alpha-blended geometry is hidden, and lights/grade/UI/water animation are absent. Each map is checked against its own exact GLB source; no old map is relabelled.

Cyan surface-ID renders identify both formerly black pixels (34,468) and (193,512) as paving. Baseline baked256 and baked1024 give zero RGB there; the repaired versions give every channel above0.4. Both actual256 before/after originals were directly inspected. The two decoded surface-ID images differ at one pixel only, (18,495), at the joined slab edge; this is recorded rather than claiming raster identity. Continuous path coverage and unchanged collision contracts still require full-scene route checks before adoption.

This candidate has not been installed. Complete source-matched ordinary/wash/spill lighting, saved libraries, native full-scene art/framing/routes, memory/device and release acceptance remain required. The original working authoring file and user live applications were not altered.
