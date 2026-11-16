#!/usr/bin/env python3
"""pass 9-48: 16x16 Excalibur-ish textures for the Escapement chain items (kubejs/assets/gearwrights/textures/item/)."""
import math, random
from pathlib import Path
from PIL import Image
OUT = Path(__file__).resolve().parents[2] / "modpack/overrides/kubejs/assets/gearwrights/textures/item"
OUTLINE = (34, 22, 16, 255)

def ramp(c, k):  # k in [-1,1]
    return tuple(max(0, min(255, int(v * (1 + .45 * k)))) for v in c) + (255,)

def pile(base, motes, seed):
    r = random.Random(seed); im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); px = im.load()
    for y in range(6, 15):
        w = int(7 * math.sin((y - 5) / 10 * math.pi) + (y - 6) * .5)
        for x in range(8 - w, 8 + w):
            if 0 <= x < 16:
                k = -.6 + (y - 6) / 9 * .4 - (x - 8) / 16 + r.uniform(-.25, .25)
                px[x, y] = ramp(base, -k)
    for _ in range(9):
        x, y = r.randint(3, 12), r.randint(8, 13)
        if px[x, y][3]: px[x, y] = motes[r.randrange(len(motes))]
    outline(im); return im

def gear(body, accent, seed, spring=None, center=None):
    r = random.Random(seed); im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); px = im.load()
    cx = cy = 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy); a = math.atan2(y - cy, x - cx)
            tooth = (math.cos(a * 8) > .35)
            if d <= 4.6 or (d <= 6.4 and tooth):
                if d < 1.6: px[x, y] = center or ramp(accent, .3)
                elif 2.6 < d < 3.4: px[x, y] = ramp(body, -.5)
                else: px[x, y] = ramp(body, -(x + y - 15) / 18 + r.uniform(-.08, .08))
    if spring:
        for i in range(10):
            a = i * .9; d = 1.5 + i * .5
            x, y = int(round(cx + 5 + math.cos(a) * d * .5)), int(round(cy + 5 + math.sin(a) * d * .5))
            if 0 <= x < 16 and 0 <= y < 16: px[x, y] = spring
    outline(im); return im

def outline(im):
    px = im.load(); src = im.copy().load()
    for y in range(16):
        for x in range(16):
            if src[x, y][3]: continue
            if any(0 <= x + dx < 16 and 0 <= y + dy < 16 and src[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = OUTLINE

def escapement():
    im = gear((150, 104, 44), (120, 214, 180), 6, center=(170, 255, 220, 255)); px = im.load()
    for x, y in ((3, 2), (4, 3), (12, 2), (11, 3), (5, 4), (10, 4)): px[x, y] = (200, 160, 80, 255)   # the anchor's arms
    for x, y in ((7, 1), (8, 1)): px[x, y] = (230, 196, 110, 255)
    return im

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    teal = [(110, 220, 180, 255), (70, 170, 140, 255), (200, 255, 230, 255)]
    pile((58, 54, 52), teal, 1).save(OUT / "foundry_residue.png")
    pile((40, 92, 84), [(220, 255, 240, 255), (150, 240, 210, 255)], 2).save(OUT / "distilled_residue.png")
    gear((120, 112, 104), (90, 90, 90), 3).save(OUT / "incomplete_movement.png")
    gear((176, 128, 54), (110, 80, 40), 4, spring=(220, 200, 150, 255)).save(OUT / "unwound_movement.png")
    gear((150, 60, 52), (200, 40, 40), 5, spring=(240, 90, 90, 255)).save(OUT / "bled_movement.png")
    gear((74, 52, 92), (60, 140, 120), 7, spring=(140, 230, 200, 255), center=(20, 20, 30, 255)).save(OUT / "wound_movement.png")
    escapement().save(OUT / "escapement.png")
    print("9-48 textures:", sorted(p.name for p in OUT.glob("*.png") if p.stem in
          ("foundry_residue", "distilled_residue", "incomplete_movement", "unwound_movement", "bled_movement", "wound_movement", "escapement")))

if __name__ == "__main__":
    main()
