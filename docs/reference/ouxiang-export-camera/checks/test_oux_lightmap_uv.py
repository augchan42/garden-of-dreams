"""Real exported roof fixtures: approved bytes, idempotence and fail-before-write."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import tempfile
import unittest
import numpy as np
from verify_mountain_export import Glb
from ouxiang_tile_lightmap_uv import allocate_oux_charts

ROOT = Path(__file__).resolve().parents[1]
NAME = 'SITE_ouxiang-xie_MAT_rooftile'
APPROVED = 'be80374cbc0959830205af0efbe198f044ec25df15e7933c91178d0ecf516e5a'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class OuxiangExportCharts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='garden-oux-export-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def fixture(self, source):
        path = self.root / source.name
        shutil.copy2(source, path)
        return path

    def test_complete_export_reproduces_native_reviewed_candidate(self):
        path = self.fixture(ROOT / 'docs/reference/imperial-roof-charts/candidate-complete.glb')
        report = allocate_oux_charts(path)
        self.assertEqual(digest(path), APPROVED)
        self.assertEqual(report['target_triangles'], 4730)
        self.assertGreaterEqual(report['target_uv2_minimum_altitude_at_512'], 1.0)
        self.assertEqual(report['all_expanded_triangles_checked'], 241810)

    def test_target_site_reproduces_complete_candidate_attributes(self):
        path = self.fixture(ROOT / 'export/sites/SITE_ouxiang-xie.glb')
        allocate_oux_charts(path)
        site = Glb(path)
        complete = Glb(ROOT / 'docs/reference/ouxiang-roof-proposal/garden-oux-uv-proposal.glb')
        def expanded(g):
            n = next(n for n in g.doc['nodes'] if n.get('name') == NAME)
            p = g.doc['meshes'][n['mesh']]['primitives'][0]
            indices = g.accessor(p['indices']).ravel()
            return {k: g.accessor(v)[indices] for k, v in p['attributes'].items()}
        a, b = expanded(site), expanded(complete)
        self.assertEqual(a.keys(), b.keys())
        for key in a:
            np.testing.assert_array_equal(a[key], b[key], err_msg=key)

    def test_second_allocation_leaves_file_bytes_unchanged(self):
        path = self.fixture(ROOT / 'export/sites/SITE_ouxiang-xie.glb')
        allocate_oux_charts(path)
        before = path.read_bytes()
        report = allocate_oux_charts(path)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(report['status'], 'already_allocated')

    def test_distorted_cylinder_rejected_without_writing(self):
        path = self.fixture(ROOT / 'export/sites/SITE_ouxiang-xie.glb')
        g = Glb(path)
        n = next(n for n in g.doc['nodes'] if n.get('name') == NAME)
        p = g.doc['meshes'][n['mesh']]['primitives'][0]
        a = g.doc['accessors'][p['attributes']['POSITION']]
        view = g.doc['bufferViews'][a['bufferView']]
        indices = g.accessor(p['indices']).ravel()
        positions = g.accessor(p['attributes']['POSITION'])
        # Use a natively inspected saved tile vertex, not a classifier from
        # the implementation under test. Move all its split export copies.
        inventory = json.loads((ROOT / 'docs/reference/ouxiang-roof-native/source-inspection/source-geometry.json').read_text())
        tile = next(row for row in inventory['objects'] if row['name'].startswith('KIT_pavilion_water_tiles'))
        x, y, z = tile['world_positions_z_up'][0]
        expected = np.asarray([x, z, -y])
        index = np.linalg.norm(positions - expected, axis=1).argmin()
        self.assertLess(float(np.linalg.norm(positions[index] - expected)), 3e-5)
        chosen = positions[index]
        data = bytearray(g.bytes)
        binary_offset = 28 + struct.unpack_from('<I', data, 12)[0]
        stride = view.get('byteStride', 12)
        for i in np.flatnonzero(np.all(positions == chosen, axis=1)):
            offset = binary_offset + view.get('byteOffset', 0) + a.get('byteOffset', 0) + int(i) * stride
            struct.pack_into('<f', data, offset, float(positions[i, 0]) + 0.1)
        path.write_bytes(data)
        before = path.read_bytes()
        with self.assertRaises(AssertionError):
            allocate_oux_charts(path)
        self.assertEqual(path.read_bytes(), before)

if __name__ == '__main__':
    unittest.main()
