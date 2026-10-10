"""Compare completed full-route diagnostics without treating them as final acceptance."""
from pathlib import Path
import hashlib
import json
import re
import struct

ROOT = Path('/tmp/garden-memory-caps-20261010')
BASELINE = Path('/tmp/garden-full-phone-20261010')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    pipeline = json.loads((ROOT / 'phone-pipeline.json').read_text())
    assert pipeline['status'] == 'complete'
    current = json.loads((ROOT / 'actual-phone/garden-phone-profile.json').read_text())
    before = json.loads((BASELINE / 'actual-phone/garden-phone-profile.json').read_text())
    build = json.loads((ROOT / 'phone-build-report.json').read_text())
    assert current['build']['full_base_script_sha256'] == before['build']['profile_script_sha256']
    assert current['build']['demo_base_script_sha256'] == before['build']['demo_base_script_sha256']
    assert current['status'] == before['status'] == 'complete'
    assert set(current['samples']) == set(before['samples'])
    assert current['completed_tours'] == before['completed_tours'] == 2
    assert len(current['legs']) == len(before['legs']) == 52
    assert current['timed_seconds'] >= 600 and current['time_scale'] == 1
    assert current['physics_ticks_per_second'] == 60
    for name, expected in pipeline['files'].items():
        assert sha(ROOT / 'actual-phone' / name) == expected
    for name, capture in current['captures'].items():
        data = (ROOT / 'actual-phone' / capture['file']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == capture['sha256']
        assert list(struct.unpack('>II', data[16:24])) == capture['image_size']
    diagnostics = re.findall(r'^(?:SCRIPT ERROR|ERROR|WARNING):.*$',
                             (ROOT / 'actual-phone/app.log').read_text(), re.M)
    samples = list(current['samples'].values())
    old_samples = list(before['samples'].values())
    failures = {budget: sum(not row[budget] for row in current['budget_results'].values())
                for budget in next(iter(current['budget_results'].values()))}
    peak = max(row['texture_memory_bytes'] for row in samples)
    old_peak = max(row['texture_memory_bytes'] for row in old_samples)
    memory_delta = sorted({before['samples'][name]['texture_memory_bytes'] - row['texture_memory_bytes']
                           for name, row in current['samples'].items()})
    result = dict(status='completed_diagnostic', production_adopted=False,
                  device=current['device_model'], gpu=current['renderer_device'],
                  target_2020_adreno=False, apk_sha256=build['apk_sha256'],
                  tours=current['completed_tours'], legs=len(current['legs']),
                  rooms=current['visited_rooms'], timed_seconds=current['timed_seconds'],
                  samples=len(samples), captures=len(current['captures']),
                  complete_json_reads=pipeline['complete_reads'],
                  incomplete_json_reads=pipeline['incomplete_reads'],
                  texture_peak_bytes=peak, baseline_texture_peak_bytes=old_peak,
                  saved_peak_bytes=old_peak-peak, margin_to_64_mib_bytes=67108864-peak,
                  matched_sample_memory_savings_bytes=memory_delta,
                  draw_calls_max=max(row['visible_draw_calls_max'] for row in samples),
                  primitives_max=max(row['visible_primitives_max'] for row in samples),
                  practicals_max=max(row['active_practicals_max'] for row in samples),
                  p95_ms_range=[min(row['frame_interval_p95_ms'] for row in samples),
                                max(row['frame_interval_p95_ms'] for row in samples)],
                  budget_failures=failures,
                  supported_floor_rays=sum(leg['supported_ray_samples'] for leg in current['legs']),
                  floor_ray_misses=sum(leg['grounded_ray_samples']-leg['supported_ray_samples']
                                       for leg in current['legs']),
                  diagnostics=diagnostics,
                  actual_device_cap_resources=pipeline['actual_device_cap_resources'],
                  scope='Two full normal-physics tours and at least600timedseconds on Pixel7Pro. '
                        'No final art,60fps,2020Adreno,release or live service acceptance. '
                        'Direct image review and separate native touch sequence still required.')
    assert not diagnostics, diagnostics
    assert result['floor_ray_misses'] == 0
    assert result['saved_peak_bytes'] == 6638592
    assert result['incomplete_json_reads'] == 0
    (ROOT / 'full-phone-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['actual_device_cap_resources','rooms']}, indent=2))

if __name__ == '__main__':
    main()
