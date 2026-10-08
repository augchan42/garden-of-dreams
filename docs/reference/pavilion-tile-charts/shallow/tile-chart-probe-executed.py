import bpy,pathlib,json,sys,numpy as np
root=pathlib.Path('/Users/auchan/projects/garden-of-dreams');sys.path.insert(0,str(root/'scripts'))
from pavilion_roof_geometry import components
w=pathlib.Path(json.load(open('/tmp/garden-tile-ridge-candidate.json'))['folder']);bpy.ops.wm.open_mainfile(filepath=str(w/'blender/authoring.blend'));obj=bpy.data.objects['QINFANG_kit_roof_hex'];points=[]
for vertices,faces in components(obj.data):
 if len(vertices)==15 and len(faces)==8:
  points.extend(tuple(float(v) for v in obj.matrix_world@obj.data.vertices[i].co) for i in vertices)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(w/'export/garden-of-dreams.glb'));obj=bpy.data.objects['SITE_qinfang-ting_MAT_pavilion_atlas'];bpy.context.view_layer.update()
points=np.asarray(points)
positions=np.asarray([tuple(obj.matrix_world@vertex.co) for vertex in obj.data.vertices])
matched=np.zeros(len(positions),dtype=bool)
for start in range(0,len(positions),1024):
 block=positions[start:start+1024]
 distance=((block[:,None,:]-points[None,:,:])**2).sum(axis=2).min(axis=1)
 matched[start:start+1024]=distance<1e-10
faces=[p for p in obj.data.polygons if all(matched[i] for i in p.vertices)]
assert len(faces)==672,('Unexpected cap triangle classification',len(faces))
image=bpy.data.images.load(str(w/'export/lightmaps/SITE_qinfang-ting_MAT_pavilion_atlas.png'));image.colorspace_settings.name='Non-Color';width,height=image.size;pixels=np.empty(width*height*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(height,width,4);uv=obj.data.uv_layers[1]
rows=[]
for face in faces:
 coords=np.asarray([uv.data[i].uv for i in face.loop_indices],dtype=float);assert len(coords)==3
 edges=coords[[1,2,0]]-coords
 area=abs(np.linalg.det(np.stack([coords[1]-coords[0],coords[2]-coords[0]])))*width*height/2
 span=np.linalg.norm(edges*np.array([width,height]),axis=1).max();altitude=2*area/span
 center=coords.mean(axis=0);x=min(width-1,max(0,int(center[0]*width)));y=min(height-1,max(0,int(center[1]*height)))
 rows.append({'face':face.index,'uv2':coords.tolist(),'area_texels':float(area),'minimum_altitude_texels':float(altitude),'centroid_rgb':pixels[y,x,:3].astype(float).tolist()})
report={'status':'tile_chart_texels_inspected','scope':'Imported exact candidate cap triangles/native float readback. Centroid samples and UV chart geometry only; not raster coverage, Cycles shadow/radiometric or final art acceptance.','triangles':len(faces),'source_size':[width,height],'area_texel_quantiles':np.quantile([r['area_texels'] for r in rows],[0,.25,.5,.75,1]).tolist(),'minimum_altitude_texel_quantiles':np.quantile([r['minimum_altitude_texels'] for r in rows],[0,.25,.5,.75,1]).tolist(),'centroid_zero_fraction':sum(max(r['centroid_rgb'])==0 for r in rows)/len(rows),'triangles_under_one_texel_altitude':sum(r['minimum_altitude_texels']<1 for r in rows),'rows':rows}
(w/'tile-chart-texels.json').write_text(json.dumps(report,indent=2)+'\n');print('TILE_CHART_TEXELS_PASS',json.dumps({k:v for k,v in report.items() if k!='rows'}))
