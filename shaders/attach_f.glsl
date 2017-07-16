#version 140

struct p3d_LightSourceParameters {
    vec4 position;
    vec4 diffuse;
    vec3 attenuation;
    vec3 spotDirection;
    float spotCosCutoff;
    float spotExponent;
    };

in vec2 texcoord;
in vec3 T;
in vec3 B;
in vec3 N;
in vec3 vpos;

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1; //normal+gloss

uniform p3d_LightSourceParameters spot;

out vec4 final_color;

void main()
    {
    final_color=vec4(0.22, 0.22, 0.25, 1.0);

    vec4 albedo=texture(p3d_Texture0, texcoord);
    vec4 normal_map=texture(p3d_Texture1,texcoord);
    float gloss=normal_map.a;
    vec3 norm=normalize(N);
    vec3 normal=normal_map.xyz*2.0-1.0;
    norm*=normal.z;
    norm+=T*normal.x;
    norm+=B*normal.y;
    norm=normalize(norm);

    vec3 diff = spot.position.xyz - vpos * spot.position.w;
    vec3 L = normalize(diff);
    vec3 E = normalize(-vpos);
    vec3 R = normalize(-reflect(L, norm));
    vec4 diffuse = clamp(albedo * spot.diffuse * max(dot(norm, L), 0), 0, 1);
    vec4 specular = spot.diffuse * pow(max(dot(R, E), 0), 200.0)*gloss;

    float spotEffect = dot(normalize(spot.spotDirection), -L);

    if (spotEffect >spot.spotCosCutoff)
        {
        diffuse *= pow(spotEffect, spot.spotExponent);
        final_color += diffuse / dot(spot.attenuation, vec3(1, length(diff), length(diff) * length(diff)));
        final_color+=specular;
        }

    final_color.a = albedo.a;
    }
