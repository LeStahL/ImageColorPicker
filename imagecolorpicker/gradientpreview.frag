#version 450

uniform vec2 iResolution;

out vec4 oColor;

{%- for (weight, mix, cmap) in colorMaps %}
vec3 cmap_{{ weight.name }}{{ mix.name }}(float t) {
    {%- for color in cmap %}
    const vec3 c{{ loop.index - 1 }} = {{ color }};
    {%- endfor %}

    return c0+t*(c1+t*(c2+t*(c3+t*(c4+t*(c5+t*c6)))));
}
{%- endfor %}

void main() {
    oColor = vec4(0,0,0,1);
    vec2 uv = gl_FragCoord.xy / iResolution;

    {%- for (weight, mix, cmap) in colorMaps %}
    if(uv.y > {{ (loop.index - 1) / (loop.length) }})
        oColor = vec4(cmap_{{ weight.name }}{{ mix.name }}(uv.x), 1.);
    {%- endfor %}
}
