"""Build an isolated debug APK for actual phone diagnostics, never a store release."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import re

ROOT = Path(__file__).resolve().parents[1]
GODOT = '/Applications/Godot.app/Contents/MacOS/Godot'
REPORT = ROOT / 'export/android-profile-build.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--normal-atlas-size-limit', type=int, choices=[0, 1024], default=0)
    parser.add_argument('--report', type=Path, default=REPORT)
    parser.add_argument('--apk', type=Path, default=ROOT / 'build/garden-phone-profile.apk')
    args = parser.parse_args()
    source = ROOT / 'godot'
    fixture = Path(tempfile.mkdtemp(prefix='garden-android-profile-'))
    output = args.apk.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    normal_names = ['garden-of-dreams_pavilion_normal.png', 'garden-of-dreams_wall_normal.png']
    original_normal_hashes = {name + suffix: sha(source / 'assets' / (name + suffix))
                              for name in normal_names for suffix in ['', '.import']}
    state = {'status': 'preparing', 'fixture': str(fixture), 'apk': str(output),
             'scope': 'Isolated debug profiling export of the installed source and matching runtime maps; no production project settings or source scene changes. Not a final release or target-device acceptance.',
             'normal_atlas_size_limit': args.normal_atlas_size_limit,
             'production_normal_files_sha256': original_normal_hashes,
             'source_glb_sha256': sha(source / 'assets/garden-of-dreams.glb'), 'phases': []}
    def save():
        report_path.write_text(json.dumps(state, indent=2) + '\n')
    save()
    record = json.loads((source / 'assets/garden-source.json').read_text())
    assert record['source_glb_sha256'] == state['source_glb_sha256']
    shutil.copytree(source, fixture, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.godot', 'android', 'tests'))
    if args.normal_atlas_size_limit:
        changes = []
        for name in normal_names:
            path = fixture / 'assets' / (name + '.import')
            contents, count = re.subn(r'^process/size_limit=\d+$',
                                     'process/size_limit=' + str(args.normal_atlas_size_limit),
                                     path.read_text(), flags=re.MULTILINE)
            assert count == 1, 'Missing or ambiguous size limit: ' + name
            changes.append((path, contents))
        for path, contents in changes:
            path.write_text(contents)
    for name in ['imported', 'uid_cache.bin', 'global_script_class_cache.cfg']:
        path = source / '.godot' / name
        destination = fixture / '.godot' / name
        destination.parent.mkdir(exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, destination)
        elif path.exists():
            shutil.copy2(path, destination)
    (fixture / 'tests').mkdir()
    shutil.copy2(source / 'tests/profile_android.gd', fixture / 'tests/profile_android.gd')
    shutil.copy2(source / 'tests/texture_binding_inventory.gd', fixture / 'tests/texture_binding_inventory.gd')
    assert sha(fixture / 'assets/garden-of-dreams.glb') == state['source_glb_sha256']
    project = fixture / 'project.godot'
    contents = project.read_text()
    assert contents.count('[rendering]') == 1
    contents = contents.replace('[rendering]', '[rendering]\ntextures/vram_compression/import_etc2_astc=true')
    assert 'run/main_scene="res://runtime/first_reading_demo.tscn"' in contents
    contents = contents.replace('run/main_scene="res://runtime/first_reading_demo.tscn"',
                                'run/main_scene="res://tests/profile_android.tscn"\nconfig/icon="res://profile-icon.svg"')
    project.write_text(contents)
    (fixture / 'tests/profile_android.tscn').write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://tests/profile_android.gd" id="1"]
[node name="AndroidProfile" type="Node"]
script = ExtResource("1")
''')
    (fixture / 'profile-icon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><rect width="128" height="128" rx="20" fill="#18201f"/><path d="M28 28h72M28 42h72M28 56h30m12 0h30M28 70h72M28 84h30m12 0h30M28 98h72" stroke="#dcb472" stroke-width="7"/></svg>''')
    build = {key: state[key] for key in ['scope', 'source_glb_sha256']}
    build.update({'profile_script_sha256': sha(fixture / 'tests/profile_android.gd'),
                  'inventory_script_sha256': sha(fixture / 'tests/texture_binding_inventory.gd'),
                  'normal_atlas_size_limit': args.normal_atlas_size_limit,
                  'normal_png_sha256': {name: sha(fixture / 'assets' / name) for name in normal_names},
                  'normal_import_sha256': {name: sha(fixture / 'assets' / (name + '.import')) for name in normal_names},
                  'runtime_script_sha256': {name: sha(fixture / 'runtime' / name) for name in ['entry_route.gd', 'reading_result.gd', 'demo_finale.gd']},
                  'demo_index_sha256': sha(fixture / 'lightmaps/demo-index.json'),
                  'full_index_sha256': sha(fixture / 'lightmaps/full-index.json'),
                  'inscription_import_sha256': [sha(fixture / 'assets' / ('garden-of-dreams_gate-inscription' + suffix + '.png.import')) for suffix in ['', '-normal']]})
    (fixture / 'phone-profile-build.json').write_text(json.dumps(build, indent=2) + '\n')
    (fixture / 'export_presets.cfg').write_text('''[preset.0]
name="Android Profile"
platform="Android"
runnable=true
custom_features="garden_profile"
export_filter="all_resources"
include_filter="*.json"
exclude_filter="assets/kits/corridor/*.glb,assets/kits/pavilion/*.glb,assets/kits/wall/*.glb,assets/kits/rockery/*.glb,assets/kits/water/*.glb,assets/kits/props/*.glb,assets/kits/tech/*.glb,assets/kits/stage/*.glb"
export_path=""
encrypt_pck=false
script_export_mode=1

[preset.0.options]
architectures/armeabi-v7a=false
architectures/arm64-v8a=true
architectures/x86=false
architectures/x86_64=false
gradle_build/use_gradle_build=false
package/unique_name="org.godotengine.gardendreams.profile"
package/name="Garden of Dreams Profile"
package/signed=true
version/code=1
version/name="0.1-profile"
command_line/extra_args=""
permissions/internet=false
user_data_backup/allow=false
screen/immersive_mode=true
''')
    for name, command in [('mobile-texture-import', [GODOT, '--headless', '--editor', '--path', str(fixture), '--import']),
                          ('apk-export', [GODOT, '--headless', '--path', str(fixture), '--export-debug', 'Android Profile', str(output)])]:
        log = fixture / (name + '.log')
        phase = {'name': name, 'status': 'running', 'log': str(log)}
        state['phases'].append(phase)
        state['status'] = 'running'
        with log.open('w') as stream:
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
            phase['pid'] = process.pid
            save()
            phase['exit_code'] = process.wait()
        phase['log_sha256'] = sha(log)
        phase['engine_diagnostics'] = re.findall(r'^(?:SCRIPT ERROR|ERROR|WARNING):.*$', log.read_text(), re.MULTILINE)
        phase['status'] = 'passed' if phase['exit_code'] == 0 and not phase['engine_diagnostics'] else 'failed'
        save()
        if phase['status'] != 'passed':
            state['status'] = 'failed'
            save()
            raise RuntimeError(f'{name} failed; inspect {log}')
    assert sha(fixture / 'assets/garden-of-dreams.glb') == state['source_glb_sha256']
    for name, expected in original_normal_hashes.items():
        assert sha(source / 'assets' / name) == expected, 'Production normal asset changed: ' + name
        if not name.endswith('.import'):
            assert sha(fixture / 'assets' / name) == expected, 'Source PNG changed in fixture: ' + name
    state['apk_sha256'] = sha(output)
    state['apk_bytes'] = output.stat().st_size
    state['status'] = 'built'
    state['device_tested'] = False
    save()
    print('ANDROID_PROFILE_APK_BUILT', state['apk_bytes'], state['apk_sha256'])


if __name__ == '__main__':
    main()
