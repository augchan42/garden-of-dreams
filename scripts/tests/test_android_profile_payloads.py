"""The actual APK must contain the pinned scene and compiled diagnostics."""
from pathlib import Path
import io
import tempfile
import unittest
import zipfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from android_profile_modes import dependencies, packaged_payloads

class ProfilePayloadTests(unittest.TestCase):
    def test_reject_remapped_scripts_and_changed_scene(self):
        for mutation in ['valid', 'script_remap', 'not_compiled', 'scene_remap', 'scene_payload']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                project = Path(temp);(project/'assets').mkdir();(project/'.godot/imported').mkdir(parents=True)
                relative = '.godot/imported/garden-of-dreams.glb-fixed.scn'
                (project/relative).write_bytes(b'fixed actual scene')
                metadata = '[remap]\nimporter="scene"\npath="res://' + relative + '"\n'
                (project/'assets/garden-of-dreams.glb.import').write_text(metadata+'\n[deps]\n')
                data=io.BytesIO()
                with zipfile.ZipFile(data,'w') as archive:
                    for name in dependencies('full'):
                        path=name.removesuffix('.gd')+'.gdc'
                        expected=path if mutation!='script_remap' else 'tests/another.gdc'
                        archive.writestr('assets/'+name+'.remap','[remap]\npath="res://'+expected+'"\n')
                        archive.writestr('assets/'+path,b'BAD!' if mutation=='not_compiled' else b'GDSCfixed compiled payload')
                    archive.writestr('assets/assets/garden-of-dreams.glb.import',metadata if mutation!='scene_remap' else metadata.replace('fixed.scn','other.scn'))
                    archive.writestr('assets/'+relative,b'changed scene' if mutation=='scene_payload' else b'fixed actual scene')
                with zipfile.ZipFile(data) as archive:
                    if mutation=='valid':
                        record=packaged_payloads(archive,project,{'profile_mode':'full'})
                        self.assertEqual(len(record['compiled_profile_script_sha256']),7)
                        self.assertEqual(list(record['scene_payload_sha256']),[relative])
                    else:
                        with self.assertRaisesRegex(AssertionError,'Packaged'):packaged_payloads(archive,project,{'profile_mode':'full'})

if __name__=='__main__':unittest.main()
