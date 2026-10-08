# Roof-batch sampling diagnostic

The current b540496a source has thirteen named rooftop, pavilion-atlas or thatch material batches covered by this diagnostic. It reads their exact exported UV2 triangles and matching source-map sizes, and measures minimum triangle altitude in source pixels. A deliberately changed map-record source hash rejects before an output report is created; production files are unchanged.

These batches also contain beams, posts and other shared geometry. Even Qinfang's corrected batch contains many small triangles outside the 672 explicitly allocated cap triangles. Batch totals do not identify visible striping, establish raster coverage/gutters, measure imported filtering or prove that a complete roof needs replacement. Next isolate the remaining raised-cap parts and compare them with actual rendered views. No scene, lighting, import setting or final-art acceptance changes in this pass.
