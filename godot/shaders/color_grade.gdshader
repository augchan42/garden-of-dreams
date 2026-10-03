shader_type canvas_item;
render_mode unshaded;
uniform sampler2D screen_texture : hint_screen_texture, repeat_disable, filter_nearest;
// LUT values are display-referred data, so no source_color conversion.
uniform sampler2D grade_atlas : repeat_disable, filter_linear;
uniform float grade_strength : hint_range(0.0, 1.0) = 1.0;
vec3 grade(vec3 color) {
 vec3 p=clamp(color,vec3(0.0),vec3(1.0))*31.0;
 float slice=floor(p.b);
 vec2 a=vec2((slice*32.0+p.r+0.5)/1024.0,(p.g+0.5)/32.0);
 vec2 b=vec2((min(slice+1.0,31.0)*32.0+p.r+0.5)/1024.0,a.y);
 return mix(texture(grade_atlas,a).rgb,texture(grade_atlas,b).rgb,fract(p.b));
}
void fragment() {
 vec3 source=texture(screen_texture,SCREEN_UV).rgb;
 COLOR=vec4(mix(source,grade(source),grade_strength),1.0);
}
