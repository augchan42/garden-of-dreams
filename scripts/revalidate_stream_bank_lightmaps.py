"""Prepare an isolated UV-only bank candidate, retaining other bake provenance.

Requires a completed single-atlas bake and an isolated Godot copy. Does not
modify the working source tree. Other PNGs remain byte-identical; only their
compatibility records change after the geometry/UV preservation proof passes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from verify_stream_bank_export import verify, TARGET
from verify_canopy_candidate import Document

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(candidate):
    candidate = candidate.resolve()
    assert candidate != ROOT and (candidate/'godot/project.godot').is_file()
    proof = verify(ROOT/'export/garden-of-dreams.glb', candidate/'export/garden-of-dreams.glb')
    old, new = proof['previous_source_glb_sha256'], proof['source_glb_sha256']
    assert old != new
    proof_path = candidate/'export/stream-bank-lightmap-compatibility.json'
    proof_path.write_text(json.dumps(proof, indent=2)+'\n')
    fresh_path = candidate/'export/lightmaps'/f'{TARGET}.json'
    fresh = json.loads(fresh_path.read_text())
    assert fresh['source_glb_sha256'] == new and fresh['size'] == 1024 and fresh['samples'] == 128
    assert TARGET in Document(candidate/'export/sites/SITE_qinfang-ting.glb').nodes
    fresh['site'] = 'qinfang-ting'  # Single-mesh baker does not populate site membership.
    fresh['status'] = 'Fresh Cycles bake for visible stream-bank UV2 charts'
    fresh_path.write_text(json.dumps(fresh, indent=2)+'\n')
    fresh_png = fresh_path.with_suffix('.png')
    assert fresh_png.is_file()
    reference = {'proof': 'export/stream-bank-lightmap-compatibility.json',
                 'proof_sha256': sha(proof_path), 'changed_receiver': TARGET}

    def revalidate(value):
        if isinstance(value, list):
            return [revalidate(v) for v in value]
        if not isinstance(value, dict):
            return value
        if value.get('mesh') == TARGET and value.get('source_glb_sha256') == old:
            return fresh | ({'engine_node': value['engine_node']} if 'engine_node' in value else {})
        result = {k: revalidate(v) for k, v in value.items()}
        if result.get('source_glb_sha256') == old:
            result.setdefault('baked_from_source_glb_sha256', old)
            result['source_glb_sha256'] = new
            result['stream_bank_uv_revalidation'] = reference
        return result

    retained = {}
    changed_json = []
    for relative in ('export/lightmaps', 'godot/lightmaps'):
        for source in (ROOT/relative).rglob('*'):
            if not source.is_file() or source.suffix not in ('.json', '.png'):
                continue
            rel = source.relative_to(ROOT)
            target = candidate/rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.name == f'{TARGET}.png':
                if target != fresh_png:
                    shutil.copy2(fresh_png, target)
            elif source.suffix == '.json':
                data = revalidate(json.loads(source.read_text()))
                target.write_text(json.dumps(data, indent=2)+'\n')
                changed_json.append(str(rel))
            else:
                shutil.copy2(source, target)
                assert sha(source) == sha(target)
                retained[str(rel)] = sha(source)
    for relative in ('assets/garden-of-dreams.glb',):
        source = candidate/'export'/relative.removeprefix('assets/')
        assert source.is_file(), source
        shutil.copy2(source, candidate/'godot'/relative)
    (candidate/'godot/assets/garden-source.json').write_text(json.dumps({'source_glb_sha256': new}, indent=2)+'\n')
    import_path = candidate/'godot/lightmaps'/f'{TARGET}.png.import'
    text = import_path.read_text().replace('compress/mode=2', 'compress/mode=0').replace('process/size_limit=256', 'process/size_limit=1024')
    assert 'compress/mode=0' in text and 'process/size_limit=1024' in text
    import_path.write_text(text)
    report = {'status': 'prepared_for_native_review', 'source_glb_sha256': new,
              'retained_png_sha256': retained, 'revalidated_json': changed_json,
              'fresh_atlas_png_sha256': sha(fresh_png), 'proof_sha256': sha(proof_path)}
    (candidate/'lighting-revalidation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BANK_LIGHTING_PREPARED', len(retained), len(changed_json))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('candidate', type=Path)
    prepare(p.parse_args().candidate)
