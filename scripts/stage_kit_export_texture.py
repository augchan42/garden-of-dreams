"""Limit exported stage paint to2048 while retaining its editable source image."""
from contextlib import contextmanager
import bpy

@contextmanager
def exported_stage_paints(materials):
    replacements=[]
    copies={}
    try:
        for material in materials:
            if not material.name.startswith('MAT_stage_cyclorama_'):
                continue
            for node in material.node_tree.nodes:
                if node.type!='TEX_IMAGE' or node.image is None:
                    continue
                source=node.image
                assert tuple(source.size)==(4096,4096),source.name
                if source not in copies:
                    image=source.copy()
                    copies[source]=image
                    image.name=source.name+'.export2048'
                    image.scale(2048,2048)
                    image.pack()
                    assert tuple(image.size)==(2048,2048)
                replacements.append((node,source))
                node.image=copies[source]
        yield
    finally:
        for node,source in replacements:
            node.image=source
        for image in copies.values():
            bpy.data.images.remove(image)
