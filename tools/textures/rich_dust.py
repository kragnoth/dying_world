"""dusts v2: Neo Vitae copper_dust as the template (its main ramp + accent speckles, 12 shades), each ramp filled by continuous
interpolation along the source texture's own colours, so every template shade stays a distinct colour"""
import json, sys, colorsys
from pathlib import Path
from PIL import Image
import numpy as np
D = Path(sys.argv[1]); OUT = Path(sys.argv[2])
rows = {r['id']: r for c, g in json.load(open(D.parent / 'report.json')).items() for r in g}
def frames(fid):
    a = np.array(Image.open(D / rows[fid]['file']).convert('RGBA')); w = a.shape[1]
    return [a[i:i + w] for i in range(0, a.shape[0], w)]
def lum(c): return c[..., 0] * .299 + c[..., 1] * .587 + c[..., 2] * .114
def hue(c):
    r, g, b = (c / 255.0); h, s, v = colorsys.rgb_to_hsv(r, g, b); return h, s
def split(cols, counts=None):
    """two colour groups by hue (primary = bigger); returns (primary, accent or None), each sorted dark->light"""
    if counts is None: counts = np.ones(len(cols))
    hs = np.array([hue(c) for c in cols]); sat = hs[:, 1]
    ang = hs[:, 0] * 2 * np.pi; pts = np.stack([np.cos(ang) * sat, np.sin(ang) * sat], 1)
    a, b = pts[np.argmin(pts[:, 0] + pts[:, 1])], pts[np.argmax(pts[:, 0] + pts[:, 1])]
    for _ in range(10):
        lab = np.linalg.norm(pts - a, axis=1) > np.linalg.norm(pts - b, axis=1)
        if lab.all() or (~lab).all(): break
        a, b = np.average(pts[~lab], 0, counts[~lab]), np.average(pts[lab], 0, counts[lab])
    if lab.all() or (~lab).all() or np.linalg.norm(a - b) < .12: return cols[np.argsort(lum(cols))], None
    g0, g1 = cols[~lab], cols[lab]; w0, w1 = counts[~lab].sum(), counts[lab].sum()
    if w1 > w0: g0, g1, w0, w1 = g1, g0, w1, w0
    if w1 / (w0 + w1) < .08: return cols[np.argsort(lum(cols))], None
    return g0[np.argsort(lum(g0))], g1[np.argsort(lum(g1))]
def ramp(src, q):
    """colour at quantile q (0 dark .. 1 light) by linear interpolation between the source's sorted colours"""
    x = np.linspace(0, 1, len(src)); return np.array([np.interp(q, x, src[:, k]) for k in range(3)])
def accent_from(primary, shift=.08):
    out = []
    for c in primary:
        h, s, v = colorsys.rgb_to_hsv(*(c / 255.0)); h = (h + shift) % 1; s = min(1, s * 1.25 + .05); v = v * .85
        out.append(np.array(colorsys.hsv_to_rgb(h, s, v)) * 255)
    return np.array(out)
tpl = frames("neovitae:copper_dust")[0]; top = tpl[..., 3] > 0
tcols, tcounts = np.unique(tpl[top][:, :3], axis=0, return_counts=True)
tprim, tacc = split(tcols.astype(float), tcounts.astype(float))
assert tacc is not None
# 9-40 per-dust fixes (user review of v2): trim = drop the darkest share of the source's colours (outline pixels);
# mono = speckles are a darker shade of the dust's own colour, not a second hue; contrast < 1 squeezes both ramps toward the middle
FIX = {"arkaneworx:zinc_dust": dict(trim=.25), "immersiveengineering:material_dust_wood": dict(mono=True),
       "immersiveengineering:material_dust_sulfur": dict(mono=True), "minecraft:glowstone_dust": dict(contrast=.75, mono=True)}
def restyle(fr, trim=0, mono=False, contrast=1.0):
    op = fr[..., 3] > 0; cols, cnt = np.unique(fr[op][:, :3], axis=0, return_counts=True)
    if trim:
        L = lum(cols.astype(float)); keep = L >= np.quantile(L, trim); cols, cnt = cols[keep], cnt[keep]
    sp, sa = split(cols.astype(float), cnt.astype(float))
    if mono: sp = cols[np.argsort(lum(cols.astype(float)))].astype(float); sa = None
    if len(sp) < 2: sp = np.array([sp[0] * .6, sp[0], np.minimum(255, sp[0] * 1.3)])
    if sa is None or len(sa) < 2: sa = accent_from(sp, 0 if mono else .08)
    t = tpl.copy()
    for grp, src in ((tprim, sp), (tacc, sa)):
        for i, c in enumerate(grp):
            q = i / max(1, len(grp) - 1); q = .5 + (q - .5) * contrast; sel = top & np.all(tpl[..., :3] == c.astype(np.uint8), axis=-1)
            t[sel, :3] = np.clip(np.round(ramp(src, q)), 0, 255).astype(np.uint8)
    return t
done = [d for d in json.load(open(OUT.parent / 'restyled.json')) if d[0] == 'dust' and not d[1].startswith('cultivar:')]
for _, fid, _ in done:
    out = np.concatenate([restyle(fr, **FIX.get(fid, {})) for fr in frames(fid)], 0)
    ns, path = fid.split(':', 1); Image.fromarray(out, 'RGBA').save(OUT / ns / 'textures/item' / f'{path}.png')
    print(fid, len({tuple(x) for x in out[out[..., 3] > 0][:, :3]}))
