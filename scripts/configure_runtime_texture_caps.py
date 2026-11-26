"""Apply reviewed runtime caps and verify actual loaded-resource provenance."""
import hashlib
import json
from pathlib import Path
import re

TARGETS = {'garden-of-dreams_pavilion_basecolor.png': 1024,
           'garden-of-dreams_wall_basecolor.png': 1024,
           'garden-of-dreams_gate-inscription.png': 512,
           'garden-of-dreams_gate-inscription-normal.png': 512}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configure(project, targets=TARGETS):
    project = Path(project).resolve()
    records, pending = [], []
    # Validate every asset before changing any sidecar or generated file.
    for name, size in targets.items():
        png = project / 'assets' / name
        sidecar = png.with_suffix('.png.import')
        before = sidecar.read_text()
        paths = re.findall(r'^path(?:\.[^=]+)?="res://([^"\n]+)"$', before, re.MULTILINE)
        assert paths, 'Missing generated texture paths: ' + name
        caches = [(project / path).resolve() for path in paths]
        assert all(path.parent == (project / '.godot/imported').resolve()
                   and path.name.startswith(name + '-') and path.suffix == '.ctex'
                   for path in caches), 'Unexpected generated cache: ' + name
        stems = {re.sub(r'(?:\.(?:s3tc|etc2))?\.ctex$', '', path.name) for path in caches}
        assert len(stems) == 1, 'Ambiguous generated cache stem: ' + name
        stem = next(iter(stems))
        allowed = {stem + suffix for suffix in ['.md5', '.ctex', '.s3tc.ctex', '.etc2.ctex']}
        invalidated = []
        for path in sorted((project / '.godot/imported').glob(stem + '.*')):
            assert path.name in allowed, 'Unexpected sibling cache: ' + str(path)
            invalidated.append({'path': str(path.relative_to(project)), 'sha256': sha(path)})
        after, count = re.subn(r'^process/size_limit=\d+$', 'process/size_limit=' + str(size),
                              before, flags=re.MULTILINE)
        assert count == 1, 'Missing or ambiguous size limit: ' + name
        settings = {'mipmaps/generate': 'true', 'detect_3d/compress_to': '0',
                    'compress/mode': '2' if 'basecolor' in name else '0'}
        for key, value in settings.items():
            assert len(re.findall('^' + re.escape(key) + '=' + value + '$', after,
                                  re.MULTILINE)) == 1, 'Unexpected texture setting: ' + name + '/' + key
        pending.append((sidecar, after, [project / item['path'] for item in invalidated]))
        records.append({'source': name, 'source_sha256': sha(png), 'size_limit': size,
                        'old_import_sha256': hashlib.sha256(before.encode()).hexdigest(),
                        'new_import_sha256': hashlib.sha256(after.encode()).hexdigest(),
                        'invalidated_cache': invalidated})
    for sidecar, contents, caches in pending:
        sidecar.write_text(contents)
        for cache in caches:
            cache.unlink()
    assert all(sha(project / 'assets' / row['source']) == row['source_sha256'] for row in records)
    return {'status': 'configured_reimport_required',
            'scope': 'Reviewed runtime size limits; source PNGs and other parameters retained. Only same-asset generated cache/MD5 files invalidated.',
            'records': records}


# Exact loaded footprints from the reviewed native and Android comparison.
SIZES = {'pavilion_basecolor': (1024, 1024, 699064, {17, 30}, 15),
         'wall_basecolor': (1024, 1024, 699064, {17, 30}, 1),
         'gate-inscription': (512, 170, 463772, {5}, 1),
         'gate-inscription-normal': (512, 170, 347829, {4}, 1)}
CHECKERS = {'runtime_texture_caps.gd', 'test_runtime_texture_caps.gd'}


def verify_loaded_caps(project, proof):
    project = Path(project)
    assert isinstance(proof, dict) and proof.get('status') == 'passed' and proof.get('errors') == [], 'Runtime cap resource check failed or missing'
    assert proof.get('modes') == ['normal', 'demo'], 'Runtime cap material modes missing'
    assert proof.get('source_glb_sha256') == sha(project / 'assets/garden-of-dreams.glb'), 'Runtime cap staged scene changed'
    textures = proof.get('textures', {})
    assert set(textures) == set(SIZES), 'Runtime cap texture set differs'
    for name, (width, height, footprint, formats, count) in SIZES.items():
        record = textures[name]
        assert record.get('loaded_size') == [width, height], 'Runtime cap loaded size differs: ' + name
        assert record.get('mipmaps') is True, 'Runtime cap mipmaps missing: ' + name
        assert record.get('stored_format') in formats and record.get('stored_mip_bytes') == footprint, 'Runtime cap format or footprint differs: ' + name
        assert record.get('bindings') == {'normal': count, 'demo': count}, 'Runtime cap active material bindings missing: ' + name
        source = project / ('assets/garden-of-dreams_' + name + '.png')
        sidecar = source.with_suffix('.png.import')
        assert record.get('source_sha256') == sha(source), 'Runtime cap source image changed: ' + name
        assert record.get('import_sha256') == sha(sidecar), 'Runtime cap import changed: ' + name
        paths = re.findall(r'^path(?:\.[^=]+)?="res://([^"\n]+)"$', sidecar.read_text(), re.MULTILINE)
        payloads = record.get('cache_payloads', {})
        assert paths and set(payloads) == set(paths), 'Runtime cap generated cache proof missing: ' + name
        for path, expected in payloads.items():
            cache = (project / path).resolve()
            assert cache.parent == (project / '.godot/imported').resolve(), 'Runtime cap cache escapes project'
            assert cache.is_file() and sha(cache) == expected, 'Runtime cap generated pixels changed: ' + name


def verify_manifest_caps(production, staged, manifest):
    assert manifest.get('runtime_texture_caps'), 'APK lacks loaded runtime cap provenance; rebuild the profiler'
    hashes = manifest.get('runtime_caps_script_sha256', {})
    assert set(hashes) == CHECKERS, 'APK lacks runtime cap checker provenance; rebuild the profiler'
    for name, expected in hashes.items():
        for project in [production, staged]:
            assert sha(Path(project) / 'tests' / name) == expected, 'Runtime cap checker changed after APK build: ' + name
    assert sha(Path(production) / 'assets/garden-of-dreams.glb') == manifest['runtime_texture_caps'].get('source_glb_sha256'), 'Runtime cap production scene changed after APK build'
    verify_loaded_caps(staged, manifest['runtime_texture_caps'])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1] / 'godot')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    args.report.write_text(json.dumps(configure(args.project), indent=2) + '\n')
    print('RUNTIME_TEXTURE_CAPS_CONFIGURED: actual loaded-resource check required')
