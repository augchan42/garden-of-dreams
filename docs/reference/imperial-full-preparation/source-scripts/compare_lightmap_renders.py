"""Measure fixed-time render differences; visual acceptance remains separate."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
references = root / 'docs/reference'
baseline = sorted(references.glob('baked-*-uncompressed.png'))
assert len(baseline) == 15, 'Render the complete fixed-time baseline first'
report = {'scope': 'Desktop authored views at fixed shader time. Not close-up UV, motion or mobile acceptance.', 'variants': {}}
for variant in ['compressed-1024', 'compressed-512']:
    views = {}
    for path in baseline:
        target = references / path.name.replace('uncompressed', variant)
        a = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32)
        b = np.asarray(Image.open(target).convert('RGB'), dtype=np.float32)
        assert a.shape == b.shape
        difference = np.abs(a - b)
        views[path.stem.removesuffix('-uncompressed')] = {
            'mean_channel_error_255': float(difference.mean()),
            'p99_channel_error_255': float(np.percentile(difference, 99)),
            'pixels_over_8_channel_values_percent': float(np.mean(difference.max(axis=2) > 8) * 100),
        }
    report['variants'][variant] = views
    print(variant, 'largest mean channel error:', max(x['mean_channel_error_255'] for x in views.values()))
(root / 'godot/lightmap-compression-comparison.json').write_text(json.dumps(report, indent=2)+'\n')
