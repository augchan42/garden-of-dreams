"""Full tour evidence must be complete and current before collection."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import collect_android_profile as collector
import test_android_runtime_caps_gate as cap_tests
sha = cap_tests.sha

TOUR = json.loads((Path(__file__).resolve().parents[2] / 'godot/tests/test_full_garden_traversal.gd').read_text().split('const TOUR = ', 1)[1].split('\nvar route', 1)[0])


def full_report():
    samples = {}
    captures = {}
    legs = []
    arrivals = []
    def sample(label):
        samples[label] = {'frames': 180, 'frame_interval_median_ms': 17.0, 'frame_interval_p95_ms': 20.0,
                         'visible_draw_calls_max': 99, 'visible_primitives_max': 178601,
                         'global_draw_calls_max': 112, 'global_primitives_max': 190000,
                         'active_practicals_max': 4, 'texture_memory_bytes': 65318147}
    def capture(label, room):
        sample(label)
        captures[label] = {'file': 'garden-full-' + label + '.png', 'image_size': [1080, 2340],
                           'sha256': 'a' * 64, 'room': room, 'camera_settled': True}
    capture('start-terminal_room', 'terminal_room')
    for tour in range(2):
        origin = 'terminal_room'
        for index, (command, target) in enumerate(TOUR):
            label = f'{tour:02d}-{index:02d}-{origin}-to-{target}'
            sample(label)
            capture(f'{tour:02d}-{index:02d}-{target}', target)
            height = 4.0 if target == 'tubi_tang' else -.65 if target == 'aojing_guan' else 0.0
            legs.append({'tour': tour, 'from': origin, 'to': target, 'command': command,
                         'physics_frames': 600, 'walking_distance_m': 20.0, 'min_y': min(0, height),
                         'max_y': max(0, height), 'longest_air_frames': 0,
                         'grounded_ray_samples': 600, 'supported_ray_samples': 600,
                         'trace_sha256': 'b' * 64, 'end_position': [0, height, 0]})
            arrivals.append(target)
            origin = target
    return {'status': 'complete', 'error': '', 'profile_mode': 'full', 'completed_tours': 2,
            'render_budget_scope': 'engine_global_all_viewports',
            'timed_seconds': 735.0, 'minimum_timed_seconds': 600, 'physics_ticks_per_second': 60,
            'time_scale': 1.0, 'fps_cap': 60, 'visited_rooms': sorted(set(arrivals)),
            'arrival_signals': arrivals, 'legs': legs, 'samples': samples, 'captures': captures,
            'budget_results': {name: {'texture': True, 'draw_calls': True, 'primitives': True,
                                     'practicals': True, 'p95_60fps': False} for name in samples}}


class FullProfileTests(unittest.TestCase):
    def test_reflection_work_cannot_hide_behind_root_visible_counts(self):
        report = full_report()
        first = next(iter(report['samples']))
        report['samples'][first]['global_draw_calls_max'] = 171
        report['samples'][first]['global_primitives_max'] = 310000
        report['budget_results'][first]['draw_calls'] = False
        report['budget_results'][first]['primitives'] = False
        collector.verify_full_report(report)
        for mutation in ['scope', 'missing', 'fraction', 'boolean', 'nan', 'below_root', 'false_pass']:
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(report)
                sample = changed['samples'][first]
                if mutation == 'scope': del changed['render_budget_scope']
                elif mutation == 'missing': del sample['global_primitives_max']
                elif mutation == 'fraction': sample['global_draw_calls_max'] = 171.5
                elif mutation == 'boolean': sample['global_draw_calls_max'] = True
                elif mutation == 'nan': sample['global_draw_calls_max'] = float('nan')
                elif mutation == 'below_root': sample['global_primitives_max'] = 1
                elif mutation == 'false_pass': changed['budget_results'][first]['draw_calls'] = True
                with self.assertRaises(AssertionError): collector.verify_full_report(changed)

    def test_only_explicit_absence_can_wait_at_startup(self):
        parser = getattr(collector, 'parse_profile_publication', None)
        self.assertTrue(callable(parser), 'Explicit unpublished report handling is missing')
        self.assertIsNone(parser(b'GARDEN_PROFILE_NOT_PUBLISHED\n'))
        self.assertEqual(parser(b'{"status":"running"}'), {'status': 'running'})
        for data in [b'', b'{"status":', b'cat: report missing\n']:
            with self.assertRaises(json.JSONDecodeError): parser(data)

    def test_complete_tour_accepts_without_hiding_failed_fps(self):
        verifier = getattr(collector, 'verify_full_report', None)
        self.assertTrue(callable(verifier), 'Full report validation is missing')
        verifier(full_report())

    def test_reject_incomplete_unsafe_or_false_tour_evidence(self):
        verifier = getattr(collector, 'verify_full_report', None)
        self.assertTrue(callable(verifier), 'Full report validation is missing')
        for mutation in ['short', 'one_tour', 'missing_leg', 'wrong_order', 'signal', 'room', 'sample',
                         'capture', 'unsettled', 'unsafe_file', 'wrong_height', 'floor', 'air',
                         'physics', 'time', 'zero_frames', 'nan', 'false_budget', 'duplicate_capture']:
            with self.subTest(mutation=mutation):
                report = full_report()
                first = next(iter(report['samples']))
                cap = report['captures'][first]
                if mutation == 'short': report['timed_seconds'] = 599
                elif mutation == 'one_tour': report['completed_tours'] = 1
                elif mutation == 'missing_leg': report['legs'].pop()
                elif mutation == 'wrong_order': report['legs'][0]['command'] = 'back'
                elif mutation == 'signal': report['arrival_signals'].pop()
                elif mutation == 'room': report['visited_rooms'].pop()
                elif mutation == 'sample': del report['samples'][first]
                elif mutation == 'capture': del report['captures'][first]
                elif mutation == 'unsettled': cap['camera_settled'] = False
                elif mutation == 'unsafe_file': cap['file'] = '../../other-app'
                elif mutation == 'wrong_height': report['legs'][0]['end_position'][1] = 2
                elif mutation == 'floor': report['legs'][0]['supported_ray_samples'] = 599
                elif mutation == 'air': report['legs'][0]['longest_air_frames'] = 25
                elif mutation == 'physics': report['physics_ticks_per_second'] = 120
                elif mutation == 'time': report['time_scale'] = 2
                elif mutation == 'zero_frames': report['samples'][first]['frames'] = 0
                elif mutation == 'nan': report['samples'][first]['frame_interval_p95_ms'] = float('nan')
                elif mutation == 'false_budget': report['budget_results'][first]['p95_60fps'] = True
                elif mutation == 'duplicate_capture': cap['file'] = next(c['file'] for n,c in report['captures'].items() if n != first)
                with self.assertRaises(AssertionError): verifier(report)

    def test_actual_device_proof_is_specific_to_normal_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            _, _, manifest, _ = cap_tests.RuntimeCapsCollectorTests().fixture(Path(temp))
            proof = copy.deepcopy(manifest['runtime_texture_caps'])
            proof['modes'] = ['normal']
            for texture in proof['textures'].values(): del texture['bindings']['demo']
            collector.verify_device_caps(proof, mode='normal')
            with self.assertRaises(AssertionError): collector.verify_device_caps(proof)
            with self.assertRaises(AssertionError): collector.verify_device_caps(proof, mode='typo')

    def test_full_producer_and_dependencies_pinned_before_phone_access(self):
        for mutation in ['valid', 'missing_manifest', 'changed_production', 'changed_staged', 'changed_traversal']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                project, staged, manifest, build = cap_tests.RuntimeCapsCollectorTests().fixture(root)
                names = ['profile_android.gd', 'profile_android_full.gd', 'profile_frame_costs.gd',
                         'profile_report_store.gd', 'runtime_texture_caps.gd', 'texture_binding_inventory.gd',
                         'test_full_garden_traversal.gd']
                for name in names:
                    if not (project / 'tests' / name).exists(): (project / 'tests' / name).write_text('actual ' + name)
                    (staged / 'tests' / name).write_bytes((project / 'tests' / name).read_bytes())
                manifest['profile_mode'] = build['profile_mode'] = 'full'
                manifest['profile_script_sha256'] = sha(project / 'tests/profile_android_full.gd')
                manifest['profile_dependency_sha256'] = {'tests/' + name: sha(project / 'tests' / name) for name in names}
                if mutation == 'missing_manifest': del manifest['profile_dependency_sha256']
                elif mutation == 'changed_production': (project / 'tests/profile_frame_costs.gd').write_text('changed timing')
                elif mutation == 'changed_staged': (staged / 'tests/profile_android_full.gd').write_text('changed producer')
                elif mutation == 'changed_traversal': (project / 'tests/test_full_garden_traversal.gd').write_text('different tour')
                path = staged / 'phone-profile-build.json'; path.write_text(json.dumps(manifest))
                build['phone_profile_build_sha256'] = sha(path)
                calls = []
                def adb(*args):
                    calls.append(args)
                    if args[1] == 'pm': return b'package:/data/app/fixture/base.apk\n'
                    return (build['apk_sha256'] + '  /data/app/fixture/base.apk\n').encode()
                with patch.object(collector, 'ROOT', root):
                    if mutation == 'valid': collector.verify_profile_build(build, adb)
                    else:
                        with self.assertRaisesRegex(AssertionError, 'profile|Profile'): collector.verify_profile_build(build, adb)
                        self.assertEqual(calls, [])


if __name__ == '__main__': unittest.main()
