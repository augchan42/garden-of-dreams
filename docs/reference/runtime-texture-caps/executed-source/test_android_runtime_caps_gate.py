"""Reject absent or stale cap evidence before reading or changing the phone."""
from pathlib import Path
import copy
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


class RuntimeCapsCollectorTests(unittest.TestCase):
    def fixture(self, root):
        project = root / 'godot'
        (project / 'assets').mkdir(parents=True)
        (project / 'tests').mkdir()
        (project / '.godot/imported').mkdir(parents=True)
        (project / 'assets/garden-of-dreams.glb').write_bytes(b'actual staged scene')
        for name in ['profile_android.gd', 'profile_report_store.gd', 'test_moon_runtime_import.gd',
                     'moon-paint-atlas.json', 'runtime_texture_caps.gd', 'test_runtime_texture_caps.gd']:
            (project / 'tests' / name).write_text('fixture ' + name)
        textures = {}
        for name, width, height, fmt, count, stored in [
                ('pavilion_basecolor', 1024, 1024, 17, 15, 699064),
                ('wall_basecolor', 1024, 1024, 17, 1, 699064),
                ('gate-inscription', 512, 170, 5, 1, 463772),
                ('gate-inscription-normal', 512, 170, 4, 1, 347829),
                ('moon-paint', 512, 512, 4, 1, 1048575)]:
            source = project / ('assets/garden-of-dreams_' + name + '.png')
            source.write_bytes(('original ' + name).encode())
            cache = project / ('.godot/imported/' + name + '.ctex')
            cache.write_bytes(('generated ' + name).encode())
            source.with_suffix('.png.import').write_text('[remap]\nimporter="texture"\npath="res://' + str(cache.relative_to(project)) + '"\n\n[params]\ncompress/mode=' + ('2' if 'basecolor' in name else '0') + '\nmipmaps/generate=true\ndetect_3d/compress_to=0\nprocess/size_limit=' + str(width) + '\n')
            if name != 'moon-paint':
                textures[name] = {'loaded_size': [width, height], 'stored_format': fmt,
                                  'stored_mip_bytes': stored, 'mipmaps': True,
                                  'source_sha256': sha(source), 'import_sha256': sha(source.with_suffix('.png.import')),
                                  'cache_payloads': {str(cache.relative_to(project)): sha(cache)},
                                  'bindings': {'normal': count, 'demo': count}}
        snapshot = texture_input_snapshot(project)
        manifest = {'texture_provenance_version': 1, 'production_texture_inputs': snapshot,
                    'staged_texture_inputs': snapshot, 'profile_script_sha256': sha(project / 'tests/profile_android.gd'),
                    'moon_runtime_import': {'status': 'passed', 'errors': [], 'loaded_size': [512, 512],
                                            'image_bytes': 1048575, 'source_glb_sha256': sha(project / 'assets/garden-of-dreams.glb'),
                                            'source_png_sha256': sha(project / 'assets/garden-of-dreams_moon-paint.png')},
                    'runtime_texture_caps': {'status': 'passed', 'errors': [], 'textures': textures,
                                             'modes': ['normal', 'demo'], 'source_glb_sha256': sha(project / 'assets/garden-of-dreams.glb')},
                    'runtime_caps_script_sha256': {name: sha(project / 'tests' / name)
                                                  for name in ['runtime_texture_caps.gd', 'test_runtime_texture_caps.gd']}}
        for key, name in [('moon_check_script_sha256', 'test_moon_runtime_import.gd'),
                          ('moon_paint_atlas_sha256', 'moon-paint-atlas.json'),
                          ('report_store_script_sha256', 'profile_report_store.gd')]:
            manifest[key] = sha(project / 'tests' / name)
        staged = root / 'staged'
        shutil.copytree(project, staged)
        apk = root / 'profile.apk'; apk.write_bytes(b'fixed APK identity')
        build = {'status': 'built', 'phases': [{'status': 'passed'}], 'source_glb_sha256': sha(project / 'assets/garden-of-dreams.glb'),
                 'apk': str(apk), 'apk_sha256': sha(apk), 'fixture': str(staged)}
        return project, staged, manifest, build

    def run_case(self, mutation):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); project, staged, manifest, build = self.fixture(root)
            proof = manifest['runtime_texture_caps']
            if mutation == 'missing': del manifest['runtime_texture_caps']
            elif mutation == 'wrong_size': proof['textures']['pavilion_basecolor']['loaded_size'] = [2048, 2048]
            elif mutation == 'missing_binding': proof['textures']['gate-inscription']['bindings']['demo'] = 0
            elif mutation == 'failed': proof['errors'] = ['active binding differs']
            elif mutation == 'missing_mips': proof['textures']['wall_basecolor']['mipmaps'] = False
            elif mutation == 'lossy_gate': proof['textures']['gate-inscription']['stored_format'] = 17
            elif mutation == 'missing_texture': del proof['textures']['wall_basecolor']
            elif mutation == 'changed_source_glb': (staged / 'assets/garden-of-dreams.glb').write_bytes(b'different scene')
            elif mutation == 'changed_production_glb': (project / 'assets/garden-of-dreams.glb').write_bytes(b'different current scene')
            elif mutation in ['changed_production_checker', 'changed_staged_checker']:
                where = project if mutation == 'changed_production_checker' else staged
                (where / 'tests/runtime_texture_caps.gd').write_text('different inspector')
            elif mutation == 'missing_checker_proof': del manifest['runtime_caps_script_sha256']
            elif mutation == 'changed_cache': (staged / '.godot/imported/pavilion_basecolor.ctex').write_bytes(b'stale pixels')
            elif mutation == 'missing_cache_proof': proof['textures']['wall_basecolor']['cache_payloads'] = {}
            path = staged / 'phone-profile-build.json'; path.write_text(json.dumps(manifest))
            build['phone_profile_build_sha256'] = sha(path)
            calls = []
            def adb(*args):
                calls.append(args)
                if args[1] == 'pm': return b'package:/data/app/fixture/base.apk\n'
                return (build['apk_sha256'] + '  /data/app/fixture/base.apk\n').encode()
            with patch.object(collector, 'ROOT', root):
                if mutation == 'valid':
                    record, installed = collector.verify_profile_build(build, adb)
                    self.assertEqual(installed, build['apk_sha256'])
                    self.assertEqual(record, manifest)
                else:
                    with self.assertRaisesRegex(AssertionError, 'cap|Cap'):
                        collector.verify_profile_build(build, adb)
                    self.assertEqual(calls, [], 'Invalid cap evidence must reject before phone access')

    def test_actual_device_cap_record_rejects_bad_pixels_or_bindings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); _, _, manifest, _ = self.fixture(root)
            valid = copy.deepcopy(manifest['runtime_texture_caps'])
            valid['modes'] = ['demo']
            for record in valid['textures'].values(): record['bindings'].pop('normal')
            for name in ['pavilion_basecolor', 'wall_basecolor']: valid['textures'][name]['stored_format'] = 30
            verify = getattr(collector, 'verify_device_caps', None)
            self.assertTrue(callable(verify), 'Actual Android cap verification is not implemented')
            verify(valid)
            for mutation in ['missing', 'size', 'mips', 'format', 'footprint', 'binding', 'failed']:
                with self.subTest(mutation=mutation):
                    proof = copy.deepcopy(valid)
                    if mutation == 'missing': proof = None
                    elif mutation == 'size': proof['textures']['wall_basecolor']['loaded_size'] = [2048, 2048]
                    elif mutation == 'mips': proof['textures']['gate-inscription']['mipmaps'] = False
                    elif mutation == 'format': proof['textures']['gate-inscription']['stored_format'] = 30
                    elif mutation == 'footprint': proof['textures']['pavilion_basecolor']['stored_mip_bytes'] = 2796216
                    elif mutation == 'binding': proof['textures']['wall_basecolor']['bindings']['demo'] = 0
                    elif mutation == 'failed': proof['errors'] = ['wrong material']
                    with self.assertRaisesRegex(AssertionError, 'cap|Cap'): verify(proof)

    def test_valid_resource_and_material_proof_accepts(self): self.run_case('valid')

    def test_missing_or_invalid_caps_reject_before_phone_access(self):
        for mutation in ['missing', 'wrong_size', 'missing_binding', 'failed', 'missing_mips',
                         'lossy_gate', 'missing_texture', 'changed_source_glb', 'changed_production_glb',
                         'changed_production_checker', 'changed_staged_checker',
                         'missing_checker_proof', 'changed_cache', 'missing_cache_proof']:
            with self.subTest(mutation=mutation): self.run_case(mutation)


if __name__ == '__main__': unittest.main()
