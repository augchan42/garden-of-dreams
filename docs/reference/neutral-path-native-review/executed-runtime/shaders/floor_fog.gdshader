shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;
uniform sampler2D fog_mask : repeat_enable, filter_linear;
uniform vec4 fog_color : source_color = vec4(0.18,0.42,0.19,1.0);
uniform float phase_offset = 0.0;
// Negative uses the runtime clock; nonnegative allows deterministic captures.
uniform float timeline_time = -1.0;
void fragment() {
 float t = (timeline_time < 0.0 ? TIME : timeline_time) + phase_offset;
 float a = texture(fog_mask,UV+vec2(t*0.008,t*0.003)).a;
 float b = texture(fog_mask,UV*1.7+vec2(-t*0.005,t*0.004)).a;
 vec2 edge = smoothstep(vec2(0.0),vec2(0.12),UV)*smoothstep(vec2(0.0),vec2(0.12),vec2(1.0)-UV);
 ALBEDO = fog_color.rgb;
 ALPHA = (a+b)*0.7*edge.x*edge.y;
}
