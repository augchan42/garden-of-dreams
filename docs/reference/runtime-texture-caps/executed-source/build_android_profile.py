"""Build an isolated debug APK for actual phone diagnostics, never a store release."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import re
from android_texture_provenance import texture_input_snapshot, verify_texture_inputs
from configure_moon_paint_import import configure as configure_moon_import
from configure_runtime_texture_caps import configure as configure_runtime_caps, verify_loaded_caps, verify_manifest_caps

ROOT = Path(__file__).resolve().parents[1]
GODOT = '/Applications/Godot.app/Contents/MacOS/Godot'
REPORT = ROOT / 'export/android-profile-build.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--normal-atlas-size-limit', type=int, choices=[0, 1024], default=0)
    parser.add_argument('--orm-atlas-size-limit', type=int, choices=[0, 1024], default=0)
    parser.add_argument('--reuse-ui-font-sizes', action='store_true',
                        help='Isolated candidate: reuse existing 22pt heading/16pt body sizes.')
    parser.add_argument('--report', type=Path, default=REPORT)
    parser.add_argument('--apk', type=Path, default=ROOT / 'build/garden-phone-profile.apk')
    args = parser.parse_args()
    source = ROOT / 'godot'
    production_texture_inputs = texture_input_snapshot(source)
    fixture = Path(tempfile.mkdtemp(prefix='garden-android-profile-'))
    output = args.apk.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    normal_names = ['garden-of-dreams_pavilion_normal.png', 'garden-of-dreams_wall_normal.png']
    orm_names = ['garden-of-dreams_pavilion_orm.png', 'garden-of-dreams_wall_orm.png']
    original_normal_hashes = {name + suffix: sha(source / 'assets' / (name + suffix))
                              for name in normal_names for suffix in ['', '.import']}
    original_orm_hashes = {name + suffix: sha(source / 'assets' / (name + suffix))
                          for name in orm_names for suffix in ['', '.import']}
    state = {'status': 'preparing', 'fixture': str(fixture), 'apk': str(output),
             'scope': 'Isolated debug profiling export of the installed source and matching runtime maps; no production project settings or source scene changes. Not a final release or target-device acceptance.',
             'normal_atlas_size_limit': args.normal_atlas_size_limit,
             'orm_atlas_size_limit': args.orm_atlas_size_limit,
             'reuse_ui_font_sizes': args.reuse_ui_font_sizes,
             'production_normal_files_sha256': original_normal_hashes,
             'production_orm_files_sha256': original_orm_hashes,
             'production_texture_inputs': production_texture_inputs,
             'build_tool_sha256': sha(Path(__file__)),
             'source_glb_sha256': sha(source / 'assets/garden-of-dreams.glb'), 'phases': []}
    def save():
        report_path.write_text(json.dumps(state, indent=2) + '\n')
    save()
    record = json.loads((source / 'assets/garden-source.json').read_text())
    assert record['source_glb_sha256'] == state['source_glb_sha256']
    shutil.copytree(source, fixture, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.godot', 'android', 'tests'))
    runtime_names = ['entry_route.gd', 'reading_result.gd', 'demo_finale.gd', 'baked_materials.gd']
    production_runtime_hashes = {name: sha(source / 'runtime' / name) for name in runtime_names}
    renderer_paths = ['runtime/baked_materials.gd', 'shaders/baked_diffuse.gdshader']
    production_renderer_hashes = {name: sha(source / name) for name in renderer_paths}
    state['production_renderer_files_sha256'] = production_renderer_hashes
    if args.reuse_ui_font_sizes:
        edits = [
            ('demo_finale.gd', 'heading.add_theme_font_size_override("font_size", 28)',
             'heading.add_theme_font_size_override("font_size", 22)'),
            ('reading_result.gd', 'card.add_theme_font_size_override("normal_font_size",18)',
             'card.add_theme_font_size_override("normal_font_size",16)'),
        ]
        for name, before, after in edits:
            path = fixture / 'runtime' / name
            contents = path.read_text()
            if contents.count(before) == 1:
                path.write_text(contents.replace(before, after))
            else:
                assert contents.count(before) == 0 and contents.count(after) == 1, 'Missing/ambiguous candidate font override: ' + name
    for size_limit, names in [(args.normal_atlas_size_limit, normal_names),
                              (args.orm_atlas_size_limit, orm_names)]:
        if not size_limit:
            continue
        changes = []
        for name in names:
            path = fixture / 'assets' / (name + '.import')
            contents, count = re.subn(r'^process/size_limit=\d+$',
                                     'process/size_limit=' + str(size_limit),
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
    for name in ['test_moon_runtime_import.gd', 'moon-paint-atlas.json', 'profile_report_store.gd',
                 'runtime_texture_caps.gd', 'test_runtime_texture_caps.gd']:
        shutil.copy2(source / 'tests' / name, fixture / 'tests' / name)
    state['moon_import_configuration'] = configure_moon_import(fixture)
    state['runtime_caps_configuration'] = configure_runtime_caps(fixture)
    assert sha(fixture / 'assets/garden-of-dreams.glb') == state['source_glb_sha256']
    project = fixture / 'project.godot'
    contents = project.read_text()
    assert contents.count('[rendering]') == 1
    contents = contents.replace('[rendering]', '[rendering]\ntextures/vram_compression/import_etc2_astc=true')
    main_scenes = re.findall(r'^run/main_scene="([^"]+)"$', contents, flags=re.MULTILINE)
    assert len(main_scenes) == 1 and main_scenes[0] in [
        'res://runtime/first_reading_demo.tscn', 'res://runtime/entry_route.tscn'
    ], 'Unexpected production main scene; profiling must use a known Garden project'
    contents = contents.replace('run/main_scene="' + main_scenes[0] + '"',
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
                  'report_store_script_sha256': sha(fixture / 'tests/profile_report_store.gd'),
                  'inventory_script_sha256': sha(fixture / 'tests/texture_binding_inventory.gd'),
                  'runtime_caps_script_sha256': {name: sha(source / 'tests' / name) for name in ['runtime_texture_caps.gd', 'test_runtime_texture_caps.gd']},
                  'moon_check_script_sha256': sha(fixture / 'tests/test_moon_runtime_import.gd'),
                  'moon_paint_atlas_sha256': sha(fixture / 'tests/moon-paint-atlas.json'),
                  'normal_atlas_size_limit': args.normal_atlas_size_limit,
                  'orm_atlas_size_limit': args.orm_atlas_size_limit,
                  'reuse_ui_font_sizes': args.reuse_ui_font_sizes,
                  'normal_png_sha256': {name: sha(fixture / 'assets' / name) for name in normal_names},
                  'normal_import_sha256': {name: sha(fixture / 'assets' / (name + '.import')) for name in normal_names},
                  'orm_png_sha256': {name: sha(fixture / 'assets' / name) for name in orm_names},
                  'orm_import_sha256': {name: sha(fixture / 'assets' / (name + '.import')) for name in orm_names},
                  'production_runtime_script_sha256': production_runtime_hashes,
                  'runtime_script_sha256': {name: sha(fixture / 'runtime' / name) for name in runtime_names},
                  'renderer_files_sha256': {name: sha(fixture / name) for name in renderer_paths},
                  'demo_index_sha256': sha(fixture / 'lightmaps/demo-index.json'),
                  'full_index_sha256': sha(fixture / 'lightmaps/full-index.json'),
                  'inscription_import_sha256': [sha(fixture / 'assets' / ('garden-of-dreams_gate-inscription' + suffix + '.png.import')) for suffix in ['', '-normal']]})
    (fixture / 'export_presets.cfg').write_text('''[preset.0]
name="Android Profile"
platform="Android"
runnable=true
custom_features="garden_profile"
export_filter="all_resources"
include_filter="*.json"
exclude_filter="assets/kits/corridor/KIT_*,assets/kits/pavilion/KIT_*,assets/kits/wall/KIT_*,assets/kits/rockery/KIT_*,assets/kits/water/KIT_*,assets/kits/props/KIT_*,assets/kits/tech/KIT_*,assets/kits/stage/KIT_*,assets/kits/KIT_stage*.glb"
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
                          ('moon-runtime-import-check', [GODOT, '--headless', '--path', str(fixture),
                           '--script', 'res://tests/test_moon_runtime_import.gd', '--',
                           '--output=' + str(fixture / 'moon-runtime-import-check.json')]),
                          ('runtime-texture-cap-check', [GODOT, '--headless', '--path', str(fixture),
                           '--script', 'res://tests/test_runtime_texture_caps.gd', '--',
                           '--output=' + str(fixture / 'runtime-texture-caps.json')]),
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
        if name == 'mobile-texture-import':
            verify_texture_inputs(source, production_texture_inputs, 'Production')
            staged_texture_inputs = texture_input_snapshot(fixture)
            for texture, expected in production_texture_inputs.items():
                assert staged_texture_inputs[texture]['source_sha256'] == expected['source_sha256'], 'Staged texture source changed: ' + texture
            build.update({
                'texture_provenance_version': 1,
                'production_texture_inputs': production_texture_inputs,
                'staged_texture_inputs': staged_texture_inputs,
                'normal_import_sha256': {name: sha(fixture / 'assets' / (name + '.import')) for name in normal_names},
                'orm_import_sha256': {name: sha(fixture / 'assets' / (name + '.import')) for name in orm_names},
                'inscription_import_sha256': [sha(fixture / 'assets' / ('garden-of-dreams_gate-inscription' + suffix + '.png.import')) for suffix in ['', '-normal']],
            })
            state['staged_texture_inputs'] = staged_texture_inputs
            save()
        if name == 'moon-runtime-import-check':
            moon = json.loads((fixture / 'moon-runtime-import-check.json').read_text())
            assert moon['status'] == 'passed' and not moon['errors']
            assert moon['source_glb_sha256'] == state['source_glb_sha256']
            assert moon['source_png_sha256'] == sha(fixture / 'assets/garden-of-dreams_moon-paint.png')
            assert moon['loaded_size'] == [512, 512]
            build['moon_runtime_import'] = moon
            save()
        if name == 'runtime-texture-cap-check':
            caps = json.loads((fixture / 'runtime-texture-caps.json').read_text())
            verify_loaded_caps(fixture, caps)
            build['runtime_texture_caps'] = caps
            verify_manifest_caps(source, fixture, build)
            # Pin finalized imports, generated pixels and active bindings before export.
            (fixture / 'phone-profile-build.json').write_text(json.dumps(build, indent=2) + '\n')
            state['phone_profile_build_sha256'] = sha(fixture / 'phone-profile-build.json')
            save()
    assert sha(fixture / 'assets/garden-of-dreams.glb') == state['source_glb_sha256']
    verify_texture_inputs(source, production_texture_inputs, 'Production')
    verify_texture_inputs(fixture, staged_texture_inputs, 'Staged')
    for name, expected in {**original_normal_hashes, **original_orm_hashes}.items():
        assert sha(source / 'assets' / name) == expected, 'Production atlas asset changed: ' + name
        if not name.endswith('.import'):
            assert sha(fixture / 'assets' / name) == expected, 'Source PNG changed in fixture: ' + name
    for name, expected in production_runtime_hashes.items():
        assert sha(source / 'runtime' / name) == expected, 'Production runtime changed: ' + name
    for name, expected in production_renderer_hashes.items():
        assert sha(source / name) == sha(fixture / name) == expected, 'Renderer changed: ' + name
    verify_manifest_caps(source, fixture, build)
    state['apk_sha256'] = sha(output)
    state['apk_bytes'] = output.stat().st_size
    state['status'] = 'built'
    state['device_tested'] = False
    save()
    print('ANDROID_PROFILE_APK_BUILT', state['apk_bytes'], state['apk_sha256'])


if __name__ == '__main__':
    main()
