"""Regenerate the cyclorama wash losslessly, preserving the native bake pixels."""
import argparse
import hashlib
import json
from pathlib import Path
import re

NAME = 'SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas-front.png'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configure(project):
    project = Path(project).resolve()
    source = project / 'lightmaps/backdrop-wash' / NAME
    sidecar = source.with_suffix('.png.import')
    before = sidecar.read_text()
    paths = re.findall(r'^path(?:\.[^=]+)?="res://([^"\n]+)"$', before, re.MULTILINE)
    assert paths, 'Missing generated wash texture paths'
    caches = [(project / path).resolve() for path in paths]
    folder = (project / '.godot/imported').resolve()
    assert all(p.parent == folder and p.name.startswith(NAME + '-')
               and p.suffix == '.ctex' for p in caches), 'Unexpected wash texture cache'
    stems = {re.sub(r'(?:\.(?:s3tc|etc2))?\.ctex$', '', p.name) for p in caches}
    assert len(stems) == 1, 'Ambiguous wash cache stem'
    stem = next(iter(stems))
    allowed = {stem + suffix for suffix in ['.md5', '.ctex', '.s3tc.ctex', '.etc2.ctex']}
    generated = sorted(folder.glob(stem + '.*'))
    assert all(p.name in allowed and p.resolve().parent == folder for p in generated), 'Unexpected wash cache sibling'
    contents = before
    for key, value in {'compress/mode': '0', 'process/size_limit': '256',
                       'mipmaps/generate': 'false', 'detect_3d/compress_to': '0'}.items():
        contents, count = re.subn(r'^' + re.escape(key) + r'=.*$', key + '=' + value,
                                 contents, flags=re.MULTILINE)
        assert count == 1, 'Missing or ambiguous wash parameter: ' + key
    source_hash = sha(source)
    invalidated = [{'path': p.relative_to(project).as_posix(), 'sha256': sha(p)} for p in generated]
    sidecar.write_text(contents)
    for path in generated:
        path.unlink()
    assert sha(source) == source_hash
    return {'status': 'configured_reimport_required', 'source_sha256': source_hash,
            'size_limit': 256, 'compression': 'lossless', 'invalidated_cache': invalidated,
            'old_import_sha256': hashlib.sha256(before.encode()).hexdigest(),
            'new_import_sha256': hashlib.sha256(contents.encode()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1] / 'godot')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    args.report.write_text(json.dumps(configure(args.project), indent=2) + '\n')
    print('BACKDROP_WASH_IMPORT_CONFIGURED: lossless256; actual-resource check required')
