"""Test-only capture correction; no game runtime or source changes."""


def transform(text):
    replacements = [
        ('var density := false\n', 'var density := false\nvar last_lod_settle_ms := 0\n'),
        (' # Subscribe before forcing a frame so a synchronous completion cannot be missed.\n',
         ' # Wait through the real timed FloraLOD update after the camera stops.\n'
         ' var lod_start := Time.get_ticks_msec()\n'
         ' await create_timer(0.25, true, false, true).timeout\n'
         ' while Time.get_ticks_msec() - lod_start < 250:await process_frame\n'
         ' await process_frame\n'
         ' last_lod_settle_ms = Time.get_ticks_msec() - lod_start\n'
         ' check(last_lod_settle_ms >= 250, "Timed foliage settle ended early")\n'
         ' # Subscribe before forcing a frame so a synchronous completion cannot be missed.\n'),
        ('func inspect(phase: String,portrait: bool) -> void:\n',
         'func reed_lod_state() -> Array:\n'
         ' var state: Array = []\n'
         ' for plant in route.get_node("FloraLOD").plants:\n'
         '  if not str(plant.node.name).begins_with("HERO_flora_ziling"):continue\n'
         '  var distance: float = route.camera.global_position.distance_to(plant.node.global_position)\n'
         '  check(plant.node.mesh == (plant.lower if plant.is_lower else plant.base), "Reed mesh/state mismatch")\n'
         '  if distance > plant.distance + 2.0:check(plant.is_lower, "Distant reed LOD not settled")\n'
         '  elif distance < plant.distance - 2.0:check(not plant.is_lower, "Near reed LOD not settled")\n'
         '  state.append({"name":str(plant.node.name),"is_lower":plant.is_lower,"camera_distance":distance,"lod_distance":plant.distance})\n'
         ' check(not state.is_empty(), "Missing captured reed LOD state")\n'
         ' return state\n\n'
         'func inspect(phase: String,portrait: bool) -> void:\n'),
        ('"camera_transition_running":false,"text":route.output_label.text',
         '"camera_transition_running":false,"lod_settle_ms":last_lod_settle_ms,"reed_lod_state":reed_lod_state(),"text":route.output_label.text'),
        ('"touch":touch,"density":density,"subject_vertex_counts":counts',
         '"touch":touch,"density":density,"lod_settle_seconds":0.25,"subject_vertex_counts":counts'),
        ('with completed tweens, all imported',
         'with completed tweens and a real0.25-second foliage wait plus measured capture LOD state, all imported'),
    ]
    for old, new in replacements:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    return text
