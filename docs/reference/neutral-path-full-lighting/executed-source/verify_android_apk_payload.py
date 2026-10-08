"""Check a filtered Android diagnostic APK against actual runtime texture bindings."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(build_path, baseline_path, inventory_path):
    build = json.loads(build_path.read_text())
    baseline = json.loads(baseline_path.read_text())
    inventory = json.loads(inventory_path.read_text())
    assert inventory['status'] == 'passed' and inventory['mode'] == 'normal'
    assert build['source_glb_sha256'] == baseline['source_glb_sha256'] == inventory['source_glb_sha256']
    for record in [build, baseline]:
        assert record['status'] == 'built'
        assert all(p['status'] == 'passed' and not p.get('engine_diagnostics') for p in record['phases'])
        assert sha(Path(record['apk'])) == record['apk_sha256']
    with zipfile.ZipFile(baseline['apk']) as previous, zipfile.ZipFile(build['apk']) as current:
        old_names, names = set(previous.namelist()), set(current.namelist())
        retained_imports, generated = [], []
        for texture in inventory['textures']:
            path = texture['resource_path']
            if not path:
                assert texture['resource_class'] == 'ViewportTexture', 'Unknown generated texture'
                generated.append({'class': texture['resource_class'], 'bindings': texture['bindings']})
                continue
            assert path.startswith('res://'), path
            name = 'assets/' + path.removeprefix('res://') + '.import'
            assert name in names, 'Missing bound texture import: ' + path
            assert previous.read(name) == current.read(name), 'Changed texture import: ' + path
            remaps = re.findall(r'^path(?:\.[^=]+)?="(res://[^"]+)"$', current.read(name).decode(), re.MULTILINE)
            assert any('assets/' + p.removeprefix('res://') in names for p in remaps), 'Missing imported texture payload: ' + path
            retained_imports.append(name)
        catalog_name = 'assets/assets/flora-placements.json'
        assert catalog_name in names
        placements = json.loads(current.read(catalog_name))
        variants = sorted({p['variant'] for p in placements.values()})
        for variant in variants:
            name = 'assets/assets/kits/flora/KIT_flora_' + variant + '_LOD1.glb.import'
            assert name in names and previous.read(name) == current.read(name), 'Missing/changed runtime flora LOD: ' + variant
        assert 'assets/assets/garden-of-dreams.glb.import' in names
        removed, added = sorted(old_names - names), sorted(names - old_names)
        assert not added, 'Unexpected new package files'
        assert all('KIT_' in n or n.startswith('assets/assets/kits/') for n in removed), 'Removed non-kit package data'
        changed = [n for n in sorted(old_names & names) if previous.read(n) != current.read(n)]
        protected = [n for n in old_names & names if n.startswith(('assets/.godot/imported/', 'assets/runtime/', 'assets/shaders/')) or n.endswith('.json')]
        assert not set(changed) & set(protected), 'Changed retained imported payload, script or catalog'
    return {
        'status': 'archive_payload_verified_device_pending',
        'source_glb_sha256': build['source_glb_sha256'],
        'baseline_apk_sha256': baseline['apk_sha256'], 'apk_sha256': build['apk_sha256'],
        'baseline_apk_bytes': baseline['apk_bytes'], 'apk_bytes': build['apk_bytes'],
        'saved_bytes': baseline['apk_bytes'] - build['apk_bytes'],
        'file_texture_imports_retained': len(retained_imports), 'generated_runtime_textures': generated,
        'runtime_flora_variants_retained': variants, 'unchanged_protected_payloads': len(protected),
        'removed_entries': removed, 'added_entries': added, 'changed_retained_entries': changed,
        'scope': 'APK archive verification against actual normal-route bindings. Native import/export passes are checked; signatures, UID cache and regenerated scene bundles may change. No filtered-APK phone, final art, performance or release acceptance.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-report', required=True, type=Path)
    parser.add_argument('--baseline-build-report', required=True, type=Path)
    parser.add_argument('--inventory', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = verify(args.build_report, args.baseline_build_report, args.inventory)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('ANDROID_APK_PAYLOAD_PASS', report['apk_bytes'], 'saved=', report['saved_bytes'], 'file_textures=', report['file_texture_imports_retained'])


if __name__ == '__main__':
    main()
