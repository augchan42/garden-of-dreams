"""Check outward normals on the saved hexagonal pavilion's open tile strips."""
import bpy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pavilion_roof_geometry import components
roof=bpy.data.objects['QINFANG_kit_roof_hex']
ridges=[faces for vertices,faces in components(roof.data) if len(vertices)==15 and len(faces)==8]
assert len(ridges)==42,'Expected seven raised tile strips on each of six facets'
inward=[face.index for faces in ridges for face in faces if face.normal.z<=.25]
assert not inward, f'{len(inward)} raised tile faces point inward instead of above the roof'
print('PAVILION_TILE_RIDGES_PASS: 42 strips, 336 outward faces')
