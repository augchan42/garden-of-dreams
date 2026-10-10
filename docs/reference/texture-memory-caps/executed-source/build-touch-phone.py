"""Build a separate demo from the verified cap fixture after the sustained run ends."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path('/tmp/garden-memory-caps-20261010')
REPO = Path('/Users/auchan/projects/garden-of-dreams')
GODOT = '/Applications/Godot.app/Contents/MacOS/Godot'
sys.path.insert(0, str(REPO / 'scripts'))
from android_texture_provenance import texture_input_snapshot, verify_texture_inputs

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    full = json.loads((ROOT / 'phone-pipeline.json').read_text())
    assert full['status'] == 'complete', 'Do not build or install during the sustained run'
    original = json.loads((ROOT / 'phone-build-report.json').read_text())
    assert sha(original['apk']) == original['apk_sha256'] == full['installed_apk_sha256']
    folder = ROOT / 'touch-phone'
    folder.mkdir(exist_ok=False)
    fixture = folder / 'godot'
    subprocess.run(['/bin/cp', '-cR', original['fixture'], str(fixture)], check=True)
    shutil.copy2(REPO / 'godot/tests/profile_android.gd', fixture / 'tests/profile_android.gd')
    manifest = json.loads((fixture / 'phone-profile-build.json').read_text())
    verify_texture_inputs(REPO / 'godot', manifest['production_texture_inputs'], 'Production')
    verify_texture_inputs(fixture, manifest['staged_texture_inputs'], 'Staged')
    manifest.update(profile_mode='demo', profile_script_sha256=sha(fixture / 'tests/profile_android.gd'),
                    scope='Four texture caps; unchanged production demo profiler and native touch sequence.')
    manifest['same_cap_payload_full_apk_sha256'] = original['apk_sha256']
    manifest['actual_device_full_cap_proof'] = full['actual_device_cap_resources']
    state = dict(status='preparing', fixture=str(fixture), apk=str(folder / 'garden-memory-demo.apk'),
                 source_glb_sha256=original['source_glb_sha256'], phases=[])

    def save():
        (folder / 'build-report.json').write_text(json.dumps(state, indent=2) + '\n')

    def run(name, args):
        log = folder / (name + '.log')
        row = dict(name=name, status='running', log=str(log))
        state['phases'].append(row)
        save()
        with log.open('w') as stream:
            child = subprocess.Popen([GODOT, '--headless', '--path', str(fixture), *args],
                                     stdout=stream, stderr=subprocess.STDOUT)
            row['pid'] = child.pid
            save()
            row['exit_code'] = child.wait(timeout=180)
        row['engine_diagnostics'] = re.findall(r'^(?:SCRIPT ERROR|ERROR|WARNING):.*$', log.read_text(), re.M)
        row['status'] = 'passed' if row['exit_code'] == 0 and not row['engine_diagnostics'] else 'failed'
        row['log_sha256'] = sha(log)
        save()
        assert row['status'] == 'passed', log.read_text()[-4000:]
        print(name, 'passed', flush=True)

    save()
    run('import', ['--editor', '--import'])
    actual = texture_input_snapshot(fixture)
    assert actual == manifest['staged_texture_inputs'], 'Demo preparation changed texture inputs'
    run('cap-check', ['--script', 'res://tests/test_memory_caps.gd', '--',
                      '--output=' + str(folder / 'cap-resources.json')])
    cap = json.loads((folder / 'cap-resources.json').read_text())
    assert cap['status'] == 'passed' and not cap['errors']
    manifest['memory_cap_resource_check'] = cap
    (fixture / 'phone-profile-build.json').write_text(json.dumps(manifest, indent=2) + '\n')
    state['phone_profile_build_sha256'] = sha(fixture / 'phone-profile-build.json')
    save()
    run('export', ['--export-debug', 'Android Profile', state['apk']])
    payloads = json.loads((ROOT / 'apk-input-verification-v2.json').read_text())['payload_sha256']
    inventory = json.loads((ROOT / 'candidate-inventory-normal.json').read_text())
    with zipfile.ZipFile(original['apk']) as before, zipfile.ZipFile(state['apk']) as after:
        for name, expected in payloads.items():
            assert hashlib.sha256(after.read(name)).hexdigest() == expected
        bound = 0
        for item in inventory['textures']:
            path = item['resource_path']
            if not path:
                assert item['resource_class'] == 'ViewportTexture'
                continue
            name = 'assets/' + path.removeprefix('res://') + '.import'
            assert before.read(name) == after.read(name), name
            bound += 1
        assert bound == 177
        protected = [name for name in before.namelist()
                     if name.startswith(('assets/runtime/', 'assets/shaders/'))
                     or (name.endswith('.json') and name != 'assets/phone-profile-build.json')]
        for name in protected:
            assert before.read(name) == after.read(name), name
        scene = 'assets/.godot/imported/garden-of-dreams.glb-869f920d830dc1625bcf5b31432c447d.scn'
        assert before.read(scene) == after.read(scene)
    verify_texture_inputs(REPO / 'godot', manifest['production_texture_inputs'], 'Production')
    verify_texture_inputs(fixture, manifest['staged_texture_inputs'], 'Staged')
    state.update(status='built', apk_sha256=sha(state['apk']), apk_bytes=Path(state['apk']).stat().st_size,
                 payload_proof=dict(bound_imports=bound, unchanged_texture_payloads=len(payloads),
                                    unchanged_protected_entries=len(protected), scene_unchanged=True,
                                    compared_full_apk_sha256=original['apk_sha256']))
    save()
    print('TOUCH_PHONE_APK_VERIFIED', state['apk_sha256'], flush=True)

if __name__ == '__main__':
    main()
