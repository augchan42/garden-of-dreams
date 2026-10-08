shader_type spatial;
render_mode cull_disabled;
uniform sampler2D wave_normal : hint_normal, repeat_enable, filter_linear_mipmap;
uniform sampler2D reflection_texture : source_color, filter_linear, repeat_disable;
uniform mat4 reflection_matrix;
uniform float reflection_strength = 0.78;
uniform float timeline_time = -1.0;
varying vec3 world_position;
void vertex() {
 world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
}
void fragment() {
 float t=timeline_time<0.0 ? TIME : timeline_time;
 vec2 uv=world_position.xz*.22;
 vec3 a=texture(wave_normal,uv+vec2(t*.015,t*.008)).rgb*2.0-1.0;
 vec3 b=texture(wave_normal,uv*1.7+vec2(-t*.011,t*.017)).rgb*2.0-1.0;
 vec2 ripple=(a.xy+b.xy)*.22;
 NORMAL=normalize(mat3(VIEW_MATRIX)*normalize(vec3(ripple.x,1.0,ripple.y)));
 vec4 projected=reflection_matrix*vec4(world_position,1.0);
 vec2 reflection_uv=projected.xy/max(projected.w,.0001)*.5+.5;
 reflection_uv.y=1.0-reflection_uv.y;
 reflection_uv+=ripple*.008;
 vec3 reflected=texture(reflection_texture,clamp(reflection_uv,vec2(.001),vec2(.999))).rgb;
 float inside=step(0.0,reflection_uv.x)*step(reflection_uv.x,1.0)*step(0.0,reflection_uv.y)*step(reflection_uv.y,1.0)*step(0.0,projected.w);
 ALBEDO=vec3(.009,.04,.018);
 EMISSION=reflected*vec3(.55,.9,.6)*reflection_strength*inside;
 METALLIC=.15;
 ROUGHNESS=.2;
 SPECULAR=.6;
}
