"""Exercise the atlas export gate with the actual preceding scene and atlas bytes.

The positive fixture is a CPU binary substitution, not a Blender export or bake.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct

from verify_garden_atlas_export import compare
from verify_mountain_export import Glb


def write_glb(path, doc, binary):
    document = json.dumps(doc, separators=(',', ':')).encode()
    document += b' ' * (-len(document) % 4)
    binary = bytes(binary) + b'\0' * (-len(binary) % 4)
    path.write_bytes(struct.pack('<III', 0x46546c67, 2, 28+len(document)+len(binary))
                     + struct.pack('<II', len(document), 0x4e4f534a) + document
                     + struct.pack('<II', len(binary), 0x004e4942) + binary)


def main():
    parser = argparse.ArgumentParser()
    for flag in ('before', 'baseline-root', 'candidate-root', 'output-root'):
        parser.add_argument('--'+flag, type=Path, required=True)
    args = parser.parse_args()
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=False)
    previous = Glb(args.before)
    doc = copy.deepcopy(previous.doc)
    binary = bytearray(previous.binary)
    for kind in ('pavilion', 'wall'):
        image = next(i for i in doc['images'] if i['name'] == kind+'_basecolor')
        view = doc['bufferViews'][image['bufferView']]
        assert not any(a.get('bufferView') == image['bufferView'] for a in doc['accessors'])
        binary += b'\0' * (-len(binary) % 4)
        data = (args.candidate_root/'textures/atlases'/kind/f'{kind}_basecolor.png').read_bytes()
        view['byteOffset'], view['byteLength'] = len(binary), len(data)
        binary += data
    doc['buffers'][0]['byteLength'] = len(binary)
    positive = root/'atlas-color-substitution.glb'
    write_glb(positive, doc, binary)
    report = compare(args.before, positive, args.baseline_root, args.candidate_root)
    (root/'positive-preservation.json').write_text(json.dumps(report, indent=2)+'\n')
    results = []

    def reject(name, changed_doc, changed_binary):
        file = root/(name+'.glb')
        write_glb(file, changed_doc, changed_binary)
        try:
            compare(args.before, file, args.baseline_root, args.candidate_root)
        except AssertionError as error:
            results.append({'case':name, 'rejected':True, 'reason':str(error),
                            'fixture_sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
            file.unlink()
        else:
            raise AssertionError('Unexpected acceptance: '+name)

    reject('unchanged-old-palette', previous.doc, previous.binary)
    bad = copy.deepcopy(doc)
    node = next(n for n in bad['nodes'] if 'camera' in n)
    node['translation'] = [100, 100, 100]
    reject('changed-camera', bad, binary)
    for attribute in ('POSITION', 'TEXCOORD_0', 'TEXCOORD_1'):
        bad_binary = bytearray(binary)
        primitive = next(p for m in doc['meshes'] for p in m['primitives'] if attribute in p['attributes'])
        index = previous.accessor(primitive['indices']).ravel()[0]
        accessor = doc['accessors'][primitive['attributes'][attribute]]
        assert accessor['componentType'] == 5126
        view = doc['bufferViews'][accessor['bufferView']]
        columns = {'VEC2':2, 'VEC3':3}[accessor['type']]
        offset = view.get('byteOffset', 0)+accessor.get('byteOffset', 0)+int(index)*view.get('byteStride', columns*4)
        value = struct.unpack_from('<f', bad_binary, offset)[0]
        struct.pack_into('<f', bad_binary, offset, value+1)
        reject('changed-'+attribute.lower(), doc, bad_binary)
    bad_binary = bytearray(binary)
    normal = next(i for i in doc['images'] if i['name'] == 'pavilion_normal')
    offset = doc['bufferViews'][normal['bufferView']].get('byteOffset', 0)
    bad_binary[offset+16] ^= 1
    reject('changed-normal-image', doc, bad_binary)
    bad = copy.deepcopy(doc)
    material = next(m for m in bad['materials'] if m['name'] == 'MAT_pavilion_atlas')
    material['emissiveFactor'] = [1, 1, 1]
    reject('changed-emission', bad, binary)
    bad = copy.deepcopy(doc)
    assert bad['samplers']
    bad['samplers'][0]['wrapS'] = 33071 if bad['samplers'][0].get('wrapS') != 33071 else 10497
    reject('changed-sampler', bad, binary)
    bad = copy.deepcopy(doc)
    bad['images'][0]['mimeType'] = 'image/jpeg'
    reject('changed-image-mime-type', bad, binary)
    site_results = {}
    for file in sorted((args.before.parent/'sites').glob('*.glb')):
        scene = Glb(file)
        kinds = [kind for kind in ('pavilion', 'wall')
                 if any(i['name'] == kind+'_basecolor' for i in scene.doc['images'])]
        if not kinds:
            site_results[file.name] = {'atlas_color_images_present':False, 'scope':'No atlas substitution needed; native site export still required.'}
            continue
        site_doc = copy.deepcopy(scene.doc)
        site_binary = bytearray(scene.binary)
        for kind in kinds:
            image = next(i for i in site_doc['images'] if i['name'] == kind+'_basecolor')
            view = site_doc['bufferViews'][image['bufferView']]
            site_binary += b'\0' * (-len(site_binary) % 4)
            data = (args.candidate_root/'textures/atlases'/kind/f'{kind}_basecolor.png').read_bytes()
            view['byteOffset'], view['byteLength'] = len(site_binary), len(data)
            site_binary += data
        site_doc['buffers'][0]['byteLength'] = len(site_binary)
        fixture = root/('control-'+file.name)
        write_glb(fixture, site_doc, site_binary)
        site_results[file.name] = compare(file, fixture, args.baseline_root, args.candidate_root, require_both=False)
        fixture.unlink()
    assert len(site_results) == 15, 'All site fixtures required'
    summary = {'status':'atlas_export_gate_controls_passed',
               'scope':'CPU substitution of two actual candidate PNGs into the actual neutral scene. No Blender source save, native import, lighting bake or production adoption claimed.',
               'positive_fixture_sha256':report['after_sha256'], 'positive':report,
               'negative_cases':results, 'site_controls':site_results}
    (root/'gate-controls.json').write_text(json.dumps(summary, indent=2)+'\n')
    print('GARDEN_ATLAS_EXPORT_GATE_CONTROLS_PASS', len(results))


if __name__ == '__main__':
    main()
