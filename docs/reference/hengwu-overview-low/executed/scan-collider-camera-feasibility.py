"""Approximate camera directions from current world bounds, never acceptance."""
from pathlib import Path
import itertools
import json
import math

work = Path(__file__).parent
source = json.loads((work / 'current-source-constraints.json').read_text())
bounds = source['collider_bounds']
subjects = ['COL_hengwu_table', 'COL_hengwu_rock', 'COL_hengwu_stool',
            'COL_hengwu_stool_001', 'COL_hengwu_stool_002', 'COL_hengwu_stool_003']
points = {name: list(itertools.product(*zip(bounds[name]['min'], bounds[name]['max']))) for name in subjects}
sub = lambda a, b: tuple(x-y for x, y in zip(a, b))
dot = lambda a, b: sum(x*y for x, y in zip(a, b))
cross = lambda a, b: (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
normalize = lambda a: tuple(v/math.sqrt(dot(a, a)) for v in a)

def project(eye, target, fov, width, height, keep_width):
    forward = normalize(sub(target, eye))
    right = normalize(cross(forward, (0, 1, 0)))
    up = cross(right, forward)
    tan = math.tan(math.radians(fov)/2)
    tan_x, tan_y = (tan, tan*height/width) if keep_width else (tan*width/height, tan)
    result = {}
    for name, geometry in points.items():
        pixels = []
        for world in geometry:
            delta = sub(world, eye)
            depth = dot(delta, forward)
            if depth <= 0:return None
            pixels.append((width*(.5+dot(delta, right)/(2*depth*tan_x)), height*(.5-dot(delta, up)/(2*depth*tan_y))))
        result[name] = {'min': [min(p[i] for p in pixels) for i in (0, 1)],
                        'max': [max(p[i] for p in pixels) for i in (0, 1)]}
    return result

def fits(rows, width, panel_top):
    return rows is not None and all(row['min'][0]>=12 and row['max'][0]<=width-12 and
        row['min'][1]>=49 and row['max'][1]<=panel_top-14 for row in rows.values())

baseline_eye = (-17.5, 2.6, -10.5)
baseline_target = (-18, 1.1, -15.2)
baseline = {label: project(baseline_eye, baseline_target, 55, width, height, keep)
            for label, width, height, keep in [('desktop', 1410, 600, False), ('portrait', 390, 844, True), ('narrow', 360, 800, True)]}
candidates = []
for x, y, z, tx, ty, tz, fov in itertools.product(
        [-21.8, -20.8, -19.8, -18.8, -17.8, -16.8, -15.8, -14.8],
        [1.6, 1.9, 2.2, 2.5], [-10.5, -11, -11.5],
        [-19, -18.5, -18, -17.5], [-1, -.5, 0, .5, 1], [-14, -14.8, -15.4],
        [55, 65, 75, 85, 95, 105]):
    eye, target = (x, y, z), (tx, ty, tz)
    # A conservative box check excludes cameras in walls or stones; floors are intentionally excluded.
    if any(all(row['min'][i]-.2 <= eye[i] <= row['max'][i]+.2 for i in range(3))
           for name, row in bounds.items() if 'floor' not in name and 'court' not in name and 'approach' not in name):continue
    rows = project(eye, target, fov, 390, 844, True)
    if not fits(rows, 390, 534):continue
    narrow = project(eye, target, fov, 360, 800, True)
    if not fits(narrow, 360, 502):continue
    width = rows['COL_hengwu_table']['max'][0]-rows['COL_hengwu_table']['min'][0]
    rock_width = rows['COL_hengwu_rock']['max'][0]-rows['COL_hengwu_rock']['min'][0]
    score = min(width, rock_width)-.4*(fov-55)-5*abs(y-1.9)
    candidates.append({'eye': eye, 'target': target, 'horizontal_fov': fov, 'score': score,
                       'portrait_collider_projection': rows, 'narrow_collider_projection': narrow})
candidates.sort(key=lambda row: row['score'], reverse=True)
selected = []
for row in candidates:
    if any(sum((a-b)**2 for a, b in zip(row['eye'], prior['eye'])) < .75 for prior in selected):continue
    selected.append(row)
    if len(selected)==6:break
report = {'status': 'approximate_collider_camera_directions_only', 'source_glb_sha256': source['source_glb_sha256'],
          'runtime_sha256': source['runtime_sha256'], 'subjects': subjects, 'baseline': baseline,
          'fitting_approximate_candidates': len(candidates), 'selected_directions': selected,
          'scope': 'CPU projection of collision boxes using assumed UI bounds from current original arrivals. Includes four stools and nearest pierced stone. Boxes do not establish rendered geometry, occlusion, lens quality or readable art. No production camera edit or native process; original comparison and actual-geometry/ID controls required before selecting any pose.'}
(work / 'approximate-camera-directions.json').write_text(json.dumps(report, indent=2)+'\n')
print('HENGWU_APPROXIMATE_DIRECTIONS', len(candidates), 'fitting boxes;', len(selected), 'distinct directions; no visual acceptance')
