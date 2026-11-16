import json, sys
from pathlib import Path
from PIL import Image
import numpy as np
D = Path(sys.argv[1]); rows = json.load(open(D / 'index.json'))
def mask(fn):
    im = Image.open(D / fn).convert('RGBA'); w, h = im.size
    if h > w: im = im.crop((0, 0, w, w)); h = w            # animated strip -> first frame
    a = np.array(im)[:, :, 3] > 0
    if w != 16:
        f = w // 16
        a = a[:16 * f, :16 * f].reshape(16, f, 16, f).any(axis=(1, 3)) if f >= 1 else a
    return a, w
for r in rows:
    m, w = mask(r['file']); r['res'] = w; r['m'] = m
    ys, xs = np.nonzero(m)
    r['area'] = int(m.sum())
    r['bbox'] = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else (0, 0, 0, 0)
    r['bw'] = r['bbox'][2] - r['bbox'][0] + 1 if len(xs) else 0; r['bh'] = r['bbox'][3] - r['bbox'][1] + 1 if len(xs) else 0
out = {}
for c in ('ingot', 'nugget', 'dust'):
    g = [r for r in rows if r['cat'] == c]
    cons = np.mean([r['m'] for r in g], axis=0) >= .5
    areas = np.array([r['area'] for r in g]); med = float(np.median(areas))
    for r in g:
        inter = (r['m'] & cons).sum(); uni = (r['m'] | cons).sum()
        r['iou'] = round(float(inter / uni) if uni else 0, 2); r['area_ratio'] = round(r['area'] / med, 2)
    ious = np.array([r['iou'] for r in g]); q1 = np.percentile(ious, 25)
    print(f"== {c}: {len(g)} textures, median area {med:.0f}px, consensus {int(cons.sum())}px, median IoU {np.median(ious):.2f}")
    for r in sorted(g, key=lambda r: r['iou']):
        flag = []
        if r['iou'] < .45: flag.append('shape')
        if r['area_ratio'] > 1.6: flag.append('too big')
        if r['area_ratio'] < .55: flag.append('too small')
        if r['res'] != 16: flag.append(f"{r['res']}px")
        r['flag'] = flag
        if flag: print(f"  {r['id']:55s} iou {r['iou']:.2f} area x{r['area_ratio']:.2f} bbox {r['bw']}x{r['bh']} res {r['res']} [{', '.join(flag)}]  <- {r['src']}")
    out[c] = [{k: v for k, v in r.items() if k != 'm'} for r in g]
    # contact sheet sorted by IoU
    S = 64; cols = 10; rowsn = (len(g) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * (S + 8), rowsn * (S + 8)), (60, 60, 60, 255))
    for i, r in enumerate(sorted(g, key=lambda r: r['iou'])):
        im = Image.open(D / r['file']).convert('RGBA'); w, h = im.size
        if h > w: im = im.crop((0, 0, w, w))
        im = im.resize((S, S), Image.NEAREST); x, y = (i % cols) * (S + 8) + 4, (i // cols) * (S + 8) + 4
        if r['flag']:
            from PIL import ImageDraw; ImageDraw.Draw(sheet).rectangle([x - 3, y - 3, x + S + 2, y + S + 2], outline=(220, 60, 60, 255), width=3)
        sheet.alpha_composite(im, (x, y))
    sheet.save(D.parent / f'sheet_{c}.png')
json.dump(out, open(D.parent / 'report.json', 'w'), indent=1, default=str)
