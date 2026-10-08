"""Inject export corruptions and require the preservation guard to reject them."""
import copy
import json
from pathlib import Path
import struct
import tempfile

import numpy as np

from verify_roof_cone_export import Glb, ROOF, compare, inverted_normal_error

ROOT = Path(__file__).resolve().parents[1]


def write_glb(path, document, binary):
    payload = json.dumps(document, separators=(',', ':')).encode()
    payload += b' ' * (-len(payload) % 4)
    path.write_bytes(struct.pack('<III', 0x46546C67, 2, 28 + len(payload) + len(binary))
                     + struct.pack('<II', len(payload), 0x4E4F534A) + payload
                     + struct.pack('<II', len(binary), 0x004E4942) + binary)


def change_attribute(glb, document, binary, node_name, field, delta):
    node = next(n for n in document['nodes'] if n['name'] == node_name)
    primitive = document['meshes'][node['mesh']]['primitives'][0]
    accessor = document['accessors'][primitive['attributes'][field]]
    view = document['bufferViews'][accessor['bufferView']]
    offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    first = np.frombuffer(binary, dtype='<f4', count=len(delta), offset=offset)
    first += delta


def main():
    source = Path('/tmp/garden-roof-cone-export/export/garden-of-dreams.glb')
    baseline = Path('/tmp/garden-roof-cone-before.glb')
    glb = Glb(source)
    accepted = compare(baseline, source)
    rejected = []
    with tempfile.TemporaryDirectory(prefix='garden-roof-cone-negative-') as directory:
        for case in ('camera', 'spot_outer', 'equal_cones', 'material', 'roof_position', 'roof_uv', 'unrelated_normal'):
            document, binary = copy.deepcopy(glb.doc), bytearray(glb.binary)
            if case == 'camera':
                document['cameras'][0]['perspective']['yfov'] += .01
            elif case in ('spot_outer', 'equal_cones'):
                spot = next(l for l in document['extensions']['KHR_lights_punctual']['lights']
                            if l['name'] == 'LGT_ouxiang-xie_key')['spot']
                spot['outerConeAngle' if case == 'spot_outer' else 'innerConeAngle'] = spot['outerConeAngle'] + (.01 if case == 'spot_outer' else 0)
            elif case == 'material':
                document['materials'][0]['doubleSided'] = not document['materials'][0].get('doubleSided', False)
            else:
                node_name = ROOF
                field, delta = {'roof_position': ('POSITION', [.01, 0, 0]),
                                'roof_uv': ('TEXCOORD_0', [.01, 0]),
                                'unrelated_normal': ('NORMAL', [.01, 0, 0])}[case]
                if case == 'unrelated_normal':
                    node_name = next(n['name'] for n in document['nodes'] if 'mesh' in n and not n['name'].startswith(('COL_', 'KIT_pavilion_roof_')) and n['name'] != ROOF)
                change_attribute(glb, document, binary, node_name, field, delta)
            path = Path(directory) / (case + '.glb')
            write_glb(path, document, binary)
            try:
                compare(baseline, path)
            except AssertionError:
                rejected.append(case)
            else:
                raise AssertionError('Corrupted export accepted: ' + case)
        # The finite LOD tolerance may merge near duplicates but must cover both
        # sets and reject a changed direction, a missing match or downward output.
        old = {(-.085199, -.944189, .318196), (-.085298, -.944181, .318194)}
        new = {(.085298, .944181, -.318194)}
        assert 0 < inverted_normal_error(old, new, True) < .0002
        for case, candidate in [('lod_direction', {(.086298, .944181, -.318194)}),
                                ('lod_missing_match', new | {(0, 1, 0)}),
                                ('lod_still_downward', old)]:
            try:
                inverted_normal_error(old, candidate, True)
            except AssertionError:
                rejected.append(case)
            else:
                raise AssertionError('Invalid LOD normals accepted: ' + case)
    report = {'scope': 'Temporary corruption rejection for the roof/cone export preservation guard; canonical assets untouched.',
              'valid_source_sha256': accepted['after_sha256'], 'rejected_cases': rejected, 'passed': True}
    (ROOT / 'export/roof-cone-export-rejections.json').write_text(json.dumps(report, indent=2) + '\n')
    print('ROOF_CONE_EXPORT_REJECTION_PASS', len(rejected), 'corruptions rejected')


if __name__ == '__main__':
    main()
