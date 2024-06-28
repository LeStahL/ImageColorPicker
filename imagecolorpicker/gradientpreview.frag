#version 450

uniform vec2 iResolution;

out vec4 oColor;

{%- for (weight, mix, cmap) in colorMaps %}
vec3 cmap_{{ weight.name }}{{ mix.name }}(float t) {
    {%- for color in cmap %}
    const vec3 c{{ loop.index - 1 }} = vec3({{ color.x }}, {{ color.y }}, {{ color.z }});
    {%- endfor %}

    return c0
    {%- for color in cmap[1:] %}
        +t*(c{{ loop.index }}
    {%- endfor %}
    {%- for color in cmap[1:] -%}
        )
    {%- endfor -%}
    ;
}
{%- endfor %}

void main() {
    oColor = vec4(0,0,0,1);
    vec2 uv = gl_FragCoord.xy / iResolution;

    {%- for (weight, mix, cmap) in colorMaps %}
    if(uv.y > {{ (loop.index - 1) / (loop.length) }})
        oColor = vec4(cmap_{{ weight.name }}{{ mix.name }}(uv.x), 1.);
    {%- endfor %}

    float dy = 1. / float({{ colorMaps.__len__() }});
    oColor.rgb = mix(oColor.rgb, vec3(0.94, 0.94, 0.94), smoothstep(.5/iResolution.y, -.5/iResolution.y, abs(mod(uv.y + .5 * dy, dy) - .5 * dy) - .0065));
}
