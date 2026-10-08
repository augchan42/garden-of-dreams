# Scene changes before lighting adoption

Explicit `godot_cast_shadow` mesh metadata now transfers through Godot's
post-import hook and all three native Blender bake paths. Only meshes with a
boolean flag change; other meshes keep their settings. Future ordinary, wash
and spill records include the applied flags. The installed source has no flags,
and native inspection preserves all 558 imported mesh settings.

The actual ceiling export supplies the flagged mesh in isolated pixel tests.
Godot now imports it with shadows off and the existing cyclorama's unshaded
paint, identical color and shared texture. A forced double-sided shadow control
darkens the test floor; the imported setting matches the explicit off control.
The default one-sided caster did not shadow this particular lamp, so the test
does not claim that its previous Godot default darkened the whole garden.

Blender's actual imported ceiling initially casts shadows. The shared bake
helper restores its false flag and preserves 558 unflagged meshes. In the
scaled diagnostic fixture, floor linear luminance changes from 0.000019 to
0.763649; forced on/off controls reproduce that change. An independent sRGB
decode of the saved PNG agrees with the reported linear value. This proves
transfer and the isolated shadow effect, not complete garden GI or final paint.

The first Godot directional fixture lacked a useful shadow control. A later
run used a stale imported scene after the hook changed; a cold rebuild of only
the isolated GLB cache applies the hook and passes. The first Blender report
mislabelled encoded PNG luminance as linear; it is rejected and retained, and
the corrected test explicitly decodes sRGB. Raw reports, exact scripts,
controls and rejected versions remain under `reference/scene-adoption/`.

Native inspection of the earlier floor repair found coplanar rendering artifacts
at the pavilion overlaps. The revised candidate lifts all eight visible joints
and their matching colliders by 2 mm. Both pavilion views lose the observed
white overlap patterns; sixteen route/inspection-light captures show the
actual exported surfaces. Every centre ray reaches its intended joint collider.
The additional white lamp is explicitly diagnostic; its bright views are not
final lighting. Earlier obstructed cameras and the coplanar version are retained.

The revised export preserves all 4,344 existing source objects and materials,
all existing exported transforms/cameras/extras, and thirteen other site GLBs.
The strict actual physics walk passes fourteen rooms, twenty-six legs and
17,581 grounded ray samples without a miss. It uses public commands, one
visitor, no position resets, no substitute paths and no injected collision
shapes. Old bakes are disabled in the isolated fixture because geometry/UVs
have changed; this is not production traversal acceptance.

Both repairs are now composed in a separate saved Blender source and export
`33b20efadae58c5eb137eda3e21236211a5fb9a1047a1ba41d6338cb48fefbce`.
The ceiling adds one node to the verified floor candidate, with unchanged
existing transforms/cameras/extras. Both floor-site exports remain byte-identical
to that verified candidate, and twelve other site exports match canonical
bytes. The combined source has 233,552 render-only triangles; this is not a
measured visible-triangle or draw budget. Scratch pointers are
`/tmp/garden-floor-lift-authoring.json` and
`/tmp/garden-combined-floor-canopy.json`.

Canonical authoring/export, the installed GLB and previous local release remain
unchanged. The new code and unshaded material are prepared for adoption.
The wash pipeline still requires five receivers; extend its strict contracts
to the sixth ceiling receiver before using the combined source. The combined
import, continuous walk/render, final moon/paint contrast, genuinely fresh
lighting, production verification and package/device checks remain open.
Thirty missing references, final site art, performance and authenticated room
services remain part of the full active goal. Evidence is indexed by
`export/scene-adoption-evidence.json`.
