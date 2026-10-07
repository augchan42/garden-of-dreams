"""Original slate-blue brushwork for the three physical painted mountain flats.

One 4096px atlas retains the editable source resolution. Strokes and pigment
variation are deterministic original raster art, following the stage-art kit.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SIZE = 4096
SEED = 7419
PALETTES = [(0.038, 0.041, 0.048), (0.050, 0.057, 0.070), (0.065, 0.073, 0.088)]


def srgb(linear):
    return np.where(linear <= .0031308, linear * 12.92,
                    1.055 * np.maximum(linear, 0) ** (1 / 2.4) - .055)


def build():
    folder = ROOT / 'textures/backdrops/mountain-paint'
    folder.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    canvas = Image.new('RGB', (SIZE, SIZE))
    regions = {}
    means = {}
    for index, palette in enumerate(PALETTES):
        top, bottom = index * SIZE // 3, (index + 1) * SIZE // 3
        height = bottom - top
        y, x = np.mgrid[:height, :SIZE]
        coarse = np.asarray(Image.fromarray(rng.integers(0, 256, (12, 48), dtype=np.uint8))
                            .resize((SIZE, height), Image.Resampling.BICUBIC), dtype=np.float32) / 255 - .5
        pigment = 1 + coarse * .16 + .022 * np.sin(y * .035 + np.sin(x * .008) * 3)
        pigment += rng.normal(0, .005, (height, SIZE))
        linear = np.asarray(palette)[None, None, :] * pigment[:, :, None]
        band = Image.fromarray(np.rint(np.clip(srgb(linear), 0, 1) * 255).astype(np.uint8))
        draw = ImageDraw.Draw(band)
        for stroke in range(850):
            px = int(rng.integers(0, SIZE))
            py = int(rng.integers(16, height - 16))
            length = int(rng.integers(18, 160))
            slope = int(rng.integers(-22, 23))
            shade = np.asarray(palette) * float(rng.uniform(.89, 1.11))
            color = tuple(np.rint(srgb(shade) * 255).astype(np.uint8))
            draw.line((px, py, px + length, py + slope), fill=color,
                      width=int(rng.integers(2, 9)))
        canvas.paste(band, (0, top))
        padding = 16 / SIZE
        regions['MAT_painted_mountains_' + str(index)] = [
            0, 1 - bottom / SIZE + padding, 1, height / SIZE - 2 * padding]
        pixels = np.asarray(band, dtype=np.float64) / 255
        decoded = np.where(pixels <= .04045, pixels / 12.92, ((pixels + .055) / 1.055) ** 2.4)
        means[str(index)] = decoded.mean(axis=(0, 1)).tolist()
        assert np.all(decoded[:, :, 1] <= (decoded[:, :, 0] + decoded[:, :, 2]) / 2 + .001)
    path = folder / 'mountain-paint.png'
    canvas.save(path)
    manifest = {'size': [SIZE, SIZE], 'seed': SEED, 'emission_strength': .6,
                'linear_palettes': PALETTES, 'mean_linear_rgb': means, 'uv_regions': regions,
                'png_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'provenance': 'Original deterministic raster brush strokes and pigment variation. No external images.'}
    (folder / 'atlas.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('MOUNTAIN_PAINT_ART_PASS', SIZE, 'shared atlas; three slate palettes')


if __name__ == '__main__':
    build()
