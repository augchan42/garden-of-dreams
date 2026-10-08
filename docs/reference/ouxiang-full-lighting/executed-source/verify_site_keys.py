"""Check the saved missing-key contracts in native Blender, without edits."""
import bpy
import math
from mathutils import Vector

for slug in ('qinfang-ting', 'ouxiang-xie', 'ziling-zhou'):
    collection = bpy.data.collections['SITE_' + slug]
    keys = [o for o in collection.objects if o.type == 'LIGHT'
            and o.data.type in ('SUN', 'SPOT') and o.data.energy > 0]
    assert len(keys) == 1, ('Missing or ambiguous owned key', slug)
    key = keys[0]
    assert key.data.use_shadow, ('Key must cast a hard shadow', slug)
    if slug == 'qinfang-ting':
        assert key.data.type == 'SUN'
        assert abs(key.data.energy - .6) < 1e-5
        assert abs(math.degrees(key.data.angle) - .5) < 1e-5
        forward = key.rotation_euler.to_quaternion() @ Vector((0, 0, -1))
        assert forward.x < 0 and forward.y > 0 and forward.z < 0
        assert abs(math.degrees(math.asin(-forward.z)) - 35) < 1e-4
    else:
        assert key.data.type == 'SPOT' and key.data.shadow_soft_size <= .02
        assert 0 < key.data.spot_blend <= .00011, ('Hard cone must export with strictly smaller inner angle', slug)
        assert abs(math.degrees(key.data.spot_size) - 65) < 1e-4
        target = bpy.data.objects['TRG_ouxiang_xie_table' if slug == 'ouxiang-xie'
                                  else 'TRG_ziling_zhou_overlook'].location.copy()
        target.z = 1
        forward = key.rotation_euler.to_quaternion() @ Vector((0, 0, -1))
        assert forward.dot((target - key.location).normalized()) > .99
    print('OWNED_SITE_KEY_PASS', slug, key.data.type, key.data.energy, flush=True)
fill = bpy.data.objects['LGT_stage_green_key'].data
assert fill.color.g - (fill.color.r + fill.color.b) / 2 <= .01
assert fill.energy <= 1.4 + 1e-5
print('SITE_KEY_RIG_PASS: three owned hard keys; neutral shared fill', flush=True)
