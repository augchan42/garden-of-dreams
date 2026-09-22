shader_type spatial;
render_mode cull_disabled;
uniform sampler2D wave_normal : hint_normal, repeat_enable, filter_linear_mipmap;
uniform vec4 water_color : source_color = vec4(0.018,0.10,0.046,1.0);
uniform float phase_offset = 0.0;
// Negative uses the runtime clock; nonnegative allows deterministic captures.
uniform float timeline_time = -1.0;
varying vec3 world_position;
void vertex() {
 world_position = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz;
}
void fragment() {
 float t = (timeline_time < 0.0 ? TIME : timeline_time) + phase_offset;
 vec2 uv = world_position.xz * 0.22;
 vec3 a = texture(wave_normal,uv + vec2(t*0.015,t*0.008)).rgb * 2.0 - 1.0;
 vec3 b = texture(wave_normal,uv*1.7 + vec2(-t*0.011,t*0.017)).rgb * 2.0 - 1.0;
 vec2 ripple = (a.xy+b.xy)*0.22;
 vec3 world_normal = normalize(vec3(ripple.x,1.0,ripple.y));
 NORMAL = normalize(mat3(VIEW_MATRIX)*world_normal);
 ALBEDO = water_color.rgb;
 METALLIC = 0.25;
 ROUGHNESS = 0.19;
 SPECULAR = 0.7;
}
