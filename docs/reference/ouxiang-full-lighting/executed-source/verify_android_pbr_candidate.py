"""Verify repaired-renderer phone evidence and visible placed atlas comparisons."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/reference/pbr-transfer'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collection(path, edges):
    evidence = json.loads((path / 'evidence.json').read_text())
    for name, expected in evidence['files'].items():
        assert sha(path / name) == expected, 'Changed collection: ' + str(path / name)
    report = json.loads((path / 'garden-phone-profile.json').read_text())
    build = json.loads((path / 'build.json').read_text())
    assert report['status'] == 'ready_for_taps'
    assert report['source_glb_sha256'] == evidence['source_glb_sha256'] == build['source_glb_sha256']
    assert build['apk_sha256'] == evidence['apk_sha256']
    assert len(report['touch_events']) == edges
    assert all(p['status'] == 'passed' and not p['engine_diagnostics'] for p in build['phases'])
    for image, record in evidence['images'].items():
        assert sha(path / image) == record['sha256']
    return report


def compare_image(before, after):
    a = np.asarray(Image.open(before).convert('RGB'), dtype=float) / 255
    b = np.asarray(Image.open(after).convert('RGB'), dtype=float) / 255
    assert a.shape == b.shape
    delta = np.abs(a - b)
    result = {'before_sha256': sha(before), 'after_sha256': sha(after),
              'rmse': float(np.sqrt(np.mean(delta * delta))),
              'p99': float(np.quantile(delta, .99)), 'maximum': float(delta.max())}
    assert result['rmse'] < 2 / 255 and result['p99'] < 8 / 255, result
    return result


def main():
    old = collection(EVIDENCE / 'android-baseline/route', 0)
    new = collection(EVIDENCE / 'android-candidate/route', 0)
    assert old['build']['normal_atlas_size_limit'] == old['build']['orm_atlas_size_limit'] == 0
    assert not old['build']['reuse_ui_font_sizes']
    assert new['build']['normal_atlas_size_limit'] == new['build']['orm_atlas_size_limit'] == 1024
    assert new['build']['reuse_ui_font_sizes']
    for key in ['device_model', 'renderer_device', 'renderer', 'native_window_size',
                'screen_dpi', 'fps_cap', 'logical_viewport_size', 'ui_content_scale_factor', 'initial_buttons']:
        assert old[key] == new[key], 'Uncontrolled device setting: ' + key
    assert old['native_window_size'] == [1080, 2340]
    for key in ['source_glb_sha256', 'profile_script_sha256', 'inventory_script_sha256',
                'renderer_files_sha256', 'production_runtime_script_sha256',
                'normal_png_sha256', 'orm_png_sha256', 'demo_index_sha256', 'full_index_sha256',
                'inscription_import_sha256']:
        assert old['build'][key] == new['build'][key], 'Uncontrolled build setting: ' + key
    renderer = old['build']['renderer_files_sha256']
    for name, expected in renderer.items():
        assert sha(ROOT / 'godot' / name) == expected
    before_textures = {t['resource_path']: t for t in old['texture_inventory']['textures']}
    after_textures = {t['resource_path']: t for t in new['texture_inventory']['textures']}
    assert len(before_textures) == len(after_textures) == 88
    assert before_textures.keys() == after_textures.keys()
    changed = {}
    for path, before in before_textures.items():
        after = after_textures[path]
        for key in ['bindings', 'stored_format', 'mipmaps']:
            assert before[key] == after[key], (path, key)
        if path.endswith(('pavilion_normal.png', 'wall_normal.png', 'pavilion_orm.png', 'wall_orm.png')):
            assert before['size'] == [2048, 2048] and after['size'] == [1024, 1024]
            changed[path] = {'before_size': before['size'], 'after_size': after['size']}
        else:
            assert before['size'] == after['size']
            assert before['stored_format_mip_data_bytes'] == after['stored_format_mip_data_bytes']
    assert len(changed) == 4
    saving = old['texture_inventory']['stored_format_mip_data_bytes'] - new['texture_inventory']['stored_format_mip_data_bytes']
    assert saving == 12 * 1024 * 1024
    measured = {}
    for name, before in old['samples'].items():
        after = new['samples'][name]
        assert before['texture_memory_bytes'] - after['texture_memory_bytes'] == saving
        assert after['active_practicals_max'] <= 4 and after['visible_draw_calls_max'] <= 150
        assert after['visible_primitives_max'] <= 300000 and after['minimum_player_y'] > -.3
        measured[name] = {'before_bytes': before['texture_memory_bytes'], 'after_bytes': after['texture_memory_bytes']}
    for name, edges in [('cast', 2), ('recast', 4), ('close', 6), ('finale', 8), ('replay', 10)]:
        before = collection(EVIDENCE / 'android-baseline/touches' / name, edges)
        after = collection(EVIDENCE / 'android-candidate/touches' / name, edges)
        assert before['reading_open'] == after['reading_open']
        assert before['room_after_touch'] == after['room_after_touch']
        assert before['build']['renderer_files_sha256'] == after['build']['renderer_files_sha256'] == renderer
        assert after['touch_events'][-2]['pressed'] and not after['touch_events'][-1]['pressed']
        assert all(b['screen_size'][1] >= 48 * after['ui_content_scale_factor'] for b in after['buttons'].values())
        measured[name] = {'before_bytes': before['texture_memory_after_touch_bytes'], 'after_bytes': after['texture_memory_after_touch_bytes']}
    phone_images = {name: compare_image(EVIDENCE / 'android-baseline/route' / ('garden-phone-' + name + '.png'),
                                        EVIDENCE / 'android-candidate/route' / ('garden-phone-' + name + '.png'))
                    for name in ['cell', 'gate', 'pavilion']}
    before = json.loads((EVIDENCE / 'mac-baseline-probes/report.json').read_text())
    after = json.loads((EVIDENCE / 'mac-candidate-probes/report.json').read_text())
    assert before['renderer_files_sha256'] == after['renderer_files_sha256'] == renderer
    assert before['source_glb_sha256'] == after['source_glb_sha256'] == old['source_glb_sha256']
    assert before['captures'].keys() == after['captures'].keys() and len(before['captures']) == 12
    mac_images = {}
    for name, capture in before['captures'].items():
        candidate = after['captures'][name]
        for key in ['clock', 'image_size', 'camera_transform', 'normal_material_owner', 'normal_scale']:
            assert capture[key] == candidate[key], (name, key)
        assert sha(EVIDENCE / 'mac-baseline-probes' / (name + '.png')) == capture['sha256']
        assert sha(EVIDENCE / 'mac-candidate-probes' / (name + '.png')) == candidate['sha256']
        if name.endswith('pbr-probe'):
            for flag in ['use_normal_texture', 'use_orm_texture']:
                assert capture['missing_map_rmse'][flag] > .0001
                assert candidate['missing_map_rmse'][flag] > .0001
        mac_images[name] = compare_image(EVIDENCE / 'mac-baseline-probes' / (name + '.png'),
                                         EVIDENCE / 'mac-candidate-probes' / (name + '.png'))
    peak = max(record['after_bytes'] for record in measured.values())
    result = {'status': 'verified_diagnostic', 'source_glb_sha256': old['source_glb_sha256'],
              'scope': 'Same-Pixel corrected-renderer route and actual reading/finale/replay taps; four original PNGs retained. Casts are stochastic; exhaustive glyph-cache warming is not measured. Native placed comparisons include positive normal/ORM effects in both screen shapes. Sampled memory passes; no sustained FPS, full-garden, 2020 Adreno, release or final per-site art acceptance.',
              'renderer_files_sha256': renderer, 'changed_atlas_dimensions': changed,
              'atlas_saving_bytes': saving, 'measured_states': measured, 'candidate_peak_bytes': peak,
              'passes_64_mib': peak <= 64 * 1024 * 1024, 'passes_decimal_64_mb': peak <= 64000000,
              'phone_images': phone_images, 'mac_images': mac_images, 'verifier_sha256': sha(Path(__file__))}
    assert result['passes_64_mib'] and result['passes_decimal_64_mb']
    (ROOT / 'export/android-pbr-candidate-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print('ANDROID_PBR_CANDIDATE_VERIFIED', 'peak_bytes=', peak, 'atlas_saving=', saving)


if __name__ == '__main__':
    main()
