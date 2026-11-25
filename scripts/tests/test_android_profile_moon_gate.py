"""A collector must not accept legacy manifests without loaded-resource proof."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import collect_android_profile as collector
from android_texture_provenance import texture_input_snapshot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CollectorMoonGateTests(unittest.TestCase):
    def test_missing_or_changed_report_writer_rejects_before_device_access(self):
        for mutation in ['missing_proof', 'production_changed', 'staged_changed']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                project = root / 'godot'
                (project / 'assets').mkdir(parents=True)
                (project / 'tests').mkdir()
                texture = project / 'assets/garden-of-dreams_moon-paint.png'
                texture.write_bytes(b'unchanged source paint')
                texture.with_suffix('.png.import').write_text('[remap]\nimporter="texture"\n\n[params]\nprocess/size_limit=512\n')
                for name in ['profile_android.gd', 'profile_report_store.gd',
                             'test_moon_runtime_import.gd', 'moon-paint-atlas.json']:
                    (project / 'tests' / name).write_text('fixture ' + name)
                snapshot = texture_input_snapshot(project)
                manifest = {'texture_provenance_version': 1,
                            'production_texture_inputs': snapshot,
                            'staged_texture_inputs': snapshot,
                            'profile_script_sha256': sha(project / 'tests/profile_android.gd'),
                            'moon_runtime_import': {'status': 'passed', 'errors': [],
                                                    'loaded_size': [512, 512], 'image_bytes': 1048575,
                                                    'source_glb_sha256': 'fixture glb',
                                                    'source_png_sha256': sha(texture)},
                            'moon_check_script_sha256': sha(project / 'tests/test_moon_runtime_import.gd'),
                            'moon_paint_atlas_sha256': sha(project / 'tests/moon-paint-atlas.json')}
                if mutation != 'missing_proof':
                    manifest['report_store_script_sha256'] = sha(project / 'tests/profile_report_store.gd')
                staged = root / 'staged'
                shutil.copytree(project, staged)
                if mutation != 'missing_proof':
                    changed = project if mutation == 'production_changed' else staged
                    (changed / 'tests/profile_report_store.gd').write_text('changed writer')
                manifest_path = staged / 'phone-profile-build.json'
                manifest_path.write_text(json.dumps(manifest))
                apk = root / 'profile.apk'
                apk.write_bytes(b'fixture APK identity')
                build = {'status': 'built', 'phases': [{'status': 'passed'}],
                         'source_glb_sha256': 'fixture glb',
                         'apk': str(apk), 'apk_sha256': sha(apk), 'fixture': str(staged),
                         'phone_profile_build_sha256': sha(manifest_path)}
                calls = []
                def adb(*args):
                    calls.append(args)
                    if args[1] == 'pm':
                        return b'package:/data/app/fixture/base.apk\n'
                    return (sha(apk) + '  /data/app/fixture/base.apk\n').encode()
                with patch.object(collector, 'ROOT', root):
                    with self.assertRaisesRegex(AssertionError, 'report writer'):
                        collector.verify_profile_build(build, adb)
                self.assertEqual(calls, [], 'Unproved writer must reject before phone access')

    def test_legacy_manifest_rejects_before_accessing_device(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'godot'
            (project / 'assets').mkdir(parents=True)
            (project / 'tests').mkdir()
            texture = project / 'assets/garden-of-dreams_moon-paint.png'
            texture.write_bytes(b'unchanged source paint')
            texture.with_suffix('.png.import').write_text('[remap]\nimporter="texture"\n\n[params]\nprocess/size_limit=512\n')
            (project / 'tests/profile_android.gd').write_text('extends Node\n')
            snapshot = texture_input_snapshot(project)
            manifest = {'texture_provenance_version': 1,
                        'production_texture_inputs': snapshot,
                        'staged_texture_inputs': snapshot,
                        'profile_script_sha256': sha(project / 'tests/profile_android.gd')}
            manifest_path = project / 'phone-profile-build.json'
            manifest_path.write_text(json.dumps(manifest))
            apk = root / 'profile.apk'
            apk.write_bytes(b'fixture APK identity')
            build = {'status': 'built', 'phases': [{'status': 'passed'}],
                     'apk': str(apk), 'apk_sha256': sha(apk), 'fixture': str(project),
                     'phone_profile_build_sha256': sha(manifest_path)}
            calls = []
            def adb(*args):
                calls.append(args)
                if args[1] == 'pm':
                    return b'package:/data/app/fixture/base.apk\n'
                return (sha(apk) + '  /data/app/fixture/base.apk\n').encode()
            with patch.object(collector, 'ROOT', root):
                with self.assertRaisesRegex(AssertionError, 'loaded moon provenance'):
                    collector.verify_profile_build(build, adb)
            self.assertEqual(calls, [], 'Unproved builds must reject before phone access')


if __name__ == '__main__':
    unittest.main()
