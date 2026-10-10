"""Canonical diagnostic producer paths and every staged script dependency."""
from pathlib import Path
import hashlib

COMMON = ['tests/profile_android.gd', 'tests/profile_report_store.gd',
          'tests/runtime_texture_caps.gd', 'tests/texture_binding_inventory.gd']
FULL = ['tests/profile_android_full.gd', 'tests/profile_frame_costs.gd',
        'tests/test_full_garden_traversal.gd']


def dependencies(mode):
    assert mode in ['demo', 'full'], 'Unknown profile mode'
    return COMMON + (FULL if mode == 'full' else [])


def producer(mode):
    assert mode in ['demo', 'full'], 'Unknown profile mode'
    return 'tests/profile_android_full.gd' if mode == 'full' else 'tests/profile_android.gd'


def snapshot(project, mode):
    return {name: hashlib.sha256((Path(project) / name).read_bytes()).hexdigest()
            for name in dependencies(mode)}


def verify(production, staged, manifest):
    mode = manifest.get('profile_mode', 'demo')
    producer_path = producer(mode)
    expected = manifest.get('profile_dependency_sha256')
    # Earlier demo evidence remains readable; full tours always require all dependencies.
    assert mode != 'full' or isinstance(expected, dict), 'Full profile dependency proof missing'
    if expected is not None:
        assert set(expected) == set(dependencies(mode)), 'Profile dependency set differs'
        assert snapshot(production, mode) == expected, 'Production profile dependency changed after build'
        assert snapshot(staged, mode) == expected, 'Staged profile dependency changed after build'
    for label, root in [('Production', production), ('Staged', staged)]:
        actual = hashlib.sha256((Path(root) / producer_path).read_bytes()).hexdigest()
        assert actual == manifest['profile_script_sha256'], label + ' profile producer changed after build'
    return mode


def packaged_payloads(package, staged, manifest):
    """Pin actual compiled diagnostic scripts and the imported scene in the APK."""
    import re
    staged = Path(staged)
    compiled = {}
    for name in dependencies(manifest.get('profile_mode', 'demo')):
        remap = package.read('assets/' + name + '.remap').decode()
        paths = re.findall(r'^path="res://([^"\n]+)"$', remap, re.MULTILINE)
        expected = name.removesuffix('.gd') + '.gdc'
        assert paths == [expected], 'Packaged profile script remap differs: ' + name
        payload = package.read('assets/' + expected)
        assert payload[:4] == b'GDSC', 'Packaged profile script is not compiled: ' + name
        compiled[expected] = hashlib.sha256(payload).hexdigest()
    scene_import = 'assets/garden-of-dreams.glb.import'
    exported = package.read('assets/' + scene_import).decode().rstrip('\0').strip()
    source = (staged / scene_import).read_text().split('\n[deps]\n')[0].strip()
    assert exported == source, 'Packaged scene remap differs'
    paths = re.findall(r'^path="res://([^"\n]+)"$', exported, re.MULTILINE)
    assert len(paths) == 1 and paths[0].startswith('.godot/imported/garden-of-dreams.glb-') and paths[0].endswith('.scn'), 'Packaged scene payload path differs'
    payload = package.read('assets/' + paths[0])
    expected = hashlib.sha256((staged / paths[0]).read_bytes()).hexdigest()
    assert hashlib.sha256(payload).hexdigest() == expected, 'Packaged imported scene changed'
    return {'compiled_profile_script_sha256': compiled, 'scene_payload_sha256': {paths[0]: expected}}
