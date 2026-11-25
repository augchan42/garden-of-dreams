"""Pin source texture bytes and their effective Godot import parameters."""
import hashlib
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def texture_input_snapshot(project):
    project = Path(project)
    records = {}
    for path in sorted(project.rglob('*.import')):
        relative = path.relative_to(project)
        # The profiling builder excludes test fixtures and native build outputs.
        if any(part in relative.parts for part in ['.godot', 'android', 'tests']):
            continue
        raw = path.read_bytes()
        text = raw.decode('utf-8')
        if 'importer="texture"' not in text:
            continue
        source = path.with_suffix('')
        assert source.is_file(), 'Missing texture source: ' + str(relative)
        _, separator, parameters = text.partition('\n[params]\n')
        assert separator, 'Missing texture parameters: ' + str(relative)
        records[source.relative_to(project).as_posix()] = {
            'source_sha256': digest(source.read_bytes()),
            'import_sha256': digest(raw),
            'parameters_sha256': digest(parameters.encode('utf-8')),
        }
    assert records, 'No texture input records'
    return records


def verify_texture_inputs(project, expected, label):
    actual = texture_input_snapshot(project)
    assert set(actual) == set(expected), label + ' texture input set changed after APK build'
    changed = [name for name in actual if actual[name] != expected[name]]
    assert not changed, label + ' texture inputs changed after APK build: ' + ', '.join(changed)
