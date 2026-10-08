"""Reject actual export geometry/material/metadata corruption before baking."""
import argparse
import copy
import json
from pathlib import Path
import struct
import tempfile

from verify_moon_contrast_export import compare
from verify_canopy_candidate import Document

parser=argparse.ArgumentParser()
parser.add_argument('--before',type=Path,required=True)
parser.add_argument('--candidate',type=Path,required=True)
parser.add_argument('--atlas',type=Path,required=True)
parser.add_argument('--report',type=Path,required=True)
args=parser.parse_args()
atlas=json.loads(args.atlas.read_text())
compare(args.before,args.candidate,atlas)
candidate=Document(args.candidate)
rejected=[]
with tempfile.TemporaryDirectory(prefix='garden-moon-contrast-export-rejections-') as folder:
    for label in ['camera','floor-transform','ceiling-shadow','unrelated-material','moon-factor','moon-sampler','duplicate-node','floor-uv']:
        document=copy.deepcopy(candidate.data)
        binary=bytearray(candidate.binary)
        if label=='camera':document['cameras'][0]['perspective']['yfov']+=.02
        elif label=='floor-transform':
            node=next(n for n in document['nodes'] if n['name'].startswith('COL_floor_joint_'))
            if 'matrix' in node:node['matrix'][12]+=.1
            else:node.setdefault('translation',[0,0,0])[0]+=.1
        elif label=='ceiling-shadow':next(n for n in document['nodes'] if n['name']=='SITE_stage_MAT_stage_canopy_paint')['extras']['godot_cast_shadow']=True
        elif label=='unrelated-material':
            material=next(m for m in document['materials'] if m['name']!='MAT_painted_moon')
            material['doubleSided']=not material.get('doubleSided',False)
        elif label=='moon-factor':next(m for m in document['materials'] if m['name']=='MAT_painted_moon')['emissiveFactor'][0]*=.8
        elif label=='moon-sampler':
            material=next(m for m in document['materials'] if m['name']=='MAT_painted_moon')
            texture=document['textures'][material['emissiveTexture']['index']]
            document['samplers'][texture['sampler']]['wrapS']=33071 if document['samplers'][texture['sampler']].get('wrapS')!=33071 else 10497
        elif label=='duplicate-node':document['nodes'].append(copy.deepcopy(document['nodes'][0]))
        else:
            node=next(n for n in document['nodes'] if n['name']=='SITE_terminal-cells_MAT_lattice_wood')
            primitive=document['meshes'][node['mesh']]['primitives'][0]
            accessor=document['accessors'][primitive['attributes']['TEXCOORD_1']]
            view=document['bufferViews'][accessor['bufferView']]
            offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
            struct.pack_into('<f',binary,offset,struct.unpack_from('<f',binary,offset)[0]+.1)
        data=json.dumps(document,separators=(',',':')).encode();data+=b' '*(-len(data)%4)
        tail=struct.pack('<II',len(binary),0x004e4942)+binary
        path=Path(folder)/(label+'.glb')
        path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
        try:compare(args.before,path,atlas)
        except AssertionError as error:rejected.append({'case':label,'reason':str(error)})
        else:raise AssertionError(('Accepted invalid contrast export',label))
args.report.write_text(json.dumps({'scope':'Actual export inputs plus constructed corruptions, rejected before source adoption/baking. Not native pixels or art acceptance.','cases':rejected},indent=2)+'\n')
print('MOON_CONTRAST_EXPORT_REJECTIONS_PASS',len(rejected))
