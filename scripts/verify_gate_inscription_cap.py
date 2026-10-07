"""Compare actual native captures and allocation before/after the import cap."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    captures = ROOT / 'docs/reference/gate-inscription-runtime-b4'
    parser.add_argument('--before', type=Path, default=captures / 'before')
    parser.add_argument('--after', type=Path, default=captures / 'after')
    parser.add_argument('--after-inventory', type=Path, default=captures / 'after')
    parser.add_argument('--output', type=Path, default=ROOT / 'export/gate-inscription-runtime-cap.json')
    args = parser.parse_args()
    before = json.loads((args.before / 'report.json').read_text())
    after = json.loads((args.after / 'report.json').read_text())
    assert before['source_glb_sha256'] == after['source_glb_sha256']
    assert not after['capture_only']
    assert len(before['textures']) == len(after['textures']) == 2
    for old, new in zip(before['textures'], after['textures']):
        assert old['source_sha256'] == new['source_sha256'], 'Original exported artwork changed'
        assert old['size'] == [2172, 724] and new['size'] == [1024, 341]
        assert old['image_format'] == new['image_format'], 'Lossless readback format changed'
    report = {'status': 'passed', 'source_glb_sha256': after['source_glb_sha256'],
              'scope': 'Same-source native lossless import, allocated-memory reduction and projected-inscription-region image comparison in four fixed-clock views. Direct review confirms arrival lettering. The diagnostic portrait close-up clips the same outer edges in both images; it is not final camera acceptance. Not proof of the pending corrected roof source or final art, atlas, traversal or phone requirements.',
              'textures_before': before['textures'], 'textures_after': after['textures'],
              'visual_limits': {'inscription_rgb_rmse': 2 / 255, 'inscription_rgb_p99': 8 / 255},
              'captures': {}, 'memory': {}}
    keys = {'desktop-arrival', 'desktop-close', 'portrait-arrival', 'portrait-close'}
    assert set(before['captures']) == set(after['captures']) == keys
    for key in sorted(keys):
        old_path, new_path = args.before / (key + '.png'), args.after / (key + '.png')
        old_record, new_record = before['captures'][key], after['captures'][key]
        old_sha = old_record['sha256'] if isinstance(old_record, dict) else old_record
        assert digest(old_path) == old_sha and digest(new_path) == new_record['sha256']
        old = np.asarray(Image.open(old_path).convert('RGB'), dtype=float) / 255
        new = np.asarray(Image.open(new_path).convert('RGB'), dtype=float) / 255
        assert old.shape == new.shape
        x0, y0, x1, y1 = new_record['inscription_rect']
        assert 0 <= x0 < x1 <= old.shape[1] and 0 <= y0 < y1 <= old.shape[0]
        error = abs(old[y0:y1, x0:x1] - new[y0:y1, x0:x1])
        rmse, p99 = float(np.sqrt(np.mean(error * error))), float(np.quantile(error, .99))
        assert rmse <= report['visual_limits']['inscription_rgb_rmse'], (key, rmse)
        assert p99 <= report['visual_limits']['inscription_rgb_p99'], (key, p99)
        report['captures'][key] = {'before_sha256': old_sha, 'after_sha256': new_record['sha256'],
                                    'inscription_rect': new_record['inscription_rect'],
                                    'inscription_rgb_rmse': rmse, 'inscription_rgb_p99': p99}
    expected_saving = sum(t['image_bytes'] for t in before['textures']) - sum(t['image_bytes'] for t in after['textures'])
    for mode in ('demo', 'normal'):
        old_path = args.before / ('runtime-texture-inventory-' + mode + '.json')
        new_path = args.after_inventory / ('runtime-texture-inventory-' + mode + '.json')
        old, new = json.loads(old_path.read_text()), json.loads(new_path.read_text())
        assert old['source_glb_sha256'] == new['source_glb_sha256'] == after['source_glb_sha256']
        assert old['unique_bound_texture_rids'] == new['unique_bound_texture_rids']
        assert len(old['views']) == len(new['views']) == (3 if mode == 'demo' else 14)
        saving = old['texture_memory_bytes'] - new['texture_memory_bytes']
        assert saving >= expected_saving * .9, (mode, saving, expected_saving)
        if mode == 'demo':
            assert new['demo_texture_target_passed'] and new['texture_memory_bytes'] <= 64 * 1024 * 1024
        report['memory'][mode] = {'before_bytes': old['texture_memory_bytes'], 'after_bytes': new['texture_memory_bytes'],
                                  'saving_bytes': saving, 'inventory_sha256': digest(new_path)}
    report['expected_image_saving_bytes'] = expected_saving
    report['native_capture_report_sha256'] = digest(args.after / 'report.json')
    report['verifier_sha256'] = digest(Path(__file__))
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('GATE_INSCRIPTION_CAP_PASS: four projected-region comparisons, same original artwork, actual demo/normal allocation reduction')


if __name__ == '__main__':
    main()
