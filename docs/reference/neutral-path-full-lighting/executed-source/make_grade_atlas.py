"""Pack the authoritative 32-cube LUT into a horizontal slice atlas for Godot."""
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
rows=[list(map(float,s.split())) for s in (root/'grade/tech-noir.cube').read_text().splitlines() if s and s[0].isdigit()]
lut=np.array(rows).reshape(32,32,32,3) # blue, green, red
atlas=np.concatenate([lut[b] for b in range(32)],axis=1)
Image.fromarray(np.uint8(np.round(np.clip(atlas,0,1)*255))).save(root/'godot/materials/tech-noir-atlas.png')
print('32-cube atlas saved (1024 × 32)')
