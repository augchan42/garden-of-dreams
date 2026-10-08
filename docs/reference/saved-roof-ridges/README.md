# Saved roof topology probe

The current saved authoring scene contains one named roof object matching the diagnosed disconnected fifteen-vertex/eight-face strip topology: QINFANG_kit_roof_hex, with forty-two strips and all 336 faces pointing toward positive local Z. The source file hash remains unchanged.

This is a topology-filtered local-normal inspection, not a complete roof inventory or world-space visibility/render acceptance. Other roof shapes did not match the filter; the result does not establish their winding or imply that the Qinfang correction can be applied to all of them. Isolate those shapes separately before changing their charts or normals.

The first probe incorrectly treated the helper's MeshPolygon objects as numeric indices and exited with TypeError. The exact failed script/log and corrected successful script/log remain here. Neither run saved the scene.
