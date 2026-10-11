"""Verify actual study-key coverage and a restoring negative control.

Run in a separate Blender process with the saved authoring file. Nothing is
saved to the blend file. Cone coverage does not prove exposure or legibility.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from math import radians

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from study_lighting_contract import inspect
from moon_paint_contract import snapshot

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--report', type=Path,
                    default=ROOT / 'export/study-lighting-coverage.json')
options = parser.parse_args(args)
source = Path(bpy.data.filepath)
assert source.is_file(), 'Load the saved authoring file in a separate process'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
coverage = inspect()
report = {'status': 'failed_source_key_coverage', 'authoring_sha256': digest,
          'source': str(source), 'coverage': coverage,
          'scope': 'Actual source cone and restoring old-layout control; no exposure, final art, engine or device acceptance.'}
options.report.parent.mkdir(parents=True, exist_ok=True)
options.report.write_text(json.dumps(report, indent=2) + '\n')
assert coverage['status'] == 'passed', 'The source key misses the outer banks'
site = bpy.data.collections['SITE_qiushuang-zhai']
practicals = [o for o in site.objects
              if o.type == 'LIGHT' and o.name.startswith('LGT_study_warm_')]
assert len(practicals) == 2 and all(o.data.type == 'POINT' for o in practicals)
before = snapshot()
key = bpy.data.objects['LGT_qiushuang-zhai_key']
original = (key.location.copy(), key.rotation_euler.copy(), key.data.spot_size)
try:
    key.location = (22, 12, 2.6)
    key.rotation_euler = (Vector((22, 15.4, 1.4)) - key.location).to_track_quat('-Z', 'Y').to_euler()
    key.data.spot_size = radians(45)
    bpy.context.view_layer.update()
    negative = inspect()
    assert negative['status'] == 'failed_key_misses_screen_banks'
    assert negative['inside_cone'] == 192 and negative['samples'] == 576
finally:
    key.location, key.rotation_euler, key.data.spot_size = original
    bpy.context.view_layer.update()
assert snapshot() == before and inspect() == coverage
assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
report.update(status='passed', negative_control=negative,
              unchanged_source_state=True, practical_names=sorted(o.name for o in practicals))
options.report.write_text(json.dumps(report, indent=2) + '\n')
print('STUDY_LIGHTING_COVERAGE_PASS: 576 source samples; old layout192; full state restored')
