shader_type spatial;
render_mode ambient_light_disabled, cull_disabled;
uniform sampler2D lightmap : repeat_disable, filter_linear;
uniform float lightmap_scale = 1.0;
uniform vec4 base_color : source_color = vec4(0.15,0.24,0.12,1.0);
uniform float material_roughness = 0.35;
uniform float material_metallic = 0.0;
uniform vec4 material_emission : source_color = vec4(0.0,0.0,0.0,1.0);
uniform float emission_energy = 1.0;
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap;
uniform bool use_albedo_texture = false;
uniform sampler2D emission_texture : source_color, filter_linear_mipmap;
uniform bool use_emission_texture = false;
void fragment() {
 vec3 base=base_color.rgb;
 if(use_albedo_texture)base*=texture(albedo_texture,UV).rgb;
 vec3 emitted=material_emission.rgb*emission_energy;
 if(use_emission_texture)emitted*=texture(emission_texture,UV).rgb;
 ALBEDO = base;
 ROUGHNESS = material_roughness;
 METALLIC = material_metallic;
 EMISSION = base * texture(lightmap,UV2).rgb * lightmap_scale + emitted;
}
