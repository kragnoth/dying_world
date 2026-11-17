"""Gearwright's Hollow logo: water wheel + votive skull in Occult Foundry haze. 64x64 pixel art.
usage: python3 wheel.py <out.png> [scale]"""
import math, sys
from PIL import Image

N = 64
img = Image.new('RGB', (N, N))
P = img.load()


def h(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def dith(x, y, v, ramp):
    """v in 0..len(ramp)-1 (float) -> ramp colour with ordered dithering between steps"""
    i = int(v); f = v - i
    i = max(0, min(len(ramp) - 1, i))
    if f > (BAYER[y % 4][x % 4] + 0.5) / 16 and i + 1 < len(ramp):
        i += 1
    return ramp[i]


def put(x, y, c):
    if 0 <= x < N and 0 <= y < N:
        P[x, y] = c


# ---- palettes (Occult Foundry: slate fog, cool sky, dark teal water, soul fire)
SKY = [h(c) for c in ('#0f1118', '#13161e', '#181b24', '#1d212b', '#232733', '#2a2e3b', '#313644', '#393f4d', '#434957', '#4e5462', '#5c6270')]
SOUL = [h(c) for c in ('#1f3c43', '#2c5c63', '#3f8c8f', '#62c8c4', '#a8f0e6', '#effff9')]
WOOD = [h(c) for c in ('#1b120b', '#2e1f13', '#45301d', '#5e4228', '#7a5734', '#977042', '#b38a55')]
IRON = [h(c) for c in ('#16181d', '#2a2e36', '#454b55', '#69707b', '#9aa2ac')]
BONE = [h(c) for c in ('#1c1a1e', '#4a4549', '#7d766f', '#aca394', '#d4ccba', '#eee8d8')]
WAX = [h(c) for c in ('#6b5d4a', '#a8977a', '#d8c9a8', '#f2e8cf')]
STONE = [h(c) for c in ('#15171c', '#23262d', '#33373f', '#474c55', '#5d636d')]
WATER = [h(c) for c in ('#0d1517', '#142226', '#1c3034', '#24363a', '#35545a', '#5b8a8d')]
OUT = h('#0b0a0d')

CX, CY = 32, 29

# ---- background haze: dark overhead, slate fog toward the horizon, soul light behind the wheel
for y in range(N):
    for x in range(N):
        v = 0.8 + (y / 48) * 7.5                     # brighter toward the fog line
        if y > 46:
            v -= (y - 46) * 0.5
        g = math.hypot(x - CX, (y - CY) * 1.1)
        v += max(0, 1 - g / 36) * 2.2                # halo behind the wheel
        v += 0.35 * math.sin(x * 0.45 + y * 0.12) * (1 if 20 < y < 48 else 0)   # drifting fog bands
        P[x, y] = SKY[max(0, min(10, int(v)))]
# soul glow (cyan) close behind the wheel
for y in range(N):
    for x in range(N):
        g = math.hypot(x - CX, y - CY)
        if 20 < g < 34:
            k = (1 - abs(g - 27) / 6)
            if k > 0.55:
                P[x, y] = SOUL[0]
# far foundry: chimney stacks in the fog
for (x0, w, top) in ((2, 3, 30), (7, 2, 35), (53, 3, 28), (58, 2, 33), (61, 2, 37)):
    for y in range(top, 52):
        for x in range(x0, x0 + w):
            put(x, y, SKY[2] if x > x0 else SKY[3])
    put(x0 + w // 2, top - 1, SKY[3])
# smoke from the stacks, drifting right
for (x0, top) in ((3, 30), (54, 28)):
    for k in range(9):
        x = x0 + k // 2 + (1 if k % 3 == 0 else 0); y = top - 2 - k
        put(x, y, SKY[4]); put(x + 1, y, SKY[3])

# ---- water wheel
R_OUT, R_IN, R_HUB = 20.5, 16.8, 4.2
PADDLES, SPOKES = 16, 8
L = (-0.6, -0.8)                                     # light from the upper left


def wood(x, y, nx, ny, base):
    lit = nx * L[0] + ny * L[1]
    return WOOD[max(0, min(6, round(base + lit * 1.6)))]


shape = [[0] * N for _ in range(N)]                  # 1 = wheel pixel (for outlines)
# paddles (behind the rim): radial boards poking past the rim
for i in range(PADDLES):
    a = 2 * math.pi * i / PADDLES + 0.1
    ca, sa = math.cos(a), math.sin(a)
    tx, ty = -sa, ca
    for r10 in range(int(R_IN * 10), int((R_OUT + 5.0) * 10)):
        r = r10 / 10
        for w10 in range(-14, 15):
            w = w10 / 10
            x, y = round(CX + ca * r + tx * w), round(CY + sa * r + ty * w)
            if 0 <= x < N and 0 <= y < N:
                face = 1 if w > 0 else -1
                base = 3.6 + (0.9 if abs(w) < 0.6 else 0) - (0.8 if r > R_OUT + 4.1 else 0)
                P[x, y] = wood(x, y, tx * face, ty * face, base)
                shape[y][x] = 1
# rim: two boards (outer + inner) with a gap of shadow between
for y in range(N):
    for x in range(N):
        dx, dy = x - CX, y - CY
        r = math.hypot(dx, dy)
        nx, ny = dx / (r or 1), dy / (r or 1)
        if R_OUT - 2.6 <= r <= R_OUT:
            P[x, y] = wood(x, y, nx, ny, 4.2 if r > R_OUT - 0.9 else 3.2); shape[y][x] = 1
        elif R_IN <= r <= R_IN + 1.9:
            P[x, y] = wood(x, y, -nx, -ny, 3.4); shape[y][x] = 1
# spokes: thick boards from hub to inner rim
for i in range(SPOKES):
    a = 2 * math.pi * i / SPOKES + math.pi / 8
    ca, sa = math.cos(a), math.sin(a)
    tx, ty = -sa, ca
    for r10 in range(int(R_HUB * 10), int((R_IN + 0.5) * 10)):
        r = r10 / 10
        for w10 in range(-12, 13):
            w = w10 / 10
            x, y = round(CX + ca * r + tx * w), round(CY + sa * r + ty * w)
            base = 3.5 + (0.8 if w < -0.3 else (-0.9 if w > 0.6 else 0))
            P[x, y] = wood(x, y, ca, sa, base)
            shape[y][x] = 1
# iron bands where spokes meet the rim
for i in range(SPOKES):
    a = 2 * math.pi * i / SPOKES + math.pi / 8
    for rr in (R_IN + 0.9,):
        x, y = round(CX + math.cos(a) * rr), round(CY + math.sin(a) * rr)
        put(x, y, IRON[3]); put(x + 1, y + 1, IRON[1])
# hub: iron disc with rim highlight and bolts
for y in range(N):
    for x in range(N):
        dx, dy = x - CX, y - CY
        r = math.hypot(dx, dy)
        if r <= R_HUB:
            lit = (dx * L[0] + dy * L[1]) / (R_HUB)
            v = 2.2 - lit * 1.3
            if r > R_HUB - 1:
                v = 1 if lit > 0 else 3.4
            P[x, y] = IRON[max(0, min(4, round(v)))]
            shape[y][x] = 1
P[CX, CY] = IRON[0]
for bx, by in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
    put(CX + bx, CY + by, IRON[4])

# outline the wheel against the haze
for y in range(N):
    for x in range(N):
        if shape[y][x]:
            continue
        nb = sum(shape[y + oy][x + ox] for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + ox < N and 0 <= y + oy < N)
        if nb:
            d = math.hypot(x - CX, y - CY)
            if d > R_OUT - 3 or d < R_IN + 3:          # silhouette + inner openings
                P[x, y] = OUT if d > R_OUT - 3 else WOOD[0]

# ---- water: the wheel's foot sits in a dark race; ripples catch the soul light
WL = 51
for y in range(WL, N):
    for x in range(N):
        v = 3.0 - (y - WL) * 0.28
        if (x * 2 + (y - WL) * 7) % 13 < 3 and (y - WL) % 2 == 0:
            v += 1
        P[x, y] = WATER[max(0, min(5, int(v)))]
for x in range(N):
    P[x, WL] = WATER[4] if x % 5 else WATER[5]
# reflection of the glow + wheel in the water
for y in range(WL + 1, N):
    for x in range(14, 51):
        if (y - WL) % 2 == 1 and abs(x - CX) < 16 - (y - WL) and (x // 3) % 2 == 0:
            P[x, y] = WATER[4]
# water spilling off the paddles on the right side
for (x0, y0, ln) in ((54, 30, 20), (52, 36, 15), (56, 26, 8)):
    for k in range(ln):
        y = y0 + k
        put(x0, y, WATER[5] if k % 4 == 0 else SOUL[2])
        if k % 3 == 1:
            put(x0 + 1, y, WATER[4])
for x in range(48, 60):
    put(x, WL - 1, SOUL[3] if x % 3 == 0 else WATER[5])   # splash

# ---- low fog bank drifting in front of the wheel's foot (blended toward the vision's fog colour)
FOG = h('#5c6270')
for y in range(38, 51):
    for x in range(N):
        wave = 2.2 * math.sin(x * 0.21 + 1.0) + 1.3 * math.sin(x * 0.53)
        k = (y - (40 + wave)) / 10
        if k <= 0:
            continue
        k = min(0.55, k * 0.65)
        if (x + y) % 2 and k < 0.2:
            continue
        r, g, b = P[x, y]
        P[x, y] = (round(r + (FOG[0] - r) * k), round(g + (FOG[1] - g) * k), round(b + (FOG[2] - b) * k))

# ---- stone plinth for the skull
for y in range(52, 59):
    for x in range(21, 43):
        v = 2.6 - (y - 52) * 0.25 + (0.8 if y == 52 else 0)
        if (x - 21) % 11 == 0 or y == 55:               # brick joints
            v = 0.6
        P[x, y] = STONE[max(0, min(4, round(v)))]
for x in range(20, 44):
    put(x, 59, OUT)
for y in range(52, 59):
    put(20, y, OUT); put(43, y, OUT)

# ---- the votive skull (blocky, front + a strip of its top)
SX, SY, SW, SH = 23, 38, 18, 14                     # front face box
for y in range(SY - 3, SY):                          # top face, receding
    for x in range(SX + (SY - y), SX + SW - (SY - y) + 1):
        P[x, y] = BONE[4] if y == SY - 1 else BONE[5]
for y in range(SY, SY + SH):
    for x in range(SX, SX + SW):
        v = 3.6 - (x - SX) / SW * 1.2 - (y - SY) / SH * 0.8   # lit from upper left
        P[x, y] = BONE[max(0, min(5, int(v)))]
# outline
for x in range(SX - 1, SX + SW + 1):
    put(x, SY + SH, OUT)
for y in range(SY - 3, SY + SH):
    put(SX - 1, y, OUT); put(SX + SW, y, OUT)
for k in range(4):
    put(SX + k - 1, SY - k, OUT); put(SX + SW - k, SY - k, OUT)
for x in range(SX + 2, SX + SW - 2):
    put(x, SY - 4, OUT)
# eye sockets: deep, each with a soul-fire pinprick
for ex in (SX + 3, SX + 10):
    for y in range(SY + 4, SY + 9):
        for x in range(ex, ex + 5):
            P[x, y] = BONE[0] if (y > SY + 4 or x > ex) else BONE[1]
    put(ex + 2, SY + 6, SOUL[4]); put(ex + 3, SY + 6, SOUL[3]); put(ex + 2, SY + 7, SOUL[2])
# brow shadow
for x in range(SX + 2, SX + SW - 2):
    if P[x, SY + 3] not in (BONE[0],):
        P[x, SY + 3] = BONE[2]
# nose
for (x, y) in ((SX + 8, SY + 10), (SX + 9, SY + 10), (SX + 8, SY + 11), (SX + 9, SY + 11), (SX + 7, SY + 11), (SX + 10, SY + 11)):
    P[x, y] = BONE[0]
# teeth: alternating, with a dark jaw line
for x in range(SX + 3, SX + SW - 3):
    P[x, SY + 13] = BONE[5] if x % 2 else BONE[1]
    P[x, SY + 12] = BONE[2]
    P[x, SY + 14] = BONE[1]
# a crack across the brow
for (x, y) in ((SX + 13, SY + 1), (SX + 12, SY + 2), (SX + 12, SY + 3), (SX + 14, SY + 2)):
    P[x, y] = BONE[1]

# ---- candle on the skull, wax running down its crown
CXd, CT = 31, 31                                     # candle x, candle top
for y in range(CT, SY - 2):
    for x in range(CXd, CXd + 3):
        P[x, y] = WAX[3] if x == CXd else (WAX[2] if x == CXd + 1 else WAX[1])
    put(CXd - 1, y, OUT); put(CXd + 3, y, OUT)
for (x, y) in ((CXd - 1, SY - 2), (CXd - 2, SY - 1), (CXd - 2, SY), (CXd + 3, SY - 2), (CXd + 4, SY - 1), (CXd + 4, SY), (CXd + 4, SY + 1),
               (CXd, SY - 2), (CXd + 1, SY - 2), (CXd + 2, SY - 2), (CXd - 1, SY - 1), (CXd + 3, SY - 1)):
    put(x, y, WAX[2] if (x + y) % 2 else WAX[3])
put(CXd + 1, CT - 1, OUT)                            # wick
# soul flame: teardrop, white-hot core
FL = [
    "..1..",
    "..2..",
    ".232.",
    ".343.",
    "23432",
    "24542",
    "23532",
    ".343.",
]
for j, row in enumerate(FL):
    for i, ch in enumerate(row):
        if ch != '.':
            put(CXd - 1 + i, CT - 1 - len(FL) + j, SOUL[int(ch)])
# glow: one soft ring of soul light around the flame (solid, no checker)
for y in range(CT - 14, CT + 2):
    for x in range(CXd - 7, CXd + 10):
        d = math.hypot(x - (CXd + 1), (y - (CT - 5)) * 1.0)
        if 4.2 < d < 6.2:
            cur = P[x, y]
            if cur in SKY or cur in IRON or cur in WOOD or cur == OUT:
                P[x, y] = SOUL[1] if d < 5.2 else SOUL[0]
# ---- ash flecks and a few soul motes in the haze
for (x, y) in ((6, 8), (14, 4), (47, 6), (58, 14), (3, 20), (61, 22), (10, 46), (20, 2), (40, 1)):
    if P[x, y] in SKY:
        P[x, y] = SKY[6]
for (x, y) in ((8, 14), (57, 8), (50, 47), (12, 40)):
    if P[x, y] in SKY:
        P[x, y] = SOUL[3]

scale = int(sys.argv[2]) if len(sys.argv) > 2 else 1
(img.resize((N * scale, N * scale), Image.NEAREST) if scale > 1 else img).save(sys.argv[1])
