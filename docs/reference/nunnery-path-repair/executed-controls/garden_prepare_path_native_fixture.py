from pathlib import Path
import hashlib,json,shutil
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path(json.load(open('/tmp/garden-nunnery-path-candidate.json'))['folder']);gd=root/'control-godot';gd.mkdir();(gd/'assets').mkdir();(gd/'shaders').mkdir();(gd/'runtime').mkdir();(gd/'maps').mkdir()
for rel in ['shaders/baked_diffuse.gdshader','runtime/baked_materials.gd']:shutil.copy2(repo/'godot'/rel,gd/rel)
for mode,path in [('before',repo/'export/garden-of-dreams.glb'),('after',root/'export/garden-of-dreams.glb')]:shutil.copy2(path,gd/'assets'/(mode+'.glb'))
shutil.copy2(repo/'export/lightmaps/SITE_stage_MAT_plaster_rock.png',gd/'maps/before.png');shutil.copy2(repo/'export/lightmaps/SITE_stage_MAT_plaster_rock.json',gd/'maps/before.json')
config='''config_version=5
[application]
config/name="Garden paving controlled comparison"
[display]
window/size/viewport_width=390
window/size/viewport_height=844
[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
textures/default_filters/use_nearest_mipmap_filter=false
''';(gd/'project.godot').write_text(config)
# Use the production 256px compression/filter policy for both native maps.
settings=(repo/'godot/lightmaps/SITE_stage_MAT_plaster_rock.png.import').read_text()
for mode in ['before','after']:
 text=settings.replace('res://lightmaps/SITE_stage_MAT_plaster_rock.png','res://maps/'+mode+'.png')
 # Cold import assigns fresh paths/UIDs; only import parameters are copied.
 params=text.split('[params]',1)[1]
 (gd/'maps'/(mode+'.png.import')).write_text('[remap]\nimporter="texture"\ntype="CompressedTexture2D"\n\n[params]'+params)
print('PATH_NATIVE_FIXTURE_PREPARED',gd)
