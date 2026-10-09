from pathlib import Path
import json
w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root'])
review=w/'reed-bold-native-comparison/visual-rejection.json'
assert not review.exists()
review.write_text(json.dumps({'status':'rejected_geometry_direction','directly_reviewed':['full/ziling_zhou-390x844.png','full/ziling_zhou-1410x600.png'],'reason':'Broad crossed plume cards read as angular flat shards rather than branching reed panicles. No production adoption or fresh lighting acceptance. Remaining originals are retained but not counted as visually reviewed.'},indent=2)+'\n')
s=Path('/tmp/garden_build_reed_bold_candidate.py').read_text().replace("out=w/'reeds-bold'","out=w/'reeds-volume'")
s=s.replace("g.leaf(root,tip,width,'reed',4,angle=.24*(k-1),bend=.10);leaf_data.append", """segments=5 if quality==1 else 2
   leafaxis=(tip-root).normalized();side=leafaxis.cross(Vector((0,0,1))).normalized();rings=[]
   for n in range(segments+1):
    u=n/segments;p=root.lerp(tip,u)+Vector((0,0,.16*math.sin(math.pi*u)));half=width*.5*math.sin(math.pi*u)**.75
    rings.append([p-side*half,p+side*half])
   for n in range(segments):
    g.face([*rings[n],rings[n+1][1],rings[n+1][0]],'culm',[(.2,n/segments),(.8,n/segments),(.8,(n+1)/segments),(.2,(n+1)/segments)])
   leaf_data.append""")
start=s.index('  # Broad card silhouettes')
end=s.index("  details.append",start)
s=s[:start]+'''  # Tapered radial plume volume: silhouette remains readable from all angles.
  sides=8 if quality==1 else 4;levels=5 if quality==1 else 3;rings=[]
  axis=(head(1)-head(.1)).normalized();across=direction.cross(Vector((0,0,1))).normalized();other=axis.cross(across).normalized()
  for n in range(levels+1):
   t=n/levels;radius=.065*math.sin(math.pi*t)**.75+.001
   rings.append([head(t)+radius*(across*math.cos(a*math.tau/sides)+other*math.sin(a*math.tau/sides)) for a in range(sides)])
  for n in range(levels):
   for a in range(sides):
    b=(a+1)%sides
    g.face([rings[n][a],rings[n][b],rings[n+1][b],rings[n+1][a]],'reed_stem',[(a/sides,n/levels),(b/sides,n/levels),(b/sides,(n+1)/levels),(a/sides,(n+1)/levels)])
''' + s[end:]
s=s.replace('three narrow arching leaves per culm and branching tawny plumes with broad crossed silhouette cards','three tapered opaque arching leaves per culm and branching tawny plumes with radial tapered volumes')
Path('/tmp/garden_build_reed_volume_candidate.py').write_text(s)
for old,new in [('run_reed_bold_candidate','run_reed_volume_candidate'),('verify_reed_bold_export','verify_reed_volume_export'),('compare_reed_bold_candidate','compare_reed_volume_candidate')]:
 t=Path('/tmp/garden_'+old+'.py').read_text().replace('reeds-bold','reeds-volume').replace('reed-bold','reed-volume').replace('build_reed_bold_candidate','build_reed_volume_candidate')
 Path('/tmp/garden_'+new+'.py').write_text(t)
print('PREPARED_VOLUME_CANDIDATE')
