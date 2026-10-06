shader_type spatial;
render_mode ambient_light_disabled, cull_disabled;
uniform sampler2D lightmap : repeat_disable, filter_linear;
uniform float lightmap_scale = 1.0;
uniform bool use_lightmap = true;
uniform bool source_unshaded = false;
uniform sampler2D backdrop_wash : repeat_disable, filter_linear;
uniform float backdrop_wash_scale = 1.0;
uniform sampler2D backdrop_wash_back : repeat_disable, filter_linear;
uniform float backdrop_wash_back_scale = 1.0;
uniform bool backdrop_wash_double_sided = false;
uniform bool use_backdrop_wash = false;
uniform vec4 base_color : source_color = vec4(0.15,0.24,0.12,1.0);
uniform float material_roughness = 0.35;
uniform float material_metallic = 0.0;
uniform vec4 material_emission : source_color = vec4(0.0,0.0,0.0,1.0);
uniform float emission_energy = 1.0;
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap;
uniform bool use_albedo_texture = false;
uniform sampler2D emission_texture : source_color, filter_linear_mipmap;
uniform bool use_emission_texture = false;
uniform bool emission_add = false;
uniform sampler2D orm_texture : filter_linear_mipmap;
uniform bool use_orm_texture = false;
uniform sampler2D normal_texture : hint_normal, filter_linear_mipmap;
uniform bool use_normal_texture = false;
uniform float normal_scale = 1.0;
void fragment() {
 vec3 base=base_color.rgb;
 if(use_albedo_texture)base*=texture(albedo_texture,UV).rgb;
 vec3 emitted=material_emission.rgb*emission_energy;
 if(use_emission_texture){
  vec3 emission_sample=texture(emission_texture,UV).rgb;
  if(emission_add)emitted+=emission_sample*emission_energy;
  else emitted*=emission_sample;
 }
 ALBEDO = source_unshaded ? vec3(0.0) : base;
 ROUGHNESS = material_roughness;
 METALLIC = material_metallic;
 if(use_normal_texture){
  NORMAL_MAP = texture(normal_texture,UV).rgb;
  NORMAL_MAP_DEPTH = normal_scale;
 }
 // Occlusion is already included in the Cycles bake; do not apply it twice.
 if(use_orm_texture){
  vec3 orm=texture(orm_texture,UV).rgb;
  ROUGHNESS *= orm.g;
  METALLIC *= orm.b;
 }
 // Cycles diffuse bakes include Lambert's 1/pi. Compatibility's unit-light
 // diffuse response omits it; match that response without scaling emission.
 vec3 baked = vec3(0.0);
 if(use_lightmap)baked += texture(lightmap,UV2).rgb * lightmap_scale;
 if(use_backdrop_wash){
  if(backdrop_wash_double_sided && !FRONT_FACING)
   baked += texture(backdrop_wash_back,UV2).rgb * backdrop_wash_back_scale;
  else baked += texture(backdrop_wash,UV2).rgb * backdrop_wash_scale;
 }
 EMISSION = base * baked * PI + emitted + (source_unshaded ? base : vec3(0.0));
}
