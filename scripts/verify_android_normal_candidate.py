"""Verify saved native allocation/capture evidence without accepting a failed budget."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/reference/android-normal-candidate-b4'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_collection(path):
    evidence = json.loads((path / 'evidence.json').read_text())
    for name, expected in evidence['files'].items():
        assert sha(path / name) == expected, 'Evidence changed: ' + str(path / name)
    report = json.loads((path / 'garden-phone-profile.json').read_text())
    build = json.loads((path / 'build.json').read_text())
    assert report['status'] == 'ready_for_taps'
    assert report['source_glb_sha256'] == build['source_glb_sha256'] == evidence['source_glb_sha256']
    assert build['apk_sha256'] == evidence['apk_sha256']
    assert all(p['status'] == 'passed' and not p['engine_diagnostics'] for p in build['phases'])
    return report, build


def compare_image(old_path, new_path):
    old = np.asarray(Image.open(old_path).convert('RGB'), dtype=float) / 255
    new = np.asarray(Image.open(new_path).convert('RGB'), dtype=float) / 255
    assert old.shape == new.shape
    difference = np.abs(old - new)
    return {'before_sha256': sha(old_path), 'after_sha256': sha(new_path),
            'rgb_rmse': float(np.sqrt(np.mean(difference * difference))),
            'rgb_p99': float(np.quantile(difference, .99)),
            'fraction_pixels_over_one_level': float(np.mean(np.max(difference, axis=2) > 1 / 255))}


def main():
    before, before_build = read_collection(EVIDENCE / 'baseline')
    after, after_build = read_collection(EVIDENCE / 'candidate')
    assert before['source_glb_sha256'] == after['source_glb_sha256']
    for key in ['device_model', 'renderer_device', 'renderer', 'native_window_size',
                'screen_dpi', 'fps_cap', 'logical_viewport_size', 'ui_content_scale_factor', 'initial_buttons']:
        assert before[key] == after[key], 'Uncontrolled phone setting: ' + key
    assert before['native_window_size'] == [1080, 2340]
    assert before['captures'] == after['captures'] and set(after['captures']) == {'cell', 'gate', 'pavilion'}
    assert all(c['clock'] == 3 and c['animated_materials'] > 0 for c in after['captures'].values())
    assert before['build']['normal_atlas_size_limit'] == 0 and after['build']['normal_atlas_size_limit'] == 1024
    for key in ['normal_png_sha256', 'runtime_script_sha256', 'profile_script_sha256',
                'inventory_script_sha256', 'demo_index_sha256', 'full_index_sha256', 'inscription_import_sha256']:
        assert before['build'][key] == after['build'][key], 'Uncontrolled asset change: ' + key
    assert before_build['production_normal_files_sha256'] == after_build['production_normal_files_sha256']
    old_textures = {t['resource_path']: t for t in before['texture_inventory']['textures']}
    new_textures = {t['resource_path']: t for t in after['texture_inventory']['textures']}
    assert len(old_textures) == len(new_textures) == 88 and old_textures.keys() == new_textures.keys()
    changed = {}
    for name, old in old_textures.items():
        new = new_textures[name]
        assert old['bindings'] == new['bindings'] and old['stored_format'] == new['stored_format']
        assert old['mipmaps'] == new['mipmaps']
        if name.endswith(('pavilion_normal.png', 'wall_normal.png')):
            assert old['size'] == [2048, 2048] and new['size'] == [1024, 1024]
            changed[name] = {'before_size': old['size'], 'after_size': new['size'],
                             'before_calculated_storage_bytes': old['stored_format_mip_data_bytes'],
                             'after_calculated_storage_bytes': new['stored_format_mip_data_bytes']}
        else:
            assert old['size'] == new['size']
            assert old['stored_format_mip_data_bytes'] == new['stored_format_mip_data_bytes']
    assert len(changed) == 2
    saving = before['texture_inventory']['stored_format_mip_data_bytes'] - after['texture_inventory']['stored_format_mip_data_bytes']
    assert saving == 8 * 1024 * 1024
    measured = {}
    for label, old in before['samples'].items():
        new = after['samples'][label]
        assert old['texture_memory_bytes'] - new['texture_memory_bytes'] == saving
        measured[label] = {'before_bytes': old['texture_memory_bytes'], 'after_bytes': new['texture_memory_bytes']}
    for stage, edges in [('cast', 2), ('recast', 4), ('close', 6), ('finale', 8), ('replay', 10)]:
        old, _ = read_collection(EVIDENCE / 'baseline-touches' / stage)
        new, _ = read_collection(EVIDENCE / 'candidate-touches' / stage)
        assert len(old['touch_events']) == len(new['touch_events']) == edges
        assert old['room_after_touch'] == new['room_after_touch']
        assert old['reading_open'] == new['reading_open']
        assert old['texture_memory_after_touch_bytes'] - new['texture_memory_after_touch_bytes'] == saving
        measured[stage] = {'before_bytes': old['texture_memory_after_touch_bytes'], 'after_bytes': new['texture_memory_after_touch_bytes']}
    phone_images = {label: compare_image(EVIDENCE / 'baseline' / ('garden-phone-' + label + '.png'),
                                         EVIDENCE / 'candidate' / ('garden-phone-' + label + '.png'))
                    for label in after['captures']}
    mac_old = json.loads((EVIDENCE / 'mac-baseline/report.json').read_text())
    mac_new = json.loads((EVIDENCE / 'mac-candidate/report.json').read_text())
    assert mac_old['source_glb_sha256'] == mac_new['source_glb_sha256'] == after['source_glb_sha256']
    assert len(mac_old['captures']) == len(mac_new['captures']) == 8
    mac_images = {}
    for label, old in mac_old['captures'].items():
        new = mac_new['captures'][label]
        assert {k: v for k, v in old.items() if k != 'sha256'} == {k: v for k, v in new.items() if k != 'sha256'}
        old_path, new_path = EVIDENCE / 'mac-baseline' / (label + '.png'), EVIDENCE / 'mac-candidate' / (label + '.png')
        assert sha(old_path) == old['sha256'] and sha(new_path) == new['sha256']
        mac_images[label] = compare_image(old_path, new_path)
    for result in [*phone_images.values(), *mac_images.values()]:
        assert result['rgb_rmse'] < 2 / 255 and result['rgb_p99'] < 8 / 255
    peak = max(record['after_bytes'] for record in measured.values())
    result = {'status': 'diagnostic_complete', 'production_normal_cap_installed': False,
              'source_glb_sha256': after['source_glb_sha256'],
              'scope': 'Native same-device debug allocation experiment and fixed-clock images at the preceding b4 scene. The complete demo still fails both memory thresholds. Arrival/full-image differences do not prove preservation of every close normal detail; Hengwu images are identical under the captured lighting. No corrected roof, release, 2020 Adreno, full garden or final art acceptance.',
              'normal_textures': changed, 'actual_renderer_saving_bytes': saving, 'measured_states': measured,
              'candidate_complete_demo_peak_bytes': peak,
              'existing_diagnostic_64_mib_passed': peak <= 64 * 1024 * 1024,
              'spec_decimal_64_mb_passed': peak <= 64_000_000,
              'phone_fixed_clock_images': phone_images, 'mac_placed_material_images': mac_images,
              'verifier_sha256': sha(Path(__file__))}
    (ROOT / 'export/android-normal-candidate-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print('ANDROID_NORMAL_DIAGNOSTIC_VERIFIED saving_bytes=', saving,
          'complete_demo_peak_bytes=', peak, 'budget_passed=', result['existing_diagnostic_64_mib_passed'])


if __name__ == '__main__':
    main()
