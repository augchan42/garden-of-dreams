from pathlib import Path
import json,shutil,hashlib
r=Path(__file__).resolve().parent;repo=Path('/Users/auchan/projects/garden-of-dreams');pub=repo/'docs/reference/aojing-ground-infill';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();review=json.loads((r/'direct-lit-review.json').read_text());assert review['direct_originals_reviewed']==50
for n in review['files']:
 out=pub/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,out)
reports=['direct-lit-review.json','adoption.json','adoption-baseline.json','canonical-replay.json','export-pipeline.json','library-preparation.json','isolated-pipeline.json','lit-validation.json','native-lit-file-verification.json','tour-jobs.json','tour-file-verification.json','native-ground-winding-inspection.json','export/aojing-source-preservation.json','export/export-preservation.json','export/aojing-ground-contract.json','export/canvas-palette-contract.json','export/ground-native-green.json','export/ground-native-baseline-red.json','export/ground-linked-library.json','export/full-lighting-refresh.json']
for n in reports:
 out=pub/'proof'/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,out)
for p in r.iterdir():
 if p.is_file() and p.suffix in ['.py','.gd','.log']:
  out=pub/'executed'/p.name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
for folder in ['lit-validation-logs','failed-native-winding-01']:
 for p in (r/folder).rglob('*'):
  if p.is_file() and p.suffix in ['.json','.py','.gd','.log']:
   out=pub/'executed'/p.relative_to(r);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
readme='''# Aojing west ground infill

A15.4 m² strip west of the pond exposed the black stage floor. One render-only canvas box now fills that strip, clipped away from the pond, approach ramp and dry ledge. All4,467 original objects, material nodes,277,543 existing triangles, cameras and colliders remain intact. The box adds12 triangles. Both ramp guards retain measured clearance; existing route support is unchanged.

![Ground inspection](native-lit-ground/desktop-west_strip.png)

![Pond reflection](native-lit-ground/portrait-reflection.png)

The first source candidate was rejected when canonical joining zeroed48 old primary UV triangles. The corrected source follows the existing UV-free canvas convention; the strict preservation test remains unchanged. All16 canonical GLBs reproduce exactly and14 other site exports are byte-identical to the preceding corridor-roof export. This changes the stage ground, not those sites' geometry.

Six fresh source-lighting phases complete141 maps for the corrected export. All17 isolated native phases pass;86 originals decode and match their capture reports. Both actual desktop and portrait tours visit14 rooms over26 legs, with278 recorded originals and no floor-support failures. Fifty originals were directly inspected: eight ground views,28 room arrivals and14 corridor views. This accepts the bounded ground repair. Broad flat ground areas, abrupt water boundaries, dark covered-walk bands and painted-sky projection artifacts remain for the full art pass.

The first native geometry fixture wrongly expected counter-clockwise Godot triangles. Actual imported old and new faces share clockwise front winding. The corrected test checks all12 face cross products against imported shading normals, outward directions and both upward tops. It retains the measured importer quantization bound. Source/export/bakes did not change for this fixture correction. Original failed logs and fixture remain retained. Godot documents clockwise front faces in its [ArrayMesh reference](https://docs.godotengine.org/en/stable/classes/class_arraymesh.html).

Adoption uses607 exact reviewed source/engine inputs with reversible backups. All499 protected kit/source/runtime inputs and432 kit/lightmap import parameter blocks remain unchanged. In particular, the preceding2048 stage-paint export repair is preserved. Historical isolated native evidence used the preceding stage kit; current installed checks validate the combined production inputs separately.

Installed source/native/render validation is running. No current combined APK, final art, target-phone,2020 Adreno or sustained-budget acceptance is claimed. The previous offline APK predates both this ground addition and the stage-kit input change and remains uninstalled. The separate Ouxiang one-pixel cross-run difference and stage root-window capture timeouts remain unresolved. User editor sessions were not reloaded.

The full goal remains open: fourteen-site art/spec, five missing reference slots, device budgets, release and authenticated reading/history/AI/presence/social. `files.json` hashes all published evidence. Complete source input and all tour/capture originals are retained in the durable goal archive.
'''
(pub/'README.md').write_text(readme)
manifest={'source_glb_sha256':review['source_glb_sha256'],'files':{str(p.relative_to(pub)):sha(p) for p in sorted(pub.rglob('*')) if p.is_file() and p!=pub/'files.json'}};(pub/'files.json').write_text(json.dumps(manifest,indent=2)+'\n')
for n,h in manifest['files'].items():assert sha(pub/n)==h
print('AOJING_PUBLIC_EVIDENCE_PASS',len(manifest['files']))
