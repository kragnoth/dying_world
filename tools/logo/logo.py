"""Gearwright's Hollow logo: Create's large water wheel + a votive skull, rendered from the real models/textures,
over a blurred Occult Foundry haze, with a stone pixel title (style of the Skill Perks logo). usage: python3 logo.py out.png"""
import math, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/claude/tex')
from render import Scene, load_tex, rot_x, rot_y

V = '/home/claude/tex/v/assets/minecraft/textures/'
CR = '/home/claude/tex/c/assets/create/textures/block/'
OBJ = '/home/claude/tex/c/assets/create/models/block/large_water_wheel/waterwheel_large.obj'
W = H = 1024
rnd = random.Random(5)
FOG = (92, 98, 112)                # occult_foundry fog #5c6270
SOUL = (98, 200, 196)

# ------------------------------------------------------------------ backdrop: blurred foundry haze
bg = Image.new('RGB', (W, H))
px = bg.load()
for y in range(H):
    t = y / H
    top, mid, low = np.array((24, 27, 34)), np.array(FOG), np.array((40, 44, 54))
    c = top + (mid - top) * min(1, t / 0.62) if t < 0.62 else mid + (low - mid) * ((t - 0.62) / 0.38)
    for x in range(W):
        px[x, y] = tuple(int(v) for v in c)
d = ImageDraw.Draw(bg, 'RGBA')
# far pines and foundry stacks, two depth layers
for layer, (base, col, hmin, hmax) in enumerate(((650, (52, 57, 68, 255), 120, 260), (700, (36, 40, 49, 255), 160, 330))):
    x = -40
    while x < W + 40:
        if rnd.random() < 0.18:                  # chimney
            w = rnd.randint(26, 44); top = base - rnd.randint(hmax, hmax + 120)
            d.rectangle((x, top, x + w, H), fill=col)
            d.rectangle((x - 4, top, x + w + 4, top + 14), fill=col)
            for k in range(6):                   # smoke
                d.ellipse((x - 20 + k * 22, top - 60 - k * 38, x + 60 + k * 30, top - 10 - k * 34), fill=col[:3] + (60,))
            x += w + rnd.randint(30, 90)
        else:                                    # pine
            hgt = rnd.randint(hmin, hmax); w = hgt * 0.42
            for tier in range(4):
                ty = base - hgt + tier * hgt * 0.22
                d.polygon(((x, ty), (x - w * (0.35 + tier * 0.17), ty + hgt * 0.34), (x + w * (0.35 + tier * 0.17), ty + hgt * 0.34)), fill=col)
            d.rectangle((x - 5, base - hgt * 0.2, x + 5, H), fill=col)
            x += rnd.randint(40, 110)
d.rectangle((0, 740, W, H), fill=(30, 33, 41, 255))
bg = bg.filter(ImageFilter.GaussianBlur(9))
# soul light behind the wheel and skull
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r, a in ((360, 26), (290, 34), (220, 42), (150, 50)):
    gd.ellipse((512 - r, 380 - r, 512 + r, 380 + r), fill=SOUL + (a,))
glow = glow.filter(ImageFilter.GaussianBlur(60))
bg = bg.convert('RGBA'); bg.alpha_composite(glow)
# drifting fog bands
fog = Image.new('RGBA', (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(fog)
for k in range(9):
    y = rnd.randint(380, 760); x = rnd.randint(-200, 900)
    fd.ellipse((x, y, x + rnd.randint(300, 600), y + rnd.randint(50, 110)), fill=FOG + (rnd.randint(50, 90),))
fog = fog.filter(ImageFilter.GaussianBlur(30))
bg.alpha_composite(fog)
# ash flecks
ad = ImageDraw.Draw(bg)
for _ in range(70):
    x, y = rnd.randint(20, W - 20), rnd.randint(20, 720)
    s = rnd.choice((2, 3, 3, 4))
    ad.rectangle((x, y, x + s, y + s), fill=(170, 172, 178, rnd.randint(90, 170)))

# ------------------------------------------------------------------ the wheel (Create's model, spruce)
tex = {
    'axis': load_tex(CR + 'axis.png'), 'axis_top': load_tex(CR + 'axis_top.png'),
    'waterwheel_metal': load_tex(CR + 'waterwheel_metal.png'),
    'waterwheel_log': load_tex(V + 'block/spruce_log.png'), 'waterwheel_plank': load_tex(V + 'block/spruce_planks.png'),
    'waterwheel_stripped_log': load_tex(V + 'block/spruce_log_top.png'),
}
cam = rot_x(math.radians(12)) @ rot_y(math.radians(-20))
ws = Scene()
R = rot_x(-math.pi / 2)
ws.add_obj(OBJ, tex, lambda p: R @ (p - np.array([0.5, 0.5, 0.5])))
wheel = ws.render(W, H, cam, 134, (512, 352))
# fade the wheel slightly into the haze (atmospheric depth)
arr = np.asarray(wheel).astype(np.float32)
haze = np.array(FOG + (0,), np.float32)
mask = arr[..., 3:4] / 255
arr[..., :3] = arr[..., :3] * 0.82 + np.array(FOG) * 0.18
wheel = Image.fromarray(arr.astype(np.uint8), 'RGBA')
# dark rim so it separates from the fog
sil = wheel.split()[3].filter(ImageFilter.MaxFilter(7))
rim = Image.new('RGBA', (W, H), (12, 13, 17, 0)); rim.putalpha(sil.point(lambda a: 150 if a > 0 else 0))
bg.alpha_composite(rim.filter(ImageFilter.GaussianBlur(2)))
bg.alpha_composite(wheel)

# ------------------------------------------------------------------ the votive skull: skull block + lit candle
skel = load_tex(V + 'entity/skeleton/skeleton.png').copy()
for (u, v, c) in ((9, 12, (0.38, 0.78, 0.77)), (10, 12, (0.66, 0.94, 0.90)), (13, 12, (0.66, 0.94, 0.90)), (14, 12, (0.38, 0.78, 0.77))):
    skel[v, u, :3] = c
cand = load_tex(V + 'block/candle_lit.png')
flame = load_tex(V + 'particle/soul_fire_flame.png')
ss = Scene()
S = 2.0                                                  # skull scaled to a full block for the logo
sk = lambda p: (p - np.array([0.5, 0, 0.5])) * S
ss.add_box((4, 0, 4), (12, 8, 12), {
    'south': (8, 8, 16, 16), 'north': (24, 8, 32, 16), 'east': (16, 8, 24, 16), 'west': (0, 8, 8, 16),
    'up': (8, 0, 16, 8), 'down': (16, 0, 24, 8)}, skel, sk)
# candle (vanilla template_candle element) standing on the crown, slightly off-centre
CS = 1.0
cx = lambda p: (p - np.array([0.5, 0, 0.5])) * CS + np.array([0.22, 0.5 * S, -0.12])
ss.add_box((7, 0, 7), (9, 6, 9), {'south': (0, 8, 2, 14), 'north': (0, 8, 2, 14), 'east': (0, 8, 2, 14), 'west': (0, 8, 2, 14),
                                  'up': (0, 6, 2, 8)}, cand, cx)
# wick (the two crossed planes, as in the model)
for ang in (math.pi / 4, -math.pi / 4):
    c, s = math.cos(ang) * 0.5, math.sin(ang) * 0.5
    pts = [np.array((8 - c, 7, 8 - s)) / 16, np.array((8 + c, 7, 8 + s)) / 16, np.array((8 + c, 6, 8 + s)) / 16, np.array((8 - c, 6, 8 - s)) / 16]
    ss.add_quad([cx(p) for p in pts], [(0, 5 / 16), (1 / 16, 5 / 16), (1 / 16, 6 / 16), (0, 6 / 16)], cand)
SKS, SKY_ = 232, 772
skull_img = ss.render(W, H, cam, SKS, (512, SKY_))
# soul-fire flame particle as a billboard above the wick
wick_world = cx(np.array((8, 7, 8)) / 16)
wv = cam @ wick_world
fx, fy = 512 + wv[0] * SKS, SKY_ - wv[1] * SKS
fl = Image.fromarray((flame * 255).astype(np.uint8), 'RGBA').resize((64, 64), Image.NEAREST)
# skull glow + shadow
sg = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sgd = ImageDraw.Draw(sg)
sgd.ellipse((340, 520, 684, 830), fill=SOUL + (60,))
sgd.ellipse((int(fx) - 70, int(fy) - 110, int(fx) + 70, int(fy) + 10), fill=SOUL + (120,))
bg.alpha_composite(sg.filter(ImageFilter.GaussianBlur(40)))
sh = skull_img.split()[3].filter(ImageFilter.MaxFilter(9))
dark = Image.new('RGBA', (W, H), (8, 9, 12, 0)); dark.putalpha(sh.point(lambda a: 170 if a > 0 else 0))
bg.alpha_composite(dark.filter(ImageFilter.GaussianBlur(3)))
bg.alpha_composite(skull_img)
bg.alpha_composite(fl, (int(fx) - 32, int(fy) - 58))
# soul light from the eye sockets
eg = Image.new('RGBA', (W, H), (0, 0, 0, 0)); egd = ImageDraw.Draw(eg)
EYES = []
for ex in (6.0, 10.0):                                   # socket centres on the face (texture row 4, cols 1-2 / 5-6)
    v = cam @ sk(np.array((ex, 3.5, 12)) / 16)
    EYES.append((512 + v[0] * SKS, SKY_ - v[1] * SKS))
for (x, y) in EYES:
    egd.ellipse((x - 40, y - 26, x + 40, y + 26), fill=SOUL + (120,))
bg.alpha_composite(eg.filter(ImageFilter.GaussianBlur(16)))

# ------------------------------------------------------------------ title: chunky pixel font filled with cobbled deepslate
FONT = {
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'I': ["111", "010", "010", "010", "010", "010", "111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "'": ["1", "1", "0", "0", "0", "0", "0"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    ' ': ["000", "000", "000", "000", "000", "000", "000"],
}


def text_mask(txt, s, gap=1):
    w = sum((len(FONT[c][0]) + gap) * s for c in txt) - gap * s
    m = Image.new('L', (w, 7 * s), 0); md = ImageDraw.Draw(m)
    x = 0
    for c in txt:
        g = FONT[c]
        for j, row in enumerate(g):
            for i, ch in enumerate(row):
                if ch == '1':
                    md.rectangle((x + i * s, j * s, x + (i + 1) * s - 1, (j + 1) * s - 1), fill=255)
        x += (len(g[0]) + gap) * s
    return m


def tiled(path, size, texel):
    t = Image.open(path).convert('RGB')
    t = t.resize((t.width * texel, t.height * texel), Image.NEAREST)
    out = Image.new('RGB', size)
    for yy in range(0, size[1], t.height):
        for xx in range(0, size[0], t.width):
            out.paste(t, (xx, yy))
    return out


def stamp(dst, mask, fill_img, xy, outline=(14, 15, 19), ow=5, shadow=(0, 0, 0), so=(6, 6)):
    x, y = xy
    big = mask.filter(ImageFilter.MaxFilter(ow * 2 + 1))
    def layer(color, alpha_l):
        return Image.merge('RGBA', (*Image.new('RGB', dst.size, color).split(), alpha_l))
    sh_l = Image.new('L', dst.size, 0); sh_l.paste(big, (x - ow + so[0], y - ow + so[1]))
    dst.alpha_composite(layer(shadow, sh_l.point(lambda a: int(a * 0.6))))
    out_l = Image.new('L', dst.size, 0); out_l.paste(big, (x - ow, y - ow))
    dst.alpha_composite(layer(outline, out_l))
    fl = Image.new('RGBA', dst.size, (0, 0, 0, 0)); fl.paste(fill_img.convert('RGBA'), (x, y), mask)
    dst.alpha_composite(fl)


title = "GEARWRIGHT'S HOLLOW"
s = 8
tm = text_mask(title, s)
# bevel inside the letters: lighten top/left edge pixels, darken bottom/right (like the reference)
fill = tiled(V + 'block/cobblestone.png', tm.size, 2)
fa = np.asarray(fill).astype(np.float32); m = np.asarray(tm) > 0
up = np.zeros_like(m); up[3:] = m[:-3]
left = np.zeros_like(m); left[:, 3:] = m[:, :-3]
dn = np.zeros_like(m); dn[:-3] = m[3:]
rt = np.zeros_like(m); rt[:, :-3] = m[:, 3:]
fa[m & ~(up & left)] *= 1.35
fa[m & ~(dn & rt)] *= 0.6
fill = Image.fromarray(np.clip(fa * 1.12, 0, 255).astype(np.uint8))
tx = (W - tm.width) // 2
TY = 832
stamp(bg, tm, fill, (tx, TY))

# divider bar (polished deepslate)
bar_w, bar_h = 860, 14
bar = tiled(V + 'block/polished_deepslate.png', (bar_w, bar_h), 2)
bd = ImageDraw.Draw(bg)
bx = (W - bar_w) // 2; by = TY + tm.height + 22
bd.rectangle((bx - 4, by - 4, bx + bar_w + 3, by + bar_h + 3), fill=(14, 15, 19))
bg.paste(bar, (bx, by))
bd.line((bx, by, bx + bar_w - 1, by), fill=(150, 152, 160))
bd.line((bx, by + bar_h - 1, bx + bar_w - 1, by + bar_h - 1), fill=(40, 42, 48))

# gold subtitle
sub = "THE WORLD ENDED SLOWLY"
sm = text_mask(sub, 4)
grad = Image.new('RGB', sm.size)
gp = grad.load()
for yy in range(sm.height):
    t = yy / max(1, sm.height - 1)
    c = (int(252 - 40 * t), int(214 - 90 * t), int(98 - 60 * t))
    for xx in range(sm.width):
        gp[xx, yy] = c
stamp(bg, sm, grad, ((W - sm.width) // 2, by + bar_h + 22), ow=3, so=(4, 4))

# ------------------------------------------------------------------ frame (bevelled stone border, as in the reference)
fd = ImageDraw.Draw(bg)
for i, c in enumerate(((20, 21, 25), (124, 126, 132), (164, 166, 172), (124, 126, 132), (70, 72, 78), (20, 21, 25))):
    fd.rectangle((i * 3, i * 3, W - 1 - i * 3, H - 1 - i * 3), outline=c, width=3)

bg.convert('RGB').save(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/tex/logo.png')
