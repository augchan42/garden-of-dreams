"""Reject saved duplicate floor surfaces and lost floor coverage in Blender.

The baseline records include all upward polygons, including the unchanged
pavilion plinth. The audit uses independent intersections and scanline unions.
No Blender files are saved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_paving_footprint import inspect_scene, faces, overlaps, compare_footprint


def inspect(baseline):
    scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
    bpy.context.window.scene=scene
    bpy.context.view_layer.update()
    actual=inspect_scene(scene)
    old,new=faces(json.loads(Path(baseline).read_text())),faces(actual)
    bad=overlaps(new)
    assert not bad, ('Duplicate saved paving',bad)
    coverage=compare_footprint(old,new)
    return {'visible_top_faces':len(new),'positive_coplanar_pairs':0,'footprint':coverage}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert not args.output.exists(),'Do not overwrite prior source evidence'
    source=Path(bpy.data.filepath)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    report=inspect(args.baseline)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    report.update(status='saved_paving_source_passed',authoring_sha256=digest,
                  baseline_sha256=hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
                  scope='Read-only actual saved top faces: no duplicate area above1e-5m2; complete baseline floor union within10micrometre XY storage precision. No lighting or rendering acceptance.')
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('SAVED_PAVING_SOURCE_PASS',len(faces(inspect_scene(bpy.context.scene))),flush=True)


if __name__=='__main__':main()
