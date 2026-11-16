#version 150

// Thermal Print: every pixel becomes exactly PaperWhite, InkRed or InkBlack.
// Mode 1 (default) is the Land two-record method further down; the numbered steps below are Mode 0.
//
// The eye still "sees" colour because of memory colour (grass is green, sky is blue), simultaneous
// contrast (black next to red reads cool, white next to red reads cyan-ish) and Land/retinex
// constancy. All we have to do is put the right ink in the right places:
//   1. Luminance from a green/blue-weighted mix, so red objects don't wash out to paper.
//   2. Contrast/gamma curve (red ink is light, so the tone curve compensates).
//   3. Ordered Bayer dither, stage 1: luminance vs threshold -> ink or paper.
//   4. Stage 2 for inked pixels: warmth vs an offset threshold -> red or black. Warm mid-tones mix
//      red and black dots (maroon/brown); cool mid-tones mix black and paper (grey).
// Two modes: Land two-record (default, below) and the classic warmth split. One pass, 5 texture
// samples, no loops, no buffers, no error diffusion. Screen-space dither ->
// stable frame to frame, no shimmer.

uniform sampler2D DiffuseSampler;
uniform vec2 OutSize;

uniform float Enabled;
uniform vec3  PaperWhite;
uniform vec3  InkRed;
uniform vec3  InkBlack;
uniform vec3  LumaWeights;
uniform float Contrast;
uniform float Gamma;
uniform float Brightness;
uniform float WarmStrength;
uniform float SkinStrength;
uniform float RedLightness;   // how far into the light tones red ink is still used (red ink is light)
uniform float BayerSize;      // 4 or 8
uniform float DotScale;       // >= 1: dot size in screen pixels
uniform float Sharpen;        // local-contrast boost before dithering (0 = off; 4 extra taps)
uniform float Mode;           // 1 = Land two-record (default), 0 = classic warmth split
uniform float Chroma;         // Land mode: how far the long-wave (red) record departs from the short-wave one
uniform float Surround;       // Land mode: retinex surround - push each pixel's red/white balance away from its neighbourhood

in vec2 texCoord;
out vec4 fragColor;

// Ordered dither by bit interleaving (no table, no texture). Returns 0..1 thresholds.
float bayer4(ivec2 p) {
    p &= 3;
    int xy = p.x ^ p.y;
    int v = ((xy & 1) << 3) | ((p.x & 1) << 2) | (xy & 2) | ((p.x & 2) >> 1);
    return (float(v) + 0.5) / 16.0;
}

float bayer8(ivec2 p) {
    p &= 7;
    int xy = p.x ^ p.y;
    int v = ((xy & 1) << 5) | ((p.x & 1) << 4) | ((xy & 2) << 2) | ((p.x & 2) << 1) | ((xy & 4) >> 1) | ((p.x & 4) >> 2);
    return (float(v) + 0.5) / 64.0;
}

float bayer(ivec2 p) {
    return mix(bayer4(p), bayer8(p), step(6.0, BayerSize));   // branchless 4x4 / 8x8 select
}

void main() {
    float ds = max(1.0, floor(DotScale + 0.5));
    vec2 cell = floor(gl_FragCoord.xy / ds);
    // sample the source at the dot's centre so a whole dot shares one decision
    vec2 uv = (cell * ds + 0.5 * ds) / OutSize;
    vec3 c = texture(DiffuseSampler, uv).rgb;

    // 1-2. green/blue-weighted luminance (+ optional unsharp mask: badge prints live on edges) + tone curve
    vec3 lw = LumaWeights / max(1e-4, dot(LumaWeights, vec3(1.0)));
    float lum = dot(c, lw);
    vec2 o = ds * 1.5 / OutSize;
    vec3 avg = 0.25 * (texture(DiffuseSampler, uv + vec2(o.x, 0.0)).rgb + texture(DiffuseSampler, uv - vec2(o.x, 0.0)).rgb
                     + texture(DiffuseSampler, uv + vec2(0.0, o.y)).rgb + texture(DiffuseSampler, uv - vec2(0.0, o.y)).rgb);
    float around = dot(avg, lw);
    lum += (lum - around) * Sharpen;
    lum = clamp((lum - 0.5) * Contrast + 0.5 + Brightness, 0.0, 1.0);
    lum = pow(lum, Gamma);

    // warmth: red dominance + a skin/orange term (r > g > b), gated by saturation
    float hi = max(c.r, max(c.g, c.b));
    float lo = min(c.r, min(c.g, c.b));
    float sat = (hi - lo) / max(hi, 1e-4);
    float redDom = clamp((c.r - max(c.g, c.b)) * WarmStrength, 0.0, 1.0);
    float skin = clamp(min(c.r - c.g, c.g - c.b) * SkinStrength, 0.0, 1.0);
    float warm = clamp(redDom + skin, 0.0, 1.0) * smoothstep(0.08, 0.35, sat);

    // 3. stage 1: ink or paper. Warm areas print a bit lighter as red (red ink reads light), so
    //    shift the threshold so warm light tones still get (red) ink instead of going to paper.
    ivec2 p = ivec2(cell);
    float t1 = bayer(p);
    float inkLum = mix(lum, lum - RedLightness * (1.0 - lum), warm);
    float ink = step(inkLum, t1);                              // 1 = put ink here

    // 4. stage 2: red or black, offset dither so it doesn't lock to the same dot pattern.
    //    Dark warm tones lean black (maroon = red + black dots), light warm tones are pure red.
    float t2 = bayer(p + ivec2(2, 1) * int(1.0 + step(6.0, BayerSize)));
    float redness = warm * clamp(0.35 + lum * 1.3, 0.0, 1.0);
    float red = step(t2, redness);

    vec3 inked = mix(InkBlack, InkRed, red);
    vec3 classic = mix(PaperWhite, inked, ink);

    // ---- Land two-record mode ---------------------------------------------------------------
    // Edwin Land: a red-filter record projected in RED light + a green-filter record in WHITE light
    // reads as (nearly) full colour - the brain judges colour from long/short-wave RATIOS across the
    // scene, not per point. Our inks are that setup: paper = white light, red ink = red light,
    // black = no light. Per pixel, solve for the paper/red/black mix that reproduces the long-wave
    // (red) and short-wave (green/blue) brightness with the ACTUAL ink colours, then dither the three
    // with one ordered threshold. Retinex surround: each record is pushed away from its neighbourhood
    // average, which strengthens the colour edges the brain fills colour in from.
    float Lw = c.r;                                  // long-wave record
    float Sw = dot(c, vec3(0.0, 0.7, 0.3));          // short-wave record (green + some blue)
    float aL = avg.r, aS = dot(avg, vec3(0.0, 0.7, 0.3));
    Lw += (Lw - aL) * Sharpen;  Sw += (Sw - aS) * Sharpen;              // shared edge boost
    float dLS = (Lw - Sw) - (aL - aS) * Surround;                      // chroma vs. its surround
    float mid = 0.5 * (Lw + Sw);
    Lw = mid + 0.5 * dLS * Chroma;
    Sw = mid - 0.5 * dLS * Chroma;
    // the same tone curve as the classic mode, per record
    Lw = pow(clamp((Lw - 0.5) * Contrast + 0.5 + Brightness, 0.0, 1.0), Gamma);
    Sw = pow(clamp((Sw - 0.5) * Contrast + 0.5 + Brightness, 0.0, 1.0), Gamma);
    // solve  Lw = B.r + p (W.r-B.r) + r (R.r-B.r),  Sw = B.g + p (W.g-B.g) + r (R.g-B.g)  for p (paper), r (red)
    float a11 = PaperWhite.r - InkBlack.r, a12 = InkRed.r - InkBlack.r;
    float a21 = PaperWhite.g - InkBlack.g, a22 = InkRed.g - InkBlack.g;
    float y1 = Lw - InkBlack.r, y2 = Sw - InkBlack.g;
    float det = a11 * a22 - a12 * a21;
    float pp = (y1 * a22 - a12 * y2) / det;
    float rr = (a11 * y2 - a21 * y1) / det;
    // outside the paper/red/black triangle: least-squares onto the nearest edge instead of clipping
    // (cool colours -> paper/black edge, deep reds -> red/black edge)
    float ppPB = clamp((y1 * a11 + y2 * a21) / (a11 * a11 + a21 * a21), 0.0, 1.0);
    float rrRB = clamp((y1 * a12 + y2 * a22) / (a12 * a12 + a22 * a22), 0.0, 1.0);
    pp = mix(pp, ppPB, step(rr, 0.0));  rr = max(rr, 0.0);
    rr = mix(rr, rrRB, step(pp, 0.0));  pp = max(pp, 0.0);
    float tot = pp + rr;
    pp /= max(tot, 1.0);  rr /= max(tot, 1.0);       // over-bright -> scale back onto paper/red edge
    float t = bayer(p);
    float isW = step(t, pp);                          // threshold below paper share -> paper
    float isR = step(t, pp + rr) - isW;               // next band -> red ink
    vec3 land = PaperWhite * isW + InkRed * isR + InkBlack * (1.0 - isW - isR);

    vec3 outc = mix(classic, land, step(0.5, Mode));
    fragColor = vec4(mix(texture(DiffuseSampler, texCoord).rgb, outc, step(0.5, Enabled)), 1.0);
}
