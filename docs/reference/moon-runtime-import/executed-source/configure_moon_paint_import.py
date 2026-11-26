"""Retain the original moon painting and regenerate its 512px lossless runtime import."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def configure(project):
    project = Path(project).resolve()
    source = project / 'assets/garden-of-dreams_moon-paint.png'
    sidecar = source.with_suffix('.png.import')
    before = sidecar.read_text()
    matches = re.findall(r'^path="res://([^"\n]+)"$', before, re.MULTILINE)
    assert len(matches) == 1, 'Moon requires one lossless generated cache'
    cache = (project / matches[0]).resolve()
    assert cache.parent == (project / '.godot/imported').resolve(), 'Moon cache must remain inside this project'
    assert cache.name.startswith('garden-of-dreams_moon-paint.png-') and cache.suffix == '.ctex', 'Unexpected moon cache'
    contents = before
    for key, value in {'compress/mode': '0', 'process/size_limit': '512',
                       'mipmaps/generate': 'true', 'detect_3d/compress_to': '0'}.items():
        contents, count = re.subn(r'^' + re.escape(key) + r'=.*$', key + '=' + value,
                                 contents, flags=re.MULTILINE)
        assert count == 1, 'Missing or ambiguous moon parameter: ' + key
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    records = []
    for path in [cache, cache.with_suffix('.md5')]:
        if path.exists():
            records.append({'file': path.relative_to(project).as_posix(),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    sidecar.write_text(contents)
    # Generated texture caches can retain the prior size after a sidecar edit.
    # Remove only this reproducible cache; Godot must rebuild it before adoption.
    for path in [cache, cache.with_suffix('.md5')]:
        path.unlink(missing_ok=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    return {'status': 'configured_reimport_required', 'source_sha256': source_hash,
            'size_limit': 512, 'compression': 'lossless', 'invalidated_cache': records,
            'old_import_sha256': hashlib.sha256(before.encode()).hexdigest(),
            'new_import_sha256': hashlib.sha256(contents.encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1] / 'godot')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = configure(args.project)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('MOON_PAINT_IMPORT_CONFIGURED: original painting, lossless 512px; actual-resource check required')


if __name__ == '__main__':
    main()
