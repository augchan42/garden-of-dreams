"""Guard the release entry point and production-project isolation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'build_demo_handoff.py'
spec = importlib.util.spec_from_file_location('demo_handoff', MODULE)
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


class DemoHandoffTests(unittest.TestCase):
    def test_wrong_or_ambiguous_package_startup_is_rejected(self):
        for source in ['', 'run/main_scene="res://runtime/entry_route.tscn"\n',
                       'run/main_scene="res://runtime/first_reading_demo.tscn"\n' * 2]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                handoff.require_demo_config(source)
        for source in ['', 'run/main_scene="x"\nrun/main_scene="y"\n']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                handoff.demo_config(source)

    def test_universal_staging_enables_astc_when_false_or_missing(self):
        startup = '[application]\nrun/main_scene="res://runtime/entry_route.tscn"\n'
        for rendering in ['', '[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
                          '[rendering]\ntextures/vram_compression/import_etc2_astc=false\n',
                          '[rendering]\ntextures/vram_compression/import_etc2_astc=true\n']:
            with self.subTest(rendering=rendering):
                result = handoff.demo_config(startup + rendering + '\n[input]\nexample=1\n')
                self.assertEqual(result.count('textures/vram_compression/import_etc2_astc=true'), 1)
                self.assertNotIn('textures/vram_compression/import_etc2_astc=false', result)
                self.assertIn('[input]\nexample=1', result)
                self.assertIn('[rendering]', result)
                handoff.require_demo_config(result)

    def test_staging_preserves_production_assets_and_startup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, staged = root / 'source', root / 'stage'
            source.mkdir()
            original = '[application]\nrun/main_scene="res://runtime/entry_route.tscn"\n'
            (source / 'project.godot').write_text(original)
            (source / 'export_presets.cfg').write_text('original export options')
            (source / 'assets').mkdir()
            (source / 'assets/scene.glb').write_bytes(b'unchanged scene data')
            (source / '.godot').mkdir()
            (source / '.godot/cached.scn').write_bytes(b'old imported cache')
            before = handoff.project_files(source)
            handoff.stage_project(source, staged)
            self.assertEqual(handoff.project_files(source), before)
            self.assertEqual((source / 'project.godot').read_text(), original)
            self.assertEqual((staged / 'assets/scene.glb').read_bytes(), b'unchanged scene data')
            self.assertFalse((staged / '.godot').exists())
            handoff.require_demo_config((staged / 'project.godot').read_text())
            with self.assertRaisesRegex(ValueError, 'already exists'):
                handoff.stage_project(source, staged)


if __name__ == '__main__':
    unittest.main()
