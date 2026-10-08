"""Read spill PNGs at native precision and verify decoded physical maxima."""
import hashlib
import json
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'export/lightmaps/terminal-spill'
manifest = json.loads((source / 'manifest.json').read_text())
report = {}
for name, record in manifest['records'].items():
    path = source / record['texture']
    image = bpy.data.images.load(str(path), check_existing=False)
    image.colorspace_settings.name = 'Non-Color'
    pixels = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(pixels)
    rgb = pixels.reshape(-1, 4)[:, :3]
    assert np.isfinite(rgb).all() and rgb.min() >= 0 and rgb.max() <= 1
    if record['linear_max'] > 1e-12:
        assert abs(float(rgb.max()) - 1) < 1e-5
    else:
        assert rgb.max() == 0
    report[name] = {
        'png_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'normalized_max': float(rgb.max()),
        'decoded_linear_max': float(rgb.max()) * record['scale'],
        'finite': True,
    }
    assert report[name]['png_sha256'] == record['png_sha256']
    assert abs(report[name]['decoded_linear_max'] - record['linear_max']) < 1e-10
    bpy.data.images.remove(image)
(ROOT / 'export/terminal-spill-pixels.json').write_text(json.dumps(report, indent=2) + '\n')
print('TERMINAL_SPILL_PIXEL_PASS', len(report), 'native normalized PNGs decode to original physical maxima')
