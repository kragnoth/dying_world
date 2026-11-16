#version 150

// "Soot & Tar" haze - a light touch: the world is polluted, not dead.
//  - colour gently muted (warm light keeps full colour), a faint umber cast
//  - no crushed blacks; a soft brown vignette and barely-there film grain

uniform sampler2D DiffuseSampler;
uniform vec2 InSize;
uniform float Time;
uniform float Strength;
uniform float Grain;

in vec2 texCoord;
out vec4 fragColor;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec3 c = texture(DiffuseSampler, texCoord).rgb;
    float l = dot(c, vec3(0.299, 0.587, 0.114));

    float warm = clamp((c.r - c.b) * 2.5, 0.0, 1.0) * smoothstep(0.35, 0.85, l);
    vec3 g = mix(vec3(l), c, 0.82 + 0.18 * warm);                 // gently muted
    g = mix(g, vec3(l * 1.05, l * 0.98, l * 0.86), 0.12);         // faint umber haze

    float n = hash(floor(texCoord * InSize) + vec2(floor(Time * 24.0) * 17.0, floor(Time * 24.0) * 31.0)) - 0.5;
    g += n * Grain;

    vec2 d = texCoord - 0.5;
    float v = smoothstep(0.35, 0.95, length(d) * 1.3);
    g = mix(g, g * vec3(0.80, 0.76, 0.70), v * 0.5);              // soft vignette

    fragColor = vec4(clamp(mix(c, g, Strength), 0.0, 1.0), 1.0);
}
