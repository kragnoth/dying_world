#!/usr/bin/env python3
"""
gen_pass4_2c.py - pass 4-2c: CONTAINER YARD HALL for the industrial mineshaft (run AFTER gen_pass4_2a.py and gen_pass4_2b.py; safe to re-run).
yard_hall_1/2: 31x12x31 hall (interior 29x10x29) with 4 tunnel connectors (7x6 openings, jigsaw at y=3 face centre, same convention as the hub).
  Two 7-wide cross aisles leave four 11x11 quadrants; each holds 1-2 rows of 4x4x10 shipping containers stacked 1-2 high.
  4-2c2 (user feedback): containers are now SOLID and purely decorative (all R&R container wall blocks, nothing inside, no open end);
  the door end (R&R *_container_doors, facing outward, latch flags on bottom/top rows) faces the aisle 70% / the wall 30%.
  Loot barrels (storage/workshop/fuel/office/stash tables) stand on the aisle side next to the container ends (~0-2 per row).
  yard_hall_1 also has a Create track down the middle of the N-S aisle (like the track tunnels); yard_hall_2 does not.
Container facts from the jar: wall block = full block with random plain/patch/hole skin per face (no props); doors block: facing + bottom/top flags.
4-2c3 (user spec): containers are 3x3 cross-section, BOTH ends = 3x3 door faces of one colour, 4-7 wall columns between (length 6-9), stacked 1-2.
  Containers + loot barrels live in a SEPARATE template yard_hall_N_boxes.nbt placed via minecraft:list_pool_element WITHOUT the no-float processor,
  so caverns can no longer eat chunks out of them (hall shell/interior keep mineshaft_no_float).
Adds both halls to the `tunnels` pool (weight 1 each). R&R ships no container structures.
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from rr_connect import connect
from gen_pass4_2a import M, R, TUN, wall, jig, lamp, w, elem, OUT, CRATES, NOFLOAT
from gen_pass4_2b import lbarrel

W, HT, C = 31, 12, 15
COLORS, CW = ["red", "blue", "green", "bare"], [3, 3, 3, 1]
LOOT = [("mineshaft_storage", 45), ("mineshaft_workshop", 20), ("mineshaft_fuel", 15), ("mineshaft_office", 10), ("mineshaft_stash", 10)]
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
# quadrant: (x0, x1, z0, z1, aisle on +x side?, aisle on +z side?)
QUADS = {"NW": (1, 11, 1, 11, True, True), "NE": (19, 29, 1, 11, False, True), "SW": (1, 11, 19, 29, True, False), "SE": (19, 29, 19, 29, False, False)}

def container(t, x0, y0, z0, axis, length, color):
    """SOLID decorative container, 3 wide x 3 high x `length` long; BOTH end faces = container doors facing outward (latch flags bottom/top rows)."""
    ends = ("west", "east") if axis == "x" else ("north", "south")
    for a in range(length):
        for lat in range(3):
            for k in range(3):
                X, Z = (x0 + a, z0 + lat) if axis == "x" else (x0 + lat, z0 + a)
                if a in (0, length - 1):
                    props = {"facing": ends[0] if a == 0 else ends[1]}
                    if k == 0: props["bottom"] = "true"
                    if k == 2: props["top"] = "true"
                    t.set(X, y0 + k, Z, R(f"{color}_container_doors"), props)
                else: t.set(X, y0 + k, Z, R(f"{color}_container_wall"))

def end_barrels(t, bx, r, x0, z0, axis, length, open_face):
    """0-2 loot barrels on the aisle side next to the container end; t = hall (to avoid clutter clashes), bx = boxes layer"""
    n = 0
    for lat in (0, 2):
        if r.random() > (.5 if lat == 0 else .25): continue
        if axis == "x": X, Z = (x0 + length if open_face == "east" else x0 - 1), z0 + lat
        else: X, Z = x0 + lat, (z0 + length if open_face == "south" else z0 - 1)
        if bx.has(X, 1, Z): continue
        tab = r.choices([x for x, _ in LOOT], [wt for _, wt in LOOT])[0]
        lbarrel(bx, X, 1, Z, tab); n += 1
    return n

def hall(seed, track):
    r = random.Random(zlib.crc32(b"yard_hall") + seed); t = Tpl(W, HT, W); bx = Tpl(W, HT, W)
    for x in range(W):
        for z in range(W):
            for y in range(HT):
                if 0 < x < W - 1 and 0 < y < HT - 1 and 0 < z < W - 1: t.set(x, y, z, M("air"))
                elif y == 0:
                    p = r.random(); t.set(x, y, z, R("weathered_concrete") if p < .6 else R("rebar_concrete") if p < .85 else R("tread_plate"))
                else: t.set(x, y, z, wall(r))
    for f, (jx, jz, face) in {"N": (C, 0, "north"), "S": (C, W - 1, "south"), "W": (0, C, "west"), "E": (W - 1, C, "east")}.items():
        for a in range(C - 3, C + 4):
            for y in range(1, 7):
                t.set(a if f in "NS" else jx, y, jz if f in "NS" else a, M("air"))
        jig(t, jx, 3, jz, face, TUN, "dying_world:mineshaft/tunnels")
    cols = (C - 3, C + 3)                             # 4 full-height columns at the aisle crossings (floor to ceiling)
    for ax in cols:
        for az in cols:
            for y in range(1, 11): t.set(ax, y, az, R("rusted_girder"), {"axis": "y"})
    for z in cols:                                    # MAIN I-beams along the aisle edges, split by the columns (ends connect as 'column')
        for x in range(1, W - 1):
            if x not in cols: t.set(x, 10, z, R("rusted_beam"), {"axis": "x"})
    for x in cols:
        for z in range(1, W - 1):
            if z not in cols: t.set(x, 10, z, R("rusted_beam"), {"axis": "z"})
    for q in (5, 25):                                 # SUB girders: wall -> main beam in every quadrant ('flange' ends), both directions
        for a, b in ((1, C - 4), (C + 4, W - 2)):
            for k in range(a, b + 1):
                t.set(q, 10, k, R("rusted_girder"), {"axis": "z"}); t.set(k, 10, q, R("rusted_girder"), {"axis": "x"})
    for z in range(C - 2, C + 3): t.set(C, 10, z, R("rusted_girder"), {"axis": "z"})   # cross girder between the two x-beams over the aisle centre
    for x, z in ((C, 5), (C, 25), (5, C), (25, C)): lamp(t, r, x, 10, z)
    lamp(t, r, C, 9, C)
    for z in range(1, W - 1):                         # hazard stripes on the aisle edges
        for x in (C - 3, C + 3):
            if r.random() < .35: t.set(x, 0, z, R("hazard_plating"))
    if track:
        for z in range(1, W - 1): t.set(C, 1, z, "create:track", {"shape": "zo"})
    boxes = 0; barrels = 0
    for qn, (x0, x1, z0, z1, ax_pos, az_pos) in QUADS.items():
        axis = r.choice(["x", "z"])
        lo, hi = (z0, z1) if axis == "x" else (x0, x1)
        open_face = ("east" if ax_pos else "west") if axis == "x" else ("south" if az_pos else "north")
        off = r.randint(0, 2); rows = [p for p in (lo + off, lo + off + 4, lo + off + 8) if p + 2 <= hi and r.random() < .8] or [lo + off]
        for rp in rows:
            length = 2 + r.randint(4, 7)                              # 2 door ends + 4-7 wall columns
            if axis == "x": a0 = x1 - length + 1 if ax_pos else x0
            else: a0 = z1 - length + 1 if az_pos else z0
            x, z = (a0, rp) if axis == "x" else (rp, a0)
            container(bx, x, 1, z, axis, length, r.choices(COLORS, CW)[0]); boxes += 1
            barrels += end_barrels(t, bx, r, x, z, axis, length, open_face)
            if r.random() < .45: container(bx, x, 4, z, axis, length, r.choices(COLORS, CW)[0]); boxes += 1
    for _ in range(10):                               # loose clutter along the aisle edges (kept off the centre lane)
        side = r.choice([C - 2, C + 2]); pos = r.randint(2, W - 3)
        if abs(pos - C) <= 3: continue
        x, z = (side, pos) if r.random() < .5 else (pos, side)
        if not bx.has(x, 1, z) and (not t.has(x, 1, z) or t.b[(x, 1, z)][0] == M("air")):
            t.set(x, 1, z, r.choice(CRATES + [R("rusted_drum"), R("tar_leaking_drum"), R("wooden_pallet")]))
    return t, bx, boxes, barrels

def main():
    N = OUT / "structure/mineshaft"; stats = []
    for s, track in ((1, True), (2, False)):
        t, bx, b, ba = hall(s, track); connect(t)
        (N / f"yard_hall_{s}.nbt").write_bytes(t.bytes()); (N / f"yard_hall_{s}_boxes.nbt").write_bytes(bx.bytes()); stats.append((b, ba))
    p = OUT / "worldgen/template_pool/mineshaft/tunnels.json"
    j = json.loads(p.read_text())
    def lst(n): return {"weight": 1, "element": {"element_type": "minecraft:list_pool_element", "projection": "rigid", "elements": [
        {"element_type": "minecraft:single_pool_element", "location": f"dying_world:mineshaft/yard_hall_{n}", "processors": NOFLOAT, "projection": "rigid"},
        {"element_type": "minecraft:single_pool_element", "location": f"dying_world:mineshaft/yard_hall_{n}_boxes", "processors": "minecraft:empty", "projection": "rigid"}]}}
    def is_hall(e): return "yard_hall" in json.dumps(e)
    j["elements"] = [e for e in j["elements"] if not is_hall(e)] + [lst(1), lst(2)]
    w(p, j)
    print(f"4-2c: 2 yard halls (containers/loot barrels: {stats}), tunnels pool now {len(j['elements'])} entries")

if __name__ == "__main__":
    main()
