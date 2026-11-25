"""Verify a fresh diagnostic APK's finalized texture provenance and bound payloads."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

from android_profile_modes import verify as verify_profile_scripts, packaged_payloads
from android_texture_provenance import verify_texture_inputs
from configure_runtime_texture_caps import verify_manifest_caps

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remaps(text):
    return dict(re.findall(r'^(path(?:\.[^=]+)?)="(res://[^"]+)"$', text, re.MULTILINE))


def verify(build_path, inventory_path, previous_path=None):
    build = json.loads(build_path.read_text())
    inventory = json.loads(inventory_path.read_text())
    assert build['status'] == 'built' and all(p['status'] == 'passed' and not p.get('engine_diagnostics') for p in build['phases'])
    assert inventory['status'] == 'passed' and inventory['mode'] == 'normal'
    assert sha(Path(build['apk'])) == build['apk_sha256']
    assert build['source_glb_sha256'] == inventory['source_glb_sha256']
    fixture = Path(build['fixture'])
    manifest_path = fixture/'phone-profile-build.json'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['texture_provenance_version'] == 1
    assert sha(manifest_path) == build['phone_profile_build_sha256']
    verify_texture_inputs(ROOT/'godot', manifest['production_texture_inputs'], 'Production')
    verify_texture_inputs(fixture, manifest['staged_texture_inputs'], 'Staged')
    verify_profile_scripts(ROOT/'godot', fixture, manifest)
    verify_manifest_caps(ROOT/'godot', fixture, manifest)
    payloads, imports, generated = {}, [], []
    with zipfile.ZipFile(build['apk']) as package:
        names = set(package.namelist())
        assert package.read('assets/phone-profile-build.json') == manifest_path.read_bytes()
        profile_payloads = packaged_payloads(package, fixture, manifest)
        for texture in inventory['textures']:
            resource = texture['resource_path']
            if not resource:
                assert texture['resource_class'] == 'ViewportTexture'
                generated.append(texture['bindings'])
                continue
            path = resource.removeprefix('res://')
            assert resource.startswith('res://') and path in manifest['staged_texture_inputs']
            assert texture['source_sha256'] == manifest['production_texture_inputs'][path]['source_sha256']
            assert texture['import_sha256'] == manifest['production_texture_inputs'][path]['import_sha256']
            import_name = 'assets/'+path+'.import'
            assert import_name in names, 'Missing bound import: '+path
            exported = package.read(import_name).decode().rstrip('\0').strip()
            staged = (fixture/(path+'.import')).read_text().split('\n[deps]\n')[0].strip()
            actual_paths, staged_paths = remaps(exported), remaps(staged)
            assert actual_paths and all(staged_paths.get(key) == value for key,value in actual_paths.items())
            # Android strips the unused desktop compression remap.
            removed = set(staged_paths)-set(actual_paths)
            assert removed <= {'path.s3tc'}
            for key in removed:
                staged = re.sub(r'^'+re.escape(key)+r'=.*\n?', '', staged, flags=re.MULTILINE)
            assert exported == staged.strip(), 'Changed exported texture metadata: '+path
            for payload in actual_paths.values():
                relative = payload.removeprefix('res://')
                archive_name = 'assets/'+relative
                assert archive_name in names, 'Missing bound payload: '+path
                expected = sha(fixture/relative)
                assert hashlib.sha256(package.read(archive_name)).hexdigest() == expected, 'Changed bound payload: '+path
                payloads[archive_name] = expected
            imports.append(import_name)
        placements = json.loads(package.read('assets/assets/flora-placements.json'))
        variants = sorted({p['variant'] for p in placements.values()})
        for variant in variants:
            path='assets/kits/flora/KIT_flora_'+variant+'_LOD1.glb.import'
            name='assets/'+path
            assert name in names
            actual=remaps(package.read(name).decode())
            expected=remaps((fixture/path).read_text())
            assert actual and actual==expected
            for resource in actual.values():
                relative=resource.removeprefix('res://')
                assert hashlib.sha256(package.read('assets/'+relative)).hexdigest()==sha(fixture/relative)
        comparison = None
        if previous_path:
            previous = json.loads(previous_path.read_text())
            assert previous['status']=='built' and sha(Path(previous['apk']))==previous['apk_sha256']
            assert previous['source_glb_sha256']==build['source_glb_sha256']
            with zipfile.ZipFile(previous['apk']) as old:
                old_names=set(old.namelist())
                protected=[n for n in old_names & names if n.startswith(('assets/runtime/','assets/shaders/')) or n.endswith('.json') and n!='assets/phone-profile-build.json']
                assert all(old.read(n)==package.read(n) for n in protected), 'Changed runtime, shader or catalog'
                comparison={'previous_apk_sha256':previous['apk_sha256'],'unchanged_runtime_shader_catalog_entries':len(protected),'added_entries':sorted(names-old_names),'removed_entries':sorted(old_names-names),'changed_retained_entries':[n for n in sorted(old_names & names) if old.read(n)!=package.read(n)]}
    return {'profile_mode': manifest.get('profile_mode', 'demo'), **profile_payloads, 'status':'finalized_inputs_and_bound_payloads_verified_device_pending','apk_sha256':build['apk_sha256'],'apk_bytes':build['apk_bytes'],'source_glb_sha256':build['source_glb_sha256'],'production_texture_input_count':len(manifest['production_texture_inputs']),'staged_texture_input_count':len(manifest['staged_texture_inputs']),'bound_file_import_count':len(imports),'generated_textures':generated,'payload_sha256':payloads,'runtime_flora_variants':variants,'previous_comparison':comparison,'scope':'Actual APK manifest, current-source texture provenance, finalized platform remaps/cache payloads and normal-route bound textures verified. No install, phone samples, sustained performance or release acceptance.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-report',type=Path,required=True)
    parser.add_argument('--inventory',type=Path,required=True)
    parser.add_argument('--previous-build-report',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=verify(args.build_report,args.inventory,args.previous_build_report)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('ANDROID_PROFILE_INPUTS_PASS',report['apk_bytes'],'bound imports=',report['bound_file_import_count'])


if __name__=='__main__':
    main()
