import json, sys, zipfile
from pathlib import Path
from PIL import Image
import numpy as np
D = Path(sys.argv[1]); OUT = Path(sys.argv[2])
rows = {r['id']: r for c, g in json.load(open(D.parent / 'report.json')).items() for r in g}
def load(fid):
    im = Image.open(D / rows[fid]['file']).convert('RGBA'); a = np.array(im); w = a.shape[1]
    return [a[i:i + w] for i in range(0, a.shape[0], w)]          # frames
def lum(px): return px[..., 0] * .299 + px[..., 1] * .587 + px[..., 2] * .114
def palette(fr):
    op = fr[..., 3] > 0
    inner = op.copy(); inner[1:-1, 1:-1] = op[1:-1, 1:-1] & op[:-2, 1:-1] & op[2:, 1:-1] & op[1:-1, :-2] & op[1:-1, 2:]
    inner[0, :] = inner[-1, :] = inner[:, 0] = inner[:, -1] = False
    m = inner if inner.sum() >= 20 else op
    cols = fr[m][:, :3].astype(float); return cols[np.argsort(lum(cols))]
def recolor(tpl, fr, lift=0):
    t = tpl.copy(); op = t[..., 3] > 0; L = lum(t[..., :3].astype(float))
    lv = np.sort(np.unique(L[op])); pal = palette(fr)
    for v in lv:
        q = np.searchsorted(lv, v) / max(1, len(lv) - 1)           # rank of this shade in the template
        q = min(1, max(0, q * (1 - lift) + lift))
        c = pal[min(len(pal) - 1, int(round(q * (len(pal) - 1))))]
        sel = op & (L == v); t[sel, :3] = c.astype(np.uint8)
    return t
TPL = {"ingot": "minecraft:iron_ingot", "nugget": "minecraft:iron_nugget", "dust": "neovitae:iron_dust"}
SKIP_NS = ("titanium",)
KEEP = {"ingot": lambda r: r['bw'] == 12 and r['bh'] == 13,          # already Excalibur-shaped
        "nugget": lambda r: (r['bw'], r['bh']) in ((9, 7), (8, 7)) or 'experience' in r['id'],
        "dust": lambda r: r['id'].startswith('neovitae:') and r['id'] != 'neovitae:corrupted_dust'}
EXTRA_SKIP = {"create:copper_ingot"}                                   # texture ships in Create's jar but no such item exists
done = []
for fid, r in sorted(rows.items()):
    c = r['cat']
    if fid.split(':')[0] in SKIP_NS or fid in EXTRA_SKIP or KEEP[c](r): continue
    tpl = load(TPL[c])[0]
    frames = [recolor(tpl, fr) for fr in load(fid)]
    out = np.concatenate(frames, axis=0)
    ns, path = fid.split(':', 1); p = OUT / ns / 'textures/item' / f'{path}.png'; p.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out, 'RGBA').save(p); done.append((c, fid, len(frames)))
for c in ("ingot", "nugget", "dust"): print(c, [f for k, f, _ in done if k == c])
json.dump(done, open(OUT.parent / 'restyled.json', 'w'))
